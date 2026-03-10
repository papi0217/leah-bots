"""
services/weather.py — Weather service with OpenWeatherMap API.
Add WEATHER_API_KEY to .env to enable. Falls back gracefully if not configured.
"""

import asyncio
import logging
import time
from typing import Optional
from config import WEATHER_API_KEY, WEATHER_CACHE_TTL

log = logging.getLogger(__name__)

_cache: dict = {}  # key: city_country -> (timestamp, data)


async def get_weather(city: str, country_code: str = "US", lang: str = "en") -> str:
    """
    Fetch current weather for a city. Returns a formatted string.
    If WEATHER_API_KEY is not set, returns a placeholder message.
    """
    if not WEATHER_API_KEY:
        if lang == "es":
            return "🌤️ El servicio meteorológico estará disponible una vez que se configure la clave de la API del clima."
        return "🌤️ Weather service will be available once the weather API key is configured."

    cache_key = f"{city}_{country_code}"
    now = time.time()
    if cache_key in _cache:
        ts, data = _cache[cache_key]
        if now - ts < WEATHER_CACHE_TTL:
            return _format_weather(data, lang)

    try:
        import aiohttp
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city},{country_code}&appid={WEATHER_API_KEY}&units=imperial&lang={'es' if lang == 'es' else 'en'}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    _cache[cache_key] = (now, data)
                    return _format_weather(data, lang)
                else:
                    log.warning("Weather API returned status %s", resp.status)
    except Exception as e:
        log.error("Weather fetch failed: %s", e)

    if lang == "es":
        return "🌤️ No pude obtener el clima en este momento. ¡Pero Naples siempre está hermoso!"
    return "🌤️ I couldn't fetch the weather right now. But it's always beautiful here!"


def _format_weather(data: dict, lang: str) -> str:
    try:
        temp = round(data["main"]["temp"])
        feels = round(data["main"]["feels_like"])
        desc = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        city = data["name"]
        if lang == "es":
            return f"🌤️ *Clima en {city}:* {temp}°F (sensación {feels}°F)\n{desc} | Humedad: {humidity}%"
        return f"🌤️ *Weather in {city}:* {temp}°F (feels like {feels}°F)\n{desc} | Humidity: {humidity}%"
    except Exception:
        if lang == "es":
            return "🌤️ Clima disponible pronto."
        return "🌤️ Weather available soon."
