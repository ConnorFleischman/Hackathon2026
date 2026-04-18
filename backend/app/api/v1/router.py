"""Aggregate all versioned feature routers under /api/v1."""

from fastapi import APIRouter

from app.api.routes import (
    admin,
    auth,
    campuses,
    comments,
    location,
    posts,
    reactions,
    reports,
    users,
    websocket,
)

v1_router = APIRouter()

v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
v1_router.include_router(users.router, prefix="/users", tags=["users"])
v1_router.include_router(campuses.router, prefix="/campuses", tags=["campuses"])
v1_router.include_router(location.router, prefix="/location", tags=["location"])
v1_router.include_router(posts.router, prefix="/posts", tags=["posts"])
v1_router.include_router(comments.router, prefix="/comments", tags=["comments"])
v1_router.include_router(reactions.router, prefix="/reactions", tags=["reactions"])
v1_router.include_router(reports.router, prefix="/reports", tags=["reports"])
v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
v1_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
