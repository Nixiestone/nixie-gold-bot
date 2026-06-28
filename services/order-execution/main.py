"""
Order Execution Service
Consumes processed.signals, sends Telegram alerts, writes to Neon PostgreSQL,
and publishes to executed.orders.
"""
import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone

import asyncpg
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiohttp import web
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s [order-execution] %(levelname)s %(message)s',
)
log = logging.getLogger('order-execution')

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'redpanda:9092')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
NEON_DATABASE_URL = os.getenv('NEON_DATABASE_URL', '')
METRICS_PORT = int(os.getenv('METRICS_PORT', 8002))

orders_processed = Counter('order_execution_orders_total', 'Total signals processed')
telegram_sent = Counter('order_execution_telegram_sent_total', 'Telegram alerts successfully sent')
telegram_errors = Counter('order_execution_telegram_errors_total', 'Telegram send failures')
db_writes = Counter('order_execution_db_writes_total', 'PostgreSQL rows written')
db_errors = Counter('order_execution_db_errors_total', 'PostgreSQL write failures')
execution_latency = Histogram(
    'order_execution_latency_ms',
    'Time from signal receipt to Telegram send',
    buckets=[10, 25, 50, 100, 250, 500, 1000],
)
telegram_success_rate = Gauge('order_execution_telegram_success_rate', 'Rolling Telegram success rate')

# Liveness flag — flipped True once Kafka is connected, False on fatal error.
_ready = False

_sent_count = 0
_total_count = 0


def _update_success_rate(success: bool) -> None:
    global _sent_count, _total_count
    _total_count += 1
    if success:
        _sent_count += 1
    if _total_count > 0:
        telegram_success_rate.set(_sent_count / _total_count)


def format_telegram_message(signal: dict) -> str:
    direction = signal.get('signal', 'UNKNOWN')
    emoji = '' if direction == 'LONG' else ''
    return (
        f"{emoji} *XAU/USD {direction} Signal*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"*Entry:* `${signal.get('entry_price', 0):.2f}`\n"
        f"*Stop Loss:* `${signal.get('stop_loss', 0):.2f}` "
        f"({signal.get('pips_risk', 0):.1f} pips)\n"
        f"*TP1:* `${signal.get('take_profit_1', 0):.2f}` (1.5R)\n"
        f"*TP2:* `${signal.get('take_profit_2', 0):.2f}` (2.5R)\n"
        f"*TP3:* `${signal.get('take_profit_3', 0):.2f}` (4.0R)\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"*Confidence:* {signal.get('confidence', 0)}%\n"
        f"*Regime:* {signal.get('regime', 'N/A')}\n"
        f"*Session:* {signal.get('session', 'N/A')}\n"
        f"*Level:* {signal.get('level_name', 'N/A')}\n"
        f"*R/R:* {signal.get('rr_ratio', 0):.2f}\n"
        f"*Risk:* ${signal.get('risk_dollars', 0):.2f}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"_Latency: {signal.get('latency_ms', 0):.0f}ms_"
    )


async def send_telegram(bot: Bot, signal: dict) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning('Telegram not configured — skipping alert')
        return False
    try:
        msg = format_telegram_message(signal)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=msg,
            parse_mode='Markdown',
        )
        telegram_sent.inc()
        return True
    except TelegramError as e:
        telegram_errors.inc()
        log.error(f'Telegram send failed: {e}')
        return False


async def write_to_db(pool: asyncpg.Pool, signal: dict, tg_ok: bool) -> int | None:
    """Insert the signal and its corresponding order row in one transaction."""
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                signal_id = await conn.fetchval(
                    """
                    INSERT INTO signals
                        (ts, direction, entry, sl, tp1, tp2, tp3, confidence, regime, level_name, session, latency_ms)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    RETURNING id
                    """,
                    datetime.fromtimestamp(signal.get('processed_ts', time.time()), tz=timezone.utc),
                    signal.get('signal'),
                    signal.get('entry_price'),
                    signal.get('stop_loss'),
                    signal.get('take_profit_1'),
                    signal.get('take_profit_2'),
                    signal.get('take_profit_3'),
                    float(signal.get('confidence', 0)),
                    signal.get('regime'),
                    signal.get('level_name'),
                    signal.get('session'),
                    signal.get('latency_ms'),
                )
                await conn.execute(
                    """
                    INSERT INTO orders (signal_id, telegram_sent_at, telegram_ok, status)
                    VALUES ($1, $2, $3, $4)
                    """,
                    signal_id,
                    datetime.now(tz=timezone.utc) if tg_ok else None,
                    tg_ok,
                    'sent' if tg_ok else 'failed',
                )
            db_writes.inc()
            return signal_id
    except Exception as e:
        db_errors.inc()
        log.error(f'DB write failed: {e}')
        return None


async def process_signal(
    signal: dict,
    bot: Bot,
    pool: asyncpg.Pool | None,
    producer: AIOKafkaProducer,
) -> None:
    t0 = time.monotonic()
    orders_processed.inc()

    # Telegram alert
    tg_ok = await send_telegram(bot, signal)
    _update_success_rate(tg_ok)

    # DB write (signal + order rows)
    signal_id = None
    if pool:
        signal_id = await write_to_db(pool, signal, tg_ok)

    # Publish to executed.orders
    order = {
        'signal_id': signal.get('id'),
        'db_id': signal_id,
        'ts': time.time(),
        'direction': signal.get('signal'),
        'entry_price': signal.get('entry_price'),
        'telegram_sent': tg_ok,
        'status': 'sent' if tg_ok else 'failed',
    }
    await producer.send('executed.orders', json.dumps(order).encode())

    latency_ms = (time.monotonic() - t0) * 1000
    execution_latency.observe(latency_ms)
    log.info(
        f"Order processed — signal {signal.get('signal')} @ {signal.get('entry_price')}, "
        f"telegram={'ok' if tg_ok else 'fail'}, latency={latency_ms:.1f}ms"
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


async def consume_loop(consumer, bot, pool, producer):
    async for msg in consumer:
        signal = json.loads(msg.value.decode())
        await process_signal(signal, bot, pool, producer)


async def main() -> None:
    start_http_server(METRICS_PORT)
    log.info(f'Prometheus metrics on :{METRICS_PORT}')

    consumer = AIOKafkaConsumer(
        'processed.signals',
        bootstrap_servers=KAFKA_BROKER,
        group_id='order-execution',
        auto_offset_reset='latest',
    )
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKER)

    global _ready
    await consumer.start()
    await producer.start()
    _ready = True
    log.info(f'Connected to Kafka at {KAFKA_BROKER}')

    bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

    pool = None
    if NEON_DATABASE_URL:
        try:
            pool = await asyncpg.create_pool(NEON_DATABASE_URL, min_size=1, max_size=3)
            log.info('Connected to Neon PostgreSQL')
        except Exception as e:
            log.error(f'DB connection failed: {e} — continuing without DB')

    try:
        await asyncio.gather(
            health_server(),
            consume_loop(consumer, bot, pool, producer),
        )
    except Exception:
        _ready = False
        raise
    finally:
        _ready = False
        await consumer.stop()
        await producer.stop()
        if pool:
            await pool.close()


if __name__ == '__main__':
    asyncio.run(main())
