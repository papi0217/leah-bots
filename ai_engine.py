"""
ai_engine.py — Groq LLaMA integration with bilingual 5-star hospitality persona.
City-agnostic: works for Naples, Miami, New York, Paris, or any city.
"""

import logging
import asyncio
from typing import Optional
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_TIMEOUT

log = logging.getLogger(__name__)

try:
    from groq import AsyncGroq
    _client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except Exception as e:
    log.warning("Groq client not initialized: %s", e)
    _client = None


SYSTEM_PROMPT_EN = """You are {concierge_name}, a warm, sophisticated, and deeply caring AI concierge for {property_name} in {city}, {country}.

YOUR PERSONALITY:
- You are like the best concierge at a 5-star hotel — warm, attentive, genuinely interested in the guest's experience
- You speak with elegance but never stiffness — you feel like a knowledgeable local friend who happens to know everything
- You ask thoughtful questions before making recommendations — you want to understand what the guest truly wants
- You follow up after experiences to show you genuinely care about how it went
- You anticipate needs before they are expressed
- You never rush a guest — every interaction feels unhurried and personal
- You use the guest's name naturally and warmly throughout the conversation
- You celebrate good moments with the guest and empathize deeply with any frustrations
- Your goal is that every single guest leaves a glowing 5-star review

PROPERTY DETAILS:
{property_context}

KNOWLEDGE BASE:
{knowledge_base}

LOCAL INFORMATION:
{local_context}

CURRENT CONDITIONS:
{current_conditions}

RULES:
1. Always respond in {language_name} unless the guest switches language
2. Never make up information — if you don't know, say so warmly and offer to find out
3. If there is a safety issue, acknowledge it immediately and say you are alerting the host
4. Never share the host's personal phone number unless it's the emergency contact
5. Keep responses warm, concise, and actionable — never robotic or list-heavy
6. When recommending restaurants or activities, ask 1-2 questions first to understand preferences
7. After a guest uses a recommendation, follow up to ask how it was
8. If a guest seems unhappy, express genuine empathy and take immediate action
9. Always end with an open invitation for more help — make the guest feel cared for"""

SYSTEM_PROMPT_ES = """Eres {concierge_name}, un/a conserje de IA cálido/a, sofisticado/a y genuinamente atento/a para {property_name} en {city}, {country}.

TU PERSONALIDAD:
- Eres como el mejor conserje de un hotel de 5 estrellas — cálido/a, atento/a, genuinamente interesado/a en la experiencia del huésped
- Hablas con elegancia pero sin rigidez — te sientes como un/a amigo/a local conocedor/a que sabe de todo
- Haces preguntas reflexivas antes de hacer recomendaciones — quieres entender lo que el huésped realmente desea
- Haces seguimiento después de las experiencias para mostrar que genuinamente te importa cómo salió todo
- Anticipas las necesidades antes de que se expresen
- Nunca apresuras a un huésped — cada interacción se siente tranquila y personal
- Usas el nombre del huésped de forma natural y cálida durante toda la conversación
- Celebras los buenos momentos con el huésped y empatizas profundamente con cualquier frustración
- Tu objetivo es que cada huésped deje una reseña brillante de 5 estrellas

DETALLES DE LA PROPIEDAD:
{property_context}

BASE DE CONOCIMIENTOS:
{knowledge_base}

INFORMACIÓN LOCAL:
{local_context}

CONDICIONES ACTUALES:
{current_conditions}

REGLAS:
1. Siempre responde en español a menos que el huésped cambie de idioma
2. Nunca inventes información — si no sabes, dilo calurosamente y ofrece averiguarlo
3. Si hay un problema de seguridad, reconócelo de inmediato y di que estás alertando al anfitrión
4. Nunca compartas el número personal del anfitrión a menos que sea el contacto de emergencia
5. Mantén las respuestas cálidas, concisas y accionables — nunca robóticas ni llenas de listas
6. Al recomendar restaurantes o actividades, haz 1-2 preguntas primero para entender las preferencias
7. Después de que un huésped use una recomendación, pregunta cómo estuvo
8. Si un huésped parece insatisfecho, expresa empatía genuina y toma acción inmediata
9. Siempre termina con una invitación abierta para más ayuda — haz que el huésped se sienta atendido"""


def build_property_context(prop: dict) -> str:
    amenities = prop.get("amenities", "")
    if isinstance(amenities, list):
        amenities = ", ".join(amenities)
    rules = prop.get("house_rules", "")
    if isinstance(rules, list):
        rules = "; ".join(rules)
    return (
        f"Property: {prop.get('property_name', prop.get('name', 'Our Property'))}\n"
        f"Address: {prop.get('address', 'N/A')}\n"
        f"City: {prop.get('city', 'N/A')}, {prop.get('state_region', prop.get('state', ''))}, {prop.get('country', 'USA')}\n"
        f"Check-in: {prop.get('checkin_time', prop.get('checkin', 'N/A'))} | Check-out: {prop.get('checkout_time', prop.get('checkout', 'N/A'))}\n"
        f"WiFi: {prop.get('wifi_ssid', 'N/A')} / Password: {prop.get('wifi_pass', prop.get('wifi_pass', 'N/A'))}\n"
        f"Keypad Code: {prop.get('keypad_code', prop.get('keypad', 'N/A'))}\n"
        f"Max Guests: {prop.get('max_guests', 'N/A')}\n"
        f"Amenities: {amenities}\n"
        f"House Rules: {rules}\n"
        f"Emergency Contact: {prop.get('emergency', prop.get('emergency_contact', 'N/A'))}"
    )


async def call_groq(
    guest_message: str,
    property_data: dict,
    lang: str = "en",
    knowledge_base: str = "",
    local_context: str = "",
    current_conditions: str = "",
    conversation_history: Optional[list] = None,
) -> str:
    """Call Groq LLaMA with full context and return the concierge response."""
    if not _client:
        if lang == "es":
            return "Disculpa, el servicio de IA no está disponible en este momento. Por favor contacta a tu anfitrión directamente."
        return "I'm sorry, the AI service is not available right now. Please contact your host directly."

    prop_ctx = build_property_context(property_data)
    city = property_data.get("city", "your destination")
    country = property_data.get("country", "")
    concierge = property_data.get("concierge_name", property_data.get("name", "Leah"))
    prop_name = property_data.get("property_name", property_data.get("name", "our property"))
    lang_name = "Spanish" if lang == "es" else "English"

    system_template = SYSTEM_PROMPT_ES if lang == "es" else SYSTEM_PROMPT_EN
    system_prompt = system_template.format(
        concierge_name=concierge,
        property_name=prop_name,
        city=city,
        country=country,
        language_name=lang_name,
        property_context=prop_ctx,
        knowledge_base=knowledge_base or ("No additional files uploaded yet." if lang == "en" else "No se han subido archivos adicionales aún."),
        local_context=local_context or ("Local information not yet available." if lang == "en" else "Información local no disponible aún."),
        current_conditions=current_conditions or ("Weather data not configured yet." if lang == "en" else "Datos del clima no configurados aún."),
    )

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history[-8:])  # Last 4 exchanges
    messages.append({"role": "user", "content": guest_message})

    try:
        response = await asyncio.wait_for(
            _client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                max_tokens=400,
                temperature=0.75,
            ),
            timeout=GROQ_TIMEOUT,
        )
        return response.choices[0].message.content.strip()
    except asyncio.TimeoutError:
        log.error("Groq timeout for message: %s", guest_message[:50])
        if lang == "es":
            return "Disculpa la demora. Déjame verificar eso para ti y te respondo de inmediato. 😊"
        return "I apologize for the delay. Let me look into that for you right away. 😊"
    except Exception as e:
        log.error("Groq error: %s", e)
        if lang == "es":
            return "Disculpa, tuve un pequeño inconveniente. ¿Puedes repetir tu pregunta? 😊"
        return "I'm sorry, I had a small hiccup. Could you repeat your question? 😊"


async def generate_city_context(city: str, country: str, lang: str = "en") -> str:
    """
    Generate a city knowledge context for non-Naples properties.
    This is called once during onboarding to build the local context.
    """
    if not _client:
        return ""

    prompt = (
        f"You are a knowledgeable local expert for {city}, {country}. "
        f"Write a comprehensive local guide in {'Spanish' if lang == 'es' else 'English'} covering: "
        f"top 10 restaurants with cuisine types and price ranges, top 5 attractions, "
        f"top 3 beaches or parks, local transportation tips, best neighborhoods, "
        f"and any unique local customs or tips for visitors. "
        f"Format it clearly with sections. Be specific and accurate."
    )
    try:
        response = await asyncio.wait_for(
            _client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.5,
            ),
            timeout=30,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log.error("City context generation failed: %s", e)
        return f"Local information for {city}, {country} — please ask your host for local recommendations."
