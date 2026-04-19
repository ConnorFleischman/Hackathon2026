"""
SQLAlchemy ORM models.

Import concrete model modules here so metadata is registered on `Base.metadata`
and Alembic sees all tables when `import app.db.models` runs.
"""

from app.db.base import Base
from app.db.models.admin_action import AdminAction
from app.db.models.audit_log import AuditLog
from app.db.models.ban import Ban
from app.db.models.campus import Campus
from app.db.models.category import Category
from app.db.models.comment import Comment
from app.db.models.post import Post
from app.db.models.post_flag import PostFlag
from app.db.models.reaction import Reaction
from app.db.models.report import Report
from app.db.models.session import Session
from app.db.models.user import User
from app.db.models.user_location import UserLocation

__all__ = [
    "AdminAction",
    "AuditLog",
    "Ban",
    "Base",
    "Campus",
    "Category",
    "Comment",
    "Post",
    "PostFlag",
    "Reaction",
    "Report",
    "Session",
    "User",
    "UserLocation",
]
