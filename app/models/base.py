"""Database connection and models setup."""
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column

from app.core.extensions import db


class CRUDMixin:
    """Mixin that adds convenience methods for CRUD operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it to the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if commit:
            return self.save()
        return self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        if commit:
            db.session.commit()
        return self


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        """Return snake-case of the class name."""
        return cls.__name__.lower()

    def __init__(self, **kwargs):
        """Allow initialization with keyword arguments."""
        super().__init__()
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(f"Invalid keyword argument: {key}")
            setattr(self, key, value)


class TimeStampedModel(Model):
    """Base model class that includes timestamp fields."""

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="The created at date.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="The updated at date.",
    )
