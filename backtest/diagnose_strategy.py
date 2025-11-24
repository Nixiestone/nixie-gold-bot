"""
Diagnose Strategy - Check why signals aren't generating
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from datetime import datetime, timedelta
import config
from data.data_handler import DataHandler
from indicators.technical import TechnicalIndicators
from indicators.structural import StructuralLevels
from strategy.regime_detector import RegimeDetector
from data.market_hours import MarketHours

print("[SCAN] STRATEGY DIAGNOSTIC TOOL")
print("=" * 60)

# Connect and get data
handler = DataHandler()
if not handler.connect_mt5():
    print("[ERROR] Failed to connect to MT5")
    exit()

print("\n📥 Fetching recent data...")
df_h4 = handler.get_gold_data('H4', 500)
df_m15 = handler.get_gold_data('M15', 1000)

if df_h4 is None or df_m15 is None:
    print("[ERROR] Failed to fetch data")
    handler.disconnect_mt5()
    exit()

# Calculate indicators
print("[CALC] Calculating indicators...")
tech = TechnicalIndicators()
df_h4 = tech.calculate_all(df_h4)
df_m15 = tech.calculate_all(df_m15)

# Analyze last 100 bars
print("\n" + "=" * 60)
print("[DATA] ANALYZING LAST 100 H4 BARS")
print("=" * 60)

detector = RegimeDetector()
market_hours = MarketHours()
structural = StructuralLevels()

favorable_count = 0
session_ok_count = 0
level_near_count = 0
sweep_count = 0
rsi_ok_count = 0

for i in range(-100, 0):
    try:
        current_h4 = df_h4.iloc[:i]
        current_m15 = df_m15[df_m15.index <= current_h4.index[-1]]
        
        if len(current_m15) < 50:
            continue
        
        timestamp = current_h4.index[-1]
        
        # Check regime
        regime, adx = detector.detect_regime(current_h4)
        if detector.is_favorable_regime(regime):
            favorable_count += 1
        
        # Check session
        should_trade, _ = market_hours.should_trade_now(timestamp)
        if should_trade:
            session_ok_count += 1
        
        # Check for nearby levels
        levels = structural.identify_key_levels(current_h4)
        current_price = current_m15['Close'].iloc[-1]
        nearest, name, dist = structural.find_nearest_level(current_price, levels, max_distance_pips=30)
        
        if nearest:
            level_near_count += 1
            
            # Check for sweep
            sweep = structural.check_liquidity_sweep(current_m15, nearest)
            if sweep['detected']:
                sweep_count += 1
        
        # Check RSI
        rsi = current_m15['RSI'].iloc[-1]
        if rsi < config.RSI_OVERSOLD or rsi > config.RSI_OVERBOUGHT:
            rsi_ok_count += 1
            
    except Exception as e:
        continue

print(f"\nCondition Analysis (out of ~100 bars checked):")
print(f"  ✓ Favorable Regime:     {favorable_count:3d} bars ({favorable_count}%)")
print(f"  ✓ Trading Session OK:   {session_ok_count:3d} bars ({session_ok_count}%)")
print(f"  ✓ Near Key Level:       {level_near_count:3d} bars ({level_near_count}%)")
print(f"  ✓ Liquidity Sweep:      {sweep_count:3d} bars ({sweep_count}%)")
print(f"  ✓ RSI Extreme:          {rsi_ok_count:3d} bars ({rsi_ok_count}%)")

# Calculate probability of all conditions meeting
all_conditions = (favorable_count/100) * (session_ok_count/100) * (level_near_count/100) * (sweep_count/100) * (rsi_ok_count/100) * 100

print(f"\n📈 Probability of ALL conditions meeting: ~{all_conditions:.2f}%")

if all_conditions < 1:
    print("\n[WARN]  Strategy is VERY SELECTIVE (< 1% of bars qualify)")
    print("This means:")
    print("  ✓ GOOD: High quality signals only")
    print("  ✗ BAD: Very few trading opportunities")
    print("\n💡 Options:")
    print("  1. Keep strict (recommended) - wait for perfect setups")
    print("  2. Relax RSI thresholds: 35→40 and 65→60")
    print("  3. Increase level detection range: 20→30 pips")

# Show current indicator values
print("\n" + "=" * 60)
print("[DATA] CURRENT MARKET CONDITIONS")
print("=" * 60)

current_price = df_m15['Close'].iloc[-1]
rsi = df_m15['RSI'].iloc[-1]
stoch_k = df_m15['Stoch_K'].iloc[-1]
stoch_d = df_m15['Stoch_D'].iloc[-1]
adx = df_h4['ADX'].iloc[-1]

regime, _ = detector.detect_regime(df_h4)

print(f"Price:           ${current_price:.2f}")
print(f"RSI:             {rsi:.1f} (Oversold < {config.RSI_OVERSOLD}, Overbought > {config.RSI_OVERBOUGHT})")
print(f"Stochastic K:    {stoch_k:.1f}")
print(f"Stochastic D:    {stoch_d:.1f}")
print(f"ADX:             {adx:.1f}")
print(f"Regime:          {detector.get_regime_description(regime)}")

should_trade, reason = market_hours.should_trade_now()
print(f"Session Status:  {reason}")

# Check levels
levels = structural.identify_key_levels(df_h4)
nearest, name, dist = structural.find_nearest_level(current_price, levels)

if nearest:
    print(f"Nearest Level:   {name} at ${nearest:.2f} ({dist:.1f} pips away)")
else:
    print(f"Nearest Level:   None within 20 pips")

handler.disconnect_mt5()

print("\n" + "=" * 60)
print("[SUCCESS] Diagnostic complete!")
print("=" * 60)