"""Shared database-facing enums for SQLAlchemy models and schemas."""

from enum import Enum
from typing import TypeVar

from sqlalchemy import Enum as SqlEnum


class StrEnum(str, Enum):
    """String enum base that serializes cleanly across DB/API layers."""

    def __str__(self) -> str:
        return self.value


EnumT = TypeVar("EnumT", bound=StrEnum)


def db_enum(enum_class: type[EnumT], *, name: str) -> SqlEnum:
    """Persist enum values in the database instead of enum member names."""
    return SqlEnum(
        enum_class,
        name=name,
        values_callable=lambda members: [member.value for member in members],
        validate_strings=True,
    )


class UserRole(StrEnum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    ORG_ACCOUNT = "org_account"


class UserStatus(StrEnum):
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class PostType(StrEnum):
    STANDARD = "standard"
    ANNOUNCEMENT = "announcement"
    EVENT = "event"
    SAFETY_ALERT = "safety_alert"


class VisibilityStatus(StrEnum):
    PENDING_MODERATION = "pending_moderation"
    VISIBLE = "visible"
    HIDDEN = "hidden"
    ARCHIVED = "archived"
    REMOVED = "removed"
    EXPIRED = "expired"


class ModerationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    FLAGGED = "flagged"
    AUTO_HIDDEN = "auto_hidden"
    REJECTED = "rejected"


class ReactionType(StrEnum):
    LIKE = "like"
    DISLIKE = "dislike"


class ReportStatus(StrEnum):
    OPEN = "open"
    REVIEWING = "reviewing"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class LocationSource(StrEnum):
    GPS = "gps"
    MANUAL = "manual"
    ADMIN = "admin"


class FlagSource(StrEnum):
    AI = "ai"
    USER_REPORT = "user_report"
    ADMIN = "admin"


class FlagType(StrEnum):
    HARASSMENT = "harassment"
    THREAT = "threat"
    HATE_SPEECH = "hate_speech"
    SPAM = "spam"
    SELF_HARM = "self_harm"
    OTHER = "other"


class FlagDecision(StrEnum):
    PENDING_REVIEW = "pending_review"
    ALLOWED = "allowed"
    HIDDEN = "hidden"
    REMOVED = "removed"


class ReportTargetType(StrEnum):
    POST = "post"
    COMMENT = "comment"
    USER = "user"


__all__ = [
    "db_enum",
    "FlagDecision",
    "FlagSource",
    "FlagType",
    "LocationSource",
    "ModerationStatus",
    "PostType",
    "ReactionType",
    "ReportStatus",
    "ReportTargetType",
    "StrEnum",
    "UserRole",
    "UserStatus",
    "VisibilityStatus",
]
