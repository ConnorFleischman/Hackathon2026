"""Password hashing and access-token helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core.config import get_settings

_hasher = PasswordHasher()
TokenType = Literal["access"]


def _require_secret(secret: str, *, purpose: str) -> str:
    """Return a trimmed secret or raise a configuration error."""
    resolved = secret.strip()
    if not resolved:
        raise RuntimeError(f"{purpose} secret is not configured")
    return resolved


def hash_password(password: str) -> str:
    """Return an Argon2id hash suitable for storing in the users table."""
    return _hasher.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return ``True`` when a plaintext password matches its stored hash."""
    try:
        _hasher.verify(password_hash, plain_password)
        return True
    except (VerifyMismatchError, InvalidHashError):
        return False


def _utc_now() -> datetime:
    """Return the current UTC timestamp used for token timestamps."""
    return datetime.now(timezone.utc)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Create a signed access token for a user id and related identity claims."""
    settings = get_settings()
    secret = _require_secret(settings.JWT_SECRET, purpose="Access token")
    now = _utc_now()
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def decode_token(
    token: str,
    *,
    secret: str | None = None,
    algorithms: list[str] | None = None,
    audience: str | list[str] | None = None,
    issuer: str | None = None,
    options: dict[str, Any] | None = None,
    expected_type: TokenType | None = None,
) -> dict[str, Any]:
    """Decode a signed access token and optionally enforce its ``type`` claim."""
    settings = get_settings()
    resolved_secret = _require_secret(
        secret if secret is not None else settings.JWT_SECRET,
        purpose="JWT decode",
    )
    decode_algorithms = algorithms if algorithms is not None else [settings.JWT_ALGORITHM]
    decode_options: dict[str, Any] = {"verify_signature": True, "require": ["exp", "sub"]}
    if options:
        decode_options.update(options)

    claims = jwt.decode(
        token,
        resolved_secret,
        algorithms=decode_algorithms,
        audience=audience,
        issuer=issuer,
        options=decode_options,
    )
    if expected_type is not None and claims.get("type") != expected_type:
        raise jwt.InvalidTokenError(
            f"Expected token type {expected_type!r}, got {claims.get('type')!r}",
        )
    return claims
