# Quick Deploy - One Command Deployment

**Deploy LEAH bots to Railway in one command with full automation.**

## Prerequisites

- Node.js 18+ installed
- GitHub account
- Telegram account
- 5 credentials ready (see below)

## Get Your Credentials (5 minutes)

Before deploying, gather these:

### 1. Demo Bot Token
- Go to Telegram
- Search: `@BotFather`
- Send: `/newbot`
- Name it: `leah_luxury_host_demo_bot`
- Copy the token (looks like: `8633547753:AAEElVx4U7O5b3yu7AlK9BrYm7RbQoxDKt8`)

### 2. Onboarding Bot Token
- Same process as above
- Name it: `Leah_onboarding_bot`
- Copy the token

### 3. Groq API Key
- Go to: https://console.groq.com
- Sign up (free)
- Create API key
- Copy it

### 4. Weather API Key
- Go to: https://openweathermap.org/api
- Sign up (free)
- Create API key
- Copy it

### 5. Your Telegram ID
- Go to Telegram
- Search: `@userinfobot`
- Send: `/start`
- Copy your User ID

## Deploy (One Command)

### On Mac/Linux:

```bash
git clone https://github.com/papi0217/leah-bots.git
cd leah-bots
bash deploy.sh
```

### On Windows:

```bash
git clone https://github.com/papi0217/leah-bots.git
cd leah-bots
bash deploy.sh
```

Or use Git Bash / WSL.

## What Happens

The script will:

1. ✅ Check prerequisites (Node.js, npm, Git, Python)
2. ✅ Install Railway CLI
3. ✅ Login to Railway (browser opens)
4. ✅ Prompt you for 5 credentials
5. ✅ Initialize Railway project
6. ✅ Set environment variables
7. ✅ Deploy to Railway (10-15 minutes)
8. ✅ Verify deployment and show logs

## During Deployment

- **Don't close the terminal**
- **Don't interrupt the process**
- **Wait for "DEPLOYMENT COMPLETE ✅"**

## After Deployment

### Test Your Bots

1. Open Telegram
2. Search: `@leah_luxury_host_demo_bot`
3. Send: `/start`
4. Bot should respond

Repeat for: `@Leah_onboarding_bot`

### Monitor Deployment

```bash
railway logs -f
```

### Check Status

```bash
railway status
```

## Troubleshooting

### "Cannot login in non-interactive mode"

```bash
railway login
bash deploy.sh
```

### "Node.js not found"

Install from: https://nodejs.org

### "Deployment failed"

Check logs:
```bash
railway logs -f | grep -i error
```

### "Bot not responding"

1. Verify bot token is correct
2. Check logs for errors
3. Restart: `railway up --force`

## Cost

- Free tier: $0 (includes $5 credit)
- Paid tier: $5/month after credit

## That's It! 🎉

Your LEAH bots are now live on Railway, handling real guests and hosts 24/7.

---

**Questions?** See `DEPLOYMENT.md` for detailed guide.
