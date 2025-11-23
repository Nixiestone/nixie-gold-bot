import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import MetaTrader5 as mt5
from datetime import datetime
import config

class LiveTrader:
    def __init__(self):
        self.symbol = config.SYMBOL
        self.magic_number = 123456  
    
    def execute_trade(self, signal):
        """
        Execute a trade based on signal
        
        WARNING: This places REAL trades!
        Only use when you're confident in the bot.
        """
        try:
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                print(f"❌ Symbol {self.symbol} not found")
                return False
            
            if not symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL:
                print(f"❌ Trading not allowed for {self.symbol}")
                return False
            
            lot_size = signal['lot_size']
            entry_price = signal['entry_price']
            stop_loss = signal['stop_loss']
            take_profit = signal['take_profit_1']  
            
            if signal['signal'] == 'LONG':
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(self.symbol).ask
            else:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(self.symbol).bid
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": stop_loss,
                "tp": take_profit,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": f"Nixie Bot {signal['signal']}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            print(f" Sending {signal['signal']} order...")
            result = mt5.order_send(request)
            
            if result is None:
                print(f"❌ Order send failed: {mt5.last_error()}")
                return False
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"❌ Order failed: {result.retcode}")
                print(f"   Comment: {result.comment}")
                return False
            
            print(f"✅ Order executed successfully!")
            print(f"   Ticket: {result.order}")
            print(f"   Volume: {result.volume}")
            print(f"   Price: {result.price}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error executing trade: {e}")
            return False
    
    def close_position(self, position_id):
        """Close a specific position"""
        try:
            position = mt5.positions_get(ticket=position_id)
            if not position:
                print(f"❌ Position {position_id} not found")
                return False
            
            position = position[0]
            
            if position.type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(self.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(self.symbol).ask
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": position_id,
                "price": price,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": "Nixie Bot Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ Position closed: {position_id}")
                return True
            else:
                print(f"❌ Failed to close position: {result.comment if result else 'Unknown error'}")
                return False
                
        except Exception as e:
            print(f"❌ Error closing position: {e}")
            return False
    
    def get_open_positions(self):
        """Get all open positions from this bot"""
        try:
            positions = mt5.positions_get(symbol=self.symbol)
            if positions is None:
                return []
            
            bot_positions = [p for p in positions if p.magic == self.magic_number]
            return bot_positions
            
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return []
    
    def check_position_status(self, position_id):
        """Check if position hit TP1 and move SL to breakeven"""
        try:
            position = mt5.positions_get(ticket=position_id)
            if not position:
                return None
            
            position = position[0]
            current_price = position.price_current
            entry_price = position.price_open
            
            if position.type == mt5.ORDER_TYPE_BUY:
                profit_pips = (current_price - entry_price) / 0.10
            else:
                profit_pips = (entry_price - current_price) / 0.10
            
            return {
                'ticket': position_id,
                'profit_pips': profit_pips,
                'profit_dollars': position.profit,
                'type': 'LONG' if position.type == mt5.ORDER_TYPE_BUY else 'SHORT'
            }
            
        except Exception as e:
            print(f"❌ Error checking position: {e}")
            return None
    
    def modify_stop_loss(self, position_id, new_sl):
        """Modify stop loss (e.g., move to breakeven)"""
        try:
            position = mt5.positions_get(ticket=position_id)
            if not position:
                return False
            
            position = position[0]
            
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": self.symbol,
                "position": position_id,
                "sl": new_sl,
                "tp": position.tp
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ Stop loss modified to ${new_sl:.2f}")
                return True
            else:
                print(f"❌ Failed to modify SL")
                return False
                
        except Exception as e:
            print(f"❌ Error modifying SL: {e}")
            return False


if __name__ == "__main__":
    print("⚠️  WARNING: This module executes REAL trades!")
    print("   Only use on a demo account for testing!")
    print()
    
    trader = LiveTrader()
    
    positions = trader.get_open_positions()
    print(f" Open positions: {len(positions)}")
    
    for pos in positions:
        status = trader.check_position_status(pos.ticket)
        if status:
            print(f"   Ticket: {pos.ticket}")
            print(f"   Type: {status['type']}")
            print(f"   Profit: ${status['profit_dollars']:.2f} ({status['profit_pips']:.1f} pips)")