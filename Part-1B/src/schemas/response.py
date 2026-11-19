"""Code review response schemas, findings, summary, and telemetry entities.

Cites: Part-1B/specs/001-code-review-assistant/data-model.md
"""

from pydantic import BaseModel, Field, model_validator

from src.schemas.enums import DefectCategory, ReviewStatus, SeverityLevel


class ReviewFinding(BaseModel):
    """Individual code defect or improvement identified by the assistant.

    Cites: data-model.md (ReviewFinding)
    """

    id: str = Field(
        ...,
        description="Unique identifier for the finding within this review",
        examples=["F001", "sec-sqli-01"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Concise description of the finding",
        examples=["Potential SQL Injection Vulnerability"],
    )
    category: DefectCategory = Field(
        ...,
        description="Category of the defect",
        examples=[DefectCategory.SECURITY],
    )
    severity: SeverityLevel = Field(
        ...,
        description="Severity level of the defect",
        examples=[SeverityLevel.CRITICAL],
    )
    start_line: int = Field(
        ...,
        ge=1,
        description="1-based starting line number where defect begins",
        examples=[12],
    )
    end_line: int = Field(
        ...,
        ge=1,
        description="1-based ending line number where defect concludes",
        examples=[14],
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Detailed explanation of the issue and why it poses a problem",
    )
    recommendation: str = Field(
        ...,
        min_length=1,
        description="Actionable guidance on how to fix or mitigate the defect",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model-estimated confidence score between 0.0 and 1.0",
        examples=[0.95],
    )

    @model_validator(mode="after")
    def validate_line_bounds(self) -> "ReviewFinding":
        """Validate invariant: start_line <= end_line."""
        if self.start_line > self.end_line:
            raise ValueError(
                f"Invariant violation: start_line ({self.start_line}) cannot exceed end_line ({self.end_line})."
            )
        return self


class ReviewSummary(BaseModel):
    """Aggregated status and counts of findings.

    Cites: data-model.md (ReviewSummary)
    """

    status: ReviewStatus = Field(
        ...,
        description="Aggregated review outcome: FAIL if any CRITICAL or HIGH findings exist, else PASS",
        examples=[ReviewStatus.PASS],
    )
    total_findings: int = Field(
        default=0,
        ge=0,
        description="Total number of findings identified",
    )
    critical_count: int = Field(default=0, ge=0)
    high_count: int = Field(default=0, ge=0)
    medium_count: int = Field(default=0, ge=0)
    low_count: int = Field(default=0, ge=0)
    info_count: int = Field(default=0, ge=0)


class ReviewTelemetry(BaseModel):
    """Operational telemetry and execution metadata for the review request.

    Cites: data-model.md (ReviewTelemetry)
    """

    model_id: str = Field(
        default="openai/gpt-oss-120b",
        description="Exact Groq model identifier used for analysis",
    )
    prompt_version: str = Field(
        default="v1.0.0",
        description="Version identifier of prompt template used",
    )
    latency_ms: int = Field(
        default=0,
        ge=0,
        description="Round-trip execution latency in milliseconds",
    )
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    retry_count: int = Field(default=0, ge=0)


class CodeReviewResponse(BaseModel):
    """Top-level response payload for POST /api/v1/review.

    Cites: data-model.md (CodeReviewResult)
    """

    findings: list[ReviewFinding] = Field(
        default_factory=list,
        description="List of detected defects conforming to schema and invariants",
    )
    summary: ReviewSummary = Field(
        ...,
        description="Aggregated review summary and gate status",
    )
    telemetry: ReviewTelemetry = Field(
        ...,
        description="Execution metadata and performance metrics",
    )
    markdown_report: str | None = Field(
        default=None,
        description="Formatted markdown review report if requested",
    )
