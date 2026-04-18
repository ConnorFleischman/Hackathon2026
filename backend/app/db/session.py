"""Engine and session factory; used by dependencies and Alembic."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _configured_database_url() -> str:
    url = settings.DATABASE_URL
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not configured; set it in the environment before using the database.",
        )
    return url


def get_engine() -> Engine:
    """Return the shared SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(_configured_database_url(), pool_pre_ping=True)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Return the session factory bound to the shared engine."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
        )
    return _session_factory


def get_db_session() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI Depends."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
