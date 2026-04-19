"""FastAPI application entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.api.routes import health
from app.api.v1.router import v1_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.models.campus import Campus
from app.db.session import get_session_factory

configure_logging()

REPO_DIR = Path(__file__).resolve().parents[2]
CLIENT_DIR = REPO_DIR / "Client"
DEFAULT_CAMPUSES = [
    {
        "name": "Marist University",
        "slug": "marist",
        "city": "Poughkeepsie",
        "state": "NY",
        "country": "USA",
        "description": "Default campus available for local development.",
    },
    {
        "name": "SUNY New Paltz",
        "slug": "suny-new-paltz",
        "city": "New Paltz",
        "state": "NY",
        "country": "USA",
        "description": "Secondary campus for local testing and demos.",
    },
]


def seed_default_campuses() -> None:
    """Make a fresh database usable for the browser client."""
    session = get_session_factory()()
    try:
        existing_campus = session.scalar(select(Campus.id).limit(1))
        if existing_campus is not None:
            return

        session.add_all(Campus(**campus) for campus in DEFAULT_CAMPUSES)
        session.commit()
    finally:
        session.close()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Seed baseline data before serving requests."""
    seed_default_campuses()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend foundation for the campus social application.",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health.router)
app.include_router(v1_router, prefix="/api/v1")

if CLIENT_DIR.exists():
    app.mount("/js", StaticFiles(directory=CLIENT_DIR / "js"), name="client-js")
    app.mount("/css", StaticFiles(directory=CLIENT_DIR / "css"), name="client-css")
    app.mount("/static", StaticFiles(directory=CLIENT_DIR / "static"), name="client-static")

    @app.get("/", include_in_schema=False)
    def serve_root() -> RedirectResponse:
        """Open the login page when the app root is requested."""
        return RedirectResponse(url="/login.html", status_code=307)

    @app.get("/Index.html", include_in_schema=False)
    def serve_index() -> FileResponse:
        """Serve the client shell page."""
        return FileResponse(CLIENT_DIR / "Index.html")

    @app.get("/login.html", include_in_schema=False)
    def serve_login() -> FileResponse:
        """Serve the login page."""
        return FileResponse(CLIENT_DIR / "login.html")

    @app.get("/Homepage.html", include_in_schema=False)
    def serve_homepage() -> FileResponse:
        """Serve the feed page."""
        return FileResponse(CLIENT_DIR / "Homepage.html")

    @app.get("/Messages.html", include_in_schema=False)
    def serve_messages() -> FileResponse:
        """Serve the messages placeholder page."""
        return FileResponse(CLIENT_DIR / "Messages.html")

    @app.get("/Profile.html", include_in_schema=False)
    def serve_profile() -> FileResponse:
        """Serve the profile page."""
        return FileResponse(CLIENT_DIR / "Profile.html")
