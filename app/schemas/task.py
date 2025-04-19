"""Pydantic schemas for Task model."""
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas import BaseSchema, ResponseSchema


class StatusEnum(Enum):
    """Task status enumeration."""

    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    READY = "Ready"


class PriorityEnum(Enum):
    """Task priority enumeration."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskBase(BaseSchema):
    """Base schema for Task model."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="The title of the task",
        examples=["Finish project", "Call client"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1024,
        description="Optional description of the task",
        examples=["Detailed explanation about the task"],
    )
    status: StatusEnum = Field(
        default=StatusEnum.TODO,
        description="The status of the task",
        examples=["todo", "in_progress", "done"],
    )
    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        description="The priority of the task",
        examples=["low", "medium", "high"],
    )
    due_date: Optional[date] = Field(
        default=None, description="The due date of the task", examples=["2025-04-30"]
    )
    category_id: Optional[UUID] = Field(
        default=None, description="ID of the category the task belongs to", examples=[1]
    )


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    tag_ids: Optional[List[UUID]] = Field(
        default_factory=list,
        description="List of tag IDs to assign to the task",
        examples=[[1, 2, 3]],
    )


class TaskUpdate(BaseSchema):
    """Schema for updating a task."""

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=128,
        description="The new title of the task",
        examples=["Update resume"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1024,
        description="The new description of the task",
        examples=["Updated task details"],
    )
    status: Optional[StatusEnum] = Field(
        None, description="Updated status of the task", examples=["in_progress"]
    )
    priority: Optional[PriorityEnum] = Field(
        None, description="Updated priority of the task", examples=["high"]
    )
    due_date: Optional[date] = Field(
        None, description="New due date of the task", examples=["2025-05-01"]
    )
    category_id: Optional[UUID] = Field(
        None, description="Updated category ID", examples=[2]
    )
    tag_ids: Optional[List[UUID]] = Field(
        default=None, description="Updated list of tag IDs", examples=[[3, 4]]
    )

    class ConfigDict:
        """Configuration for TaskUpdate schema."""

        extra = "forbid"


class TaskTagUpdate(BaseSchema):
    """Schema for updating task tags."""

    tag_ids: List[UUID] = Field(
        ..., description="List of tag IDs to assign", examples=[[1, 2]]
    )


class TaskInDB(TaskBase):
    """Schema for task data from database."""

    id: UUID = Field(..., description="Task ID", examples=[1])
    user_id: UUID = Field(
        ..., description="ID of the user who owns the task", examples=[42]
    )
    created_at: datetime = Field(
        ..., description="Creation timestamp", examples=[datetime.now()]
    )
    updated_at: datetime = Field(
        ..., description="Last update timestamp", examples=[datetime.now()]
    )
    is_overdue: bool = Field(
        ..., description="Whether the task is overdue", examples=[False]
    )
    category: Optional[str] = Field(
        default=None, description="Name of the category", examples=["Work"]
    )
    tags: List[str] = Field(
        default_factory=list,
        description="List of tag names",
        examples=[["urgent", "client"]],
    )

    @field_validator("is_overdue", mode="before")
    @classmethod
    def calculate_overdue(cls, v, values):
        """Calculate if the task is overdue if not provided."""
        if v is not None:
            return v
        due_date = values.get("due_date")
        if due_date:
            return due_date < datetime.now().date()
        return False


class TaskResponse(ResponseSchema[TaskInDB]):
    """Response schema for a single task."""

    pass


class TasksResponse(ResponseSchema[List[TaskInDB]]):
    """Response schema for multiple tasks."""

    pass


class TaskSearchParams(BaseSchema):
    """Schema for task search parameters."""

    title: Optional[str] = Field(
        None, description="Filter by task title", examples=["Report"]
    )
    status: Optional[StatusEnum] = Field(
        None, description="Filter by status", examples=["done"]
    )
    priority: Optional[PriorityEnum] = Field(
        None, description="Filter by priority", examples=["low"]
    )
    category_id: Optional[UUID] = Field(
        None, description="Filter by category ID", examples=[1]
    )
    tag_ids: Optional[List[UUID]] = Field(
        None, description="Filter by tag IDs", examples=[[2, 5]]
    )
    is_overdue: Optional[bool] = Field(
        None, description="Filter by overdue tasks", examples=[True]
    )
    due_date_from: Optional[date] = Field(
        None, description="Start of due date range", examples=["2025-04-01"]
    )
    due_date_to: Optional[date] = Field(
        None, description="End of due date range", examples=["2025-04-30"]
    )
    sort_by: Optional[str] = Field(
        default="created_at", description="Field to sort by", examples=["due_date"]
    )
    sort_order: Optional[str] = Field(
        default="desc", description="Sort order: 'asc' or 'desc'", examples=["asc"]
    )
    page: int = Field(default=1, description="Pagination page number", examples=[1])
    per_page: int = Field(
        default=20, description="Number of tasks per page", examples=[10]
    )

    @field_validator("due_date_to")
    @classmethod
    def validate_due_date_range(cls, v, values):
        """Validate that due_date_to is after due_date_from."""
        due_date_from = values.get("due_date_from")
        if v and due_date_from:
            if v < due_date_from:
                raise ValueError("due_date_to must be after due_date_from")
        return v

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        """Validate sort_by field."""
        valid_fields = [
            "created_at",
            "updated_at",
            "due_date",
            "priority",
            "status",
            "title",
        ]
        if v not in valid_fields:
            raise ValueError(f"sort_by must be one of: {', '.join(valid_fields)}")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        """Validate sort_order field."""
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be either 'asc' or 'desc'")
        return v
