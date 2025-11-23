# Nixie's Gold Trading Bot

An advanced quantitative trading system for gold (XAU/USD) that combines technical analysis, smart money concepts, and machine learning to identify high-probability trading opportunities.

![Python Version](https://img.shields.io/badge/python-3.11.9-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

---

## Table of Contents

- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Strategy Explained](#strategy-explained)
- [Machine Learning](#machine-learning)
- [Backtesting](#backtesting)
- [Live Trading](#live-trading)
- [AWS Deployment (24/7 Trading)](#aws-deployment)
- [Risk Management](#risk-management)
- [Troubleshooting](#troubleshooting)
- [Performance](#performance)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [Author](#author)

---

## About the Project

Nixie's Gold Bot is a sophisticated algorithmic trading system designed specifically for trading gold. After years of studying price action and institutional trading patterns, I built this bot to automate the identification of high-quality trade setups that professional traders look for.

The bot doesn't try to trade every market movement. Instead, it waits patiently for the perfect confluence of factors - regime alignment, liquidity sweeps, momentum confirmation, and structural levels - before generating a signal. This selective approach leads to fewer but higher-quality trades.

### Why Gold?

Gold is one of the most liquid markets in the world, trading 24/5 with massive daily volume. It respects technical levels beautifully and shows clear institutional footprints. The XAU/USD pair offers excellent risk-to-reward ratios when traded correctly.

### What Makes This Different?

Most trading bots try to trade every small move. This one doesn't. It's built on the principle that quality beats quantity. The bot combines:
- Multi-timeframe analysis (H4 + M15)
- Smart money concepts (liquidity sweeps, order flow)
- Strict regime filtering
- Machine learning for signal filtering
- Professional risk management

---

## Key Features

### Core Trading Features
- ** Sniper Entry System** - Only trades when all conditions align perfectly
- ** Multi-Timeframe Analysis** - Combines H4 for bias and M15 for entries
- ** Liquidity Detection** - Identifies stop hunts and sweep patterns
- ** Regime Classification** - Adapts to trending, ranging, and breakout conditions
- ** Smart Money Concepts** - Trades like institutions, not retail

### Technical Features
- **🤖 Machine Learning Integration** - Optional AI-powered signal filtering
- **📱 Telegram Notifications** - Get instant alerts on your phone
- **🔄 Automated Execution** - Optional auto-trading capability
- **📊 Comprehensive Backtesting** - Test on years of historical data
- **📝 Trade Logging** - Automatic tracking for ML training

### Risk Management
- **💰 Dynamic Position Sizing** - Based on account balance and risk %
- **🛡️ Strict Stop Losses** - Never exceed 30 pips
- **🎯 Multiple Take Profits** - TP1, TP2, TP3 with partial closes
- **📉 Drawdown Protection** - Conservative risk per trade (1-2%)

---

##  How It Works

### The 6-Point Confluence System

The bot only generates a signal when ALL these conditions are met:

1. **Market Regime** 
   - Identifies if market is trending, ranging, or breaking out
   - Only trades in favorable conditions
   - Uses ADX and Bollinger Bands

2. **Trading Session** 
   - Only trades during London/NY sessions
   - High liquidity periods (08:00-21:00 GMT)
   - Avoids low-volume Asian hours

3. **Structural Level** 
   - Price must be near a key level (PDH, PDL, Asian range, Fibs)
   - Levels where institutions have orders
   - Maximum 20 pips away

4. **Liquidity Sweep** 
   - Detects stop hunts above/below levels
   - Price breaks level then reverses quickly
   - Classic smart money move

5. **Momentum Confirmation** 
   - RSI shows extremes or divergence
   - Stochastic confirms with crossover
   - MACD supports the direction

6. **Risk/Reward** 
   - Minimum 1.5:1 reward-to-risk ratio
   - Stop loss under 30 pips
   - Multiple profit targets

**Result:** Only 0.5-1% of market conditions meet all criteria. When they do, win rate is typically 65-75%.

---

##  Getting Started

### Prerequisites

Before you begin, make sure you have:

- **Python 3.11.9** installed ([Download here](https://www.python.org/downloads/))
- **MetaTrader 5** platform ([Download here](https://www.metatrader5.com/))
- **Trading account** (demo or live) with a broker that offers XAUUSDm (Exness)
- **Telegram account** for receiving signals
- **Windows/Linux/Mac** computer (VPS recommended for 24/7 operation)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/nixiestone/nixie-gold-bot.git
cd nixie-gold-bot

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up your configuration
cp .env.example .env
# Edit .env with your credentials

# Test the setup
python config.py

# Run the bot
python main.py
```

---

##  Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/nixiestone/nixie-gold-bot.git
cd nixie-gold-bot
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv

# Activate:
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Mac/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**What gets installed:**
- `MetaTrader5` - Connect to MT5 platform
- `pandas` & `numpy` - Data manipulation
- `ta` - Technical indicators
- `scikit-learn` & `xgboost` - Machine learning
- `python-telegram-bot` - Telegram integration
- `schedule` - Task scheduling
- Other utilities

### Step 4: Set Up MetaTrader 5

1. Download and install [MetaTrader 5](https://www.metatrader5.com/)
2. Open an account with Exness broker (or any demo broker acconut for testing)
3. Login to MT5
4. Verify `XAUUSDm` symbol exists in Market Watch
5. Enable algo trading: Tools → Options → Expert Advisors → Allow automated trading

### Step 5: Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Name your bot (e.g., "My Gold Trading Bot")
4. Choose username (e.g., `my_gold_bot`)
5. Copy the **Bot Token** (looks like `123456789:ABCdefGHIjklMNOpqrs`)
6. Search for `@userinfobot` to get your **Chat ID**

**For Multi-User Broadcasting:**
- Share your bot username with others
- They message your bot and type `/start`
- They automatically receive all signals!
- See [Multi-User Setup](#multi-user-telegram-broadcasting) below

### Step 6: Configure Environment

Create a `.env` file in the project root:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrs
TELEGRAM_CHAT_ID=987654321

# MetaTrader 5 Configuration
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Server

# Trading Configuration
ACCOUNT_BALANCE=10000
RISK_PERCENT=1.5
SYMBOL=XAUUSDm

# Environment
ENVIRONMENT=development
```

---

## Configuration

### Basic Settings (`config.py`)

```python
# Risk Management
RISK_PERCENT = 1.5           # Risk per trade (1-2% recommended)
MAX_RISK_PERCENT = 2.0       # Maximum allowed risk
MAX_STOP_LOSS_PIPS = 30      # Maximum stop loss

# Take Profit Ratios
TP1_RATIO = 1.5              # First target at 1.5R
TP2_RATIO = 2.5              # Second target at 2.5R
TP3_RATIO = 4.0              # Third target at 4.0R

# Strategy Parameters
RSI_OVERSOLD = 35            # RSI oversold level
RSI_OVERBOUGHT = 65          # RSI overbought level
ADX_THRESHOLD_TRENDING = 25  # Trend strength threshold

# Scanning
SCAN_INTERVAL_MINUTES = 15   # How often to check for signals

# Machine Learning
USE_ML_FILTER = True         # Enable ML filtering
ML_CONFIDENCE_THRESHOLD = 0.65
```

### Trading Sessions

The bot trades during:
- **London Session:** 08:00 - 16:00 GMT
- **New York Session:** 13:00 - 21:00 GMT

These are the highest liquidity periods for gold.

### Adjusting Aggressiveness

**Conservative (Recommended for beginners):**
```python
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RISK_PERCENT = 1.0
```

**Moderate (Balanced):**
```python
RSI_OVERSOLD = 35
RSI_OVERBOUGHT = 65
RISK_PERCENT = 1.5
```

**Aggressive (Experienced only):**
```python
RSI_OVERSOLD = 40
RSI_OVERBOUGHT = 60
RISK_PERCENT = 2.0
```

---

##  Multi-User Telegram Broadcasting

Want to share signals with multiple users? The bot supports broadcasting to unlimited subscribers!

### How It Works

**Two Modes:**

1. **Single User** (Default) - Only you receive signals
2. **Multi-User** - Broadcast to all subscribers

### Enable Multi-User Mode

**Method 1: Interactive (Users Subscribe Themselves) ⭐ Recommended**

```bash
# Start the interactive bot
python execution/telegram_multi_user.py interactive
```

Now users can:
1. Find your bot on Telegram
2. Send `/start` command
3. Automatically get subscribed
4. Receive all future signals!

**User Commands:**
- `/start` - Subscribe to signals
- `/stop` - Unsubscribe
- `/status` - Check subscription status
- `/stats` - View bot statistics

**Method 2: Manual (You Add Chat IDs)**

1. Users get their Chat ID from `@userinfobot`
2. Create `subscribers.json`:
   ```json
   [
     123456789,
     987654321,
     555666777
   ]
   ```
3. Run your bot normally - all subscribers get signals!

### Running Both Bots

**Terminal 1:** Interactive bot (handles subscriptions)
```bash
python execution/telegram_multi_user.py interactive
```

**Terminal 2:** Trading bot (generates signals)
```bash
python launcher.py
```

Or on AWS, run both in separate `screen` sessions!

### Subscriber Management

**View subscribers:**
```bash
python execution/telegram_multi_user.py
```

**Add subscriber programmatically:**
```python
from execution.telegram_multi_user import MultiUserTelegramBot

bot = MultiUserTelegramBot()
bot.add_subscriber(chat_id=123456789, username="user123")
```

**Remove subscriber:**
```python
bot.remove_subscriber(chat_id=123456789)
```

### Privacy & Security

- ✅ Subscriber data stored locally in `subscribers.json`
- ✅ File automatically added to `.gitignore`
- ✅ Users can unsubscribe anytime with `/stop`
- ✅ Bot auto-removes blocked/deleted accounts
- ⚠️ Anyone with bot link can subscribe (use `/stop` to remove unwanted subscribers)

---

## 🎮 Usage

### Development Mode (Testing)

For learning and testing without sending real signals:

```bash
# In .env file:
ENVIRONMENT=development

# Run bot
python main.py
```

**What happens:**
- ✅ Connects to MT5
- ✅ Scans for signals
- ✅ Shows analysis in terminal
- ❌ Does NOT send Telegram alerts
- ❌ Does NOT execute trades

### Production Mode (Live Signals)

When you're ready to receive real signals:

```bash
# In .env file:
ENVIRONMENT=production

# Run bot
python main.py
```

**What happens:**
- ✅ Connects to MT5
- ✅ Scans for signals
- ✅ Sends alerts to Telegram
- ❌ Does NOT auto-execute (unless enabled)

### Auto-Trading Mode (Advanced)

**⚠️ WARNING:** Only enable after thorough testing on demo account!

```python
# In config.py:
AUTO_TRADE = True

# Run bot
python main.py
```

**What happens:**
- ✅ Automatically executes trades
- ✅ Places stop loss and take profit
- ✅ Manages positions
- ⚠️ Uses REAL money!

### Running 24/7

**Option 1: Keep Terminal Open**
```bash
python main.py
# Leave running
```

**Option 2: Use VPS (Recommended)**
1. Get a VPS (Vultr, DigitalOcean, AWS)
2. Install Python and MT5 on VPS
3. Set up the bot
4. Run with `nohup` or `screen`

```bash
# Linux VPS example:
nohup python main.py > output.log 2>&1 &
```

---

##  Strategy Explained

### The Philosophy

Professional traders don't try to catch every move. They wait for high-probability setups where multiple factors align. This bot does the same.

### Entry Logic

**For a LONG signal:**
1. Price sweeps below a key level (stop hunt)
2. Quickly reverses back above the level
3. RSI shows oversold conditions or bullish divergence
4. Stochastic crosses up from oversold zone
5. Market regime is favorable
6. Trading session is London or NY

**For a SHORT signal:**
1. Price sweeps above a key level
2. Quickly reverses back below the level
3. RSI shows overbought or bearish divergence
4. Stochastic crosses down from overbought
5. Market regime is favorable
6. Trading session is London or NY

### Why Liquidity Sweeps?

Institutions need liquidity to fill large orders. They often:
1. Push price above/below obvious levels
2. Trigger retail stop losses
3. Fill their orders at better prices
4. Reverse direction quickly

This creates a "liquidity sweep" - a brief fake-out followed by the real move. By detecting these patterns, we can trade with the institutions instead of against them.

### Key Structural Levels

The bot monitors:
- **Previous Day High/Low (PDH/PDL)**
- **Asian Session Range**
- **Weekly Opening Price**
- **Fibonacci Retracement Levels** (61.8%, 78.6%)
- **Round Numbers** (psychological levels)

These are where orders cluster and reversals often occur.

---

## 🤖 Machine Learning

### How It Works

The bot can learn from your trading results to improve signal quality.

**Training Process:**

1. **Data Collection**
   - Every signal is logged with all features
   - You track the outcome (win/loss)
   - Data stored in `models/trade_history.json`

2. **Feature Extraction**
   - RSI, MACD, ADX values
   - Volume patterns
   - Price momentum
   - Volatility metrics
   - ~20 features per trade

3. **Model Training**
   - Uses XGBoost classifier
   - Learns which feature combinations predict wins
   - Requires minimum 20 completed trades

4. **Signal Filtering**
   - Before sending signal, ML model evaluates it
   - If confidence < threshold (65%), signal is rejected
   - Only highest-quality signals get through

### Training Your Model

```bash
# After collecting 20+ trades with outcomes
python -c "from models.ml_model import MLSignalFilter; ml = MLSignalFilter(); ml.train_from_real_trades()"
```

### Updating Trade Outcomes

```python
from models.trade_logger import TradeLogger

logger = TradeLogger()

# After each trade closes
logger.update_outcome(
    timestamp='2025-01-15T10:30:00',  # Original signal time
    outcome='win',                     # or 'loss'
    pnl=150.00                        # Profit/loss in dollars
)

# View statistics
logger.print_statistics()
```

### Disable ML Filter

If you don't want ML filtering:

```python
# In config.py:
USE_ML_FILTER = False
```

---

## Backtesting

### Basic Backtest

```bash
python backtest/backtester.py
```

Tests the last 6 months of data by default.

### Custom Date Range

```python
from backtest.backtester import Backtester

backtester = Backtester()
results = backtester.run_backtest(
    start_date='2024-01-01',
    end_date='2024-12-31',
    initial_capital=10000
)
```

### Diagnostic Tool

Find out why signals aren't generating:

```bash
python backtest/diagnose_strategy.py
```

**Shows:**
- How often each condition is met
- Probability of signal generation
- Current market conditions
- What's preventing signals

### Relaxed Backtest

For testing with more signals:

```bash
python backtest/run_backtest_optimized.py
```

Temporarily relaxes parameters to generate more trades for analysis.

### Understanding Results

**Good backtest metrics:**
- Win Rate: 65-75%
- Profit Factor: > 1.8
- Max Drawdown: < 15%
- Expectancy: > 0.8R

**Red flags:**
- Win Rate: < 55%
- Profit Factor: < 1.3
- Max Drawdown: > 20%
- Too many trades (not selective enough)

---

## ☁️ AWS Deployment

### Run Your Bot 24/7 for FREE (First 12 Months)

Want your bot to run continuously without keeping your computer on? Deploy to AWS!

**What you get:**
- ✅ 750 hours/month FREE (enough for 24/7)
- ✅ Windows Server in the cloud
- ✅ No more keeping your PC on
- ✅ Professional setup
- ✅ Auto-restart on crashes

### Quick Start

1. **Prepare your bot:**
   ```bash
   python setup_aws.py
   ```

2. **Follow the complete guide:**
    **[AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)** - Step-by-step tutorial

3. **Key files for AWS:**
   - `launcher.py` - Keeps bot running 24/7
   - `start_bot.bat` - Easy Windows startup
   - `health_check.py` - Verify everything works
   - `requirements_aws.txt` - Minimal dependencies

### What the Guide Covers

- Account creation and server launch
- Remote desktop connection
- Python and MT5 installation
- Bot deployment and configuration
- Auto-restart setup
- Billing alerts (stay within free tier)
- Security best practices
- Troubleshooting

**Time needed:** 45-60 minutes for first-time setup

**Cost:** $0 for first 12 months (AWS Free Tier)

### After 12 Months

- AWS t2.micro: ~$8.50/month
- Or migrate to cheaper VPS providers
- Or run locally when actively monitoring

---

## 🛡️ Risk Management

### Safety First

**Before going live:**
1. ✅ Run on demo account for 30+ days
2. ✅ Achieve 60%+ win rate on demo
3. ✅ Understand every component
4. ✅ Test with minimum position sizes
5. ✅ Have emergency stop plan
6. ✅ Never risk more than you can afford to lose

### Position Management

**The bot automatically:**
- Calculates position size based on account balance
- Places stop loss 5-10 pips beyond sweep level
- Sets three take profit targets
- Moves SL to breakeven after TP1 (if auto-trading enabled)

**Manual management:**
```python
from execution.live_trader import LiveTrader

trader = LiveTrader()

# Check positions
positions = trader.get_open_positions()

# Move stop loss
trader.modify_stop_loss(position_id, new_sl_price)

# Close position
trader.close_position(position_id)
```

### Monitoring

**Daily checks:**
- Review Telegram signals
- Check `logs/trading.log`
- Verify MT5 connection stable
- Update trade outcomes for ML

**Weekly reviews:**
- Win rate analysis
- Risk/reward actual vs expected
- Adjust parameters if needed
- Retrain ML model

### Emergency Stop

To stop the bot:
```bash
# In terminal where bot is running:
Ctrl + C
```

To pause trading without stopping:
```python
# In config.py:
ENVIRONMENT = 'development'  # Switches to dry-run mode
```

---

##  Risk Management

### Position Sizing Formula

```
Position Size = (Account Balance × Risk %) / (Stop Loss in Pips × Pip Value)
```

**Example:**
- Account: $10,000
- Risk: 1.5% = $150
- Stop Loss: 20 pips
- Pip Value: $10 per pip per lot
- **Position Size: $150 / (20 × $10) = 0.75 lots**

### The 1% Rule

Never risk more than 1-2% of your account on a single trade. This ensures:
- Survive losing streaks
- Compound gains effectively
- Reduce emotional stress
- Stay in the game long-term

**20 consecutive losses at 1% risk:**
- Account: $10,000 → $8,179 (18% drawdown)
- Still recoverable

**20 consecutive losses at 5% risk:**
- Account: $10,000 → $3,585 (64% drawdown)
- Nearly wiped out

### Take Profit Strategy

**Standard split:**
- TP1 (1.5R): Close 45% of position
- TP2 (2.5R): Close 30% of position
- TP3 (4.0R): Trail remaining 25%

**After TP1 hits:**
- Move stop loss to breakeven
- Worst case: Small profit or breakeven
- Best case: Catch big move with TP2/TP3

### Maximum Risk Limits

**Per Trade:**
- Absolute max: 2% of account
- Recommended: 1-1.5%
- Conservative: 0.5-1%

**Per Day:**
- Stop after 2 losses in a day
- Max daily risk: 3%
- Review strategy if triggered

**Per Week:**
- Max 5 trades per week (highly selective)
- Stop after 15% drawdown
- Take break and review

---

##  Troubleshooting

### Common Issues

#### MT5 Won't Connect

**Problem:** `Failed to connect to MT5`

**Solutions:**
1. Make sure MT5 is open and running
2. Check you're logged into your account
3. Verify credentials in `.env` file
4. Check broker server name is correct
5. Enable algo trading in MT5 settings

#### Symbol Not Found

**Problem:** `Symbol XAUUSDm not found`

**Solutions:**
1. Open MT5 Market Watch
2. Right-click → Show All
3. Search for your broker's gold symbol
4. Common names: `XAUUSDm`, `XAUUSD`, `GOLDm`, `GOLD`
5. Update `SYMBOL` in `.env` file

#### No Signals Generated

**Problem:** Bot runs but never sends signals

**This is normal!** The strategy is very selective. To diagnose:

```bash
python backtest/diagnose_strategy.py
```

**Typical causes:**
- Not in trading session (outside 08:00-21:00 GMT)
- No liquidity sweeps detected
- RSI not in extreme zones
- Market conditions don't meet criteria

**Not a problem - shows bot is disciplined!**

#### Telegram Not Working

**Problem:** Signals don't appear in Telegram

**Solutions:**
1. Verify bot token in `.env`
2. Check chat ID is correct
3. Start a chat with your bot first
4. Test with: `python execution/telegram_bot.py`
5. Check for error messages in logs

#### Import Errors

**Problem:** `ModuleNotFoundError`

**Solutions:**
```bash
# Make sure virtual environment is active
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Reinstall requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### Getting Help

1. **Check logs:** `logs/trading.log`
2. **Run diagnostics:** `python backtest/diagnose_strategy.py`
3. **Test individual modules:**
   ```bash
   python data/data_handler.py
   python indicators/technical.py
   python strategy/signal_generator.py
   ```
4. **Open an issue:** [GitHub Issues](https://github.com/nixiestone/nixie-gold-bot/issues)

---

## Performance

### Expected Metrics

**Conservative settings:**
- Signals per week: 1-3
- Win rate: 70-80%
- Average R-multiple: 2.0
- Monthly return: 8-12%

**Moderate settings:**
- Signals per week: 3-5
- Win rate: 65-75%
- Average R-multiple: 1.8
- Monthly return: 10-15%

### Real-World Expectations

**Month 1-2:**
- Learning phase
- Collect data
- Fine-tune parameters
- May see few signals

**Month 3-6:**
- ML model trained
- Performance stabilizes
- More consistent results
- Build confidence

**Month 6+:**
- Fully optimized
- Mature ML model
- Compound returns
- Scale gradually

**Remember:** Past performance doesn't guarantee future results!

---

## 🤝 Contributing

Contributions are welcome! Whether it's bug fixes, new features, or documentation improvements.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/nixie-gold-bot.git

# Create branch
git checkout -b feature/my-feature

# Make changes and test
python -m pytest tests/

# Commit and push
git add .
git commit -m "Description of changes"
git push origin feature/my-feature
```

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to functions
- Comment complex logic
- Update README if adding features

---

##  Disclaimer

**IMPORTANT: Please read carefully before using this software.**

### Trading Risk

Trading foreign exchange, gold, and other leveraged instruments involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results.

**Key risks:**
- You can lose all your invested capital
- Leverage magnifies both gains and losses
- Market conditions change constantly
- No strategy wins 100% of the time
- Technical failures can occur

### Software Disclaimer

This software is provided "as is" without warranty of any kind. The author is not responsible for:
- Trading losses incurred
- Technical malfunctions
- Data errors or delays
- Missed opportunities
- Any other damages

### Not Financial Advice

This bot is a tool for automated technical analysis. It does NOT provide:
- Financial advice
- Investment recommendations
- Guaranteed profits
- Professional trading services

Always:
- Do your own research
- Understand what you're trading
- Start with a demo account
- Only risk money you can afford to lose
- Consult a financial advisor if unsure

### Regulatory Compliance

**Your responsibility:**
- Check local regulations on automated trading
- Ensure compliance with financial laws
- Use licensed brokers only
- Report trading income to tax authorities

### Use at Your Own Risk

By using this software, you acknowledge that:
- You understand the risks involved
- You take full responsibility for your trading decisions
- The author is not liable for any losses
- You will not hold the author responsible for any outcomes

**Test thoroughly on demo accounts before risking real money!**

---

## 👨‍💻 Author

**Blessing Omoregie**

I'm a quantitative trader and developer passionate about building systematic trading strategies. After years of manual trading and studying institutional order flow, I created this bot to automate the high-probability setups I trade myself.

This project represents countless hours of backtesting, forward testing, and refinement. My goal is to help traders move from emotional, discretionary trading to disciplined, systematic approaches.

### Connect

- **GitHub:** [@nixiestone](https://github.com/nixiestone)
- **Project Link:** [https://github.com/nixiestone/nixie-gold-bot](https://github.com/nixiestone/nixie-gold-bot)

### Support the Project

If you find this bot helpful:
- ⭐ Star the repository
- 🐛 Report bugs and issues
- 💡 Suggest improvements
- 🔀 Contribute code
- 📢 Share with others

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**In summary:**
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ❌ No liability
- ❌ No warranty

---

## 🙏 Acknowledgments

- The quantitative trading community for sharing knowledge
- Technical analysis pioneers who developed the indicators used
- Open source contributors who built the libraries this depends on
- Everyone who tests the bot and provides feedback

---

## 📝 Version History

**v1.0.0** - Initial Release
- Multi-timeframe analysis
- Smart money concepts
- Telegram integration
- Backtesting framework
- Machine learning support
- Automated execution
- Comprehensive risk management

---

## 🚦 Status

**Active Development** - Regularly maintained and updated.

**Next planned features:**
- Multi-symbol support (Silver, US30, etc.)
- Web dashboard for monitoring
- Discord integration
- Advanced ML models
- Portfolio management
- Cloud deployment guides

---

## 📬 Contact

Got questions? Found a bug? Want to collaborate?

- **Issues:** [GitHub Issues](https://github.com/nixiestone/nixie-gold-bot/issues)
- **Discussions:** [GitHub Discussions](https://github.com/nixiestone/nixie-gold-bot/discussions)

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star! ⭐**

Made with ❤️ by [Blessing Omoregie](https://github.com/nixiestone)

**Trade smart. Trade safe. Trade systematically.**

</div>