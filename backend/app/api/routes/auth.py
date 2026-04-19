"""Authentication routes."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import CurrentUser, DbSession
from app.core.security import create_access_token, hash_password, verify_password
from app.db.enums import UserRole, UserStatus
from app.db.models.campus import Campus
from app.db.models.user import User
from app.schemas.auth import AuthResponse, AuthenticatedUserResponse, LoginRequest, RegisterRequest

router = APIRouter()


def _auth_response(user: User) -> AuthResponse:
    """Build the standard login/register response payload."""
    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={
            "email": user.email,
            "username": user.username,
            "campus_id": str(user.campus_id) if user.campus_id is not None else None,
            "role": user.role.value,
            "status": user.status.value,
            "is_verified": user.is_verified,
        },
    )
    return AuthResponse(access_token=access_token, user=AuthenticatedUserResponse.model_validate(user))


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession) -> AuthResponse:
    """Create a new user account and return an access token."""
    campus = db.get(Campus, payload.campus_id)
    if campus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campus not found",
        )

    if db.scalar(select(User.id).where(User.email == payload.email)) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )
    if db.scalar(select(User.id).where(User.username == payload.username)) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken",
        )

    user = User(
        email=payload.email,
        username=payload.username,
        display_name=payload.display_name,
        campus_id=campus.id,
        password_hash=hash_password(payload.password),
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with that email or username already exists",
        ) from exc

    db.refresh(user)
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: DbSession) -> AuthResponse:
    """Verify credentials and issue a Bearer access token."""
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verified account required",
        )

    return _auth_response(user)


@router.get("/me", response_model=AuthenticatedUserResponse)
def get_me(user: CurrentUser) -> User:
    """Return the authenticated user's profile."""
    return user
