"""Database initialization."""
from app.db.db import CRUDMixin, Model, TimeStampedModel

__all__ = ["CRUDMixin", "Model", "TimeStampedModel"]
