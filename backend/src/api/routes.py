"""
API route registration for the Flask application.

This module centralizes all API route imports and registration.
"""

from api import api_bp


def register_routes(app):
    """
    Register all API routes with the Flask application.

    Args:
        app: The Flask application instance.
    """
    # Import routes to register them with blueprint
    import api.scenarios  # noqa: F401
    import api.workflow  # noqa: F401
    import api.constitution  # noqa: F401
    import api.presenter_notes  # noqa: F401

    # Register the API blueprint with the app
    app.register_blueprint(api_bp)
