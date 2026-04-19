from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.enums import VisibilityStatus
from app.utils.ids import new_uuid

if TYPE_CHECKING:
    from app.db.models.post import Post
    from app.db.models.post_flag import PostFlag
    from app.db.models.report import Report
    from app.db.models.user import User


class Comment(TimestampMixin, Base):
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    post_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("posts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    parent_comment_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("comments.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    visibility_status: Mapped[VisibilityStatus] = mapped_column(
        Enum(VisibilityStatus, name="visibility_status"),
        nullable=False,
        server_default=text("'visible'"),
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)

    post: Mapped["Post"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship(back_populates="comments")
    parent_comment: Mapped["Comment | None"] = relationship(remote_side=[id], back_populates="replies")
    replies: Mapped[list["Comment"]] = relationship(back_populates="parent_comment", cascade="all, delete-orphan")
    flags: Mapped[list["PostFlag"]] = relationship(back_populates="comment", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="target_comment")
