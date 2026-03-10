"""
escalation.py — Host alert formatting and delivery. Bilingual support.
Also forwards new onboarding completions to the platform owner.
"""

import logging
from typing import Optional
from telegram import Bot
from telegram.constants import ParseMode

log = logging.getLogger(__name__)


def format_alert(
    esc_type: str,
    property_name: str,
    guest_name: str,
    guest_tg: str,
    guest_msg: str,
    bot_response: str,
    lang: str = "en",
) -> str:
    """Format a host alert message."""
    if esc_type == "CRITICAL":
        emoji = "🚨"
        label_en = "CRITICAL ALERT — LIFE SAFETY"
        label_es = "ALERTA CRÍTICA — SEGURIDAD"
    elif esc_type == "HIGH":
        emoji = "⚠️"
        label_en = "HIGH PRIORITY ISSUE"
        label_es = "PROBLEMA DE ALTA PRIORIDAD"
    elif esc_type == "REVIEW_RISK":
        emoji = "🆘"
        label_en = "REVIEW RISK ALERT"
        label_es = "ALERTA DE RIESGO DE RESEÑA"
    elif esc_type == "SERVICE_CONFIRM":
        emoji = "✅"
        label_en = "SERVICE REQUEST"
        label_es = "SOLICITUD DE SERVICIO"
    elif esc_type == "PRAISE":
        emoji = "⭐"
        label_en = "GUEST PRAISE"
        label_es = "ELOGIO DEL HUÉSPED"
    else:
        emoji = "📋"
        label_en = "GUEST ALERT"
        label_es = "ALERTA DE HUÉSPED"

    label = label_es if lang == "es" else label_en

    if lang == "es":
        return (
            f"{emoji} *{label}*\n"
            f"🏠 Propiedad: {property_name}\n"
            f"👤 Huésped: {guest_name} (@{guest_tg})\n\n"
            f"💬 *Mensaje del huésped:*\n_{guest_msg}_\n\n"
            f"🤖 *Respuesta de Leah:*\n_{bot_response}_\n\n"
            f"{'⚡ ACCIÓN REQUERIDA: Contacta al huésped de inmediato.' if esc_type in ('CRITICAL','HIGH') else ''}"
            f"{'💡 Riesgo de reseña negativa — haz seguimiento personal.' if esc_type == 'REVIEW_RISK' else ''}"
            f"{'🎉 Este huésped probablemente dejará una reseña de 5 estrellas.' if esc_type == 'PRAISE' else ''}"
        )
    return (
        f"{emoji} *{label}*\n"
        f"🏠 Property: {property_name}\n"
        f"👤 Guest: {guest_name} (@{guest_tg})\n\n"
        f"💬 *Guest message:*\n_{guest_msg}_\n\n"
        f"🤖 *Leah's response:*\n_{bot_response}_\n\n"
        f"{'⚡ ACTION REQUIRED: Contact guest immediately.' if esc_type in ('CRITICAL','HIGH') else ''}"
        f"{'💡 Negative review risk — follow up personally.' if esc_type == 'REVIEW_RISK' else ''}"
        f"{'🎉 This guest is likely to leave a 5-star review!' if esc_type == 'PRAISE' else ''}"
    )


async def send_host_alert(
    bot: Bot,
    group_id: str,
    esc_type: str,
    property_name: str,
    guest_name: str,
    guest_tg: str,
    guest_msg: str,
    bot_response: str,
    lang: str = "en",
) -> bool:
    """Send an alert to the host's Telegram group."""
    if not group_id:
        log.warning("No group_id configured for property %s", property_name)
        return False
    try:
        text = format_alert(esc_type, property_name, guest_name, guest_tg,
                            guest_msg, bot_response, lang)
        await bot.send_message(
            chat_id=group_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
        )
        return True
    except Exception as e:
        log.error("Failed to send host alert: %s", e)
        return False


async def notify_owner_new_onboarding(
    bot: Bot,
    owner_id: int,
    host_name: str,
    host_tg_id: int,
    property_name: str,
    city: str,
    country: str,
    data: dict,
) -> bool:
    """Notify the platform owner when a new host completes onboarding."""
    if not owner_id:
        return False
    try:
        lines = [
            "🎉 *NEW HOST ONBOARDING COMPLETED*",
            f"👤 Host: {host_name} (TG ID: {host_tg_id})",
            f"🏠 Property: {property_name}",
            f"📍 City: {city}, {country}",
            "",
            "*Full Configuration:*",
        ]
        for k, v in data.items():
            if k not in ("state", "language"):
                lines.append(f"• {k.replace('_', ' ').title()}: {v}")
        await bot.send_message(
            chat_id=owner_id,
            text="\n".join(lines),
            parse_mode=ParseMode.MARKDOWN,
        )
        return True
    except Exception as e:
        log.error("Failed to notify owner: %s", e)
        return False
