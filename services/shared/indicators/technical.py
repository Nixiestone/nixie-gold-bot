import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
import config


class TechnicalIndicators:
    def calculate_all(self, df):
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
            return df.dropna()
        except Exception as e:
            print(f'Error calculating indicators: {e}')
            return df

    def add_emas(self, df):
        df['EMA_20'] = EMAIndicator(close=df['Close'], window=config.EMA_FAST).ema_indicator()
        df['EMA_50'] = EMAIndicator(close=df['Close'], window=config.EMA_SLOW).ema_indicator()
        return df

    def add_adx(self, df):
        adx = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['ADX'] = adx.adx()
        df['ADX_POS'] = adx.adx_pos()
        df['ADX_NEG'] = adx.adx_neg()
        return df

    def add_bollinger_bands(self, df):
        bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_upper'] = bb.bollinger_hband()
        df['BB_middle'] = bb.bollinger_mavg()
        df['BB_lower'] = bb.bollinger_lband()
        df['BB_width'] = bb.bollinger_wband()
        return df

    def add_rsi(self, df):
        df['RSI'] = RSIIndicator(close=df['Close'], window=config.RSI_PERIOD).rsi()
        return df

    def add_stochastic(self, df):
        stoch = StochasticOscillator(
            high=df['High'], low=df['Low'], close=df['Close'],
            window=config.STOCH_PERIOD, smooth_window=config.STOCH_SMOOTH_K
        )
        df['Stoch_K'] = stoch.stoch()
        df['Stoch_D'] = stoch.stoch_signal()
        return df

    def add_macd(self, df):
        macd = MACD(
            close=df['Close'],
            window_fast=config.MACD_FAST,
            window_slow=config.MACD_SLOW,
            window_sign=config.MACD_SIGNAL,
        )
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['MACD_diff'] = macd.macd_diff()
        return df

    def add_atr(self, df):
        df['ATR'] = AverageTrueRange(
            high=df['High'], low=df['Low'], close=df['Close'], window=config.ATR_PERIOD
        ).average_true_range()
        return df

    def add_volume_analysis(self, df):
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        df['PVT'] = (
            (df['Close'] - df['Close'].shift(1)) / df['Close'].shift(1) * df['Volume']
        ).cumsum()
        return df

    def check_rsi_divergence(self, df, lookback=14):
        try:
            recent = df.tail(lookback)
            if recent['Low'].iloc[-1] < recent['Low'].iloc[0] and \
               recent['RSI'].iloc[-1] > recent['RSI'].iloc[0]:
                return 'bullish'
            if recent['High'].iloc[-1] > recent['High'].iloc[0] and \
               recent['RSI'].iloc[-1] < recent['RSI'].iloc[0]:
                return 'bearish'
            return None
        except Exception:
            return None

    def check_macd_divergence(self, df, lookback=14):
        try:
            recent = df.tail(lookback)
            if recent['Low'].iloc[-1] < recent['Low'].iloc[0] and \
               recent['MACD'].iloc[-1] > recent['MACD'].iloc[0]:
                return 'bullish'
            if recent['High'].iloc[-1] > recent['High'].iloc[0] and \
               recent['MACD'].iloc[-1] < recent['MACD'].iloc[0]:
                return 'bearish'
            return None
        except Exception:
            return None
