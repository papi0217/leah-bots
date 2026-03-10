#!/usr/bin/env python3
"""
LEAH Onboarding Assistant — Host Property Configuration
Guides hosts through complete setup to create custom LEAH instance
Generates property configuration JSON for guest concierge
"""

import os
import json
import asyncio
import logging
import qrcode
import uuid
from io import BytesIO
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
    ConversationHandler,
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
# CONFIGURATION
# ============================================================================

ONBOARDING_BOT_TOKEN = os.getenv('ONBOARDING_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
OWNER_TELEGRAM_ID = int(os.getenv('OWNER_TELEGRAM_ID', '0'))

if not all([ONBOARDING_BOT_TOKEN, GROQ_API_KEY, OWNER_TELEGRAM_ID]):
    logger.error("❌ Missing required environment variables")
    exit(1)

groq_client = Groq(api_key=GROQ_API_KEY)

# ============================================================================
# CONVERSATION STATES
# ============================================================================

HOST_NAME, HOST_EMAIL, NUM_PROPERTIES = range(3)
PROPERTY_NAME, PROPERTY_TYPE, GUEST_CAPACITY = range(3, 6)
CHECKIN_TIME, CHECKOUT_TIME, ENTRY_INSTRUCTIONS = range(6, 9)
WIFI_NAME, WIFI_PASSWORD, PARKING, HOUSE_RULES = range(9, 13)
AMENITIES, RESTAURANTS, COFFEE_SHOPS, ATTRACTIONS = range(13, 17)
TONE_PREFERENCE, CONFIRMATION = range(17, 19)

# ============================================================================
# ONBOARDING BOT CONFIGURATION (LOCKED)
# ============================================================================

ONBOARDING_BOT_CONFIG = {
    'name': 'LEAH Onboarding Assistant',
    'handle': '@Leah_onboarding_bot',
    'purpose': 'Guide hosts through property setup and LEAH configuration',
}

# ============================================================================
# QR CODE GENERATION
# ============================================================================

class QRCodeGenerator:
    """Generates QR codes for property concierge access"""
    
    @staticmethod
    def generate_property_qr(property_id: str, property_name: str) -> bytes:
        """Generate QR code for property concierge access"""
        
        # Create unique concierge link
        concierge_link = f"https://leah-concierge.app/property/{property_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(concierge_link)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        logger.info(f"Onboarding Bot: Generated QR code for property {property_id}")
        return img_bytes.getvalue()

# ============================================================================
# CONFIGURATION GENERATOR
# ============================================================================

class ConfigurationGenerator:
    """Generates LEAH configuration files from onboarding data"""
    
    @staticmethod
    def generate_configs(user_data: Dict) -> Dict:
        """Generate all configuration files"""
        
        property_id = str(uuid.uuid4())[:8]
        
        # Host profile
        host_profile = {
            "host_id": str(uuid.uuid4()),
            "name": user_data.get('host_name', ''),
            "email": user_data.get('host_email', ''),
            "created_at": datetime.now().isoformat(),
            "properties": [property_id],
        }
        
        # Property profile
        property_profile = {
            "property_id": property_id,
            "name": user_data.get('property_name', ''),
            "type": user_data.get('property_type', 'villa'),
            "address": user_data.get('property_address', ''),
            "guest_capacity": user_data.get('guest_capacity', 0),
            "created_at": datetime.now().isoformat(),
        }
        
        # Guest response config
        guest_response_config = {
            "property_id": property_id,
            "checkin_time": user_data.get('checkin_time', '4:00 PM'),
            "checkout_time": user_data.get('checkout_time', '11:00 AM'),
            "entry_instructions": user_data.get('entry_instructions', ''),
            "wifi_name": user_data.get('wifi_name', ''),
            "wifi_password": user_data.get('wifi_password', ''),
            "parking_instructions": user_data.get('parking_instructions', ''),
            "house_rules": user_data.get('house_rules', ''),
            "amenities": user_data.get('amenities', []),
            "tone": user_data.get('tone_preference', 'professional'),
        }
        
        # Local recommendations
        local_recommendations = {
            "property_id": property_id,
            "restaurants": user_data.get('restaurants', []),
            "coffee_shops": user_data.get('coffee_shops', []),
            "attractions": user_data.get('attractions', []),
        }
        
        return {
            "host_profile": host_profile,
            "property_profile": property_profile,
            "guest_response_config": guest_response_config,
            "local_recommendations": local_recommendations,
            "property_id": property_id,
        }

# ============================================================================
# ONBOARDING HANDLERS
# ============================================================================

async def onboarding_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start onboarding flow"""
    
    user_id = update.effective_user.id
    
    message = """✨ **Welcome to LEAH Onboarding** ✨

I'm here to set up your custom LEAH concierge in just 5-10 minutes.

**What we'll do:**
1. Gather your property information
2. Configure guest responses
3. Set up local recommendations
4. Generate your custom LEAH instance
5. Create QR codes for your guests

**What you'll get:**
✓ Custom LEAH concierge for your property
✓ 24/7 guest support automation
✓ Reduced message response time
✓ Higher guest satisfaction
✓ More time for your business

Let's begin! What's your name?"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: User {user_id} started onboarding")
    
    return HOST_NAME

async def onboarding_host_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get host name"""
    
    host_name = update.message.text.strip()
    
    if len(host_name) < 2 or len(host_name) > 100:
        await update.message.reply_text("Please enter a valid name (2-100 characters).")
        return HOST_NAME
    
    context.user_data['host_name'] = host_name
    
    message = f"""✓ **Name:** {host_name}

What's your email address? (We'll use this for your account and support)"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Host name set to {host_name}")
    
    return HOST_EMAIL

async def onboarding_host_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get host email"""
    
    email = update.message.text.strip()
    
    if '@' not in email or len(email) < 5:
        await update.message.reply_text("Please enter a valid email address.")
        return HOST_EMAIL
    
    context.user_data['host_email'] = email
    
    message = f"""✓ **Email:** {email}

How many properties do you want to set up LEAH for right now? (You can add more later)
(Enter a number, e.g., 1)"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Host email set to {email}")
    
    return NUM_PROPERTIES

async def onboarding_num_properties(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get number of properties"""
    
    try:
        num_props = int(update.message.text.strip())
        
        if num_props < 1 or num_props > 20:
            await update.message.reply_text("Please enter a valid number (1-20).")
            return NUM_PROPERTIES
        
        context.user_data['num_properties'] = num_props
        context.user_data['current_property'] = 1
        
        message = f"""✓ **Properties:** {num_props}

**Property 1 of {num_props}**

What's the name of your first property?
(Example: "Villa Paradiso" or "Beachfront Penthouse")"""
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"Onboarding Bot: Number of properties set to {num_props}")
        
        return PROPERTY_NAME
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return NUM_PROPERTIES

async def onboarding_property_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get property name"""
    
    property_name = update.message.text.strip()
    
    if len(property_name) < 3 or len(property_name) > 100:
        await update.message.reply_text("Please enter a valid property name (3-100 characters).")
        return PROPERTY_NAME
    
    context.user_data['property_name'] = property_name
    
    message = f"""✓ **Property:** {property_name}

What type of property is this?
(apartment, house, villa, condo, townhouse, etc.)"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Property name set to {property_name}")
    
    return PROPERTY_TYPE

async def onboarding_property_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get property type"""
    
    property_type = update.message.text.strip().lower()
    context.user_data['property_type'] = property_type
    
    message = f"""✓ **Type:** {property_type}

How many guests can your property accommodate?
(Enter a number, e.g., 8)"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Property type set to {property_type}")
    
    return GUEST_CAPACITY

async def onboarding_guest_capacity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get guest capacity"""
    
    try:
        capacity = int(update.message.text.strip())
        
        if capacity < 1 or capacity > 500:
            await update.message.reply_text("Please enter a valid capacity (1-500).")
            return GUEST_CAPACITY
        
        context.user_data['guest_capacity'] = capacity
        
        message = f"""✓ **Capacity:** {capacity} guests

What time do guests check in?
(Example: "4:00 PM" or "16:00")"""
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"Onboarding Bot: Guest capacity set to {capacity}")
        
        return CHECKIN_TIME
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return GUEST_CAPACITY

async def onboarding_checkin_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get check-in time"""
    
    checkin_time = update.message.text.strip()
    context.user_data['checkin_time'] = checkin_time
    
    message = f"""✓ **Check-in:** {checkin_time}

What time do guests check out?
(Example: "11:00 AM" or "11:00")"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Check-in time set to {checkin_time}")
    
    return CHECKOUT_TIME

async def onboarding_checkout_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get check-out time"""
    
    checkout_time = update.message.text.strip()
    context.user_data['checkout_time'] = checkout_time
    
    message = f"""✓ **Check-out:** {checkout_time}

How do guests enter the property?
(Example: "Smart lock code 1234" or "Lockbox under the mat")"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Check-out time set to {checkout_time}")
    
    return ENTRY_INSTRUCTIONS

async def onboarding_entry_instructions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get entry instructions"""
    
    entry_instructions = update.message.text.strip()
    context.user_data['entry_instructions'] = entry_instructions
    
    message = f"""✓ **Entry:** Configured

What's your Wi-Fi network name (SSID)?
(Example: "Villa Paradiso" or "GuestNetwork")"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Entry instructions set")
    
    return WIFI_NAME

async def onboarding_wifi_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get Wi-Fi name"""
    
    wifi_name = update.message.text.strip()
    context.user_data['wifi_name'] = wifi_name
    
    message = f"""✓ **Wi-Fi Name:** {wifi_name}

What's the Wi-Fi password?"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Wi-Fi name set to {wifi_name}")
    
    return WIFI_PASSWORD

async def onboarding_wifi_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get Wi-Fi password"""
    
    wifi_password = update.message.text.strip()
    context.user_data['wifi_password'] = wifi_password
    
    message = f"""✓ **Wi-Fi Password:** Configured

How do guests park? (parking instructions)
(Example: "Free parking in the driveway" or "Paid lot across the street")"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Wi-Fi password set")
    
    return PARKING

async def onboarding_parking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get parking instructions"""
    
    parking = update.message.text.strip()
    context.user_data['parking_instructions'] = parking
    
    message = f"""✓ **Parking:** Configured

What are your house rules?
(Example: "No smoking indoors, Quiet hours 10pm-8am, Respect neighbors")"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Parking instructions set")
    
    return HOUSE_RULES

async def onboarding_house_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get house rules"""
    
    house_rules = update.message.text.strip()
    context.user_data['house_rules'] = house_rules
    
    message = f"""✓ **House Rules:** Configured

What amenities does your property have?
(List separated by commas: Pool, WiFi, Kitchen, Spa, Wine Cellar, Beach Access, etc.)"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: House rules set")
    
    return AMENITIES

async def onboarding_amenities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get amenities"""
    
    amenities = [a.strip() for a in update.message.text.split(',')]
    context.user_data['amenities'] = amenities
    
    message = f"""✓ **Amenities:** {len(amenities)} configured

What restaurants do you recommend for your guests?
(List separated by commas: Restaurant Name - Cuisine Type - Distance)
(Example: "Ristorante Stella - Italian - 2km, Le Petit Bistro - French - 1.5km")"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Amenities set ({len(amenities)} items)")
    
    return RESTAURANTS

async def onboarding_restaurants(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get restaurant recommendations"""
    
    restaurants = [r.strip() for r in update.message.text.split(',')]
    context.user_data['restaurants'] = restaurants
    
    message = f"""✓ **Restaurants:** {len(restaurants)} recommended

What coffee shops or cafes do you recommend?
(List separated by commas, or type "none" if not applicable)"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Restaurants set ({len(restaurants)} items)")
    
    return COFFEE_SHOPS

async def onboarding_coffee_shops(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get coffee shop recommendations"""
    
    coffee_input = update.message.text.strip().lower()
    
    if coffee_input == 'none':
        context.user_data['coffee_shops'] = []
    else:
        context.user_data['coffee_shops'] = [c.strip() for c in update.message.text.split(',')]
    
    message = f"""✓ **Coffee Shops:** Configured

What attractions or activities do you recommend?
(List separated by commas: Attraction Name - Distance)
(Example: "Beach - 500m, Museum - 2km, Hiking Trail - 5km")"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Coffee shops set")
    
    return ATTRACTIONS

async def onboarding_attractions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get attraction recommendations"""
    
    attractions = [a.strip() for a in update.message.text.split(',')]
    context.user_data['attractions'] = attractions
    
    message = f"""✓ **Attractions:** {len(attractions)} recommended

What tone should LEAH use when responding to guests?

🎯 **Professional** — Formal, business-like, efficient
😊 **Friendly** — Warm, conversational, approachable
✨ **Ultra-Luxury** — Sophisticated, refined, exclusive

Which style matches your property best?"""
    
    keyboard = [
        [InlineKeyboardButton("Professional", callback_data="tone_professional")],
        [InlineKeyboardButton("Friendly", callback_data="tone_friendly")],
        [InlineKeyboardButton("Ultra-Luxury", callback_data="tone_luxury")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Attractions set ({len(attractions)} items)")
    
    return TONE_PREFERENCE

async def onboarding_tone_preference(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle tone preference selection"""
    
    query = update.callback_query
    await query.answer()
    
    tone_map = {
        "tone_professional": "professional",
        "tone_friendly": "friendly",
        "tone_luxury": "ultra-luxury",
    }
    
    selected_tone = tone_map.get(query.data, "professional")
    context.user_data['tone_preference'] = selected_tone
    
    # Generate configurations
    configs = ConfigurationGenerator.generate_configs(context.user_data)
    property_id = configs['property_id']
    
    # Generate QR code
    qr_bytes = QRCodeGenerator.generate_property_qr(
        property_id,
        context.user_data['property_name']
    )
    
    # Create summary
    summary = f"""✅ **Setup Complete!**

🏠 **Property:** {context.user_data['property_name']}
👥 **Capacity:** {context.user_data['guest_capacity']} guests
🎯 **Tone:** {selected_tone.title()}
🔗 **Property ID:** `{property_id}`

**Your Configuration Files:**
✓ host_profile.json
✓ property_profile.json
✓ guest_response_config.json
✓ local_recommendations.json

**What's Next:**
1. Your custom LEAH concierge is ready
2. Share the QR code with guests for instant access
3. Guests can now ask LEAH anything about your property
4. You'll see only escalations that need human attention

**Guest Experience:**
Your guests will now have 24/7 access to:
• Property information and amenities
• Check-in/checkout assistance
• Wi-Fi and parking details
• Restaurant recommendations
• Local attractions and activities
• Emergency support

🎉 **Welcome to LEAH!**

Your property is now configured and ready to serve guests."""
    
    await query.edit_message_text(summary, parse_mode="Markdown")
    
    # Send QR code
    qr_file = BytesIO(qr_bytes)
    qr_file.name = f"leah_qr_{property_id}.png"
    await query.message.reply_photo(
        photo=qr_file,
        caption=f"🔗 Guest Concierge QR Code\n\nProperty: {context.user_data['property_name']}\nID: {property_id}\n\nShare this with your guests!"
    )
    
    # Send configuration summary
    config_summary = f"""📋 **Your Configuration Summary:**

**Host Profile:**
Name: {context.user_data['host_name']}
Email: {context.user_data['host_email']}

**Property Details:**
Name: {context.user_data['property_name']}
Type: {context.user_data['property_type']}
Capacity: {context.user_data['guest_capacity']} guests

**Access Information:**
Check-in: {context.user_data['checkin_time']}
Check-out: {context.user_data['checkout_time']}
Entry: {context.user_data['entry_instructions']}

**Amenities:** {', '.join(context.user_data['amenities'])}

**Restaurants:** {len(context.user_data['restaurants'])} recommended
**Attractions:** {len(context.user_data['attractions'])} recommended

**Tone:** {selected_tone.title()}

All configurations have been saved and your LEAH concierge is now active!"""
    
    await query.message.reply_text(config_summary, parse_mode="Markdown")
    
    logger.info(f"Onboarding Bot: Onboarding complete for user {query.from_user.id}")
    
    return ConversationHandler.END

async def onboarding_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel onboarding"""
    
    await update.message.reply_text("Onboarding cancelled. Feel free to start again anytime!")
    return ConversationHandler.END

async def onboarding_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    
    help_text = """📚 **Onboarding Help**

**Getting Started:**
/start — Begin property setup
/cancel — Cancel onboarding
/help — Show this message

**What We'll Configure:**
1. Your host profile (name, email)
2. Property details (name, type, capacity)
3. Access information (check-in, entry)
4. Guest amenities and rules
5. Local recommendations
6. Response tone

**Output:**
✓ Custom LEAH configuration
✓ QR code for guests
✓ Property ID
✓ Configuration files

**Time Required:**
5-10 minutes for complete setup"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Help shown to {update.effective_user.id}")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

async def main_onboarding_bot() -> None:
    """Start Onboarding Bot"""
    
    logger.info("=" * 70)
    logger.info("🚀 LEAH ONBOARDING ASSISTANT BOT — STARTING")
    logger.info("=" * 70)
    
    app = Application.builder().token(ONBOARDING_BOT_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", onboarding_start)],
        states={
            HOST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_host_name)],
            HOST_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_host_email)],
            NUM_PROPERTIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_num_properties)],
            PROPERTY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_property_name)],
            PROPERTY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_property_type)],
            GUEST_CAPACITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_guest_capacity)],
            CHECKIN_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_checkin_time)],
            CHECKOUT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_checkout_time)],
            ENTRY_INSTRUCTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_entry_instructions)],
            WIFI_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_wifi_name)],
            WIFI_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_wifi_password)],
            PARKING: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_parking)],
            HOUSE_RULES: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_house_rules)],
            AMENITIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_amenities)],
            RESTAURANTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_restaurants)],
            COFFEE_SHOPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_coffee_shops)],
            ATTRACTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_attractions)],
            TONE_PREFERENCE: [],
        },
        fallbacks=[CommandHandler("cancel", onboarding_cancel)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", onboarding_help))
    
    logger.info("✅ Onboarding Bot initialized")
    logger.info(f"📱 Handle: {ONBOARDING_BOT_CONFIG['handle']}")
    logger.info("=" * 70)
    
    async with app:
        await app.initialize()
        await app.start()
        logger.info("✅ Onboarding Bot started successfully")
        
        # Keep running
        await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main_onboarding_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Onboarding Bot shutting down...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
