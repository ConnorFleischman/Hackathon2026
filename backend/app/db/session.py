"""Synchronous SQLAlchemy engine and session setup."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _configured_database_url() -> str:
    """Return DATABASE_URL or raise with a clear configuration error."""
    database_url = settings.DATABASE_URL
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured; set it in environment variables or backend/.env.",
        )
    return database_url


def get_engine() -> Engine:
    """
    Return a lazily-initialized shared SQLAlchemy engine.

    Sync sessions keep request handlers and Alembic on the same connection model.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            _configured_database_url(),
            future=True,
            pool_pre_ping=True,
            pool_recycle=1800,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Return a process-wide session factory bound to the shared engine."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            class_=Session,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
    return _session_factory


def check_database_connection() -> None:
    """Open a connection and execute a trivial query so config errors fail clearly."""
    try:
        with get_engine().connect() as connection:
            connection.exec_driver_sql("SELECT 1")
    except SQLAlchemyError as exc:
        raise RuntimeError(
            "Database connection failed; check DATABASE_URL and confirm the PostgreSQL host is reachable.",
        ) from exc


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and always closes it."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Generator[Session, None, None]:
    """Backward-compatible alias used by existing dependencies."""
    yield from get_db()


__all__ = [
    "check_database_connection",
    "get_db",
    "get_db_session",
    "get_engine",
    "get_session_factory",
]
