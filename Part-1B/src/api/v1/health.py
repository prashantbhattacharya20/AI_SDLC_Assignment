"""Health check endpoint for service availability."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Service health and readiness check")
async def health_check() -> dict[str, str]:
    """Return 200 OK indicating the review assistant service is operational."""
    return {
        "status": "ok",
        "provider": "groq",
        "version": "1.0.0",
    }
