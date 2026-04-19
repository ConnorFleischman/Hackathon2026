"""Campus lookup routes."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.core.dependencies import DbSession
from app.db.models.campus import Campus

router = APIRouter()


class CampusResponse(BaseModel):
    """Campus summary returned by list and detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    city: str | None
    state: str | None
    country: str | None
    description: str | None


@router.get("", response_model=list[CampusResponse])
def list_campuses(db: DbSession) -> list[Campus]:
    """Return all campuses ordered for user selection and lookup."""
    return list(db.scalars(select(Campus).order_by(Campus.name.asc())))


@router.get("/{campus_slug}", response_model=CampusResponse)
def get_campus(campus_slug: str, db: DbSession) -> Campus:
    """Return a single campus by slug."""
    campus = db.scalar(select(Campus).where(Campus.slug == campus_slug))
    if campus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campus not found",
        )
    return campus
