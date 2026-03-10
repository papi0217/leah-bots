"""
onboarding_bot.py — Host onboarding bot for SolutionA4U Leah AI Concierge Platform.
Token: @property_onboarding_bot
Handles 20-step host setup, file uploads, and forwards all data to the platform owner.
"""

import asyncio
import json
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from telegram.constants import ParseMode

from config import ONBOARDING_BOT_TOKEN, OWNER_TELEGRAM_ID, SETUP_FEE, MONTHLY_FEE, TRIAL_DAYS, BRAND_NAME, PLATFORM_NAME
from storage import (
    init_db, get_or_create_host, update_host, get_or_create_onboarding,
    update_onboarding, get_onboarding, reset_onboarding,
    create_property, get_host, update_host_by_id, activate_trial, log_payment
)
from escalation import notify_owner_new_onboarding
from services.file_processor import save_telegram_file, extract_text, extract_keywords
from storage import save_kb_file, get_host_properties
from ai_engine import generate_city_context
from rate_limit import is_allowed

log = logging.getLogger(__name__)

# ─── Step Definitions ─────────────────────────────────────────────────────────

STEPS = [
    "language", "host_name", "business_name", "property_name",
    "city", "state_region", "country", "address",
    "concierge_name", "wifi_ssid", "wifi_pass",
    "checkin_time", "checkout_time", "keypad_code",
    "max_guests", "amenities", "house_rules",
    "emergency_contact", "telegram_group", "upload_files",
    "confirm", "complete",
]

PROMPTS_EN = {
    "language": "🌍 *Welcome to {brand}!*\n\nI'm going to help you set up your AI concierge in just a few minutes.\n\nFirst — what language would you prefer?\n\n[🇺🇸 English] [🇪🇸 Español]",
    "host_name": "Wonderful! Let's get started. 😊\n\nWhat's your name? (First and last name)",
    "business_name": "Great to meet you, *{host_name}*! 🌟\n\nWhat's the name of your business or company? (Or just your name if you're an individual host)",
    "property_name": "Perfect! Now, what's the name of your property?\n\n_(e.g., 'Beachfront Paradise Villa', 'Downtown Loft', 'Casa del Sol')_",
    "city": "Beautiful name! 🏠\n\nWhat city is your property located in?\n\n_(e.g., Naples, Miami, New York, Cancún, Barcelona)_",
    "state_region": "And what state, province, or region?\n\n_(e.g., Florida, New York, Quintana Roo — or type 'N/A' if not applicable)_",
    "country": "What country?\n\n_(e.g., USA, Mexico, Spain, Colombia)_",
    "address": "What's the full street address of your property?\n\n_(This helps guests find you and allows Leah to give accurate local recommendations)_",
    "concierge_name": "Now the fun part! 🎉\n\nWhat would you like to name your AI concierge?\n\n_(Default is 'Leah' — but you can choose any name that fits your brand, like 'Sofia', 'Marco', 'Aria', etc.)_",
    "wifi_ssid": "Great choice! Now let's set up the essentials your guests will need.\n\n📶 What's your WiFi network name (SSID)?",
    "wifi_pass": "And the WiFi password?",
    "checkin_time": "⏰ What time is check-in?\n\n_(e.g., 3:00 PM, 15:00)_",
    "checkout_time": "And check-out time?\n\n_(e.g., 11:00 AM, 11:00)_",
    "keypad_code": "🔑 What's the keypad/door code for your property?\n\n_(Type 'N/A' if you use a lockbox or smart lock with a different system)_",
    "max_guests": "👥 What's the maximum number of guests allowed?",
    "amenities": "🏊 What amenities does your property offer?\n\n_(List them separated by commas, e.g.: Pool, Beach Access, Full Kitchen, BBQ Grill, Gym, Parking)_",
    "house_rules": "📋 What are your house rules?\n\n_(List them separated by commas, e.g.: No smoking, Quiet hours 10 PM–8 AM, No parties, Pets not allowed)_",
    "emergency_contact": "🚨 What's the emergency contact phone number for your property?\n\n_(This is shared with guests only in genuine emergencies)_",
    "telegram_group": "Almost done! 🎉\n\nTo receive guest alerts, please:\n1. Create a private Telegram group (e.g., 'Leah Alerts - {property_name}')\n2. Add me (@property_onboarding_bot) to the group\n3. Send me the group's chat ID or just type *DONE* and I'll find it\n\n_(You'll receive CRITICAL alerts, issue reports, service requests, and 5-star review notifications here)_",
    "upload_files": "🗂️ *Knowledge Base Upload*\n\nNow you can upload files to make your concierge truly personalized:\n\n📄 House Rules (PDF, TXT, DOCX)\n📄 Amenities Guide\n📄 Local Recommendations\n📄 FAQ\n📄 Emergency Procedures\n📄 House Manual\n\nUpload as many files as you like, then type *DONE* when finished.\n\n_(You can also add more files later at any time)_",
    "confirm": "✨ *Almost ready!*\n\nHere's a summary of your setup:\n\n{summary}\n\nLooks good? Type *CONFIRM* to activate your 7-day free trial, or *EDIT* to make changes.",
    "complete": "🎉 *Welcome to {brand}, {host_name}!*\n\nYour AI concierge *{concierge_name}* is now active and ready to serve your guests!\n\n✅ 7-day FREE trial activated\n✅ Knowledge base configured\n✅ Host alerts connected\n\n*Your trial ends in {trial_days} days.* After that, it's just ${monthly_fee}/month.\n\nShare this link with your guests:\n`https://t.me/naples_luxury_guest_bot?start=property_{property_id}`\n\nNeed help? Just message me anytime. Welcome to the family! 🌟",
}

PROMPTS_ES = {
    "language": "🌍 *¡Bienvenido/a a {brand}!*\n\nTe ayudaré a configurar tu conserje de IA en solo unos minutos.\n\nPrimero — ¿qué idioma prefieres?\n\n[🇺🇸 English] [🇪🇸 Español]",
    "host_name": "¡Perfecto! Comencemos. 😊\n\n¿Cuál es tu nombre? (Nombre y apellido)",
    "business_name": "¡Un placer conocerte, *{host_name}*! 🌟\n\n¿Cuál es el nombre de tu negocio o empresa? (O simplemente tu nombre si eres anfitrión individual)",
    "property_name": "¡Perfecto! Ahora, ¿cuál es el nombre de tu propiedad?\n\n_(ej: 'Villa Paraíso Frente al Mar', 'Loft del Centro', 'Casa del Sol')_",
    "city": "¡Qué bonito nombre! 🏠\n\n¿En qué ciudad está ubicada tu propiedad?\n\n_(ej: Naples, Miami, Cancún, Barcelona, Bogotá)_",
    "state_region": "¿Y en qué estado, provincia o región?\n\n_(ej: Florida, Quintana Roo, Cataluña — o escribe 'N/A' si no aplica)_",
    "country": "¿En qué país?\n\n_(ej: USA, México, España, Colombia)_",
    "address": "¿Cuál es la dirección completa de tu propiedad?\n\n_(Esto ayuda a los huéspedes a encontrarte y permite a Leah dar recomendaciones locales precisas)_",
    "concierge_name": "¡Ahora la parte divertida! 🎉\n\n¿Cómo te gustaría llamar a tu conserje de IA?\n\n_(El nombre predeterminado es 'Leah' — pero puedes elegir cualquier nombre que se adapte a tu marca, como 'Sofía', 'Marco', 'Aria', etc.)_",
    "wifi_ssid": "¡Excelente elección! Ahora configuremos lo esencial que necesitarán tus huéspedes.\n\n📶 ¿Cuál es el nombre de tu red WiFi (SSID)?",
    "wifi_pass": "¿Y la contraseña del WiFi?",
    "checkin_time": "⏰ ¿A qué hora es el check-in?\n\n_(ej: 3:00 PM, 15:00)_",
    "checkout_time": "¿Y la hora de check-out?\n\n_(ej: 11:00 AM, 11:00)_",
    "keypad_code": "🔑 ¿Cuál es el código del teclado/puerta de tu propiedad?\n\n_(Escribe 'N/A' si usas una caja de llaves o cerradura inteligente con un sistema diferente)_",
    "max_guests": "👥 ¿Cuál es el número máximo de huéspedes permitidos?",
    "amenities": "🏊 ¿Qué comodidades ofrece tu propiedad?\n\n_(Enuméralas separadas por comas, ej: Piscina, Acceso a la Playa, Cocina Completa, Parrilla BBQ, Gimnasio, Estacionamiento)_",
    "house_rules": "📋 ¿Cuáles son las reglas de tu casa?\n\n_(Enuméralas separadas por comas, ej: No fumar, Silencio de 10 PM–8 AM, No fiestas, No se permiten mascotas)_",
    "emergency_contact": "🚨 ¿Cuál es el número de contacto de emergencia para tu propiedad?\n\n_(Se comparte con los huéspedes solo en emergencias genuinas)_",
    "telegram_group": "¡Casi listo! 🎉\n\nPara recibir alertas de huéspedes, por favor:\n1. Crea un grupo privado de Telegram (ej: 'Alertas Leah - {property_name}')\n2. Agrégame (@property_onboarding_bot) al grupo\n3. Envíame el ID del chat del grupo o simplemente escribe *LISTO*\n\n_(Recibirás alertas CRÍTICAS, reportes de problemas, solicitudes de servicio y notificaciones de reseñas de 5 estrellas aquí)_",
    "upload_files": "🗂️ *Carga de Base de Conocimientos*\n\nAhora puedes subir archivos para hacer tu conserje verdaderamente personalizado:\n\n📄 Reglas de la Casa (PDF, TXT, DOCX)\n📄 Guía de Comodidades\n📄 Recomendaciones Locales\n📄 Preguntas Frecuentes\n📄 Procedimientos de Emergencia\n📄 Manual de la Casa\n\nSube todos los archivos que quieras, luego escribe *LISTO* cuando termines.\n\n_(También puedes agregar más archivos en cualquier momento)_",
    "confirm": "✨ *¡Casi listo!*\n\nAquí hay un resumen de tu configuración:\n\n{summary}\n\n¿Todo bien? Escribe *CONFIRMAR* para activar tu prueba gratuita de 7 días, o *EDITAR* para hacer cambios.",
    "complete": "🎉 *¡Bienvenido/a a {brand}, {host_name}!*\n\nTu conserje de IA *{concierge_name}* ya está activo y listo para atender a tus huéspedes.\n\n✅ Prueba GRATUITA de 7 días activada\n✅ Base de conocimientos configurada\n✅ Alertas de anfitrión conectadas\n\n*Tu prueba termina en {trial_days} días.* Después, son solo ${monthly_fee}/mes.\n\nComparte este enlace con tus huéspedes:\n`https://t.me/naples_luxury_guest_bot?start=property_{property_id}`\n\n¿Necesitas ayuda? Solo escríbeme en cualquier momento. ¡Bienvenido/a a la familia! 🌟",
}


def get_prompt(step: str, lang: str, **kwargs) -> str:
    prompts = PROMPTS_ES if lang == "es" else PROMPTS_EN
    template = prompts.get(step, f"Please provide: {step}")
    try:
        return template.format(brand=BRAND_NAME, trial_days=TRIAL_DAYS, monthly_fee=MONTHLY_FEE, **kwargs)
    except (KeyError, ValueError):
        return template


def build_summary(data: dict, lang: str) -> str:
    fields = [
        ("host_name", "Host Name" if lang == "en" else "Nombre del Anfitrión"),
        ("business_name", "Business" if lang == "en" else "Negocio"),
        ("property_name", "Property" if lang == "en" else "Propiedad"),
        ("city", "City" if lang == "en" else "Ciudad"),
        ("country", "Country" if lang == "en" else "País"),
        ("address", "Address" if lang == "en" else "Dirección"),
        ("concierge_name", "Concierge Name" if lang == "en" else "Nombre del Conserje"),
        ("wifi_ssid", "WiFi Network" if lang == "en" else "Red WiFi"),
        ("checkin_time", "Check-in" if lang == "en" else "Check-in"),
        ("checkout_time", "Check-out" if lang == "en" else "Check-out"),
        ("max_guests", "Max Guests" if lang == "en" else "Máx. Huéspedes"),
        ("emergency_contact", "Emergency" if lang == "en" else "Emergencia"),
    ]
    lines = []
    for key, label in fields:
        val = data.get(key, "—")
        lines.append(f"• *{label}:* {val}")
    return "\n".join(lines)


# ─── Handlers ─────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        return
    get_or_create_host(user.id)
    reset_onboarding(user.id)
    update_onboarding(user.id, state="language")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
         InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")]
    ])
    await update.message.reply_text(
        get_prompt("language", "en"),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


async def callback_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = "es" if query.data == "lang_es" else "en"
    update_onboarding(user.id, state="host_name", language=lang)
    await query.edit_message_text(
        get_prompt("host_name", lang),
        parse_mode=ParseMode.MARKDOWN,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        return

    ob = get_onboarding(user.id)
    if not ob:
        await cmd_start(update, context)
        return

    lang = ob.get("language", "en")
    state = ob.get("state", "start")
    data = ob.get("data", {})
    text = update.message.text.strip() if update.message.text else ""

    # ── File upload during upload_files step ──
    if state == "upload_files" and update.message.document:
        await _handle_file_upload(update, context, ob, data, lang)
        return

    if state == "upload_files" and update.message.photo:
        await _handle_photo_upload(update, context, ob, data, lang)
        return

    # ── Text input routing ──
    step_handlers = {
        "host_name":         _step_host_name,
        "business_name":     _step_business_name,
        "property_name":     _step_property_name,
        "city":              _step_city,
        "state_region":      _step_state_region,
        "country":           _step_country,
        "address":           _step_address,
        "concierge_name":    _step_concierge_name,
        "wifi_ssid":         _step_wifi_ssid,
        "wifi_pass":         _step_wifi_pass,
        "checkin_time":      _step_checkin,
        "checkout_time":     _step_checkout,
        "keypad_code":       _step_keypad,
        "max_guests":        _step_max_guests,
        "amenities":         _step_amenities,
        "house_rules":       _step_house_rules,
        "emergency_contact": _step_emergency,
        "telegram_group":    _step_telegram_group,
        "upload_files":      _step_upload_done,
        "confirm":           _step_confirm,
    }

    handler = step_handlers.get(state)
    if handler:
        await handler(update, context, ob, data, lang, text)
    else:
        await update.message.reply_text(
            "Please type /start to begin the setup." if lang == "en" else "Por favor escribe /start para comenzar la configuración."
        )


# ─── Step Handlers ────────────────────────────────────────────────────────────

async def _step_host_name(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="business_name", data_update={"host_name": text})
    update_host(update.effective_user.id, name=text, language=lang)
    await update.message.reply_text(get_prompt("business_name", lang, host_name=text), parse_mode=ParseMode.MARKDOWN)


async def _step_business_name(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="property_name", data_update={"business_name": text})
    await update.message.reply_text(get_prompt("property_name", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_property_name(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="city", data_update={"property_name": text})
    await update.message.reply_text(get_prompt("city", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_city(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="state_region", data_update={"city": text})
    await update.message.reply_text(get_prompt("state_region", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_state_region(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="country", data_update={"state_region": text})
    await update.message.reply_text(get_prompt("country", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_country(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="address", data_update={"country": text})
    await update.message.reply_text(get_prompt("address", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_address(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="concierge_name", data_update={"address": text})
    await update.message.reply_text(get_prompt("concierge_name", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_concierge_name(update, context, ob, data, lang, text):
    name = text if text.strip() else "Leah"
    update_onboarding(update.effective_user.id, state="wifi_ssid", data_update={"concierge_name": name})
    await update.message.reply_text(get_prompt("wifi_ssid", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_wifi_ssid(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="wifi_pass", data_update={"wifi_ssid": text})
    await update.message.reply_text(get_prompt("wifi_pass", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_wifi_pass(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="checkin_time", data_update={"wifi_pass": text})
    await update.message.reply_text(get_prompt("checkin_time", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_checkin(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="checkout_time", data_update={"checkin_time": text})
    await update.message.reply_text(get_prompt("checkout_time", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_checkout(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="keypad_code", data_update={"checkout_time": text})
    await update.message.reply_text(get_prompt("keypad_code", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_keypad(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="max_guests", data_update={"keypad_code": text})
    await update.message.reply_text(get_prompt("max_guests", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_max_guests(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="amenities", data_update={"max_guests": text})
    await update.message.reply_text(get_prompt("amenities", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_amenities(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="house_rules", data_update={"amenities": text})
    await update.message.reply_text(get_prompt("house_rules", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_house_rules(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="emergency_contact", data_update={"house_rules": text})
    await update.message.reply_text(get_prompt("emergency_contact", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_emergency(update, context, ob, data, lang, text):
    update_onboarding(update.effective_user.id, state="telegram_group", data_update={"emergency_contact": text})
    prop_name = data.get("property_name", "your property")
    await update.message.reply_text(
        get_prompt("telegram_group", lang, property_name=prop_name),
        parse_mode=ParseMode.MARKDOWN
    )


async def _step_telegram_group(update, context, ob, data, lang, text):
    group_id = text if text.upper() not in ("DONE", "LISTO") else ""
    update_onboarding(update.effective_user.id, state="upload_files", data_update={"telegram_group": group_id})
    await update.message.reply_text(get_prompt("upload_files", lang), parse_mode=ParseMode.MARKDOWN)


async def _step_upload_done(update, context, ob, data, lang, text):
    if text.upper() in ("DONE", "LISTO", "SKIP", "OMITIR"):
        # Refresh data
        ob = get_onboarding(update.effective_user.id)
        data = ob["data"]
        summary = build_summary(data, lang)
        update_onboarding(update.effective_user.id, state="confirm")
        await update.message.reply_text(
            get_prompt("confirm", lang, summary=summary),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        msg = "Please upload a file or type DONE to continue." if lang == "en" else "Por favor sube un archivo o escribe LISTO para continuar."
        await update.message.reply_text(msg)


async def _handle_file_upload(update, context, ob, data, lang, *args):
    doc = update.message.document
    user = update.effective_user
    msg = "⏳ Processing your file..." if lang == "en" else "⏳ Procesando tu archivo..."
    await update.message.reply_text(msg)

    # We need a property_id — create a temp one or use 0
    host = get_or_create_host(user.id)
    props = get_host_properties(host["host_id"])
    property_id = props[0]["property_id"] if props else 0

    local_path = await save_telegram_file(context.bot, doc.file_id, doc.file_name)
    if not local_path:
        err = "❌ Unsupported file type. Please upload PDF, TXT, DOCX, or image files." if lang == "en" else "❌ Tipo de archivo no compatible. Por favor sube archivos PDF, TXT, DOCX o imágenes."
        await update.message.reply_text(err)
        return

    content = extract_text(local_path)
    keywords = extract_keywords(content) if content else ""
    file_type = _guess_file_type(doc.file_name)
    save_kb_file(property_id, file_type, doc.file_name, content, local_path, keywords)

    ok = "✅ *{name}* uploaded and added to your knowledge base!\n\nUpload more files or type DONE to continue." if lang == "en" else "✅ *{name}* subido y agregado a tu base de conocimientos!\n\nSube más archivos o escribe LISTO para continuar."
    await update.message.reply_text(ok.format(name=doc.file_name), parse_mode=ParseMode.MARKDOWN)


async def _handle_photo_upload(update, context, ob, data, lang, *args):
    photo = update.message.photo[-1]
    user = update.effective_user
    msg = "⏳ Processing your image..." if lang == "en" else "⏳ Procesando tu imagen..."
    await update.message.reply_text(msg)

    host = get_or_create_host(user.id)
    props = get_host_properties(host["host_id"])
    property_id = props[0]["property_id"] if props else 0

    local_path = await save_telegram_file(context.bot, photo.file_id, f"photo_{photo.file_id}.jpg")
    if not local_path:
        return

    content = extract_text(local_path)
    keywords = extract_keywords(content) if content else ""
    save_kb_file(property_id, "image_document", f"photo_{photo.file_id}.jpg", content, local_path, keywords)

    ok = "✅ Image uploaded and processed!\n\nUpload more files or type DONE to continue." if lang == "en" else "✅ ¡Imagen subida y procesada!\n\nSube más archivos o escribe LISTO para continuar."
    await update.message.reply_text(ok)


async def _step_confirm(update, context, ob, data, lang, text):
    upper = text.upper()
    if upper in ("CONFIRM", "CONFIRMAR"):
        await _complete_onboarding(update, context, ob, data, lang)
    elif upper in ("EDIT", "EDITAR"):
        msg = "No problem! Type /start to restart the setup from the beginning." if lang == "en" else "¡Sin problema! Escribe /start para reiniciar la configuración desde el principio."
        await update.message.reply_text(msg)
    else:
        msg = "Please type CONFIRM to activate or EDIT to make changes." if lang == "en" else "Por favor escribe CONFIRMAR para activar o EDITAR para hacer cambios."
        await update.message.reply_text(msg)


async def _complete_onboarding(update, context, ob, data, lang):
    user = update.effective_user
    host = get_or_create_host(user.id)
    host_id = host["host_id"]

    # Create property record
    property_id = create_property(
        host_id=host_id,
        property_name=data.get("property_name", "My Property"),
        city=data.get("city", ""),
        state_region=data.get("state_region", ""),
        country=data.get("country", "USA"),
        address=data.get("address", ""),
        concierge_name=data.get("concierge_name", "Leah"),
        wifi_ssid=data.get("wifi_ssid", ""),
        wifi_pass=data.get("wifi_pass", ""),
        checkin_time=data.get("checkin_time", "3:00 PM"),
        checkout_time=data.get("checkout_time", "11:00 AM"),
        keypad_code=data.get("keypad_code", ""),
        max_guests=int(data.get("max_guests", 6)) if str(data.get("max_guests", "6")).isdigit() else 6,
        amenities=data.get("amenities", ""),
        house_rules=data.get("house_rules", ""),
        emergency=data.get("emergency_contact", ""),
        telegram_group=data.get("telegram_group", ""),
    )

    # Activate trial
    activate_trial(host_id)
    update_host(user.id, name=data.get("host_name", ""), status="trial")
    update_onboarding(user.id, state="complete")

    # Generate city context if not Naples
    city = data.get("city", "naples").lower()
    if "naples" not in city:
        await update.message.reply_text(
            "🌍 Generating local knowledge base for your city... this takes about 15 seconds." if lang == "en"
            else "🌍 Generando base de conocimientos local para tu ciudad... esto toma unos 15 segundos."
        )
        city_ctx = await generate_city_context(data.get("city", ""), data.get("country", ""), lang)
        if city_ctx:
            save_kb_file(property_id, "local_context", f"local_guide_{city}.txt", city_ctx, "", "")

    # Notify owner
    await notify_owner_new_onboarding(
        bot=context.bot,
        owner_id=OWNER_TELEGRAM_ID,
        host_name=data.get("host_name", user.first_name),
        host_tg_id=user.id,
        property_name=data.get("property_name", ""),
        city=data.get("city", ""),
        country=data.get("country", ""),
        data=data,
    )

    # Send completion message
    completion = get_prompt(
        "complete", lang,
        host_name=data.get("host_name", user.first_name),
        concierge_name=data.get("concierge_name", "Leah"),
        property_id=property_id,
    )
    await update.message.reply_text(completion, parse_mode=ParseMode.MARKDOWN)


def _guess_file_type(filename: str) -> str:
    name = filename.lower()
    if any(w in name for w in ["rule", "regla", "policy", "politic"]):
        return "house_rules"
    elif any(w in name for w in ["amenity", "ameniti", "comodidad", "facility"]):
        return "amenities"
    elif any(w in name for w in ["faq", "question", "pregunta", "frequent"]):
        return "faq"
    elif any(w in name for w in ["emergency", "emergencia", "safety", "seguridad"]):
        return "emergency_procedures"
    elif any(w in name for w in ["manual", "guide", "guia", "instruccion", "instruction"]):
        return "house_manual"
    elif any(w in name for w in ["restaurant", "local", "recommend", "recomiend", "food", "comida"]):
        return "local_recommendations"
    return "general"


# ─── Build Application ────────────────────────────────────────────────────────

def build_onboarding_app() -> Application:
    init_db()
    app = Application.builder().token(ONBOARDING_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(callback_language, pattern="^lang_"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    log.info("Onboarding bot built — @property_onboarding_bot")
    return app
