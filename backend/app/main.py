"""
FastAPI application entrypoint.

Route handlers stay thin; business logic lives in services; persistence in repositories.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.api.v1.router import v1_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title="Campus Social API",
    description="Backend for the campus-based social application.",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)


@app.on_event("startup")
async def on_startup() -> None:
    """Reserved for connection pools, shared clients, and readiness integration."""
    pass


if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health.router, tags=["health"])
app.include_router(v1_router, prefix="/api/v1")
