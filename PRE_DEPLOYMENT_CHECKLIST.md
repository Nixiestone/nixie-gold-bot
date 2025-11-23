# ✅ Pre-Deployment Checklist

## Before deploying to AWS, complete this checklist!

---

## 📋 Local Testing Complete

- [ ] Bot runs on local machine without errors
- [ ] MT5 connects successfully
- [ ] All indicators calculate correctly
- [ ] Telegram bot sends test messages
- [ ] Configuration validated (`python config.py`)
- [ ] Health check passes (`python health_check.py`)
- [ ] Bot ran for at least 24 hours locally
- [ ] Reviewed logs for any errors
- [ ] No import errors or missing dependencies

---

## 🔐 Credentials & Security

- [ ] `.env` file has all real credentials (not placeholders!)
- [ ] Telegram bot token is correct
- [ ] Telegram chat ID is correct
- [ ] MT5 login credentials are correct
- [ ] MT5 server name is exactly correct
- [ ] Tested Telegram message delivery
- [ ] Password is strong (if using live account)
- [ ] 2FA enabled on trading account (if available)

---

## 💰 Account & Risk Settings

- [ ] Using **demo account** for first deployment
- [ ] Account balance in `.env` matches actual balance
- [ ] Risk percent set appropriately (1-2% max)
- [ ] Symbol name matches broker's exactly (XAUUSDm)
- [ ] Comfortable with position sizing formula
- [ ] Understand stop loss placement
- [ ] Know how to manually close positions if needed
- [ ] Have emergency plan if internet fails

---

## 📊 Strategy Understanding

- [ ] Read and understand the full README
- [ ] Know all 6 conditions for signal generation
- [ ] Understand why strategy is selective
- [ ] Comfortable with 0-3 signals per week
- [ ] Understand liquidity sweep concept
- [ ] Know difference between dev and production mode
- [ ] Reviewed backtesting results
- [ ] Know expected win rate (65-75%)

---

## 🛠️ Files Ready for Upload

- [ ] All `.py` files present and tested
- [ ] `launcher.py` created
- [ ] `setup_aws.py` created
- [ ] `health_check.py` created
- [ ] `start_bot.bat` created
- [ ] `requirements_aws.txt` created
- [ ] `.env` file with production credentials
- [ ] All directories created (logs/, models/, data/)
- [ ] `__init__.py` files in all packages

---

## ☁️ AWS Prerequisites

- [ ] AWS account created
- [ ] Credit card verified (for identity)
- [ ] Email verified
- [ ] Can access AWS Console
- [ ] Know which region to use (closest to you)
- [ ] Understand Free Tier limits (750 hours/month)
- [ ] Billing alerts will be configured
- [ ] Have key pair file ready (.pem)
- [ ] Can connect via Remote Desktop

---

## 📱 Communication Setup

- [ ] Phone number works for 2FA
- [ ] Email notifications enabled
- [ ] Telegram installed on phone
- [ ] Started chat with your bot
- [ ] Tested receiving messages
- [ ] Know how to check Telegram on mobile
- [ ] Have backup contact method

---

## 🧪 Testing Completed

**Local Tests:**
- [ ] `python config.py` → Passes ✅
- [ ] `python data/data_handler.py` → Connects ✅
- [ ] `python indicators/technical.py` → Calculates ✅
- [ ] `python strategy/signal_generator.py` → Analyzes ✅
- [ ] `python execution/telegram_bot.py` → Sends ✅
- [ ] `python health_check.py` → All green ✅
- [ ] `python main.py` → Runs 10+ minutes ✅
- [ ] `python launcher.py` → Auto-restarts ✅

**Backtest:**
- [ ] Ran backtest successfully
- [ ] Understand results (even if no signals)
- [ ] Ran diagnostic tool
- [ ] Know why signals are/aren't generated

---

## 📖 Documentation Review

- [ ] Read README.md completely
- [ ] Read AWS_DEPLOYMENT.md completely
- [ ] Read QUICKSTART.md
- [ ] Bookmarked GitHub repo
- [ ] Know where to find help
- [ ] Understand disclaimer and risks
- [ ] Ready to follow guide step-by-step

---

## ⏱️ Time & Resources

- [ ] Have 60+ minutes for initial setup
- [ ] Stable internet connection
- [ ] Not rushing or distracted
- [ ] MT5 installer downloaded
- [ ] Python installer downloaded
- [ ] Bot files ready to upload
- [ ] Can stay connected for full setup

---

## 🎯 Expectations Set

- [ ] Understand bot is very selective
- [ ] Comfortable with 0-3 signals per week
- [ ] Know this is not "get rich quick"
- [ ] Prepared to wait for quality setups
- [ ] Won't panic if no signals for days
- [ ] Will follow risk management strictly
- [ ] Won't modify strategy during testing
- [ ] Committed to 30+ days demo testing

---

## 💾 Backup Plan

- [ ] Have backup of all bot files
- [ ] Saved `.env` file securely offline
- [ ] Wrote down all credentials separately
- [ ] Know how to download from GitHub
- [ ] Can recreate environment if needed
- [ ] Have local copy before uploading

---

## 🚨 Emergency Contacts

- [ ] Know broker's support number
- [ ] Have AWS support bookmarked
- [ ] Saved MT5 login details offline
- [ ] Know how to stop bot (Ctrl+C)
- [ ] Know how to close all positions manually
- [ ] Have trading journal ready

---

## 📊 Monitoring Plan

**Daily:**
- [ ] Will check Telegram for signals
- [ ] Will verify bot is running (if on AWS)
- [ ] Will check logs for errors

**Weekly:**
- [ ] Will reconnect to AWS and check status
- [ ] Will review all signals and outcomes
- [ ] Will check AWS billing (should be $0)
- [ ] Will update trade logger

**Monthly:**
- [ ] Will analyze win rate
- [ ] Will retrain ML model (if 20+ trades)
- [ ] Will review and adjust parameters
- [ ] Will check for updates

---

## ✅ Final Pre-Flight

- [ ] Everything above is checked ✅
- [ ] Feeling confident and prepared
- [ ] Not rushed or uncertain
- [ ] Ready to follow guide exactly
- [ ] Understand this is a learning process
- [ ] Committed to proper testing
- [ ] Ready to deploy!

---

## 🎯 Go/No-Go Decision

**GREEN LIGHT (Ready to Deploy):**
- All checklist items are ✅
- Feeling confident
- Have time to complete setup
- Not distracted

**RED LIGHT (Not Ready Yet):**
- Missing checklist items
- Unsure about something
- Rushed or distracted
- Need to test more locally

---

## 📞 If You're Not Sure

**Ask yourself:**

1. Can the bot run on my computer for 24 hours without errors?
2. Do I understand why signals are generated?
3. Am I using a demo account first?
4. Have I read all the documentation?
5. Do I have 60+ minutes for AWS setup?

**If any answer is "No"** → Test more locally first!

**If all answers are "Yes"** → You're ready! 🚀

---

## 🚀 Ready to Deploy?

If everything is checked:

1. **Save this checklist** (you did great!)
2. **Open:** [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)
3. **Follow it step by step**
4. **Don't skip any steps**
5. **Take your time**

**You got this! 💪**

---

**Questions before deploying?**

- Review: [README.md](README.md)
- Check: [QUICKSTART.md](QUICKSTART.md)
- Ask: [GitHub Discussions](https://github.com/nixiestone/nixie-gold-bot/discussions)

---

Made with ❤️ by Blessing Omoregie (@nixiestone)

*Safety first. Test thoroughly. Deploy confidently.*