"""Liveness and readiness probes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def get_health() -> dict[str, str]:
    """Process is up; does not verify dependencies."""
    return {"status": "ok"}


@router.get("/ready")
def get_ready() -> dict[str, bool]:
    """Readiness placeholder: full dependency checks are not wired in this scaffold."""
    return {"ready": False}
