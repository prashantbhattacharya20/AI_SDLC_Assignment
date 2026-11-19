"""Unit tests for domain enumerations and error response schemas (T006)."""

import pytest
from pydantic import ValidationError


def test_defect_category_enum():
    from src.schemas.enums import DefectCategory

    assert DefectCategory.BUG == "BUG"
    assert DefectCategory.SECURITY == "SECURITY"
    assert DefectCategory.PERFORMANCE == "PERFORMANCE"
    assert DefectCategory.MAINTAINABILITY == "MAINTAINABILITY"

    with pytest.raises(ValueError):
        DefectCategory("STYLE")


def test_severity_level_enum():
    from src.schemas.enums import SeverityLevel

    assert SeverityLevel.CRITICAL == "CRITICAL"
    assert SeverityLevel.HIGH == "HIGH"
    assert SeverityLevel.MEDIUM == "MEDIUM"
    assert SeverityLevel.LOW == "LOW"
    assert SeverityLevel.INFO == "INFO"

    with pytest.raises(ValueError):
        SeverityLevel("URGENT")


def test_review_status_enum():
    from src.schemas.enums import ReviewStatus

    assert ReviewStatus.PASS == "PASS"
    assert ReviewStatus.FAIL == "FAIL"

    with pytest.raises(ValueError):
        ReviewStatus("WARN")


def test_error_response_schema():
    from src.schemas.errors import ErrorResponse

    error = ErrorResponse(
        error_code="INVALID_PAYLOAD",
        message="Payload exceeded maximum byte limit",
        status_code=413,
        details=[{"field": "code", "issue": "Exceeded 65536 bytes"}],
    )
    assert error.error_code == "INVALID_PAYLOAD"
    assert error.status_code == 413
    assert len(error.details) == 1
    assert error.timestamp is not None


# ---------------------------------------------------------------------------
# User Story 1 Schemas & Invariant Unit Tests (T018)
# ---------------------------------------------------------------------------


def test_code_review_request_valid():
    from src.schemas.request import CodeReviewRequest

    req = CodeReviewRequest(
        code="def hello(): pass\n",
        file_path="app.py",
        language="python",
        include_markdown=True,
    )
    assert req.code == "def hello(): pass\n"
    assert req.language == "python"
    assert req.include_markdown is True


def test_code_review_request_default_language():
    from src.schemas.request import CodeReviewRequest

    req = CodeReviewRequest(code="print('hello')\n")
    assert req.language == "python"
    assert req.include_markdown is True


def test_code_review_request_empty_code():
    from src.schemas.request import CodeReviewRequest

    with pytest.raises(ValidationError):
        CodeReviewRequest(code="")


def test_review_finding_schema_valid():
    from src.schemas.enums import DefectCategory, SeverityLevel
    from src.schemas.response import ReviewFinding

    finding = ReviewFinding(
        id="F001",
        title="Uncaught Exception",
        category=DefectCategory.BUG,
        severity=SeverityLevel.HIGH,
        start_line=2,
        end_line=5,
        description="Potential KeyError when accessing missing dict key",
        recommendation="Use dict.get(key) instead",
        confidence=0.92,
    )
    assert finding.id == "F001"
    assert finding.category == "BUG"
    assert finding.severity == "HIGH"
    assert finding.start_line == 2
    assert finding.end_line == 5
    assert finding.confidence == 0.92


def test_review_finding_invalid_line_bounds():
    from src.schemas.enums import DefectCategory, SeverityLevel
    from src.schemas.response import ReviewFinding

    # start_line > end_line
    with pytest.raises(ValidationError):
        ReviewFinding(
            id="F002",
            title="Line Order Error",
            category=DefectCategory.BUG,
            severity=SeverityLevel.LOW,
            start_line=10,
            end_line=5,
            description="desc",
            recommendation="recom",
            confidence=0.8,
        )


def test_review_finding_invalid_confidence():
    from src.schemas.enums import DefectCategory, SeverityLevel
    from src.schemas.response import ReviewFinding

    # confidence > 1.0
    with pytest.raises(ValidationError):
        ReviewFinding(
            id="F003",
            title="Confidence Error",
            category=DefectCategory.PERFORMANCE,
            severity=SeverityLevel.LOW,
            start_line=1,
            end_line=1,
            description="desc",
            recommendation="recom",
            confidence=1.5,
        )
