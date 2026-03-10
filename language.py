"""
language.py — Language detection and preference management.
"""

import logging
from config import STRINGS

log = logging.getLogger(__name__)

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    log.warning("langdetect not available — defaulting to English detection only")


def detect_language(text: str) -> str:
    """Detect language from text. Returns 'en' or 'es'."""
    if not LANGDETECT_AVAILABLE:
        # Simple heuristic fallback
        spanish_words = ["hola", "gracias", "por favor", "buenos", "cómo", "qué", "está", "necesito", "quiero", "puedo"]
        lower = text.lower()
        if any(w in lower for w in spanish_words):
            return "es"
        return "en"
    try:
        lang = detect(text)
        if lang == "es":
            return "es"
        return "en"
    except Exception:
        return "en"


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Get a translated string, falling back to English."""
    lang_strings = STRINGS.get(lang, STRINGS["en"])
    template = lang_strings.get(key, STRINGS["en"].get(key, key))
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template
