"""
state.py — Conversation state enums for SolutionA4U Leah AI Concierge Platform
"""

from enum import Enum, auto


class GuestState(str, Enum):
    """States for guest conversations."""
    AWAITING_NAME         = "awaiting_name"
    ACTIVE                = "active"
    AWAITING_CUISINE      = "awaiting_cuisine"
    AWAITING_VIBE         = "awaiting_vibe"
    AWAITING_BUDGET       = "awaiting_budget"
    AWAITING_SERVICE_CONFIRM = "awaiting_service_confirm"
    AWAITING_FOLLOWUP     = "awaiting_followup"
    ESCALATED             = "escalated"


class OnboardingState(str, Enum):
    """States for host onboarding flow (20 steps)."""
    START                  = "start"
    LANGUAGE               = "language"
    HOST_NAME              = "host_name"
    BUSINESS_NAME          = "business_name"
    PROPERTY_NAME          = "property_name"
    CITY                   = "city"
    STATE_REGION           = "state_region"
    COUNTRY                = "country"
    ADDRESS                = "address"
    CONCIERGE_NAME         = "concierge_name"
    WIFI_SSID              = "wifi_ssid"
    WIFI_PASS              = "wifi_pass"
    CHECKIN_TIME           = "checkin_time"
    CHECKOUT_TIME          = "checkout_time"
    KEYPAD_CODE            = "keypad_code"
    MAX_GUESTS             = "max_guests"
    AMENITIES              = "amenities"
    HOUSE_RULES            = "house_rules"
    EMERGENCY_CONTACT      = "emergency_contact"
    TELEGRAM_GROUP         = "telegram_group"
    UPLOAD_FILES           = "upload_files"
    PAYMENT                = "payment"
    COMPLETE               = "complete"


class DemoState(str, Enum):
    """States for demo bot interaction."""
    AWAITING_NAME          = "awaiting_name"
    ACTIVE                 = "active"
    AWAITING_CUISINE       = "awaiting_cuisine"
    AWAITING_VIBE          = "awaiting_vibe"
    AWAITING_BUDGET        = "awaiting_budget"
    AWAITING_SERVICE_CONFIRM = "awaiting_service_confirm"
    TRIAL_REQUESTED        = "trial_requested"
