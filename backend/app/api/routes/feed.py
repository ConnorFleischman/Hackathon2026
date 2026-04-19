"""Campus feed routes."""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import Select, select

from app.core.dependencies import CurrentUser, DbSession
from app.db.enums import ModerationStatus, VisibilityStatus
from app.db.models.post import Post
from app.schemas.post import PostResponse
from app.utils.clocks import utc_now

router = APIRouter()


@router.get("", response_model=list[PostResponse])
def get_feed(
    user: CurrentUser,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=100),
) -> list[Post]:
    """Return the authenticated user's active campus feed, newest first."""
    if user.campus_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to a campus to view the feed",
        )

    statement: Select[tuple[Post]] = (
        select(Post)
        .where(
            Post.campus_id == user.campus_id,
            Post.visibility_status == VisibilityStatus.VISIBLE.value,
            Post.moderation_status == ModerationStatus.APPROVED.value,
            Post.expires_at > utc_now(),
        )
        .order_by(Post.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(statement))
