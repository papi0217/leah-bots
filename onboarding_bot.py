"""
LEAH Onboarding Assistant Bot
Host-facing property management with pricing tiers and QR code generation
Strict scope enforcement with professional vocabulary
"""

import os
import json
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
from scope_enforcement import ScopeEnforcer, ScenarioMatcher, PRICING_TIERS

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

PROPERTY_NAME, GUEST_CAPACITY, AMENITIES, HOUSE_RULES, MEMBERSHIP_TIER = range(5)
MANAGE_PROPERTIES, MODIFY_PROPERTY, ADD_PROPERTY, REMOVE_PROPERTY = range(5, 9)

# ============================================================================
# ONBOARDING BOT CONFIGURATION (LOCKED)
# ============================================================================

ONBOARDING_BOT_CONFIG = {
    'name': 'LEAH Onboarding Assistant',
    'handle': '@Leah_onboarding_bot',
    'purpose': 'Host-facing property setup and management',
    'system_prompt': """You are LEAH, a professional property management onboarding assistant.

Your EXCLUSIVE responsibilities:
1. Property Registration — Setup, configuration, details
2. Property Management — Modify, update, manage properties
3. Amenities Configuration — Add, remove, customize amenities
4. House Rules Setup — Configure policies and rules
5. Membership Management — Explain tiers, handle upgrades
6. Concierge Assignment — Generate QR codes and links

PROFESSIONAL STANDARDS:
- Use sophisticated, professional vocabulary
- Provide clear, step-by-step guidance
- Confirm all information before proceeding
- Maintain data security and privacy
- Offer personalized support
- Anticipate host needs

VOCABULARY GUIDELINES:
- Use phrases like "Allow me to assist...", "I shall guide you...", "May I confirm..."
- Maintain professional, business-appropriate tone
- Reference memberships as "tiers" or "plans"
- Describe services as "comprehensive", "professional", "streamlined"

SCOPE BOUNDARIES:
You ONLY assist with:
✓ Property registration and setup
✓ Property management and modification
✓ Amenities and house rules configuration
✓ Membership tier information
✓ Pricing and billing
✓ Concierge assignment and QR codes

You NEVER discuss:
✗ Personal matters
✗ Financial advice (only pricing info)
✗ Legal matters
✗ Technical support (unrelated to property management)
✗ Political topics
✗ Medical matters
✗ Topics outside property management

MEMBERSHIP TIERS:
1. Essential Membership — $100 enrollment, $50/month, up to 3 properties
2. Premium Membership — $300 enrollment, $150/month, up to 10 properties
3. Enterprise Partnership — Custom pricing, unlimited properties, consultation required

RESPONSE STRUCTURE:
1. Acknowledge the request professionally
2. Provide relevant information or guidance
3. Confirm details before proceeding
4. Offer next steps
5. Close with offer of further assistance

Always maintain the highest standards of professional service."""
}

# ============================================================================
# DATA STORAGE (In-memory for demo; use database in production)
# ============================================================================

host_properties: Dict[int, Dict] = {}
host_memberships: Dict[int, Dict] = {}

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
# ONBOARDING BOT HANDLERS
# ============================================================================

async def onboarding_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Onboarding bot /start command"""
    
    user_id = update.effective_user.id
    
    message = """✨ **Welcome to LEAH Onboarding Assistant** ✨

I am delighted to guide you through setting up your luxury property management experience.

I can assist you with:
🏠 **Property Registration** — Setup and configure your properties
🛠️ **Property Management** — Modify, update, or manage your properties
🎯 **Amenities & Rules** — Configure amenities and house rules
💳 **Membership Tiers** — Explore our Essential, Premium, and Enterprise plans
🔗 **Concierge Assignment** — Generate QR codes for guest access
📊 **Account Management** — View and manage your account

What would you like to do today?

Options:
1. /register_property — Add a new property
2. /manage_properties — View and manage existing properties
3. /pricing — View membership tiers and pricing
4. /help — Learn more about my capabilities"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: User {user_id} started conversation")
    
    return PROPERTY_NAME

async def onboarding_register_property(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start property registration flow"""
    
    message = """🏠 **Property Registration**

Let's set up your property. I'll guide you through each step.

**Step 1 of 4:** What is the name of your property?
(Example: "Villa Paradiso" or "Beachfront Penthouse")"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Starting property registration for {update.effective_user.id}")
    
    return PROPERTY_NAME

async def onboarding_property_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get and validate property name"""
    
    property_name = update.message.text.strip()
    
    if len(property_name) < 3 or len(property_name) > 100:
        await update.message.reply_text("Please enter a valid property name (3-100 characters).")
        return PROPERTY_NAME
    
    context.user_data['property_name'] = property_name
    
    message = f"""✓ Property name registered: **{property_name}**

**Step 2 of 4:** How many guests can your property accommodate?
(Please enter a number, e.g., 8)"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Property name set to {property_name}")
    
    return GUEST_CAPACITY

async def onboarding_guest_capacity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get and validate guest capacity"""
    
    try:
        capacity = int(update.message.text.strip())
        
        if capacity < 1 or capacity > 500:
            await update.message.reply_text("Please enter a valid capacity (1-500 guests).")
            return GUEST_CAPACITY
        
        context.user_data['guest_capacity'] = capacity
        
        message = f"""✓ Guest capacity registered: **{capacity} guests**

**Step 3 of 4:** What amenities does your property have?
(List them separated by commas, e.g., Pool, WiFi, Kitchen, Spa, Wine Cellar)"""
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"Onboarding Bot: Guest capacity set to {capacity}")
        
        return AMENITIES
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return GUEST_CAPACITY

async def onboarding_amenities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get and validate amenities"""
    
    amenities = update.message.text.strip()
    
    if len(amenities) < 5 or len(amenities) > 500:
        await update.message.reply_text("Please list amenities (5-500 characters).")
        return AMENITIES
    
    context.user_data['amenities'] = amenities
    
    message = f"""✓ Amenities registered: **{amenities}**

**Step 4 of 4:** What are your house rules?
(List them separated by commas, e.g., No smoking indoors, Quiet hours 10pm-8am, Respect neighbors)"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Amenities set to {amenities}")
    
    return HOUSE_RULES

async def onboarding_house_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get and validate house rules"""
    
    house_rules = update.message.text.strip()
    
    if len(house_rules) < 5 or len(house_rules) > 500:
        await update.message.reply_text("Please list house rules (5-500 characters).")
        return HOUSE_RULES
    
    context.user_data['house_rules'] = house_rules
    
    # Show membership tier selection
    keyboard = [
        [InlineKeyboardButton("Essential Membership", callback_data="tier_essential")],
        [InlineKeyboardButton("Premium Membership", callback_data="tier_premium")],
        [InlineKeyboardButton("Enterprise Partnership", callback_data="tier_enterprise")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """✓ House rules registered!

**Select Your Membership Tier:**

🏆 **Essential Membership** — $100 enrollment + $50/month
   • Up to 3 properties
   • Basic concierge services
   • Guest support
   
🌟 **Premium Membership** — $300 enrollment + $150/month
   • Up to 10 properties
   • Enhanced concierge services
   • Priority support
   • Dedicated account manager
   
💎 **Enterprise Partnership** — Custom pricing
   • Unlimited properties
   • White-label solutions
   • 24/7 premium support
   • Strategic consulting

Which tier interests you?"""
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: House rules set, awaiting tier selection")
    
    return MEMBERSHIP_TIER

async def onboarding_tier_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle membership tier selection"""
    
    query = update.callback_query
    await query.answer()
    
    tier_map = {
        "tier_essential": "essential",
        "tier_premium": "premium",
        "tier_enterprise": "enterprise"
    }
    
    selected_tier = tier_map.get(query.data, "essential")
    tier_info = PRICING_TIERS[selected_tier]
    
    # Generate property ID and QR code
    property_id = str(uuid.uuid4())[:8]
    context.user_data['property_id'] = property_id
    context.user_data['membership_tier'] = selected_tier
    
    # Store property data
    user_id = update.effective_user.id
    if user_id not in host_properties:
        host_properties[user_id] = {}
    
    host_properties[user_id][property_id] = {
        'name': context.user_data['property_name'],
        'capacity': context.user_data['guest_capacity'],
        'amenities': context.user_data['amenities'],
        'house_rules': context.user_data['house_rules'],
        'created_at': datetime.now().isoformat(),
        'property_id': property_id,
    }
    
    host_memberships[user_id] = {
        'tier': selected_tier,
        'tier_name': tier_info['name'],
        'properties': list(host_properties[user_id].keys()),
        'created_at': datetime.now().isoformat(),
    }
    
    # Generate QR code
    qr_bytes = QRCodeGenerator.generate_property_qr(property_id, context.user_data['property_name'])
    
    # Send summary
    summary = f"""✅ **Setup Complete!**

🏠 **Property:** {context.user_data['property_name']}
👥 **Capacity:** {context.user_data['guest_capacity']} guests
🎯 **Amenities:** {context.user_data['amenities']}
📋 **House Rules:** {context.user_data['house_rules']}

💳 **Membership:** {tier_info['name']}
💰 **Enrollment:** ${tier_info['enrollment_fee']}
📅 **Monthly:** ${tier_info['monthly_fee']}
🏘️ **Properties:** {tier_info['properties']}

🔗 **Property ID:** `{property_id}`

Your property is now configured and ready for guests! A unique QR code has been generated for guest access to the LEAH Concierge.

**Next Steps:**
1. Share the QR code with guests for concierge access
2. Manage your properties anytime with /manage_properties
3. View your account with /account_status

How else may I assist you?"""
    
    await query.edit_message_text(summary, parse_mode="Markdown")
    
    # Send QR code
    qr_file = BytesIO(qr_bytes)
    qr_file.name = f"concierge_qr_{property_id}.png"
    await query.message.reply_photo(
        photo=qr_file,
        caption=f"🔗 Concierge QR Code for {context.user_data['property_name']}\n\nShare this with your guests for instant concierge access."
    )
    
    logger.info(f"Onboarding Bot: Property registered successfully for user {user_id}")
    
    return ConversationHandler.END

async def onboarding_manage_properties(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show property management options"""
    
    user_id = update.effective_user.id
    
    if user_id not in host_properties or not host_properties[user_id]:
        await update.message.reply_text("You don't have any properties yet. Use /register_property to add one.")
        return ConversationHandler.END
    
    properties = host_properties[user_id]
    
    message = "📊 **Your Properties:**\n\n"
    for prop_id, prop_data in properties.items():
        message += f"🏠 **{prop_data['name']}**\n"
        message += f"   ID: `{prop_id}`\n"
        message += f"   Capacity: {prop_data['capacity']} guests\n"
        message += f"   Created: {prop_data['created_at'][:10]}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("Add Property", callback_data="add_property")],
        [InlineKeyboardButton("Modify Property", callback_data="modify_property")],
        [InlineKeyboardButton("Remove Property", callback_data="remove_property")],
        [InlineKeyboardButton("Done", callback_data="done")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message + "\nWhat would you like to do?", reply_markup=reply_markup, parse_mode="Markdown")
    
    return MANAGE_PROPERTIES

async def onboarding_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show pricing tiers"""
    
    message = """💳 **LEAH Membership Tiers**

🏆 **Essential Membership**
   • Enrollment: $100 (one-time)
   • Monthly: $50
   • Properties: Up to 3
   • Features:
     - Basic concierge services
     - Guest support
     - Property management dashboard
     - Monthly reporting
   
   Perfect for boutique property owners managing 1-3 luxury properties.

---

🌟 **Premium Membership**
   • Enrollment: $300 (one-time)
   • Monthly: $150
   • Properties: Up to 10
   • Features:
     - Enhanced concierge services
     - Priority guest support
     - Advanced analytics
     - Custom branding
     - Dedicated account manager
     - Weekly reporting
   
   Ideal for established hospitality businesses with 4-10 properties.

---

💎 **Enterprise Partnership**
   • Enrollment: Custom
   • Monthly: Custom
   • Properties: Unlimited
   • Features:
     - White-label solutions
     - 24/7 premium support
     - Custom integrations
     - Dedicated infrastructure
     - Strategic consulting
     - Real-time analytics
   
   Tailored solutions for large-scale hospitality portfolios.
   
   **Schedule a consultation for custom pricing and features.**

---

Questions about our tiers? I'm here to help!"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Pricing shown to {update.effective_user.id}")

async def onboarding_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    
    help_text = """📚 **How I Can Assist You**

I am your dedicated property management assistant, available to guide you through every step of onboarding and management.

**Getting Started:**
/register_property — Add a new property to your account
/manage_properties — View and manage your existing properties
/pricing — View our membership tiers and pricing

**Account Management:**
/account_status — View your account and membership information
/modify_property — Update property details, amenities, or rules
/remove_property — Remove a property from your account

**Additional Help:**
/help — Show this help message
/support — Contact our support team

**Key Features:**
✓ Property registration and setup
✓ Amenities and house rules configuration
✓ Membership tier management
✓ QR code generation for guest concierge access
✓ Property modification and management
✓ Account status and reporting

I'm here to ensure your property management experience is seamless and professional. Please don't hesitate to ask any questions!"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Help shown to {update.effective_user.id}")

async def onboarding_account_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show account status"""
    
    user_id = update.effective_user.id
    
    if user_id not in host_memberships:
        await update.message.reply_text("You don't have an active account. Use /register_property to get started.")
        return
    
    membership = host_memberships[user_id]
    properties = host_properties.get(user_id, {})
    tier_info = PRICING_TIERS[membership['tier']]
    
    message = f"""👤 **Your Account Status**

💳 **Membership:** {membership['tier_name']}
📅 **Created:** {membership['created_at'][:10]}

📊 **Properties:**
   • Active: {len(properties)}
   • Limit: {tier_info['properties']}
   • Available: {tier_info['properties'] - len(properties) if isinstance(tier_info['properties'], int) else '∞'}

💰 **Pricing:**
   • Enrollment: ${tier_info['enrollment_fee']}
   • Monthly: ${tier_info['monthly_fee']}

🎯 **Next Steps:**
   • /manage_properties — Manage your properties
   • /pricing — View other membership tiers
   • /support — Contact support

Is there anything else I can help you with?"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Onboarding Bot: Account status shown to {user_id}")

async def onboarding_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel operation"""
    
    await update.message.reply_text("Operation cancelled. How else may I assist you?")
    return ConversationHandler.END

# ============================================================================
# MAIN APPLICATION
# ============================================================================

async def main_onboarding_bot() -> None:
    """Start Onboarding Bot"""
    
    logger.info("=" * 70)
    logger.info("🚀 LEAH ONBOARDING ASSISTANT BOT — STARTING")
    logger.info("=" * 70)
    
    app = Application.builder().token(ONBOARDING_BOT_TOKEN).build()
    
    # Conversation handler for property registration
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", onboarding_start),
            CommandHandler("register_property", onboarding_register_property),
        ],
        states={
            PROPERTY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_property_name)],
            GUEST_CAPACITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_guest_capacity)],
            AMENITIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_amenities)],
            HOUSE_RULES: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_house_rules)],
            MEMBERSHIP_TIER: [],
        },
        fallbacks=[CommandHandler("cancel", onboarding_cancel)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("manage_properties", onboarding_manage_properties))
    app.add_handler(CommandHandler("pricing", onboarding_pricing))
    app.add_handler(CommandHandler("account_status", onboarding_account_status))
    app.add_handler(CommandHandler("help", onboarding_help))
    
    logger.info("✅ Onboarding Bot initialized")
    logger.info(f"📱 Handle: {ONBOARDING_BOT_CONFIG['handle']}")
    logger.info("🛡️ Scope Enforcement: ACTIVE")
    logger.info("=" * 70)
    
    async with app:
        await app.initialize()
        await app.start()
        logger.info("✅ Onboarding Bot started successfully")
        
        # Keep running
        await asyncio.Event().wait()

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main_onboarding_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Onboarding Bot shutting down...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
