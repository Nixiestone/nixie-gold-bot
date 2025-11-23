# ⚡ Quick Start Guide - Nixie's Gold Bot

Get your bot running in 30 minutes! Follow this checklist step by step.

---

## 📋 Pre-Flight Checklist

Before you begin, make sure you have:

- [ ] Python 3.11.9 installed
- [ ] MetaTrader 5 installed
- [ ] Trading account (demo or live)
- [ ] Telegram account
- [ ] 30 minutes of time

---

## 🚀 Local Setup (Test on Your Computer)

### Step 1: Get the Code (2 minutes)

```bash
# Clone repository
git clone https://github.com/nixiestone/nixie-gold-bot.git
cd nixie-gold-bot

# Or download ZIP and extract
```

### Step 2: Set Up Environment (5 minutes)

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Telegram (5 minutes)

1. Open Telegram
2. Search: `@BotFather`
3. Send: `/newbot`
4. Name it: `My Gold Trading Bot`
5. Username: `my_gold_signals_bot`
6. **Copy the bot token**
7. Search: `@userinfobot`
8. **Copy your chat ID**

### Step 4: Set Up MT5 (3 minutes)

1. Open MetaTrader 5
2. Login to your account
3. Tools → Options → Expert Advisors
4. Check ✅ "Allow algorithmic trading"
5. Verify `XAUUSDm` symbol exists in Market Watch

### Step 5: Configure Bot (5 minutes)

Create `.env` file in project root:

```bash
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id_number

MT5_LOGIN=your_mt5_account_number
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_broker_server_name

SYMBOL=XAUUSDm
ACCOUNT_BALANCE=10000
RISK_PERCENT=1.5
ENVIRONMENT=development
```

### Step 6: Test Everything (5 minutes)

```bash
# Test configuration
python config.py
# Should show: ✅ Configuration validated

# Test MT5 connection
python data/data_handler.py
# Should show: ✅ Connected to MetaTrader 5

# Test Telegram
python execution/telegram_bot.py
# Should send test message to Telegram

# Test signal generator
python strategy/signal_generator.py
# Shows current market analysis
```

### Step 7: Run the Bot! (5 minutes)

```bash
# Start in development mode (dry run)
python main.py
```

**You should see:**
- ✅ Connected to MT5
- ✅ Scanning for signals
- ✅ Market analysis output
- ❌ No Telegram alerts (development mode)

**Let it run for 5-10 minutes**, then `Ctrl+C` to stop.

### Step 8: Go Live (Optional)

When ready for real signals:

1. Edit `.env`:
   ```bash
   ENVIRONMENT=production
   ```

2. Run again:
   ```bash
   python main.py
   ```

3. Now you'll get Telegram alerts! 📱

### Step 9: Enable Multi-User (Optional)

Want to share signals with friends/subscribers?

**Option 1: Interactive (Users Subscribe Themselves)**
```bash
# In separate terminal
python execution/telegram_multi_user.py interactive
```

Users send `/start` to your bot to subscribe!

**Option 2: Manual**

Create `subscribers.json`:
```json
[
  123456789,
  987654321
]
```

All subscribers get every signal automatically!

---

## ☁️ AWS Deployment (24/7 Operation)

### Why Deploy to AWS?

- ✅ Bot runs 24/7 even when your PC is off
- ✅ Professional setup
- ✅ Free for 12 months
- ✅ Auto-restart on crashes

### Quick Deploy Steps

**Time needed:** 45-60 minutes

1. **Prepare locally:**
   ```bash
   python setup_aws.py
   ```

2. **Create AWS account:**
   - Go to: https://aws.amazon.com/free
   - Sign up (credit card needed for verification)

3. **Launch server:**
   - EC2 → Launch Instance
   - Windows Server 2022
   - t2.micro (free tier)
   - Create key pair (save it!)

4. **Connect via Remote Desktop**

5. **Install on server:**
   - Python 3.11.9
   - MetaTrader 5
   - Upload bot files
   - Install requirements

6. **Start bot:**
   ```cmd
   python launcher.py
   ```

7. **Disconnect** (bot keeps running!)

📖 **Full guide:** [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)

---

## 📊 What to Expect

### First Week (Learning)

- **Signals:** Probably 0-2 (bot is very selective!)
- **This is normal!** Strategy waits for perfect setups
- Watch what it's looking for
- Check logs to see analysis

### Week 2-4 (Testing)

- **Signals:** 2-5 per month
- Paper trade them manually
- Track outcomes
- Build confidence

### Month 2+ (Live)

- **Signals:** 3-8 per month
- 65-75% win rate expected
- Follow signals exactly
- Scale position sizes gradually

---

## 🎯 Quick Commands Reference

```bash
# Development mode (no signals sent)
python main.py

# Health check
python health_check.py

# Test components
python data/data_handler.py
python indicators/technical.py
python strategy/signal_generator.py
python execution/telegram_bot.py

# Backtest
python backtest/backtester.py

# Diagnose why no signals
python backtest/diagnose_strategy.py

# 24/7 launcher (with auto-restart)
python launcher.py
```

---

## ⚙️ Quick Settings

### Conservative (Fewer signals, higher win rate)

```python
# config.py
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RISK_PERCENT = 1.0
```

### Moderate (Balanced)

```python
# config.py
RSI_OVERSOLD = 35
RSI_OVERBOUGHT = 65
RISK_PERCENT = 1.5
```

### Aggressive (More signals, lower win rate)

```python
# config.py
RSI_OVERSOLD = 40
RSI_OVERBOUGHT = 60
RISK_PERCENT = 2.0
```

---

## 🆘 Quick Troubleshooting

### No Signals?

**This is normal!** The bot is very selective.

```bash
# Check what's happening
python backtest/diagnose_strategy.py
```

### MT5 Won't Connect?

1. Make sure MT5 is open
2. Check you're logged in
3. Verify credentials in `.env`
4. Enable algo trading in MT5 settings

### Telegram Not Working?

```bash
# Test it
python execution/telegram_bot.py
```

Check:
- Bot token correct
- Chat ID correct
- You messaged bot first

### Import Errors?

```bash
# Reactivate virtual environment
.venv\Scripts\activate

# Reinstall
pip install -r requirements.txt
```

---

## 📱 Daily Workflow

### Morning Routine (2 minutes)

1. Check Telegram for signals
2. If signal received:
   - Review setup
   - Enter trade manually or let auto-execute
   - Set alerts for TP levels

### Weekly Review (10 minutes)

1. Check bot logs: `logs/trading.log`
2. Review trade outcomes
3. Update trade logger with results
4. Check win rate and metrics

### Monthly Maintenance (20 minutes)

1. Analyze performance
2. Retrain ML model if 20+ trades
3. Adjust parameters if needed
4. Update dependencies

---

## 🎓 Next Steps

After quickstart works:

1. **Read full README:** [README.md](README.md)
2. **Study the strategy:** Understand why signals trigger
3. **Run backtests:** Test on historical data
4. **Paper trade:** Follow signals without real money
5. **Deploy to AWS:** For 24/7 operation
6. **Go live:** Start with minimum sizes

---

## 📊 Expected Timeline

**Day 1:** Setup and testing (this guide)
**Week 1:** Learn patterns, wait for signals
**Week 2-4:** Paper trade, collect data
**Month 2:** Go live with small sizes
**Month 3+:** Scale up gradually

---

## ✅ Success Criteria

You're ready to go live when:

- [ ] Bot runs for 7+ days without crashes
- [ ] Received and paper traded 5+ signals
- [ ] Understand all 6 entry conditions
- [ ] Win rate on paper trades > 60%
- [ ] Comfortable with risk per trade
- [ ] Know how to check logs
- [ ] Can restart bot if needed
- [ ] Telegram alerts working perfectly

---

## 💡 Pro Tips

1. **Be Patient** - Strategy is selective by design
2. **Trust the Process** - Don't override bot decisions
3. **Start Small** - Use minimum lot sizes
4. **Keep Learning** - Study why signals win/lose
5. **Stay Disciplined** - Follow risk management strictly

---

## 📞 Get Help

- **Issues:** [GitHub Issues](https://github.com/nixiestone/nixie-gold-bot/issues)
- **Questions:** [Discussions](https://github.com/nixiestone/nixie-gold-bot/discussions)
- **Docs:** [Full README](README.md)
- **AWS Guide:** [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)

---

**🎉 You're all set! Happy trading!**

Made with ❤️ by Blessing Omoregie (@nixiestone)

Remember: Trade smart. Trade safe. Trade systematically.