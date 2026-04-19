"""FastAPI dependencies shared across HTTP routes."""

from collections.abc import Generator, Mapping
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.enums import UserStatus
from app.db.models.user import User
from app.db.session import get_db_session


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped database session."""
    yield from get_db_session()


_bearer = HTTPBearer(auto_error=False)
UserClaims = dict[str, Any]


def _bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None or (credentials.scheme or "").lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = (credentials.credentials or "").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


async def get_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> str:
    """Extract the raw Bearer token or raise 401."""
    return _bearer_token(credentials)


async def get_current_user_claims(
    token: Annotated[str, Depends(get_bearer_token)],
) -> UserClaims:
    """Decode and validate the Bearer token used for API authentication."""
    try:
        return decode_token(token, expected_type="access")
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


async def get_optional_user_claims(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> UserClaims | None:
    """Return validated claims when a Bearer token is present."""
    if credentials is None or (credentials.scheme or "").lower() != "bearer":
        return None

    raw = (credentials.credentials or "").strip()
    if not raw:
        return None

    try:
        return decode_token(raw, expected_type="access")
    except InvalidTokenError:
        return None


async def get_verified_user(
    user: Annotated[UserClaims, Depends(get_current_user_claims)],
) -> UserClaims:
    """Reject tokens for accounts that are not marked as verified."""
    if user.get("is_verified") is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verified account required",
        )
    return user


async def get_active_user(
    user: Annotated[UserClaims, Depends(get_verified_user)],
) -> UserClaims:
    """Reject tokens for accounts whose status is not ``active``."""
    if str(user.get("status") or "").strip().lower() != UserStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )
    return user


def get_current_user_record(
    user_claims: Annotated[UserClaims, Depends(get_current_user_claims)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve the token subject to the current user record."""
    try:
        user_id = UUID(claims_get_sub(user_claims))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject is not a valid user id",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user was not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )

    return user


CurrentUserClaims = Annotated[UserClaims, Depends(get_current_user_claims)]
OptionalUserClaims = Annotated[UserClaims | None, Depends(get_optional_user_claims)]
VerifiedUserClaims = Annotated[UserClaims, Depends(get_verified_user)]
ActiveUserClaims = Annotated[UserClaims, Depends(get_active_user)]
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user_record)]


def claims_get_sub(user: Mapping[str, Any]) -> str:
    """Return the token subject as text or raise when it is absent."""
    sub = user.get("sub")
    if sub is None or sub == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject missing",
        )
    return str(sub)
