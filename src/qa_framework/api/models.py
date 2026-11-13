"""Pydantic models for API testing."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        extra="allow",
        str_strip_whitespace=True,
        validate_assignment=True,
        populate_by_name=True,
    )


class PaginatedResponse(BaseSchema, Generic[T]):
    """Standard paginated response wrapper."""

    data: list[T]
    page: int = 1
    per_page: int = 10
    total: int = 0
    total_pages: int = 0


class ErrorResponse(BaseSchema):
    """Standard error response."""

    error: str
    message: str | None = None
    code: str | None = None
    details: dict[str, Any] | None = None


class HealthCheck(BaseSchema):
    """Health check response."""

    status: str
    version: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: dict[str, str] | None = None


# --- JSONPlaceholder models ---


class User(BaseSchema):
    id: int
    name: str
    username: str
    email: str
    address: dict[str, Any] | None = None
    phone: str | None = None
    website: str | None = None
    company: dict[str, Any] | None = None


class Post(BaseSchema):
    id: int
    user_id: int = Field(alias="userId")
    title: str
    body: str


class Comment(BaseSchema):
    id: int
    post_id: int = Field(alias="postId")
    name: str
    email: str
    body: str


class Album(BaseSchema):
    id: int
    user_id: int = Field(alias="userId")
    title: str


class Photo(BaseSchema):
    id: int
    album_id: int = Field(alias="albumId")
    title: str
    url: str
    thumbnail_url: str = Field(alias="thumbnailUrl")


class Todo(BaseSchema):
    id: int
    user_id: int = Field(alias="userId")
    title: str
    completed: bool
