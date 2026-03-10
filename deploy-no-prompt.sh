#!/bin/bash

# LEAH BOTS - Non-Interactive Railway Deployment
# This script deploys LEAH bots without any prompts or browser interaction

set -e

echo "═══════════════════════════════════════════════════════════"
echo "LEAH BOTS - AUTOMATED RAILWAY DEPLOYMENT (NO PROMPTS)"
echo "═══════════════════════════════════════════════════════════"

# Check prerequisites
echo ""
echo "Checking Prerequisites..."
echo "═══════════════════════════════════════════════════════════"

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js first."
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm first."
    exit 1
fi
echo "✅ npm found: $(npm --version)"

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git first."
    exit 1
fi
echo "✅ Git found: $(git --version)"

# Install Railway CLI if not present
echo ""
echo "Installing/Updating Railway CLI..."
echo "═══════════════════════════════════════════════════════════"
npm install -g @railway/cli > /dev/null 2>&1 || true
echo "✅ Railway CLI ready: $(railway --version)"

# Check for .env file
echo ""
echo "Checking Environment Variables..."
echo "═══════════════════════════════════════════════════════════"

if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo ""
    echo "Please create a .env file with the following variables:"
    echo "DEMO_BOT_TOKEN=your_token_here"
    echo "ONBOARDING_BOT_TOKEN=your_token_here"
    echo "GROQ_API_KEY=your_key_here"
    echo "WEATHER_API_KEY=your_key_here"
    echo "OWNER_TELEGRAM_ID=your_id_here"
    echo "RENDER=true"
    echo "LOG_LEVEL=INFO"
    echo ""
    exit 1
fi

# Load environment variables
source .env

# Validate required variables
if [ -z "$DEMO_BOT_TOKEN" ] || [ -z "$ONBOARDING_BOT_TOKEN" ] || [ -z "$GROQ_API_KEY" ] || [ -z "$WEATHER_API_KEY" ] || [ -z "$OWNER_TELEGRAM_ID" ]; then
    echo "❌ Missing required environment variables in .env file!"
    echo ""
    echo "Required variables:"
    echo "  - DEMO_BOT_TOKEN"
    echo "  - ONBOARDING_BOT_TOKEN"
    echo "  - GROQ_API_KEY"
    echo "  - WEATHER_API_KEY"
    echo "  - OWNER_TELEGRAM_ID"
    echo ""
    exit 1
fi

echo "✅ All required environment variables found"

# Check for Railway token
echo ""
echo "Checking Railway Authentication..."
echo "═══════════════════════════════════════════════════════════"

if [ -z "$RAILWAY_TOKEN" ]; then
    echo "⚠️  RAILWAY_TOKEN not set in environment"
    echo ""
    echo "To deploy, you need to:"
    echo "1. Get your Railway token from: https://railway.app/account/tokens"
    echo "2. Set it as an environment variable:"
    echo "   export RAILWAY_TOKEN=your_token_here"
    echo ""
    echo "Then run this script again:"
    echo "   bash deploy-no-prompt.sh"
    echo ""
    exit 1
fi

echo "✅ Railway token found"

# Initialize Railway project
echo ""
echo "Initializing Railway Project..."
echo "═══════════════════════════════════════════════════════════"

# Create or use existing project
if [ ! -f ".railway/config.json" ]; then
    echo "Creating new Railway project..."
    railway init --no-prompt > /dev/null 2>&1 || true
    echo "✅ Railway project initialized"
else
    echo "✅ Using existing Railway project"
fi

# Set environment variables
echo ""
echo "Setting Environment Variables..."
echo "═══════════════════════════════════════════════════════════"

railway variables set \
    DEMO_BOT_TOKEN="$DEMO_BOT_TOKEN" \
    ONBOARDING_BOT_TOKEN="$ONBOARDING_BOT_TOKEN" \
    GROQ_API_KEY="$GROQ_API_KEY" \
    WEATHER_API_KEY="$WEATHER_API_KEY" \
    OWNER_TELEGRAM_ID="$OWNER_TELEGRAM_ID" \
    RENDER=true \
    LOG_LEVEL=INFO > /dev/null 2>&1

echo "✅ Environment variables set"

# Deploy to Railway
echo ""
echo "Deploying to Railway..."
echo "═══════════════════════════════════════════════════════════"
echo "This may take 5-10 minutes..."
echo ""

railway up --no-prompt

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Your LEAH bots are now deployed to Railway!"
echo ""
echo "Test on Telegram:"
echo "  Demo Bot: @leah_luxury_host_demo_bot"
echo "  Onboarding Bot: @Leah_onboarding_bot"
echo ""
echo "View logs:"
echo "  railway logs -f"
echo ""
echo "View project:"
echo "  railway open"
echo ""
