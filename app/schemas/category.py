"""Pydantic schemas for Category model."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.schemas import BaseSchema, ResponseSchema


class CategoryBase(BaseSchema):
    """Base schema for Category model."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="The name of the category",
        examples=["Work", "Personal"],
    )
    description: Optional[str] = Field(
        None,
        max_length=256,
        description="A brief description of the category",
        examples=["Tasks related to work"],
    )


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    pass


class CategoryUpdate(BaseSchema):
    """Schema for updating a category."""

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=64,
        description="The updated name of the category",
        examples=["Work", "Errands"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=256,
        description="The updated description of the category",
        examples=["Updated description for category"],
    )

    class ConfigDict:
        """Configuration for CategoryUpdate schema."""

        extra = "forbid"


class CategoryInDB(CategoryBase):
    """Schema for category data from database."""

    id: UUID = Field(description="The unique identifier of the category", examples=[1])
    user_id: UUID = Field(
        description="The ID of the user who owns this category", examples=[42]
    )
    created_at: datetime = Field(
        description="The date and time the category was created",
        examples=[datetime.now()],
    )
    updated_at: datetime = Field(
        description="The date and time the category was last updated",
        examples=[datetime.now()],
    )


class CategoryResponse(ResponseSchema[CategoryInDB]):
    """Response schema for category endpoints."""

    pass


class CategoriesResponse(ResponseSchema[List[CategoryInDB]]):
    """Response schema for multiple categories."""

    pass


class CategoryStats(CategoryInDB):
    """Schema for category with task stats."""

    task_count: int = Field(
        description="The total number of tasks in the category", examples=[10]
    )
    completed_count: int = Field(
        description="The number of completed tasks", examples=[7]
    )
    overdue_count: int = Field(description="The number of overdue tasks", examples=[2])

    @property
    def completion_rate(self) -> float:
        """Calculate the completion rate for tasks in this category."""
        if self.task_count == 0:
            return 100.0
        return round((self.completed_count / self.task_count) * 100, 2)


class CategoryStatsResponse(ResponseSchema[List[CategoryStats]]):
    """Response schema for category statistics."""

    pass
