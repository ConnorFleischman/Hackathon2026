"""Password hashing and JWT helpers — interfaces stubbed until auth rollout."""

from typing import Any


def hash_password(password: str) -> str:
    """Return a stored password representation for the given plaintext password."""
    raise NotImplementedError


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return True if the plaintext password matches the stored hash."""
    raise NotImplementedError


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Create a signed JWT access token for the given subject (e.g. user id)."""
    raise NotImplementedError


def create_refresh_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Create a signed JWT refresh token for the given subject."""
    raise NotImplementedError


def decode_token(token: str) -> dict[str, Any]:
    """Validate and decode a JWT, returning its claims (including standard and custom fields)."""
    raise NotImplementedError
