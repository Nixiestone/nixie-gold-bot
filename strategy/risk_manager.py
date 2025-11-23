import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import config

class RiskManager:
    def calculate_position_size(self, account_balance, entry_price, stop_loss, pip_value=10.0):
        """
        Calculate lot size based on risk percentage
        
        Default pip_value for gold: $10 per pip per lot
        """
        try:
            risk_amount = account_balance * (config.RISK_PERCENT / 1000)
            
            pip_risk = abs(entry_price - stop_loss) / 0.10
            
            if pip_risk > config.MAX_STOP_LOSS_PIPS:
                print(f"Stop loss too wide: {pip_risk:.1f} pips (max: {config.MAX_STOP_LOSS_PIPS})")
                return 0
            
            position_size = risk_amount / (pip_risk * pip_value)
            
            position_size = round(position_size, 2)
            
            if position_size < 0.01:
                position_size = 0.01
            
            return position_size
            
        except Exception as e:
            print(f"Error calculating position size: {e}")
            return 0
    
    def calculate_targets(self, entry, stop_loss, direction):
        """Calculate TP1, TP2, TP3 based on risk/reward ratios"""
        try:
            risk = abs(entry - stop_loss)
            
            if direction == 'LONG':
                tp1 = entry + (risk * config.TP1_RATIO)
                tp2 = entry + (risk * config.TP2_RATIO)
                tp3 = entry + (risk * config.TP3_RATIO)
            else: 
                tp1 = entry - (risk * config.TP1_RATIO)
                tp2 = entry - (risk * config.TP2_RATIO)
                tp3 = entry - (risk * config.TP3_RATIO)
            
            return tp1, tp2, tp3
            
        except Exception as e:
            print(f"Error calculating targets: {e}")
            return None, None, None
    
    def price_to_pips(self, price_diff):
        """Convert price difference to pips"""
        return abs(price_diff) / 0.10
    
    def validate_risk_reward(self, entry, stop_loss, take_profit):
        """Validate minimum risk/reward ratio"""
        try:
            risk = abs(entry - stop_loss)
            reward = abs(take_profit - entry)
            
            if risk == 0:
                return False
            
            rr_ratio = reward / risk
            
            return rr_ratio >= config.MIN_RISK_REWARD
            
        except Exception as e:
            return False