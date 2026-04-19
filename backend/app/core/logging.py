"""Application-wide structured logging setup."""

import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger

from app.core.config import get_settings


def _parse_level(name: str) -> int:
    level = getattr(logging, name.upper(), None)
    if isinstance(level, int):
        return level
    return logging.INFO


def configure_logging() -> None:
    """
    Configure the root logger for structured, consistent output.

    When ``LOG_JSON`` is true (typical in production), records are JSON lines on stdout.
    Otherwise a human-readable format is used for local development.
    """
    settings = get_settings()
    level = _parse_level(settings.LOG_LEVEL)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if settings.LOG_JSON:
        formatter: logging.Formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            rename_fields={
                "levelname": "level",
                "asctime": "timestamp",
            },
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    # Quiet overly chatty libraries unless DEBUG
    if level > logging.DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger; prefer ``__name__`` for *name*."""
    return logging.getLogger(name)


def log_context(logger: logging.Logger, message: str, **fields: Any) -> None:
    """
    Emit an INFO log with structured extra fields (visible in JSON output).

    Standard logging ``extra`` is used so JSON formatters can pick up keys.
    """
    logger.info(message, extra=fields)
