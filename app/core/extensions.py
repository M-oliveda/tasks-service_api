"""Flask extensions initialization."""
from flasgger import Swagger
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Instantiate extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)


def register_extensions(app):
    """
    Register Flask extensions.

    Args:
        app: Flask application instance
    """
    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize Migrations
    migrate.init_app(app, db)

    # Initialize JWT
    jwt.init_app(app)

    # Initialize CORS
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    # Initialize Rate Limiter
    limiter.init_app(app)

    # Initialize Swagger UI
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/api/v1/apispec_1.json",
                "rule_filter": lambda rule: rule.rule.startswith("/api/v1"),
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/v1/apidocs/",
    }

    Swagger(app, config=swagger_config)

    return None
