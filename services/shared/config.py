"""
Cloud-compatible config for distributed trading services.
MT5 credentials are removed; Alpha Vantage + Kafka + Neon replace them.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Market data ---
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')
SYMBOL = os.getenv('SYMBOL', 'XAUUSD')
POLL_INTERVAL_SECONDS = int(os.getenv('POLL_INTERVAL_SECONDS', 3480))  # 58 min -> 25 calls/day

# --- Kafka ---
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'redpanda:9092')
TOPIC_RAW_TICKS = 'raw.ticks'
TOPIC_SIGNALS = 'processed.signals'
TOPIC_ORDERS = 'executed.orders'

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# --- Database ---
NEON_DATABASE_URL = os.getenv('NEON_DATABASE_URL', '')

# --- Account ---
ACCOUNT_BALANCE = float(os.getenv('ACCOUNT_BALANCE', 10000))
RISK_PERCENT = float(os.getenv('RISK_PERCENT', 1.5))
MAX_RISK_PERCENT = float(os.getenv('MAX_RISK_PERCENT', 2.0))

# --- Indicators ---
ADX_THRESHOLD_TRENDING = 25
ADX_THRESHOLD_RANGING = 20
BB_WIDTH_THRESHOLD = 0.02

EMA_FAST = 20
EMA_SLOW = 50
RSI_PERIOD = 14
RSI_OVERSOLD = 35
RSI_OVERBOUGHT = 65
STOCH_PERIOD = 5
STOCH_SMOOTH_K = 3
STOCH_SMOOTH_D = 3
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
ATR_PERIOD = 14

# --- Risk ---
MIN_RISK_REWARD = 1.5
MAX_STOP_LOSS_PIPS = 30
TP1_RATIO = 1.5
TP2_RATIO = 2.5
TP3_RATIO = 4.0
TP1_SIZE_PERCENT = 45
TP2_SIZE_PERCENT = 30
TP3_SIZE_PERCENT = 25

# --- Sessions (GMT) ---
LONDON_OPEN = 8
LONDON_CLOSE = 16
NY_OPEN = 13
NY_CLOSE = 21

# --- Timeframes ---
TIMEFRAME_H4 = 'H4'
TIMEFRAME_M15 = 'M15'

# --- Signal processor ---
MIN_H4_BARS = 100   # minimum H4 bars before generating signals
MIN_M15_BARS = 200  # minimum M15 bars before generating signals

# --- Logging ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
