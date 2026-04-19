from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.enums import FlagDecision, FlagSource, FlagType, db_enum
from app.utils.ids import new_uuid

if TYPE_CHECKING:
    from app.db.models.comment import Comment
    from app.db.models.post import Post
    from app.db.models.user import User


class PostFlag(TimestampMixin, Base):
    __tablename__ = "post_flags"
    __table_args__ = (
        CheckConstraint(
            "(post_id IS NOT NULL AND comment_id IS NULL) OR (post_id IS NULL AND comment_id IS NOT NULL)",
            name="post_flag_single_target",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    post_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("posts.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    comment_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("comments.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    source: Mapped[FlagSource] = mapped_column(
        db_enum(FlagSource, name="flag_source"),
        nullable=False,
    )
    flag_type: Mapped[FlagType] = mapped_column(
        db_enum(FlagType, name="flag_type"),
        nullable=False,
    )
    decision: Mapped[FlagDecision] = mapped_column(
        db_enum(FlagDecision, name="flag_decision"),
        index=True,
        nullable=False,
        server_default=text("'pending_review'"),
    )
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    reviewed_by_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    post: Mapped["Post | None"] = relationship(back_populates="flags")
    comment: Mapped["Comment | None"] = relationship(back_populates="flags")
    created_by_user: Mapped["User | None"] = relationship(
        back_populates="post_flags_created",
        foreign_keys=[created_by_user_id],
    )
    reviewed_by_user: Mapped["User | None"] = relationship(
        back_populates="post_flags_reviewed",
        foreign_keys=[reviewed_by_user_id],
    )
