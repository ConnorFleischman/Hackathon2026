from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.enums import ReactionType, db_enum
from app.utils.ids import new_uuid

if TYPE_CHECKING:
    from app.db.models.post import Post
    from app.db.models.user import User


class Reaction(TimestampMixin, Base):
    __tablename__ = "reactions"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_reactions_post_user"),)

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
    reaction_type: Mapped[ReactionType] = mapped_column(
        db_enum(ReactionType, name="reaction_type"),
        nullable=False,
        server_default=text("'like'"),
    )

    post: Mapped["Post"] = relationship(back_populates="reactions")
    user: Mapped["User"] = relationship(back_populates="reactions")
