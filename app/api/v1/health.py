"""Health check endpoint for the TasksService API."""
from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from app.core.extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/")


@health_bp.get("/health")
def health_check():
    """
    Health check endpoint.

    ---
    tags:
      - Health
    responses:
      200:
        description: Service is healthy
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: ok
                version:
                  type: string
                  example: 1.0.0
                db_connection:
                  type: boolean
                  example: true
    """
    db_connection = False
    try:
        db.session.execute(text("SELECT 1"))
        db_connection = True
        current_app.logger.info("DB connection successful")
    except Exception as e:
        current_app.logger.error("DB connection error:", e)

    return jsonify({"status": "ok", "version": "0.1.0", "db_connection": db_connection})
