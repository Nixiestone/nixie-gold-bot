"""
Backtester - Test strategy on historical data
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config
from data.data_handler import DataHandler
from indicators.technical import TechnicalIndicators
from strategy.signal_generator import SignalGenerator
from strategy.risk_manager import RiskManager

class Backtester:
    def __init__(self):
        self.handler = DataHandler()
        self.signal_generator = SignalGenerator()
        self.technical = TechnicalIndicators()
        self.risk_manager = RiskManager()
        
        self.trades = []
        self.equity_curve = []
    
    def run_backtest(self, start_date, end_date, initial_capital=10000):
        """
        Run backtest over historical period
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            initial_capital: Starting balance
        """
        try:
            print("📊 Starting Backtest...")
            print(f"Period: {start_date} to {end_date}")
            print(f"Initial Capital: ${initial_capital:,.2f}")
            print("=" * 60)
            
            # Connect to MT5
            if not self.handler.connect_mt5():
                print("❌ Failed to connect to MT5")
                return None
            
            capital = initial_capital
            self.trades = []
            self.equity_curve = [initial_capital]
            
            # Get historical data
            print("📥 Fetching historical data...")
            df_h4 = self.handler.get_gold_data('H4', 5000)  # Large dataset
            df_m15 = self.handler.get_gold_data('M15', 10000)
            
            if df_h4 is None or df_m15 is None:
                print("❌ Failed to fetch data")
                return None
            
            # Calculate indicators
            print("🔢 Calculating indicators...")
            df_h4 = self.technical.calculate_all(df_h4)
            df_m15 = self.technical.calculate_all(df_m15)
            
            # Filter by date range
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            
            df_h4 = df_h4[(df_h4.index >= start) & (df_h4.index <= end)]
            df_m15 = df_m15[(df_m15.index >= start) & (df_m15.index <= end)]
            
            print(f"📊 Analyzing {len(df_h4)} H4 bars...")
            
            # Simulate trading
            signals_checked = 0
            
            for i in range(100, len(df_h4) - 50):  # Leave buffer for forward testing
                # Get data up to current point
                current_h4 = df_h4.iloc[:i+1]
                current_m15 = df_m15[df_m15.index <= current_h4.index[-1]]
                
                if len(current_m15) < 100:
                    continue
                
                # Get current timestamp
                current_time = current_h4.index[-1]
                
                # Generate signal with timestamp for backtesting
                signal = self.signal_generator.generate_signal(current_h4, current_m15, current_time)
                signals_checked += 1
                
                if signal:
                    # Simulate trade execution
                    trade_result = self._simulate_trade(
                        signal,
                        df_m15[df_m15.index > current_h4.index[-1]].head(500),
                        capital
                    )
                    
                    if trade_result:
                        self.trades.append(trade_result)
                        capital += trade_result['pnl']
                        self.equity_curve.append(capital)
                        
                        print(f"Trade #{len(self.trades)}: {trade_result['direction']} | "
                              f"{'WIN' if trade_result['outcome'] == 'win' else 'LOSS'} | "
                              f"P&L: ${trade_result['pnl']:.2f} | Balance: ${capital:.2f}")
                
                # Progress update
                if i % 100 == 0:
                    progress = (i / len(df_h4)) * 100
                    print(f"Progress: {progress:.1f}% | Signals: {len(self.trades)} | Balance: ${capital:.2f}")
            
            # Calculate final metrics
            print("\n" + "=" * 60)
            print("✅ Backtest Complete!")
            print("=" * 60)
            
            if len(self.trades) == 0:
                print("\n⚠️  NO TRADES GENERATED")
                print("This could mean:")
                print("  1. Strategy conditions are very strict (GOOD - selective bot)")
                print("  2. Historical period had no suitable setups")
                print("  3. Parameters need adjustment")
                print(f"\nBars analyzed: {signals_checked}")
                print(f"Signals generated: 0")
                print("\n💡 Try:")
                print("  - Running backtest on different date range")
                print("  - Adjusting RSI thresholds in config.py")
                print("  - Checking if data quality is good")
                
                self.handler.disconnect_mt5()
                return None
            
            metrics = self._calculate_metrics(initial_capital, capital)
            self._print_results(metrics)
            
            self.handler.disconnect_mt5()
            return metrics
            
        except Exception as e:
            print(f"❌ Backtest error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _simulate_trade(self, signal, future_data, capital):
        """Simulate how a trade would have performed"""
        try:
            entry = signal['entry_price']
            stop_loss = signal['stop_loss']
            tp1 = signal['take_profit_1']
            tp2 = signal['take_profit_2']
            tp3 = signal['take_profit_3']
            direction = signal['signal']
            
            # Calculate position size
            lot_size = self.risk_manager.calculate_position_size(capital, entry, stop_loss)
            
            if lot_size == 0:
                return None
            
            # Track trade through future data
            for i, (timestamp, bar) in enumerate(future_data.iterrows()):
                if direction == 'LONG':
                    # Check if stop loss hit
                    if bar['Low'] <= stop_loss:
                        pnl = (stop_loss - entry) * lot_size * 100  # 100 oz per lot
                        return {
                            'direction': direction,
                            'entry': entry,
                            'exit': stop_loss,
                            'outcome': 'loss',
                            'pnl': pnl,
                            'pips': self.risk_manager.price_to_pips(stop_loss - entry),
                            'bars_held': i + 1,
                            'timestamp': timestamp
                        }
                    
                    # Check if TP1 hit
                    if bar['High'] >= tp1:
                        pnl = (tp1 - entry) * lot_size * 100
                        return {
                            'direction': direction,
                            'entry': entry,
                            'exit': tp1,
                            'outcome': 'win',
                            'pnl': pnl,
                            'pips': self.risk_manager.price_to_pips(tp1 - entry),
                            'bars_held': i + 1,
                            'timestamp': timestamp
                        }
                
                else:  # SHORT
                    # Check if stop loss hit
                    if bar['High'] >= stop_loss:
                        pnl = (entry - stop_loss) * lot_size * 100
                        return {
                            'direction': direction,
                            'entry': entry,
                            'exit': stop_loss,
                            'outcome': 'loss',
                            'pnl': pnl,
                            'pips': self.risk_manager.price_to_pips(entry - stop_loss),
                            'bars_held': i + 1,
                            'timestamp': timestamp
                        }
                    
                    # Check if TP1 hit
                    if bar['Low'] <= tp1:
                        pnl = (entry - tp1) * lot_size * 100
                        return {
                            'direction': direction,
                            'entry': entry,
                            'exit': tp1,
                            'outcome': 'win',
                            'pnl': pnl,
                            'pips': self.risk_manager.price_to_pips(entry - tp1),
                            'bars_held': i + 1,
                            'timestamp': timestamp
                        }
                
                # Max bars to hold
                if i > 100:  # Exit if not hit after 100 M15 bars (25 hours)
                    break
            
            return None
            
        except Exception as e:
            print(f"Error simulating trade: {e}")
            return None
    
    def _calculate_metrics(self, initial_capital, final_capital):
        """Calculate performance metrics"""
        if len(self.trades) == 0:
            return {}
        
        wins = [t for t in self.trades if t['outcome'] == 'win']
        losses = [t for t in self.trades if t['outcome'] == 'loss']
        
        total_trades = len(self.trades)
        win_count = len(wins)
        loss_count = len(losses)
        
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t['pnl'] for t in self.trades)
        gross_profit = sum(t['pnl'] for t in wins)
        gross_loss = abs(sum(t['pnl'] for t in losses))
        
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        avg_win = (gross_profit / win_count) if win_count > 0 else 0
        avg_loss = (gross_loss / loss_count) if loss_count > 0 else 0
        
        expectancy = (win_rate/100 * avg_win) - ((100-win_rate)/100 * avg_loss)
        
        # Max drawdown
        peak = initial_capital
        max_dd = 0
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            dd = ((peak - equity) / peak * 100) if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
        
        return {
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'total_pnl': total_pnl,
            'total_return_pct': ((final_capital - initial_capital) / initial_capital * 100),
            'total_trades': total_trades,
            'wins': win_count,
            'losses': loss_count,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'expectancy': expectancy,
            'max_drawdown_pct': max_dd
        }
    
    def _print_results(self, metrics):
        """Print backtest results"""
        if not metrics:
            print("\n⚠️  No metrics to display (no trades generated)")
            return
            
        print(f"\n📊 BACKTEST RESULTS")
        print("=" * 60)
        print(f"Initial Capital:    ${metrics['initial_capital']:,.2f}")
        print(f"Final Capital:      ${metrics['final_capital']:,.2f}")
        print(f"Total P&L:          ${metrics['total_pnl']:,.2f} ({metrics['total_return_pct']:.2f}%)")
        print(f"\nTotal Trades:       {metrics['total_trades']}")
        print(f"Wins:               {metrics['wins']}")
        print(f"Losses:             {metrics['losses']}")
        print(f"Win Rate:           {metrics['win_rate']:.2f}%")
        print(f"\nProfit Factor:      {metrics['profit_factor']:.2f}")
        print(f"Avg Win:            ${metrics['avg_win']:.2f}")
        print(f"Avg Loss:           ${metrics['avg_loss']:.2f}")
        print(f"Expectancy:         ${metrics['expectancy']:.2f}")
        print(f"Max Drawdown:       {metrics['max_drawdown_pct']:.2f}%")
        print("=" * 60)


# Run backtest
if __name__ == "__main__":
    backtester = Backtester()
    
    # Run backtest for last 6 months
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    print(f"Running backtest from {start_date} to {end_date}...")
    results = backtester.run_backtest(start_date, end_date, initial_capital=10000)
    
    if results:
        print("\n✅ Backtest complete! Check results above.")
        