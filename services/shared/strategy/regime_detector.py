import config


class RegimeDetector:
    def detect_regime(self, df):
        try:
            adx = df['ADX'].iloc[-1]
            ema_20 = df['EMA_20'].iloc[-1]
            ema_50 = df['EMA_50'].iloc[-1]
            close = df['Close'].iloc[-1]
            bb_width = (df['BB_upper'].iloc[-1] - df['BB_lower'].iloc[-1]) / close

            if adx > config.ADX_THRESHOLD_TRENDING:
                return ('trending_bull', adx) if ema_20 > ema_50 else ('trending_bear', adx)
            elif adx < config.ADX_THRESHOLD_RANGING and bb_width < config.BB_WIDTH_THRESHOLD:
                return 'range', adx
            return 'breakout_pending', adx
        except Exception as e:
            print(f'Error detecting regime: {e}')
            return 'unknown', 0

    def is_favorable_regime(self, regime):
        return regime in {'range', 'breakout_pending', 'trending_bull', 'trending_bear'}

    def get_regime_description(self, regime):
        return {
            'trending_bull': 'Strong Uptrend',
            'trending_bear': 'Strong Downtrend',
            'range': 'Range-bound',
            'breakout_pending': 'Breakout Pending',
            'unknown': 'Unknown',
        }.get(regime, regime)
