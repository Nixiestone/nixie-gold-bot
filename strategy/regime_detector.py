import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import config

class RegimeDetector:
    def detect_regime(self, df):
        """
        Detect market regime
        
        Returns: (regime_name, adx_value)
        Regimes: 'trending_bull', 'trending_bear', 'range', 'breakout_pending'
        """
        try:
            adx = df['ADX'].iloc[-1]
            ema_20 = df['EMA_20'].iloc[-1]
            ema_50 = df['EMA_50'].iloc[-1]
            close = df['Close'].iloc[-1]
            
            bb_width = (df['BB_upper'].iloc[-1] - df['BB_lower'].iloc[-1]) / close
            
            if adx > config.ADX_THRESHOLD_TRENDING:
                if ema_20 > ema_50:
                    return 'trending_bull', adx
                else:
                    return 'trending_bear', adx
            
            elif adx < config.ADX_THRESHOLD_RANGING and bb_width < config.BB_WIDTH_THRESHOLD:
                return 'range', adx
            
            else:
                return 'breakout_pending', adx
                
        except Exception as e:
            print(f"Error detecting regime: {e}")
            return 'unknown', 0
    
    def is_favorable_regime(self, regime):
        """Check if regime is good for trading"""
        favorable = ['range', 'breakout_pending', 'trending_bull', 'trending_bear']
        return regime in favorable
    
    def get_regime_description(self, regime):
        """Get human-readable description of regime"""
        descriptions = {
            'trending_bull': '📈 Strong Uptrend',
            'trending_bear': '📉 Strong Downtrend',
            'range': '↔️  Range-bound',
            'breakout_pending': '⚡ Breakout Pending',
            'unknown': '❓ Unknown'
        }
        return descriptions.get(regime, regime)


if __name__ == "__main__":
    from data.data_handler import DataHandler
    from indicators.technical import TechnicalIndicators
    
    handler = DataHandler()
    if handler.connect_mt5():
        df = handler.get_gold_data('H4', 200)
        
        if df is not None:
            tech = TechnicalIndicators()
            df = tech.calculate_all(df)
            
            detector = RegimeDetector()
            regime, adx = detector.detect_regime(df)
            
            print(f"Market Regime: {detector.get_regime_description(regime)}")
            print(f"ADX Value: {adx:.2f}")
            print(f"Favorable: {detector.is_favorable_regime(regime)}")
        
        handler.disconnect_mt5()