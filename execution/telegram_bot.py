import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from telegram import Bot
from telegram.error import TelegramError
import config

class TelegramNotifier:
    def __init__(self):
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.bot = Bot(token=self.bot_token)
    
    async def send_signal(self, signal_data):
        """
        Send formatted trading signal to Telegram
        """
        try:
            message = self._format_signal_message(signal_data)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            print("Signal sent to Telegram successfully!")
            return True
            
        except TelegramError as e:
            print(f"Telegram error: {e}")
            return False
        except Exception as e:
            print(f"Error sending signal: {e}")
            return False
    
    def _format_signal_message(self, signal):
        """Format signal into beautiful Telegram message"""
        
        direction_emoji = "🟢" if signal['signal'] == 'LONG' else "🔴"
        
        message = f"""
{direction_emoji} *NIXIE'S GOLD TRADING SIGNAL*

*Direction:* {signal['signal']}
*Confidence:* {signal['confidence']}%

 *Entry Details:*
Entry Price: `${signal['entry_price']:.2f}`
Stop Loss: `${signal['stop_loss']:.2f}`
Risk: `{signal['pips_risk']:.1f} pips`

 *Take Profit Levels:*
TP1 (45%): `${signal['take_profit_1']:.2f}` _{signal['pips_tp1']:.1f} pips_
TP2 (30%): `${signal['take_profit_2']:.2f}` _{signal['pips_tp2']:.1f} pips_
TP3 (25%): `${signal['take_profit_3']:.2f}` _{signal['pips_tp3']:.1f} pips_

 *Risk Management:*
Position Size: `{signal['lot_size']} lots`
Risk Amount: `${signal['risk_dollars']:.2f}`
Expected Reward: `${signal['expected_reward']:.2f}`
Risk/Reward: `1:{signal['rr_ratio']:.2f}`

 *Trade Setup:*
Regime: {signal.get('regime', 'N/A')}
Level: {signal.get('level_name', 'N/A')}
Session: {signal.get('session', 'N/A')}

 Time: `{signal.get('timestamp', 'N/A')}`

---
 *Instructions:*
1. Enter at market or use limit order
2. Set stop loss immediately
3. Move SL to breakeven after TP1 hits
4. Let runners work toward TP2 and TP3

_Nixie's Quant Project by Blessing Omoregie_
        """
        
        return message.strip()
    
    async def send_text(self, text):
        """Send plain text message"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='Markdown'
            )
            return True
        except Exception as e:
            print(f"Error sending text: {e}")
            return False
    
    async def send_startup_message(self):
        """Send message when bot starts"""
        message = """
 *Nixie's Gold Bot Started!*

The bot is now monitoring gold markets and will send signals when high-probability setups are detected.

 *Configuration:*
• Symbol: XAUUSDm
• Risk per trade: {risk}%
• Scan interval: {interval} minutes

 *Target Win Rate:* 65-75%
 *Min Risk/Reward:* 1:{min_rr}

Bot is active and scanning! 
        """.format(
            risk=config.RISK_PERCENT,
            interval=config.SCAN_INTERVAL_MINUTES,
            min_rr=config.MIN_RISK_REWARD
        )
        
        await self.send_text(message)
    
    async def send_error(self, error_message):
        """Send error notification"""
        message = f"*Bot Error*\n\n`{error_message}`"
        await self.send_text(message)
    
    async def send_daily_summary(self, stats):
        """Send daily performance summary"""
        message = f"""
 *Daily Summary*

Signals Generated: {stats.get('signals', 0)}
Win Rate: {stats.get('win_rate', 0)}%
Profit/Loss: ${stats.get('pnl', 0):.2f}

Keep trading smart! 
        """
        await self.send_text(message)


def send_signal_sync(signal_data):
    """Synchronous wrapper to send signal"""
    notifier = TelegramNotifier()
    asyncio.run(notifier.send_signal(signal_data))

def send_text_sync(text):
    """Synchronous wrapper to send text"""
    notifier = TelegramNotifier()
    asyncio.run(notifier.send_text(text))


if __name__ == "__main__":
    print(" Testing Telegram Bot...")
    

    test_signal = {
        'signal': 'LONG',
        'entry_price': 2050.00,
        'stop_loss': 2040.00,
        'take_profit_1': 2065.00,
        'take_profit_2': 2075.00,
        'take_profit_3': 2090.00,
        'lot_size': 0.50,
        'confidence': 78,
        'pips_risk': 10.0,
        'pips_tp1': 15.0,
        'pips_tp2': 25.0,
        'pips_tp3': 40.0,
        'risk_dollars': 150.00,
        'expected_reward': 340.00,
        'rr_ratio': 2.27,
        'timestamp': '2025-01-15 10:30:00',
        'regime': 'Range-bound',
        'level_name': 'PDL',
        'session': 'London'
    }
    
    print("Sending test signal to Telegram...")
    send_signal_sync(test_signal)
    print("Check your Telegram!")