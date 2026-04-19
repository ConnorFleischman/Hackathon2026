from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, String, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.enums import ModerationStatus, PostType, VisibilityStatus
from app.utils.ids import new_uuid

if TYPE_CHECKING:
    from app.db.models.campus import Campus
    from app.db.models.category import Category
    from app.db.models.comment import Comment
    from app.db.models.post_flag import PostFlag
    from app.db.models.reaction import Reaction
    from app.db.models.user import User


class Post(TimestampMixin, Base):
    __tablename__ = "posts"
    __table_args__ = (
        CheckConstraint("event_end_at IS NULL OR event_start_at IS NULL OR event_end_at >= event_start_at", name="post_event_window_valid"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    campus_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("campuses.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    category_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("categories.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    type: Mapped[PostType] = mapped_column(
        Enum(PostType, name="post_type"),
        index=True,
        nullable=False,
        server_default=text("'standard'"),
    )
    visibility_status: Mapped[VisibilityStatus] = mapped_column(
        Enum(VisibilityStatus, name="visibility_status"),
        index=True,
        nullable=False,
        server_default=text("'pending_moderation'"),
    )
    moderation_status: Mapped[ModerationStatus] = mapped_column(
        Enum(ModerationStatus, name="moderation_status"),
        index=True,
        nullable=False,
        server_default=text("'pending'"),
    )
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    event_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    event_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    event_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="posts")
    campus: Mapped["Campus | None"] = relationship(back_populates="posts")
    category: Mapped["Category | None"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    reactions: Mapped[list["Reaction"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    flags: Mapped[list["PostFlag"]] = relationship(back_populates="post", cascade="all, delete-orphan")
