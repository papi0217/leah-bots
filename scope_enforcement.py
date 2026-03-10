"""
LEAH Bots — Scope Enforcement System
Comprehensive validation and scope control for both bots
Ensures strict adherence to bot duties and professional redirects
"""

from enum import Enum
from typing import Tuple, Optional, Dict, List

# ============================================================================
# BOT SCOPE DEFINITIONS
# ============================================================================

class BotScope(Enum):
    """Defines the scope for each bot"""
    DEMO = "demo"
    ONBOARDING = "onboarding"

# ============================================================================
# DEMO BOT SCOPE (Guest-Facing Concierge)
# ============================================================================

DEMO_BOT_SCOPE = {
    "name": "LEAH Luxury Concierge",
    "primary_duties": [
        "Property information and amenities",
        "Restaurant recommendations",
        "Activity and entertainment suggestions",
        "Guest support and assistance",
        "House rules and policies",
        "Local recommendations",
        "Concierge services"
    ],
    "keywords": {
        "property_info": [
            "amenities", "pool", "spa", "wifi", "kitchen", "bedroom", "bathroom",
            "parking", "garage", "laundry", "air conditioning", "heating",
            "television", "entertainment", "appliances", "facilities",
            "check-in", "check-out", "keys", "access", "security", "alarm"
        ],
        "restaurants": [
            "restaurant", "dining", "food", "cuisine", "eat", "lunch", "dinner",
            "breakfast", "cafe", "bar", "bistro", "pizzeria", "steakhouse",
            "seafood", "italian", "french", "spanish", "asian", "mexican",
            "reservation", "booking", "table", "menu", "chef"
        ],
        "activities": [
            "activity", "entertainment", "attraction", "tour", "excursion",
            "beach", "hiking", "museum", "gallery", "theater", "cinema",
            "shopping", "spa", "massage", "yoga", "fitness", "golf",
            "water sports", "adventure", "sightseeing", "nightlife"
        ],
        "guest_support": [
            "help", "assistance", "support", "problem", "issue", "emergency",
            "urgent", "broken", "damaged", "not working", "maintenance",
            "repair", "fix", "complaint", "concern", "question", "information"
        ],
        "house_rules": [
            "rules", "policy", "policies", "quiet hours", "noise", "smoking",
            "pets", "guests", "parking", "trash", "cleaning", "damage",
            "curfew", "restrictions", "allowed", "permitted", "prohibited"
        ]
    }
}

# ============================================================================
# ONBOARDING BOT SCOPE (Host-Facing Property Management)
# ============================================================================

ONBOARDING_BOT_SCOPE = {
    "name": "LEAH Onboarding Assistant",
    "primary_duties": [
        "Property registration and setup",
        "Property management",
        "Amenities configuration",
        "House rules setup",
        "Pricing and membership management",
        "Property modification",
        "QR code generation",
        "Concierge assignment"
    ],
    "keywords": {
        "property_setup": [
            "property", "register", "setup", "create", "add", "new property",
            "property name", "location", "address", "city", "country",
            "capacity", "guests", "bedrooms", "bathrooms", "square feet"
        ],
        "amenities": [
            "amenities", "add amenity", "remove amenity", "features",
            "pool", "spa", "wifi", "kitchen", "parking", "laundry",
            "air conditioning", "heating", "television", "appliances"
        ],
        "house_rules": [
            "rules", "add rule", "remove rule", "quiet hours", "smoking",
            "pets", "guests", "parking", "cleaning", "damage", "policy"
        ],
        "pricing": [
            "pricing", "membership", "tier", "plan", "cost", "fee",
            "enrollment", "monthly", "subscription", "upgrade", "downgrade",
            "properties", "limit", "expansion", "consultation"
        ],
        "property_management": [
            "modify", "edit", "update", "change", "remove property",
            "delete", "manage", "view", "list", "details", "description",
            "features", "settings", "configuration"
        ],
        "qr_code": [
            "qr code", "qr", "generate", "create qr", "code", "scan",
            "link", "access", "concierge", "assign"
        ]
    }
}

# ============================================================================
# COMPREHENSIVE SCENARIO DATABASE
# ============================================================================

DEMO_BOT_SCENARIOS = {
    # Property Information Scenarios
    "property_info": [
        "What amenities are available?",
        "Does the property have WiFi?",
        "Is there a pool?",
        "Tell me about the kitchen",
        "How many bedrooms?",
        "What's the parking situation?",
        "Is there air conditioning?",
        "Do you have a spa?",
        "What's included in the property?",
        "Can you describe the facilities?",
        "Is laundry available?",
        "What entertainment options are there?",
        "Tell me about check-in and check-out",
        "How do I access the property?",
        "What security measures are in place?",
    ],
    # Restaurant Scenarios
    "restaurants": [
        "Where can I eat?",
        "What restaurants do you recommend?",
        "I'm looking for Italian food",
        "Where's the best seafood restaurant?",
        "Can you recommend a fine dining restaurant?",
        "What about casual dining options?",
        "Are there any Michelin-starred restaurants nearby?",
        "I'd like a reservation for dinner",
        "What's good for breakfast?",
        "Do you know any romantic restaurants?",
        "What about vegetarian options?",
        "Can you recommend a wine bar?",
        "Where's the nearest café?",
        "What's your favorite restaurant?",
        "Are there any local specialties I should try?",
    ],
    # Activity Scenarios
    "activities": [
        "What activities are available?",
        "What can I do in the area?",
        "Are there any tours?",
        "Can you recommend attractions?",
        "What about water sports?",
        "Is there a beach nearby?",
        "Are there hiking trails?",
        "What museums are close by?",
        "Can you suggest entertainment?",
        "What's there to do in the evening?",
        "Are there any cultural events?",
        "Can I go shopping nearby?",
        "What about golf courses?",
        "Are there spa services available?",
        "What's the nightlife like?",
    ],
    # Guest Support Scenarios
    "guest_support": [
        "I need help with something",
        "There's a problem with the WiFi",
        "The air conditioning isn't working",
        "I need to report an issue",
        "Can you help me with check-in?",
        "What should I do in an emergency?",
        "Something is broken",
        "I have a question about the property",
        "Can you assist me?",
        "I need maintenance",
        "There's a noise complaint",
        "I need extra towels",
        "Can you arrange something for me?",
        "I'm locked out",
        "Can you help with directions?",
    ],
    # House Rules Scenarios
    "house_rules": [
        "What are the house rules?",
        "When are quiet hours?",
        "Can I smoke inside?",
        "Are pets allowed?",
        "How many guests can stay?",
        "What's the parking policy?",
        "When do I need to check out?",
        "Can I have parties?",
        "What about noise levels?",
        "Are there any restrictions?",
        "What's not allowed?",
        "Can I cook?",
        "What about trash disposal?",
        "Are there any curfews?",
        "What happens if I break something?",
    ],
}

ONBOARDING_BOT_SCENARIOS = {
    # Property Setup Scenarios
    "property_setup": [
        "I want to add a new property",
        "How do I register my property?",
        "What information do I need to provide?",
        "Can I manage multiple properties?",
        "How do I set up my first property?",
        "What's the registration process?",
        "Do I need to provide property details?",
        "How many properties can I add?",
        "Can I edit property information?",
        "What details are required?",
    ],
    # Amenities Scenarios
    "amenities": [
        "How do I add amenities?",
        "What amenities should I list?",
        "Can I modify amenities later?",
        "How do I remove an amenity?",
        "What amenities are most popular?",
        "Can I add custom amenities?",
        "How detailed should amenity descriptions be?",
        "What if I'm missing an amenity?",
        "Can I update amenities?",
        "How do guests see my amenities?",
    ],
    # House Rules Scenarios
    "house_rules": [
        "How do I set house rules?",
        "What rules should I have?",
        "Can I customize rules?",
        "How do I add quiet hours?",
        "Can I prohibit smoking?",
        "What about pet policies?",
        "How do I set check-in/check-out times?",
        "Can guests see the rules?",
        "How do I modify rules?",
        "What are recommended rules?",
    ],
    # Pricing Scenarios
    "pricing": [
        "What are the membership tiers?",
        "How much does it cost?",
        "What's included in each tier?",
        "Can I upgrade my membership?",
        "What's the difference between tiers?",
        "Do I need to pay monthly?",
        "What about additional properties?",
        "How do I add more properties?",
        "What's the enterprise option?",
        "Can I schedule a consultation?",
        "What's the enrollment fee?",
        "How many properties per tier?",
        "What happens if I exceed my limit?",
        "Can I downgrade?",
        "What's included in the price?",
    ],
    # Property Management Scenarios
    "property_management": [
        "How do I manage my properties?",
        "Can I edit property details?",
        "How do I remove a property?",
        "Can I view all my properties?",
        "How do I update descriptions?",
        "Can I change amenities?",
        "How do I modify pricing?",
        "Can I view guest information?",
        "How do I track bookings?",
        "Can I generate reports?",
    ],
    # QR Code Scenarios
    "qr_code": [
        "How do I get a QR code?",
        "What's the QR code for?",
        "Can I generate QR codes?",
        "How do guests use the QR code?",
        "Can I customize the QR code?",
        "What information is in the QR code?",
        "How do I share the QR code?",
        "Can I regenerate a QR code?",
        "What's the concierge link?",
        "How does the concierge assignment work?",
    ],
}

# ============================================================================
# OUT-OF-SCOPE REDIRECT MESSAGES
# ============================================================================

OUT_OF_SCOPE_REDIRECTS = {
    "demo": {
        "generic": "I appreciate your question, but that's outside my scope as your luxury concierge. I'm here to assist with property information, restaurant recommendations, activities, and guest support. How can I help you with your stay?",
        "by_category": {
            "personal": "I'm designed to assist with your luxury experience at the property. For personal matters, I'd recommend contacting support directly. Is there anything about the property or local recommendations I can help with?",
            "financial": "I'm unable to discuss financial or payment matters. Please contact our support team for billing inquiries. Can I help you with property information or local recommendations instead?",
            "medical": "For medical emergencies, please contact emergency services immediately. For non-urgent health concerns, please consult a healthcare professional. Is there anything else I can assist you with?",
            "legal": "I'm unable to provide legal advice. For legal matters, please consult with a qualified attorney. Can I help you with your stay at the property?",
            "technical": "For technical issues beyond property systems, please contact our support team. I can help with property-related questions and local recommendations.",
            "political": "I'm here to provide exceptional hospitality service. I don't discuss political matters. How can I enhance your stay?",
            "religious": "I respect all beliefs and backgrounds. I'm here to provide exceptional service. How can I assist you with your stay?",
        }
    },
    "onboarding": {
        "generic": "I appreciate your inquiry, but that's outside my scope as your property management assistant. I'm here to help with property setup, management, amenities configuration, pricing tiers, and concierge assignment. What can I assist you with?",
        "by_category": {
            "personal": "I'm designed to assist with property management and onboarding. For personal matters, please contact support. Can I help you with your property setup?",
            "financial_advice": "I provide pricing information for our membership tiers, but I cannot offer financial advice. For financial planning, consult with a qualified advisor. Can I explain our pricing tiers?",
            "legal": "I'm unable to provide legal advice. For legal matters, consult with a qualified attorney. I can help with property management and setup.",
            "technical_support": "For technical issues unrelated to property management, please contact our support team. I can assist with property setup and management.",
            "political": "I'm here to provide professional property management services. I don't discuss political matters. How can I help with your properties?",
            "medical": "For medical matters, please consult with a healthcare professional. I'm here to assist with property management.",
        }
    }
}

# ============================================================================
# SCOPE ENFORCEMENT ENGINE
# ============================================================================

class ScopeEnforcer:
    """Enforces strict scope boundaries for both bots"""
    
    @staticmethod
    def validate_demo_bot_query(user_message: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validates if user query is within Demo Bot scope
        Returns: (is_valid, category, redirect_message)
        """
        message_lower = user_message.lower()
        
        # Check against all valid keywords
        for category, keywords in DEMO_BOT_SCOPE["keywords"].items():
            for keyword in keywords:
                if keyword in message_lower:
                    return True, category, None
        
        # Detect out-of-scope categories
        out_of_scope_indicators = {
            "personal": ["my life", "personal", "private", "family", "relationship", "dating"],
            "financial": ["price", "cost", "payment", "money", "credit card", "bank", "investment"],
            "medical": ["sick", "illness", "disease", "doctor", "medicine", "health condition", "hospital"],
            "legal": ["lawsuit", "lawyer", "legal", "court", "attorney", "contract"],
            "political": ["politics", "election", "government", "vote", "party", "policy"],
            "religious": ["religion", "god", "faith", "belief", "church", "prayer"],
        }
        
        for category, indicators in out_of_scope_indicators.items():
            for indicator in indicators:
                if indicator in message_lower:
                    redirect = OUT_OF_SCOPE_REDIRECTS["demo"]["by_category"].get(
                        category,
                        OUT_OF_SCOPE_REDIRECTS["demo"]["generic"]
                    )
                    return False, category, redirect
        
        # Generic out-of-scope redirect
        return False, "unknown", OUT_OF_SCOPE_REDIRECTS["demo"]["generic"]
    
    @staticmethod
    def validate_onboarding_bot_query(user_message: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validates if user query is within Onboarding Bot scope
        Returns: (is_valid, category, redirect_message)
        """
        message_lower = user_message.lower()
        
        # Check against all valid keywords
        for category, keywords in ONBOARDING_BOT_SCOPE["keywords"].items():
            for keyword in keywords:
                if keyword in message_lower:
                    return True, category, None
        
        # Detect out-of-scope categories
        out_of_scope_indicators = {
            "personal": ["my life", "personal", "private", "family", "relationship"],
            "financial_advice": ["invest", "stock", "crypto", "financial advice", "tax"],
            "legal": ["lawsuit", "lawyer", "legal", "court", "attorney"],
            "political": ["politics", "election", "government", "vote"],
            "medical": ["sick", "illness", "disease", "doctor", "health"],
        }
        
        for category, indicators in out_of_scope_indicators.items():
            for indicator in indicators:
                if indicator in message_lower:
                    redirect = OUT_OF_SCOPE_REDIRECTS["onboarding"]["by_category"].get(
                        category,
                        OUT_OF_SCOPE_REDIRECTS["onboarding"]["generic"]
                    )
                    return False, category, redirect
        
        # Generic out-of-scope redirect
        return False, "unknown", OUT_OF_SCOPE_REDIRECTS["onboarding"]["generic"]
    
    @staticmethod
    def get_demo_bot_scope_info() -> Dict:
        """Returns comprehensive scope information for Demo Bot"""
        return {
            "name": DEMO_BOT_SCOPE["name"],
            "duties": DEMO_BOT_SCOPE["primary_duties"],
            "categories": list(DEMO_BOT_SCOPE["keywords"].keys()),
        }
    
    @staticmethod
    def get_onboarding_bot_scope_info() -> Dict:
        """Returns comprehensive scope information for Onboarding Bot"""
        return {
            "name": ONBOARDING_BOT_SCOPE["name"],
            "duties": ONBOARDING_BOT_SCOPE["primary_duties"],
            "categories": list(ONBOARDING_BOT_SCOPE["keywords"].keys()),
        }

# ============================================================================
# SCENARIO MATCHER
# ============================================================================

class ScenarioMatcher:
    """Matches user queries to predefined scenarios"""
    
    @staticmethod
    def match_demo_scenario(user_message: str) -> Optional[str]:
        """Matches user message to Demo Bot scenario"""
        message_lower = user_message.lower()
        
        for category, scenarios in DEMO_BOT_SCENARIOS.items():
            for scenario in scenarios:
                if scenario.lower() in message_lower or message_lower in scenario.lower():
                    return category
        
        return None
    
    @staticmethod
    def match_onboarding_scenario(user_message: str) -> Optional[str]:
        """Matches user message to Onboarding Bot scenario"""
        message_lower = user_message.lower()
        
        for category, scenarios in ONBOARDING_BOT_SCENARIOS.items():
            for scenario in scenarios:
                if scenario.lower() in message_lower or message_lower in scenario.lower():
                    return category
        
        return None

# ============================================================================
# PROFESSIONAL VOCABULARY FOR LUXURY HOSPITALITY
# ============================================================================

LUXURY_VOCABULARY = {
    "greetings": [
        "Good morning, and welcome to our distinguished property.",
        "Greetings! I'm delighted to assist you.",
        "Welcome to an exceptional experience.",
        "How may I be of service?",
    ],
    "confirmations": [
        "Certainly, I'd be delighted to assist.",
        "Of course, allow me to help.",
        "Absolutely, that's an excellent choice.",
        "I'm pleased to accommodate your request.",
    ],
    "recommendations": [
        "I would be honored to recommend...",
        "May I suggest an exquisite option...",
        "I believe you would appreciate...",
        "Allow me to present a refined selection...",
    ],
    "assistance": [
        "I'm at your complete disposal.",
        "Please don't hesitate to reach out.",
        "I'm here to ensure your complete satisfaction.",
        "Your comfort is my priority.",
    ],
    "closings": [
        "Is there anything else I may arrange for you?",
        "How else may I be of service?",
        "Please let me know if you require further assistance.",
        "I remain at your service.",
    ],
}

# ============================================================================
# PRICING TIER DEFINITIONS
# ============================================================================

PRICING_TIERS = {
    "essential": {
        "name": "Essential Membership",
        "enrollment_fee": 100,
        "monthly_fee": 50,
        "properties": 3,
        "features": [
            "Up to 3 properties",
            "Basic concierge services",
            "Guest support",
            "Property management dashboard",
            "Monthly reporting",
        ],
        "description": "Perfect for boutique property owners managing 1-3 luxury properties."
    },
    "premium": {
        "name": "Premium Membership",
        "enrollment_fee": 300,
        "monthly_fee": 150,
        "properties": 10,
        "features": [
            "Up to 10 properties",
            "Enhanced concierge services",
            "Priority guest support",
            "Advanced analytics",
            "Custom branding",
            "Dedicated account manager",
            "Weekly reporting",
        ],
        "description": "Ideal for established hospitality businesses with 4-10 properties."
    },
    "enterprise": {
        "name": "Enterprise Partnership",
        "enrollment_fee": "Custom",
        "monthly_fee": "Custom",
        "properties": "Unlimited",
        "features": [
            "Unlimited properties",
            "White-label solutions",
            "24/7 premium support",
            "Custom integrations",
            "Dedicated infrastructure",
            "Strategic consulting",
            "Real-time analytics",
        ],
        "description": "Tailored solutions for large-scale hospitality portfolios. Schedule a consultation."
    }
}
