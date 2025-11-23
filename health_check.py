import os
import sys
from datetime import datetime

print("Health Check - Nixie's Gold Bot")
print("=" * 50)

# Check Python version
print(f"Python: {sys.version}")

# Check if virtual environment
in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
print(f"Virtual Env: {'Yes' if in_venv else 'No'}")

# Check if .env exists
env_exists = os.path.exists('.env')
print(f".env file: {'Found' if env_exists else 'Missing'}")

# Check if MT5 can import
try:
    import MetaTrader5 as mt5
    print("MT5 Import: Success")
except:
    print("MT5 Import: Failed")

# Check if telegram can import
try:
    import telegram
    print("Telegram Import: Success")
except:
    print("Telegram Import: Failed")

# Check log directory
log_exists = os.path.exists('logs')
print(f"Logs directory: {'Found' if log_exists else 'Missing'}")

print("=" * 50)
print("Health check complete!")
