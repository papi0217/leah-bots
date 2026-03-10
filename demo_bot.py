#!/usr/bin/env python3
"""
LEAH Demo Bot — Guest Experience Simulation & Sales Conversion
Demonstrates LEAH concierge capabilities to potential hosts
Includes sales trigger and seamless onboarding transition
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from groq import Groq

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - DEMO_BOT: %(message)s',
    handlers=[
        logging.FileHandler('demo_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DEMO_BOT_TOKEN = os.getenv('DEMO_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
OWNER_TELEGRAM_ID = int(os.getenv('OWNER_TELEGRAM_ID', '0'))
ONBOARDING_BOT_HANDLE = os.getenv('ONBOARDING_BOT_HANDLE', '@Leah_onboarding_bot')

if not all([DEMO_BOT_TOKEN, GROQ_API_KEY, OWNER_TELEGRAM_ID]):
    logger.error("❌ Missing required environment variables")
    exit(1)

groq_client = Groq(api_key=GROQ_API_KEY)

# ============================================================================
# DEMO BOT CONFIGURATION (LOCKED)
# ============================================================================

DEMO_BOT_CONFIG = {
    'name': 'LEAH Luxury Experience Assistant Host',
    'handle': '@leah_luxury_host_demo_bot',
    'purpose': 'Demonstrate LEAH concierge to potential hosts',
    'system_prompt': """You are LEAH, a luxury property concierge assistant demonstrating your capabilities to a potential host.

The person you're talking to is a property owner/manager who is ROLEPLAYING AS A GUEST to experience what their guests would experience.

Your role:
- Respond as if the user is a real guest staying at a luxury property
- Demonstrate exceptional hospitality and service
- Answer questions about property amenities, services, local recommendations
- Handle requests with professionalism and warmth
- Show why hosts should use LEAH for their properties

CRITICAL: You are demonstrating to a HOST, not actually serving a guest. Your responses should:
1. Be exceptionally professional and polished
2. Show the VALUE of having LEAH handle guest requests
3. Demonstrate how LEAH reduces host workload
4. Show guest satisfaction improvements

Tone: Sophisticated, warm, helpful, professional luxury hospitality

CAPABILITIES TO DEMONSTRATE:
✓ Property information and amenities
✓ Check-in/checkout assistance
✓ Restaurant recommendations
✓ Activity and entertainment suggestions
✓ Local recommendations
✓ Emergency support
✓ House rules and policies
✓ Appliance and facility help
✓ Booking assistance
✓ 24/7 availability

EXAMPLE INTERACTIONS:
Guest: "What's the Wi-Fi password?"
LEAH: "Of course! The Wi-Fi network is 'Villa Paradiso' and the password is 'LuxuryStay2024'. You should connect automatically. If you have any trouble, please let me know."

Guest: "I'd like restaurant recommendations"
LEAH: "I'd be delighted to suggest some exceptional dining options. Are you looking for fine dining, casual, specific cuisine, or something particular to your preferences?"

Guest: "There's an issue with the hot water"
LEAH: "I sincerely apologize for the inconvenience. Let me help immediately. Have you checked if the water heater switch is on? It's located in the utility closet. If that doesn't resolve it, I can arrange for our maintenance team to visit within the hour."

Remember: Every response demonstrates why hosts should use LEAH."""
}

# ============================================================================
# DEMO FLOW STATES
# ============================================================================

DEMO_INTRO = 0
DEMO_CONFIRMATION = 1
DEMO_ACTIVE = 2
DEMO_SALES_MODE = 3

# ============================================================================
# DEMO BOT HANDLERS
# ============================================================================

async def demo_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start demo with introduction"""
    
    user_id = update.effective_user.id
    
    # Initialize user state
    if 'demo_state' not in context.user_data:
        context.user_data['demo_state'] = DEMO_INTRO
        context.user_data['message_count'] = 0
        context.user_data['sales_trigger_shown'] = False
        context.user_data['conversation_history'] = []
    
    message = """✨ **Welcome to LEAH Luxury Concierge Demo** ✨

I'm LEAH — the AI concierge that transforms guest experiences and reduces your workload.

**What you're about to see:**
This is a live demonstration of how LEAH responds to guest requests. You'll roleplay as a guest staying at a luxury property, and I'll show you exactly how I handle every type of request — from check-in questions to restaurant recommendations to emergencies.

**Why this matters:**
Every response you see demonstrates how LEAH:
✓ Handles guest requests 24/7
✓ Reduces your response time from hours to seconds
✓ Improves guest satisfaction
✓ Manages your property intelligently
✓ Handles edge cases gracefully

**Ready to experience what your guests will experience?**

Simply type "OK", "I understand", "start demo", or anything similar to begin. Ask me anything a guest might ask — check-in questions, Wi-Fi passwords, restaurant recommendations, local attractions, emergencies, or anything else.

I'm here to impress you. Let's begin."""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    context.user_data['demo_state'] = DEMO_CONFIRMATION
    logger.info(f"Demo Bot: User {user_id} started — awaiting confirmation")
    
    return DEMO_CONFIRMATION

async def demo_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Wait for demo confirmation"""
    
    user_message = update.message.text.lower()
    user_id = update.effective_user.id
    
    # Check for confirmation keywords
    confirmation_keywords = ['ok', 'start', 'begin', 'yes', 'ready', 'understand', 'demo', 'go', 'let\'s', 'confirm']
    
    if any(keyword in user_message for keyword in confirmation_keywords):
        # Reset conversation history and enter demo mode
        context.user_data['conversation_history'] = []
        context.user_data['message_count'] = 0
        context.user_data['demo_state'] = DEMO_ACTIVE
        
        welcome = """🎭 **DEMO MODE ACTIVE** 🎭

You are now a guest at Villa Paradiso, a luxury 8-bedroom oceanfront villa.

**Property Details:**
🏰 Villa Paradiso — Luxury oceanfront villa
👥 Sleeps 8 guests
🏊 Amenities: Pool, spa, wine cellar, beach access, gourmet kitchen
📍 Location: Mediterranean coast
🌙 Check-in: 4 PM | Check-out: 11 AM

Ask me anything a guest might ask. I'm here to provide exceptional service.

What can I help you with?"""
        
        await update.message.reply_text(welcome, parse_mode="Markdown")
        logger.info(f"Demo Bot: Demo mode activated for user {user_id}")
        return DEMO_ACTIVE
    else:
        # Clarify
        clarification = "I'm ready to start the demo whenever you are! Just say 'OK' or 'start demo' and we'll begin. 😊"
        await update.message.reply_text(clarification)
        return DEMO_CONFIRMATION

async def demo_active_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle messages during active demo"""
    
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Demo Bot: Message from {user_id}: {user_message}")
    
    # Increment message count
    context.user_data['message_count'] += 1
    
    # Check for sales trigger keywords
    sales_keywords = ['pricing', 'cost', 'setup', 'trial', 'how to get', 'features', 'automation', 'how does it work', 'how much', 'sign up', 'buy', 'purchase', 'host', 'for me', 'my property']
    
    if any(keyword in user_message.lower() for keyword in sales_keywords):
        # Switch to sales mode
        context.user_data['demo_state'] = DEMO_SALES_MODE
        return await demo_sales_mode(update, context)
    
    # Show sales trigger after 5 messages
    if context.user_data['message_count'] == 5 and not context.user_data['sales_trigger_shown']:
        context.user_data['sales_trigger_shown'] = True
        
        # Add trigger message after response
        trigger_message = """💡 **Quick Note:**
If at any moment you'd like to stop the demo and learn how LEAH works for hosts, simply ask about pricing, setup, or features, and I'll explain the system. Otherwise, feel free to continue testing my capabilities!"""
        
        # Will be sent after main response
        context.user_data['pending_trigger'] = trigger_message
    
    # Add to conversation history
    context.user_data['conversation_history'].append({"role": "user", "content": user_message})
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    # Generate response with Groq
    try:
        messages = [
            {"role": "system", "content": DEMO_BOT_CONFIG['system_prompt']}
        ]
        
        # Add conversation history (last 10 messages)
        for msg in context.user_data['conversation_history'][-10:]:
            messages.append(msg)
        
        logger.info(f"Demo Bot: Generating response for {user_id}...")
        
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            temperature=0.8,
            max_tokens=500,
            top_p=0.9,
        )
        
        generated_response = response.choices[0].message.content.strip()
        
        if not generated_response or len(generated_response) < 20:
            generated_response = "I apologize for the difficulty. Could you please rephrase your request? I'm here to assist with any guest needs."
            logger.warning(f"Demo Bot: Response validation failed for {user_id}")
        
        # Add response to history
        context.user_data['conversation_history'].append({"role": "assistant", "content": generated_response})
        
        # Send response
        await update.message.reply_text(generated_response)
        logger.info(f"Demo Bot: Response sent to {user_id}")
        
        # Send pending trigger if exists
        if 'pending_trigger' in context.user_data:
            await asyncio.sleep(1)
            await update.message.reply_text(context.user_data['pending_trigger'], parse_mode="Markdown")
            del context.user_data['pending_trigger']
        
        return DEMO_ACTIVE
        
    except Exception as e:
        logger.error(f"Demo Bot: Groq API error for {user_id}: {str(e)}")
        error_response = "I apologize, but I'm experiencing a temporary issue. Please try again in a moment."
        await update.message.reply_text(error_response)
        return DEMO_ACTIVE

async def demo_sales_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Switch to sales explanation mode"""
    
    user_id = update.effective_user.id
    
    sales_message = """🎯 **LEAH for Hosts — How It Works**

You've just experienced what your guests experience. Now let me explain what LEAH does for you.

**The Problem You're Solving:**
✗ Guests message at all hours
✗ Repetitive questions (Wi-Fi, check-in, rules)
✗ Delayed responses hurt satisfaction
✗ You're managing communication instead of your property

**The LEAH Solution:**
✓ 24/7 AI concierge handles guest requests instantly
✓ Learns your property details and local recommendations
✓ Responds in seconds, not hours
✓ Handles 95% of guest questions automatically
✓ You only see escalations that need human attention

**What LEAH Handles:**
• Check-in/checkout assistance
• Property questions and amenities
• Wi-Fi, parking, appliances
• Restaurant and activity recommendations
• Local information
• Emergency support
• House rules clarification
• Booking assistance

**The Result:**
📈 Higher guest satisfaction (5-star reviews)
⏰ 90% less time managing messages
💰 Reduced cancellations and complaints
🎯 More time growing your business

**Membership Options:**

🏆 **Essential** — $100 enrollment + $50/month
   • Up to 3 properties
   • Basic concierge
   • Guest support

🌟 **Premium** — $300 enrollment + $150/month
   • Up to 10 properties
   • Enhanced concierge
   • Priority support
   • Dedicated manager

💎 **Enterprise** — Custom pricing
   • Unlimited properties
   • White-label solution
   • 24/7 premium support

**Ready to Get Started?**

I can connect you to our onboarding assistant who will set up a customized LEAH for your property in 5-10 minutes.

Would you like to begin your trial onboarding?"""
    
    await update.message.reply_text(sales_message, parse_mode="Markdown")
    
    # Offer onboarding transition
    keyboard = [
        [InlineKeyboardButton("Start Trial Onboarding", callback_data="start_onboarding")],
        [InlineKeyboardButton("Ask More Questions", callback_data="continue_demo")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    transition_message = f"""**Next Step:**

Option 1: Start your trial onboarding with our assistant
Option 2: Continue asking me questions about LEAH

Which would you prefer?"""
    
    await update.message.reply_text(transition_message, reply_markup=reply_markup)
    context.user_data['demo_state'] = DEMO_SALES_MODE
    logger.info(f"Demo Bot: Entered sales mode for user {user_id}")
    
    return DEMO_SALES_MODE

async def demo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle callback button clicks"""
    
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_onboarding":
        onboarding_message = f"""🎉 **Welcome to LEAH Onboarding!**

I'm connecting you to our onboarding assistant who will:

1. Gather your property details
2. Configure your guest responses
3. Set up your custom LEAH instance
4. Generate your guest concierge link

**Start your trial now:**

Contact our onboarding assistant: {ONBOARDING_BOT_HANDLE}

Simply message them and say "I'm ready to onboard" and they'll guide you through the entire process.

The setup takes 5-10 minutes and you'll have a fully functional LEAH concierge for your property.

Looking forward to serving your guests! 🎯"""
        
        await query.edit_message_text(onboarding_message, parse_mode="Markdown")
        logger.info(f"Demo Bot: Onboarding transition for user {query.from_user.id}")
        
    elif query.data == "continue_demo":
        continue_message = """Great! Feel free to ask me more questions about:

• How LEAH learns your property
• Integration with your booking system
• Response customization
• Guest satisfaction improvements
• Pricing and billing
• Technical requirements
• Or continue the guest experience demo

What would you like to know?"""
        
        await query.edit_message_text(continue_message)
        context.user_data['demo_state'] = DEMO_ACTIVE
        return DEMO_ACTIVE

async def demo_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    
    help_text = """📚 **Demo Bot Help**

**Commands:**
/start — Begin the demo
/help — Show this message
/admin_status — View bot status (admin only)

**During Demo:**
• Roleplay as a guest at Villa Paradiso
• Ask anything a guest might ask
• Experience LEAH's capabilities
• After 5 messages, you'll see a sales trigger
• Ask about pricing/setup to enter sales mode

**Transition to Onboarding:**
Once you're impressed, you can transition to our onboarding assistant to set up your custom LEAH.

This demo shows exactly what your guests will experience."""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")
    logger.info(f"Demo Bot: Help shown to {update.effective_user.id}")

async def demo_admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin status command"""
    
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ Unauthorized")
        return
    
    status = f"""🤖 **LEAH Demo Bot — Status**

✅ **Status:** Running
🏷️ **Name:** {DEMO_BOT_CONFIG['name']}
📱 **Handle:** {DEMO_BOT_CONFIG['handle']}
🎯 **Purpose:** {DEMO_BOT_CONFIG['purpose']}

🛡️ **Features:**
• Guest experience simulation
• Sales trigger system
• Onboarding transition
• Robust input handling
• Groq AI integration

📊 **Capabilities:**
• Property information
• Restaurant recommendations
• Activity suggestions
• Guest support
• Emergency handling

⏰ **Timestamp:** {datetime.now().isoformat()}"""
    
    await update.message.reply_text(status, parse_mode="Markdown")
    logger.info(f"Demo Bot: Admin status requested by {update.effective_user.id}")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

async def main_demo_bot() -> None:
    """Start Demo Bot"""
    
    logger.info("=" * 70)
    logger.info("🚀 LEAH DEMO BOT — STARTING")
    logger.info("=" * 70)
    
    app = Application.builder().token(DEMO_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", demo_start))
    app.add_handler(CommandHandler("help", demo_help))
    app.add_handler(CommandHandler("admin_status", demo_admin_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, demo_confirmation), group=1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, demo_active_message), group=2)
    
    logger.info("✅ Demo Bot initialized")
    logger.info(f"📱 Handle: {DEMO_BOT_CONFIG['handle']}")
    logger.info("=" * 70)
    
    async with app:
        await app.initialize()
        await app.start()
        logger.info("✅ Demo Bot started successfully")
        
        # Keep running
        await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main_demo_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Demo Bot shutting down...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
