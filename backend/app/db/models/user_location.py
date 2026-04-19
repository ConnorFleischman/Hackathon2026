from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import LocationSource
from app.utils.ids import new_uuid

if TYPE_CHECKING:
    from app.db.models.campus import Campus
    from app.db.models.user import User


class UserLocation(Base):
    __tablename__ = "user_locations"

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
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    source: Mapped[LocationSource] = mapped_column(
        Enum(LocationSource, name="location_source"),
        nullable=False,
        server_default=text("'gps'"),
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="locations")
    campus: Mapped["Campus | None"] = relationship(back_populates="locations")
