"""API v1 master router mounting endpoints."""

from fastapi import APIRouter

from src.api.v1.review import router as review_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(review_router, tags=["Review"])
