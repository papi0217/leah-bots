#!/usr/bin/env python3
"""
LEAH Demo Bot — Luxury Experience Assistant Host
Telegram Bot for converting property managers into paying customers
through an immersive guest experience simulation.

System Design: Complete behavioral specification with 6 phases,
Casa Lumina demo property, 5-message sales trigger, and seamless
handoff to onboarding bot.

Author: Manus AI
Version: 3.1 (Production-Ready)
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
INACTIVITY_NUDGE = 600  # 10 minutes

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

# ============================================================================
# ENUMS & STATE MANAGEMENT
# ============================================================================

class DemoBotPhase(Enum):
    """Demo bot conversation phases"""
    IDLE = "idle"
    PRE_DEMO_INTRO = "pre_demo_intro"
    CONFIRMATION_GATE = "confirmation_gate"
    SIMULATION_ACTIVE = "simulation_active"
    SALES_NUDGE_SENT = "sales_nudge_sent"
    SALES_PIVOT = "sales_pivot"
    HANDOFF_TO_ONBOARDING = "handoff_to_onboarding"
    SESSION_EXPIRED = "session_expired"


class UserSession:
    """Manages user session state"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.phase = DemoBotPhase.IDLE
        self.message_count = 0
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.host_name = None
        self.nudge_sent = False
        self.sales_pivot_shown = False
        self.conversation_history = []

    def is_expired(self) -> bool:
        """Check if session has expired (60 minutes)"""
        return (datetime.now() - self.created_at).total_seconds() > SESSION_TIMEOUT

    def is_inactive(self) -> bool:
        """Check if user has been inactive for 10 minutes"""
        return (datetime.now() - self.last_activity).total_seconds() > INACTIVITY_NUDGE

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

    def increment_message_count(self):
        """Increment message counter"""
        self.message_count += 1


# Global session store
user_sessions: Dict[int, UserSession] = {}


# ============================================================================
# PHASE 1: PRE-DEMO INTRODUCTION
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - begin demo introduction"""
    user_id = update.effective_user.id
    
    # Initialize or retrieve session
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id)
    
    session = user_sessions[user_id]
    session.phase = DemoBotPhase.PRE_DEMO_INTRO
    session.update_activity()
    
    logger.info(f"User {user_id} started demo bot")
    
    intro_message = (
        "Hello! I'm <b>LEAH</b> — Luxury Experience Assistant Host.\n\n"
        "I'm your property's 24/7 AI concierge. I handle every guest interaction: "
        "check-in instructions, local recommendations, issue reports, and everything "
        "in between — so you don't have to.\n\n"
        "In a moment, I'll simulate exactly what your guests would experience from the "
        "moment they message me.\n\n"
        "<b>You'll play the role of a guest arriving at the property I manage.</b>\n\n"
        "Ready to see what your guests will love? Type <b>\"Let's go\"</b> to begin."
    )
    
    await update.message.reply_html(intro_message)


# ============================================================================
# PHASE 2: CONFIRMATION GATE
# ============================================================================

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle confirmation gate - wait for 'Let's go' or similar"""
    user_id = update.effective_user.id
    user_text = update.message.text.lower().strip()
    
    if user_id not in user_sessions:
        await update.message.reply_text("Please start with /start first.")
        return
    
    session = user_sessions[user_id]
    session.update_activity()
    
    # Affirmative responses
    affirmative = ["let's go", "go", "start", "ready", "yes", "ok", "👍", "begin", "show me"]
    
    if any(word in user_text for word in affirmative):
        # Enter simulation phase
        session.phase = DemoBotPhase.SIMULATION_ACTIVE
        session.message_count = 0
        session.conversation_history = []
        
        logger.info(f"User {user_id} confirmed - entering simulation")
        
        # Send system message
        await update.message.reply_text(
            "— SIMULATION START — Demo property loaded: Casa Lumina, Miami Beach —",
            parse_mode="HTML"
        )
        
        # Welcome message as concierge
        welcome = (
            f"Welcome to <b>{DEMO_PROPERTY['name']}</b> ✨\n\n"
            "I'm LEAH, your personal concierge for the duration of your stay. "
            "I'm here 24/7 to make sure everything is absolutely perfect.\n\n"
            "To get started — what's your name? I love making every experience personal."
        )
        await update.message.reply_html(welcome)
    
    # Educational responses
    elif any(word in user_text for word in ["what", "how", "tell", "more", "info"]):
        pitch = (
            "LEAH is an AI concierge that handles guest communication 24/7. "
            "I answer questions, provide recommendations, handle emergencies, and more. "
            "Let's experience it together — just say \"Let's go\" when ready!"
        )
        await update.message.reply_text(pitch)
    
    # Unclear response
    else:
        await update.message.reply_text(
            "I'm ready when you are! Just type \"Let's go\" and I'll show you everything."
        )


# ============================================================================
# PHASE 3: LIVE GUEST SIMULATION
# ============================================================================

async def generate_concierge_response(guest_message: str, context_info: Dict) -> str:
    """Generate AI response using Groq API with luxury hospitality tone"""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Build system prompt with property context
        system_prompt = f"""You are LEAH, a luxury property concierge for {DEMO_PROPERTY['name']}.
        
Your role: Provide exceptional guest service with warmth, professionalism, and attention to detail.

Property Details:
- Location: {DEMO_PROPERTY['location']}
- Type: {DEMO_PROPERTY['type']}
- Check-in: {DEMO_PROPERTY['checkin_time']} | Check-out: {DEMO_PROPERTY['checkout_time']}
- WiFi: {DEMO_PROPERTY['wifi']['network']} / {DEMO_PROPERTY['wifi']['password']}
- Amenities: {', '.join(DEMO_PROPERTY['amenities'])}

Tone: Warm, professional, luxury hospitality. Like a 5-star hotel concierge.
Length: 2-4 sentences, conversational.
Never break character. Never mention you're an AI demo.
Always be helpful, proactive, and anticipate guest needs."""

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


async def handle_guest_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle guest messages during simulation"""
    user_id = update.effective_user.id
    user_text = update.message.text
    
    if user_id not in user_sessions:
        await update.message.reply_text("Please start with /start first.")
        return
    
    session = user_sessions[user_id]
    
    # Check session expiration
    if session.is_expired():
        session.phase = DemoBotPhase.SESSION_EXPIRED
        await update.message.reply_text(
            "Your session has expired. Type /start to begin a new demo."
        )
        return
    
    session.update_activity()
    
    # Handle different phases
    if session.phase == DemoBotPhase.PRE_DEMO_INTRO or session.phase == DemoBotPhase.CONFIRMATION_GATE:
        await handle_confirmation(update, context)
    
    elif session.phase == DemoBotPhase.SIMULATION_ACTIVE or session.phase == DemoBotPhase.SALES_NUDGE_SENT:
        # Capture guest name on first message
        if session.message_count == 0:
            session.host_name = user_text
            response = f"Wonderful to meet you, {user_text}! I'm so glad you're here. How can I make your stay absolutely perfect?"
            await update.message.reply_text(response)
            session.increment_message_count()
            return
        
        # Generate concierge response
        response = await generate_concierge_response(user_text, {"property": DEMO_PROPERTY})
        await update.message.reply_text(response)
        
        session.increment_message_count()
        
        # ===== PHASE 4: SALES TRIGGER (after 5 messages) =====
        if session.message_count == 5 and not session.nudge_sent:
            session.phase = DemoBotPhase.SALES_NUDGE_SENT
            session.nudge_sent = True
            
            sales_nudge = (
                "💡 <b>Quick Note:</b>\n\n"
                "If at any moment you'd like to stop the demo and learn how LEAH works "
                "<b>for hosts</b>, simply ask about pricing, setup, or features, "
                "and I'll explain the system.\n\n"
                "Otherwise, feel free to keep exploring!"
            )
            await update.message.reply_html(sales_nudge)
            logger.info(f"User {user_id} reached 5-message trigger")
        
        # ===== PHASE 5: SALES PIVOT (on interest signal) =====
        interest_keywords = ["pricing", "cost", "how much", "setup", "configure", "host", "for me", "own property", "features", "how does it work", "interested"]
        if any(keyword in user_text.lower() for keyword in interest_keywords) and not session.sales_pivot_shown:
            session.phase = DemoBotPhase.SALES_PIVOT
            session.sales_pivot_shown = True
            
            sales_pivot = (
                "<b>LEAH for Hosts — How It Works:</b>\n\n"
                "LEAH is an enterprise-grade AI concierge that handles guest communication automatically. "
                "You configure LEAH with your property information, and LEAH handles 95% of guest requests instantly.\n\n"
                "<b>Benefits:</b>\n"
                "✓ 90% less time managing messages\n"
                "✓ Higher guest satisfaction\n"
                "✓ More bookings\n"
                "✓ Better reviews\n"
                "✓ Scalable to multiple properties\n\n"
                "<b>Pricing:</b>\n"
                "• <b>Essential:</b> $100 + $50/month (1-3 properties)\n"
                "• <b>Premium:</b> $300 + $150/month (4-10 properties)\n"
                "• <b>Enterprise:</b> Custom pricing (unlimited)\n\n"
                "<b>Ready to get started?</b> Click below to begin onboarding."
            )
            
            keyboard = [[
                InlineKeyboardButton("Start Onboarding", url=f"https://t.me/{ONBOARDING_BOT_HANDLE.lstrip('@')}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(sales_pivot, reply_markup=reply_markup)
            logger.info(f"User {user_id} shown sales pivot")


# ============================================================================
# ADMIN COMMANDS
# ============================================================================

async def admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to view bot status"""
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("Unauthorized")
        return
    
    active_sessions = len(user_sessions)
    status_message = (
        f"<b>Demo Bot Status</b>\n\n"
        f"Active Sessions: {active_sessions}\n"
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
    logger.info("Starting LEAH Demo Bot...")
    
    if not all([DEMO_BOT_TOKEN, GROQ_API_KEY]):
        logger.error("Missing required environment variables")
        return
    
    # Create application
    app = Application.builder().token(DEMO_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin_status", admin_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guest_message))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Start polling
    logger.info("Demo Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
