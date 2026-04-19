"""Authentication request and response schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.enums import UserRole, UserStatus


class AuthenticatedUserResponse(BaseModel):
    """Public user fields returned by auth endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    username: str
    display_name: str | None
    campus_id: UUID | None
    role: UserRole
    status: UserStatus
    is_verified: bool


class RegisterRequest(BaseModel):
    """Request body for account registration."""

    email: str = Field(min_length=3, max_length=255)
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    campus_id: UUID
    display_name: str | None = Field(default=None, max_length=120)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("email must be a valid email address")
        return normalized

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("username must not be blank")
        if not normalized.replace("_", "").isalnum():
            raise ValueError("username may only contain letters, numbers, and underscores")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value.strip() != value:
            raise ValueError("password must not start or end with whitespace")
        return value

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class LoginRequest(BaseModel):
    """Request body for login."""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("email must be a valid email address")
        return normalized


class AuthResponse(BaseModel):
    """Bearer token response returned by register and login."""

    access_token: str
    token_type: str = "bearer"
    user: AuthenticatedUserResponse
