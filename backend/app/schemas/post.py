"""Post request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PostCreateRequest(BaseModel):
    """Request body for creating a short text post."""

    body: str = Field(min_length=1, max_length=500)

    @field_validator("body")
    @classmethod
    def normalize_body(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("body must not be blank")
        return normalized


class PostResponse(BaseModel):
    """Compact post representation returned by create and detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    campus_id: UUID | None
    body: str
    created_at: datetime
    expires_at: datetime
