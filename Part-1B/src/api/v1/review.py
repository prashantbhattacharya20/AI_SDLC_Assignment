"""API v1 code review endpoint router.

Cites: Part-1B/specs/001-code-review-assistant/plan.md (Layer 1: Web & API Layer)
"""

from fastapi import APIRouter, Depends, status

from src.schemas.errors import ErrorResponse
from src.schemas.request import CodeReviewRequest
from src.schemas.response import CodeReviewResponse
from src.services.review_service import ReviewService, get_review_service

router = APIRouter()


@router.post(
    "/review",
    response_model=CodeReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Python code for automated AI-powered review",
    responses={
        200: {"model": CodeReviewResponse, "description": "Successful code review with findings"},
        413: {"model": ErrorResponse, "description": "Payload exceeds line or byte limits"},
        422: {"model": ErrorResponse, "description": "Validation error, unsupported language, or secret detected"},
        502: {"model": ErrorResponse, "description": "Groq LLM provider unavailable after retries"},
    },
)
async def review_code(
    request: CodeReviewRequest,
    service: ReviewService = Depends(get_review_service),
) -> CodeReviewResponse:
    """Analyze submitted Python source code and return structured findings and telemetry."""
    result_dict = await service.review_code(request)
    return CodeReviewResponse(**result_dict)


@router.get(
    "/health",
    summary="Service health and availability check",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def health_check() -> dict:
    """Return 200 OK indicating the code review assistant is operational."""
    return {
        "status": "ok",
        "provider": "groq",
        "version": "1.0.0",
    }
