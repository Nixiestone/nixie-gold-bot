"""
Run backtest with optimized parameters
This version is more lenient to generate more signals for testing
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import config

# Temporarily adjust parameters for backtesting
print("🔧 Adjusting parameters for backtest...")
print(f"Original RSI Oversold: {config.RSI_OVERSOLD}")
print(f"Original RSI Overbought: {config.RSI_OVERBOUGHT}")

# Make conditions less strict for backtesting
config.RSI_OVERSOLD = 40  # Was 35
config.RSI_OVERBOUGHT = 60  # Was 65
config.ADX_THRESHOLD_TRENDING = 20  # Was 25 (allow weaker trends)

print(f"Adjusted RSI Oversold: {config.RSI_OVERSOLD}")
print(f"Adjusted RSI Overbought: {config.RSI_OVERBOUGHT}")
print()

from backtest.backtester import Backtester

# Run backtest
backtester = Backtester()

# Test recent period (last 3 months)
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

print(f"🔍 Running backtest with relaxed parameters...")
print(f"Period: {start_date} to {end_date}")
print(f"This should generate more signals for analysis\n")

results = backtester.run_backtest(start_date, end_date, initial_capital=10000)

if results:
    print("\n✅ Backtest complete!")
    print("\n💡 TIP: If you want stricter signals (higher quality), adjust:")
    print("   - RSI_OVERSOLD back to 35")
    print("   - RSI_OVERBOUGHT back to 65")
    print("   in config.py")
else:
    print("\n⚠️  Still no signals? Try:")
    print("1. Check a different time period")
    print("2. Verify MT5 data is complete")
    print("3. Run: python data/data_handler.py to check data quality")