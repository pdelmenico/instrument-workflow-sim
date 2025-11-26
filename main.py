"""Main Flask application entry point."""
import logging
from flask import Flask
from flask_cors import CORS

from api.routes import api_bp


def create_app():
    """Create and configure Flask application.

    Returns:
        Configured Flask app instance
    """
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Enable CORS
    CORS(app)

    # Register blueprints
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        """Root endpoint."""
        return {
            "service": "Instrument Workflow Simulator",
            "version": "1.0.0-phase1a",
            "description": "Discrete-event simulation engine for diagnostic instrument workflows",
            "endpoints": {
                "simulate": "POST /api/simulate",
                "events": "GET /api/simulation/<run_id>/events",
                "summary": "GET /api/simulation/<run_id>/summary",
                "health": "GET /api/health"
            }
        }

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
