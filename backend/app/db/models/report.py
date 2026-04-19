from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.enums import ReportStatus, ReportTargetType, db_enum
from app.utils.ids import new_uuid

if TYPE_CHECKING:
    from app.db.models.comment import Comment
    from app.db.models.post import Post
    from app.db.models.user import User


class Report(TimestampMixin, Base):
    __tablename__ = "reports"
    __table_args__ = (
        CheckConstraint(
            "(target_post_id IS NOT NULL)::int + (target_comment_id IS NOT NULL)::int + (target_user_id IS NOT NULL)::int = 1",
            name="report_single_target",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    reporter_user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    target_type: Mapped[ReportTargetType] = mapped_column(
        db_enum(ReportTargetType, name="report_target_type"),
        index=True,
        nullable=False,
    )
    target_post_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("posts.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    target_comment_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("comments.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    target_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        db_enum(ReportStatus, name="report_status"),
        index=True,
        nullable=False,
        server_default=text("'open'"),
    )
    resolver_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    reporter_user: Mapped["User"] = relationship(
        back_populates="reports_made",
        foreign_keys=[reporter_user_id],
    )
    target_user: Mapped["User | None"] = relationship(
        back_populates="reports_about",
        foreign_keys=[target_user_id],
    )
    target_post: Mapped["Post | None"] = relationship(backref="reports", foreign_keys=[target_post_id])
    target_comment: Mapped["Comment | None"] = relationship(
        back_populates="reports",
        foreign_keys=[target_comment_id],
    )
