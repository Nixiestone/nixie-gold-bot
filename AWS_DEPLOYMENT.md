# 🚀 AWS Free Tier Deployment Guide

## Deploy Nixie's Gold Bot to Run 24/7 for FREE (First 12 Months)

This guide will walk you through deploying your trading bot on Amazon Web Services (AWS) using their Free Tier offering. No technical background needed - just follow each step carefully!

---

## 📋 What You Get with AWS Free Tier

- **750 hours/month** of server time (enough for 24/7 operation)
- **1 vCPU + 1 GB RAM** Windows Server
- **30 GB storage**
- **Free for 12 months** after signing up
- **Location:** Choose closest data center for lowest latency

---

## 🎯 Overview - What We're Going to Do

1. ✅ Create AWS account
2. ✅ Launch Windows server in the cloud
3. ✅ Connect to the server
4. ✅ Install Python and MT5
5. ✅ Upload and configure the bot
6. ✅ Set up automatic restarts
7. ✅ Monitor and maintain

**Time needed:** 45-60 minutes for first-time setup

---

## 📦 Part 1: Prepare Your Bot Locally

Before deploying to AWS, let's prepare everything on your computer.

### Step 1.1: Run AWS Setup Script

```bash
# In your project folder
python setup_aws.py
```

This creates:
- `launcher.py` - Keeps bot running
- `start_bot.bat` - Easy Windows startup
- `health_check.py` - Verify everything works
- `requirements_aws.txt` - Minimal dependencies

### Step 1.2: Edit Your .env File

Make sure your `.env` has production settings:

```bash
ENVIRONMENT=production
TELEGRAM_BOT_TOKEN=your_actual_token
TELEGRAM_CHAT_ID=your_actual_chat_id
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
```

### Step 1.3: Test Locally First

```bash
# Test health check
python health_check.py

# Test bot starts correctly
python main.py
# Let it run for 5 minutes, then Ctrl+C

# Test launcher
python launcher.py
# Let it run, verify it restarts if you stop main.py
# Ctrl+C to stop
```

### Step 1.4: Create Deployment Package

Create a folder with these files:
```
nixie-gold-bot-deploy/
├── main.py
├── config.py
├── launcher.py
├── setup_aws.py
├── health_check.py
├── start_bot.bat
├── requirements_aws.txt
├── .env (with your actual credentials!)
├── data/
│   └── (all files)
├── indicators/
│   └── (all files)
├── strategy/
│   └── (all files)
├── execution/
│   └── (all files)
├── models/
│   └── (all files)
└── backtest/
    └── (all files)
```

**Compress this folder to a .zip file** - we'll upload it to AWS later.

---

## 🏗️ Part 2: Create AWS Account & Launch Server

### Step 2.1: Sign Up for AWS

1. Go to **https://aws.amazon.com/free**
2. Click **"Create a Free Account"**
3. Fill in:
   - Email address
   - Password
   - AWS account name (e.g., "MyTradingAccount")
4. Contact information:
   - Account type: **Personal**
   - Fill in your details
5. Payment information:
   - **Credit card required** (for verification only)
   - They'll charge ~$1 and refund immediately
   - You won't be charged if you stay within free tier limits
6. Verify identity:
   - Phone verification
   - Enter code they text/call you
7. Select support plan:
   - Choose **"Basic support - Free"**
8. Complete!

⏰ **Wait 5-10 minutes** for account activation email.

### Step 2.2: Launch Your Server

1. **Log in** to AWS Console: https://console.aws.amazon.com

2. **Search for EC2**:
   - Top search bar → type "EC2"
   - Click "EC2" (Virtual Servers in the Cloud)

3. **Check Your Region** (top-right corner):
   - Choose closest to you:
     - US East (N. Virginia) - `us-east-1`
     - Europe (Frankfurt) - `eu-central-1`
     - Asia Pacific (Singapore) - `ap-southeast-1`
   - **Write this down!** Your server will be here.

4. **Click "Launch Instance"** (big orange button)

5. **Configure Instance**:

   **Name:**
   ```
   NixieGoldBot
   ```

   **Application and OS Images (AMI):**
   - Click: **Windows**
   - Select: **Microsoft Windows Server 2022 Base**
   - Verify tag: **"Free tier eligible"** ✅
   - Architecture: 64-bit (x86)

   **Instance Type:**
   - Select: **t2.micro**
   - Shows: "Free tier eligible" ✅
   - 1 vCPU, 1 GiB Memory

   **Key Pair (login):**
   - Click: **"Create new key pair"**
   - Name: `nixie-trading-key`
   - Type: **RSA**
   - Format: **.pem** (or .ppk if using PuTTY)
   - Click: **"Create key pair"**
   - **File downloads** → Save it somewhere safe!
   - ⚠️ **CRITICAL:** Don't lose this file! You can't login without it!

   **Network Settings:**
   - Check: ✅ **"Allow RDP traffic from"**
   - Source: **"My IP"** (more secure) or **"Anywhere"** (easier)
   - Security Group Name: `nixie-bot-security`

   **Configure Storage:**
   - 30 GB gp3 (default is fine)
   - Keep "Delete on termination" checked

   **Advanced Details:**
   - Leave everything as default

6. **Review Summary** on the right:
   - Free tier eligible: ✅
   - Windows Server 2022: ✅
   - t2.micro: ✅

7. **Click "Launch Instance"** (orange button)

8. **Success!**
   - Click "View all instances"
   - You'll see your instance starting up
   - ⏰ **Wait 3-5 minutes** for "Instance State" to show **"Running"**

---

## 🔐 Part 3: Connect to Your Server

### Step 3.1: Get Your Password

1. In **EC2 Dashboard**, click on your instance (checkbox)

2. Click **"Connect"** button (top)

3. Click **"RDP client"** tab

4. Click **"Get Password"**

5. Click **"Upload private key file"**
   - Select the `.pem` file you downloaded earlier

6. Click **"Decrypt Password"**

7. **Copy the password** shown (you'll need it!)

8. Also copy the **"Public DNS"** address (looks like: `ec2-X-X-X-X.compute.amazonaws.com`)

### Step 3.2: Connect via Remote Desktop

**On Windows:**

1. Search: **"Remote Desktop Connection"** (or press `Win + R` → type `mstsc`)

2. Computer: **Paste the Public DNS**

3. Click **"Show Options"**

4. User name: **Administrator**

5. Click **"Connect"**

6. Enter **Password** (the decrypted one)

7. Certificate warning → Click **"Yes"**

8. **You're in!** 🎉

**On Mac:**

1. Download **"Microsoft Remote Desktop"** from App Store

2. Click **"Add PC"**

3. PC Name: **Paste Public DNS**

4. User account: **Administrator**

5. Password: **Paste decrypted password**

6. Click **"Add"** then double-click to connect

**On Linux:**

1. Install Remmina: `sudo apt install remmina`

2. Open Remmina → New Connection

3. Protocol: **RDP**

4. Server: **Paste Public DNS**

5. Username: **Administrator**

6. Password: **Paste decrypted password**

7. Connect!

---

## 🛠️ Part 4: Set Up the Server

**All these steps happen INSIDE the remote desktop window (on the cloud server)!**

### Step 4.1: Disable IE Enhanced Security

(This lets you download files)

1. **Server Manager** should open automatically
   - If not: Click Start → Server Manager

2. Click **"Local Server"** (left sidebar)

3. Find **"IE Enhanced Security Configuration"**

4. Click **"On"** next to it

5. Set both to **"Off"**:
   - Administrators: **Off**
   - Users: **Off**

6. Click **"OK"**

### Step 4.2: Install Python

1. Open **Microsoft Edge** browser

2. Go to: **https://www.python.org/downloads/**

3. Download: **Python 3.11.9** (or latest 3.11.x)

4. **Run the installer**

5. ⚠️ **CRITICAL:** Check ✅ **"Add Python to PATH"**

6. Click **"Install Now"**

7. Wait for installation

8. Click **"Close"**

9. **Verify installation:**
   - Open Command Prompt (search "cmd")
   - Type: `python --version`
   - Should show: `Python 3.11.9` ✅

### Step 4.3: Install MetaTrader 5

1. In Edge, go to your **broker's website**

2. Download **MetaTrader 5**

3. Install it

4. **Log in** with your trading account

5. **Enable Algo Trading:**
   - Tools → Options
   - Expert Advisors tab
   - Check ✅ **"Allow algorithmic trading"**
   - Check ✅ **"Allow DLL imports"**
   - Click **"OK"**

6. **Verify XAUUSDm symbol:**
   - View → Market Watch (or Ctrl+M)
   - Right-click → **"Show All"**
   - Find your gold symbol (XAUUSDm)
   - Double-click to open a chart

7. **Keep MT5 running!** Minimize it, don't close.

### Step 4.4: Upload Your Bot

**Option 1: Download from GitHub (if you pushed to GitHub)**

1. In Edge, go to: `https://github.com/nixiestone/nixie-gold-bot`

2. Click **"Code"** → **"Download ZIP"**

3. Extract to Desktop

**Option 2: Transfer via RDP**

1. On your **local computer**:
   - Copy the `nixie-gold-bot-deploy.zip` you created earlier

2. In **Remote Desktop window**:
   - Paste on the Desktop (Ctrl+V)
   - Right-click → Extract All
   - Extract to Desktop

### Step 4.5: Install Python Packages

1. Open **Command Prompt** as Administrator:
   - Search "cmd"
   - Right-click → **"Run as administrator"**

2. Navigate to bot folder:
   ```cmd
   cd Desktop\nixie-gold-bot
   ```

3. Create virtual environment:
   ```cmd
   python -m venv venv
   ```

4. Activate it:
   ```cmd
   venv\Scripts\activate
   ```

5. Install packages:
   ```cmd
   pip install --upgrade pip
   pip install -r requirements_aws.txt
   ```

6. Wait 5-10 minutes for installation

### Step 4.6: Configure .env File

1. Open **.env** file (right-click → Edit)

2. Make sure it has YOUR real credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_real_token
   TELEGRAM_CHAT_ID=your_real_chat_id
   MT5_LOGIN=your_real_account
   MT5_PASSWORD=your_real_password
   MT5_SERVER=your_real_server
   ENVIRONMENT=production
   ```

3. Save and close

### Step 4.7: Test Everything

```cmd
# Test health check
python health_check.py
```

Expected output:
```
✅ Python: 3.11.9
✅ Virtual Env: Yes
✅ .env file: Found
✅ MT5 Import: Success
✅ Telegram Import: Success
✅ Logs directory: Found
```

```cmd
# Test bot startup
python main.py
```

Let it run for 2-3 minutes. You should see:
- ✅ Connected to MT5
- ✅ Fetching data
- ✅ Scanning for signals
- Maybe a startup message on Telegram

Press `Ctrl+C` to stop.

### Step 4.8: (Optional) Enable Multi-User Broadcasting

If you want to share signals with multiple people:

**Option A: Let users subscribe themselves**

Open a second Command Prompt:
```cmd
cd Desktop\nixie-gold-bot
venv\Scripts\activate
python execution\telegram_multi_user.py interactive
```

Keep this running! Users can now send `/start` to your bot.

**Option B: Add users manually**

Create `subscribers.json` on Desktop:
```json
[
  123456789,
  987654321
]
```

---

## 🚀 Part 5: Start Bot Permanently

### Method 1: Using Launcher (Recommended)

```cmd
# Start the launcher
python launcher.py
```

The launcher will:
- ✅ Start your bot
- ✅ Monitor it continuously
- ✅ Restart if it crashes
- ✅ Log everything
- ✅ Prevent infinite restart loops

**Keep this Command Prompt window open!**

### Method 2: With Multi-User Broadcasting (Advanced)

If using multi-user mode, you need TWO windows:

**Command Prompt 1:** Interactive bot (subscriptions)
```cmd
cd Desktop\nixie-gold-bot
venv\Scripts\activate
python execution\telegram_multi_user.py interactive
```

**Command Prompt 2:** Main bot (signals)
```cmd
cd Desktop\nixie-gold-bot
venv\Scripts\activate
python launcher.py
```

Both stay open and running!

### Method 3: Using Batch File (Easiest)

1. Double-click **start_bot.bat** on Desktop

2. Bot starts automatically

3. Window stays open - don't close it!

### Important: Disconnecting Correctly

**DO NOT click "Shut Down" inside the Windows server!**

Instead:
1. Just **close the Remote Desktop window** (click X on YOUR computer)
2. Or click **"Disconnect"** from the Windows start menu
3. Server keeps running 24/7 ✅
4. Your bot keeps scanning ✅

---

## 📊 Part 6: Monitoring & Maintenance

### Reconnecting to Check on Bot

1. Open Remote Desktop Connection

2. Enter same Public DNS and credentials

3. You'll see your Command Prompt still running!

### Check Logs

```cmd
# View launcher log
type logs\launcher.log

# View bot log
type logs\trading.log

# View last 20 lines
powershell -command "Get-Content logs\trading.log -Tail 20"
```

### Telegram Monitoring

Your bot sends:
- ✅ Startup notification
- ✅ Trading signals
- ✅ Error alerts
- ✅ Daily summaries

### Weekly Maintenance

**Monday morning routine:**

1. Reconnect via RDP

2. Check bot is running:
   ```cmd
   tasklist | findstr python
   ```

3. Check logs for errors:
   ```cmd
   powershell -command "Get-Content logs\trading.log -Tail 50"
   ```

4. Verify MT5 is logged in (check MT5 window)

5. Check AWS billing (should be $0.00)

6. Disconnect

### Restarting Bot

If you need to restart:

1. Reconnect via RDP

2. In Command Prompt window: **Ctrl+C** (stop launcher)

3. Start again:
   ```cmd
   python launcher.py
   ```

Or just double-click **start_bot.bat** again!

---

## 💰 Part 7: Set Up Billing Alerts (Important!)

Protect yourself from unexpected charges:

### Step 7.1: Enable Billing Alerts

1. In AWS Console, click your name (top-right)

2. Click **"Billing and Cost Management"**

3. Click **"Billing preferences"** (left sidebar)

4. Check ✅ **"Receive Free Tier Usage Alerts"**

5. Enter your email

6. Click **"Save preferences"**

### Step 7.2: Create Budget Alert

1. Click **"Budgets"** (left sidebar)

2. Click **"Create budget"**

3. Select **"Zero spend budget"**
   - This alerts you if you're charged ANYTHING

4. Budget name: `NixieBotAlert`

5. Email: Your email

6. Click **"Create budget"**

7. You'll get email if any charges occur!

### Step 7.3: Monitor Usage

Check weekly:
1. Billing Dashboard
2. Free Tier usage bar
3. Should show ~750/750 hours used (normal for 24/7)

---

## 🔒 Part 8: Security Best Practices

### 8.1: Restrict RDP Access

1. Go to **EC2 → Security Groups**

2. Click your security group

3. Edit **"Inbound rules"**

4. RDP rule → Change source to **"My IP"**

5. Save

Now only YOUR IP can connect!

### 8.2: Regular Windows Updates

Monthly:
1. Reconnect to server
2. Windows Update → Check for updates
3. Install important updates
4. Restart if needed (bot will auto-restart)

### 8.3: Change Administrator Password

1. Reconnect to server

2. Ctrl+Alt+End (Remote Desktop equivalent of Ctrl+Alt+Del)

3. Change password

4. Write it down securely!

### 8.4: Backup Your Bot

Weekly:
1. Copy entire bot folder
2. Download to your computer
3. Keep 3 backups (weekly rotation)

---

## 🎯 Part 9: Optimization Tips

### 9.1: Reduce Memory Usage

In `config.py`:
```python
# Scan less frequently
SCAN_INTERVAL_MINUTES = 20  # Instead of 15

# Disable ML initially
USE_ML_FILTER = False

# Use fewer bars
# In data_handler.py get_gold_data() calls:
# 200 instead of 500 for H4
# 500 instead of 1000 for M15
```

### 9.2: Keep MT5 Lightweight

- Close unnecessary charts
- Use simple chart template
- Disable news feed
- Remove indicators from charts

### 9.3: Monitor Performance

```cmd
# Check memory usage
wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value

# Check if anything is using too much RAM
tasklist /FI "MEMUSAGE gt 100000"
```

If memory > 80% full:
- Restart MT5
- Restart bot
- Consider disabling ML filter

---

## 🆘 Part 10: Troubleshooting

### Bot Not Starting

```cmd
# Check Python
python --version

# Check virtual env activated
# Should see (venv) in prompt

# Check .env exists
dir .env

# Run health check
python health_check.py

# Check for errors
python main.py
```

### MT5 Not Connecting

1. Open MT5 manually
2. Check login status (bottom-right)
3. Tools → Options → Expert Advisors
4. Verify "Allow algorithmic trading" is checked
5. Restart MT5

### Telegram Not Working

```cmd
# Test telegram
python execution\telegram_bot.py
```

Check:
- Bot token correct in .env
- Chat ID correct
- You messaged bot first
- Internet connection working

### Server Won't Connect

- Check instance is **Running** (not stopped)
- Verify correct Public DNS
- Check security group allows RDP from your IP
- Reboot instance: Actions → Instance state → Reboot

### Instance Stopped Unexpectedly

Reasons:
- AWS issue (rare)
- You stopped it accidentally
- Billing issue

Fix:
1. Go to EC2 Dashboard
2. Select instance
3. Instance state → Start instance
4. Wait for "Running" status
5. Reconnect and restart bot

---

## 📋 Quick Reference Commands

```cmd
# Navigate to bot
cd Desktop\nixie-gold-bot

# Activate virtual environment
venv\Scripts\activate

# Check health
python health_check.py

# Start bot with launcher
python launcher.py

# View logs
type logs\trading.log

# Check if running
tasklist | findstr python

# Stop bot
Ctrl + C
```

---

## ✅ Success Checklist

After setup, verify:

- [ ] AWS account created
- [ ] Instance running (green dot)
- [ ] Can connect via RDP
- [ ] Python 3.11.9 installed
- [ ] MT5 installed and logged in
- [ ] Bot folder on Desktop
- [ ] Virtual environment created
- [ ] Packages installed
- [ ] .env configured with real credentials
- [ ] Health check passes
- [ ] Bot starts without errors
- [ ] Telegram notifications working
- [ ] Launcher keeps bot running
- [ ] Billing alerts configured
- [ ] Can disconnect and reconnect
- [ ] Bot survives disconnection

---

## 🎓 What You Learned

You now have:
- ✅ Cloud server running 24/7
- ✅ Automated trading bot monitoring markets
- ✅ Auto-restart if crashes
- ✅ Telegram notifications
- ✅ Proper logging
- ✅ Secure setup
- ✅ Cost monitoring

**Total cost: $0** for first 12 months! 🎉

---

## 📞 Need Help?

**Common issues solved:**
- See troubleshooting section above
- Check logs first: `logs/trading.log`
- Test components individually
- Restart MT5 if connection issues

**Still stuck?**
- GitHub Issues: [Report a problem](https://github.com/nixiestone/nixie-gold-bot/issues)
- Include: Error message, what you were doing, logs

---

**🎉 Congratulations! Your bot is now running 24/7 in the cloud!**

Made with ❤️ by Blessing Omoregie (@nixiestone)