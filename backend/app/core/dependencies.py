"""FastAPI dependencies (DB sessions, current user, etc.)."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import get_db_session


def get_db() -> Generator[Session, None, None]:
    """Yields a database session; transaction boundaries belong in services."""
    yield from get_db_session()
