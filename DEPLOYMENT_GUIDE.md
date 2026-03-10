# LEAH Bots Platform - Production Deployment Guide

**Target:** Ubuntu 22.04 LTS  
**Status:** Production-Ready  
**Last Updated:** 2026-03-10

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] Ubuntu 22.04 LTS server (clean installation)
- [ ] SSH access to server
- [ ] Telegram bot tokens (2 required)
- [ ] Groq API key
- [ ] Your Telegram ID
- [ ] Domain name (optional, for monitoring)
- [ ] 512MB+ RAM available
- [ ] 500MB+ disk space available

---

## 🚀 Step-by-Step Deployment

### Step 1: Connect to Server

```bash
ssh ubuntu@your_server_ip
```

### Step 2: Update System

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3.11-dev git curl wget
```

### Step 3: Create Application Directory

```bash
mkdir -p /home/ubuntu/leah-bots
cd /home/ubuntu/leah-bots
```

### Step 4: Clone Repository

```bash
git clone https://github.com/yourusername/leah-bots.git .
```

Or if not using git:

```bash
# Download and extract files manually
wget https://github.com/yourusername/leah-bots/archive/main.zip
unzip main.zip
mv leah-bots-main/* .
rm -rf leah-bots-main main.zip
```

### Step 5: Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Step 6: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed python-telegram-bot-21.5 groq-0.9.0 python-dotenv-1.0.1 requests-2.32.3 aiohttp-3.10.5
```

### Step 7: Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Fill in the following variables:

```
DEMO_BOT_TOKEN=your_demo_bot_token_here
ONBOARDING_BOT_TOKEN=your_onboarding_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
OWNER_TELEGRAM_ID=your_telegram_id_here
LOG_LEVEL=INFO
ENVIRONMENT=production
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

### Step 8: Test Local Execution

```bash
python3 app.py
```

**Expected Output:**
```
[2026-03-10T15:00:00.000Z] INFO - __main__: ======================================================================
[2026-03-10T15:00:00.000Z] INFO - __main__: 🚀 LEAH BOTS PLATFORM - STARTING
[2026-03-10T15:00:00.000Z] INFO - __main__: 🛡️ IRONCLAD SAFETY ENFORCEMENT ACTIVE
[2026-03-10T15:00:00.000Z] INFO - __main__: ======================================================================
[2026-03-10T15:00:00.000Z] INFO - __main__: ✅ BOTH BOTS STARTED SUCCESSFULLY
```

**Stop:** Press `Ctrl+C`

### Step 9: Set Up Systemd Service

```bash
sudo cp leah-bots.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable leah-bots
sudo systemctl start leah-bots
```

### Step 10: Verify Service Status

```bash
sudo systemctl status leah-bots
```

**Expected Output:**
```
● leah-bots.service - LEAH Bots Platform - AI-Powered Telegram Bots
     Loaded: loaded (/etc/systemd/system/leah-bots.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-03-10 15:00:00 UTC; 5s ago
   Main PID: 12345 (python3)
      Tasks: 2 (limit: 1024)
     Memory: 45.2M
        CPU: 1.234s
     CGroup: /system.slice/leah-bots.service
             └─12345 /home/ubuntu/leah-bots/venv/bin/python3 /home/ubuntu/leah-bots/app.py
```

### Step 11: Check Logs

```bash
sudo journalctl -u leah-bots -f
```

**Expected Output:**
```
Mar 10 15:00:00 ubuntu leah-bots[12345]: [2026-03-10T15:00:00.000Z] INFO - __main__: ✅ BOTH BOTS STARTED SUCCESSFULLY
Mar 10 15:00:00 ubuntu leah-bots[12345]: [2026-03-10T15:00:00.000Z] INFO - __main__: Demo Bot: @leah_luxury_host_demo_bot
Mar 10 15:00:00 ubuntu leah-bots[12345]: [2026-03-10T15:00:00.000Z] INFO - __main__: Onboarding Bot: @Leah_onboarding_bot
```

### Step 12: Test Bots on Telegram

**Test Demo Bot:**
```
1. Open Telegram
2. Search for @leah_luxury_host_demo_bot
3. Send: /start
4. Send: "What restaurants do you recommend?"
5. Verify response is received
```

**Test Onboarding Bot:**
```
1. Open Telegram
2. Search for @Leah_onboarding_bot
3. Send: /start
4. Complete setup process
5. Verify completion message
```

**Test Admin Commands:**
```
1. Send: /admin_status
2. Verify status response
```

---

## 🔧 Post-Deployment Configuration

### Enable Log Rotation

```bash
sudo nano /etc/logrotate.d/leah-bots
```

Paste:
```
/home/ubuntu/leah-bots/bot.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        sudo systemctl reload leah-bots > /dev/null 2>&1 || true
    endscript
}
```

### Set Up Monitoring

```bash
# Create monitoring script
cat > /home/ubuntu/leah-bots/monitor.sh << 'EOF'
#!/bin/bash

# Check if service is running
if ! systemctl is-active --quiet leah-bots; then
    echo "❌ LEAH Bots service is not running!"
    systemctl start leah-bots
    echo "✅ Service restarted"
fi

# Check disk space
DISK_USAGE=$(df /home/ubuntu/leah-bots | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️ Disk usage is high: ${DISK_USAGE}%"
fi

# Check memory usage
MEMORY_USAGE=$(ps aux | grep "[p]ython3 app.py" | awk '{print $6}')
echo "Memory usage: ${MEMORY_USAGE}KB"

# Check recent errors
ERRORS=$(grep "ERROR" /home/ubuntu/leah-bots/bot.log | tail -5)
if [ ! -z "$ERRORS" ]; then
    echo "⚠️ Recent errors found:"
    echo "$ERRORS"
fi

echo "✅ Monitoring check complete"
EOF

chmod +x /home/ubuntu/leah-bots/monitor.sh
```

### Set Up Cron Job for Monitoring

```bash
crontab -e
```

Add:
```
0 * * * * /home/ubuntu/leah-bots/monitor.sh >> /home/ubuntu/leah-bots/monitor.log 2>&1
```

---

## 🛠️ Maintenance

### Restart Service

```bash
sudo systemctl restart leah-bots
```

### Stop Service

```bash
sudo systemctl stop leah-bots
```

### View Logs

```bash
# Real-time logs
sudo journalctl -u leah-bots -f

# Last 100 lines
sudo journalctl -u leah-bots -n 100

# Logs from last hour
sudo journalctl -u leah-bots --since "1 hour ago"

# Logs with grep filter
sudo journalctl -u leah-bots | grep "SAFETY VIOLATION"
```

### Update Application

```bash
cd /home/ubuntu/leah-bots
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart leah-bots
```

### Check Service Status

```bash
sudo systemctl status leah-bots
```

### View Application Logs

```bash
tail -f /home/ubuntu/leah-bots/bot.log
```

---

## 🐛 Troubleshooting

### Service Won't Start

**Check logs:**
```bash
sudo journalctl -u leah-bots -n 50
```

**Common issues:**
- Missing `.env` file → Create from `.env.example`
- Invalid API keys → Verify credentials in `.env`
- Port already in use → Change port in config
- Python not found → Check venv is activated

**Solution:**
```bash
# Stop service
sudo systemctl stop leah-bots

# Check logs
sudo journalctl -u leah-bots -n 50

# Fix issue
nano /home/ubuntu/leah-bots/.env

# Restart service
sudo systemctl start leah-bots
```

### Bots Not Responding

**Check if service is running:**
```bash
sudo systemctl status leah-bots
```

**Check API connectivity:**
```bash
curl -s https://api.groq.com/health
```

**Check logs for errors:**
```bash
grep "ERROR" /home/ubuntu/leah-bots/bot.log | tail -10
```

**Restart service:**
```bash
sudo systemctl restart leah-bots
```

### High Memory Usage

**Check memory:**
```bash
ps aux | grep "python3 app.py"
```

**Solution:**
```bash
# Reduce conversation history in app.py
nano /home/ubuntu/leah-bots/app.py
# Change: conversation_history[-5:] to conversation_history[-3:]

# Restart service
sudo systemctl restart leah-bots
```

### Disk Space Issues

**Check disk usage:**
```bash
df -h /home/ubuntu/leah-bots
```

**Clean old logs:**
```bash
# Compress old logs
gzip /home/ubuntu/leah-bots/bot.log

# Remove logs older than 30 days
find /home/ubuntu/leah-bots -name "bot.log*" -mtime +30 -delete
```

---

## 📊 Monitoring Commands

### Check Service Health

```bash
# Service status
sudo systemctl status leah-bots

# Memory usage
ps aux | grep "python3 app.py" | grep -v grep

# Disk usage
du -sh /home/ubuntu/leah-bots

# Network connections
netstat -tlnp | grep python3
```

### View Statistics

```bash
# Total messages processed
grep "Message from" /home/ubuntu/leah-bots/bot.log | wc -l

# Safety violations
grep "SAFETY VIOLATION" /home/ubuntu/leah-bots/bot.log | wc -l

# API errors
grep "ERROR" /home/ubuntu/leah-bots/bot.log | wc -l

# Active conversations
grep "started conversation" /home/ubuntu/leah-bots/bot.log | tail -20
```

---

## 🔐 Security Hardening

### Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable
```

### File Permissions

```bash
# Set proper permissions
chmod 700 /home/ubuntu/leah-bots
chmod 600 /home/ubuntu/leah-bots/.env
chmod 644 /home/ubuntu/leah-bots/app.py
chmod 644 /home/ubuntu/leah-bots/requirements.txt
```

### Backup Configuration

```bash
# Create backup directory
mkdir -p /home/ubuntu/leah-bots/backups

# Backup .env file
cp /home/ubuntu/leah-bots/.env /home/ubuntu/leah-bots/backups/.env.backup

# Backup logs
cp /home/ubuntu/leah-bots/bot.log /home/ubuntu/leah-bots/backups/bot.log.backup
```

---

## 📞 Support & Troubleshooting

### Getting Help

1. **Check logs:** `sudo journalctl -u leah-bots -f`
2. **Review README:** `cat /home/ubuntu/leah-bots/README.md`
3. **Check policies:** `cat /home/ubuntu/leah-bots/SAFETY_RULES.md`
4. **Test manually:** `python3 /home/ubuntu/leah-bots/app.py`

### Reporting Issues

Include:
- Error message from logs
- Steps to reproduce
- Expected vs. actual behavior
- Server information (`uname -a`)
- Python version (`python3 --version`)

---

## ✅ Deployment Verification Checklist

After deployment, verify:

- [ ] Service is running: `sudo systemctl status leah-bots`
- [ ] Logs show successful startup
- [ ] Demo bot responds on Telegram
- [ ] Onboarding bot responds on Telegram
- [ ] Admin commands work: `/admin_status`
- [ ] Safety enforcement is active
- [ ] No errors in logs
- [ ] Memory usage is reasonable
- [ ] Disk space is available
- [ ] Service auto-starts on reboot

---

## 🎯 Next Steps

1. **Monitor performance** — Check logs regularly
2. **Update credentials** — Rotate API keys periodically
3. **Review logs** — Look for patterns or issues
4. **Test safety** — Verify enforcement is working
5. **Scale if needed** — Add more resources if required

---

**LEAH Bots Platform — Enterprise-Grade Deployment**

**Status:** ✅ Production-Ready  
**Safety:** 🛡️ IRONCLAD  
**Quality:** ⭐⭐⭐⭐⭐

---

*Last Updated: 2026-03-10*  
*Version: 1.0 (Production)*
