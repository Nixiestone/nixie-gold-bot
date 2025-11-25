import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import config

class DataHandler:
    def __init__(self):
        self.connected = False
        self.symbol = config.SYMBOL
        
    def connect_mt5(self):
        """Connect to MetaTrader 5"""
        try:
            if not mt5.initialize():
                print(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            authorized = mt5.login(
                login=config.MT5_LOGIN,
                password=config.MT5_PASSWORD,
                server=config.MT5_SERVER
            )
            
            if not authorized:
                print(f"MT5 login failed: {mt5.last_error()}")
                mt5.shutdown()
                return False
            
            self.connected = True
            print(" Connected to MetaTrader 5 successfully!")
            
            account_info = mt5.account_info()
            if account_info:
                print(f"Account: {account_info.login}")
                print(f"Balance: ${account_info.balance:.2f}")
                print(f"Equity: ${account_info.equity:.2f}")
            
            return True
            
        except Exception as e:
            print(f"Error connecting to MT5: {e}")
            return False
    
    def disconnect_mt5(self):
        """Disconnect from MetaTrader 5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            print("Disconnected from MetaTrader 5")
    
    def get_gold_data(self, timeframe='H4', bars=500):
        """
        Fetch OHLCV data for gold
        
        Args:
            timeframe: 'H4' or 'M15'
            bars: Number of bars to fetch
        
        Returns:
            DataFrame with OHLCV data
        """
        if not self.connected:
            print("Not connected to MT5. Call connect_mt5() first.")
            return None
        
        try:
            tf_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }
            
            mt5_timeframe = tf_map.get(timeframe, mt5.TIMEFRAME_H4)
            
            rates = mt5.copy_rates_from_pos(self.symbol, mt5_timeframe, 0, bars)
            
            if rates is None or len(rates) == 0:
                print(f"No data received for {self.symbol}")
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            df.rename(columns={
                'time': 'Time',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume'
            }, inplace=True)
            
            df.set_index('Time', inplace=True)
            
            print(f"Fetched {len(df)} bars of {timeframe} data for {self.symbol}")
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def get_current_price(self):
        """Get current bid/ask prices"""
        if not self.connected:
            return None, None
        
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            if tick:
                return tick.bid, tick.ask
            return None, None
        except Exception as e:
            print(f"Error getting current price: {e}")
            return None, None
    
    def get_symbol_info(self):
        """Get symbol specifications"""
        if not self.connected:
            return None
        
        try:
            info = mt5.symbol_info(self.symbol)
            if info:
                return {
                    'point': info.point,
                    'digits': info.digits,
                    'trade_contract_size': info.trade_contract_size,
                    'volume_min': info.volume_min,
                    'volume_max': info.volume_max,
                    'volume_step': info.volume_step
                }
            return None
        except Exception as e:
            print(f"Error getting symbol info: {e}")
            return None
    
    def calculate_pip_value(self, entry_price, lot_size=1.0):
        """
        Calculate pip value for position sizing
        
        For gold: 1 pip = 0.10 price movement
        """
        symbol_info = self.get_symbol_info()
        if not symbol_info:
            return 10.0 * lot_size
        
        pip_value = symbol_info['trade_contract_size'] * 0.10
        return pip_value * lot_size
    
    def price_to_pips(self, price_diff):
        """Convert price difference to pips"""
        return abs(price_diff) / 0.10


if __name__ == "__main__":
    handler = DataHandler()
    
    if handler.connect_mt5():
        df_h4 = handler.get_gold_data('H4', 100)
        df_m15 = handler.get_gold_data('M15', 200)
        
        if df_h4 is not None:
            print("\nH4 Data Sample:")
            print(df_h4.tail())
        
        if df_m15 is not None:
            print("\nM15 Data Sample:")
            print(df_m15.tail())
        
        bid, ask = handler.get_current_price()
        if bid and ask:
            print(f"\n Current Price: Bid={bid:.2f}, Ask={ask:.2f}")
        
        handler.disconnect_mt5()
    else:
        print("Failed to connect to MT5. Check your .env configuration.")