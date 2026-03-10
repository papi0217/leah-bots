"""
config.py — SolutionA4U Leah AI Concierge Platform
All credentials, constants, bilingual strings, and business configuration.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Bot Tokens ──────────────────────────────────────────────────────────────
# LEAH_Onboarding_Assist @Leah_onboarding_bot
ONBOARDING_BOT_TOKEN = os.getenv("ONBOARDING_BOT_TOKEN", "8276431208:AAEDBp3dGbDheRp96s6IXILvasWxdEnYj5w")
# LEAH_Luxury_Concierge_DEMO @leah_luxury_host_demo_bot
DEMO_BOT_TOKEN       = os.getenv("DEMO_BOT_TOKEN",       "8633547753:AAEElVx4U7O5b3yu7AlK9BrYm7RbQoxDKt8")

# ─── Owner / Admin ────────────────────────────────────────────────────────────
OWNER_TELEGRAM_ID    = int(os.getenv("OWNER_TELEGRAM_ID", "0"))
OWNER_ALERT_GROUP_ID = os.getenv("OWNER_ALERT_GROUP_ID", "")

# ─── AI ───────────────────────────────────────────────────────────────────────
GROQ_API_KEY         = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL           = "llama3-70b-8192"
GROQ_TIMEOUT         = 15

# ─── Weather API ──────────────────────────────────────────────────────────────
WEATHER_API_KEY      = os.getenv("WEATHER_API_KEY", "")
WEATHER_CACHE_TTL    = 600  # 10 minutes

# ─── Business ─────────────────────────────────────────────────────────────────
BRAND_NAME           = "SolutionA4U"
PLATFORM_NAME        = "LEAH AI Concierge"
DEMO_BOT_NAME        = "LEAH_Luxury_Concierge_DEMO"
ONBOARDING_BOT_NAME  = "LEAH_Onboarding_Assist"
SETUP_FEE            = 100.00
MONTHLY_FEE          = 45.99
TRIAL_DAYS           = 7
CURRENCY             = "USD"

# ─── Rate Limiting ────────────────────────────────────────────────────────────
RATE_LIMIT_MESSAGES  = 12
RATE_LIMIT_WINDOW    = 60  # seconds

# ─── Database ─────────────────────────────────────────────────────────────────
# Use /tmp for Render (ephemeral storage) or local data/ for local development
if os.getenv("RENDER"):
    DB_PATH = "/tmp/leah_platform.db"
else:
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    DB_PATH = os.path.join(data_dir, "leah_platform.db")

# ─── File Uploads ─────────────────────────────────────────────────────────────
if os.getenv("RENDER"):
    UPLOAD_DIR = "/tmp/uploads"
else:
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_FILE_SIZE_MB     = 20
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx", ".doc", ".jpg", ".jpeg", ".png"}

# ─── Rule Keywords (for escalation detection) ─────────────────────────────────
CRITICAL_KEYWORDS = [
    "emergency", "911", "police", "fire", "ambulance", "hospital", "danger",
    "injury", "hurt", "bleeding", "accident", "broken", "medical", "help",
    "urgent", "critical", "life", "death", "dying", "severe", "extreme"
]

HIGH_KEYWORDS = [
    "problem", "issue", "broken", "not working", "damaged", "complaint",
    "unhappy", "disappointed", "frustrated", "angry", "upset", "concerned",
    "worried", "scared", "afraid", "uncomfortable", "unsafe", "dirty",
    "smell", "noise", "loud", "cold", "hot", "no water", "no power"
]

NEGATIVE_KEYWORDS = [
    "bad", "terrible", "awful", "horrible", "poor", "worse", "worst",
    "disappointed", "regret", "waste", "money", "never", "again",
    "would not", "wouldn't", "don't recommend", "avoid", "stay away"
]

SERVICE_CONFIRM_WORDS = [
    "yes", "sure", "okay", "ok", "yep", "yeah", "please", "thanks",
    "thank you", "absolutely", "definitely", "of course", "confirm",
    "confirmed", "agreed", "accept", "approved", "go ahead", "do it",
    "sí", "claro", "por supuesto", "de acuerdo", "confirmado"
]

SERVICE_DECLINE_WORDS = [
    "no", "nope", "nah", "never", "don't", "won't", "can't", "unable",
    "not interested", "not needed", "cancel", "skip", "later",
    "no thanks", "not right now", "maybe later",
    "no", "nope", "nunca", "no gracias", "cancelar", "después"
]

# ─── Demo Bot Configuration ───────────────────────────────────────────────────
DEMO_PROPERTIES = [
    {
        "id": "demo_naples_villa",
        "name": "Beachfront Paradise Villa",
        "city": "Naples",
        "state": "FL",
        "country": "USA",
        "address": "5th Avenue South, Naples, FL 34102",
        "checkin": "3:00 PM",
        "checkout": "11:00 AM",
        "wifi_ssid": "BeachParadise_Guest",
        "wifi_pass": "Paradise2024!",
        "keypad": "1234",
        "max_guests": 6,
        "bedrooms": 3,
        "bathrooms": 2,
        "amenities": ["Pool", "Beach Access", "Full Kitchen", "BBQ Grill", "Outdoor Shower", "Beach Chairs & Umbrellas"],
        "house_rules": ["No smoking indoors", "Quiet hours 10 PM–8 AM", "No parties or events", "Pets not allowed", "Max 6 guests"],
        "emergency": "+1-239-555-1234",
        "host_name": "Marco",
        "description_en": "A stunning beachfront villa steps from the Gulf of Mexico with breathtaking sunset views.",
        "description_es": "Una impresionante villa frente al mar a pasos del Golfo de México con vistas al atardecer.",
    },
    {
        "id": "demo_naples_loft",
        "name": "Downtown Naples Luxury Loft",
        "city": "Naples",
        "state": "FL",
        "country": "USA",
        "address": "3rd Street South, Naples, FL 34102",
        "checkin": "4:00 PM",
        "checkout": "10:00 AM",
        "wifi_ssid": "NaplesLoft_Guest",
        "wifi_pass": "Loft2024!",
        "keypad": "5678",
        "max_guests": 4,
        "bedrooms": 2,
        "bathrooms": 2,
        "amenities": ["Rooftop Terrace", "Full Kitchen", "Gym Access", "Concierge Desk", "Bike Rentals"],
        "house_rules": ["No smoking", "Quiet hours 11 PM–8 AM", "No parties", "No pets", "Max 4 guests"],
        "emergency": "+1-239-555-5678",
        "host_name": "Sofia",
        "description_en": "A chic downtown loft in the heart of Naples, walking distance to galleries, restaurants, and the beach.",
        "description_es": "Un elegante loft en el centro de Naples, a poca distancia de galerías, restaurantes y la playa.",
    },
    {
        "id": "demo_naples_family",
        "name": "Family Getaway House",
        "city": "Naples",
        "state": "FL",
        "country": "USA",
        "address": "Vanderbilt Beach Road, Naples, FL 34108",
        "checkin": "3:00 PM",
        "checkout": "11:00 AM",
        "wifi_ssid": "FamilyGetaway_Guest",
        "wifi_pass": "Family2024!",
        "keypad": "9012",
        "max_guests": 8,
        "bedrooms": 4,
        "bathrooms": 3,
        "amenities": ["Private Pool", "Game Room", "Full Kitchen", "BBQ", "Kids Play Area", "Beach Gear"],
        "house_rules": ["No smoking", "Quiet hours 10 PM–8 AM", "No unsupervised parties", "Pets considered case by case", "Max 8 guests"],
        "emergency": "+1-239-555-9012",
        "host_name": "Carlos",
        "description_en": "A spacious family home near Vanderbilt Beach with a private pool, game room, and everything for a perfect family vacation.",
        "description_es": "Una espaciosa casa familiar cerca de Vanderbilt Beach con piscina privada y sala de juegos.",
    },
]

# ─── Naples Curated Restaurants ───────────────────────────────────────────────
NAPLES_RESTAURANTS = [
    {"name": "Campiello", "cuisine": ["Italian"], "vibe": ["romantic", "upscale", "date night"], "price": "$$$$", "rating": 4.8, "address": "1177 3rd St S", "phone": "(239) 435-1166", "review": "The most romantic dinner of our trip — the courtyard is magical at night and the handmade pasta is extraordinary.", "distance_from_5th": 0.2},
    {"name": "Dorona", "cuisine": ["Japanese", "Sushi"], "vibe": ["upscale", "romantic", "foodie"], "price": "$$$$", "rating": 4.8, "address": "1234 3rd St S", "phone": "(239) 261-6899", "review": "The bluefin toro sashimi was the most pristine fish I have ever tasted.", "distance_from_5th": 0.2},
    {"name": "Osteria Tulia", "cuisine": ["Italian"], "vibe": ["cozy", "romantic", "local favorite"], "price": "$$$", "rating": 4.7, "address": "466 5th Ave S", "phone": "(239) 213-2073", "review": "Cozy neighborhood Italian with incredible wine list and homemade pasta.", "distance_from_5th": 0.1},
    {"name": "The Continental", "cuisine": ["American", "Seafood"], "vibe": ["lively", "social", "happy hour"], "price": "$$$", "rating": 4.6, "address": "599 5th Ave S", "phone": "(239) 403-8700", "review": "Best happy hour in Naples — incredible oysters and craft cocktails.", "distance_from_5th": 0.1},
    {"name": "Barbatella", "cuisine": ["Italian", "Mediterranean"], "vibe": ["casual", "family", "outdoor"], "price": "$$$", "rating": 4.6, "address": "1221 3rd St S", "phone": "(239) 263-1955", "review": "Lovely outdoor seating, fresh ingredients, and the best pizza in Naples.", "distance_from_5th": 0.2},
    {"name": "Sea Salt", "cuisine": ["Seafood", "American"], "vibe": ["upscale", "romantic", "special occasion"], "price": "$$$$", "rating": 4.7, "address": "1186 3rd St S", "phone": "(239) 434-7258", "review": "Extraordinary seafood with over 100 varieties of salt — a true culinary experience.", "distance_from_5th": 0.2},
    {"name": "Bha! Bha! Persian Bistro", "cuisine": ["Persian", "Mediterranean"], "vibe": ["unique", "romantic", "adventurous"], "price": "$$$", "rating": 4.7, "address": "865 5th Ave S", "phone": "(239) 594-5557", "review": "Unique and absolutely delicious — the lamb dishes are unforgettable.", "distance_from_5th": 0.3},
    {"name": "Cote d'Azur", "cuisine": ["French"], "vibe": ["romantic", "upscale", "date night"], "price": "$$$$", "rating": 4.6, "address": "11224 Tamiami Trail N", "phone": "(239) 597-8867", "review": "Authentic French cuisine that transports you to Paris.", "distance_from_5th": 2.1},
    {"name": "Chops City Grill", "cuisine": ["Steakhouse", "American"], "vibe": ["upscale", "special occasion", "business"], "price": "$$$$", "rating": 4.7, "address": "837 5th Ave S", "phone": "(239) 262-4677", "review": "The best steakhouse in Naples — perfectly aged cuts and exceptional service.", "distance_from_5th": 0.3},
    {"name": "Tacos & Tequila Cantina", "cuisine": ["Mexican"], "vibe": ["casual", "fun", "family"], "price": "$$", "rating": 4.4, "address": "698 4th Ave N", "phone": "(239) 263-3265", "review": "Authentic Mexican flavors with the best margaritas in town.", "distance_from_5th": 0.5},
    {"name": "Vergina", "cuisine": ["Greek", "Mediterranean"], "vibe": ["casual", "family", "outdoor"], "price": "$$$", "rating": 4.5, "address": "700 5th Ave S", "phone": "(239) 659-7008", "review": "Fresh Greek food with a beautiful outdoor patio — the lamb chops are divine.", "distance_from_5th": 0.2},
    {"name": "Sails Restaurant", "cuisine": ["Seafood", "American"], "vibe": ["upscale", "waterfront", "romantic"], "price": "$$$$", "rating": 4.8, "address": "1148 5th Ave S", "phone": "(239) 430-3900", "review": "Waterfront dining at its finest — the lobster bisque is legendary.", "distance_from_5th": 0.1},
]

# ─── Bilingual UI Strings ─────────────────────────────────────────────────────
STRINGS = {
    "en": {
        "welcome_demo": "✨ Welcome! I'm *Leah*, your personal AI concierge.\n\nI'm here to make your stay absolutely perfect — from restaurant recommendations to anything you need at the property.\n\nMay I ask your name so I can take care of you properly? 😊",
        "welcome_guest": "✨ Welcome to *{property_name}*!\n\nI'm *Leah*, your personal concierge, available 24/7 for anything you need.\n\nMay I have your name so I can give you the warmest welcome? 😊",
        "ask_name": "I'd love to know your name so I can personalize your experience! What shall I call you? 😊",
        "greeting": "Wonderful to meet you, *{name}*! 🌟\n\nI'm here to make every moment of your stay special. What can I do for you today?",
        "how_was_experience": "I hope you had a wonderful time, *{name}*! 🌟\n\nHow was your experience at *{place}*? I'd love to hear all about it!",
        "followup_positive": "That's absolutely wonderful to hear! 🌟 I'm so glad you had a great time.\n\nIs there anything else I can help make your stay even more special?",
        "followup_negative": "Oh, I'm so sorry to hear that, *{name}* 😔 That's not the experience you deserve.\n\nPlease let me make it right — I'm alerting your host right now and we'll take care of this immediately.",
        "recommend_ask_cuisine": "I'd love to find the perfect restaurant for you, *{name}*! 🍽️\n\nTo make sure I recommend exactly what you're in the mood for — what type of cuisine are you craving? Italian, Seafood, Steakhouse, Japanese, French, Mexican, Mediterranean, or something else?",
        "recommend_ask_vibe": "Perfect choice! And what kind of atmosphere are you looking for tonight? Romantic and intimate, lively and social, casual and relaxed, or something special for a celebration? 🥂",
        "recommend_ask_budget": "One last question — what's your budget preference? Budget-friendly, mid-range, upscale, or special occasion (no limit)? 💫",
        "no_weather_key": "🌤️ Weather service will be available once the weather API key is configured.",
        "trial_cta": "🎉 *Impressed by what you've seen?*\n\nThis is exactly what your guests would experience — 24/7, in their language, with your property's personality.\n\nStart your *7-day FREE trial* and see the difference:\n\n✅ Full platform access\n✅ Upload your property files\n✅ Real guest conversations\n✅ No credit card required\n\n[👉 Start Free Trial — /start_trial]",
        "language_switch": "I can also assist you in Spanish! / ¡También puedo ayudarte en español!\n\nType /español to switch languages.",
        "issue_acknowledged": "Oh no, I'm so sorry to hear that, *{name}*! 😟 That is absolutely not the experience you deserve.\n\nI'm alerting your host *right now* and they will contact you within 15 minutes. You have my word.\n\nIn the meantime, let me see if there's anything I can do to help immediately...",
        "service_confirm_ask": "Of course, *{name}*! 😊 I'd be happy to arrange that for you.\n\nJust to make sure I get this exactly right — {service_detail}\n\nShall I confirm this with your host?",
        "checkin_info": "Here's everything you need for a smooth arrival, *{name}* 🏠\n\n📍 *Address:* {address}\n🔑 *Keypad Code:* {keypad}\n⏰ *Check-in:* {checkin}\n📶 *WiFi:* {wifi_ssid}\n🔐 *Password:* {wifi_pass}\n\nIs there anything else I can help you with before you arrive?",
        "escalation_resolved": "✅ I've just heard back from your host, *{name}* — they're on their way to take care of this personally. You're in great hands! 🌟",
    },
    "es": {
        "welcome_demo": "✨ ¡Bienvenido/a! Soy *Leah*, tu conserje personal con inteligencia artificial.\n\nEstoy aquí para hacer tu estadía absolutamente perfecta — desde recomendaciones de restaurantes hasta cualquier cosa que necesites.\n\n¿Me puedes decir tu nombre para atenderte como mereces? 😊",
        "welcome_guest": "✨ ¡Bienvenido/a a *{property_name}*!\n\nSoy *Leah*, tu conserje personal, disponible las 24 horas para todo lo que necesites.\n\n¿Me dices tu nombre para darte la bienvenida más cálida? 😊",
        "ask_name": "¡Me encantaría saber tu nombre para personalizar tu experiencia! ¿Cómo te llamas? 😊",
        "greeting": "¡Un placer conocerte, *{name}*! 🌟\n\nEstoy aquí para hacer cada momento de tu estadía especial. ¿En qué puedo ayudarte hoy?",
        "how_was_experience": "¡Espero que lo hayas pasado de maravilla, *{name}*! 🌟\n\n¿Cómo fue tu experiencia en *{place}*? ¡Me encantaría saberlo todo!",
        "followup_positive": "¡Qué maravilla escuchar eso! 🌟 Me alegra mucho que lo hayas pasado bien.\n\n¿Hay algo más en lo que pueda ayudarte para hacer tu estadía aún más especial?",
        "followup_negative": "Oh, lamento mucho escuchar eso, *{name}* 😔 Esa no es la experiencia que mereces.\n\nPor favor, déjame arreglarlo — estoy alertando a tu anfitrión ahora mismo y nos encargaremos de esto inmediatamente.",
        "recommend_ask_cuisine": "¡Me encantaría encontrar el restaurante perfecto para ti, *{name}*! 🍽️\n\nPara asegurarme de recomendarte exactamente lo que buscas — ¿qué tipo de cocina te apetece? ¿Italiana, Mariscos, Carnes, Japonesa, Francesa, Mexicana, Mediterránea, u otra?",
        "recommend_ask_vibe": "¡Excelente elección! ¿Y qué tipo de ambiente buscas para esta noche? ¿Romántico e íntimo, animado y social, casual y relajado, o algo especial para celebrar? 🥂",
        "recommend_ask_budget": "Una última pregunta — ¿cuál es tu presupuesto? ¿Económico, moderado, elegante, o sin límite para una ocasión especial? 💫",
        "no_weather_key": "🌤️ El servicio de clima estará disponible una vez se configure la clave de API.",
        "trial_cta": "🎉 *¿Impresionado/a por lo que has visto?*\n\nEsto es exactamente lo que tus huéspedes experimentarían — 24/7, en su idioma, con la personalidad de tu propiedad.\n\nInicia tu *prueba GRATUITA de 7 días* y ve la diferencia:\n\n✅ Acceso completo a la plataforma\n✅ Carga tus archivos de propiedad\n✅ Conversaciones reales con huéspedes\n✅ Sin tarjeta de crédito requerida\n\n[👉 Iniciar Prueba Gratuita — /start_trial]",
        "language_switch": "¡También puedo ayudarte en inglés! / I can also assist you in English!\n\nType /english to switch languages.",
        "issue_acknowledged": "¡Oh no, lamento mucho escuchar eso, *{name}*! 😟 Esa definitivamente no es la experiencia que mereces.\n\nEstoy alertando a tu anfitrión *AHORA MISMO* y te contactarán en los próximos 15 minutos. Te lo prometo.\n\nMientras tanto, déjame ver si puedo ayudarte de inmediato...",
        "service_confirm_ask": "¡Por supuesto, *{name}*! 😊 Me encantaría ayudarte a arreglarlo.\n\nSolo para asegurarme de hacerlo correctamente — {service_detail}\n\n¿Confirmo esto con tu anfitrión?",
        "checkin_info": "Aquí está todo lo que necesitas para una llegada sin problemas, *{name}* 🏠\n\n📍 *Dirección:* {address}\n🔑 *Código de Teclado:* {keypad}\n⏰ *Check-in:* {checkin}\n📶 *WiFi:* {wifi_ssid}\n🔐 *Contraseña:* {wifi_pass}\n\n¿Hay algo más en lo que pueda ayudarte antes de que llegues?",
        "escalation_resolved": "✅ Acabo de recibir noticias de tu anfitrión, *{name}* — ¡van en camino para encargarse de esto personalmente! ¡Estás en buenas manos! 🌟",
    },
}
