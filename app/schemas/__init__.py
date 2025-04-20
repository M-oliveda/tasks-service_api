"""Base Pydantic schemas for data validation."""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, model_validator

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }


class ResponseSchema(BaseSchema, Generic[T]):
    """Standard response schema with data and metadata."""

    status: str = Field(description="Response status")
    message: Optional[str] = Field(default=None, description="Response message")
    data: Optional[T] = Field(default=None, description="Response data")


class PaginatedResponseSchema(ResponseSchema[List[T]]):
    """Paginated response schema for list endpoints."""

    page: int = Field(description="Current page number")
    per_page: int = Field(description="Number of items per page")
    total: int = Field(description="Total number of items")
    pages: int = Field(description="Total number of pages")

    @model_validator(mode="before")
    @classmethod
    def calculate_pages(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total number of pages."""
        total = values.get("total")
        per_page = values.get("per_page")

        if total is not None and per_page:
            values["pages"] = (total + per_page - 1) // per_page
        return values
