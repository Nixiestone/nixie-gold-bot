import os
import sys
from pathlib import Path

def create_launcher():
    """Create launcher script"""
    launcher_code = '''"""
Launcher Script - Keeps the trading bot running 24/7
Automatically restarts if bot crashes
"""

import subprocess
import time
import sys
import logging
from datetime import datetime
import os

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/launcher.log'),
        logging.StreamHandler()
    ]
)

# The main bot script
BOT_SCRIPT = "main.py"

# Restart settings
MAX_RESTARTS_PER_HOUR = 10  # Prevent infinite restart loop
restart_times = []

def clean_old_restart_times():
    """Remove restart times older than 1 hour"""
    global restart_times
    one_hour_ago = time.time() - 3600
    restart_times = [t for t in restart_times if t > one_hour_ago]

def can_restart():
    """Check if we can restart (not too many restarts recently)"""
    clean_old_restart_times()
    return len(restart_times) < MAX_RESTARTS_PER_HOUR

def run_bot():
    """Start the trading bot"""
    logging.info(f"Starting {BOT_SCRIPT}...")
    
    try:
        # Start bot as subprocess
        process = subprocess.Popen(
            [sys.executable, BOT_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return process
        
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        return None

def monitor_bot(process):
    """Monitor bot output and status"""
    try:
        # Wait for bot to finish
        return_code = process.wait()
        
        if return_code == 0:
            logging.info("Bot stopped normally")
        else:
            logging.warning(f"Bot exited with code {return_code}")
            
        return return_code
        
    except KeyboardInterrupt:
        logging.info("Launcher stopped by user")
        process.terminate()
        raise

def main():
    """Main launcher loop"""
    logging.info("=" * 60)
    logging.info("Nixie's Gold Bot Launcher - Starting")
    logging.info("=" * 60)
    
    while True:
        try:
            # Check if we can restart
            if not can_restart():
                logging.error("Too many restarts in the last hour!")
                logging.error("Waiting 10 minutes before trying again...")
                time.sleep(600)  # Wait 10 minutes
                restart_times.clear()
                continue
            
            # Record restart time
            restart_times.append(time.time())
            
            # Start the bot
            process = run_bot()
            
            if process is None:
                logging.error("Failed to start bot. Retrying in 30 seconds...")
                time.sleep(30)
                continue
            
            # Monitor until it stops
            return_code = monitor_bot(process)
            
            # Bot stopped - decide what to do
            logging.warning("Bot stopped! Restarting in 10 seconds...")
            logging.warning(f"Restarts in last hour: {len(restart_times)}")
            
            time.sleep(10)
            
        except KeyboardInterrupt:
            logging.info("Launcher stopped by user (Ctrl+C)")
            break
        except Exception as e:
            logging.error(f"Launcher error: {e}")
            logging.error("Restarting in 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    main()
'''
    
    with open('launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    
    print("✅ Created launcher.py")

def create_directories():
    """Create necessary directories"""
    dirs = ['logs', 'models', 'data']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")

def create_startup_batch():
    """Create Windows startup batch file"""
    batch_content = """@echo off
echo Starting Nixie's Gold Bot...
cd /d "%~dp0"
python launcher.py
pause
"""
    
    with open('start_bot.bat', 'w') as f:
        f.write(batch_content)
    
    print("✅ Created start_bot.bat")

def create_requirements_minimal():
    """Create minimal requirements for AWS"""
    requirements = """# Minimal requirements for AWS Free Tier
pandas>=2.0.0
numpy>=1.24.0
MetaTrader5>=5.0.45
python-telegram-bot>=20.0
schedule>=1.2.0
ta>=0.11.0
python-dotenv>=1.0.0
pytz>=2023.3
colorama>=0.4.6
"""
    
    with open('requirements_aws.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created requirements_aws.txt (minimal version)")

def create_env_template():
    """Create .env template if it doesn't exist"""
    if not os.path.exists('.env'):
        env_template = """# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# MetaTrader 5 Configuration
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server

# Trading Configuration
ACCOUNT_BALANCE=10000
RISK_PERCENT=1.5
SYMBOL=XAUUSDm

# Environment
ENVIRONMENT=production
"""
        with open('.env', 'w') as f:
            f.write(env_template)
        
        print("✅ Created .env template")
        print("⚠️  IMPORTANT: Edit .env file with your actual credentials!")
    else:
        print("✅ .env file already exists")

def create_health_check():
    """Create health check script"""
    health_check = """import os
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
"""
    
    with open('health_check.py', 'w', encoding='utf-8') as f:
        f.write(health_check)
    
    print("✅ Created health_check.py")

def optimize_config():
    """Update config.py for AWS optimization"""
    print("\nOptimization Tips for config.py:")
    print("   1. Set SCAN_INTERVAL_MINUTES = 15 (don't scan too frequently)")
    print("   2. Set USE_ML_FILTER = False initially (saves memory)")
    print("   3. Keep indicator lookback periods reasonable")

def main():
    """Run all setup tasks"""
    print("Setting up Nixie's Gold Bot for AWS")
    print("=" * 60)
    
    create_directories()
    create_launcher()
    create_startup_batch()
    create_requirements_minimal()
    create_env_template()
    create_health_check()
    optimize_config()
    
    print("\n" + "=" * 60)
    print("AWS Setup Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Edit .env file with your credentials")
    print("2. Install requirements: pip install -r requirements_aws.txt")
    print("3. Run health check: python health_check.py")
    print("4. Test bot: python main.py")
    print("5. Start launcher: python launcher.py")
    print("\nTo start bot on Windows: Double-click start_bot.bat")

if __name__ == "__main__":
    main()