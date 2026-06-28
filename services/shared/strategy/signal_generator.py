"""
Signal Generator — cloud-adapted version.
MT5 dependency removed; uses config.ACCOUNT_BALANCE for position sizing.
"""
from datetime import datetime
import config
from data.market_hours import MarketHours
from strategy.regime_detector import RegimeDetector
from strategy.risk_manager import RiskManager
from indicators.technical import TechnicalIndicators
from indicators.structural import StructuralLevels


class SignalGenerator:
    def __init__(self):
        self.market_hours = MarketHours()
        self.regime_detector = RegimeDetector()
        self.risk_manager = RiskManager()
        self.technical = TechnicalIndicators()
        self.structural = StructuralLevels()

    def generate_signal(self, df_h4, df_m15, timestamp=None):
        """
        Generate a trading signal from H4 (trend/structure) and M15 (entry) data.
        Returns a signal dict or None.
        """
        try:
            should_trade, reason = self.market_hours.should_trade_now(timestamp)
            if not should_trade:
                return None

            regime, adx = self.regime_detector.detect_regime(df_h4)
            if not self.regime_detector.is_favorable_regime(regime):
                return None

            levels = self.structural.identify_key_levels(df_h4)
            if not levels:
                return None

            current_price = df_m15['Close'].iloc[-1]
            nearest_level, level_name, distance = self.structural.find_nearest_level(current_price, levels)
            if not nearest_level:
                return None

            sweep = self.structural.check_liquidity_sweep(df_m15, nearest_level)
            if not sweep['detected']:
                return None

            signal = None
            if sweep['direction'] == 'below':
                signal = self._check_long_conditions(df_m15, current_price, nearest_level, regime)
            elif sweep['direction'] == 'above':
                signal = self._check_short_conditions(df_m15, current_price, nearest_level, regime)

            if signal:
                signal['timestamp'] = datetime.utcnow().isoformat()
                signal['regime'] = self.regime_detector.get_regime_description(regime)
                signal['level_name'] = level_name
                signal['session'] = self.market_hours.get_current_session()

            return signal
        except Exception as e:
            print(f'Error generating signal: {e}')
            return None

    def _check_long_conditions(self, df, current_price, level, regime):
        try:
            rsi = df['RSI'].iloc[-1]
            stoch_k = df['Stoch_K'].iloc[-1]
            stoch_d = df['Stoch_D'].iloc[-1]
            rsi_div = self.technical.check_rsi_divergence(df)

            rsi_ok = rsi < config.RSI_OVERSOLD or rsi_div == 'bullish'
            stoch_ok = stoch_k > stoch_d and stoch_k < 30
            close_above = current_price > level

            if not (rsi_ok and stoch_ok and close_above):
                return None
            return self._build_signal('LONG', current_price, level, df, regime)
        except Exception as e:
            print(f'Error checking LONG conditions: {e}')
            return None

    def _check_short_conditions(self, df, current_price, level, regime):
        try:
            rsi = df['RSI'].iloc[-1]
            stoch_k = df['Stoch_K'].iloc[-1]
            stoch_d = df['Stoch_D'].iloc[-1]
            rsi_div = self.technical.check_rsi_divergence(df)

            rsi_ok = rsi > config.RSI_OVERBOUGHT or rsi_div == 'bearish'
            stoch_ok = stoch_k < stoch_d and stoch_k > 70
            close_below = current_price < level

            if not (rsi_ok and stoch_ok and close_below):
                return None
            return self._build_signal('SHORT', current_price, level, df, regime)
        except Exception as e:
            print(f'Error checking SHORT conditions: {e}')
            return None

    def _build_signal(self, direction, entry_price, level, df, regime):
        try:
            stop_loss = (level - 1.0) if direction == 'LONG' else (level + 1.0)
            pip_risk = self.risk_manager.price_to_pips(entry_price - stop_loss)
            if pip_risk > config.MAX_STOP_LOSS_PIPS:
                return None

            tp1, tp2, tp3 = self.risk_manager.calculate_targets(entry_price, stop_loss, direction)
            if not self.risk_manager.validate_risk_reward(entry_price, stop_loss, tp1):
                return None

            account_balance = config.ACCOUNT_BALANCE
            lot_size = self.risk_manager.calculate_position_size(account_balance, entry_price, stop_loss)
            if lot_size == 0:
                return None

            metrics = self.risk_manager.calculate_risk_metrics(
                entry_price, stop_loss, tp1, tp2, tp3, account_balance
            )
            confidence = self._calculate_confidence(df, regime, pip_risk)

            return {
                'signal': direction,
                'entry_price': round(entry_price, 2),
                'stop_loss': round(stop_loss, 2),
                'take_profit_1': round(tp1, 2),
                'take_profit_2': round(tp2, 2),
                'take_profit_3': round(tp3, 2),
                'lot_size': lot_size,
                'confidence': confidence,
                'pips_risk': round(metrics['pip_risk'], 1),
                'rr_ratio': round(metrics['rr_ratio'], 2),
                'risk_dollars': round(metrics['risk_dollars'], 2),
                'expected_reward': round(metrics['expected_reward'], 2),
            }
        except Exception as e:
            print(f'Error building signal: {e}')
            return None

    def _calculate_confidence(self, df, regime, pip_risk):
        try:
            confidence = 50
            if self.technical.check_rsi_divergence(df):
                confidence += 15
            if self.technical.check_macd_divergence(df):
                confidence += 10
            if regime in ('range', 'breakout_pending'):
                confidence += 10
            if pip_risk < 20:
                confidence += 10
            if df['Volume_Ratio'].iloc[-1] > 1.2:
                confidence += 5
            return min(confidence, 100)
        except Exception:
            return 50
