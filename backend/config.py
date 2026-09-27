import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory: root of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

class Config:
    """Application configuration loaded from environment variables."""
    # Base paths
    BASE_DIR = BASE_DIR
    DATA_DIR = BASE_DIR / "data"
    STATIC_DIR = BASE_DIR / "backend" / "static"
    TEMPLATES_DIR = BASE_DIR / "backend" / "templates"

    # Server Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    # Gemini AI
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

    # Telephony Provider (twilio, exotel, plivo, mock)
    TELEPHONY_PROVIDER = os.getenv("TELEPHONY_PROVIDER", "twilio").strip().lower()
    TELEPHONY_ACCOUNT_ID = os.getenv("TELEPHONY_ACCOUNT_ID", "").strip()
    TELEPHONY_AUTH_TOKEN = os.getenv("TELEPHONY_AUTH_TOKEN", "").strip()
    TELEPHONY_PHONE_NUMBER = os.getenv("TELEPHONY_PHONE_NUMBER", "").strip()

    # Speech Services
    STT_PROVIDER = os.getenv("STT_PROVIDER", "mock").strip().lower()
    STT_API_KEY = os.getenv("STT_API_KEY", "").strip()
    TTS_PROVIDER = os.getenv("TTS_PROVIDER", "gtts").strip().lower()
    TTS_API_KEY = os.getenv("TTS_API_KEY", "").strip()

    # Voice Assistant Configuration
    DEFAULT_VOICE = "Polly.Aditi"  # Indian English natural voice on Twilio
    DEFAULT_LANGUAGE = "en-IN"
