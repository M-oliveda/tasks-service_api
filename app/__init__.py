"""TasksService API application factory."""
import os

from flask import Flask

from app.api import register_blueprints
from app.core.config import get_settings
from app.core.extensions import register_extensions
from app.utils.logging import configure_logging


def create_app(config_name=None):
    """
    Create Flask application with specified configurations.

    Args:
        config_name: Configuration environment name

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Determine environment
    env = config_name or os.getenv("FLASK_ENV", "development")

    # Load configuration from pydantic settings
    settings = get_settings(env)
    app.config.from_mapping(settings.model_dump())

    # Configure logging
    configure_logging(app)

    # Configure extensions
    register_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Shell context for Flask CLI
    @app.shell_context_processor
    def shell_context():
        """Provide main entities to the shell context."""
        return {"app": app}

    return app
