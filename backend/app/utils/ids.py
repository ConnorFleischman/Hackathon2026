"""Identifier helpers (UUIDs, etc.)."""

from __future__ import annotations

from uuid import UUID, uuid4


def new_uuid() -> UUID:
    """Return a new random UUID (version 4)."""
    return uuid4()


def new_uuid_str() -> str:
    """Return a new UUID4 as a canonical string."""
    return str(new_uuid())
