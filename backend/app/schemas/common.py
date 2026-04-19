"""Shared API response envelope."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard success/error envelope for HTTP responses."""

    success: bool = True
    data: T | None = None
    error: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
