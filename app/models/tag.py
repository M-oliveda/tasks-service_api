"""Tag model for task labeling."""
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import TimeStampedModel


class Tag(TimeStampedModel):
    """Tag model for tasks."""

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, doc="The tag's unique identifier."
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False, doc="The tag's name.")

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"), nullable=False, doc="The user's unique identifier."
    )

    # Relationships
    user = relationship("User", back_populates="tags")
    task_tags = relationship(
        "TaskTag", back_populates="tag", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """Convert the tag to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        """Return a string representation of the tag."""
        return f"<Tag {self.name}>"
