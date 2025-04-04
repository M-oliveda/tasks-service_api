"""Logging configuration for the TasksService API."""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def configure_logging(app):
    """
    Configure logging for the application.

    Args:
        app: Flask application instance
    """
    log_level = app.config.get("LOG_LEVEL", "INFO")

    # Set log level
    level = getattr(logging, log_level)

    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.mkdir("logs")

    # Create formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    # Configure Flask logger
    app.logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)

    # File handler
    file_handler = RotatingFileHandler(
        "logs/tasksservice.log", maxBytes=10485760, backupCount=10  # 10MB
    )
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    # SQLAlchemy logging
    if level == logging.DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    app.logger.info("Logging configured with level: %s", log_level)
