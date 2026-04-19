"""Health endpoints for service liveness and database reachability."""

from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.db.session import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health(response: Response) -> dict[str, str]:
    """Report service liveness and whether the configured database is reachable."""
    try:
        check_database_connection()
    except RuntimeError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "service": settings.APP_NAME,
            "database": "unavailable",
        }

    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "database": "connected",
    }
