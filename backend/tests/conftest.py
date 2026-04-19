"""Shared pytest fixtures for backend integration tests."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

TEST_DB_PATH = Path(__file__).resolve().parent / "test_mvp.sqlite3"
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["JWT_SECRET"] = "change-me-development-access-secret-32chars"
os.environ.setdefault("APP_ENV", "development")

import app.db.models  # noqa: F401
from app.db.base import Base
from app.db.models.campus import Campus
from app.db.models.category import Category
from app.db.models.post import Post
from app.db.models.user import User
from app.db.session import get_engine, get_session_factory
from app.main import app

TEST_TABLES = [
    Campus.__table__,
    Category.__table__,
    User.__table__,
    Post.__table__,
]


@pytest.fixture(scope="session")
def test_app() -> Any:
    """Provide the FastAPI app under test."""
    return app


@pytest.fixture(scope="session")
def engine():
    """Shared SQLAlchemy engine for tests."""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    engine = get_engine()
    Base.metadata.create_all(engine, tables=TEST_TABLES)
    yield engine
    Base.metadata.drop_all(engine, tables=list(reversed(TEST_TABLES)))
    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture(autouse=True)
def reset_database(engine) -> None:
    """Reset the test schema before each test and seed campuses."""
    Base.metadata.drop_all(engine, tables=list(reversed(TEST_TABLES)))
    Base.metadata.create_all(engine, tables=TEST_TABLES)

    session = get_session_factory()()
    try:
        session.add_all(
            [
                Campus(
                    name="Marist College",
                    slug="marist",
                    city="Poughkeepsie",
                    state="NY",
                    country="USA",
                    description="Primary test campus",
                ),
                Campus(
                    name="Other College",
                    slug="other",
                    city="Albany",
                    state="NY",
                    country="USA",
                    description="Secondary test campus",
                ),
            ],
        )
        session.commit()
    finally:
        session.close()


@pytest.fixture
def client(test_app) -> TestClient:
    """HTTP client for integration tests."""
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture
def db_session(engine) -> Session:
    """Direct database session for setup and assertions."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def campuses(db_session: Session) -> dict[str, Campus]:
    """Seeded campus rows keyed by slug."""
    return {
        campus.slug: campus
        for campus in db_session.scalars(select(Campus).order_by(Campus.name.asc()))
    }


def register_user(
    client: TestClient,
    *,
    email: str,
    username: str,
    campus_id: str,
    password: str = "correcthorsebattery",
    display_name: str = "Test User",
) -> dict[str, Any]:
    """Register a user and return the parsed JSON body."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
            "campus_id": campus_id,
            "display_name": display_name,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def registered_user(client: TestClient, campuses: dict[str, Campus]) -> dict[str, Any]:
    """Convenience fixture that returns a registered campus user."""
    return register_user(
        client,
        email="alice@example.com",
        username="alice_user",
        campus_id=str(campuses["marist"].id),
        display_name="Alice",
    )


@pytest.fixture
def auth_headers(registered_user: dict[str, Any]) -> dict[str, str]:
    """Authorization header for the registered user."""
    return {"Authorization": f"Bearer {registered_user['access_token']}"}
