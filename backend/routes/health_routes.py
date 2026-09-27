from flask import Blueprint, jsonify
from backend.config import Config

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend status and configuration."""
    return jsonify({
        "status": "ok",
        "service": "College Voice Assistant IVR",
        "telephony_provider": Config.TELEPHONY_PROVIDER,
        "gemini_configured": bool(Config.GEMINI_API_KEY),
        "stt_provider": Config.STT_PROVIDER,
        "tts_provider": Config.TTS_PROVIDER
    }), 200
