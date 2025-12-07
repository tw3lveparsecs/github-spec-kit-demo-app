"""
Flask application entry point for GitHub Spec Kit Demo Application.

This module initializes the Flask application, configures CORS, error handlers,
and logging, and registers all API routes.
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict

from flask import Flask, jsonify, Response, make_response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Initialize Flask application
app = Flask(__name__, static_folder="../../frontend/src", static_url_path="")

# Configure CORS to allow frontend communication
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure response compression (using built-in gzip when available)
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/javascript', 'application/json',
    'application/javascript', 'text/plain', 'application/xml'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

# Try to enable Flask-Compress if available
try:
    from flask_compress import Compress
    Compress(app)
except ImportError:
    pass  # Flask-Compress not installed, use middleware fallback

# Setup structured JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@app.route("/api/health", methods=["GET"])
def health() -> Response:
    """
    Health check endpoint for Azure App Service health probes.

    Returns:
        JSON response with service status, timestamp, and version.
    """
    return jsonify(
        {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + "Z", "version": "1.0.0"}
    )


@app.errorhandler(404)
def not_found(error: HTTPException) -> tuple[Response, int]:
    """
    Handle 404 Not Found errors with user-friendly JSON response.

    Args:
        error: The HTTP exception that triggered this handler.

    Returns:
        Tuple of JSON response and 404 status code.
    """
    logger.warning(f"404 Not Found: {error.description}")
    return (
        jsonify(
            {
                "error": "The requested resource was not found",
                "code": "NOT_FOUND",
                "status": 404,
                "details": {"path": error.description},
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error: Exception) -> tuple[Response, int]:
    """
    Handle 500 Internal Server Error with user-friendly JSON response.

    Args:
        error: The exception that triggered this handler.

    Returns:
        Tuple of JSON response and 500 status code.
    """
    logger.error(f"500 Internal Server Error: {str(error)}", exc_info=True)
    return (
        jsonify(
            {
                "error": "An internal server error occurred",
                "code": "INTERNAL_ERROR",
                "status": 500,
                "details": {"message": str(error)},
            }
        ),
        500,
    )


@app.errorhandler(Exception)
def handle_exception(error: Exception) -> tuple[Response, int]:
    """
    Handle all uncaught exceptions with appropriate error responses.

    Args:
        error: The exception that was raised.

    Returns:
        Tuple of JSON response and appropriate status code.
    """
    # Handle HTTP exceptions (400, 401, 403, etc.)
    if isinstance(error, HTTPException):
        return (
            jsonify(
                {
                    "error": error.description,
                    "code": error.name.upper().replace(" ", "_"),
                    "status": error.code,
                }
            ),
            error.code or 500,
        )

    # Handle all other exceptions as 500
    logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
    return (
        jsonify(
            {
                "error": "An unexpected error occurred",
                "code": "UNEXPECTED_ERROR",
                "status": 500,
            }
        ),
        500,
    )


@app.route("/")
def index() -> Response:
    """
    Serve the main frontend application.

    Returns:
        The index.html file from the frontend static folder.
    """
    return app.send_static_file("index.html")


@app.after_request
def add_cache_headers(response: Response) -> Response:
    """
    Add caching headers for static assets.
    
    Args:
        response: The response object to modify.
        
    Returns:
        Modified response with caching headers.
    """
    # Cache static assets for 1 hour in production
    if response.content_type and (
        'text/css' in response.content_type or
        'javascript' in response.content_type or
        'image/' in response.content_type or
        'font/' in response.content_type
    ):
        response.headers['Cache-Control'] = 'public, max-age=3600'
    
    # Don't cache API responses
    if '/api/' in str(response.headers.get('Location', '')) or '/api/' in str(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    
    return response


# Register API routes
try:
    from api.routes import register_routes
    register_routes(app)
except ImportError as e:
    logger.warning(f"Could not import API routes: {e}")


if __name__ == "__main__":
    logger.info("Starting GitHub Spec Kit Demo Application")
    app.run(host="0.0.0.0", port=5000, debug=True)
