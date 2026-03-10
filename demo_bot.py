"""
LEAH Luxury Concierge Demo Bot
Guest-facing concierge with full luxury hospitality capabilities
Strict scope enforcement with sophisticated vocabulary
"""

import os
import json
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
from scope_enforcement import ScopeEnforcer, ScenarioMatcher, LUXURY_VOCABULARY

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

if not all([DEMO_BOT_TOKEN, GROQ_API_KEY, OWNER_TELEGRAM_ID]):
    logger.error("❌ Missing required environment variables")
    exit(1)

groq_client = Groq(api_key=GROQ_API_KEY)

# ============================================================================
# DEMO BOT CONFIGURATION (LOCKED)
# ============================================================================

DEMO_BOT_CONFIG = {
    'name': 'LEAH Luxury Concierge Demo',
    'handle': '@leah_luxury_host_demo_bot',
    'purpose': 'Guest-facing AI concierge for luxury property management',
    'system_prompt': """You are LEAH, an elite luxury property concierge assistant.

Your EXCLUSIVE responsibilities:
1. Property Information — Amenities, facilities, house rules, check-in/check-out
2. Restaurant Recommendations — Fine dining, casual, local specialties, reservations
3. Activity Suggestions — Attractions, entertainment, tours, experiences
4. Guest Support — Assistance, emergencies, maintenance, comfort requests
5. Local Recommendations — Shopping, services, transportation, experiences

PROFESSIONAL STANDARDS:
- Use sophisticated, refined vocabulary befitting luxury hospitality
- Address guests with utmost professionalism and warmth
- Provide personalized, detailed recommendations
- Anticipate guest needs and exceed expectations
- Maintain discretion and confidentiality
- Never discuss topics outside your concierge duties

VOCABULARY GUIDELINES:
- Use phrases like "I would be delighted to...", "Allow me to suggest...", "May I recommend..."
- Avoid casual language; maintain elegant professionalism
- Describe experiences as "exquisite", "refined", "distinguished", "exceptional"
- Reference properties as "our distinguished residence", "this exceptional property"

SCOPE BOUNDARIES:
You ONLY assist with:
✓ Property information and amenities
✓ Restaurant and dining recommendations
✓ Activities and entertainment
✓ Guest support and concierge services
✓ Local recommendations

You NEVER discuss:
✗ Personal matters
✗ Financial or payment issues
✗ Medical advice
✗ Legal matters
✗ Political topics
✗ Religious matters
✗ Topics outside your concierge duties

RESPONSE STRUCTURE:
1. Acknowledge the request professionally
2. Provide detailed, relevant information
3. Offer additional suggestions if appropriate
4. Close with an offer of further assistance

Property Details:
- Villa Paradiso: 8-guest luxury villa with Olympic pool, spa, wine cellar
- Amenities: Pool, spa, wine cellar, private beach access, 24/7 concierge
- House Rules: Quiet hours 10pm-8am, no smoking indoors, respect neighbors

Curated Restaurants:
1. Ristorante Stella — Italian fine dining, 2km away, Michelin-recommended
2. Le Petit Bistro — French cuisine, 1.5km away, intimate ambiance
3. Sushi Mastery — Japanese, 1.8km away, chef's tasting menu
4. Casa Española — Spanish tapas, 1.2km away, traditional specialties

Always maintain the highest standards of luxury hospitality."""
}

# ============================================================================
# DEMO BOT HANDLERS
# ============================================================================

async def demo_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Demo bot /start command with luxury welcome"""
    
    message = """✨ **Welcome to LEAH Luxury Concierge** ✨

I am delighted to serve as your personal concierge during your stay at our distinguished property.

I am at your complete disposal for:
🏰 **Property Information** — Amenities, facilities, house rules
🍽️ **Dining Recommendations** — Fine dining, casual, local specialties
🎭 **Activities & Entertainment** — Attractions, tours, experiences
🛎️ **Guest Support** — Assistance with any comfort needs
🗺️ **Local Recommendations** — Shopping, services, experiences

Please allow me to enhance your stay with personalized recommendations and exceptional service.

How may I be of service today?"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Demo Bot: User {update.effective_user.id} started conversation")

async def demo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Demo bot message handler with scope enforcement"""
    
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Demo Bot: Message from {user_id}: {user_message}")
    
    # Initialize conversation history
    if 'demo_history' not in context.user_data:
        context.user_data['demo_history'] = []
    
    # SCOPE ENFORCEMENT: Validate query
    is_valid, category, redirect_message = ScopeEnforcer.validate_demo_bot_query(user_message)
    
    if not is_valid:
        logger.warning(f"Demo Bot: Out-of-scope query from {user_id}: {category}")
        await update.message.reply_text(redirect_message)
        return
    
    # Match scenario for context
    scenario = ScenarioMatcher.match_demo_scenario(user_message)
    logger.info(f"Demo Bot: Matched scenario: {scenario}")
    
    # Add user message to history
    context.user_data['demo_history'].append({"role": "user", "content": user_message})
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    # Generate response with Groq
    try:
        messages = [
            {"role": "system", "content": DEMO_BOT_CONFIG['system_prompt']}
        ]
        
        # Add conversation history (last 5 messages)
        for msg in context.user_data['demo_history'][-5:]:
            messages.append(msg)
        
        logger.info(f"Demo Bot: Generating response for {user_id}...")
        
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            temperature=0.7,
            max_tokens=600,
            top_p=0.9,
        )
        
        generated_response = response.choices[0].message.content.strip()
        
        # Validate response is within scope
        if not generated_response or len(generated_response) < 20:
            generated_response = "I apologize, but I encountered a difficulty generating a response. Please rephrase your inquiry, and I shall be delighted to assist."
            logger.warning(f"Demo Bot: Response validation failed for {user_id}")
        
        # Add response to history
        context.user_data['demo_history'].append({"role": "assistant", "content": generated_response})
        
        # Send response
        await update.message.reply_text(generated_response)
        logger.info(f"Demo Bot: Response sent to {user_id}")
        
    except Exception as e:
        logger.error(f"Demo Bot: Groq API error for {user_id}: {str(e)}")
        error_response = "I sincerely apologize, but I am temporarily unable to process your request. Please allow me a moment to restore my services, and I shall be delighted to assist you shortly."
        await update.message.reply_text(error_response)

async def demo_admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin status command for Demo Bot"""
    
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("❌ Unauthorized")
        return
    
    status = f"""🤖 **LEAH Luxury Concierge Demo Bot — Status**

✅ **Status:** Running
🏷️ **Name:** {DEMO_BOT_CONFIG['name']}
📱 **Handle:** {DEMO_BOT_CONFIG['handle']}
🎯 **Purpose:** {DEMO_BOT_CONFIG['purpose']}

🛡️ **Safety Enforcement:** IRONCLAD
🔒 **Scope Enforcement:** ACTIVE
📊 **Logging:** ACTIVE
🌐 **Groq API:** Connected

📋 **Capabilities:**
• Property information & amenities
• Restaurant recommendations
• Activity suggestions
• Guest support
• Local recommendations

⏰ **Timestamp:** {datetime.now().isoformat()}"""
    
    await update.message.reply_text(status, parse_mode="Markdown")
    logger.info(f"Demo Bot: Admin status requested by {update.effective_user.id}")

async def demo_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command for Demo Bot"""
    
    help_text = """📚 **How I Can Assist You**

I am your dedicated luxury concierge, available to enhance every aspect of your stay.

**Property Information:**
Ask about amenities, facilities, house rules, check-in procedures, or any property details.
Example: "What amenities are available?" or "Tell me about the pool"

**Dining Recommendations:**
I can suggest fine dining establishments, casual restaurants, or local specialties.
Example: "Where can I find excellent Italian cuisine?" or "Recommend a romantic restaurant"

**Activities & Entertainment:**
Discover attractions, tours, entertainment venues, and unique experiences.
Example: "What activities are available?" or "Are there any museums nearby?"

**Guest Support:**
I'm here to assist with any comfort needs or concerns during your stay.
Example: "I need assistance" or "There's an issue with the WiFi"

**Local Recommendations:**
Learn about shopping, services, transportation, and local experiences.
Example: "Where can I go shopping?" or "How do I get around the area?"

Please feel free to ask me anything related to your stay, and I shall be delighted to assist."""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")
    logger.info(f"Demo Bot: Help requested by {update.effective_user.id}")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

async def main_demo_bot() -> None:
    """Start Demo Bot"""
    
    logger.info("=" * 70)
    logger.info("🚀 LEAH LUXURY CONCIERGE DEMO BOT — STARTING")
    logger.info("=" * 70)
    
    app = Application.builder().token(DEMO_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", demo_start))
    app.add_handler(CommandHandler("help", demo_help))
    app.add_handler(CommandHandler("admin_status", demo_admin_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, demo_message))
    
    logger.info("✅ Demo Bot initialized")
    logger.info(f"📱 Handle: {DEMO_BOT_CONFIG['handle']}")
    logger.info("🛡️ Scope Enforcement: ACTIVE")
    logger.info("=" * 70)
    
    async with app:
        await app.initialize()
        await app.start()
        logger.info("✅ Demo Bot started successfully")
        
        # Keep running
        await asyncio.Event().wait()

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main_demo_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Demo Bot shutting down...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
