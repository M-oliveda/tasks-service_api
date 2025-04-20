"""User model for authentication and authorization."""
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.schemas.user import RoleEnum
from app.utils.security import check_password, hash_password

from .base import TimeStampedModel


class User(TimeStampedModel):
    """User model."""

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, doc="The user's unique identifier."
    )
    username: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True, doc="The user's username."
    )
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, doc="The user's email address."
    )
    password_hash: Mapped[str] = mapped_column(
        String(128), nullable=False, doc="The user's password hash."
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum), default=RoleEnum.USER, nullable=False, doc="The user's role."
    )
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, doc="The user's last login timestamp."
    )

    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    categories = relationship(
        "Category", back_populates="user", cascade="all, delete-orphan"
    )
    tags = relationship("Tag", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        """Initialize a new user."""
        password = kwargs.pop("password", None)
        super(User, self).__init__(**kwargs)
        if password:
            self.set_password(password)

    def set_password(self, password: str) -> None:
        """Set the user's password hash."""
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return check_password(password, self.password_hash)

    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.now(timezone.utc)
        self.save()

    def to_dict(self) -> dict:
        """Convert the user to a dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self) -> str:
        """Return a string representation of the user."""
        return f"<User {self.username}>"
