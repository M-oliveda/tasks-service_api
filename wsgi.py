"""WSGI entry point for the TasksService API."""
import os

from app import create_app

# Get configuration from environment
config_name = os.getenv("FLASK_ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    app.run(port=8000)
