from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.utils.ids import new_uuid

if TYPE_CHECKING:
    from app.db.models.user import User


class AdminAction(TimestampMixin, Base):
    __tablename__ = "admin_actions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    admin_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    target_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    action_type: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    admin_user: Mapped["User | None"] = relationship(
        back_populates="admin_actions",
        foreign_keys=[admin_user_id],
    )
    target_user: Mapped["User | None"] = relationship(
        back_populates="admin_actions_targeted",
        foreign_keys=[target_user_id],
    )
