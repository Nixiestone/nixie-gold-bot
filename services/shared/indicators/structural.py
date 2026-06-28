import pandas as pd
import numpy as np
from data.market_hours import MarketHours


class StructuralLevels:
    def __init__(self):
        self.market_hours = MarketHours()

    def identify_key_levels(self, df_h4, df_daily=None):
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
            levels['fibonacci'] = self.calculate_fibonacci_levels(df_h4)
            current_price = df_h4['Close'].iloc[-1]
            levels['round_numbers'] = self.get_round_number_levels(current_price)
            return levels
        except Exception as e:
            print(f'Error identifying structural levels: {e}')
            return {}

    def get_weekly_open(self, df):
        try:
            return df.resample('W-MON', label='left', closed='left').first()['Open'].iloc[-1]
        except Exception:
            return df['Open'].iloc[0]

    def find_recent_swing_points(self, df, lookback=50):
        try:
            recent = df.tail(lookback)
            return recent['High'].max(), recent['Low'].min()
        except Exception:
            return None, None

    def calculate_fibonacci_levels(self, df, lookback=100):
        try:
            recent = df.tail(lookback)
            high = recent['High'].max()
            low = recent['Low'].min()
            r = high - low
            return {
                '0.0': low,
                '23.6': low + r * 0.236,
                '38.2': low + r * 0.382,
                '50.0': low + r * 0.500,
                '61.8': low + r * 0.618,
                '78.6': low + r * 0.786,
                '100.0': high,
            }
        except Exception:
            return {}

    def get_round_number_levels(self, current_price):
        try:
            base = int(current_price / 50) * 50
            return [base - 100, base - 50, base, base + 50, base + 100]
        except Exception:
            return []

    def find_nearest_level(self, current_price, levels, max_distance_pips=20):
        try:
            nearest_level = None
            nearest_distance = float('inf')
            nearest_name = None

            for level_name, level_price in levels.items():
                if level_name == 'fibonacci':
                    for fib_name, fib_price in level_price.items():
                        dist = abs(current_price - fib_price) / 0.10
                        if dist <= max_distance_pips and dist < nearest_distance:
                            nearest_distance = dist
                            nearest_level = fib_price
                            nearest_name = f'Fib {fib_name}'
                    continue
                if level_name == 'round_numbers':
                    for rn in level_price:
                        dist = abs(current_price - rn) / 0.10
                        if dist <= max_distance_pips and dist < nearest_distance:
                            nearest_distance = dist
                            nearest_level = rn
                            nearest_name = f'Round ${int(rn)}'
                    continue
                if level_price is not None:
                    dist = abs(current_price - level_price) / 0.10
                    if dist <= max_distance_pips and dist < nearest_distance:
                        nearest_distance = dist
                        nearest_level = level_price
                        nearest_name = level_name.upper()

            return (nearest_level, nearest_name, nearest_distance) if nearest_level else (None, None, None)
        except Exception as e:
            print(f'Error finding nearest level: {e}')
            return None, None, None

    def check_liquidity_sweep(self, df, level_price, lookback=10):
        try:
            recent = df.tail(lookback)
            for i in range(len(recent) - 2, 0, -1):
                bar = recent.iloc[i]
                prev_bar = recent.iloc[i - 1]
                next_bar = recent.iloc[i + 1]
                if bar['High'] > level_price and prev_bar['High'] <= level_price:
                    if bar['Close'] < level_price or next_bar['Close'] < level_price:
                        return {'detected': True, 'direction': 'above', 'sweep_price': bar['High']}
                if bar['Low'] < level_price and prev_bar['Low'] >= level_price:
                    if bar['Close'] > level_price or next_bar['Close'] > level_price:
                        return {'detected': True, 'direction': 'below', 'sweep_price': bar['Low']}
            return {'detected': False, 'direction': 'none'}
        except Exception as e:
            print(f'Error checking liquidity sweep: {e}')
            return {'detected': False, 'direction': 'none'}
