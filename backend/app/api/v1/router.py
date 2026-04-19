"""Versioned API router for the public HTTP endpoints."""

from fastapi import APIRouter

from app.api.routes import auth, campuses, feed, posts

v1_router = APIRouter()
v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
v1_router.include_router(campuses.router, prefix="/campuses", tags=["campuses"])
v1_router.include_router(posts.router, prefix="/posts", tags=["posts"])
v1_router.include_router(feed.router, prefix="/feed", tags=["feed"])

__all__ = ["v1_router"]
