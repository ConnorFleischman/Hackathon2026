"""Time helpers — keep UTC explicit for persistence and APIs."""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Current time in UTC with ``tzinfo=timezone.utc``."""
    return datetime.now(timezone.utc)
