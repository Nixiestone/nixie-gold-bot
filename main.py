"""
Nixie's Gold Bot - Main Execution Script
This brings everything together!
"""

import schedule
import time
from datetime import datetime
import sys
import logging
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Import our modules
import config
from data.data_handler import DataHandler
from data.market_hours import MarketHours
from indicators.technical import TechnicalIndicators
from strategy.signal_generator import SignalGenerator
from execution.telegram_bot import TelegramNotifier, send_text_sync
from execution.telegram_multi_user import MultiUserTelegramBot, send_signal_to_all
from models.ml_model import MLSignalFilter
from models.trade_logger import TradeLogger
from execution.live_trader import LiveTrader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

class NixieGoldBot:
    def __init__(self):
        self.handler = DataHandler()
        self.signal_generator = SignalGenerator()
        self.technical = TechnicalIndicators()
        self.telegram = TelegramNotifier()
        self.multi_user_telegram = MultiUserTelegramBot()  # Multi-user support
        self.ml_filter = MLSignalFilter()
        self.market_hours = MarketHours()
        self.trade_logger = TradeLogger()
        self.live_trader = LiveTrader()
        
        self.signals_today = 0
        self.last_signal_time = None
        self.running = False
        self.auto_trade_enabled = config.AUTO_TRADE  # Safety: disabled by default
        
        print(Fore.CYAN + "=" * 60)
        print(Fore.CYAN + "🤖  NIXIE'S GOLD BOT")
        print(Fore.CYAN + "    Advanced Quantitative Trading System")
        print(Fore.CYAN + "    by Blessing Omoregie")
        print(Fore.CYAN + "=" * 60)
    
    def initialize(self):
        """Initialize bot and connections"""
        try:
            print(Fore.YELLOW + "\n🔧 Initializing bot...")
            
            # Validate configuration
            if not config.validate_config():
                print(Fore.RED + "❌ Configuration validation failed!")
                return False
            
            # Connect to MT5
            print(Fore.YELLOW + "📡 Connecting to MetaTrader 5...")
            if not self.handler.connect_mt5():
                print(Fore.RED + "❌ Failed to connect to MT5")
                return False
            
            # Load ML model if available
            if config.USE_ML_FILTER:
                print(Fore.YELLOW + "🤖 Loading ML model...")
                self.ml_filter.load_model()
            
            # Send startup message to Telegram
            print(Fore.YELLOW + "📱 Sending startup notification...")
            import asyncio
            asyncio.run(self.telegram.send_startup_message())
            
            print(Fore.GREEN + "✅ Bot initialized successfully!")
            return True
            
        except Exception as e:
            print(Fore.RED + f"❌ Initialization error: {e}")
            logging.error(f"Initialization error: {e}")
            return False
    
    def scan_for_signals(self):
        """Main scanning function - looks for trading opportunities"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(Fore.CYAN + f"\n{'=' * 60}")
            print(Fore.CYAN + f"🔍 Scanning for signals at {timestamp}")
            print(Fore.CYAN + f"{'=' * 60}")
            
            # Check if we should trade now
            should_trade, reason = self.market_hours.should_trade_now()
            if not should_trade:
                print(Fore.YELLOW + f"⏸️  {reason}")
                return
            
            # Fetch market data
            print(Fore.YELLOW + "📊 Fetching market data...")
            df_h4 = self.handler.get_gold_data('H4', 200)
            df_m15 = self.handler.get_gold_data('M15', 500)
            
            if df_h4 is None or df_m15 is None:
                print(Fore.RED + "❌ Failed to fetch market data")
                return
            
            # Calculate indicators
            print(Fore.YELLOW + "🔢 Calculating technical indicators...")
            df_h4 = self.technical.calculate_all(df_h4)
            df_m15 = self.technical.calculate_all(df_m15)
            
            # Generate signal
            print(Fore.YELLOW + "🧠 Analyzing market conditions...")
            signal = self.signal_generator.generate_signal(df_h4, df_m15)
            
            if signal:
                # Apply ML filter
                if config.USE_ML_FILTER:
                    print(Fore.YELLOW + "🤖 Applying ML filter...")
                    passes_ml, ml_confidence = self.ml_filter.should_take_signal(
                        df_h4, df_m15, signal
                    )
                    
                    if not passes_ml:
                        print(Fore.RED + f"❌ Signal rejected by ML filter (confidence: {ml_confidence:.2%})")
                        return
                    
                    # Update signal with ML confidence
                    signal['ml_confidence'] = round(ml_confidence * 100, 1)
                
                # Signal approved! Send to Telegram
                self._process_signal(signal, df_h4, df_m15)
            else:
                print(Fore.BLUE + "⏸️  No trading signal at this time")
                print(Fore.BLUE + "   Waiting for next scan...")
            
        except Exception as e:
            error_msg = f"Error in scan_for_signals: {e}"
            print(Fore.RED + f"❌ {error_msg}")
            logging.error(error_msg)
            
            # Send error to Telegram
            try:
                import asyncio
                asyncio.run(self.telegram.send_error(error_msg))
            except:
                pass
    
    def _process_signal(self, signal, df_h4, df_m15):
        """Process and send approved signal"""
        try:
            print(Fore.GREEN + "\n" + "=" * 60)
            print(Fore.GREEN + "🚀 TRADING SIGNAL GENERATED!")
            print(Fore.GREEN + "=" * 60)
            
            # Display signal details
            print(Fore.WHITE + f"\nDirection: {Fore.GREEN if signal['signal'] == 'LONG' else Fore.RED}{signal['signal']}")
            print(Fore.WHITE + f"Entry: ${signal['entry_price']:.2f}")
            print(Fore.WHITE + f"Stop Loss: ${signal['stop_loss']:.2f}")
            print(Fore.WHITE + f"TP1: ${signal['take_profit_1']:.2f}")
            print(Fore.WHITE + f"Confidence: {signal['confidence']}%")
            
            if config.USE_ML_FILTER and 'ml_confidence' in signal:
                print(Fore.WHITE + f"ML Confidence: {signal['ml_confidence']}%")
            
            # Log trade for ML training
            features = self.ml_filter.extract_features(df_h4, df_m15, signal)
            if features is not None:
                self.trade_logger.log_signal(signal, features)
            
            # Send to Telegram
            if not config.DRY_RUN:
                print(Fore.YELLOW + "\n📱 Sending signal to Telegram...")
                import asyncio
                
                # Send to all subscribers
                success = asyncio.run(self.multi_user_telegram.send_signal(signal))
                
                if success:
                    print(Fore.GREEN + f"✅ Signal sent to {success} subscriber(s)!")
                    self.signals_today += 1
                    self.last_signal_time = datetime.now()
                    
                    # Auto-execute trade if enabled
                    if self.auto_trade_enabled:
                        print(Fore.YELLOW + "\n🤖 Auto-trading enabled. Executing trade...")
                        if self.live_trader.execute_trade(signal):
                            print(Fore.GREEN + "✅ Trade executed successfully!")
                        else:
                            print(Fore.RED + "❌ Trade execution failed")
                else:
                    print(Fore.RED + "❌ Failed to send signal")
            else:
                print(Fore.YELLOW + "\n⚠️  DRY RUN MODE - Signal not sent to Telegram")
                print(Fore.YELLOW + "   Set ENVIRONMENT=production in .env to enable live signals")
            
            # Log signal
            logging.info(f"Signal generated: {signal['signal']} at {signal['entry_price']}")
            
        except Exception as e:
            print(Fore.RED + f"❌ Error processing signal: {e}")
            logging.error(f"Error processing signal: {e}")
    
    def run(self):
        """Main run loop"""
        try:
            # Initialize
            if not self.initialize():
                print(Fore.RED + "❌ Failed to initialize bot. Exiting.")
                return
            
            self.running = True
            
            # Schedule scanning
            schedule.every(config.SCAN_INTERVAL_MINUTES).minutes.do(self.scan_for_signals)
            
            print(Fore.GREEN + f"\n✅ Bot is now running!")
            print(Fore.CYAN + f"📊 Scanning every {config.SCAN_INTERVAL_MINUTES} minutes")
            print(Fore.CYAN + f"💰 Risk per trade: {config.RISK_PERCENT}%")
            print(Fore.CYAN + f"🎯 Symbol: {config.SYMBOL}")
            print(Fore.CYAN + f"🤖 ML Filter: {'Enabled' if config.USE_ML_FILTER else 'Disabled'}")
            
            if config.DRY_RUN:
                print(Fore.YELLOW + "\n⚠️  Running in DRY RUN mode (no signals sent)")
            
            print(Fore.CYAN + "\n" + "=" * 60)
            print(Fore.WHITE + "Press Ctrl+C to stop the bot")
            print(Fore.CYAN + "=" * 60 + "\n")
            
            # Run first scan immediately
            self.scan_for_signals()
            
            # Main loop
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n\n⏸️  Bot stopped by user")
            self.shutdown()
        except Exception as e:
            print(Fore.RED + f"\n❌ Fatal error: {e}")
            logging.error(f"Fatal error: {e}")
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        try:
            print(Fore.YELLOW + "\n🔌 Shutting down...")
            
            # Disconnect from MT5
            self.handler.disconnect_mt5()
            
            # Send shutdown message
            if self.signals_today > 0:
                msg = f"🤖 Bot stopped. Signals today: {self.signals_today}"
                send_text_sync(msg)
            
            print(Fore.GREEN + "✅ Shutdown complete")
            self.running = False
            
        except Exception as e:
            print(Fore.RED + f"❌ Error during shutdown: {e}")


def main():
    """Entry point"""
    bot = NixieGoldBot()
    bot.run()


if __name__ == "__main__":
    main()