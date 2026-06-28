"""
Tick Ingestion Service
Polls Alpha Vantage FX_INTRADAY for XAU/USD 5-min bars, simulates per-tick data,
and publishes to Kafka topic raw.ticks.

Free tier budget: 25 API calls/day → poll every 58 min (24 calls) + 1 startup call.
"""
import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone

import aiohttp
import numpy as np
from aiokafka import AIOKafkaProducer
from prometheus_client import Counter, Histogram, start_http_server

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s [tick-ingestion] %(levelname)s %(message)s',
)
log = logging.getLogger('tick-ingestion')

ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'redpanda:9092')
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL_SECONDS', 3480))  # 58 min
METRICS_PORT = int(os.getenv('METRICS_PORT', 8000))
TICKS_PER_BAR = int(os.getenv('TICKS_PER_BAR', 12))
SPREAD = float(os.getenv('XAU_SPREAD', 0.10))  # typical XAU/USD spread in USD

tick_count = Counter('tick_ingestion_ticks_total', 'Total ticks published to Kafka')
api_calls_total = Counter('tick_ingestion_api_calls_total', 'Total Alpha Vantage API calls made')
api_errors_total = Counter('tick_ingestion_api_errors_total', 'Total Alpha Vantage API errors')
ingestion_latency = Histogram(
    'tick_ingestion_publish_latency_ms',
    'Kafka publish latency in milliseconds',
    buckets=[0.5, 1, 2, 5, 10, 25, 50, 100],
)


async def fetch_bars(session: aiohttp.ClientSession, full: bool = False) -> list[dict]:
    """Fetch XAU/USD 5-min OHLCV bars from Alpha Vantage FX_INTRADAY."""
    outputsize = 'full' if full else 'compact'
    url = (
        'https://www.alphavantage.co/query'
        f'?function=FX_INTRADAY'
        f'&from_symbol=XAU'
        f'&to_symbol=USD'
        f'&interval=5min'
        f'&outputsize={outputsize}'
        f'&apikey={ALPHA_VANTAGE_KEY}'
    )
    api_calls_total.inc()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            data = await resp.json(content_type=None)
    except Exception as e:
        api_errors_total.inc()
        raise RuntimeError(f'Alpha Vantage request failed: {e}') from e

    ts_key = 'Time Series FX (5min)'
    if ts_key not in data:
        api_errors_total.inc()
        note = data.get('Note', data.get('Information', str(list(data.keys()))))
        raise ValueError(f'Unexpected Alpha Vantage response: {note}')

    bars = []
    for ts_str, ohlcv in sorted(data[ts_key].items()):
        bars.append({
            'ts': datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                  .replace(tzinfo=timezone.utc)
                  .timestamp(),
            'open': float(ohlcv['1. open']),
            'high': float(ohlcv['2. high']),
            'low': float(ohlcv['3. low']),
            'close': float(ohlcv['4. close']),
            'volume': float(ohlcv['5. volume']),
        })
    return bars


def simulate_ticks(bar: dict, n: int = TICKS_PER_BAR) -> list[dict]:
    """
    Interpolate n ticks from a 5-min OHLCV bar.
    Adds small Gaussian noise; clamps bid within bar High/Low.
    """
    prices = np.linspace(bar['open'], bar['close'], n)
    noise = np.random.normal(0, 0.03, n)
    bar_ts = bar['ts']
    bar_vol = bar['volume']
    duration = 300  # 5 min in seconds

    ticks = []
    for i, (price, nz) in enumerate(zip(prices, noise)):
        bid = round(float(np.clip(price + nz, bar['low'], bar['high'])), 2)
        ticks.append({
            'ts': round(bar_ts + i * duration / n, 3),
            'bid': bid,
            'ask': round(bid + SPREAD, 2),
            'volume': round(bar_vol / n, 4),
            'source': 'alpha_vantage_sim',
        })
    return ticks


async def publish_ticks(producer: AIOKafkaProducer, ticks: list[dict]) -> None:
    for tick in ticks:
        t0 = time.monotonic()
        await producer.send('raw.ticks', json.dumps(tick).encode())
        ingestion_latency.observe((time.monotonic() - t0) * 1000)
        tick_count.inc()


async def run(producer: AIOKafkaProducer) -> None:
    async with aiohttp.ClientSession() as session:
        # Startup: fetch full history (1 API call) to seed the signal processor buffer
        log.info('Fetching full historical XAU/USD data from Alpha Vantage...')
        try:
            bars = await fetch_bars(session, full=True)
            log.info(f'Publishing {len(bars)} historical bars as ticks...')
            for bar in bars:
                await publish_ticks(producer, simulate_ticks(bar, n=3))
            log.info('Historical seed complete.')
        except Exception as e:
            log.error(f'Startup fetch failed: {e}. Continuing with polling loop.')

        # Main polling loop
        while True:
            await asyncio.sleep(POLL_INTERVAL)
            log.info('Polling latest bars...')
            try:
                bars = await fetch_bars(session, full=False)
                # publish last 2 bars to handle any gap
                for bar in bars[-2:]:
                    await publish_ticks(producer, simulate_ticks(bar))
                log.info(f'Published ticks for {min(2, len(bars))} bars.')
            except Exception as e:
                log.error(f'Poll failed: {e}')


async def health_server() -> None:
    """Minimal HTTP health endpoint on port 8080."""
    from aiohttp import web

    async def health(_req):
        return web.Response(text='ok')

    app = web.Application()
    app.router.add_get('/health', health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()


async def main() -> None:
    start_http_server(METRICS_PORT)
    log.info(f'Prometheus metrics on :{METRICS_PORT}')

    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=None,
    )
    await producer.start()
    log.info(f'Connected to Kafka at {KAFKA_BROKER}')

    try:
        await asyncio.gather(health_server(), run(producer))
    finally:
        await producer.stop()


if __name__ == '__main__':
    asyncio.run(main())
