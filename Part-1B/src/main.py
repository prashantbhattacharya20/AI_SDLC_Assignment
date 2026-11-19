"""FastAPI application entrypoint for AI Code Review Assistant.

Cites: Part-1B/specs/001-code-review-assistant/plan.md (Layer 1: Web & API Layer)
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.v1.router import api_v1_router
from src.config import get_settings
from src.schemas.errors import CodeReviewException, ErrorResponse


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    get_settings()

    application = FastAPI(
        title="AI Code Review Assistant",
        version="0.1.0",
        description="Automated static code analysis web service leveraging Groq LLM and deterministic validation.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Mount CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API v1 routes
    application.include_router(api_v1_router)

    # Global Exception Handlers
    @application.exception_handler(CodeReviewException)
    async def code_review_exception_handler(request: Request, exc: CodeReviewException):
        err_response = ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=err_response.model_dump(mode="json"),
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        details = [{"field": ".".join(str(loc) for loc in err["loc"]), "issue": err["msg"]} for err in exc.errors()]
        err_response = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=422,
            details=details,
        )
        return JSONResponse(
            status_code=422,
            content=err_response.model_dump(mode="json"),
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        err_response = ErrorResponse(
            error_code="HTTP_ERROR",
            message=str(exc.detail),
            status_code=exc.status_code,
            details=[],
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=err_response.model_dump(mode="json"),
        )

    return application


app = create_app()
