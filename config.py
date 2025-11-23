import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

MT5_LOGIN = int(os.getenv('MT5_LOGIN', 0))
MT5_PASSWORD = os.getenv('MT5_PASSWORD')
MT5_SERVER = os.getenv('MT5_SERVER')
SYMBOL = os.getenv('SYMBOL', 'XAUUSDm')

ACCOUNT_BALANCE = float(os.getenv('ACCOUNT_BALANCE', 10000))
RISK_PERCENT = float(os.getenv('RISK_PERCENT', 1.5))
MAX_RISK_PERCENT = float(os.getenv('MAX_RISK_PERCENT', 2.0))


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

MIN_RISK_REWARD = 1.5
MAX_STOP_LOSS_PIPS = 30
TP1_RATIO = 1.5
TP2_RATIO = 2.5
TP3_RATIO = 4.0
TP1_SIZE_PERCENT = 45
TP2_SIZE_PERCENT = 30
TP3_SIZE_PERCENT = 25

LONDON_OPEN = 8
LONDON_CLOSE = 16
NY_OPEN = 13
NY_CLOSE = 21

TIMEFRAME_H4 = 'H4'
TIMEFRAME_M15 = 'M15'

USE_ML_FILTER = True
ML_CONFIDENCE_THRESHOLD = 0.65
ML_MODEL_PATH = 'models/trained_model.pkl'
ML_TRAINING_SAMPLES = 1000

BACKTEST_START_DATE = '2023-01-01'
BACKTEST_END_DATE = '2025-09-28'
BACKTEST_INITIAL_CAPITAL = 100


LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/trading.log'


SCAN_INTERVAL_MINUTES = 15


ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
DRY_RUN = ENVIRONMENT == 'development'  # Don't send real trades in development

# WARNING: Set to True to execute trades automatically!
AUTO_TRADE = True

def validate_config():
    """Validate that all required config is set"""
    errors = []
    
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN not set in .env file")
    
    if not TELEGRAM_CHAT_ID:
        errors.append("TELEGRAM_CHAT_ID not set in .env file")
    
    if MT5_LOGIN == 0:
        errors.append("MT5_LOGIN not set in .env file")
    
    if not MT5_PASSWORD:
        errors.append("MT5_PASSWORD not set in .env file")
    
    if not MT5_SERVER:
        errors.append("MT5_SERVER not set in .env file")
    
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Configuration validated successfully!")
    return True

if __name__ == "__main__":
    validate_config()