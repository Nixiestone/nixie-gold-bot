"""
Signal Generator - Core trading logic
This is the brain of Nixie's Gold Bot!
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

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
        Main signal generation function
        
        Args:
            df_h4: H4 timeframe data
            df_m15: M15 timeframe data
            timestamp: Optional timestamp for backtesting
        
        Returns: Signal dict or None
        """
        try:
            # Step 1: Check if we should trade now
            should_trade, reason = self.market_hours.should_trade_now(timestamp)
            if not should_trade:
                print(f"⏸️  {reason}")
                return None
            
            # Step 2: Check regime
            regime, adx = self.regime_detector.detect_regime(df_h4)
            if not self.regime_detector.is_favorable_regime(regime):
                print(f"⏸️  Unfavorable regime: {regime}")
                return None
            
            print(f"✅ Trading session active: {self.market_hours.get_current_session()}")
            print(f"✅ Regime: {self.regime_detector.get_regime_description(regime)}")
            
            # Step 3: Identify structural levels
            levels = self.structural.identify_key_levels(df_h4)
            if not levels:
                print("⚠️  No structural levels identified")
                return None
            
            # Step 4: Check for level interaction
            current_price = df_m15['Close'].iloc[-1]
            nearest_level, level_name, distance = self.structural.find_nearest_level(current_price, levels)
            
            if not nearest_level:
                print(f"⏸️  No nearby levels (Current: ${current_price:.2f})")
                return None
            
            print(f"🎯 Near level: {level_name} at ${nearest_level:.2f} ({distance:.1f} pips away)")
            
            # Step 5: Check for liquidity sweep
            sweep = self.structural.check_liquidity_sweep(df_m15, nearest_level)
            if not sweep['detected']:
                print(f"⏸️  No liquidity sweep detected at {level_name}")
                return None
            
            print(f"💥 Liquidity sweep detected! Direction: {sweep['direction']}")
            
            # Step 6: Check momentum conditions
            signal = None
            
            if sweep['direction'] == 'below':
                # Potential LONG
                signal = self._check_long_conditions(df_m15, current_price, nearest_level, regime)
            
            elif sweep['direction'] == 'above':
                # Potential SHORT
                signal = self._check_short_conditions(df_m15, current_price, nearest_level, regime)
            
            if signal:
                # Add metadata
                signal['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                signal['regime'] = self.regime_detector.get_regime_description(regime)
                signal['level_name'] = level_name
                signal['session'] = self.market_hours.get_current_session()
                
                print(f"🚀 SIGNAL GENERATED: {signal['signal']}")
            
            return signal
            
        except Exception as e:
            print(f"❌ Error generating signal: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _check_long_conditions(self, df, current_price, level, regime):
        """Check if all conditions are met for a LONG entry"""
        try:
            # Get indicators
            rsi = df['RSI'].iloc[-1]
            stoch_k = df['Stoch_K'].iloc[-1]
            stoch_d = df['Stoch_D'].iloc[-1]
            
            # Check RSI divergence
            rsi_div = self.technical.check_rsi_divergence(df)
            
            print(f"📊 LONG Check - RSI: {rsi:.1f}, Stoch K: {stoch_k:.1f}, D: {stoch_d:.1f}")
            
            # Conditions for LONG
            rsi_ok = rsi < config.RSI_OVERSOLD or rsi_div == 'bullish'
            stoch_ok = stoch_k > stoch_d and stoch_k < 30
            
            # Price must have closed back above level
            close_above = current_price > level
            
            if not (rsi_ok and stoch_ok and close_above):
                print(f"⏸️  LONG conditions not met:")
                print(f"   RSI oversold or divergence: {rsi_ok}")
                print(f"   Stochastic crossover: {stoch_ok}")
                print(f"   Closed above level: {close_above}")
                return None
            
            # Build LONG signal
            return self._build_signal('LONG', current_price, level, df, regime)
            
        except Exception as e:
            print(f"❌ Error checking LONG conditions: {e}")
            return None
    
    def _check_short_conditions(self, df, current_price, level, regime):
        """Check if all conditions are met for a SHORT entry"""
        try:
            # Get indicators
            rsi = df['RSI'].iloc[-1]
            stoch_k = df['Stoch_K'].iloc[-1]
            stoch_d = df['Stoch_D'].iloc[-1]
            
            # Check RSI divergence
            rsi_div = self.technical.check_rsi_divergence(df)
            
            print(f"📊 SHORT Check - RSI: {rsi:.1f}, Stoch K: {stoch_k:.1f}, D: {stoch_d:.1f}")
            
            # Conditions for SHORT
            rsi_ok = rsi > config.RSI_OVERBOUGHT or rsi_div == 'bearish'
            stoch_ok = stoch_k < stoch_d and stoch_k > 70
            
            # Price must have closed back below level
            close_below = current_price < level
            
            if not (rsi_ok and stoch_ok and close_below):
                print(f"⏸️  SHORT conditions not met:")
                print(f"   RSI overbought or divergence: {rsi_ok}")
                print(f"   Stochastic crossover: {stoch_ok}")
                print(f"   Closed below level: {close_below}")
                return None
            
            # Build SHORT signal
            return self._build_signal('SHORT', current_price, level, df, regime)
            
        except Exception as e:
            print(f"❌ Error checking SHORT conditions: {e}")
            return None
    
    def _build_signal(self, direction, entry_price, level, df, regime):
        """Build complete signal with all details"""
        try:
            # Calculate stop loss
            if direction == 'LONG':
                # Stop below the sweep low
                stop_loss = level - (10 * 0.10)  # 10 pips below
            else:
                # Stop above the sweep high
                stop_loss = level + (10 * 0.10)  # 10 pips above
            
            # Validate stop loss distance
            pip_risk = self.risk_manager.price_to_pips(entry_price - stop_loss)
            if pip_risk > config.MAX_STOP_LOSS_PIPS:
                print(f"⚠️  Stop loss too wide: {pip_risk:.1f} pips")
                return None
            
            # Calculate take profit levels
            tp1, tp2, tp3 = self.risk_manager.calculate_targets(entry_price, stop_loss, direction)
            
            # Validate risk/reward
            if not self.risk_manager.validate_risk_reward(entry_price, stop_loss, tp1):
                print(f"⚠️  Risk/reward ratio too low")
                return None
            
            # Get actual account balance from MT5
            from data.data_handler import DataHandler
            handler = DataHandler()
            account_balance = config.ACCOUNT_BALANCE  # Fallback
            
            # Try to get real balance if connected
            try:
                import MetaTrader5 as mt5
                account_info = mt5.account_info()
                if account_info:
                    account_balance = account_info.balance
                    print(f"💰 Using live account balance: ${account_balance:.2f}")
            except:
                print(f"⚠️  Using config balance: ${account_balance:.2f}")
            
            # Calculate position size
            lot_size = self.risk_manager.calculate_position_size(
                account_balance,
                entry_price,
                stop_loss
            )
            
            if lot_size == 0:
                print(f"⚠️  Position size calculation failed")
                return None
            
            # Calculate all metrics
            metrics = self.risk_manager.calculate_risk_metrics(
                entry_price, stop_loss, tp1, tp2, tp3, account_balance
            )
            
            # Calculate confidence score (0-100)
            confidence = self._calculate_confidence(df, regime, pip_risk)
            
            # Build signal dictionary
            signal = {
                'signal': direction,
                'entry_price': round(entry_price, 2),
                'stop_loss': round(stop_loss, 2),
                'take_profit_1': round(tp1, 2),
                'take_profit_2': round(tp2, 2),
                'take_profit_3': round(tp3, 2),
                'lot_size': lot_size,
                'confidence': confidence,
                'pips_risk': round(metrics['pip_risk'], 1),
                'pips_tp1': round(metrics['pip_tp1'], 1),
                'pips_tp2': round(metrics['pip_tp2'], 1),
                'pips_tp3': round(metrics['pip_tp3'], 1),
                'risk_dollars': round(metrics['risk_dollars'], 2),
                'expected_reward': round(metrics['expected_reward'], 2),
                'rr_ratio': round(metrics['rr_ratio'], 2)
            }
            
            return signal
            
        except Exception as e:
            print(f"❌ Error building signal: {e}")
            return None
    
    def _calculate_confidence(self, df, regime, pip_risk):
        """
        Calculate confidence score (0-100) based on multiple factors
        """
        try:
            confidence = 50  # Base confidence
            
            # RSI divergence adds confidence
            rsi_div = self.technical.check_rsi_divergence(df)
            if rsi_div:
                confidence += 15
            
            # MACD divergence adds confidence
            macd_div = self.technical.check_macd_divergence(df)
            if macd_div:
                confidence += 10
            
            # Favorable regime adds confidence
            if regime in ['range', 'breakout_pending']:
                confidence += 10
            
            # Low risk (tight stop) adds confidence
            if pip_risk < 20:
                confidence += 10
            
            # High volume adds confidence
            volume_ratio = df['Volume_Ratio'].iloc[-1]
            if volume_ratio > 1.2:
                confidence += 5
            
            # Cap at 100
            confidence = min(confidence, 100)
            
            return confidence
            
        except Exception as e:
            return 50  # Default confidence


# Test the signal generator
if __name__ == "__main__":
    from data.data_handler import DataHandler
    
    print("🤖 Testing Nixie's Signal Generator...")
    print("=" * 50)
    
    handler = DataHandler()
    if handler.connect_mt5():
        # Get data
        df_h4 = handler.get_gold_data('H4', 200)
        df_m15 = handler.get_gold_data('M15', 500)
        
        if df_h4 is not None and df_m15 is not None:
            # Calculate indicators
            tech = TechnicalIndicators()
            df_h4 = tech.calculate_all(df_h4)
            df_m15 = tech.calculate_all(df_m15)
            
            # Generate signal
            generator = SignalGenerator()
            signal = generator.generate_signal(df_h4, df_m15)
            
            if signal:
                print("\n" + "=" * 50)
                print("🎯 TRADING SIGNAL GENERATED!")
                print("=" * 50)
                for key, value in signal.items():
                    print(f"{key}: {value}")
            else:
                print("\n⏸️  No trading signal at this time")
        
        handler.disconnect_mt5()
    else:
        print("❌ Failed to connect to MT5")