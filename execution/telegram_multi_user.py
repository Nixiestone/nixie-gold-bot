"""
Multi-User Telegram Bot - Send signals to multiple subscribers
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError
import json
import os
import config

class MultiUserTelegramBot:
    def __init__(self):
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.subscribers_file = 'subscribers.json'
        self.subscribers = self.load_subscribers()
        self.bot = Bot(token=self.bot_token)
    
    def load_subscribers(self):
        """Load subscriber list from file"""
        if os.path.exists(self.subscribers_file):
            try:
                with open(self.subscribers_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_subscribers(self):
        """Save subscriber list to file"""
        with open(self.subscribers_file, 'w') as f:
            json.dump(self.subscribers, f, indent=2)
    
    def add_subscriber(self, chat_id, username=None):
        """Add a new subscriber"""
        if chat_id not in self.subscribers:
            self.subscribers.append(chat_id)
            self.save_subscribers()
            print(f"✅ Added subscriber: {chat_id} ({username})")
            return True
        return False
    
    def remove_subscriber(self, chat_id):
        """Remove a subscriber"""
        if chat_id in self.subscribers:
            self.subscribers.remove(chat_id)
            self.save_subscribers()
            print(f"❌ Removed subscriber: {chat_id}")
            return True
        return False
    
    async def send_to_all(self, message, parse_mode='Markdown'):
        """Send message to all subscribers"""
        failed = []
        success_count = 0
        
        for chat_id in self.subscribers:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=parse_mode
                )
                success_count += 1
            except TelegramError as e:
                print(f"⚠️  Failed to send to {chat_id}: {e}")
                failed.append(chat_id)
        
        # Remove failed chat IDs (user blocked bot or deleted account)
        for chat_id in failed:
            if "bot was blocked" in str(e).lower():
                self.remove_subscriber(chat_id)
        
        print(f"📤 Sent to {success_count}/{len(self.subscribers)} subscribers")
        return success_count
    
    async def send_signal(self, signal_data):
        """Send trading signal to all subscribers"""
        message = self._format_signal_message(signal_data)
        return await self.send_to_all(message)
    
    def _format_signal_message(self, signal):
        """Format signal into beautiful Telegram message"""
        direction_emoji = "🟢" if signal['signal'] == 'LONG' else "🔴"
        
        message = f"""
{direction_emoji} *NIXIE'S GOLD TRADING SIGNAL*

*Direction:* {signal['signal']}
*Confidence:* {signal['confidence']}%

📊 *Entry Details:*
Entry Price: `${signal['entry_price']:.2f}`
Stop Loss: `${signal['stop_loss']:.2f}`
Risk: `{signal['pips_risk']:.1f} pips`

🎯 *Take Profit Levels:*
TP1 (45%): `${signal['take_profit_1']:.2f}` _{signal['pips_tp1']:.1f} pips_
TP2 (30%): `${signal['take_profit_2']:.2f}` _{signal['pips_tp2']:.1f} pips_
TP3 (25%): `${signal['take_profit_3']:.2f}` _{signal['pips_tp3']:.1f} pips_

⚙️ *Risk Management:*
Position Size: `{signal['lot_size']} lots`
Risk Amount: `${signal['risk_dollars']:.2f}`
Expected Reward: `${signal['expected_reward']:.2f}`
Risk/Reward: `1:{signal['rr_ratio']:.2f}`

📍 *Trade Setup:*
Regime: {signal.get('regime', 'N/A')}
Level: {signal.get('level_name', 'N/A')}
Session: {signal.get('session', 'N/A')}

⏰ Time: `{signal.get('timestamp', 'N/A')}`

---
💡 *Instructions:*
1. Enter at market or use limit order
2. Set stop loss immediately
3. Move SL to breakeven after TP1 hits
4. Let runners work toward TP2 and TP3

_Nixie's Quant Project by Blessing Omoregie_
        """
        
        return message.strip()
    
    def get_subscriber_count(self):
        """Get number of subscribers"""
        return len(self.subscribers)


# Interactive Bot (for users to subscribe/unsubscribe)
class InteractiveTelegramBot:
    def __init__(self):
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.multi_user = MultiUserTelegramBot()
        self.app = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        username = update.effective_user.username
        
        self.multi_user.add_subscriber(chat_id, username)
        
        welcome_message = f"""
👋 *Welcome to Nixie's Gold Bot!*

You've been subscribed to trading signals!

📊 *What you'll receive:*
• High-probability gold trading signals
• Entry price and stop loss
• Multiple take profit targets
• Risk management details

⚙️ *Commands:*
/start - Subscribe to signals
/stop - Unsubscribe from signals
/status - Check your subscription status
/stats - Bot statistics

🎯 *Strategy:*
We trade gold using a 6-factor confluence system:
1. Market regime
2. Trading session timing
3. Key structural levels
4. Liquidity sweeps
5. Momentum confirmation
6. Risk/reward validation

📈 *Expected:*
• 0-3 signals per week (very selective!)
• 65-75% win rate target
• Minimum 1:1.5 risk/reward ratio

_Developed by Blessing Omoregie (@nixiestone)_
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command"""
        chat_id = update.effective_chat.id
        
        removed = self.multi_user.remove_subscriber(chat_id)
        
        if removed:
            message = "👋 You've been unsubscribed. Use /start to subscribe again."
        else:
            message = "You weren't subscribed. Use /start to subscribe."
        
        await update.message.reply_text(message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        chat_id = update.effective_chat.id
        
        if chat_id in self.multi_user.subscribers:
            status = "✅ *Active* - You're receiving signals"
        else:
            status = "❌ *Inactive* - Use /start to subscribe"
        
        message = f"""
📊 *Your Status:*
{status}

Chat ID: `{chat_id}`
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        total_subscribers = self.multi_user.get_subscriber_count()
        
        message = f"""
📊 *Bot Statistics:*

Total Subscribers: {total_subscribers}
Strategy: 6-Factor Confluence
Symbol: XAUUSDm (Gold)
Risk per Trade: {config.RISK_PERCENT}%

🎯 *Performance Targets:*
Win Rate: 65-75%
Min R:R: 1:{config.MIN_RISK_REWARD}
Signals/Week: 1-3

💡 This bot is very selective - quality over quantity!
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    def run_interactive(self):
        """Run the interactive bot (for subscriptions)"""
        self.app = Application.builder().token(self.bot_token).build()
        
        # Add command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("stop", self.stop_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))
        
        print("🤖 Interactive Telegram bot started!")
        print("📱 Users can now use /start to subscribe")
        print("Press Ctrl+C to stop")
        
        # Start the bot using run_polling (blocking)
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


# Synchronous wrappers
def send_signal_to_all(signal_data):
    """Send signal to all subscribers"""
    bot = MultiUserTelegramBot()
    return asyncio.run(bot.send_signal(signal_data))

def send_text_to_all(text):
    """Send text to all subscribers"""
    bot = MultiUserTelegramBot()
    return asyncio.run(bot.send_to_all(text))


# Test/Demo
if __name__ == "__main__":
    print("🤖 Nixie's Multi-User Telegram Bot")
    print("=" * 60)
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        # Run interactive bot for users to subscribe
        print("\n🔄 Starting interactive mode...")
        print("Users can message your bot to subscribe!\n")
        
        bot = InteractiveTelegramBot()
        bot.run_interactive()  # No asyncio.run needed
    else:
        # Test broadcast
        print("\n📊 Current Subscribers:")
        bot = MultiUserTelegramBot()
        print(f"Total: {bot.get_subscriber_count()}")
        print(f"Chat IDs: {bot.subscribers}")
        
        print("\n💡 To allow users to subscribe:")
        print("   python execution/telegram_multi_user.py interactive")
        print("\n💡 To add users manually:")
        print("   Edit subscribers.json and add their chat IDs")