"""Unit tests for Markdown report generation and quality gate evaluation (T033)."""

from src.schemas.enums import DefectCategory, ReviewStatus, SeverityLevel
from src.schemas.request import CodeReviewRequest
from src.schemas.response import ReviewFinding, ReviewSummary, ReviewTelemetry


def test_reporter_quality_gate_fail_on_critical_or_high():
    from src.services.reporter import Reporter

    reporter = Reporter()

    critical_finding = ReviewFinding(
        id="F1",
        title="Remote Code Execution",
        category=DefectCategory.SECURITY,
        severity=SeverityLevel.CRITICAL,
        start_line=1,
        end_line=1,
        description="RCE vulnerability",
        recommendation="Sanitize input",
        confidence=0.99,
    )
    status = reporter.evaluate_quality_gate([critical_finding])
    assert status == ReviewStatus.FAIL

    high_finding = ReviewFinding(
        id="F2",
        title="SQL Injection",
        category=DefectCategory.SECURITY,
        severity=SeverityLevel.HIGH,
        start_line=1,
        end_line=1,
        description="SQLi vulnerability",
        recommendation="Use ORM",
        confidence=0.95,
    )
    status = reporter.evaluate_quality_gate([high_finding])
    assert status == ReviewStatus.FAIL


def test_reporter_quality_gate_pass_on_medium_low_info():
    from src.services.reporter import Reporter

    reporter = Reporter()

    medium_finding = ReviewFinding(
        id="F3",
        title="Unindexed Loop",
        category=DefectCategory.PERFORMANCE,
        severity=SeverityLevel.MEDIUM,
        start_line=1,
        end_line=2,
        description="Loop inefficiency",
        recommendation="Optimize loop",
        confidence=0.85,
    )
    status = reporter.evaluate_quality_gate([medium_finding])
    assert status == ReviewStatus.PASS

    status_empty = reporter.evaluate_quality_gate([])
    assert status_empty == ReviewStatus.PASS


def test_reporter_generate_markdown_content():
    from src.services.reporter import Reporter

    reporter = Reporter()

    req = CodeReviewRequest(code="def add(a, b): return a + b\n", file_path="calc.py")
    findings = [
        ReviewFinding(
            id="F001",
            title="Missing Type Hints",
            category=DefectCategory.MAINTAINABILITY,
            severity=SeverityLevel.INFO,
            start_line=1,
            end_line=1,
            description="Function lacks type annotations.",
            recommendation="Add type annotations to function parameters and return.",
            confidence=0.9,
        )
    ]
    summary = ReviewSummary(
        status=ReviewStatus.PASS,
        total_findings=1,
        info_count=1,
    )
    telemetry = ReviewTelemetry(
        model_id="openai/gpt-oss-120b",
        prompt_version="v1.0.0",
        latency_ms=150,
    )

    md = reporter.generate_markdown(req, findings, summary, telemetry)
    assert "# Code Review Report for `calc.py`" in md
    assert "PASS" in md
    assert "Missing Type Hints" in md
    assert "MAINTAINABILITY" in md
    assert "openai/gpt-oss-120b" in md
