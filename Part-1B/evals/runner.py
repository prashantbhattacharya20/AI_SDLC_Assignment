"""Automated evaluation harness runner and benchmark report generator.

Cites: Part-1B/specs/001-code-review-assistant/plan.md (Evaluation Strategy)
"""

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from evals.metrics import (
    compute_invariant_compliance,
    compute_percentile,
    compute_schema_adherence,
    compute_semantic_metrics,
    validate_invariants,
    validate_schema,
)
from src.schemas.errors import CodeReviewException
from src.schemas.request import CodeReviewRequest
from src.services.review_service import ReviewService


class EvaluationRunner:
    """Orchestrates benchmark dataset execution and evaluates metric thresholds."""

    def __init__(
        self,
        dataset_path: Path | None = None,
        config_path: Path | None = None,
    ):
        base_dir = Path(__file__).resolve().parent
        self.dataset_path = dataset_path or (base_dir / "dataset.json")
        self.config_path = config_path or (base_dir / "config.json")

        self.dataset = json.loads(self.dataset_path.read_text(encoding="utf-8"))
        self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.thresholds = self.config.get("thresholds", {})

    async def run_benchmark(
        self,
        review_service: ReviewService | None = None,
        prompt_version: str | None = None,
    ) -> dict[str, Any]:
        """Execute all test cases in the dataset and score against frozen thresholds."""
        service = review_service or ReviewService(prompt_version=prompt_version)
        cases = self.dataset.get("cases", [])

        case_results: list[dict[str, Any]] = []
        predictions: list[bool] = []
        ground_truth: list[bool] = []
        latencies: list[int] = []
        provider_errors: list[dict[str, Any]] = []

        total_latency_ms = 0

        for case in cases:
            case_id = case["id"]
            code = case["code"]
            is_clean = case.get("is_clean", False)
            case.get("expected_status", "PASS")
            expected_http = case.get("expected_http_status", 200)

            req = CodeReviewRequest(
                code=code,
                file_path=case.get("file_path"),
                language=case.get("language", "python"),
                include_markdown=True,
            )

            start_t = time.perf_counter()
            is_schema_valid = False
            schema_errors: list[str] = []
            is_invariant_compliant = False
            invariant_errors: list[str] = []
            defect_predicted = None
            is_unevaluable = False
            is_provider_error = False
            response_payload: dict[str, Any] = {}
            error_code = None

            try:
                res = await service.review_code(req)
                elapsed_ms = int((time.perf_counter() - start_t) * 1000)
                latencies.append(elapsed_ms)
                total_latency_ms += elapsed_ms

                # Independent schema validation
                is_schema_valid, schema_errors = validate_schema(res, expected_http_status=expected_http)

                # Independent invariant validation
                is_invariant_compliant, invariant_errors = validate_invariants(
                    res, code=code, expected_http_status=expected_http
                )

                response_payload = res

                findings = res.get("findings", [])
                summary = res.get("summary", {})
                status = summary.get("status", "PASS")

                # Prediction is True if defect detected (findings > 0 or status == FAIL)
                defect_predicted = (len(findings) > 0) or (status == "FAIL")
                predictions.append(defect_predicted)
                ground_truth.append(not is_clean)

            except CodeReviewException as exc:
                elapsed_ms = int((time.perf_counter() - start_t) * 1000)
                latencies.append(elapsed_ms)
                total_latency_ms += elapsed_ms
                error_code = exc.error_code

                err_payload = {
                    "error_code": exc.error_code,
                    "message": exc.message,
                    "status_code": exc.status_code,
                    "details": exc.details,
                    "timestamp": datetime.now(UTC).isoformat(),
                }

                if exc.status_code == expected_http:
                    # Expected deterministic validation outcome (e.g. TC-ADV-02 secret screening)
                    is_schema_valid, schema_errors = validate_schema(err_payload, expected_http_status=expected_http)
                    is_invariant_compliant, invariant_errors = validate_invariants(
                        err_payload, code=code, expected_http_status=expected_http
                    )
                    defect_predicted = True if not is_clean else False
                    predictions.append(defect_predicted)
                    ground_truth.append(not is_clean)
                else:
                    # Unexpected provider or network failure (e.g. HTTP 502, 404, rate limits)
                    is_schema_valid = False
                    schema_errors = [f"Unexpected error status {exc.status_code}: {exc.message}"]
                    is_invariant_compliant = False
                    invariant_errors = ["Provider error encountered"]
                    is_provider_error = True
                    is_unevaluable = True
                    provider_errors.append(
                        {
                            "case_id": case_id,
                            "status_code": exc.status_code,
                            "error_code": exc.error_code,
                            "message": exc.message,
                        }
                    )

                response_payload = err_payload

            except Exception as exc:
                elapsed_ms = int((time.perf_counter() - start_t) * 1000)
                latencies.append(elapsed_ms)
                total_latency_ms += elapsed_ms
                error_code = "UNHANDLED_EXCEPTION"
                is_schema_valid = False
                schema_errors = [f"Unhandled exception: {exc}"]
                is_invariant_compliant = False
                invariant_errors = [f"Unhandled exception: {exc}"]
                is_provider_error = True
                is_unevaluable = True
                provider_errors.append(
                    {
                        "case_id": case_id,
                        "status_code": 500,
                        "error_code": "UNHANDLED_EXCEPTION",
                        "message": str(exc),
                    }
                )
                response_payload = {"error": str(exc), "error_code": "UNHANDLED_EXCEPTION"}

            case_results.append(
                {
                    "case_id": case_id,
                    "category": case.get("category"),
                    "scenario": case.get("scenario"),
                    "is_clean": is_clean,
                    "is_schema_valid": is_schema_valid,
                    "schema_errors": schema_errors,
                    "is_invariant_compliant": is_invariant_compliant,
                    "invariant_errors": invariant_errors,
                    "defect_predicted": defect_predicted,
                    "is_unevaluable": is_unevaluable,
                    "is_provider_error": is_provider_error,
                    "latency_ms": elapsed_ms,
                    "error_code": error_code,
                    "summary": response_payload.get("summary"),
                    "findings_count": len(response_payload.get("findings", []))
                    if "findings" in response_payload
                    else 0,
                }
            )

        # Compute Dimensions A, B, and C
        schema_adherence = compute_schema_adherence(case_results)
        invariant_compliance = compute_invariant_compliance(case_results)
        semantic = compute_semantic_metrics(predictions, ground_truth)
        avg_latency_ms = round(total_latency_ms / len(cases), 2) if cases else 0
        p95_latency_ms = compute_percentile(latencies, 95.0)

        metrics = {
            "schema_adherence": schema_adherence,
            "invariant_compliance": invariant_compliance,
            "precision": semantic["precision"],
            "recall": semantic["recall"],
            "f1_score": semantic["f1_score"],
            "false_positive_rate": semantic["false_positive_rate"],
            "confusion_matrix": {
                "tp": semantic["tp"],
                "fp": semantic["fp"],
                "fn": semantic["fn"],
                "tn": semantic["tn"],
            },
            "avg_latency_ms": avg_latency_ms,
            "p95_latency_ms": p95_latency_ms,
            "evaluated_cases_count": len(predictions),
            "unevaluable_cases_count": len(provider_errors),
            "provider_errors": provider_errors,
        }

        # Check against frozen thresholds
        performance_targets = self.config.get("performance_targets", {})
        p95_target = performance_targets.get("latency_p95_under_500_lines_ms", 15000)
        p95_latency_passed = p95_latency_ms <= p95_target

        threshold_eval = {
            "schema_adherence": schema_adherence >= self.thresholds.get("schema_adherence_min", 1.0),
            "invariant_compliance": invariant_compliance >= self.thresholds.get("invariant_compliance_min", 1.0),
            "precision": semantic["precision"] >= self.thresholds.get("precision_min", 0.80),
            "recall": semantic["recall"] >= self.thresholds.get("recall_min", 0.80),
            "f1_score": semantic["f1_score"] >= self.thresholds.get("f1_score_min", 0.80),
            "false_positive_rate": semantic["false_positive_rate"]
            <= self.thresholds.get("false_positive_rate_max", 0.15),
            "p95_latency": p95_latency_passed,
            "zero_provider_errors": len(provider_errors) == 0,
        }

        # Gate pass requires all thresholds met, zero provider errors, and sufficient evaluated cases
        min_required_cases = min(len(cases), 15)
        overall_status = (
            "PASS"
            if (all(threshold_eval.values()) and len(predictions) >= min_required_cases and len(predictions) > 0)
            else "FAIL"
        )

        return {
            "status": overall_status,
            "benchmark_version": self.config.get("benchmark_version", "1.0.0"),
            "model_id": self.config.get("model_id", "openai/gpt-oss-120b"),
            "prompt_version": service.prompt_version,
            "metrics": metrics,
            "threshold_eval": threshold_eval,
            "summary": {
                "total_cases": len(cases),
                "passed_thresholds": sum(1 for v in threshold_eval.values() if v),
                "total_thresholds": len(threshold_eval),
            },
            "case_results": case_results,
        }

    @staticmethod
    def save_results(results: dict[str, Any], output_path: Path) -> None:
        """Serialize benchmark results to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    @staticmethod
    def save_harness_log(results: dict[str, Any], output_path: Path) -> None:
        """Serialize human-readable markdown harness log."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        m = results.get("metrics", {})
        status = results.get("status", "UNKNOWN")
        status_badge = "🟢 **PASS**" if status == "PASS" else "🔴 **FAIL**"

        lines = [
            "# AI Code Review Assistant: Evaluation Harness Log",
            f"\n**Execution Status**: {status_badge}",
            f"- **Benchmark Version**: `{results.get('benchmark_version')}`",
            f"- **Model**: `{results.get('model_id')}`",
            f"- **Prompt Version**: `{results.get('prompt_version')}`",
            f"- **Total Cases**: {results.get('summary', {}).get('total_cases')}",
            f"- **Evaluated Predictions**: {m.get('evaluated_cases_count', 0)}",
            f"- **Unevaluable Cases (Provider Errors)**: {m.get('unevaluable_cases_count', 0)}",
            f"- **Average Latency**: {m.get('avg_latency_ms', 0)} ms",
            f"- **p95 Latency**: {m.get('p95_latency_ms', 0)} ms (Target: < 15,000 ms)",
            "\n## Dimension Scorecard",
            "\n| Evaluation Dimension | Threshold | Observed Score | Gate Status |",
            "| :--- | :---: | :---: | :---: |",
            f"| **Dimension A: Schema Adherence** | 100% | {m.get('schema_adherence', 0) * 100:.1f}% | {'✓ PASS' if results.get('threshold_eval', {}).get('schema_adherence') else '✗ FAIL'} |",
            f"| **Dimension B: Invariant Compliance** | 100% | {m.get('invariant_compliance', 0) * 100:.1f}% | {'✓ PASS' if results.get('threshold_eval', {}).get('invariant_compliance') else '✗ FAIL'} |",
            f"| **Dimension C: Precision** | >= 80% | {m.get('precision', 0) * 100:.1f}% | {'✓ PASS' if results.get('threshold_eval', {}).get('precision') else '✗ FAIL'} |",
            f"| **Dimension C: Recall** | >= 80% | {m.get('recall', 0) * 100:.1f}% | {'✓ PASS' if results.get('threshold_eval', {}).get('recall') else '✗ FAIL'} |",
            f"| **Dimension C: F1 Score** | >= 80% | {m.get('f1_score', 0) * 100:.1f}% | {'✓ PASS' if results.get('threshold_eval', {}).get('f1_score') else '✗ FAIL'} |",
            f"| **Dimension C: False Positive Rate** | <= 15% | {m.get('false_positive_rate', 0) * 100:.1f}% | {'✓ PASS' if results.get('threshold_eval', {}).get('false_positive_rate') else '✗ FAIL'} |",
            f"| **Performance: p95 Latency** | <= 15,000 ms | {m.get('p95_latency_ms', 0)} ms | {'✓ PASS' if results.get('threshold_eval', {}).get('p95_latency') else '✗ FAIL'} |",
            f"| **Reliability: Zero Provider Errors** | 0 errors | {m.get('unevaluable_cases_count', 0)} errors | {'✓ PASS' if results.get('threshold_eval', {}).get('zero_provider_errors') else '✗ FAIL'} |",
            "\n## Confusion Matrix",
            f"- **True Positives (TP)**: {m.get('confusion_matrix', {}).get('tp')}",
            f"- **False Positives (FP)**: {m.get('confusion_matrix', {}).get('fp')}",
            f"- **False Negatives (FN)**: {m.get('confusion_matrix', {}).get('fn')}",
            f"- **True Negatives (TN)**: {m.get('confusion_matrix', {}).get('tn')}",
            "\n## Case Execution Breakdown",
            "\n| Case ID | Category | Scenario | Predicted | Clean Code | Latency | Status |",
            "| :--- | :--- | :--- | :---: | :---: | :---: | :---: |",
        ]

        for c in results.get("case_results", []):
            if c.get("is_unevaluable"):
                pred_str = "Unevaluable (Provider Error)"
                icon = "✗"
            else:
                pred_str = "Defect" if c.get("defect_predicted") else "Clean"
                passed = (
                    c.get("defect_predicted") == (not c.get("is_clean"))
                    and c.get("is_schema_valid", False)
                    and c.get("is_invariant_compliant", False)
                )
                icon = "✓" if passed else "✗"
            clean_str = "Clean" if c.get("is_clean") else "Defect"
            lines.append(
                f"| `{c.get('case_id')}` | {c.get('category')} | {c.get('scenario')} | {pred_str} | {clean_str} | {c.get('latency_ms')}ms | {icon} |"
            )

        if m.get("provider_errors"):
            lines.extend(
                [
                    "\n## Provider Errors Detail",
                    "\n| Case ID | Status Code | Error Code | Error Message |",
                    "| :--- | :---: | :--- | :--- |",
                ]
            )
            for pe in m.get("provider_errors", []):
                lines.append(
                    f"| `{pe.get('case_id')}` | {pe.get('status_code')} | `{pe.get('error_code')}` | {pe.get('message')} |"
                )

        output_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="Run AI Code Review Evaluation Harness")
    parser.add_argument("--mode", choices=["baseline", "final"], default="baseline", help="Benchmark generation stage")
    parser.add_argument("--dataset", type=Path, default=None, help="Path to ground truth dataset.json")
    parser.add_argument("--config", type=Path, default=None, help="Path to config.json")
    parser.add_argument("--prompt-version", type=str, default=None, help="Explicit prompt version override")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output evidence directory")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    if args.output_dir:
        evidence_dir = args.output_dir
    elif args.mode == "baseline":
        evidence_dir = base_dir / "evidence" / "initial-generation"
    else:
        evidence_dir = base_dir / "evidence" / "final-generation"

    if args.prompt_version:
        prompt_version = args.prompt_version
    elif args.mode == "baseline":
        prompt_version = "v1.0.0"
    else:
        prompt_version = "v2.1.0"
    runner = EvaluationRunner(dataset_path=args.dataset, config_path=args.config)
    print(f"Starting evaluation benchmark [Mode: {args.mode}, Prompt: {prompt_version}]...")
    results = asyncio.run(runner.run_benchmark(prompt_version=prompt_version))

    out_json = evidence_dir / "eval-results.json"
    out_md = evidence_dir / "harness-log.md"

    EvaluationRunner.save_results(results, out_json)
    EvaluationRunner.save_harness_log(results, out_md)

    print(f"Benchmark complete. Status: {results['status']}")
    print(f"- JSON evidence: {out_json}")
    print(f"- Log transcript: {out_md}")
    print(f"- Evaluated cases: {results['metrics']['evaluated_cases_count']}/{results['summary']['total_cases']}")
    print(f"- Unevaluable cases: {results['metrics']['unevaluable_cases_count']}")
    print(f"- Schema Adherence: {results['metrics']['schema_adherence'] * 100:.1f}%")
    print(f"- Invariant Compliance: {results['metrics']['invariant_compliance'] * 100:.1f}%")
    print(f"- Precision: {results['metrics']['precision'] * 100:.1f}%")
    print(f"- Recall: {results['metrics']['recall'] * 100:.1f}%")
    print(f"- F1 Score: {results['metrics']['f1_score'] * 100:.1f}%")
    print(f"- False-Positive Rate: {results['metrics']['false_positive_rate'] * 100:.1f}%")
    print(f"- Average Latency: {results['metrics']['avg_latency_ms']} ms")
    print(f"- p95 Latency: {results['metrics']['p95_latency_ms']} ms")
