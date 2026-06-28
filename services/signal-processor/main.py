"""
Signal Processor Service
Consumes raw.ticks from Kafka, aggregates into M15/H4 OHLCV bars,
runs the 6-point confluence signal logic, and publishes to processed.signals.

Target: <50ms end-to-end tick -> signal latency (asyncio + threadpool for NumPy).
"""
import asyncio
import json
import logging
import os
import time
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

import pandas as pd
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiohttp import web
from prometheus_client import Counter, Histogram, Gauge, start_http_server

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s [signal-processor] %(levelname)s %(message)s',
)
log = logging.getLogger('signal-processor')

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'redpanda:9092')
METRICS_PORT = int(os.getenv('METRICS_PORT', 8001))
MIN_H4_BARS = int(os.getenv('MIN_H4_BARS', 60))
MIN_M15_BARS = int(os.getenv('MIN_M15_BARS', 100))
MAX_TICKS = int(os.getenv('MAX_TICKS', 50000))  # rolling tick buffer size

ticks_consumed = Counter('signal_processor_ticks_consumed_total', 'Ticks consumed from raw.ticks')
signals_generated = Counter('signal_processor_signals_total', 'Trading signals generated')
processing_latency = Histogram(
    'signal_processor_latency_ms',
    'End-to-end signal processing latency in ms',
    buckets=[1, 5, 10, 20, 30, 50, 100, 250, 500],
)
buffer_size_gauge = Gauge('signal_processor_tick_buffer_size', 'Current tick buffer size')
last_signal_ts = Gauge('signal_processor_last_signal_timestamp', 'Unix timestamp of last signal')

# Liveness flag — flipped True once Kafka is connected, False on fatal error.
_ready = False


class TickBuffer:
    """Rolling buffer of raw ticks; resamples into OHLCV DataFrames on demand."""

    def __init__(self, maxlen: int = MAX_TICKS):
        self._ticks: deque = deque(maxlen=maxlen)
        self._last_bar_ts: dict[str, float] = {}

    def add(self, tick: dict) -> None:
        self._ticks.append(tick)

    def __len__(self) -> int:
        return len(self._ticks)

    def to_ohlcv(self, freq: str) -> pd.DataFrame:
        if not self._ticks:
            return pd.DataFrame()

        df = pd.DataFrame(list(self._ticks))
        df['ts'] = pd.to_datetime(df['ts'], unit='s', utc=True)
        df = df.set_index('ts').sort_index()
        mid = (df['bid'] + df['ask']) / 2.0

        ohlcv = pd.DataFrame({
            'Open': mid.resample(freq).first(),
            'High': df['ask'].resample(freq).max(),
            'Low': df['bid'].resample(freq).min(),
            'Close': mid.resample(freq).last(),
            'Volume': df['volume'].resample(freq).sum(),
        }).dropna()

        return ohlcv

    def new_bar_closed(self, freq: str) -> bool:
        """Returns True if a new bar has closed since the last check."""
        now = pd.Timestamp.now(tz='UTC')
        current_bar_open = now.floor(freq)
        last = self._last_bar_ts.get(freq, 0.0)
        bar_ts = current_bar_open.timestamp()
        if bar_ts > last:
            self._last_bar_ts[freq] = bar_ts
            return True
        return False


def build_signal_dfs(buffer: TickBuffer):
    """Resample buffer and calculate indicators. Run in thread pool to avoid blocking."""
    import sys, os as _os
    sys.path.insert(0, '/app/shared')

    from indicators.technical import TechnicalIndicators

    tech = TechnicalIndicators()
    df_m15 = buffer.to_ohlcv('15min')
    df_h4 = buffer.to_ohlcv('4h')

    if len(df_m15) < MIN_M15_BARS or len(df_h4) < MIN_H4_BARS:
        return None, None, len(df_m15), len(df_h4)

    df_m15 = tech.calculate_all(df_m15)
    df_h4 = tech.calculate_all(df_h4)

    if df_m15.empty or df_h4.empty:
        return None, None, 0, 0

    return df_m15, df_h4, len(df_m15), len(df_h4)


async def process_tick(
    tick: dict,
    buffer: TickBuffer,
    producer: AIOKafkaProducer,
    executor: ThreadPoolExecutor,
    tick_ts: float,
) -> None:
    buffer.add(tick)
    buffer_size_gauge.set(len(buffer))

    # Only attempt signal generation when a new M15 bar closes
    if not buffer.new_bar_closed('15min'):
        return

    loop = asyncio.get_running_loop()
    t0 = time.monotonic()

    try:
        df_m15, df_h4, n_m15, n_h4 = await loop.run_in_executor(
            executor, build_signal_dfs, buffer
        )
    except Exception as e:
        log.error(f'Indicator calculation error: {e}')
        return

    if df_m15 is None:
        log.debug(f'Not enough bars yet — M15: {n_m15}/{MIN_M15_BARS}, H4: {n_h4}/{MIN_H4_BARS}')
        return

    try:
        import sys
        sys.path.insert(0, '/app/shared')
        from strategy.signal_generator import SignalGenerator

        gen = SignalGenerator()
        signal = gen.generate_signal(df_h4, df_m15)
    except Exception as e:
        log.error(f'Signal generation error: {e}')
        return

    latency_ms = (time.monotonic() - t0) * 1000
    processing_latency.observe(latency_ms)

    if signal:
        signal['id'] = str(uuid.uuid4())
        signal['ingestion_ts'] = tick_ts
        signal['processed_ts'] = time.time()
        signal['latency_ms'] = round(latency_ms, 2)

        payload = json.dumps(signal).encode()
        await producer.send('processed.signals', payload)
        signals_generated.inc()
        last_signal_ts.set(time.time())
        log.info(
            f"Signal: {signal['signal']} @ {signal['entry_price']} "
            f"(confidence {signal['confidence']}%, latency {latency_ms:.1f}ms)"
        )


async def health_handler(_req):
    if _ready:
        return web.Response(text='ok')
    return web.Response(status=503, text='kafka not connected')


async def health_server() -> None:
    app = web.Application()
    app.router.add_get('/health', health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 8080).start()


async def main() -> None:
    start_http_server(METRICS_PORT)
    log.info(f'Prometheus metrics on :{METRICS_PORT}')

    consumer = AIOKafkaConsumer(
        'raw.ticks',
        bootstrap_servers=KAFKA_BROKER,
        group_id='signal-processor',
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode()),
    )
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKER)

    global _ready
    await consumer.start()
    await producer.start()
    _ready = True
    log.info(f'Connected to Kafka at {KAFKA_BROKER}')

    buffer = TickBuffer()
    executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='signal')

    try:
        await asyncio.gather(
            health_server(),
            consume_loop(consumer, producer, buffer, executor),
        )
    except Exception:
        _ready = False
        raise
    finally:
        _ready = False
        await consumer.stop()
        await producer.stop()
        executor.shutdown(wait=False)


async def consume_loop(consumer, producer, buffer, executor):
    async for msg in consumer:
        tick = msg.value
        tick_ts = tick.get('ts', time.time())
        ticks_consumed.inc()
        await process_tick(tick, buffer, producer, executor, tick_ts)


if __name__ == '__main__':
    asyncio.run(main())
