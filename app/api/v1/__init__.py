"""API v1 routes."""
from flask import Blueprint

from app.api.v1.health import health_bp

# Create v1 blueprint
api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# Register nested blueprints
api_v1_bp.register_blueprint(health_bp)

# Import other routes after fully registered blueprint to avoid circular imports
# from app.api.v1 import auth
# from app.api.v1 import tasks
# from app.api.v1 import categories
# from app.api.v1 import tags
