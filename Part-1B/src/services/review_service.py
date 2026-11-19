"""Review service orchestrating analysis, pre-validation guards, and invariant enforcement.

Cites: Part-1B/specs/001-code-review-assistant/plan.md (Layer 3: Core Service Layer)
"""

import time
from typing import Any

from pydantic import ValidationError

from src.config import get_settings
from src.llm.client import GroqClient, LLMClient
from src.llm.prompt import render_prompt
from src.schemas.enums import SeverityLevel
from src.schemas.errors import (
    PayloadTooLargeError,
    SecretDetectedError,
    UnsupportedLanguageError,
)
from src.schemas.request import CodeReviewRequest
from src.schemas.response import (
    CodeReviewResponse,
    ReviewFinding,
    ReviewSummary,
    ReviewTelemetry,
)
from src.services.reporter import Reporter
from src.services.secret_scanner import SecretScanner
from src.services.syntax_checker import SyntaxChecker


class ReviewService:
    """Core domain service orchestrating the multi-stage code review pipeline."""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        secret_scanner: SecretScanner | None = None,
        syntax_checker: SyntaxChecker | None = None,
        reporter: Reporter | None = None,
        prompt_version: str | None = None,
    ):
        self.settings = get_settings()
        self.prompt_version = prompt_version or self.settings.PROMPT_VERSION
        self.llm_client = llm_client or GroqClient()
        self.secret_scanner = secret_scanner or SecretScanner()
        self.syntax_checker = syntax_checker or SyntaxChecker()
        self.reporter = reporter or Reporter()

    def count_lines(self, code: str) -> int:
        """Count the total number of lines in the submitted code."""
        return len(code.splitlines()) or 1

    def enforce_invariants(self, raw_findings: list[dict[str, Any]], total_lines: int) -> list[ReviewFinding]:
        """Validate and sanitize raw model findings against deterministic invariants.

        Invariants:
        1. Strict schema compliance (Pydantic validation).
        2. Line number boundaries: 1 <= start_line <= end_line <= total_lines.
        3. Deduplication: Filter out exact duplicate findings.
        """
        validated_findings: list[ReviewFinding] = []
        seen_keys = set()

        for idx, finding_data in enumerate(raw_findings):
            try:
                if "id" not in finding_data or not finding_data["id"]:
                    finding_data["id"] = f"F{idx + 1:03d}"

                start_l = int(finding_data.get("start_line", 1))
                end_l = int(finding_data.get("end_line", start_l))

                start_l = max(1, min(start_l, total_lines))
                end_l = max(start_l, min(end_l, total_lines))

                finding_data["start_line"] = start_l
                finding_data["end_line"] = end_l

                finding = ReviewFinding(**finding_data)

                dedup_key = (
                    finding.category,
                    finding.start_line,
                    finding.end_line,
                    finding.title.strip().lower(),
                )
                if dedup_key in seen_keys:
                    continue
                seen_keys.add(dedup_key)

                validated_findings.append(finding)
            except (ValidationError, ValueError, TypeError):
                continue

        return validated_findings

    def compute_summary(self, findings: list[ReviewFinding]) -> ReviewSummary:
        """Compute aggregated counts and determine release quality gate status.

        Rule: FAIL if any CRITICAL or HIGH findings exist; otherwise PASS.
        """
        critical = sum(1 for f in findings if f.severity == SeverityLevel.CRITICAL)
        high = sum(1 for f in findings if f.severity == SeverityLevel.HIGH)
        medium = sum(1 for f in findings if f.severity == SeverityLevel.MEDIUM)
        low = sum(1 for f in findings if f.severity == SeverityLevel.LOW)
        info = sum(1 for f in findings if f.severity == SeverityLevel.INFO)

        status = self.reporter.evaluate_quality_gate(findings)

        return ReviewSummary(
            status=status,
            total_findings=len(findings),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            info_count=info,
        )

    def generate_markdown(
        self,
        request: CodeReviewRequest,
        findings: list[ReviewFinding],
        summary: ReviewSummary,
        telemetry: ReviewTelemetry,
    ) -> str:
        """Render human-readable markdown review report."""
        return self.reporter.generate_markdown(request, findings, summary, telemetry)

    async def review_code(self, request: CodeReviewRequest) -> dict[str, Any]:
        """Execute complete code review pipeline with strict pre-validation gates."""
        start_time = time.perf_counter()

        # Gate 1: Language validation
        if request.language.strip().lower() != "python":
            raise UnsupportedLanguageError(
                f"Unsupported language '{request.language}'. Only Python is supported in this MVP."
            )

        # Gate 2: Payload limits (Lines and UTF-8 Bytes)
        line_count = len(request.code.splitlines())
        if line_count > self.settings.MAX_PAYLOAD_LINES:
            raise PayloadTooLargeError(
                f"Submitted payload contains {line_count} lines, exceeding maximum limit of {self.settings.MAX_PAYLOAD_LINES} lines."
            )

        byte_count = len(request.code.encode("utf-8"))
        if byte_count > self.settings.MAX_PAYLOAD_BYTES:
            raise PayloadTooLargeError(
                f"Submitted payload contains {byte_count} UTF-8 bytes, exceeding maximum limit of {self.settings.MAX_PAYLOAD_BYTES} bytes."
            )

        # Gate 3: Secret screening (zero Groq invocations if detected)
        secret_detections = self.secret_scanner.scan(request.code)
        if secret_detections:
            details = [{"issue": d.masked_description(), "line": d.line_number} for d in secret_detections]
            raise SecretDetectedError(
                message="Secret pattern or credential detected in submitted source code.",
                details=details,
            )

        # Gate 4: Deterministic Python AST syntax checking
        syntax_finding = self.syntax_checker.check_syntax(request.code)
        if syntax_finding is not None:
            findings = [syntax_finding]
            summary = self.compute_summary(findings)
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            telemetry = ReviewTelemetry(
                model_id="deterministic-ast",
                prompt_version="ast-parser",
                latency_ms=latency_ms,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                retry_count=0,
            )
            markdown_report = None
            if request.include_markdown:
                markdown_report = self.generate_markdown(request, findings, summary, telemetry)

            response = CodeReviewResponse(
                findings=findings,
                summary=summary,
                telemetry=telemetry,
                markdown_report=markdown_report,
            )
            return response.model_dump(mode="json")

        # Gate 5: Semantic Review via Groq LLM
        prompt = render_prompt(
            code=request.code,
            file_path=request.file_path,
            version=self.prompt_version,
        )

        llm_response = await self.llm_client.generate_review(prompt)
        raw_findings = llm_response.get("parsed", {}).get("findings", [])

        # Post-validation: Enforce Invariants
        findings = self.enforce_invariants(raw_findings, line_count or 1)
        summary = self.compute_summary(findings)

        telem_data = llm_response.get("telemetry", {})
        telemetry = ReviewTelemetry(
            model_id=telem_data.get("model_id", self.settings.MODEL_ID),
            prompt_version=self.prompt_version,
            latency_ms=telem_data.get("latency_ms", 0),
            prompt_tokens=telem_data.get("prompt_tokens", 0),
            completion_tokens=telem_data.get("completion_tokens", 0),
            total_tokens=telem_data.get("total_tokens", 0),
            retry_count=telem_data.get("retry_count", 0),
        )

        markdown_report = None
        if request.include_markdown:
            markdown_report = self.generate_markdown(request, findings, summary, telemetry)

        response = CodeReviewResponse(
            findings=findings,
            summary=summary,
            telemetry=telemetry,
            markdown_report=markdown_report,
        )

        return response.model_dump(mode="json")


def get_review_service() -> ReviewService:
    """FastAPI dependency for accessing the review service."""
    return ReviewService()
