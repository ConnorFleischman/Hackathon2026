"""Post creation and lookup routes."""

from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.db.enums import ModerationStatus, PostType, VisibilityStatus
from app.db.models.campus import Campus
from app.db.models.post import Post
from app.db.models.user import User
from app.schemas.post import PostCreateRequest, PostResponse
from app.utils.clocks import utc_now

router = APIRouter()

POST_TTL_HOURS = 24


def _resolve_user_campus(db: DbSession, user: User) -> Campus:
    """Load the posting campus directly from the authenticated user record."""
    if user.campus_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to a campus to create posts",
        )

    campus = db.get(Campus, user.campus_id)
    if campus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campus not found",
        )
    return campus


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreateRequest, db: DbSession, user: CurrentUser) -> Post:
    """Create a short text post for the current user's campus."""
    campus = _resolve_user_campus(db, user)
    expires_at = utc_now() + timedelta(hours=POST_TTL_HOURS)

    post = Post(
        user_id=user.id,
        campus_id=campus.id,
        type=PostType.STANDARD.value,
        visibility_status=VisibilityStatus.VISIBLE.value,
        moderation_status=ModerationStatus.APPROVED.value,
        title=None,
        body=payload.body,
        expires_at=expires_at,
        category_id=None,
        event_name=None,
        event_location=None,
        event_start_at=None,
        event_end_at=None,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: UUID, db: DbSession) -> Post:
    """Return a single visible, non-expired post."""
    post = db.scalar(
        select(Post).where(
            Post.id == post_id,
            Post.visibility_status == VisibilityStatus.VISIBLE.value,
            Post.moderation_status == ModerationStatus.APPROVED.value,
            Post.expires_at > utc_now(),
        ),
    )
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post
