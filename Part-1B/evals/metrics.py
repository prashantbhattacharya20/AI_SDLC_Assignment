"""Independent evaluation metric scorers and validation gates across three dimensions.

Dimension A: Schema Adherence (100% target)
Dimension B: Deterministic Invariant Compliance (100% target)
Dimension C: Semantic Quality (Precision >=80%, Recall >=80%, F1 >=80%, FPR <=15%)

Cites: Part-1B/specs/001-code-review-assistant/plan.md (Evaluation Strategy)
"""

from typing import Any

from pydantic import ValidationError

from src.schemas.enums import DefectCategory, ReviewStatus, SeverityLevel
from src.schemas.errors import ErrorResponse
from src.schemas.response import CodeReviewResponse


def validate_schema(
    payload: Any,
    expected_http_status: int = 200,
) -> tuple[bool, list[str]]:
    """Validate that a model response payload strictly conforms to the declared Pydantic schema.

    - When expected_http_status == 200: Validates against CodeReviewResponse (including
      nested ReviewFinding, ReviewSummary, and ReviewTelemetry).
    - When expected_http_status != 200: Validates against ErrorResponse and verifies
      the HTTP status_code matches expected_http_status.

    Returns:
        tuple[bool, list[str]]: (is_schema_valid, list_of_error_descriptions)
    """
    if not isinstance(payload, dict):
        return False, ["Payload must be a dictionary"]

    errors: list[str] = []

    if expected_http_status == 200:
        for required_key in ("findings", "summary", "telemetry"):
            if required_key not in payload:
                errors.append(f"Schema violation: Missing required top-level field '{required_key}'")

        try:
            CodeReviewResponse.model_validate(payload)
        except ValidationError as exc:
            for err in exc.errors():
                loc = ".".join(str(p) for p in err["loc"])
                errors.append(f"Schema violation at '{loc}': {err['msg']}")
        except Exception as exc:
            errors.append(f"Unexpected schema validation failure: {exc}")

        return len(errors) == 0, errors
    else:
        try:
            err_obj = ErrorResponse.model_validate(payload)
            if err_obj.status_code != expected_http_status:
                errors.append(f"HTTP status code mismatch: expected {expected_http_status}, got {err_obj.status_code}")
                return False, errors
        except ValidationError as exc:
            for err in exc.errors():
                loc = ".".join(str(p) for p in err["loc"])
                errors.append(f"Error schema violation at '{loc}': {err['msg']}")
            return False, errors
        except Exception as exc:
            return False, [f"Unexpected error schema validation failure: {exc}"]
        return True, []


def validate_invariants(
    payload: Any,
    code: str,
    expected_http_status: int = 200,
) -> tuple[bool, list[str]]:
    """Validate that a review result satisfies all deterministic physical and domain invariants.

    Invariants evaluated:
    1. Line boundary limits: 1 <= start_line <= end_line <= total_lines_in_code
    2. Category enum compliance: category in DefectCategory (BUG, SECURITY, PERFORMANCE, MAINTAINABILITY)
    3. Severity enum compliance: severity in SeverityLevel (CRITICAL, HIGH, MEDIUM, LOW, INFO)
    4. Duplicate suppression: No duplicate findings sharing (category, start_line, end_line, normalized title)
    5. Summary counts consistency: total_findings == len(findings), and per-severity counts match findings
    6. Quality gate consistency: status == FAIL if critical_count > 0 or high_count > 0, else PASS
    7. Confidence bounds: 0.0 <= confidence <= 1.0 for each finding
    8. Deterministic error invariants (non-200): status_code matches, error_code present, no raw credentials echoed

    Returns:
        tuple[bool, list[str]]: (is_invariant_compliant, list_of_invariant_violations)
    """
    if not isinstance(payload, dict):
        return False, ["Payload must be a dictionary"]

    errors: list[str] = []

    if expected_http_status != 200:
        # Expected deterministic HTTP error response (e.g. TC-ADV-02 secret screening)
        status_code = payload.get("status_code")
        if status_code != expected_http_status:
            errors.append(f"Invariant violation: status_code ({status_code}) != expected ({expected_http_status})")
        if not payload.get("error_code"):
            errors.append("Invariant violation: error_code must be non-empty in error response")

        # Privacy invariant: ensure raw credential tokens are never echoed
        msg = str(payload.get("message", ""))
        details_str = str(payload.get("details", []))
        if "gsk_" in msg or "gsk_" in details_str:
            errors.append("Invariant violation: Raw API credential pattern was echoed in error response")

        return len(errors) == 0, errors

    # Standard review response (HTTP 200)
    total_lines = len(code.splitlines()) or 1
    findings = payload.get("findings")
    if not isinstance(findings, list):
        return False, ["Invariant violation: 'findings' must be a list"]

    summary = payload.get("summary")
    if not isinstance(summary, dict):
        return False, ["Invariant violation: 'summary' must be a dict"]

    valid_categories = {c.value for c in DefectCategory}
    valid_severities = {s.value for s in SeverityLevel}

    seen_dedup_keys: set[tuple[str, int, int, str]] = set()
    crit_count = 0
    high_count = 0
    med_count = 0
    low_count = 0
    info_count = 0

    for idx, f in enumerate(findings):
        if not isinstance(f, dict):
            errors.append(f"Finding [{idx}] is not a dict")
            continue

        f_id = f.get("id", f"F{idx + 1}")
        start_line = f.get("start_line")
        end_line = f.get("end_line")
        category = f.get("category")
        severity = f.get("severity")
        confidence = f.get("confidence")
        title = str(f.get("title", "")).strip().lower()

        # Invariant 1: Line number boundaries
        if not isinstance(start_line, int) or not isinstance(end_line, int):
            errors.append(f"Finding {f_id}: start_line or end_line is not an integer")
        else:
            if start_line < 1:
                errors.append(f"Finding {f_id}: start_line ({start_line}) cannot be less than 1")
            if start_line > end_line:
                errors.append(f"Finding {f_id}: start_line ({start_line}) exceeds end_line ({end_line})")
            if end_line > total_lines:
                errors.append(f"Finding {f_id}: end_line ({end_line}) exceeds total code lines ({total_lines})")

        # Invariant 2: Category enum
        if category not in valid_categories:
            errors.append(f"Finding {f_id}: category '{category}' not in DefectCategory")

        # Invariant 3: Severity enum
        if severity not in valid_severities:
            errors.append(f"Finding {f_id}: severity '{severity}' not in SeverityLevel")
        else:
            if severity == SeverityLevel.CRITICAL.value:
                crit_count += 1
            elif severity == SeverityLevel.HIGH.value:
                high_count += 1
            elif severity == SeverityLevel.MEDIUM.value:
                med_count += 1
            elif severity == SeverityLevel.LOW.value:
                low_count += 1
            elif severity == SeverityLevel.INFO.value:
                info_count += 1

        # Invariant 4: Confidence range
        if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
            errors.append(f"Finding {f_id}: confidence ({confidence}) out of [0.0, 1.0] bounds")

        # Invariant 5: Deduplication check
        if isinstance(start_line, int) and isinstance(end_line, int) and category:
            dedup_key = (category, start_line, end_line, title)
            if dedup_key in seen_dedup_keys:
                errors.append(f"Duplicate finding detected: {dedup_key}")
            seen_dedup_keys.add(dedup_key)

    # Invariant 6: Summary count consistency
    if summary.get("total_findings") != len(findings):
        errors.append(
            f"Summary total_findings ({summary.get('total_findings')}) != actual findings count ({len(findings)})"
        )
    if summary.get("critical_count") != crit_count:
        errors.append(f"Summary critical_count ({summary.get('critical_count')}) != actual ({crit_count})")
    if summary.get("high_count") != high_count:
        errors.append(f"Summary high_count ({summary.get('high_count')}) != actual ({high_count})")
    if summary.get("medium_count") != med_count:
        errors.append(f"Summary medium_count ({summary.get('medium_count')}) != actual ({med_count})")
    if summary.get("low_count") != low_count:
        errors.append(f"Summary low_count ({summary.get('low_count')}) != actual ({low_count})")
    if summary.get("info_count") != info_count:
        errors.append(f"Summary info_count ({summary.get('info_count')}) != actual ({info_count})")

    # Invariant 7: Quality Gate rule (FAIL if critical > 0 or high > 0, else PASS)
    expected_status = ReviewStatus.FAIL.value if (crit_count > 0 or high_count > 0) else ReviewStatus.PASS.value
    if summary.get("status") != expected_status:
        errors.append(f"Summary status '{summary.get('status')}' does not match expected '{expected_status}'")

    return len(errors) == 0, errors


def compute_schema_adherence(results: list[dict[str, Any]]) -> float:
    """Compute Dimension A: Percentage of evaluable model outputs adhering strictly to the JSON schema.

    Scoring formula:
        Schema Adherence = (Valid Evaluable Responses) / (Total Evaluable Responses)
    Unevaluable provider failures are excluded from the denominator.
    If there are zero evaluable cases, returns 0.0 to prevent false PASS.
    """
    evaluable = [r for r in results if not r.get("is_unevaluable", False)]
    if not evaluable:
        return 0.0

    valid_count = sum(1 for r in evaluable if r.get("is_schema_valid", False))
    return round(valid_count / len(evaluable), 4)


def compute_invariant_compliance(results: list[dict[str, Any]]) -> float:
    """Compute Dimension B: Percentage of evaluable outputs satisfying deterministic invariants.

    Scoring formula:
        Invariant Compliance = (Compliant Evaluable Responses) / (Total Evaluable Responses)
    Unevaluable provider failures are excluded from the denominator.
    If there are zero evaluable cases, returns 0.0 to prevent false PASS.
    """
    evaluable = [r for r in results if not r.get("is_unevaluable", False)]
    if not evaluable:
        return 0.0

    compliant_count = sum(1 for r in evaluable if r.get("is_invariant_compliant", False))
    return round(compliant_count / len(evaluable), 4)


def compute_percentile(values: list[int | float], percentile: float = 95.0) -> float:
    """Compute the given percentile (e.g. 95th) of a list of numeric values using linear interpolation."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (percentile / 100.0)
    f = int(k)
    c = f + 1
    if c < len(sorted_vals):
        return round(float(sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f])), 2)
    return round(float(sorted_vals[f]), 2)


def compute_semantic_metrics(predictions: list[bool], ground_truth: list[bool]) -> dict[str, float]:
    """Compute Dimension C: Precision, Recall, F1 Score, and False-Positive Rate.

    Args:
        predictions: Boolean list where True indicates a defect was predicted (FAIL / finding present).
        ground_truth: Boolean list where True indicates a genuine defect exists (is_clean == False).
    """
    if len(predictions) != len(ground_truth):
        raise ValueError("Predictions and ground_truth lists must have identical lengths.")

    if not predictions:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "false_positive_rate": 0.0,
            "tp": 0,
            "fp": 0,
            "fn": 0,
            "tn": 0,
        }

    tp = sum(1 for p, g in zip(predictions, ground_truth, strict=False) if p is True and g is True)
    fp = sum(1 for p, g in zip(predictions, ground_truth, strict=False) if p is True and g is False)
    fn = sum(1 for p, g in zip(predictions, ground_truth, strict=False) if p is False and g is True)
    tn = sum(1 for p, g in zip(predictions, ground_truth, strict=False) if p is False and g is False)

    precision = tp / (tp + fp) if (tp + fp) > 0 else (1.0 if sum(ground_truth) == 0 else 0.0)
    recall = tp / (tp + fn) if (tp + fn) > 0 else (1.0 if sum(ground_truth) == 0 else 0.0)
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }
