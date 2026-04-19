"""Integration tests for the active HTTP API."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.enums import ModerationStatus, PostType, VisibilityStatus
from app.db.models.post import Post
from app.db.models.user import User
from app.utils.clocks import utc_now
from tests.conftest import register_user


def ensure_utc(value: datetime) -> datetime:
    """Normalize SQLite-returned naive datetimes to UTC for assertions."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def test_app_startup_and_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Campus Social API",
        "database": "connected",
    }


def test_client_pages_are_served(client: TestClient) -> None:
    root = client.get("/", follow_redirects=False)
    login_page = client.get("/login.html")
    homepage = client.get("/Homepage.html")
    global_js = client.get("/js/global.js")

    assert root.status_code == 307
    assert root.headers["location"] == "/login.html"
    assert login_page.status_code == 200
    assert "ChatMuch" in login_page.text
    assert homepage.status_code == 200
    assert "Campus Feed" in homepage.text
    assert global_js.status_code == 200
    assert "window.ChatMuch" in global_js.text


def test_database_enums_store_lowercase_values() -> None:
    assert User.__table__.c.role.type.enums == ["user", "moderator", "admin", "super_admin", "org_account"]
    assert User.__table__.c.status.type.enums == ["pending_verification", "active", "suspended", "banned"]
    assert Post.__table__.c.type.type.enums == ["standard", "announcement", "event", "safety_alert"]
    assert Post.__table__.c.visibility_status.type.enums == [
        "pending_moderation",
        "visible",
        "hidden",
        "archived",
        "removed",
        "expired",
    ]
    assert Post.__table__.c.moderation_status.type.enums == [
        "pending",
        "approved",
        "flagged",
        "auto_hidden",
        "rejected",
    ]


def test_register_success(client: TestClient, campuses) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice_user",
            "password": "correcthorsebattery",
            "campus_id": str(campuses["marist"].id),
            "display_name": "Alice",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "alice@example.com"
    assert body["user"]["username"] == "alice_user"
    assert body["user"]["campus_id"] == str(campuses["marist"].id)
    assert body["user"]["status"] == "active"
    assert body["user"]["is_verified"] is True


def test_duplicate_registration_rejected(client: TestClient, campuses) -> None:
    register_user(
        client,
        email="alice@example.com",
        username="alice_user",
        campus_id=str(campuses["marist"].id),
    )

    duplicate_email = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice_user_two",
            "password": "correcthorsebattery",
            "campus_id": str(campuses["marist"].id),
            "display_name": "Alice",
        },
    )
    duplicate_username = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice2@example.com",
            "username": "alice_user",
            "password": "correcthorsebattery",
            "campus_id": str(campuses["marist"].id),
            "display_name": "Alice",
        },
    )

    assert duplicate_email.status_code == 409
    assert duplicate_email.json()["detail"] == "Email is already registered"
    assert duplicate_username.status_code == 409
    assert duplicate_username.json()["detail"] == "Username is already taken"


def test_login_success(client: TestClient, campuses) -> None:
    register_user(
        client,
        email="alice@example.com",
        username="alice_user",
        campus_id=str(campuses["marist"].id),
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "correcthorsebattery"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["user"]["email"] == "alice@example.com"


def test_login_invalid_password_rejected(client: TestClient, campuses) -> None:
    register_user(
        client,
        email="alice@example.com",
        username="alice_user",
        campus_id=str(campuses["marist"].id),
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_me_with_valid_token(client: TestClient, registered_user, auth_headers) -> None:
    response = client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == registered_user["user"]


def test_create_post_success(
    client: TestClient,
    db_session: Session,
    registered_user,
    auth_headers,
) -> None:
    response = client.post(
        "/api/v1/posts",
        json={"body": "Campus lunch special is great today."},
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == registered_user["user"]["id"]
    assert body["campus_id"] == registered_user["user"]["campus_id"]
    assert body["body"] == "Campus lunch special is great today."
    assert body["expires_at"] > body["created_at"]

    post = db_session.get(Post, UUID(body["id"]))
    assert post is not None
    assert str(post.user_id) == registered_user["user"]["id"]
    assert str(post.campus_id) == registered_user["user"]["campus_id"]
    assert post.visibility_status == VisibilityStatus.VISIBLE
    assert post.moderation_status == ModerationStatus.APPROVED
    assert ensure_utc(post.expires_at) > utc_now()


def test_create_post_unauthenticated_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/posts", json={"body": "Hello campus"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_feed_returns_same_campus_posts(
    client: TestClient,
    campuses,
    registered_user,
    auth_headers,
) -> None:
    client.post(
        "/api/v1/posts",
        json={"body": "Marist post"},
        headers=auth_headers,
    )

    other_user = register_user(
        client,
        email="bob@example.com",
        username="bob_user",
        campus_id=str(campuses["other"].id),
        display_name="Bob",
    )
    client.post(
        "/api/v1/posts",
        json={"body": "Other campus post"},
        headers={"Authorization": f"Bearer {other_user['access_token']}"},
    )

    response = client.get("/api/v1/feed", headers=auth_headers)

    assert response.status_code == 200
    posts = response.json()
    assert [post["body"] for post in posts] == ["Marist post"]
    assert all(post["campus_id"] == registered_user["user"]["campus_id"] for post in posts)


def test_feed_excludes_expired_posts(
    client: TestClient,
    db_session: Session,
    campuses,
    registered_user,
    auth_headers,
) -> None:
    active_post = client.post(
        "/api/v1/posts",
        json={"body": "Active campus post"},
        headers=auth_headers,
    )
    assert active_post.status_code == 201

    expired_post = Post(
        user_id=UUID(registered_user["user"]["id"]),
        campus_id=UUID(str(campuses["marist"].id)),
        type=PostType.STANDARD,
        visibility_status=VisibilityStatus.VISIBLE,
        moderation_status=ModerationStatus.APPROVED,
        title=None,
        body="Expired campus post",
        expires_at=utc_now() - timedelta(hours=1),
    )
    db_session.add(expired_post)
    db_session.commit()

    time.sleep(1)
    newest_post = client.post(
        "/api/v1/posts",
        json={"body": "Newest campus post"},
        headers=auth_headers,
    )
    assert newest_post.status_code == 201

    response = client.get("/api/v1/feed", headers=auth_headers)

    assert response.status_code == 200
    assert [post["body"] for post in response.json()] == [
        "Newest campus post",
        "Active campus post",
    ]
