"""
SQLAlchemy ORM models.

Import concrete model modules here so metadata is registered on `Base.metadata`
and Alembic sees all tables when `import app.db.models` runs.
"""

from app.db.base import Base

__all__ = ["Base"]
