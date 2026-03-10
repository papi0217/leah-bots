"""
onboarding_bot_v2.py — Ultra-simplified client onboarding for SOLUTIONa4U
Hosts can set up their property in 5 minutes with zero technical knowledge.
"""

import logging
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes

from config import ONBOARDING_BOT_TOKEN, OWNER_TELEGRAM_ID, GROQ_API_KEY
from storage import (
    get_or_create_host, update_host, get_or_create_onboarding, update_onboarding,
    get_onboarding, create_property, get_host_properties, init_db
)
from language import detect_language, get_translation
from state import OnboardingState

log = logging.getLogger(__name__)

# ─── ONBOARDING STATES ───────────────────────────────────────────────────────

WELCOME, LANGUAGE, PROPERTY_NAME, CITY, CHECKIN, CHECKOUT, WIFI_SSID, WIFI_PASS, RULES, EMERGENCY, REVIEW, PAYMENT = range(12)

# ─── TRANSLATIONS ────────────────────────────────────────────────────────────

STRINGS = {
    "en": {
        "welcome": "🏠 Welcome to SOLUTIONa4U!\n\nI'm Leah, your AI concierge assistant. I'll help you set up your property in just 5 minutes.\n\nLet's start! What language do you prefer?",
        "language_selected": "Perfect! Let's set up your property.",
        "property_name_prompt": "What's the name of your property?\n\n(Example: Beachfront Villa, Downtown Loft, Family Getaway)",
        "city_prompt": "What city/region is your property in?\n\n(Example: Naples, Miami, New York)",
        "checkin_prompt": "What time do guests check in?\n\n(Example: 3:00 PM or 15:00)",
        "checkout_prompt": "What time do guests check out?\n\n(Example: 11:00 AM or 11:00)",
        "wifi_ssid_prompt": "What's your WiFi network name (SSID)?\n\n(Or skip with /skip)",
        "wifi_pass_prompt": "What's your WiFi password?\n\n(Or skip with /skip)",
        "rules_prompt": "What are your house rules?\n\n(Example: No smoking, quiet hours after 10 PM, max 2 guests per bedroom)\n\nOr skip with /skip",
        "emergency_prompt": "What's your emergency contact number?\n\n(Example: +1-555-123-4567)\n\nOr skip with /skip",
        "review_prompt": "Perfect! Here's your setup:\n\n{summary}\n\nDoes everything look correct?",
        "payment_prompt": "Great! Your property is ready.\n\n💰 Setup fee: $60 (one-time)\n📅 Then: $12/month per property\n\nClick below to complete payment via PayPal.",
        "success": "🎉 Congratulations!\n\nYour property is now live with Leah AI Concierge.\n\n✅ Guests can find you at @naples_luxury_guest_bot\n✅ You'll receive alerts for all guest requests\n✅ Your first 7 days are on trial\n\nWelcome to the SOLUTIONa4U family!",
        "error": "❌ Something went wrong. Please try again or contact support@solutiona4u.com",
    },
    "es": {
        "welcome": "🏠 ¡Bienvenido a SOLUTIONa4U!\n\nSoy Leah, tu asistente de conserje de IA. Te ayudaré a configurar tu propiedad en solo 5 minutos.\n\n¡Comencemos! ¿Qué idioma prefieres?",
        "language_selected": "¡Perfecto! Configuremos tu propiedad.",
        "property_name_prompt": "¿Cuál es el nombre de tu propiedad?\n\n(Ejemplo: Villa Frente al Mar, Loft del Centro, Casa Familiar)",
        "city_prompt": "¿En qué ciudad/región está tu propiedad?\n\n(Ejemplo: Nápoles, Miami, Nueva York)",
        "checkin_prompt": "¿A qué hora entran los huéspedes?\n\n(Ejemplo: 3:00 PM o 15:00)",
        "checkout_prompt": "¿A qué hora salen los huéspedes?\n\n(Ejemplo: 11:00 AM o 11:00)",
        "wifi_ssid_prompt": "¿Cuál es el nombre de tu red WiFi (SSID)?\n\n(O salta con /skip)",
        "wifi_pass_prompt": "¿Cuál es tu contraseña de WiFi?\n\n(O salta con /skip)",
        "rules_prompt": "¿Cuáles son tus reglas de la casa?\n\n(Ejemplo: No fumar, horas tranquilas después de las 10 PM, máx 2 huéspedes por habitación)\n\nO salta con /skip",
        "emergency_prompt": "¿Cuál es tu número de contacto de emergencia?\n\n(Ejemplo: +1-555-123-4567)\n\nO salta con /skip",
        "review_prompt": "¡Perfecto! Aquí está tu configuración:\n\n{summary}\n\n¿Todo se ve correcto?",
        "payment_prompt": "¡Excelente! Tu propiedad está lista.\n\n💰 Tarifa de configuración: $60 (única vez)\n📅 Luego: $12/mes por propiedad\n\nHaz clic a continuación para completar el pago a través de PayPal.",
        "success": "🎉 ¡Felicitaciones!\n\nTu propiedad ahora está en vivo con Leah AI Concierge.\n\n✅ Los huéspedes pueden encontrarte en @naples_luxury_guest_bot\n✅ Recibirás alertas para todas las solicitudes de huéspedes\n✅ Tus primeros 7 días están en prueba\n\n¡Bienvenido a la familia SOLUTIONa4U!",
        "error": "❌ Algo salió mal. Por favor, inténtalo de nuevo o contacta a support@solutiona4u.com",
    }
}

def t(lang: str, key: str, **kwargs) -> str:
    """Get translated string."""
    text = STRINGS.get(lang, STRINGS["en"]).get(key, key)
    return text.format(**kwargs) if kwargs else text

# ─── HANDLERS ────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start onboarding."""
    user_id = update.effective_user.id
    lang = detect_language(update.message.text if update.message else "")
    
    # Create host record
    get_or_create_host(user_id)
    get_or_create_onboarding(user_id)
    update_onboarding(user_id, language=lang)
    
    # Language selection buttons
    keyboard = [
        [InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("Español", callback_data="lang_es")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(t(lang, "welcome"), reply_markup=reply_markup)
    return LANGUAGE

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle language selection."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = "en" if "en" in query.data else "es"
    
    update_onboarding(user_id, language=lang)
    
    await query.edit_message_text(t(lang, "language_selected"))
    await query.message.reply_text(t(lang, "property_name_prompt"))
    
    return PROPERTY_NAME

async def property_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get property name."""
    user_id = update.effective_user.id
    ob = get_onboarding(user_id)
    lang = ob["language"]
    
    property_name = update.message.text.strip()
    update_onboarding(user_id, data_update={"property_name": property_name})
    
    await update.message.reply_text(t(lang, "city_prompt"))
    return CITY

async def city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get city."""
    user_id = update.effective_user.id
    ob = get_onboarding(user_id)
    lang = ob["language"]
    
    city = update.message.text.strip()
    update_onboarding(user_id, data_update={"city": city})
    
    await update.message.reply_text(t(lang, "checkin_prompt"))
    return CHECKIN

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get check-in time."""
    user_id = update.effective_user.id
    ob = get_onboarding(user_id)
    lang = ob["language"]
    
    checkin = update.message.text.strip()
    update_onboarding(user_id, data_update={"checkin_time": checkin})
    
    await update.message.reply_text(t(lang, "checkout_prompt"))
    return CHECKOUT

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get check-out time."""
    user_id = update.effective_user.id
    ob = get_onboarding(user_id)
    lang = ob["language"]
    
    checkout = update.message.text.strip()
    update_onboarding(user_id, data_update={"checkout_time": checkout})
    
    await update.message.reply_text(t(lang, "wifi_ssid_prompt"))
    return WIFI_SSID

async def wifi_ssid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get WiFi SSID."""
    user_id = update.effective_user.id
    ob = get_onboarding(user_id)
    lang = ob["language"]
    
    wifi_ssid = update.message.text.strip() if update.message.text.lower() != "/skip" else ""
    update_onboarding(user_id, data_update={"wifi_ssid": wifi_ssid})
    
    await update.message.reply_text(t(lang, "wifi_pass_prompt"))
    return WIFI_PASS

async def wifi_pass(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get WiFi password."""
    user_id = update.effective_user.id
    ob = get_onboarding(user_id)
    lang = ob["language"]
    
    wifi_pass = update.message.text.strip() if update.message.text.lower() != "/skip" else ""
    update_onboarding(user_id, data_update={"wifi_pass": wifi_pass})
    
    await update.message.reply_text(t(lang, "rules_prompt"))
    return RULES

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get house rules."""
    user_id = update.effective_user.id
    ob = get_onboarding(user_id)
    lang = ob["language"]
    
    rules = update.message.text.strip() if update.message.text.lower() != "/skip" else ""
    update_onboarding(user_id, data_update={"house_rules": rules})
    
    await update.message.reply_text(t(lang, "emergency_prompt"))
    return EMERGENCY

async def emergency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get emergency contact."""
    user_id = update.effective_user.id
    ob = get_onboarding(user_id)
    lang = ob["language"]
    
    emergency = update.message.text.strip() if update.message.text.lower() != "/skip" else ""
    update_onboarding(user_id, data_update={"emergency_contact": emergency})
    
    # Build summary
    data = ob["data"]
    summary = f"""
📍 Property: {data.get('property_name', 'N/A')}
🏙️ City: {data.get('city', 'N/A')}
🔑 Check-in: {data.get('checkin_time', 'N/A')}
🔓 Check-out: {data.get('checkout_time', 'N/A')}
📶 WiFi: {data.get('wifi_ssid', 'Not provided')}
📋 Rules: {data.get('house_rules', 'Not provided')}
🚨 Emergency: {data.get('emergency_contact', 'Not provided')}
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, looks good!", callback_data="confirm_yes")],
        [InlineKeyboardButton("❌ Let me edit", callback_data="confirm_no")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(t(lang, "review_prompt", summary=summary), reply_markup=reply_markup)
    return REVIEW

async def review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Review and confirm setup."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    ob = get_onboarding(user_id)
    lang = ob["language"]
    
    if "yes" in query.data:
        # Create property in database
        host = get_or_create_host(user_id)
        data = ob["data"]
        
        prop_id = create_property(
            host["host_id"],
            property_name=data.get("property_name", "Unnamed"),
            city=data.get("city", "Unknown"),
            checkin_time=data.get("checkin_time", ""),
            checkout_time=data.get("checkout_time", ""),
            wifi_ssid=data.get("wifi_ssid", ""),
            wifi_pass=data.get("wifi_pass", ""),
            house_rules=data.get("house_rules", ""),
            emergency=data.get("emergency_contact", ""),
        )
        
        # Forward to owner
        owner_msg = f"""
🎉 NEW PROPERTY REGISTERED

Host: {host['name'] or 'Unknown'} (ID: {user_id})
Property: {data.get('property_name')}
City: {data.get('city')}
Check-in: {data.get('checkin_time')}
Check-out: {data.get('checkout_time')}

Property ID: {prop_id}
Registered: {datetime.utcnow().isoformat()}
"""
        try:
            await context.bot.send_message(OWNER_TELEGRAM_ID, owner_msg)
        except Exception as e:
            log.error(f"Failed to notify owner: {e}")
        
        await query.edit_message_text(t(lang, "payment_prompt"))
        
        # Payment button
        keyboard = [
            [InlineKeyboardButton("💳 Pay $60 via PayPal", url="https://www.paypal.com/")],
            [InlineKeyboardButton("✅ I've paid, activate my property", callback_data="payment_done")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("", reply_markup=reply_markup)
        
        return PAYMENT
    else:
        await query.edit_message_text(t(lang, "property_name_prompt"))
        return PROPERTY_NAME

async def payment_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Complete setup after payment."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    ob = get_onboarding(user_id)
    lang = ob["language"]
    
    # Activate trial
    host = get_or_create_host(user_id)
    update_host(user_id, status="trial")
    
    await query.edit_message_text(t(lang, "success"))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel onboarding."""
    await update.message.reply_text("Onboarding cancelled. Type /start to begin again.")
    return ConversationHandler.END

# ─── MAIN ────────────────────────────────────────────────────────────────────

def build_onboarding_app() -> Application:
    """Build the onboarding bot application."""
    app = Application.builder().token(ONBOARDING_BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [CallbackQueryHandler(language_selected)],
            PROPERTY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, property_name)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
            CHECKIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkin)],
            CHECKOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout)],
            WIFI_SSID: [MessageHandler(filters.TEXT & ~filters.COMMAND, wifi_ssid)],
            WIFI_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, wifi_pass)],
            RULES: [MessageHandler(filters.TEXT & ~filters.COMMAND, rules)],
            EMERGENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, emergency)],
            REVIEW: [CallbackQueryHandler(review)],
            PAYMENT: [CallbackQueryHandler(payment_done)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    return app

if __name__ == "__main__":
    init_db()
    app = build_onboarding_app()
    app.run_polling()
