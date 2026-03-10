# LEAH Bots Deployment Guide

Complete step-by-step guide for deploying LEAH bots to production.

## Prerequisites

Before deploying, ensure you have:

1. **GitHub Account** — For version control
2. **Railway Account** — https://railway.app (free tier available)
3. **Telegram Account** — For testing bots
4. **Node.js & npm** — For Railway CLI
5. **Git** — For version control
6. **Python 3.8+** — For local testing

## Required Credentials

Gather these before starting deployment:

| Credential | Source | Example |
|-----------|--------|---------|
| Demo Bot Token | @BotFather | `your_demo_token` |
| Onboarding Bot Token | @BotFather | `your_onboarding_token` |
| Groq API Key | https://console.groq.com | `your_groq_key` |
| Weather API Key | https://openweathermap.org/api | `your_weather_key` |
| Your Telegram ID | @userinfobot | `your_telegram_id` |

## Quick Deploy (5 Minutes)

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

Browser opens. Sign in with GitHub.

### Step 3: Clone Repository

```bash
git clone https://github.com/papi0217/leah-bots.git
cd leah-bots
```

### Step 4: Initialize Railway Project

```bash
railway init
```

Answer prompts:
- Create new project: `y`
- Project name: `leah-bots`
- Environment: (press Enter for default)

### Step 5: Set Environment Variables

Replace values with your credentials:

```bash
railway variables set \
  DEMO_BOT_TOKEN=your_demo_token \
  ONBOARDING_BOT_TOKEN=your_onboarding_token \
  GROQ_API_KEY=your_groq_key \
  WEATHER_API_KEY=your_weather_key \
  OWNER_TELEGRAM_ID=your_telegram_id \
  RENDER=true \
  LOG_LEVEL=INFO
```

### Step 6: Deploy

```bash
railway up
```

Wait 10-15 minutes for deployment to complete.

### Step 7: Verify Deployment

```bash
railway logs -f
```

Look for:
```
✅ Demo bot started — @leah_luxury_host_demo_bot
✅ Onboarding bot started — @Leah_onboarding_bot
🚀 Both bots are live and polling for messages...
```

## Local Testing

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
# nano .env  (or use your editor)
```

### Run Bots Locally

```bash
python app.py
```

Bots will start polling. Send messages on Telegram to test.

### Stop Bots

Press `Ctrl+C` in terminal.

## Testing Bots

### Test Demo Bot

1. Open Telegram
2. Search: `@leah_luxury_host_demo_bot`
3. Send: `/start`
4. Expected response: Welcome message with menu

### Test Onboarding Bot

1. Open Telegram
2. Search: `@Leah_onboarding_bot`
3. Send: `/start`
4. Expected response: Property setup wizard

### Test Features

**Demo Bot:**
- `/amenities` — List property amenities
- `/restaurants` — Get restaurant recommendations
- `/weather` — Current weather
- `/issue` — Report an issue

**Onboarding Bot:**
- `/property_name` — Set property name
- `/guest_capacity` — Set max guests
- `/amenities` — Add amenities
- `/rules` — Set house rules

## Monitoring

### View Logs

```bash
# Real-time logs
railway logs -f

# Last 50 lines
railway logs --tail 50

# Search for errors
railway logs | grep -i error

# Save to file
railway logs > deployment.log
```

### Check Status

```bash
railway status
```

### View Variables

```bash
railway variables
```

### View Deployments

```bash
railway deployments
```

## Troubleshooting

### Issue: "Cannot login in non-interactive mode"

**Solution:**
```bash
railway login
```

### Issue: "Project not found"

**Solution:**
```bash
railway init
```

### Issue: "Deployment failed"

**Check logs:**
```bash
railway logs -f | grep -i error
```

**Common causes:**
- Invalid bot token
- Missing API key
- Dockerfile issues
- Port conflicts

### Issue: "Bot not responding on Telegram"

**Verify deployment:**
```bash
railway status
railway logs -f
```

**Check:**
- Bot token is correct
- Bot is online (@BotFather → /mybots)
- No errors in logs
- Railway service is running

### Issue: "API key invalid"

**Solution:**
1. Verify key is correct
2. Check API quota at provider dashboard
3. Regenerate key if needed
4. Update with: `railway variables set KEY=new_value`
5. Redeploy: `railway up --force`

## Updating Deployment

### Update Code

```bash
# Make changes locally
git add .
git commit -m "Update: description"
git push

# Redeploy
railway up --force
```

### Update Environment Variables

```bash
# Update single variable
railway variables set KEY=new_value

# Redeploy
railway up --force

# Verify
railway logs -f
```

### Rollback Deployment

```bash
# View deployment history
railway deployments

# Rollback to previous
railway deployments --id <deployment_id> --rollback
```

## Production Checklist

- [ ] All credentials are correct
- [ ] Bots respond on Telegram
- [ ] Demo bot shows amenities
- [ ] Onboarding bot shows setup wizard
- [ ] Logs show no errors
- [ ] Rate limiting is working
- [ ] Database is created
- [ ] Escalation system is active
- [ ] Bilingual support is working
- [ ] Monitoring is set up

## Cost Analysis

| Component | Cost | Notes |
|-----------|------|-------|
| Railway Free Tier | $0 | Includes $5 credit |
| Railway Paid | $5/month | After credit expires |
| Telegram Bot API | $0 | Free |
| Groq API | $0 | Free tier included |
| OpenWeather API | $0 | Free tier included |
| **Total** | **$0-5/month** | Very affordable |

## Scaling

### Upgrade Plan

```bash
# View current plan
railway status

# Upgrade to paid tier
# Go to https://railway.app and upgrade
```

### Handle More Users

- Paid tier supports 100+ concurrent users
- Database automatically scales
- Rate limiting prevents abuse
- Logs help identify bottlenecks

## Maintenance

### Regular Tasks

- [ ] Check logs weekly
- [ ] Monitor API quotas
- [ ] Update dependencies monthly
- [ ] Review escalations
- [ ] Backup database

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Backup Database

```bash
# Download database
railway run python -c "import shutil; shutil.copy('leah_bots.db', 'backup.db')"
```

## Support

- **Railway Docs:** https://docs.railway.app
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Groq API:** https://console.groq.com
- **OpenWeather:** https://openweathermap.org/api

## Next Steps

1. ✅ Deploy bots to Railway
2. ✅ Test both bots on Telegram
3. ✅ Monitor logs for 24 hours
4. ✅ Set up escalation alerts
5. ✅ Prepare for customer onboarding
6. ✅ Create marketing materials
7. ✅ Launch to production

---

**Your LEAH bots are now production-ready!** 🚀
