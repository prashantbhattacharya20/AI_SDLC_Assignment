"""Code review request schemas.

Cites: Part-1B/specs/001-code-review-assistant/data-model.md (CodeReviewRequest)
"""

from pydantic import BaseModel, Field, field_validator


class CodeReviewRequest(BaseModel):
    """Input payload for POST /api/v1/review endpoint.

    Cites: data-model.md (CodeReviewRequest)
    """

    code: str = Field(
        ...,
        min_length=1,
        description="Source code snippet to be reviewed (max 1,000 lines, max 65,536 UTF-8 bytes)",
        examples=["def add(a: int, b: int) -> int:\n    return a + b\n"],
    )
    file_path: str | None = Field(
        default=None,
        description="Optional relative or absolute file path to provide context",
        examples=["src/utils/calculator.py"],
    )
    language: str = Field(
        default="python",
        description="Programming language identifier. Only 'python' is supported in this MVP.",
        examples=["python"],
    )
    include_markdown: bool = Field(
        default=True,
        description="Whether to generate and include a human-readable markdown review report in the response",
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if cleaned != "python":
            raise ValueError(f"Unsupported language '{v}'. Only Python is supported in this MVP.")
        return "python"

    @field_validator("code")
    @classmethod
    def validate_code_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Submitted code cannot be empty or purely whitespace.")
        return v
