import sys
from pathlib import Path
from flask import Flask, jsonify, redirect
from flask_cors import CORS

# Add root folder to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.config import Config
from backend.routes.health_routes import health_bp
from backend.routes.voice_routes import voice_bp
from backend.utils.logger import logger

def create_app() -> Flask:
    """Application factory for the College Voice Assistant."""
    app = Flask(__name__, static_folder=str(Config.STATIC_DIR))
    CORS(app)

    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(voice_bp)

    @app.route("/")
    def index():
        """Root redirect to interactive IVR test simulator."""
        return redirect("/test/ivr")

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "Endpoint not found", "status": 404}), 404

    @app.errorhandler(500)
    def handle_500(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"error": "Internal server error", "status": 500}), 500

    return app

app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting College Voice Assistant on http://{Config.HOST}:{Config.PORT}")
    logger.info(f"Telephony provider configured: {Config.TELEPHONY_PROVIDER}")
    logger.info(f"Gemini API key configured: {'Yes' if Config.GEMINI_API_KEY else 'No (using local rule fallback)'}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
