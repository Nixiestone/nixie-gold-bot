import config


class RiskManager:
    def calculate_position_size(self, account_balance, entry_price, stop_loss, pip_value=10.0):
        try:
            risk_amount = account_balance * (config.RISK_PERCENT / 1000)
            pip_risk = abs(entry_price - stop_loss) / 0.10
            if pip_risk > config.MAX_STOP_LOSS_PIPS:
                return 0
            position_size = risk_amount / (pip_risk * pip_value)
            position_size = round(position_size, 2)
            return max(position_size, 0.01)
        except Exception:
            return 0

    def calculate_targets(self, entry, stop_loss, direction):
        try:
            risk = abs(entry - stop_loss)
            if direction == 'LONG':
                return (
                    entry + risk * config.TP1_RATIO,
                    entry + risk * config.TP2_RATIO,
                    entry + risk * config.TP3_RATIO,
                )
            return (
                entry - risk * config.TP1_RATIO,
                entry - risk * config.TP2_RATIO,
                entry - risk * config.TP3_RATIO,
            )
        except Exception:
            return None, None, None

    def price_to_pips(self, price_diff):
        return abs(price_diff) / 0.10

    def validate_risk_reward(self, entry, stop_loss, take_profit):
        try:
            risk = abs(entry - stop_loss)
            reward = abs(take_profit - entry)
            return risk > 0 and (reward / risk) >= config.MIN_RISK_REWARD
        except Exception:
            return False

    def calculate_risk_metrics(self, entry, stop_loss, tp1, tp2, tp3, account_balance):
        pip_risk = self.price_to_pips(entry - stop_loss)
        pip_tp1 = self.price_to_pips(tp1 - entry)
        pip_tp2 = self.price_to_pips(tp2 - entry)
        pip_tp3 = self.price_to_pips(tp3 - entry)
        risk_dollars = account_balance * (config.RISK_PERCENT / 100)
        rr_ratio = pip_tp1 / pip_risk if pip_risk > 0 else 0
        return {
            'pip_risk': pip_risk,
            'pip_tp1': pip_tp1,
            'pip_tp2': pip_tp2,
            'pip_tp3': pip_tp3,
            'risk_dollars': risk_dollars,
            'expected_reward': risk_dollars * rr_ratio,
            'rr_ratio': rr_ratio,
        }
