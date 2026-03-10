"""
demo_bot.py — SolutionA4U Demo Bot (@naples_luxury_guest_bot)
Full showcase of Leah AI Concierge features. Bilingual (EN/ES).
Demonstrates: restaurant recommendations, issue escalation, service requests,
review risk detection, property info, weather, and seamless trial onboarding handoff.
"""

import asyncio
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from telegram.constants import ParseMode

from config import (
    DEMO_BOT_TOKEN, DEMO_PROPERTIES, BRAND_NAME, PLATFORM_NAME,
    SETUP_FEE, MONTHLY_FEE, TRIAL_DAYS, STRINGS
)
from storage import init_db, get_or_create_guest_session, update_guest_session, get_guest_session, log_message, update_review_score, log_escalation
from rules import check_rules, classify_review_delta
from language import detect_language, t
from ai_engine import call_groq
from recommendations import get_recommendations, format_recommendations_list
from services.weather import get_weather
from escalation import send_host_alert
from rate_limit import is_allowed

log = logging.getLogger(__name__)

# ─── Demo Property Selector ───────────────────────────────────────────────────

def get_demo_property(prop_id: str = None) -> dict:
    if prop_id:
        for p in DEMO_PROPERTIES:
            if p["id"] == prop_id:
                return p
    return DEMO_PROPERTIES[0]


def get_demo_property_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    label = "🏠 Switch Property" if lang == "en" else "🏠 Cambiar Propiedad"
    buttons = []
    for p in DEMO_PROPERTIES:
        buttons.append([InlineKeyboardButton(p["name"], callback_data=f"prop_{p['id']}")])
    return InlineKeyboardMarkup(buttons)


# ─── Commands ─────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        return

    # Parse deep link for property
    args = context.args or []
    prop_id = None
    if args and args[0].startswith("property_"):
        prop_id = args[0].replace("property_", "demo_naples_villa")  # map to demo

    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")

    # Reset session for fresh demo
    update_guest_session(user.id, "demo", state="awaiting_name", guest_name=None, language=lang)

    await update.message.reply_text(
        t("welcome_demo", lang),
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")

    if lang == "es":
        text = (
            "🌟 *¿Qué puedo hacer por ti?*\n\n"
            "Soy Leah, tu conserje personal de IA. Aquí tienes lo que puedo hacer:\n\n"
            "🍽️ /restaurantes — Recomendaciones personalizadas\n"
            "🌤️ /clima — Clima actual\n"
            "🏠 /propiedad — Información de tu alojamiento\n"
            "🎭 /actividades — Qué hacer en la ciudad\n"
            "🚨 /emergencia — Contacto de emergencia\n"
            "🌍 /idioma — Cambiar idioma\n"
            "🏘️ /propiedades — Ver propiedades demo\n"
            "💼 /trial — Iniciar prueba gratuita de 7 días\n\n"
            "O simplemente escríbeme lo que necesitas. ¡Estoy aquí para ti! 😊"
        )
    else:
        text = (
            "🌟 *What can I do for you?*\n\n"
            "I'm Leah, your personal AI concierge. Here's what I can help with:\n\n"
            "🍽️ /restaurants — Personalized dining recommendations\n"
            "🌤️ /weather — Current weather conditions\n"
            "🏠 /property — Your accommodation info\n"
            "🎭 /activities — Things to do in the city\n"
            "🚨 /emergency — Emergency contact\n"
            "🌍 /language — Switch language\n"
            "🏘️ /properties — View demo properties\n"
            "💼 /trial — Start your 7-day free trial\n\n"
            "Or just tell me what you need — I'm here for you! 😊"
        )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_restaurants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        return
    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")
    name = session.get("guest_name") or (user.first_name or "")

    update_guest_session(user.id, "demo", state="awaiting_cuisine")
    await update.message.reply_text(
        t("recommend_ask_cuisine", lang, name=name),
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        return
    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")
    weather = await get_weather("Naples", "US", lang)
    await update.message.reply_text(weather, parse_mode=ParseMode.MARKDOWN)


async def cmd_property(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        return
    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")
    name = session.get("guest_name") or (user.first_name or "")
    prop = get_demo_property()

    await update.message.reply_text(
        t("checkin_info", lang,
          name=name or ("Guest" if lang == "en" else "Huésped"),
          address=prop["address"],
          keypad=prop["keypad"],
          checkin=prop["checkin"],
          wifi_ssid=prop["wifi_ssid"],
          wifi_pass=prop["wifi_pass"]),
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_activities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        return
    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")
    name = session.get("guest_name") or (user.first_name or "")

    if lang == "es":
        text = (
            f"🎭 *Actividades en Naples para ti, {name}!*\n\n"
            "🏖️ *Playa de Naples* — La playa más hermosa del Golfo, perfecta para el atardecer\n"
            "🛍️ *5th Avenue South* — Boutiques de lujo, galerías de arte y restaurantes finos\n"
            "🐬 *Crucero de delfines* — Avistamiento de delfines y manatíes (2 horas, $45/persona)\n"
            "🎨 *Galería de Arte de Naples* — Colecciones de artistas locales e internacionales\n"
            "🌿 *Naples Botanical Garden* — 170 acres de jardines tropicales impresionantes\n"
            "⛵ *Alquiler de kayak* — Explora los manglares de Naples\n"
            "🐊 *Everglades Tour* — A solo 45 minutos, una experiencia única\n\n"
            "¿Te gustaría más detalles sobre alguna de estas actividades? 😊"
        )
    else:
        text = (
            f"🎭 *Things to Do in Naples for You, {name}!*\n\n"
            "🏖️ *Naples Beach* — The most beautiful Gulf beach, perfect for sunsets\n"
            "🛍️ *5th Avenue South* — Luxury boutiques, art galleries, and fine dining\n"
            "🐬 *Dolphin Cruise* — Dolphin & manatee sightings (2 hrs, $45/person)\n"
            "🎨 *Naples Art Gallery* — Local and international artist collections\n"
            "🌿 *Naples Botanical Garden* — 170 acres of stunning tropical gardens\n"
            "⛵ *Kayak Rentals* — Explore the Naples mangroves\n"
            "🐊 *Everglades Tour* — Just 45 minutes away — a truly unique experience\n\n"
            "Would you like more details on any of these? 😊"
        )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_emergency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")
    prop = get_demo_property()

    if lang == "es":
        text = (
            "🚨 *Contactos de Emergencia*\n\n"
            f"📞 *Anfitrión:* {prop['emergency']}\n"
            "🚒 *Bomberos/Policía/Ambulancia:* 911\n"
            "🏥 *Hospital más cercano:* NCH Downtown Naples, (239) 436-5000\n\n"
            "Estoy aquí contigo. ¿Qué está pasando? Cuéntame y actuamos de inmediato. 💙"
        )
    else:
        text = (
            "🚨 *Emergency Contacts*\n\n"
            f"📞 *Host:* {prop['emergency']}\n"
            "🚒 *Fire/Police/Ambulance:* 911\n"
            "🏥 *Nearest Hospital:* NCH Downtown Naples, (239) 436-5000\n\n"
            "I'm right here with you. What's happening? Tell me and we'll act immediately. 💙"
        )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇸 English", callback_data="setlang_en"),
         InlineKeyboardButton("🇪🇸 Español", callback_data="setlang_es")]
    ])
    msg = "Choose your preferred language:" if lang == "en" else "Elige tu idioma preferido:"
    await update.message.reply_text(msg, reply_markup=keyboard)


async def cmd_properties(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")
    msg = "🏘️ *Demo Properties — Choose one to explore:*\n\n" if lang == "en" else "🏘️ *Propiedades Demo — Elige una para explorar:*\n\n"
    for p in DEMO_PROPERTIES:
        desc = p.get("description_es" if lang == "es" else "description_en", "")
        msg += f"🏠 *{p['name']}*\n_{desc}_\n\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=get_demo_property_keyboard(lang))


async def cmd_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")
    name = session.get("guest_name") or (user.first_name or "")

    if lang == "es":
        text = (
            f"🎉 *¡Excelente decisión, {name}!*\n\n"
            f"Tu prueba gratuita de *{TRIAL_DAYS} días* de {PLATFORM_NAME} por {BRAND_NAME} está a un paso.\n\n"
            "✅ Conserje de IA bilingüe activo 24/7\n"
            "✅ Sube tus archivos y manuales de la propiedad\n"
            "✅ Alertas en tiempo real para el anfitrión\n"
            "✅ Motor de recomendaciones personalizado\n"
            "✅ Optimización de reseñas de 5 estrellas\n"
            "✅ Sin tarjeta de crédito requerida\n\n"
            f"Después de la prueba, son solo *${MONTHLY_FEE}/mes*.\n\n"
            "👉 Haz clic aquí para comenzar tu configuración:\n"
            "https://t.me/property_onboarding_bot"
        )
    else:
        text = (
            f"🎉 *Excellent choice, {name}!*\n\n"
            f"Your *{TRIAL_DAYS}-day FREE trial* of {PLATFORM_NAME} by {BRAND_NAME} is one step away.\n\n"
            "✅ Bilingual AI concierge active 24/7\n"
            "✅ Upload your property files & manuals\n"
            "✅ Real-time host alert system\n"
            "✅ Personalized recommendation engine\n"
            "✅ 5-star review optimization\n"
            "✅ No credit card required\n\n"
            f"After the trial, it's just *${MONTHLY_FEE}/month*.\n\n"
            "👉 Click here to start your setup:\n"
            "https://t.me/property_onboarding_bot"
        )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🚀 Start Free Trial" if lang == "en" else "🚀 Comenzar Prueba Gratuita",
            url="https://t.me/property_onboarding_bot"
        )
    ]])
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)


async def cmd_demo_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trigger a demo escalation scenario to show hosts what alerts look like."""
    user = update.effective_user
    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")
    name = session.get("guest_name") or (user.first_name or "Guest")

    scenarios = [
        {
            "en": "The AC in the master bedroom isn't working and it's very hot.",
            "es": "El aire acondicionado del dormitorio principal no funciona y hace mucho calor.",
            "type": "HIGH"
        },
        {
            "en": "We noticed a small water leak under the kitchen sink.",
            "es": "Notamos una pequeña fuga de agua debajo del fregadero de la cocina.",
            "type": "HIGH"
        },
        {
            "en": "We're absolutely loving this place! The sunset view is incredible.",
            "es": "¡Estamos absolutamente encantados con este lugar! La vista al atardecer es increíble.",
            "type": "PRAISE"
        },
    ]
    scenario = random.choice(scenarios)
    guest_msg = scenario["es"] if lang == "es" else scenario["en"]

    if lang == "es":
        intro = (
            f"🎭 *Escenario de Demostración*\n\n"
            f"Simulando que el huésped *{name}* envía:\n\n"
            f"💬 _{guest_msg}_\n\n"
            f"Observa cómo respondo y cómo se ve la alerta del anfitrión... 👇"
        )
    else:
        intro = (
            f"🎭 *Demo Scenario*\n\n"
            f"Simulating guest *{name}* sending:\n\n"
            f"💬 _{guest_msg}_\n\n"
            f"Watch how I respond and what the host alert looks like... 👇"
        )

    await update.message.reply_text(intro, parse_mode=ParseMode.MARKDOWN)
    await asyncio.sleep(1.5)

    # Process as if it were a real message
    await _process_guest_message(update, context, session, guest_msg, lang, name, is_scenario=True)


# ─── Callback Handlers ────────────────────────────────────────────────────────

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if data.startswith("setlang_"):
        new_lang = data.replace("setlang_", "")
        update_guest_session(user.id, "demo", language=new_lang)
        msg = "✅ Language set to English! How can I help you? 😊" if new_lang == "en" else "✅ ¡Idioma cambiado a Español! ¿En qué puedo ayudarte? 😊"
        await query.edit_message_text(msg)

    elif data.startswith("prop_"):
        prop_id = data.replace("prop_", "")
        prop = get_demo_property(prop_id)
        session = get_or_create_guest_session(user.id, bot_type="demo")
        lang = session.get("language", "en")
        desc = prop.get("description_es" if lang == "es" else "description_en", "")
        if lang == "es":
            msg = f"🏠 *{prop['name']}*\n\n_{desc}_\n\nAhora estás explorando esta propiedad. ¿En qué puedo ayudarte? 😊"
        else:
            msg = f"🏠 *{prop['name']}*\n\n_{desc}_\n\nYou're now exploring this property. How can I help you? 😊"
        await query.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)

    elif data == "start_trial":
        session = get_or_create_guest_session(user.id, bot_type="demo")
        lang = session.get("language", "en")
        msg = "🚀 Starting your free trial setup! Head to: https://t.me/property_onboarding_bot" if lang == "en" else "🚀 ¡Iniciando tu configuración de prueba gratuita! Ve a: https://t.me/property_onboarding_bot"
        await query.edit_message_text(msg)


# ─── Main Message Handler ─────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        await update.message.reply_text("⏳ You're sending messages too fast. Please wait a moment. / Estás enviando mensajes muy rápido. Por favor espera un momento.")
        return

    session = get_or_create_guest_session(user.id, bot_type="demo")
    lang = session.get("language", "en")
    state = session.get("state", "awaiting_name")
    text = update.message.text.strip() if update.message.text else ""

    # Auto-detect language from message
    detected = detect_language(text)
    if detected != lang and len(text) > 10:
        lang = detected
        update_guest_session(user.id, "demo", language=lang)

    # ── Awaiting name ──
    if state == "awaiting_name":
        name = text.split()[0].capitalize() if text else (user.first_name or "Guest")
        update_guest_session(user.id, "demo", state="active", guest_name=name)
        await update.message.reply_text(
            t("greeting", lang, name=name),
            parse_mode=ParseMode.MARKDOWN,
        )
        # After greeting, show a teaser of capabilities
        await asyncio.sleep(1)
        if lang == "es":
            teaser = (
                "Para mostrarte lo que puedo hacer, prueba cualquiera de estos:\n\n"
                "🍽️ /restaurantes — Recomendaciones personalizadas\n"
                "🌤️ /clima — Clima actual\n"
                "🏠 /propiedad — Info del alojamiento\n"
                "🎭 /escenario — Ver una demostración en vivo\n"
                "💼 /trial — Comenzar prueba gratuita\n\n"
                "O simplemente cuéntame lo que necesitas. 😊"
            )
        else:
            teaser = (
                "To show you what I can do, try any of these:\n\n"
                "🍽️ /restaurants — Personalized recommendations\n"
                "🌤️ /weather — Current weather\n"
                "🏠 /property — Accommodation info\n"
                "🎭 /scenario — See a live demo\n"
                "💼 /trial — Start free trial\n\n"
                "Or just tell me what you need. 😊"
            )
        await update.message.reply_text(teaser)
        return

    # ── Recommendation flow ──
    if state == "awaiting_cuisine":
        update_guest_session(user.id, "demo", state="awaiting_vibe",
                             pending_service=text)
        await update.message.reply_text(t("recommend_ask_vibe", lang), parse_mode=ParseMode.MARKDOWN)
        return

    if state == "awaiting_vibe":
        cuisine = session.get("pending_service", "")
        update_guest_session(user.id, "demo", state="awaiting_budget",
                             pending_service=f"{cuisine}|{text}")
        await update.message.reply_text(t("recommend_ask_budget", lang), parse_mode=ParseMode.MARKDOWN)
        return

    if state == "awaiting_budget":
        parts = (session.get("pending_service") or "").split("|")
        cuisine = parts[0] if parts else ""
        vibe = parts[1] if len(parts) > 1 else ""
        budget = text
        recs = get_recommendations(cuisine_pref=cuisine, vibe_pref=vibe, budget_pref=budget)
        msg = format_recommendations_list(recs, lang)
        update_guest_session(user.id, "demo", state="awaiting_followup",
                             pending_place=recs[0]["name"] if recs else "")
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        return

    # ── Follow-up after recommendation ──
    if state == "awaiting_followup":
        place = session.get("pending_place", "the restaurant")
        update_guest_session(user.id, "demo", state="active")
        # Check sentiment
        rule = check_rules(text, lang)
        if rule["urgency"] in ("CRITICAL", "HIGH", "MEDIUM"):
            await update.message.reply_text(t("followup_negative", lang), parse_mode=ParseMode.MARKDOWN)
            update_review_score(session["session_id"], -0.5)
        else:
            await update.message.reply_text(t("followup_positive", lang), parse_mode=ParseMode.MARKDOWN)
            update_review_score(session["session_id"], +0.3)
        return

    # ── Service confirmation ──
    if state == "awaiting_service_confirm":
        rule = check_rules(text, lang)
        if rule["intent"] == "service_confirm":
            update_guest_session(user.id, "demo", state="active")
            if lang == "es":
                reply = "✅ ¡Perfecto! He confirmado tu solicitud con el anfitrión. Te contactarán pronto. ¿Hay algo más en lo que pueda ayudarte? 😊"
            else:
                reply = "✅ Perfect! I've confirmed your request with the host. They'll be in touch shortly. Is there anything else I can help with? 😊"
            await update.message.reply_text(reply)
        elif rule["intent"] == "service_decline":
            update_guest_session(user.id, "demo", state="active")
            if lang == "es":
                reply = "Sin problema. Estoy aquí si cambias de opinión. ¿Hay algo más que pueda hacer por ti? 😊"
            else:
                reply = "No problem at all! I'm here if you change your mind. Is there anything else I can help with? 😊"
            await update.message.reply_text(reply)
        else:
            if lang == "es":
                reply = "¿Confirmas la solicitud? Escribe *sí* para confirmar o *no* para cancelar."
            else:
                reply = "Do you confirm the request? Type *yes* to confirm or *no* to cancel."
            await update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
        return

    # ── General message — process through rules + AI ──
    name = session.get("guest_name") or (user.first_name or ("Guest" if lang == "en" else "Huésped"))
    await _process_guest_message(update, context, session, text, lang, name)


async def _process_guest_message(update, context, session, text, lang, name, is_scenario=False):
    """Core message processing: rules check → AI → review scoring → escalation."""
    user = update.effective_user
    prop = get_demo_property()

    # Log incoming message
    log_message(session["session_id"], "guest", text)

    # Rules check first
    rule = check_rules(text, lang)

    # Show typing indicator
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    if rule["intent"] in ("critical", "high", "negative"):
        # Immediate empathetic response
        reply = t("issue_acknowledged", lang, name=name)
        await update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)

        # Log escalation
        esc_type = rule["urgency"]
        log_escalation(session["session_id"], None, esc_type, text, reply)

        # Show demo host alert
        await asyncio.sleep(1.5)
        if lang == "es":
            alert_preview = (
                f"📱 *Vista previa de alerta para el anfitrión:*\n\n"
                f"{'🚨' if esc_type == 'CRITICAL' else '⚠️'} *ALERTA {esc_type}*\n"
                f"🏠 {prop['name']}\n"
                f"👤 Huésped: {name}\n"
                f"💬 _{text}_\n\n"
                f"_[El anfitrión recibe esto en tiempo real en su grupo de Telegram]_"
            )
        else:
            alert_preview = (
                f"📱 *Host Alert Preview:*\n\n"
                f"{'🚨' if esc_type == 'CRITICAL' else '⚠️'} *{esc_type} ALERT*\n"
                f"🏠 {prop['name']}\n"
                f"👤 Guest: {name}\n"
                f"💬 _{text}_\n\n"
                f"_[Host receives this in real-time in their Telegram group]_"
            )
        await update.message.reply_text(alert_preview, parse_mode=ParseMode.MARKDOWN)
        update_review_score(session["session_id"], classify_review_delta(rule["intent"]))

    elif rule["intent"] == "service_confirm":
        update_guest_session(user.id, "demo", state="active")
        if lang == "es":
            reply = "✅ ¡Confirmado! He notificado al anfitrión. ¿Hay algo más en lo que pueda ayudarte? 😊"
        else:
            reply = "✅ Confirmed! I've notified the host. Is there anything else I can help with? 😊"
        await update.message.reply_text(reply)

    else:
        # Call AI for general conversation
        prop_data = {**prop, "concierge_name": "Leah", "property_name": prop["name"]}
        ai_reply = await call_groq(
            guest_message=text,
            property_data=prop_data,
            lang=lang,
            knowledge_base="",
            local_context=_get_naples_context(lang),
            current_conditions="",
        )
        await update.message.reply_text(ai_reply, parse_mode=ParseMode.MARKDOWN)
        log_message(session["session_id"], "bot", ai_reply)

        # Check if positive sentiment — show praise alert preview
        positive_words_en = ["amazing", "wonderful", "perfect", "love", "fantastic", "incredible", "beautiful", "great", "excellent", "best"]
        positive_words_es = ["increíble", "maravilloso", "perfecto", "amor", "fantástico", "hermoso", "excelente", "mejor", "encantado"]
        all_pos = positive_words_en + positive_words_es
        if any(w in text.lower() for w in all_pos):
            update_review_score(session["session_id"], +0.3)
            await asyncio.sleep(1.5)
            if lang == "es":
                praise_preview = (
                    "⭐ *Vista previa de alerta para el anfitrión:*\n\n"
                    f"🎉 *ELOGIO DEL HUÉSPED*\n"
                    f"🏠 {prop['name']}\n"
                    f"👤 Huésped: {name}\n"
                    f"💬 _{text}_\n\n"
                    "_¡Este huésped probablemente dejará una reseña de 5 estrellas!_ 🌟"
                )
            else:
                praise_preview = (
                    "⭐ *Host Alert Preview:*\n\n"
                    f"🎉 *GUEST PRAISE*\n"
                    f"🏠 {prop['name']}\n"
                    f"👤 Guest: {name}\n"
                    f"💬 _{text}_\n\n"
                    "_This guest is likely to leave a 5-star review!_ 🌟"
                )
            await update.message.reply_text(praise_preview, parse_mode=ParseMode.MARKDOWN)

    # After 5th message, show trial CTA
    session = get_guest_session(user.id, "demo")
    if session and session.get("messages_count", 0) == 5:
        await asyncio.sleep(2)
        await update.message.reply_text(
            t("trial_cta", lang),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🚀 Start Free Trial" if lang == "en" else "🚀 Comenzar Prueba Gratuita",
                    url="https://t.me/property_onboarding_bot"
                )
            ]])
        )


def _get_naples_context(lang: str) -> str:
    if lang == "es":
        return (
            "Naples, Florida es una ciudad de lujo en la costa del Golfo de México. "
            "Conocida por sus playas de arena blanca, 5th Avenue South con boutiques y restaurantes de lujo, "
            "3rd Street South, el Naples Pier, el Botanical Garden, y la proximidad a los Everglades. "
            "El clima es subtropical — cálido y soleado la mayor parte del año. "
            "Mejor época para visitar: noviembre a abril (temporada seca). "
            "Restaurantes destacados: Campiello, Dorona, Sea Salt, Chops City Grill, Osteria Tulia."
        )
    return (
        "Naples, Florida is a luxury coastal city on the Gulf of Mexico. "
        "Known for white sand beaches, 5th Avenue South with luxury boutiques and fine dining, "
        "3rd Street South, the Naples Pier, Botanical Garden, and proximity to the Everglades. "
        "Climate is subtropical — warm and sunny most of the year. "
        "Best time to visit: November to April (dry season). "
        "Top restaurants: Campiello, Dorona, Sea Salt, Chops City Grill, Osteria Tulia."
    )


# ─── Build Application ────────────────────────────────────────────────────────

def build_demo_app() -> Application:
    init_db()
    app = Application.builder().token(DEMO_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("restaurants", cmd_restaurants))
    app.add_handler(CommandHandler("restaurantes", cmd_restaurants))
    app.add_handler(CommandHandler("weather", cmd_weather))
    app.add_handler(CommandHandler("clima", cmd_weather))
    app.add_handler(CommandHandler("property", cmd_property))
    app.add_handler(CommandHandler("propiedad", cmd_property))
    app.add_handler(CommandHandler("activities", cmd_activities))
    app.add_handler(CommandHandler("actividades", cmd_activities))
    app.add_handler(CommandHandler("emergency", cmd_emergency))
    app.add_handler(CommandHandler("emergencia", cmd_emergency))
    app.add_handler(CommandHandler("language", cmd_language))
    app.add_handler(CommandHandler("idioma", cmd_language))
    app.add_handler(CommandHandler("properties", cmd_properties))
    app.add_handler(CommandHandler("propiedades", cmd_properties))
    app.add_handler(CommandHandler("trial", cmd_trial))
    app.add_handler(CommandHandler("scenario", cmd_demo_scenario))
    app.add_handler(CommandHandler("escenario", cmd_demo_scenario))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    log.info("Demo bot built — @naples_luxury_guest_bot")
    return app
