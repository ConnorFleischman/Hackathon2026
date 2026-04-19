from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.enums import UserRole, UserStatus, db_enum
from app.utils.ids import new_uuid

if TYPE_CHECKING:
    from app.db.models.admin_action import AdminAction
    from app.db.models.audit_log import AuditLog
    from app.db.models.ban import Ban
    from app.db.models.comment import Comment
    from app.db.models.post import Post
    from app.db.models.post_flag import PostFlag
    from app.db.models.reaction import Reaction
    from app.db.models.report import Report
    from app.db.models.session import Session
    from app.db.models.user_location import UserLocation


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    campus_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("campuses.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        db_enum(UserRole, name="user_role"),
        nullable=False,
        server_default=text("'user'"),
    )
    status: Mapped[UserStatus] = mapped_column(
        db_enum(UserStatus, name="user_status"),
        nullable=False,
        server_default=text("'pending_verification'"),
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    sessions: Mapped[list["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    posts: Mapped[list["Post"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reactions: Mapped[list["Reaction"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    locations: Mapped[list["UserLocation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reports_made: Mapped[list["Report"]] = relationship(
        back_populates="reporter_user",
        foreign_keys="Report.reporter_user_id",
    )
    reports_about: Mapped[list["Report"]] = relationship(
        back_populates="target_user",
        foreign_keys="Report.target_user_id",
    )
    post_flags_created: Mapped[list["PostFlag"]] = relationship(
        back_populates="created_by_user",
        foreign_keys="PostFlag.created_by_user_id",
    )
    post_flags_reviewed: Mapped[list["PostFlag"]] = relationship(
        back_populates="reviewed_by_user",
        foreign_keys="PostFlag.reviewed_by_user_id",
    )
    bans_received: Mapped[list["Ban"]] = relationship(
        back_populates="user",
        foreign_keys="Ban.user_id",
    )
    bans_issued: Mapped[list["Ban"]] = relationship(
        back_populates="issued_by_user",
        foreign_keys="Ban.issued_by_user_id",
    )
    bans_lifted: Mapped[list["Ban"]] = relationship(
        back_populates="lifted_by_user",
        foreign_keys="Ban.lifted_by_user_id",
    )
    admin_actions: Mapped[list["AdminAction"]] = relationship(
        back_populates="admin_user",
        foreign_keys="AdminAction.admin_user_id",
    )
    admin_actions_targeted: Mapped[list["AdminAction"]] = relationship(
        back_populates="target_user",
        foreign_keys="AdminAction.target_user_id",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="actor_user")
