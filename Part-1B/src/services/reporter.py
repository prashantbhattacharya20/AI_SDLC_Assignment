"""Reporter service for Markdown generation and release quality gating.

Cites: Part-1B/specs/001-code-review-assistant/plan.md (Layer 3: Core Service Layer)
"""

from src.schemas.enums import ReviewStatus, SeverityLevel
from src.schemas.request import CodeReviewRequest
from src.schemas.response import ReviewFinding, ReviewSummary, ReviewTelemetry


class Reporter:
    """Evaluates release gating and formats human-readable review reports."""

    def evaluate_quality_gate(self, findings: list[ReviewFinding]) -> ReviewStatus:
        """Evaluate automated release quality gate.

        Rule: FAIL if any CRITICAL or HIGH severity finding exists, otherwise PASS.
        """
        for f in findings:
            if f.severity in (SeverityLevel.CRITICAL, SeverityLevel.HIGH):
                return ReviewStatus.FAIL
        return ReviewStatus.PASS

    def generate_markdown(
        self,
        request: CodeReviewRequest,
        findings: list[ReviewFinding],
        summary: ReviewSummary,
        telemetry: ReviewTelemetry,
    ) -> str:
        """Render formatted GitHub-flavored Markdown review report."""
        status_badge = "🔴 **FAIL**" if summary.status == ReviewStatus.FAIL else "🟢 **PASS**"
        file_header = f" for `{request.file_path}`" if request.file_path else ""

        lines = [
            f"# Code Review Report{file_header}",
            f"\n**Quality Gate Status**: {status_badge}",
            f"- **Total Findings**: {summary.total_findings}",
            f"- **Critical**: {summary.critical_count} | **High**: {summary.high_count} | **Medium**: {summary.medium_count} | **Low**: {summary.low_count} | **Info**: {summary.info_count}",
            f"- **Model**: `{telemetry.model_id}` ({telemetry.prompt_version}) | **Latency**: {telemetry.latency_ms}ms",
            "\n---",
        ]

        if not findings:
            lines.append("\n✅ **No defects detected. Clean code!**")
        else:
            lines.append("\n## Detected Findings\n")
            for f in findings:
                lines.append(
                    f"### [{f.id}] {f.title} ({f.severity.value} - {f.category.value})\n"
                    f"- **Lines**: {f.start_line} - {f.end_line}\n"
                    f"- **Confidence**: {f.confidence:.2f}\n"
                    f"- **Description**: {f.description}\n"
                    f"- **Recommendation**: {f.recommendation}\n"
                )

        return "\n".join(lines)
