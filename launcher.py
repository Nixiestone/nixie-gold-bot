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
        logging.FileHandler('logs/launcher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def print_banner():
    """Print startup banner"""
    try:
        # Import colorama for cross-platform colored output
        try:
            from colorama import init, Fore, Style
            init()
        except ImportError:
            # Create dummy color classes if colorama not available
            class DummyColor:
                def __getattr__(self, name):
                    return ''
            Fore = DummyColor()
            Style = DummyColor()
        
        banner = f"""
{Fore.YELLOW}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   {Fore.CYAN}███╗   ██╗██╗██╗  ██╗██╗███████╗´ ███████╗            {Fore.YELLOW}║
║   {Fore.CYAN}████╗  ██║██║╚██╗██╔╝██║██╔════╝ ██╔════╝            {Fore.YELLOW}║
║   {Fore.CYAN}██╔██╗ ██║██║ ╚███╔╝ ██║█████╗   ███████╗            {Fore.YELLOW}║
║   {Fore.CYAN}██║╚██╗██║██║ ██╔██╗ ██║██╔══╝   ╚════██║            {Fore.YELLOW}║
║   {Fore.CYAN}██║ ╚████║██║██╔╝ ██╗██║███████╗ ███████║            {Fore.YELLOW}║
║   {Fore.CYAN}╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝╚═╝╚══════╝ ╚══════╝            {Fore.YELLOW}║
║                                                          ║
║              {Fore.GREEN}🤖 GOLD TRADING BOT - INTRADAY{Fore.YELLOW}              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)
    except Exception as e:
        logging.warning(f"Could not display banner: {e}")


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
        # Start bot as subprocess with proper output handling
        process = subprocess.Popen(
            [sys.executable, BOT_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stdout and stderr
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Start background thread to log bot output
        import threading
        
        def log_output(pipe, logger_func):
            try:
                for line in iter(pipe.readline, ''):
                    if line:
                        logger_func(line.strip())
            except Exception as e:
                logging.error(f"Output logging error: {e}")
            finally:
                pipe.close()
        
        # Start output logging thread
        output_thread = threading.Thread(
            target=log_output,
            args=(process.stdout, logging.info),
            daemon=True
        )
        output_thread.start()
        
        return process
        
    except FileNotFoundError:
        logging.error(f"Bot script '{BOT_SCRIPT}' not found!")
        return None
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        return None


def monitor_bot(process):
    """Monitor bot output and status"""
    try:
        # Wait for bot to finish with timeout to allow KeyboardInterrupt
        while process.poll() is None:
            time.sleep(1)
        
        return_code = process.returncode
        
        if return_code == 0:
            logging.info("Bot stopped normally")
        else:
            logging.warning(f"Bot exited with code {return_code}")
            
        return return_code
        
    except KeyboardInterrupt:
        logging.info("Launcher stopped by user")
        try:
            process.terminate()
            # Give process time to terminate gracefully
            for _ in range(10):
                if process.poll() is not None:
                    break
                time.sleep(0.5)
            else:
                # Force kill if not terminated
                process.kill()
                logging.warning("Bot process force killed")
        except Exception as e:
            logging.error(f"Error terminating bot process: {e}")
        raise
    except Exception as e:
        logging.error(f"Error monitoring bot: {e}")
        return 1


def handle_restart_delay(restart_count):
    """Handle increasing restart delays based on failure count"""
    if restart_count > 5:
        delay = 300  # 5 minutes after 5+ failures
    elif restart_count > 3:
        delay = 120  # 2 minutes after 3-5 failures
    elif restart_count > 1:
        delay = 30   # 30 seconds after 2-3 failures
    else:
        delay = 10   # 10 seconds for first failure
    
    logging.info(f"Restarting in {delay} seconds...")
    time.sleep(delay)


def main():
    """Main launcher loop"""
    logging.info("=" * 60)
    logging.info("Nixie's Gold Bot Launcher - Starting")
    logging.info("=" * 60)
    
    # Print banner at startup
    print_banner()
    
    consecutive_failures = 0
    
    while True:
        try:
            # Check if we can restart
            if not can_restart():
                logging.error("Too many restarts in the last hour!")
                logging.error("Waiting 10 minutes before trying again...")
                time.sleep(600)  # Wait 10 minutes
                restart_times.clear()
                consecutive_failures = 0
                continue
            
            # Record restart time
            restart_times.append(time.time())
            
            # Start the bot
            process = run_bot()
            
            if process is None:
                consecutive_failures += 1
                logging.error(f"Failed to start bot. Consecutive failures: {consecutive_failures}")
                handle_restart_delay(consecutive_failures)
                continue
            
            # Reset consecutive failures on successful start
            consecutive_failures = 0
            
            # Monitor until it stops
            return_code = monitor_bot(process)
            
            # Bot stopped - decide what to do
            logging.warning("Bot stopped! Restarting...")
            logging.warning(f"Restarts in last hour: {len(restart_times)}")
            
            handle_restart_delay(len(restart_times))
            
        except KeyboardInterrupt:
            logging.info("Launcher stopped by user (Ctrl+C)")
            break
        except Exception as e:
            consecutive_failures += 1
            logging.error(f"Launcher error: {e}")
            logging.error(f"Consecutive failures: {consecutive_failures}")
            handle_restart_delay(consecutive_failures)


if __name__ == "__main__":
    main()