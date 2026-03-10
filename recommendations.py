"""
recommendations.py — Dynamic restaurant/activity recommendation engine.
City-agnostic: uses Naples curated data for Naples properties,
AI-generated context for other cities.
"""

import logging
import random
from typing import List, Dict, Optional
from config import NAPLES_RESTAURANTS

log = logging.getLogger(__name__)


def score_restaurant(restaurant: Dict, cuisine_pref: str, vibe_pref: str, budget_pref: str) -> float:
    score = 0.0
    cuisines = [c.lower() for c in restaurant.get("cuisine", [])]
    vibes = [v.lower() for v in restaurant.get("vibe", [])]
    price = restaurant.get("price", "$$")

    # Cuisine match
    if cuisine_pref and any(cuisine_pref.lower() in c for c in cuisines):
        score += 15.0
    elif cuisine_pref and any(c in cuisine_pref.lower() for c in cuisines):
        score += 8.0

    # Vibe match
    if vibe_pref:
        for v in vibes:
            if vibe_pref.lower() in v or v in vibe_pref.lower():
                score += 10.0
                break

    # Budget match
    budget_map = {"budget": "$", "mid-range": "$$", "upscale": "$$$", "special": "$$$$"}
    preferred_price = budget_map.get(budget_pref.lower() if budget_pref else "", "")
    if preferred_price and price == preferred_price:
        score += 8.0
    elif preferred_price and abs(len(price) - len(preferred_price)) <= 1:
        score += 4.0

    # Rating boost
    score += restaurant.get("rating", 4.0) * 2.0

    # Small random factor for variety
    score += random.uniform(0, 1.5)

    return score


def get_recommendations(
    cuisine_pref: str = "",
    vibe_pref: str = "",
    budget_pref: str = "",
    seen_names: Optional[List[str]] = None,
    city: str = "naples",
    restaurants: Optional[List[Dict]] = None,
    count: int = 3,
) -> List[Dict]:
    """Return top N restaurant recommendations, avoiding already-seen ones."""
    seen = set(n.lower() for n in (seen_names or []))
    pool = restaurants if restaurants else NAPLES_RESTAURANTS

    # Filter out seen
    available = [r for r in pool if r["name"].lower() not in seen]
    if not available:
        available = pool  # Reset if all seen

    scored = [(score_restaurant(r, cuisine_pref, vibe_pref, budget_pref), r) for r in available]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:count]]


def format_recommendation(r: Dict, lang: str = "en", rank: int = 1) -> str:
    """Format a single restaurant recommendation."""
    name = r.get("name", "Restaurant")
    cuisine = " & ".join(r.get("cuisine", []))
    price = r.get("price", "$$")
    rating = r.get("rating", 4.5)
    review = r.get("review", "")
    phone = r.get("phone", "")
    address = r.get("address", "")
    stars = "⭐" * round(rating)

    if lang == "es":
        return (
            f"🍽️ *{name}*\n"
            f"{cuisine} • {price} • {stars} {rating}/5\n"
            f"_{review}_\n"
            f"📍 {address}\n"
            f"{'📞 ' + phone if phone else ''}"
        )
    return (
        f"🍽️ *{name}*\n"
        f"{cuisine} • {price} • {stars} {rating}/5\n"
        f"_{review}_\n"
        f"📍 {address}\n"
        f"{'📞 ' + phone if phone else ''}"
    )


def format_recommendations_list(recs: List[Dict], lang: str = "en") -> str:
    """Format a list of recommendations into a message."""
    if not recs:
        if lang == "es":
            return "Lo siento, no encontré restaurantes que coincidan con tus preferencias. ¿Puedo sugerirte algo diferente?"
        return "I'm sorry, I couldn't find restaurants matching your preferences. May I suggest something different?"

    parts = []
    for i, r in enumerate(recs, 1):
        parts.append(format_recommendation(r, lang, i))

    if lang == "es":
        footer = "\n\n¿Cuál de estos te llama la atención? ¡Puedo ayudarte con la reserva! 😊"
    else:
        footer = "\n\nWhich of these catches your eye? I can help with reservations! 😊"

    return "\n\n".join(parts) + footer
