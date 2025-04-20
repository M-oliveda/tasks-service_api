"""Task model for user tasks."""
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.extensions import db
from app.schemas.task import PriorityEnum, StatusEnum

from .base import TimeStampedModel
from .tag import Tag


class TaskTag(db.Model):
    """Association table for Task-Tag many-to-many relationship."""

    __tablename__ = "task_tag"

    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("task.id"), primary_key=True, doc="The task's unique identifier."
    )
    tag_id: Mapped[UUID] = mapped_column(
        ForeignKey("tag.id"), primary_key=True, doc="The tag's unique identifier."
    )

    # Relationships
    task = relationship("Task", back_populates="task_tags")
    tag = relationship("Tag", back_populates="task_tags")


class Task(TimeStampedModel):
    """Task model."""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(
        String(128), nullable=False, doc="The task's title"
    )
    description: Mapped[str] = mapped_column(
        String(1024), nullable=True, doc="The task's description"
    )
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum),
        default=StatusEnum.TODO,
        nullable=False,
        doc="The task's status",
    )
    priority: Mapped[PriorityEnum] = mapped_column(
        Enum(PriorityEnum),
        default=PriorityEnum.MEDIUM,
        nullable=False,
        doc="The task's priority",
    )
    due_date: Mapped[datetime] = mapped_column(
        Date, nullable=True, doc="The task's due date"
    )

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"), nullable=False, doc="The user's unique identifier."
    )
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("category.id"),
        nullable=True,
        doc="The category's unique identifier.",
    )

    # Relationships
    user = relationship("User", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    task_tags = relationship(
        "TaskTag", back_populates="task", cascade="all, delete-orphan"
    )

    @property
    def tags(self) -> List[Tag]:
        """Get the tags associated with this task."""
        return [task_tag.tag for task_tag in self.task_tags]

    def add_tag(self, tag: Tag) -> None:
        """Add a tag to this task."""
        task_tag = TaskTag(task=self, tag=tag)
        db.session.add(task_tag)

    def remove_tag(self, tag: Tag) -> None:
        """Remove a tag from this task."""
        task_tag = (
            db.session.query(TaskTag).filter_by(task_id=self.id, tag_id=tag.id).first()
        )
        if task_tag:
            db.session.delete(task_tag)

    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        if not self.due_date:
            return False
        return self.due_date < datetime.now().date()

    def to_dict(self) -> dict:
        """Convert the task to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category": self.category.name if self.category else None,
            "tags": [tag.name for tag in self.tags],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_overdue": self.is_overdue(),
        }

    def __repr__(self) -> str:
        """Return a string representation of the task."""
        return f"<Task {self.title}>"
