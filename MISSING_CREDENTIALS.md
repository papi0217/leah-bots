# LEAH Bots Platform — Missing Credentials Guide

**Status:** Code is 100% complete and production-ready.  
**What's Missing:** Only API credentials and bot tokens (4 items).  
**Setup Time:** 10 minutes to gather all credentials.

---

## 📋 Required Credentials (4 Total)

### 1. Demo Bot Token

**What it is:** Telegram bot token for the guest-facing concierge bot  
**Get it from:** https://t.me/botfather  
**Steps:**
1. Open Telegram and search for `@botfather`
2. Send: `/start`
3. Send: `/newbot`
4. Choose a name: `LEAH Luxury Concierge Demo`
5. Choose a username: `leah_luxury_host_demo_bot`
6. Copy the token provided (looks like: `123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh`)
7. Paste into `.env` as: `DEMO_BOT_TOKEN=your_token_here`

**Variable name in .env:** `DEMO_BOT_TOKEN`  
**The code is ready. This is the only thing missing.**

---

### 2. Onboarding Bot Token

**What it is:** Telegram bot token for the host-facing setup wizard  
**Get it from:** https://t.me/botfather  
**Steps:**
1. Open Telegram and search for `@botfather`
2. Send: `/start`
3. Send: `/newbot`
4. Choose a name: `LEAH Onboarding Assistant`
5. Choose a username: `Leah_onboarding_bot`
6. Copy the token provided (looks like: `123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh`)
7. Paste into `.env` as: `ONBOARDING_BOT_TOKEN=your_token_here`

**Variable name in .env:** `ONBOARDING_BOT_TOKEN`  
**The code is ready. This is the only thing missing.**

---

### 3. Groq API Key

**What it is:** API key for Groq AI service (provides intelligent responses)  
**Get it from:** https://console.groq.com  
**Steps:**
1. Go to https://console.groq.com
2. Sign up or log in with your account
3. Click "API Keys" in the left sidebar
4. Click "Create API Key"
5. Copy the API key (looks like: `gsk_abcdefghijklmnopqrstuvwxyz...`)
6. Paste into `.env` as: `GROQ_API_KEY=your_key_here`

**Variable name in .env:** `GROQ_API_KEY`  
**The code is ready. This is the only thing missing.**

---

### 4. Owner Telegram ID

**What it is:** Your personal Telegram ID (for admin commands)  
**Get it from:** https://t.me/userinfobot  
**Steps:**
1. Open Telegram and search for `@userinfobot`
2. Send: `/start`
3. The bot will show your ID (looks like: `123456789`)
4. Copy the ID
5. Paste into `.env` as: `OWNER_TELEGRAM_ID=your_id_here`

**Variable name in .env:** `OWNER_TELEGRAM_ID`  
**The code is ready. This is the only thing missing.**

---

## 🚀 Quick Setup (10 Minutes)

### Step 1: Gather Credentials (5 minutes)

```bash
# 1. Get Demo Bot Token from @botfather
DEMO_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh

# 2. Get Onboarding Bot Token from @botfather
ONBOARDING_BOT_TOKEN=987654321:ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvuts

# 3. Get Groq API Key from https://console.groq.com
GROQ_API_KEY=gsk_abcdefghijklmnopqrstuvwxyz1234567890

# 4. Get Your Telegram ID from @userinfobot
OWNER_TELEGRAM_ID=123456789
```

### Step 2: Update .env File (3 minutes)

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Fill in:**
```
DEMO_BOT_TOKEN=your_demo_bot_token_here
ONBOARDING_BOT_TOKEN=your_onboarding_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
OWNER_TELEGRAM_ID=your_telegram_id_here
```

### Step 3: Run Bots (2 minutes)

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start bots
python3 app.py
```

**Expected output:**
```
[2026-03-10T15:00:00.000Z] INFO - __main__: ✅ BOTH BOTS STARTED SUCCESSFULLY
```

---

## ✅ Verification Checklist

After adding credentials, verify:

- [ ] `.env` file created with all 4 variables
- [ ] All values are non-empty
- [ ] No quotes around values (unless specified)
- [ ] Tokens start with numbers followed by colon
- [ ] Groq key starts with `gsk_`
- [ ] Telegram ID is numeric only
- [ ] Bots start without errors
- [ ] Demo bot responds on Telegram
- [ ] Onboarding bot responds on Telegram
- [ ] Admin commands work: `/admin_status`

---

## 🔍 Credential Format Reference

**Demo Bot Token:**
```
Format: 123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh
Length: ~50 characters
Starts with: Numbers, then colon
Source: @botfather
```

**Onboarding Bot Token:**
```
Format: 987654321:ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvuts
Length: ~50 characters
Starts with: Numbers, then colon
Source: @botfather
```

**Groq API Key:**
```
Format: gsk_abcdefghijklmnopqrstuvwxyz1234567890
Length: ~40+ characters
Starts with: gsk_
Source: https://console.groq.com
```

**Owner Telegram ID:**
```
Format: 123456789
Length: 9-10 digits
Starts with: Numbers only
Source: @userinfobot
```

---

## 🛡️ Security Notes

**IMPORTANT:**
- ✅ Never commit `.env` file to GitHub (it's in `.gitignore`)
- ✅ Never share your API keys or tokens
- ✅ Never paste credentials in public channels
- ✅ Rotate keys periodically
- ✅ Use strong, unique credentials
- ✅ Store backups securely

**Safe Storage:**
```bash
# Keep .env file secure
chmod 600 .env

# Backup securely
cp .env /secure/location/.env.backup
chmod 600 /secure/location/.env.backup
```

---

## 🚨 Troubleshooting

### "Missing required environment variables"

**Problem:** Error when starting bots

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check all variables are set
grep -E "^(DEMO_BOT_TOKEN|ONBOARDING_BOT_TOKEN|GROQ_API_KEY|OWNER_TELEGRAM_ID)" .env

# Verify no empty values
grep "=PASTE_YOUR" .env
```

### "Invalid token format"

**Problem:** Telegram bot token rejected

**Solution:**
1. Verify token format: `numbers:letters`
2. Copy token directly from @botfather (no extra spaces)
3. Check token is for correct bot
4. Regenerate token if needed

### "API key invalid"

**Problem:** Groq API key rejected

**Solution:**
1. Verify key starts with `gsk_`
2. Copy key directly from console.groq.com
3. Check key hasn't expired
4. Generate new key if needed

### "Telegram ID not recognized"

**Problem:** Admin commands don't work

**Solution:**
1. Verify ID is numeric only
2. Get ID from @userinfobot
3. Check no spaces or special characters
4. Verify it's your personal ID, not a group ID

---

## 📞 Support

If you encounter issues:

1. **Check logs:** `tail -f bot.log`
2. **Review README:** `cat README.md`
3. **Check credentials:** `grep -v "^#" .env | grep -v "^$"`
4. **Test manually:** `python3 app.py`

---

## ✨ Summary

**The code is 100% complete and production-ready.**

All you need to do:
1. Get 4 credentials (10 minutes)
2. Update `.env` file (3 minutes)
3. Run bots (2 minutes)
4. Test on Telegram (5 minutes)

**Total setup time: 20 minutes**

---

**LEAH Bots Platform — Ready for Deployment**

**Status:** ✅ Code Complete  
**Missing:** 🔑 4 API Credentials  
**Setup Time:** ⏱️ 20 minutes

---

*Last Updated: 2026-03-10*  
*Version: 1.0 (Production)*
