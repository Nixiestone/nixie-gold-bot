import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
import config

class TechnicalIndicators:
    def __init__(self):
        pass
    
    def calculate_all(self, df):
        """
        Calculate all technical indicators on a dataframe
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added indicator columns
        """
        try:
            df = df.copy()
            
            df = self.add_emas(df)
            
            df = self.add_adx(df)
            
            df = self.add_bollinger_bands(df)
            

            df = self.add_rsi(df)
            
            df = self.add_stochastic(df)
            
            df = self.add_macd(df)
            
            df = self.add_atr(df)
            
            df = self.add_volume_analysis(df)
            
            df = df.dropna()
            
            return df
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return df
    
    def add_emas(self, df):
        """Add Exponential Moving Averages"""
        ema_fast = EMAIndicator(close=df['Close'], window=config.EMA_FAST)
        ema_slow = EMAIndicator(close=df['Close'], window=config.EMA_SLOW)
        
        df['EMA_20'] = ema_fast.ema_indicator()
        df['EMA_50'] = ema_slow.ema_indicator()
        
        return df
    
    def add_adx(self, df):
        """Add Average Directional Index (trend strength)"""
        adx = ADXIndicator(
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            window=14
        )
        
        df['ADX'] = adx.adx()
        df['ADX_POS'] = adx.adx_pos()
        df['ADX_NEG'] = adx.adx_neg()
        
        return df
    
    def add_bollinger_bands(self, df):
        """Add Bollinger Bands"""
        bb = BollingerBands(
            close=df['Close'],
            window=20,
            window_dev=2
        )
        
        df['BB_upper'] = bb.bollinger_hband()
        df['BB_middle'] = bb.bollinger_mavg()
        df['BB_lower'] = bb.bollinger_lband()
        df['BB_width'] = bb.bollinger_wband()
        
        return df
    
    def add_rsi(self, df):
        """Add Relative Strength Index"""
        rsi = RSIIndicator(close=df['Close'], window=config.RSI_PERIOD)
        df['RSI'] = rsi.rsi()
        
        return df
    
    def add_stochastic(self, df):
        """Add Stochastic Oscillator"""
        stoch = StochasticOscillator(
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            window=config.STOCH_PERIOD,
            smooth_window=config.STOCH_SMOOTH_K
        )
        
        df['Stoch_K'] = stoch.stoch()
        df['Stoch_D'] = stoch.stoch_signal()
        
        return df
    
    def add_macd(self, df):
        """Add MACD"""
        macd = MACD(
            close=df['Close'],
            window_fast=config.MACD_FAST,
            window_slow=config.MACD_SLOW,
            window_sign=config.MACD_SIGNAL
        )
        
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['MACD_diff'] = macd.macd_diff()
        
        return df
    
    def add_atr(self, df):
        """Add Average True Range (volatility)"""
        atr = AverageTrueRange(
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            window=config.ATR_PERIOD
        )
        
        df['ATR'] = atr.average_true_range()
        
        return df
    
    def add_volume_analysis(self, df):
        """Add volume-based indicators"""
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        df['PVT'] = ((df['Close'] - df['Close'].shift(1)) / df['Close'].shift(1) * df['Volume']).cumsum()
        
        return df
    
    def check_rsi_divergence(self, df, lookback=14):
        """
        Check for RSI divergence (bullish or bearish)
        Returns: 'bullish', 'bearish', or None
        """
        try:
            recent_df = df.tail(lookback)
            
            price_lower_low = recent_df['Low'].iloc[-1] < recent_df['Low'].iloc[0]
            rsi_higher_low = recent_df['RSI'].iloc[-1] > recent_df['RSI'].iloc[0]
            
            if price_lower_low and rsi_higher_low:
                return 'bullish'
            
            price_higher_high = recent_df['High'].iloc[-1] > recent_df['High'].iloc[0]
            rsi_lower_high = recent_df['RSI'].iloc[-1] < recent_df['RSI'].iloc[0]
            
            if price_higher_high and rsi_lower_high:
                return 'bearish'
            
            return None
            
        except Exception as e:
            return None
    
    def check_macd_divergence(self, df, lookback=14):
        """
        Check for MACD divergence
        Returns: 'bullish', 'bearish', or None
        """
        try:
            recent_df = df.tail(lookback)
            
            price_lower_low = recent_df['Low'].iloc[-1] < recent_df['Low'].iloc[0]
            macd_higher_low = recent_df['MACD'].iloc[-1] > recent_df['MACD'].iloc[0]
            
            if price_lower_low and macd_higher_low:
                return 'bullish'
            
            price_higher_high = recent_df['High'].iloc[-1] > recent_df['High'].iloc[0]
            macd_lower_high = recent_df['MACD'].iloc[-1] < recent_df['MACD'].iloc[0]
            
            if price_higher_high and macd_lower_high:
                return 'bearish'
            
            return None
            
        except Exception as e:
            return None


if __name__ == "__main__":
    from data.data_handler import DataHandler
    
    handler = DataHandler()
    if handler.connect_mt5():
        df = handler.get_gold_data('H4', 200)
        
        if df is not None:
            tech = TechnicalIndicators()
            df = tech.calculate_all(df)
            
            print("Technical Indicators Sample:")
            print(df[['Close', 'EMA_20', 'EMA_50', 'RSI', 'ADX', 'MACD']].tail(10))
            
            rsi_div = tech.check_rsi_divergence(df)
            macd_div = tech.check_macd_divergence(df)
            
            print(f"\nRSI Divergence: {rsi_div if rsi_div else 'None'}")
            print(f"MACD Divergence: {macd_div if macd_div else 'None'}")
        
        handler.disconnect_mt5()