import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from data.market_hours import MarketHours

class StructuralLevels:
    def __init__(self):
        self.market_hours = MarketHours()
    
    def identify_key_levels(self, df_h4, df_daily=None):
        """
        Identify all key structural levels
        
        Returns dict with levels:
        {
            'pdh': Previous Day High,
            'pdl': Previous Day Low,
            'pdc': Previous Day Close,
            'asian_high': Asian session high,
            'asian_low': Asian session low,
            'weekly_open': Weekly opening price,
            'swing_high': Recent swing high,
            'swing_low': Recent swing low,
            'fibonacci_levels': [...]
        }
        """
        levels = {}
        
        try:
            pd_levels = self.market_hours.get_previous_day_levels(df_h4)
            if pd_levels:
                levels.update(pd_levels)
            
            asian_high, asian_low = self.market_hours.get_asian_range(df_h4)
            if asian_high and asian_low:
                levels['asian_high'] = asian_high
                levels['asian_low'] = asian_low
            
            levels['weekly_open'] = self.get_weekly_open(df_h4)
            
            swing_high, swing_low = self.find_recent_swing_points(df_h4)
            levels['swing_high'] = swing_high
            levels['swing_low'] = swing_low
            
            fib_levels = self.calculate_fibonacci_levels(df_h4)
            levels['fibonacci'] = fib_levels
            
            current_price = df_h4['Close'].iloc[-1]
            levels['round_numbers'] = self.get_round_number_levels(current_price)
            
            return levels
            
        except Exception as e:
            print(f"Error identifying structural levels: {e}")
            return {}
    
    def get_weekly_open(self, df):
        """Get the opening price of the week (Monday)"""
        try:
            df_weekly = df.resample('W-MON', label='left', closed='left').first()
            return df_weekly['Open'].iloc[-1]
        except:
            return df['Open'].iloc[0]
    
    def find_recent_swing_points(self, df, lookback=50):
        """
        Find recent swing highs and lows
        Uses pivot points logic
        """
        try:
            recent_df = df.tail(lookback)
            
            swing_high = recent_df['High'].max()
            
            swing_low = recent_df['Low'].min()
            
            return swing_high, swing_low
            
        except Exception as e:
            print(f"Error finding swing points: {e}")
            return None, None
    
    def calculate_fibonacci_levels(self, df, lookback=100):
        """
        Calculate Fibonacci retracement levels from last major swing
        """
        try:
            recent_df = df.tail(lookback)
            
            swing_high = recent_df['High'].max()
            swing_low = recent_df['Low'].min()
            
            range_val = swing_high - swing_low
            
            fib_levels = {
                '0.0': swing_low,
                '23.6': swing_low + (range_val * 0.236),
                '38.2': swing_low + (range_val * 0.382),
                '50.0': swing_low + (range_val * 0.500),
                '61.8': swing_low + (range_val * 0.618),
                '78.6': swing_low + (range_val * 0.786),
                '100.0': swing_high
            }
            
            return fib_levels
            
        except Exception as e:
            print(f"Error calculating Fibonacci levels: {e}")
            return {}
    
    def get_round_number_levels(self, current_price):
        """
        Get psychological round number levels near current price
        For gold: 1900, 1950, 2000, 2050, etc.
        """
        try:
            base = int(current_price / 50) * 50
            
            levels = [
                base - 100,
                base - 50,
                base,
                base + 50,
                base + 100
            ]
            
            return levels
            
        except Exception as e:
            return []
    
    def find_nearest_level(self, current_price, levels, max_distance_pips=20):
        """
        Find the nearest structural level to current price
        
        Returns: (level_price, level_name, distance_pips)
        """
        try:
            nearest_level = None
            nearest_distance = float('inf')
            nearest_name = None
            
            for level_name, level_price in levels.items():
                if level_name == 'fibonacci':

                    for fib_name, fib_price in level_price.items():
                        distance = abs(current_price - fib_price)
                        distance_pips = distance / 0.10
                        
                        if distance_pips <= max_distance_pips and distance_pips < nearest_distance:
                            nearest_distance = distance_pips
                            nearest_level = fib_price
                            nearest_name = f"Fib {fib_name}"
                    continue
                
                if level_name == 'round_numbers':

                    for rn_price in level_price:
                        distance = abs(current_price - rn_price)
                        distance_pips = distance / 0.10
                        
                        if distance_pips <= max_distance_pips and distance_pips < nearest_distance:
                            nearest_distance = distance_pips
                            nearest_level = rn_price
                            nearest_name = f"Round ${int(rn_price)}"
                    continue
                
                if level_price is not None:
                    distance = abs(current_price - level_price)
                    distance_pips = distance / 0.10
                    
                    if distance_pips <= max_distance_pips and distance_pips < nearest_distance:
                        nearest_distance = distance_pips
                        nearest_level = level_price
                        nearest_name = level_name.upper()
            
            if nearest_level:
                return nearest_level, nearest_name, nearest_distance
            
            return None, None, None
            
        except Exception as e:
            print(f"Error finding nearest level: {e}")
            return None, None, None
    
    def check_liquidity_sweep(self, df, level_price, lookback=10):
        """
        Check if price swept a level (stop hunt)
        
        A sweep occurs when:
        1. Price breaks above/below a level
        2. Then quickly reverses back
        
        Returns: {'detected': bool, 'direction': 'above'/'below'/'none'}
        """
        try:
            recent_bars = df.tail(lookback)
            
            for i in range(len(recent_bars) - 2, 0, -1):
                bar = recent_bars.iloc[i]
                prev_bar = recent_bars.iloc[i - 1]
                next_bar = recent_bars.iloc[i + 1]
                
                if bar['High'] > level_price and prev_bar['High'] <= level_price:
                    if bar['Close'] < level_price or next_bar['Close'] < level_price:
                        return {
                            'detected': True,
                            'direction': 'above',
                            'sweep_price': bar['High']
                        }
                
                if bar['Low'] < level_price and prev_bar['Low'] >= level_price:
                    if bar['Close'] > level_price or next_bar['Close'] > level_price:
                        return {
                            'detected': True,
                            'direction': 'below',
                            'sweep_price': bar['Low']
                        }
            
            return {'detected': False, 'direction': 'none'}
            
        except Exception as e:
            print(f"Error checking liquidity sweep: {e}")
            return {'detected': False, 'direction': 'none'}



if __name__ == "__main__":
    from data.data_handler import DataHandler
    
    handler = DataHandler()
    if handler.connect_mt5():
        df_h4 = handler.get_gold_data('H4', 200)
        
        if df_h4 is not None:
            struct = StructuralLevels()
            levels = struct.identify_key_levels(df_h4)
            
            print("Key Structural Levels:")
            for name, value in levels.items():
                if name != 'fibonacci' and name != 'round_numbers':
                    print(f"  {name.upper()}: ${value:.2f}")
            
            print("\nFibonacci Levels:")
            if 'fibonacci' in levels:
                for fib_name, fib_value in levels['fibonacci'].items():
                    print(f"  {fib_name}: ${fib_value:.2f}")
            
            current_price = df_h4['Close'].iloc[-1]
            nearest, name, distance = struct.find_nearest_level(current_price, levels)
            
            if nearest:
                print(f"\nNearest Level to ${current_price:.2f}:")
                print(f"  Level: {name} at ${nearest:.2f}")
                print(f"  Distance: {distance:.1f} pips")
        
        handler.disconnect_mt5()