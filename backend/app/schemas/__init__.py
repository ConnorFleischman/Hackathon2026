"""Schema modules used by the HTTP API."""

from app.schemas.auth import AuthResponse, AuthenticatedUserResponse, LoginRequest, RegisterRequest
from app.schemas.post import PostCreateRequest, PostResponse

__all__ = [
    "AuthResponse",
    "AuthenticatedUserResponse",
    "LoginRequest",
    "PostCreateRequest",
    "PostResponse",
    "RegisterRequest",
]
