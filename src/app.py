import logging
from src import create_app
from flask import jsonify
import os

# Initialize the application
app = create_app()

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("personal_assistant_api")
logger.info("Starting the personal assistant API...")

@app.route("/", methods=["GET"])
def hello():
    """Root endpoint to verify API is running."""
    try:
        logger.info("Root endpoint accessed")
        return jsonify({"message": "Welcome to the personal assistant API."}), 200
    except Exception as e:
        logger.error(f"An error occurred at root endpoint: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error"}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors with a JSON response."""
    logger.warning("404 error - Page not found")
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors with a JSON response."""
    logger.error("500 error - Internal server error", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)

