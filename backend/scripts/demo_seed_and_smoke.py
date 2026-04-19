"""Run a live smoke test against the local app and seed demo feed data."""

# This file also provides a watched path that can trigger local reloads during demos.

from __future__ import annotations

import argparse
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

import httpx
from sqlalchemy import delete

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.models.user import User
from app.db.session import get_session_factory


PASSWORD = "DemoPass123!"
PAGE_PATHS = [
    "/",
    "/login.html",
    "/Homepage.html",
    "/Messages.html",
    "/Profile.html",
    "/js/global.js",
    "/js/profile.js",
    "/css/Homepage.css",
]


@dataclass
class DemoUser:
    label: str
    email: str
    username: str
    display_name: str
    access_token: str


def request_json(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    token: str | None = None,
    expected_status: int = 200,
    json: dict | None = None,
) -> dict | list:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = client.request(method, path, headers=headers, json=json)
    if response.status_code != expected_status:
        raise RuntimeError(
            f"{method} {path} returned {response.status_code}: {response.text}"
        )
    return response.json()


def request_page(
    client: httpx.Client,
    path: str,
    *,
    expected_status: int,
    follow_redirects: bool = True,
) -> None:
    response = client.get(path, follow_redirects=follow_redirects)
    if response.status_code != expected_status:
        raise RuntimeError(f"GET {path} returned {response.status_code}: {response.text}")


def create_demo_users(client: httpx.Client, campus_id: str, suffix: str) -> list[DemoUser]:
    specs = [
        ("Host", "demo_host", "Avery Host"),
        ("Events", "demo_events", "Jordan Events"),
        ("Safety", "demo_safety", "Taylor Safety"),
    ]
    users: list[DemoUser] = []

    for label, username_prefix, display_name in specs:
        email = f"{username_prefix}_{suffix}@example.com"
        username = f"{username_prefix}_{suffix}"
        payload = {
            "email": email,
            "username": username,
            "display_name": display_name,
            "campus_id": campus_id,
            "password": PASSWORD,
        }
        body = request_json(
            client,
            "POST",
            "/api/v1/auth/register",
            expected_status=201,
            json=payload,
        )
        users.append(
            DemoUser(
                label=label,
                email=email,
                username=username,
                display_name=display_name,
                access_token=body["access_token"],
            )
        )

    return users


def cleanup_previous_demo_users() -> None:
    session = get_session_factory()()
    try:
        session.execute(delete(User).where(User.email.like("demo_%@example.com")))
        session.commit()
    finally:
        session.close()


def seed_posts(client: httpx.Client, users: list[DemoUser]) -> list[dict]:
    posts_by_user = {
        users[0].access_token: [
            "Welcome to ChatMuch demo day. Drop a quick hello if you are checking out the app.",
            "Student center meetup at 5 PM for anyone curious about clubs, hackathons, and upcoming campus events.",
        ],
        users[1].access_token: [
            "Open mic night is back this Thursday in the dining hall lounge. Signups start at 6:30 PM.",
            "Hackathon prep session tomorrow after classes. Bring your laptop and any project ideas you want feedback on.",
        ],
        users[2].access_token: [
            "Campus safety reminder: the library side entrance is closed tonight, so use the main quad entrance after 8 PM.",
            "Lost a blue water bottle near Donnelly. If you found it, leave a comment on the feed after the demo.",
        ],
    }

    created_posts: list[dict] = []
    for token, messages in posts_by_user.items():
        for body in messages:
            created_posts.append(
                request_json(
                    client,
                    "POST",
                    "/api/v1/posts",
                    token=token,
                    expected_status=201,
                    json={"body": body},
                )
            )

    return created_posts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL for the running local app.",
    )
    args = parser.parse_args()

    suffix = uuid.uuid4().hex[:8]

    with httpx.Client(base_url=args.base_url, timeout=15.0) as client:
        request_page(client, "/", expected_status=200)
        request_page(client, "/login.html", expected_status=200)
        request_page(client, "/Homepage.html", expected_status=200)
        request_page(client, "/Messages.html", expected_status=200)
        request_page(client, "/Profile.html", expected_status=200)
        request_page(client, "/js/global.js", expected_status=200)
        request_page(client, "/js/profile.js", expected_status=200)
        request_page(client, "/css/Homepage.css", expected_status=200)

        health = request_json(client, "GET", "/health")
        if health.get("status") != "ok":
            raise RuntimeError(f"Unexpected health payload: {health}")

        campuses = request_json(client, "GET", "/api/v1/campuses")
        if not campuses:
            raise RuntimeError("No campuses returned by /api/v1/campuses")

        campus = next((campus for campus in campuses if campus.get("slug") == "marist"), campuses[0])
        cleanup_previous_demo_users()
        users = create_demo_users(client, campus["id"], suffix)

        login_body = request_json(
            client,
            "POST",
            "/api/v1/auth/login",
            json={"email": users[0].email, "password": PASSWORD},
        )
        primary_token = login_body["access_token"]

        me = request_json(client, "GET", "/api/v1/auth/me", token=primary_token)
        if me["email"] != users[0].email:
            raise RuntimeError("Authenticated profile payload did not match the demo user")

        created_posts = seed_posts(client, users)
        one_post = request_json(
            client,
            "GET",
            f"/api/v1/posts/{created_posts[0]['id']}",
            token=primary_token,
        )
        if one_post["body"] != created_posts[0]["body"]:
            raise RuntimeError("Single post lookup did not return the expected body")

        feed = request_json(client, "GET", "/api/v1/feed", token=primary_token)
        expected_bodies = {post["body"] for post in created_posts}
        feed_bodies = {post["body"] for post in feed}
        missing_posts = sorted(expected_bodies - feed_bodies)
        if missing_posts:
            raise RuntimeError(f"Feed is missing expected demo posts: {missing_posts}")

    print("Live smoke test passed.")
    print(f"Base URL: {args.base_url}")
    print(f"Campus: {campus['name']}")
    print("Demo login:")
    print(f"  email: {users[0].email}")
    print(f"  password: {PASSWORD}")
    print("Created users:")
    for user in users:
        print(f"  {user.display_name} (@{user.username})")
    print("Seeded posts:")
    for post in created_posts:
        print(f"  - {post['body']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
