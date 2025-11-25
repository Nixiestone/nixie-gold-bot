import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import json
from datetime import datetime
import os

class TradeLogger:
    def __init__(self, log_file='models/trade_history.json'):
        self.log_file = log_file
        self.trades = []
        self.load_history()
    
    def load_history(self):
        """Load existing trade history"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.trades = json.load(f)
                print(f"Loaded {len(self.trades)} historical trades")
            except Exception as e:
                print(f"[WARN]  Could not load history: {e}")
                self.trades = []
    
    def log_signal(self, signal_data, features):
        """
        Log a new signal for tracking
        
        Args:
            signal_data: The signal dictionary
            features: Feature vector used for this signal
        """
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'direction': signal_data['signal'],
            'entry': signal_data['entry_price'],
            'stop_loss': signal_data['stop_loss'],
            'tp1': signal_data['take_profit_1'],
            'confidence': signal_data['confidence'],
            'features': features.tolist() if hasattr(features, 'tolist') else features,
            'outcome': None,  
            'pnl': None,
            'closed_at': None
        }
        
        self.trades.append(trade_record)
        self.save_history()
        print(f" Trade logged: {signal_data['signal']} at ${signal_data['entry_price']}")
    
    def update_outcome(self, timestamp, outcome, pnl):
        """
        Update trade outcome after it closes
        
        Args:
            timestamp: Original trade timestamp
            outcome: 'win' or 'loss'
            pnl: Profit/loss amount
        """
        for trade in self.trades:
            if trade['timestamp'] == timestamp and trade['outcome'] is None:
                trade['outcome'] = outcome
                trade['pnl'] = pnl
                trade['closed_at'] = datetime.now().isoformat()
                self.save_history()
                print(f"[SUCCESS] Trade outcome updated: {outcome} (${pnl:.2f})")
                return True
        
        print(f"  Trade not found: {timestamp}")
        return False
    
    def save_history(self):
        """Save trade history to file"""
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w') as f:
                json.dump(self.trades, f, indent=2)
        except Exception as e:
            print(f" Error saving history: {e}")
    
    def get_completed_trades(self):
        """Get all trades with outcomes"""
        return [t for t in self.trades if t['outcome'] is not None]
    
    def get_training_data(self):
        """
        Convert completed trades to ML training data
        
        Returns:
            X (features), y (labels: 1=win, 0=loss)
        """
        completed = self.get_completed_trades()
        
        if len(completed) == 0:
            print("[WARN]  No completed trades for training")
            return None, None
        
        features = []
        labels = []
        
        for trade in completed:
            features.append(trade['features'])
            labels.append(1 if trade['outcome'] == 'win' else 0)
        
        print(f"   Prepared {len(features)} trades for training")
        print(f"   Wins: {sum(labels)}, Losses: {len(labels) - sum(labels)}")
        
        import numpy as np
        return np.array(features), np.array(labels)
    
    def get_statistics(self):
        """Get performance statistics"""
        completed = self.get_completed_trades()
        
        if len(completed) == 0:
            return None
        
        wins = [t for t in completed if t['outcome'] == 'win']
        losses = [t for t in completed if t['outcome'] == 'loss']
        
        total_pnl = sum(t['pnl'] for t in completed)
        win_rate = len(wins) / len(completed) * 100
        
        avg_win = sum(t['pnl'] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t['pnl'] for t in losses) / len(losses) if losses else 0
        
        return {
            'total_trades': len(completed),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss
        }
    
    def print_statistics(self):
        """Print performance stats"""
        stats = self.get_statistics()
        
        if not stats:
            print(" No completed trades yet")
            return
        
        print("\n" + "=" * 50)
        print(" TRADING STATISTICS")
        print("=" * 50)
        print(f"Total Trades:    {stats['total_trades']}")
        print(f"Wins:            {stats['wins']}")
        print(f"Losses:          {stats['losses']}")
        print(f"Win Rate:        {stats['win_rate']:.1f}%")
        print(f"Total P&L:       ${stats['total_pnl']:.2f}")
        print(f"Avg Win:         ${stats['avg_win']:.2f}")
        print(f"Avg Loss:        ${stats['avg_loss']:.2f}")
        print("=" * 50)


if __name__ == "__main__":
    logger = TradeLogger()
    
    logger.print_statistics()
    
    print(f"\n Total logged trades: {len(logger.trades)}")
    print(f" Completed trades: {len(logger.get_completed_trades())}")
    
    X, y = logger.get_training_data()
    if X is not None:
        print(f"\nReady for ML training with {len(X)} samples!")