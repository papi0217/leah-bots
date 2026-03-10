"""
rules.py — Hard safety rules engine. Always evaluated BEFORE calling AI.
"""

from config import CRITICAL_KEYWORDS, HIGH_KEYWORDS, NEGATIVE_KEYWORDS, SERVICE_CONFIRM_WORDS, SERVICE_DECLINE_WORDS


def check_rules(text: str, lang: str = "en") -> dict:
    """
    Returns a dict with:
      intent: none | critical | high | negative | service_confirm | service_decline
      urgency: NONE | CRITICAL | HIGH | MEDIUM | LOW
      reply_key: string key into STRINGS[lang] or None
    """
    lower = text.lower()

    # Life safety — always CRITICAL
    for kw in CRITICAL_KEYWORDS:
        if kw in lower:
            return {"intent": "critical", "urgency": "CRITICAL", "reply_key": "issue_acknowledged"}

    # Major amenity failure — HIGH
    for kw in HIGH_KEYWORDS:
        if kw in lower:
            return {"intent": "high", "urgency": "HIGH", "reply_key": "issue_acknowledged"}

    # Service confirmation
    for kw in SERVICE_CONFIRM_WORDS:
        if lower.strip() == kw or lower.startswith(kw + " ") or lower.endswith(" " + kw):
            return {"intent": "service_confirm", "urgency": "LOW", "reply_key": None}

    # Service decline
    for kw in SERVICE_DECLINE_WORDS:
        if lower.strip() == kw or lower.startswith(kw + " ") or lower.endswith(" " + kw):
            return {"intent": "service_decline", "urgency": "LOW", "reply_key": None}

    # Negative sentiment — MEDIUM
    for kw in NEGATIVE_KEYWORDS:
        if kw in lower:
            return {"intent": "negative", "urgency": "MEDIUM", "reply_key": "issue_acknowledged"}

    return {"intent": "none", "urgency": "NONE", "reply_key": None}


def classify_review_delta(intent: str) -> float:
    """Return a review score delta based on the intent."""
    deltas = {
        "critical": -1.0,
        "high":     -0.5,
        "negative": -0.3,
        "service_confirm": +0.2,
        "service_decline": -0.1,
        "none":     0.0,
    }
    return deltas.get(intent, 0.0)
