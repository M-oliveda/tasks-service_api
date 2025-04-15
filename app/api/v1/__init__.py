"""API v1 routes."""
from flask import Blueprint

from .category import category_bp
from .health import health_bp
from .tag import tag_bp
from .task import task_bp
from .user import user_bp

# Create v1 blueprint
api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# Register nested blueprints
api_v1_bp.register_blueprint(health_bp)
api_v1_bp.register_blueprint(user_bp)
api_v1_bp.register_blueprint(category_bp)
api_v1_bp.register_blueprint(task_bp)
api_v1_bp.register_blueprint(tag_bp)
