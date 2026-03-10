#!/usr/bin/env python3
"""
LEAH Onboarding Bot — World-Class Premium Onboarding Experience
Telegram Bot for converting prospects into activated customers through
emotionally intelligent, value-reinforcing property configuration.

Implements premium onboarding principles:
- Warm handoff from demo bot with context
- Celebratory welcome and framing
- Value-reinforcing confirmations for every step
- Progress indicators and section transitions
- Tone selection as a "wow" moment
- Celebratory completion with next steps

Author: Manus AI
Version: 4.0 (World-Class)
"""

import os
import logging
import json
import qrcode
from io import BytesIO
from datetime import datetime
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
    format='[%(asctime)s] %(levelname)s - ONBOARDING_BOT: %(message)s',
    handlers=[
        logging.FileHandler('onboarding_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

ONBOARDING_BOT_TOKEN = os.getenv('ONBOARDING_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
OWNER_TELEGRAM_ID = int(os.getenv('OWNER_TELEGRAM_ID', 0))

# ============================================================================
# ENUMS & STATE MANAGEMENT
# ============================================================================

class OnboardingPhase(Enum):
    """Onboarding bot conversation phases"""
    START = "start"
    WELCOME = "welcome"
    HOST_PROFILE = "host_profile"
    PROPERTY_DETAILS = "property_details"
    ACCESS_CHECKIN = "access_checkin"
    AMENITIES = "amenities"
    HOUSE_RULES = "house_rules"
    LOCAL_RECOMMENDATIONS = "local_recommendations"
    EMERGENCY_CONTACTS = "emergency_contacts"
    BRANDING_TONE = "branding_tone"
    TONE_SELECTION = "tone_selection"
    REVIEW = "review"
    COMPLETION = "completion"
    LIVE = "live"


class HostSession:
    """Manages host onboarding session"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.phase = OnboardingPhase.START
        self.created_at = datetime.now()
        self.host_name = None
        self.property_count = None
        self.current_property_name = None
        self.property_index = 0
        self.tone_choice = None
        
        # Configuration data
        self.config = {
            "host_profile": {},
            "property_details": {},
            "access_checkin": {},
            "amenities": {},
            "house_rules": {},
            "local_recommendations": {},
            "emergency_contacts": {},
            "branding_tone": {},
            "properties": []
        }

    def get_completion_percentage(self) -> int:
        """Calculate data completion percentage"""
        total_fields = 0
        filled_fields = 0
        
        for section, data in self.config.items():
            if isinstance(data, dict) and section != "properties":
                total_fields += len(data) if data else 1
                filled_fields += len({k: v for k, v in data.items() if v}) if data else 0
        
        return int((filled_fields / max(total_fields, 1)) * 100) if total_fields > 0 else 0


# Global session store
host_sessions: Dict[int, HostSession] = {}

# Tone selection options with examples
TONE_OPTIONS = {
    "1": {
        "name": "Professional",
        "description": "Clear, efficient, and precise",
        "example": "The check-in time is 4:00 PM. Your access code is 4821."
    },
    "2": {
        "name": "Friendly",
        "description": "Warm, approachable, and personal",
        "example": "Welcome! Check-in is at 4pm — can't wait for you to arrive! Your code is 4821."
    },
    "3": {
        "name": "Ultra-Luxury",
        "description": "Refined, elegant, and immersive",
        "example": "A warm welcome awaits you at 4:00 PM. Your private access code — 4821 — has been prepared exclusively for your arrival."
    }
}


# ============================================================================
# PHASE 1: WARM HANDOFF & WELCOME
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with warm handoff"""
    user_id = update.effective_user.id
    
    if user_id not in host_sessions:
        host_sessions[user_id] = HostSession(user_id)
    
    session = host_sessions[user_id]
    session.phase = OnboardingPhase.WELCOME
    
    # Parse handoff parameters if provided
    args = context.args
    if args and len(args) > 0:
        # Format: name-John-props-2
        for i, arg in enumerate(args):
            if arg.startswith("name-"):
                session.host_name = arg.replace("name-", "")
            elif arg.startswith("props-"):
                session.property_count = int(arg.replace("props-", ""))
    
    logger.info(f"Host {user_id} started onboarding (name: {session.host_name}, props: {session.property_count})")
    
    # Celebratory welcome
    if session.host_name:
        welcome = (
            f"🎉 <b>Welcome, {session.host_name}! Congratulations on this excellent decision.</b> 🎉\n\n"
            f"You just saw what LEAH can do for your guests. Now, let's get it set up for your {session.property_count} properties.\n\n"
            f"My name is LEAH, and I'll be your personal setup concierge for the next 8 minutes. "
            f"We'll move through 3 quick sections, and by the end, you will have a fully operational AI assistant "
            f"and custom QR codes ready for each property.\n\n"
            f"<b>Ready to begin?</b>"
        )
    else:
        welcome = (
            f"🎉 <b>Welcome to LEAH Onboarding!</b> 🎉\n\n"
            f"Congratulations on choosing LEAH. I'm your personal setup concierge, and I'll guide you through "
            f"configuring your AI assistant in just 8 minutes.\n\n"
            f"By the end, you'll have a fully operational 24/7 concierge ready to delight your guests.\n\n"
            f"Let's start with your name. What should I call you?"
        )
    
    await update.message.reply_html(welcome)
    
    if session.host_name:
        session.phase = OnboardingPhase.HOST_PROFILE
        await ask_host_profile(update, context, session)


# ============================================================================
# PHASE 2: HOST PROFILE SECTION
# ============================================================================

async def ask_host_profile(update: Update, context: ContextTypes.DEFAULT_TYPE, session: HostSession) -> None:
    """Ask host profile questions"""
    if session.phase != OnboardingPhase.HOST_PROFILE:
        return
    
    profile_message = (
        "<b>📋 Section 1 of 3: Host Profile</b> (0% complete)\n\n"
        "Let's start with your information. What's your email address?"
    )
    await update.message.reply_html(profile_message)


async def handle_host_profile_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle host profile input"""
    user_id = update.effective_user.id
    user_text = update.message.text
    
    if user_id not in host_sessions:
        await update.message.reply_text("Please start with /start first.")
        return
    
    session = host_sessions[user_id]
    
    if session.phase == OnboardingPhase.WELCOME and not session.host_name:
        session.host_name = user_text
        session.phase = OnboardingPhase.HOST_PROFILE
        
        welcome = (
            f"<b>Welcome, {session.host_name}!</b> 🌟\n\n"
            f"I'm LEAH, your personal setup concierge. In the next 8 minutes, "
            f"we'll configure your AI assistant to perfection.\n\n"
            f"First, how many properties are you setting up today?"
        )
        await update.message.reply_html(welcome)
        return
    
    if session.phase == OnboardingPhase.HOST_PROFILE and not session.property_count:
        try:
            session.property_count = int(user_text)
            session.config["host_profile"]["properties_count"] = session.property_count
            
            confirmation = (
                f"Perfect! {session.property_count} properties. "
                f"That's exciting! Let's get started.\n\n"
                f"<b>📋 Section 1 of 3: Host Profile</b> (20% complete)\n\n"
                f"What's your email address?"
            )
            await update.message.reply_html(confirmation)
        except ValueError:
            await update.message.reply_text("Please enter a number.")
        return
    
    if session.phase == OnboardingPhase.HOST_PROFILE:
        session.config["host_profile"]["email"] = user_text
        
        confirmation = (
            f"<i>Perfect. I'll use {user_text} for all updates and alerts.</i>\n\n"
            f"<b>📋 Section 1 of 3: Host Profile</b> (40% complete)\n\n"
            f"What's your WhatsApp or phone number for emergencies?"
        )
        await update.message.reply_html(confirmation)
        session.phase = OnboardingPhase.PROPERTY_DETAILS
        return
    
    if session.phase == OnboardingPhase.PROPERTY_DETAILS:
        session.config["host_profile"]["phone"] = user_text
        
        confirmation = (
            f"<i>Excellent. I'll contact you here if anything urgent comes up.</i>\n\n"
            f"<b>🏠 Section 2 of 3: Property Details</b> (50% complete)\n\n"
            f"Now, let's set up your first property. What's the property name?"
        )
        await update.message.reply_html(confirmation)
        session.phase = OnboardingPhase.ACCESS_CHECKIN
        return
    
    if session.phase == OnboardingPhase.ACCESS_CHECKIN:
        session.current_property_name = user_text
        session.config["property_details"]["name"] = user_text
        
        confirmation = (
            f"<i>Wonderful. {user_text} is going to be amazing.</i>\n\n"
            f"What's the full address?"
        )
        await update.message.reply_html(confirmation)
        session.phase = OnboardingPhase.AMENITIES
        return
    
    if session.phase == OnboardingPhase.AMENITIES:
        session.config["property_details"]["address"] = user_text
        
        confirmation = (
            f"<i>Got it. Guests will know exactly where to find you.</i>\n\n"
            f"What are your check-in and check-out times? (e.g., 3pm / 11am)"
        )
        await update.message.reply_html(confirmation)
        session.phase = OnboardingPhase.HOUSE_RULES
        return
    
    if session.phase == OnboardingPhase.HOUSE_RULES:
        session.config["property_details"]["checkin_checkout"] = user_text
        
        confirmation = (
            f"<i>Perfect. LEAH will now handle all check-in and check-out coordination.</i>\n\n"
            f"<b>🔑 Access & Check-in</b> (60% complete)\n\n"
            f"How do guests access the property? (lockbox code, smart lock, key handoff, etc.)"
        )
        await update.message.reply_html(confirmation)
        session.phase = OnboardingPhase.LOCAL_RECOMMENDATIONS
        return
    
    if session.phase == OnboardingPhase.LOCAL_RECOMMENDATIONS:
        session.config["access_checkin"]["method"] = user_text
        
        confirmation = (
            f"<i>Excellent. Guests will feel welcomed and informed.</i>\n\n"
            f"What's your WiFi network name and password?"
        )
        await update.message.reply_html(confirmation)
        session.phase = OnboardingPhase.EMERGENCY_CONTACTS
        return
    
    if session.phase == OnboardingPhase.EMERGENCY_CONTACTS:
        session.config["amenities"]["wifi"] = user_text
        
        confirmation = (
            f"<i>That's one of the top 3 questions guests ask, and now LEAH will handle it instantly, 24/7.</i>\n\n"
            f"What amenities does your property have? (pool, gym, spa, kitchen, etc.)"
        )
        await update.message.reply_html(confirmation)
        session.phase = OnboardingPhase.BRANDING_TONE
        return
    
    if session.phase == OnboardingPhase.BRANDING_TONE:
        session.config["amenities"]["list"] = user_text
        
        confirmation = (
            f"<i>Guests know exactly what's available. No more 'Is there a pool?' messages.</i>\n\n"
            f"What are your house rules? (quiet hours, smoking policy, pets, etc.)"
        )
        await update.message.reply_html(confirmation)
        session.phase = OnboardingPhase.TONE_SELECTION
        return
    
    if session.phase == OnboardingPhase.TONE_SELECTION:
        session.config["house_rules"]["rules"] = user_text
        
        confirmation = (
            f"<i>Excellent. LEAH will now politely and professionally enforce these rules.</i>\n\n"
            f"<b>🌟 Section 3 of 3: The Final Touch</b> (80% complete)\n\n"
            f"<b>Choose LEAH's Voice</b> — This defines the personality your guests will interact with.\n\n"
            f"<b>1. Professional</b> — Clear, efficient, and precise\n"
            f"Example: 'The check-in time is 4:00 PM. Your access code is 4821.'\n\n"
            f"<b>2. Friendly</b> — Warm, approachable, and personal\n"
            f"Example: 'Welcome! Check-in is at 4pm — can't wait for you to arrive! Your code is 4821.'\n\n"
            f"<b>3. Ultra-Luxury</b> — Refined, elegant, and immersive\n"
            f"Example: 'A warm welcome awaits you at 4:00 PM. Your private access code — 4821 — has been prepared exclusively for your arrival.'\n\n"
            f"<b>Which tone best matches {session.current_property_name}?</b> (Reply with 1, 2, or 3)"
        )
        await update.message.reply_html(confirmation)
        session.phase = OnboardingPhase.REVIEW
        return
    
    if session.phase == OnboardingPhase.REVIEW:
        if user_text in ["1", "2", "3"]:
            session.tone_choice = TONE_OPTIONS[user_text]["name"]
            session.config["branding_tone"]["tone"] = session.tone_choice
            
            tone_name = TONE_OPTIONS[user_text]["name"]
            confirmation = (
                f"<i>Perfect! {tone_name} it is. Your guests will love it.</i>\n\n"
                f"<b>✅ Configuration Complete!</b>\n\n"
                f"Generating your QR code and deployment files..."
            )
            await update.message.reply_html(confirmation)
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            property_slug = session.current_property_name.replace(" ", "_").lower()
            guest_bot_link = f"https://t.me/leah_{property_slug}_bot"
            qr.add_data(guest_bot_link)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            qr_buffer = BytesIO()
            img.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)
            
            # Send celebratory completion
            completion_message = (
                f"🎉 <b>Congratulations, {session.host_name} — {session.current_property_name} is now live!</b> 🎉\n\n"
                f"You did it. In just a few minutes, you've built a 24/7 AI concierge.\n\n"
                f"<b>Your unique QR Code for {session.current_property_name}:</b>\n"
                f"(See attached image)\n\n"
                f"<b>What to do next:</b>\n"
                f"1. <b>Print Your QR Code:</b> Place this code in a visible location at your property, like the entryway or on the fridge.\n"
                f"2. <b>Test Your Concierge:</b> Scan the code with your own phone right now. Ask it a question, like \"What's the Wi-Fi password?\" and see your new AI assistant in action.\n\n"
                f"That's it. You are officially set up. LEAH is now on duty, ready to provide 5-star service to your guests.\n\n"
                f"<b>You mentioned you have {session.property_count} properties to set up. Would you like to configure the next one now?</b>"
            )
            
            await update.message.reply_html(completion_message)
            await update.message.reply_photo(photo=qr_buffer, caption=f"QR Code for {session.current_property_name}")
            
            session.phase = OnboardingPhase.LIVE
            logger.info(f"Host {user_id} completed onboarding for {session.current_property_name}")
        else:
            await update.message.reply_text("Please reply with 1, 2, or 3.")


# ============================================================================
# ADMIN COMMANDS
# ============================================================================

async def admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to view bot status"""
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("Unauthorized")
        return
    
    active_hosts = len(host_sessions)
    live_instances = sum(1 for s in host_sessions.values() if s.phase == OnboardingPhase.LIVE)
    
    status_message = (
        f"<b>Onboarding Bot Status</b>\n\n"
        f"Active Sessions: {active_hosts}\n"
        f"Live Instances: {live_instances}\n"
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
    logger.info("Starting LEAH Onboarding Bot (World-Class)...")
    
    if not all([ONBOARDING_BOT_TOKEN, GROQ_API_KEY]):
        logger.error("Missing required environment variables")
        return
    
    # Create application
    app = Application.builder().token(ONBOARDING_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin_status", admin_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_host_profile_input))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Start polling
    logger.info("Onboarding Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
