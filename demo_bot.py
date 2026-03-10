#!/usr/bin/env python3
"""
LEAH Demo Bot — World-Class High-Conversion Sales Experience
Telegram Bot for converting property managers into paying customers
through an immersive, guided, emotionally intelligent guest experience.

Implements high-conversion principles:
- Guided experience with suggested questions
- Value-reinforcing commentary after each response
- Theatrical reveal and pivot moment
- Personalized pitch based on qualification
- Seamless handoff to onboarding

Author: Manus AI
Version: 4.0 (World-Class)
"""

import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from enum import Enum
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes
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
# CONSTANTS & CONFIGURATION
# ============================================================================

DEMO_BOT_TOKEN = os.getenv('DEMO_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
OWNER_TELEGRAM_ID = int(os.getenv('OWNER_TELEGRAM_ID', 0))
ONBOARDING_BOT_HANDLE = os.getenv('ONBOARDING_BOT_HANDLE', '@Leah_onboarding_bot')

# Session timeout (60 minutes)
SESSION_TIMEOUT = 3600

# Demo property data - Casa Lumina, Miami Beach
DEMO_PROPERTY = {
    "name": "Casa Lumina",
    "location": "Miami Beach, FL — 2 blocks from Ocean Drive",
    "type": "Luxury Beachfront Villa",
    "checkin_time": "3:00 PM",
    "checkout_time": "11:00 AM",
    "lockbox_code": "4729 (front gate) · 8831 (main door)",
    "wifi": {
        "network": "CasaLumina_Guest",
        "password": "SunriseBeach2024"
    },
    "pool": {
        "hours": "7am–10pm",
        "heated": True,
        "towels": "Beach cabana"
    },
    "parking": "Free valet or self-park in gated lot",
    "amenities": [
        "Oceanfront infinity pool",
        "Private beach access",
        "Spa & sauna",
        "Gourmet kitchen",
        "Home theater",
        "Wine cellar",
        "Concierge service"
    ],
    "restaurants": [
        {"name": "Casa Tua", "type": "Mediterranean", "distance": "0.3 km", "vibe": "Intimate, candlelit"},
        {"name": "Stubborn Seed", "type": "New American", "distance": "0.5 km", "vibe": "Upscale casual"},
        {"name": "The Surf Club", "type": "French", "distance": "1.2 km", "vibe": "Fine dining"},
        {"name": "Juvia", "type": "Pan-Latin", "distance": "0.7 km", "vibe": "Vibrant, energetic"},
        {"name": "Garcia's Seafood", "type": "Seafood", "distance": "0.4 km", "vibe": "Fresh, casual"}
    ],
    "attractions": [
        "Art Deco Historic District",
        "South Pointe Park",
        "Wynwood Walls (street art)",
        "Vizcaya Museum & Gardens",
        "Miami Seaquarium"
    ],
    "house_rules": [
        "Quiet hours: 10pm–8am",
        "No smoking indoors",
        "Respect neighbors",
        "Pool use: 7am–10pm only"
    ],
    "emergency": {
        "property_manager": "+1-305-555-0100",
        "maintenance": "+1-305-555-0101",
        "police": "911",
        "hospital": "Jackson Memorial Hospital"
    }
}

# Suggested questions for guided experience
SUGGESTED_QUESTIONS = [
    "What are the best fine-dining restaurants near here?",
    "I can't figure out the coffee machine, can you help?",
    "What is the Wi-Fi password?"
]

# Value commentary for each feature type
VALUE_COMMENTARY = {
    "wifi": "That's one less message you have to answer. LEAH handles these instantly, 24/7.",
    "restaurant": "Your guests get personalized recommendations without you lifting a finger. That's 5-star service on autopilot.",
    "amenity": "Guests know exactly what's available. No more 'Is there a pool?' messages. LEAH handles it.",
    "emergency": "In a crisis, your guest gets immediate help. You sleep soundly knowing LEAH is on duty.",
    "checkin": "Guests feel welcomed and informed. That's the difference between a good stay and an unforgettable one.",
}

# ============================================================================
# ENUMS & STATE MANAGEMENT
# ============================================================================

class DemoBotPhase(Enum):
    """Demo bot conversation phases"""
    INTRO = "intro"
    CONFIRMATION = "confirmation"
    SIMULATION = "simulation"
    REVEAL = "reveal"
    QUALIFICATION = "qualification"
    PITCH = "pitch"
    CLOSE = "close"
    EXPIRED = "expired"


class UserSession:
    """Manages user session state"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.phase = DemoBotPhase.INTRO
        self.message_count = 0
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.guest_name = None
        self.property_count = None
        self.conversation_history = []

    def is_expired(self) -> bool:
        """Check if session has expired"""
        return (datetime.now() - self.created_at).total_seconds() > SESSION_TIMEOUT

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

    def increment_message_count(self):
        """Increment message counter"""
        self.message_count += 1


# Global session store
user_sessions: Dict[int, UserSession] = {}


# ============================================================================
# PHASE 1: INTRO & CONFIRMATION
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with powerful intro"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id)
    
    session = user_sessions[user_id]
    session.phase = DemoBotPhase.INTRO
    session.update_activity()
    
    logger.info(f"User {user_id} started demo")
    
    intro_message = (
        "✨ <b>Welcome to LEAH — Luxury Experience Assistant Host</b> ✨\n\n"
        "I'm your property's 24/7 AI concierge. I handle every guest interaction instantly: "
        "check-in questions, restaurant recommendations, emergencies, and everything in between.\n\n"
        "<b>What You're About to Experience:</b>\n"
        "You're about to step into the shoes of a guest at <b>Casa Lumina</b>, a luxury beachfront villa. "
        "Your mission: experience the speed, intelligence, and professionalism of your future AI concierge.\n\n"
        "<b>What to Look For:</b>\n"
        "Pay close attention to the quality and speed of responses. This is the experience that earns 5-star reviews "
        "and frees up 90% of your time managing guest messages.\n\n"
        "Ready to see what your guests will experience? Type <b>\"Let's go\"</b> to begin."
    )
    
    await update.message.reply_html(intro_message)
    session.phase = DemoBotPhase.CONFIRMATION


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle confirmation gate"""
    user_id = update.effective_user.id
    user_text = update.message.text.lower().strip()
    
    if user_id not in user_sessions:
        await update.message.reply_text("Please start with /start first.")
        return
    
    session = user_sessions[user_id]
    session.update_activity()
    
    affirmative = ["let's go", "go", "start", "ready", "yes", "ok", "👍", "begin", "show me"]
    
    if any(word in user_text for word in affirmative):
        session.phase = DemoBotPhase.SIMULATION
        session.message_count = 0
        session.conversation_history = []
        
        logger.info(f"User {user_id} confirmed - entering simulation")
        
        # Vivid scene-setting welcome
        welcome = (
            f"🎭 <b>SIMULATION START</b> 🎭\n\n"
            f"<i>You've just arrived at {DEMO_PROPERTY['name']}, a stunning luxury beachfront villa in {DEMO_PROPERTY['location']}. "
            f"The sun is setting, the ocean breeze is perfect, and you're settling in for an unforgettable stay.</i>\n\n"
            f"Welcome to <b>{DEMO_PROPERTY['name']}</b> ✨\n\n"
            f"I'm LEAH, your personal concierge for the duration of your stay. I'm here 24/7 to make sure everything is absolutely perfect.\n\n"
            f"<b>To see what I can do, try asking one of these:</b>\n"
            f"• {SUGGESTED_QUESTIONS[0]}\n"
            f"• {SUGGESTED_QUESTIONS[1]}\n"
            f"• {SUGGESTED_QUESTIONS[2]}\n\n"
            f"Or ask me anything a guest would. What's on your mind?"
        )
        await update.message.reply_html(welcome)
    else:
        await update.message.reply_text(
            "I'm ready when you are! Just type \"Let's go\" and I'll show you everything."
        )


# ============================================================================
# PHASE 2: GUIDED SIMULATION WITH VALUE COMMENTARY
# ============================================================================

async def generate_concierge_response(guest_message: str) -> str:
    """Generate AI response using Groq API"""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        system_prompt = f"""You are LEAH, a luxury property concierge for {DEMO_PROPERTY['name']}.
        
Your role: Provide exceptional guest service with warmth, professionalism, and attention to detail.

Property Details:
- Location: {DEMO_PROPERTY['location']}
- Type: {DEMO_PROPERTY['type']}
- Check-in: {DEMO_PROPERTY['checkin_time']} | Check-out: {DEMO_PROPERTY['checkout_time']}
- WiFi: {DEMO_PROPERTY['wifi']['network']} / {DEMO_PROPERTY['wifi']['password']}
- Amenities: {', '.join(DEMO_PROPERTY['amenities'])}
- Restaurants: {', '.join([f"{r['name']} ({r['type']})" for r in DEMO_PROPERTY['restaurants']])}

Tone: Warm, professional, luxury hospitality. Like a 5-star hotel concierge.
Length: 2-4 sentences, conversational.
Never break character. Always be helpful and anticipate guest needs."""

        response = client.messages.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": guest_message}
            ],
            temperature=0.7,
            max_tokens=512,
            timeout=30
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return (
            "I apologize for the technical difficulty. Please try again, "
            "or feel free to ask me anything about the property!"
        )


def get_value_commentary(guest_message: str) -> Optional[str]:
    """Determine if response warrants value commentary"""
    message_lower = guest_message.lower()
    
    if any(word in message_lower for word in ["wifi", "password", "internet", "connection"]):
        return VALUE_COMMENTARY["wifi"]
    elif any(word in message_lower for word in ["restaurant", "dining", "eat", "food", "dinner"]):
        return VALUE_COMMENTARY["restaurant"]
    elif any(word in message_lower for word in ["pool", "gym", "spa", "amenity", "available"]):
        return VALUE_COMMENTARY["amenity"]
    elif any(word in message_lower for word in ["emergency", "help", "problem", "issue", "broken"]):
        return VALUE_COMMENTARY["emergency"]
    elif any(word in message_lower for word in ["check-in", "checkin", "arrive", "arrival", "access"]):
        return VALUE_COMMENTARY["checkin"]
    
    return None


async def handle_guest_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle guest messages during simulation"""
    user_id = update.effective_user.id
    user_text = update.message.text
    
    if user_id not in user_sessions:
        await update.message.reply_text("Please start with /start first.")
        return
    
    session = user_sessions[user_id]
    
    if session.is_expired():
        session.phase = DemoBotPhase.EXPIRED
        await update.message.reply_text(
            "Your session has expired. Type /start to begin a new demo."
        )
        return
    
    session.update_activity()
    
    if session.phase == DemoBotPhase.CONFIRMATION:
        await handle_confirmation(update, context)
        return
    
    if session.phase != DemoBotPhase.SIMULATION and session.phase != DemoBotPhase.REVEAL:
        return
    
    # Capture guest name on first message
    if session.message_count == 0:
        session.guest_name = user_text
        response = f"Wonderful to meet you, {user_text}! I'm so glad you're here. How can I make your stay absolutely perfect?"
        await update.message.reply_text(response)
        session.increment_message_count()
        return
    
    # Generate concierge response
    response = await generate_concierge_response(user_text)
    await update.message.reply_text(response)
    
    # Add value-reinforcing commentary
    commentary = get_value_commentary(user_text)
    if commentary:
        await update.message.reply_text(f"<i>{commentary}</i>", parse_mode="HTML")
    
    session.increment_message_count()
    
    # ===== THEATRICAL REVEAL (after 3-4 interactions) =====
    if session.message_count >= 3 and session.phase == DemoBotPhase.SIMULATION:
        session.phase = DemoBotPhase.REVEAL
        
        reveal_message = (
            "🎬 <b>And... scene.</b>\n\n"
            f"You've just experienced what your guests will feel: instant, professional, 24/7 service. "
            f"That's the magic of LEAH.\n\n"
            f"<b>Now, would you like me to show you how this all works from your side as the host?</b> "
            f"I can explain the setup, pricing, and how you can have this running for your properties in under 10 minutes.\n\n"
            f"Ready to learn how to get this for yourself?"
        )
        
        keyboard = [[
            InlineKeyboardButton("Yes, Show Me", callback_data="show_host_pitch"),
            InlineKeyboardButton("Ask Me More", callback_data="ask_more")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(reveal_message, reply_markup=reply_markup)
        logger.info(f"User {user_id} reached reveal moment")


# ============================================================================
# PHASE 3: QUALIFICATION & PERSONALIZED PITCH
# ============================================================================

async def handle_reveal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle reveal moment callbacks"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in user_sessions:
        await query.answer("Session expired.")
        return
    
    session = user_sessions[user_id]
    
    if query.data == "show_host_pitch":
        session.phase = DemoBotPhase.QUALIFICATION
        
        await query.answer()
        await query.edit_message_text(
            "<b>Perfect! Let me ask you one quick question to personalize this for you:</b>\n\n"
            "How many properties do you currently manage?",
            parse_mode="HTML"
        )
        logger.info(f"User {user_id} ready for qualification")
    
    elif query.data == "ask_more":
        await query.answer()
        await query.edit_message_text(
            "Great! Feel free to keep exploring. Ask me anything else about the property, "
            "and when you're ready to learn about the host side, just let me know!"
        )


async def handle_qualification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle property count qualification"""
    user_id = update.effective_user.id
    user_text = update.message.text
    
    if user_id not in user_sessions:
        await update.message.reply_text("Please start with /start first.")
        return
    
    session = user_sessions[user_id]
    
    if session.phase != DemoBotPhase.QUALIFICATION:
        return
    
    session.property_count = user_text
    session.phase = DemoBotPhase.PITCH
    
    logger.info(f"User {user_id} property count: {user_text}")
    
    # Personalized pitch based on property count
    pitch_message = (
        f"<b>LEAH for Hosts — How It Works:</b>\n\n"
        f"You manage {user_text} properties. Perfect. Here's what LEAH does for you:\n\n"
        f"<b>The Problem You're Solving:</b>\n"
        f"Right now, you're answering the same questions 100 times a month:\n"
        f"• \"What's the Wi-Fi password?\"\n"
        f"• \"Where's the nearest restaurant?\"\n"
        f"• \"How do I work the AC?\"\n\n"
        f"<b>The Solution:</b>\n"
        f"LEAH handles 95% of guest requests automatically. Your guests get instant, professional answers. "
        f"You get your life back.\n\n"
        f"<b>The Results:</b>\n"
        f"✓ 90% less time managing messages\n"
        f"✓ Higher guest satisfaction (5-star reviews)\n"
        f"✓ More bookings\n"
        f"✓ Better reviews\n\n"
        f"<b>Pricing for {user_text} properties:</b>\n"
        f"• <b>Essential Plan:</b> $100 one-time enrollment + $50/month (1-3 properties)\n"
        f"• <b>Premium Plan:</b> $300 one-time enrollment + $150/month (4-10 properties)\n"
        f"• <b>Enterprise:</b> Custom pricing (unlimited)\n\n"
        f"<b>The Setup:</b>\n"
        f"8 minutes. That's it. Our onboarding assistant will walk you through everything.\n\n"
        f"<b>Ready to get started?</b>"
    )
    
    keyboard = [[
        InlineKeyboardButton("Start Onboarding", url=f"https://t.me/{ONBOARDING_BOT_HANDLE.lstrip('@')}?start={user_id}")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(pitch_message, reply_markup=reply_markup)
    session.phase = DemoBotPhase.CLOSE
    logger.info(f"User {user_id} shown personalized pitch")


# ============================================================================
# ADMIN COMMANDS
# ============================================================================

async def admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to view bot status"""
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("Unauthorized")
        return
    
    active_sessions = len(user_sessions)
    converted = sum(1 for s in user_sessions.values() if s.phase == DemoBotPhase.CLOSE)
    
    status_message = (
        f"<b>Demo Bot Status</b>\n\n"
        f"Active Sessions: {active_sessions}\n"
        f"Converted to Pitch: {converted}\n"
        f"Timestamp: {datetime.now().isoformat()}\n"
        f"Status: ✅ Running"
    )
    await update.message.reply_html(status_message)
    logger.info(f"Admin status requested by {update.effective_user.id}")


# ============================================================================
# ERROR HANDLING
# ============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Start the bot"""
    logger.info("Starting LEAH Demo Bot (World-Class)...")
    
    if not all([DEMO_BOT_TOKEN, GROQ_API_KEY]):
        logger.error("Missing required environment variables")
        return
    
    # Create application
    app = Application.builder().token(DEMO_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin_status", admin_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guest_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_qualification))
    
    # Callback handlers
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_reveal_callback))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Start polling
    logger.info("Demo Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
