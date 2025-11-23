"""
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
