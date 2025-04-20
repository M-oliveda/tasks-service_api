"""Pydantic schemas for User model."""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from app.schemas import BaseSchema, ResponseSchema


class RoleEnum(Enum):
    """User role enumeration."""

    ADMIN = "admin"
    USER = "user"


class UserBase(BaseSchema):
    """Base schema for User model."""

    username: str = Field(
        min_length=3,
        max_length=64,
        description="The username of the user",
        examples=["admin", "user"],
    )
    email: EmailStr = Field(
        description="The user email", examples=["example@example.com"]
    )
    role: RoleEnum = Field(description="The user role", examples=["admin", "user"])


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(
        min_length=8, description="The user password", examples=["password123"]
    )
    confirm_password: str = Field(
        min_length=8, description="The user password", examples=["password123"]
    )

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: FieldValidationInfo) -> str:
        """Validate that password and confirm_password match."""
        password = info.data.get("password")  # Access sibling fields
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=64,
        description="The username of the user",
        examples=["admin", "user"],
    )
    email: Optional[EmailStr] = Field(
        default=None, description="The user email", examples=["example@example.com"]
    )
    password: Optional[str] = Field(
        default=None,
        min_length=8,
        description="The user password",
        examples=["password123"],
    )

    class ConfigDict:
        """Configuration for UserUpdate schema."""

        extra = "forbid"


class UserInDB(UserBase):
    """Schema for user data from database."""

    id: UUID = Field(
        description="The user ID", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    created_at: datetime = Field(
        description="The user creation date", examples=[datetime.now()]
    )
    updated_at: datetime = Field(
        description="The user update date", examples=[datetime.now()]
    )
    last_login: Optional[datetime] = Field(
        default=None, description="The user last login date", examples=[datetime.now()]
    )


class UserResponse(ResponseSchema[UserInDB]):
    """Response schema for user endpoints."""

    pass


class UsersResponse(ResponseSchema[List[UserInDB]]):
    """Response schema for multiple users."""

    pass


class UserLogin(BaseSchema):
    """Schema for user login."""

    username: str = Field(description="The user username", examples=["admin", "user"])
    password: str = Field(description="The user password", examples=["password123"])


class TokenResponse(BaseSchema):
    """Schema for JWT token response."""

    access_token: str = Field(
        description="The JWT access token",
        examples=["eyJhbGciOiJIU.eyJzdWIiOiIxMjM0NTY3ODkwIiwQ.SflKxwRJSMeKKF2QT4fwp5c"],
    )
    token_type: str = Field(description="The token type", examples=["bearer"])
    expires_in: int = Field(description="The token expiration time", examples=[3600])
