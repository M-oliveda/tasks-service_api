"""API blueprint registration."""


def register_blueprints(app):
    """
    Register API blueprints.

    Args:
        app: Flask application instance
    """
    # Import blueprints
    from app.api.v1 import api_v1_bp

    # Register blueprints
    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")
