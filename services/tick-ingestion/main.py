"""
Tick Ingestion Service
Polls Alpha Vantage FX_INTRADAY for XAU/USD 5-min bars, simulates per-tick data,
and publishes to Kafka topic raw.ticks.

Free tier budget: 25 API calls/day -> poll every 58 min (24 calls) + 1 startup call.
"""
import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone

import aiohttp
import numpy as np
from aiohttp import web
from aiokafka import AIOKafkaProducer
from prometheus_client import Counter, Histogram, start_http_server

# Liveness flag — flipped True once Kafka is connected, False on fatal error.
_ready = False

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


class PremiumEndpointError(RuntimeError):
    """Raised when Alpha Vantage rejects a call as premium-only or rate-limited."""


# Last known mid price, used to seed the pure-simulation fallback (random walk).
_last_price: float = 2000.0


async def _av_get(session: aiohttp.ClientSession, params: dict) -> dict:
    """Call Alpha Vantage and surface premium/rate-limit notices as exceptions."""
    params = {**params, 'apikey': ALPHA_VANTAGE_KEY}
    api_calls_total.inc()
    try:
        async with session.get(
            'https://www.alphavantage.co/query',
            params=params,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            data = await resp.json(content_type=None)
    except Exception as e:
        api_errors_total.inc()
        raise RuntimeError(f'Alpha Vantage request failed: {e}') from e

    # Free-tier rejections come back as Note / Information, not an HTTP error.
    if 'Note' in data or 'Information' in data:
        api_errors_total.inc()
        raise PremiumEndpointError(data.get('Note') or data.get('Information'))
    if 'Error Message' in data:
        api_errors_total.inc()
        raise ValueError(data['Error Message'])
    return data


def _parse_bars(data: dict, ts_key: str, fmt: str) -> list[dict]:
    bars = []
    for ts_str, ohlcv in sorted(data[ts_key].items()):
        bars.append({
            'ts': datetime.strptime(ts_str, fmt).replace(tzinfo=timezone.utc).timestamp(),
            'open': float(ohlcv['1. open']),
            'high': float(ohlcv['2. high']),
            'low': float(ohlcv['3. low']),
            'close': float(ohlcv['4. close']),
            'volume': float(ohlcv.get('5. volume', 0) or 0),
        })
    return bars


async def fetch_intraday_bars(session: aiohttp.ClientSession, full: bool = False) -> list[dict]:
    """FX_INTRADAY 5-min bars (premium on most plans). Raises PremiumEndpointError if unavailable."""
    data = await _av_get(session, {
        'function': 'FX_INTRADAY', 'from_symbol': 'XAU', 'to_symbol': 'USD',
        'interval': '5min', 'outputsize': 'full' if full else 'compact',
    })
    ts_key = 'Time Series FX (5min)'
    if ts_key not in data:
        raise ValueError(f'Unexpected FX_INTRADAY response keys: {list(data.keys())}')
    return _parse_bars(data, ts_key, '%Y-%m-%d %H:%M:%S')


async def fetch_daily_bars(session: aiohttp.ClientSession, full: bool = False) -> list[dict]:
    """FX_DAILY bars (free tier). Used to seed the buffer when intraday is unavailable."""
    data = await _av_get(session, {
        'function': 'FX_DAILY', 'from_symbol': 'XAU', 'to_symbol': 'USD',
        'outputsize': 'full' if full else 'compact',
    })
    ts_key = 'Time Series FX (Daily)'
    if ts_key not in data:
        raise ValueError(f'Unexpected FX_DAILY response keys: {list(data.keys())}')
    return _parse_bars(data, ts_key, '%Y-%m-%d')


async def fetch_quote(session: aiohttp.ClientSession) -> dict:
    """CURRENCY_EXCHANGE_RATE realtime quote (free tier). Returns a synthetic 5-min bar."""
    data = await _av_get(session, {
        'function': 'CURRENCY_EXCHANGE_RATE', 'from_currency': 'XAU', 'to_currency': 'USD',
    })
    rate = data.get('Realtime Currency Exchange Rate', {})
    price = float(rate.get('5. Exchange Rate'))
    bid = float(rate.get('8. Bid Price', price) or price)
    ask = float(rate.get('9. Ask Price', price) or price)
    return {
        'ts': datetime.now(timezone.utc).timestamp(),
        'open': bid, 'high': max(bid, ask), 'low': min(bid, ask),
        'close': ask, 'volume': 0.0,
    }


def simulate_random_walk_bar() -> dict:
    """Last-resort fallback: random-walk a synthetic bar from the last known price."""
    global _last_price
    drift = float(np.random.normal(0, 0.5))
    new_price = max(_last_price + drift, 1.0)
    bar = {
        'ts': datetime.now(timezone.utc).timestamp(),
        'open': _last_price,
        'high': max(_last_price, new_price) + abs(float(np.random.normal(0, 0.2))),
        'low': min(_last_price, new_price) - abs(float(np.random.normal(0, 0.2))),
        'close': new_price,
        'volume': 0.0,
    }
    _last_price = new_price
    return bar


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
    """
    Market-data ingestion with graceful degradation:
      1. FX_INTRADAY 5-min bars (best; premium on most plans)
      2. FX_DAILY seed + CURRENCY_EXCHANGE_RATE polling (free tier)
      3. Pure random-walk simulation (no API / quota exhausted)
    """
    global _last_price
    use_intraday = True

    async with aiohttp.ClientSession() as session:
        # ── Startup seed: try intraday, fall back to daily ──
        log.info('Seeding buffer from Alpha Vantage...')
        try:
            bars = await fetch_intraday_bars(session, full=True)
            log.info(f'Seeded {len(bars)} intraday bars.')
        except PremiumEndpointError as e:
            log.warning(f'FX_INTRADAY unavailable on this key ({e}); falling back to FX_DAILY.')
            use_intraday = False
            try:
                bars = await fetch_daily_bars(session, full=True)
                log.info(f'Seeded {len(bars)} daily bars.')
            except Exception as e2:
                log.error(f'Daily seed failed: {e2}; starting from simulation only.')
                bars = []
        except Exception as e:
            log.error(f'Startup seed failed: {e}; starting from simulation only.')
            bars = []

        for bar in bars:
            await publish_ticks(producer, simulate_ticks(bar, n=3))
        if bars:
            _last_price = bars[-1]['close']

        # ── Polling loop ──
        while True:
            await asyncio.sleep(POLL_INTERVAL)
            try:
                if use_intraday:
                    latest = await fetch_intraday_bars(session, full=False)
                    for bar in latest[-2:]:
                        await publish_ticks(producer, simulate_ticks(bar))
                    if latest:
                        _last_price = latest[-1]['close']
                    log.info(f'Published intraday ticks for {min(2, len(latest))} bars.')
                else:
                    bar = await fetch_quote(session)
                    await publish_ticks(producer, simulate_ticks(bar))
                    _last_price = bar['close']
                    log.info('Published quote-based ticks.')
            except PremiumEndpointError as e:
                # Quota exhausted or premium-gated: emit simulated ticks so the
                # pipeline keeps flowing instead of going dark.
                log.warning(f'API unavailable ({e}); emitting simulated ticks.')
                await publish_ticks(producer, simulate_ticks(simulate_random_walk_bar()))
            except Exception as e:
                log.error(f'Poll failed: {e}; emitting simulated ticks.')
                await publish_ticks(producer, simulate_ticks(simulate_random_walk_bar()))


async def health(_req):
    if _ready:
        return web.Response(text='ok')
    return web.Response(status=503, text='kafka not connected')


async def health_server() -> None:
    """Minimal HTTP health endpoint on port 8080."""
    app = web.Application()
    app.router.add_get('/health', health)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 8080).start()


async def main() -> None:
    start_http_server(METRICS_PORT)
    log.info(f'Prometheus metrics on :{METRICS_PORT}')

    global _ready
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=None,
    )
    await producer.start()
    _ready = True
    log.info(f'Connected to Kafka at {KAFKA_BROKER}')

    try:
        await asyncio.gather(health_server(), run(producer))
    except Exception:
        _ready = False
        raise
    finally:
        _ready = False
        await producer.stop()


if __name__ == '__main__':
    asyncio.run(main())
