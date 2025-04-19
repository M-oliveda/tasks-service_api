"""Pydantic schemas for Tag model."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.schemas import BaseSchema, ResponseSchema


class TagBase(BaseSchema):
    """Base schema for Tag model."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="The name of the tag",
        examples=["urgent", "important", "low-priority"],
    )


class TagCreate(TagBase):
    """Schema for creating a new tag."""

    pass


class TagUpdate(BaseSchema):
    """Schema for updating a tag."""

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=64,
        description="The updated name of the tag",
        examples=["updated-tag-name"],
    )

    class ConfigDict:
        """Configuration for TagUpdate schema."""

        extra = "forbid"


class TagInDB(TagBase):
    """Schema for tag data from database."""

    id: UUID = Field(description="The unique identifier of the tag", examples=[1])
    user_id: UUID = Field(
        description="The ID of the user who owns this tag", examples=[42]
    )
    created_at: datetime = Field(
        description="Timestamp when the tag was created", examples=[datetime.now()]
    )
    updated_at: datetime = Field(
        description="Timestamp when the tag was last updated", examples=[datetime.now()]
    )


class TagResponse(ResponseSchema[TagInDB]):
    """Response schema for tag endpoints."""

    pass


class TagsResponse(ResponseSchema[List[TagInDB]]):
    """Response schema for multiple tags."""

    pass


class TagStats(TagInDB):
    """Schema for tag with usage statistics."""

    task_count: int = Field(description="Number of tasks using this tag", examples=[5])

    class ConfigDict:
        """Additional configuration for TagStats schema."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "urgent",
                "user_id": 1,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "task_count": 5,
            }
        }


class TagStatsResponse(ResponseSchema[List[TagStats]]):
    """Response schema for tag statistics."""

    pass
