"""Standardized error response schemas and domain exception models.

Cites: Part-1B/specs/001-code-review-assistant/data-model.md (ErrorResponse)
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """RFC 7807 aligned standardized error response model.

    Cites: data-model.md (ErrorResponse.error_code, ErrorResponse.message, ErrorResponse.details)
    """

    error_code: str = Field(
        ...,
        description="Machine-readable error classification code",
        examples=["PAYLOAD_TOO_LARGE", "UNSUPPORTED_LANGUAGE", "SECRET_DETECTED"],
    )
    message: str = Field(
        ...,
        description="Human-readable summary of the error",
        examples=["Payload exceeded maximum allowed size"],
    )
    status_code: int = Field(
        ...,
        description="HTTP status code corresponding to the error",
        examples=[413, 422, 502],
    )
    details: list[dict[str, Any]] | None = Field(
        default=None,
        description="Structured error details and diagnostic context",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp of error occurrence in ISO 8601 format",
    )


class CodeReviewException(Exception):
    """Base exception for code review service errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: list[dict[str, Any]] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or []


class PayloadTooLargeError(CodeReviewException):
    """Raised when submitted code exceeds line count or byte limits (HTTP 413)."""

    def __init__(self, message: str, details: list[dict[str, Any]] | None = None):
        super().__init__(
            message=message,
            error_code="PAYLOAD_TOO_LARGE",
            status_code=413,
            details=details,
        )


class UnsupportedLanguageError(CodeReviewException):
    """Raised when submitted code is not Python (HTTP 422)."""

    def __init__(self, message: str, details: list[dict[str, Any]] | None = None):
        super().__init__(
            message=message,
            error_code="UNSUPPORTED_LANGUAGE",
            status_code=422,
            details=details,
        )


class SecretDetectedError(CodeReviewException):
    """Raised when secret patterns or high-entropy tokens are detected (HTTP 422)."""

    def __init__(self, message: str, details: list[dict[str, Any]] | None = None):
        super().__init__(
            message=message,
            error_code="SECRET_DETECTED",
            status_code=422,
            details=details,
        )


class ProviderUnavailableError(CodeReviewException):
    """Raised when the LLM provider fails after exhausting retries (HTTP 502)."""

    def __init__(self, message: str, details: list[dict[str, Any]] | None = None):
        super().__init__(
            message=message,
            error_code="PROVIDER_UNAVAILABLE",
            status_code=502,
            details=details,
        )
