"""Category model for task categorization."""
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import TimeStampedModel


class Category(TimeStampedModel):
    """Category model for tasks."""

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, doc="The category's unique identifier."
    )
    name: Mapped[str] = mapped_column(
        String(64), nullable=False, doc="The category's name."
    )
    description: Mapped[str] = mapped_column(
        String(256), nullable=True, doc="The category's description."
    )

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="categories")
    tasks = relationship("Task", back_populates="category")

    def to_dict(self) -> dict:
        """Convert the category to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        """Return a string representation of the category."""
        return f"<Category {self.name}>"
