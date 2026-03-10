#!/bin/bash

# LEAH Bots - Secure Automated Deployment Script
# This script deploys LEAH bots to Railway securely without storing credentials

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print with color
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        echo "Install from: https://nodejs.org"
        exit 1
    fi
    print_success "Node.js found: $(node --version)"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi
    print_success "npm found: $(npm --version)"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    print_success "Git found: $(git --version)"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 found: $(python3 --version)"
}

# Install Railway CLI
install_railway_cli() {
    print_header "Installing Railway CLI"
    
    if command -v railway &> /dev/null; then
        print_success "Railway CLI already installed: $(railway --version)"
        return
    fi
    
    print_info "Installing @railway/cli globally..."
    npm install -g @railway/cli
    print_success "Railway CLI installed"
}

# Login to Railway
login_railway() {
    print_header "Railway Authentication"
    
    if railway whoami &> /dev/null; then
        print_success "Already logged in to Railway"
        return
    fi
    
    print_info "Opening Railway login in browser..."
    print_info "Please sign in with your GitHub account"
    railway login
    
    if railway whoami &> /dev/null; then
        print_success "Successfully logged in to Railway"
    else
        print_error "Failed to login to Railway"
        exit 1
    fi
}

# Get credentials
get_credentials() {
    print_header "Enter Your Credentials"
    
    print_info "You need 5 credentials. Get them from:"
    echo "  1. Demo Bot Token: @BotFather on Telegram"
    echo "  2. Onboarding Bot Token: @BotFather on Telegram"
    echo "  3. Groq API Key: https://console.groq.com"
    echo "  4. Weather API Key: https://openweathermap.org/api"
    echo "  5. Your Telegram ID: @userinfobot on Telegram"
    echo ""
    
    # Demo Bot Token
    read -p "Enter Demo Bot Token: " DEMO_BOT_TOKEN
    if [ -z "$DEMO_BOT_TOKEN" ]; then
        print_error "Demo Bot Token cannot be empty"
        exit 1
    fi
    
    # Onboarding Bot Token
    read -p "Enter Onboarding Bot Token: " ONBOARDING_BOT_TOKEN
    if [ -z "$ONBOARDING_BOT_TOKEN" ]; then
        print_error "Onboarding Bot Token cannot be empty"
        exit 1
    fi
    
    # Groq API Key
    read -p "Enter Groq API Key: " GROQ_API_KEY
    if [ -z "$GROQ_API_KEY" ]; then
        print_error "Groq API Key cannot be empty"
        exit 1
    fi
    
    # Weather API Key
    read -p "Enter Weather API Key: " WEATHER_API_KEY
    if [ -z "$WEATHER_API_KEY" ]; then
        print_error "Weather API Key cannot be empty"
        exit 1
    fi
    
    # Telegram ID
    read -p "Enter Your Telegram ID: " OWNER_TELEGRAM_ID
    if [ -z "$OWNER_TELEGRAM_ID" ]; then
        print_error "Telegram ID cannot be empty"
        exit 1
    fi
    
    print_success "All credentials received"
}

# Initialize Railway project
init_railway_project() {
    print_header "Initializing Railway Project"
    
    if [ -f ".railway/config.json" ]; then
        print_success "Railway project already initialized"
        return
    fi
    
    print_info "Creating new Railway project..."
    railway init --name leah-bots
    print_success "Railway project initialized"
}

# Set environment variables
set_environment_variables() {
    print_header "Setting Environment Variables"
    
    print_info "Configuring environment variables..."
    
    railway variables set \
        DEMO_BOT_TOKEN="$DEMO_BOT_TOKEN" \
        ONBOARDING_BOT_TOKEN="$ONBOARDING_BOT_TOKEN" \
        GROQ_API_KEY="$GROQ_API_KEY" \
        WEATHER_API_KEY="$WEATHER_API_KEY" \
        OWNER_TELEGRAM_ID="$OWNER_TELEGRAM_ID" \
        RENDER=true \
        LOG_LEVEL=INFO
    
    print_success "Environment variables configured"
}

# Deploy to Railway
deploy_to_railway() {
    print_header "Deploying to Railway"
    
    print_info "Building and deploying bots (this takes 10-15 minutes)..."
    print_warning "Do not close this terminal"
    
    railway up
    
    print_success "Deployment complete"
}

# Verify deployment
verify_deployment() {
    print_header "Verifying Deployment"
    
    print_info "Checking deployment status..."
    railway status
    
    print_info "Showing recent logs (press Ctrl+C to stop)..."
    print_warning "Look for: '✅ Demo bot started' and '✅ Onboarding bot started'"
    
    railway logs -f --tail 20
}

# Main deployment flow
main() {
    print_header "LEAH BOTS - AUTOMATED RAILWAY DEPLOYMENT"
    
    echo ""
    print_info "This script will deploy LEAH bots to Railway securely"
    echo ""
    
    # Step 1: Check prerequisites
    check_prerequisites
    
    # Step 2: Install Railway CLI
    install_railway_cli
    
    # Step 3: Login to Railway
    login_railway
    
    # Step 4: Get credentials
    get_credentials
    
    # Step 5: Initialize Railway project
    init_railway_project
    
    # Step 6: Set environment variables
    set_environment_variables
    
    # Step 7: Deploy
    deploy_to_railway
    
    # Step 8: Verify
    verify_deployment
    
    print_header "DEPLOYMENT COMPLETE ✅"
    echo ""
    print_success "Your LEAH bots are now live on Railway!"
    echo ""
    print_info "Test your bots on Telegram:"
    echo "  1. Demo Bot: @leah_luxury_host_demo_bot"
    echo "  2. Onboarding Bot: @Leah_onboarding_bot"
    echo ""
    print_info "Monitor your deployment:"
    echo "  railway logs -f"
    echo ""
    print_info "View project status:"
    echo "  railway status"
    echo ""
}

# Run main function
main
