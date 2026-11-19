"""Unit tests for independent evaluation metric scorers and validation gates (T042)."""

from evals.metrics import (
    compute_invariant_compliance,
    compute_percentile,
    compute_schema_adherence,
    compute_semantic_metrics,
    validate_invariants,
    validate_schema,
)


def test_schema_adherence_scorer():
    # 10 valid responses
    valid_results = [{"is_schema_valid": True} for _ in range(10)]
    assert compute_schema_adherence(valid_results) == 1.0

    # 9 valid, 1 invalid
    mixed_results = [{"is_schema_valid": True} for _ in range(9)] + [{"is_schema_valid": False}]
    assert compute_schema_adherence(mixed_results) == 0.9

    # Empty list (zero evaluable cases returns 0.0 to prevent false PASS)
    assert compute_schema_adherence([]) == 0.0


def test_invariant_compliance_scorer():
    valid_results = [{"is_invariant_compliant": True} for _ in range(5)]
    assert compute_invariant_compliance(valid_results) == 1.0

    mixed_results = [
        {"is_invariant_compliant": True},
        {"is_invariant_compliant": False},
    ]
    assert compute_invariant_compliance(mixed_results) == 0.5

    # Empty list returns 0.0
    assert compute_invariant_compliance([]) == 0.0


def test_scorer_with_unevaluable_provider_errors():
    # Unevaluable cases are excluded from the denominator:
    # 1 valid evaluable case, 1 unevaluable provider error -> 1 / 1 = 1.0
    results_one_evaluable = [
        {"is_schema_valid": True, "is_invariant_compliant": True, "is_unevaluable": False},
        {"is_schema_valid": False, "is_invariant_compliant": False, "is_unevaluable": True},  # provider failure
    ]
    assert compute_schema_adherence(results_one_evaluable) == 1.0
    assert compute_invariant_compliance(results_one_evaluable) == 1.0

    # 2 evaluable cases (1 valid, 1 invalid), 1 unevaluable provider error -> 1 / 2 = 0.5
    results_mixed = [
        {"is_schema_valid": True, "is_invariant_compliant": True, "is_unevaluable": False},
        {"is_schema_valid": False, "is_invariant_compliant": False, "is_unevaluable": False},
        {"is_schema_valid": False, "is_invariant_compliant": False, "is_unevaluable": True},
    ]
    assert compute_schema_adherence(results_mixed) == 0.5
    assert compute_invariant_compliance(results_mixed) == 0.5

    # Zero evaluable cases (only provider errors) -> 0.0
    results_only_errors = [
        {"is_schema_valid": False, "is_invariant_compliant": False, "is_unevaluable": True},
    ]
    assert compute_schema_adherence(results_only_errors) == 0.0
    assert compute_invariant_compliance(results_only_errors) == 0.0


def test_semantic_metrics_scorer_perfect():
    # TP = 4, TN = 4, FP = 0, FN = 0
    predictions = [True, True, True, True, False, False, False, False]
    ground_truth = [True, True, True, True, False, False, False, False]

    metrics = compute_semantic_metrics(predictions, ground_truth)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1_score"] == 1.0
    assert metrics["false_positive_rate"] == 0.0


def test_semantic_metrics_scorer_with_fp_and_fn():
    # TP = 3, FP = 1, FN = 1, TN = 3
    predictions = [True, True, True, True, False, False, False, False]
    ground_truth = [True, True, True, False, True, False, False, False]

    metrics = compute_semantic_metrics(predictions, ground_truth)
    assert metrics["precision"] == 0.75
    assert metrics["recall"] == 0.75
    assert metrics["f1_score"] == 0.75
    assert metrics["false_positive_rate"] == 0.25


def test_semantic_metrics_empty():
    metrics = compute_semantic_metrics([], [])
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["f1_score"] == 0.0
    assert metrics["false_positive_rate"] == 0.0


def test_compute_percentile():
    assert compute_percentile([]) == 0.0
    latencies = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    p95 = compute_percentile(latencies, 95.0)
    assert 900 <= p95 <= 1000


# --- Independent Schema Validation Tests ---


def test_validate_schema_valid_payload():
    payload = {
        "findings": [
            {
                "id": "F001",
                "title": "SQL Injection",
                "category": "SECURITY",
                "severity": "CRITICAL",
                "start_line": 2,
                "end_line": 3,
                "description": "Unsanitized user input in raw SQL query.",
                "recommendation": "Use parameterized queries.",
                "confidence": 0.95,
            }
        ],
        "summary": {
            "status": "FAIL",
            "total_findings": 1,
            "critical_count": 1,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "info_count": 0,
        },
        "telemetry": {
            "model_id": "openai/gpt-oss-120b",
            "prompt_version": "v2.1.0",
            "latency_ms": 1200,
        },
    }
    is_valid, errors = validate_schema(payload, expected_http_status=200)
    assert is_valid is True
    assert errors == []


def test_validate_schema_missing_required_fields():
    # Missing 'findings' key
    payload_no_findings = {
        "summary": {"status": "PASS"},
        "telemetry": {"model_id": "openai/gpt-oss-120b"},
    }
    is_valid, errors = validate_schema(payload_no_findings, expected_http_status=200)
    assert is_valid is False
    assert any("findings" in err for err in errors)

    # Finding missing required 'title' and 'severity'
    payload_bad_finding = {
        "findings": [
            {
                "id": "F001",
                "category": "BUG",
                "start_line": 1,
                "end_line": 1,
                "description": "Desc",
                "recommendation": "Rec",
                "confidence": 0.9,
            }
        ],
        "summary": {"status": "PASS"},
        "telemetry": {"model_id": "openai/gpt-oss-120b"},
    }
    is_valid, errors = validate_schema(payload_bad_finding, expected_http_status=200)
    assert is_valid is False
    assert any("title" in err or "severity" in err for err in errors)


def test_validate_schema_invalid_enum():
    payload = {
        "findings": [
            {
                "id": "F001",
                "title": "Invalid enum test",
                "category": "NOT_A_CATEGORY",
                "severity": "MEGA_CRITICAL",
                "start_line": 1,
                "end_line": 1,
                "description": "Desc",
                "recommendation": "Rec",
                "confidence": 0.9,
            }
        ],
        "summary": {"status": "PASS"},
        "telemetry": {"model_id": "openai/gpt-oss-120b"},
    }
    is_valid, errors = validate_schema(payload, expected_http_status=200)
    assert is_valid is False
    assert len(errors) >= 1


def test_validate_schema_deterministic_http_error():
    # Valid ErrorResponse for HTTP 422
    err_payload = {
        "error_code": "SECRET_DETECTED",
        "message": "Secret pattern detected.",
        "status_code": 422,
        "details": [{"line": 1, "pattern": "Groq API Key"}],
    }
    is_valid, errors = validate_schema(err_payload, expected_http_status=422)
    assert is_valid is True
    assert errors == []

    # Status code mismatch (expected 422, got 500)
    err_payload_mismatch = {
        "error_code": "INTERNAL_ERROR",
        "message": "Error",
        "status_code": 500,
    }
    is_valid, errors = validate_schema(err_payload_mismatch, expected_http_status=422)
    assert is_valid is False
    assert any("mismatch" in err.lower() for err in errors)


# --- Independent Invariant Validation Tests ---


def test_validate_invariants_valid_payload():
    code = "def sample():\n    return 42\n"
    payload = {
        "findings": [
            {
                "id": "F001",
                "title": "Style issue",
                "category": "MAINTAINABILITY",
                "severity": "LOW",
                "start_line": 1,
                "end_line": 2,
                "description": "Function docstring missing.",
                "recommendation": "Add docstring.",
                "confidence": 0.8,
            }
        ],
        "summary": {
            "status": "PASS",
            "total_findings": 1,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 1,
            "info_count": 0,
        },
    }
    is_compliant, violations = validate_invariants(payload, code=code, expected_http_status=200)
    assert is_compliant is True
    assert violations == []


def test_validate_invariants_line_range_exceeds_source():
    # Code has 2 lines, finding claims end_line 10
    code = "x = 1\ny = 2\n"
    payload = {
        "findings": [
            {
                "id": "F001",
                "title": "Out of bounds",
                "category": "BUG",
                "severity": "HIGH",
                "start_line": 1,
                "end_line": 10,
                "confidence": 0.9,
            }
        ],
        "summary": {
            "status": "FAIL",
            "total_findings": 1,
            "critical_count": 0,
            "high_count": 1,
            "medium_count": 0,
            "low_count": 0,
            "info_count": 0,
        },
    }
    is_compliant, violations = validate_invariants(payload, code=code, expected_http_status=200)
    assert is_compliant is False
    assert any("exceeds total code lines" in v for v in violations)


def test_validate_invariants_line_boundaries_invalid():
    code = "x = 1\ny = 2\n"
    # start_line < 1
    payload_zero_start = {
        "findings": [
            {"id": "F001", "category": "BUG", "severity": "LOW", "start_line": 0, "end_line": 1, "confidence": 0.5}
        ],
        "summary": {"status": "PASS", "total_findings": 1, "low_count": 1},
    }
    is_compliant, violations = validate_invariants(payload_zero_start, code=code)
    assert is_compliant is False
    assert any("cannot be less than 1" in v for v in violations)

    # start_line > end_line
    payload_inverted = {
        "findings": [
            {"id": "F001", "category": "BUG", "severity": "LOW", "start_line": 2, "end_line": 1, "confidence": 0.5}
        ],
        "summary": {"status": "PASS", "total_findings": 1, "low_count": 1},
    }
    is_compliant, violations = validate_invariants(payload_inverted, code=code)
    assert is_compliant is False
    assert any("exceeds end_line" in v for v in violations)


def test_validate_invariants_duplicate_findings():
    code = "def foo(): pass\n"
    payload = {
        "findings": [
            {
                "id": "F001",
                "title": "Unused function",
                "category": "MAINTAINABILITY",
                "severity": "LOW",
                "start_line": 1,
                "end_line": 1,
                "confidence": 0.8,
            },
            {
                "id": "F002",
                "title": "Unused function",
                "category": "MAINTAINABILITY",
                "severity": "LOW",
                "start_line": 1,
                "end_line": 1,
                "confidence": 0.8,
            },
        ],
        "summary": {
            "status": "PASS",
            "total_findings": 2,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 2,
            "info_count": 0,
        },
    }
    is_compliant, violations = validate_invariants(payload, code=code, expected_http_status=200)
    assert is_compliant is False
    assert any("duplicate finding detected" in v.lower() for v in violations)


def test_validate_invariants_summary_consistency_failure():
    code = "def foo(): return 1 / 0\n"
    # Finding is CRITICAL, but summary says PASS
    payload_wrong_gate = {
        "findings": [
            {
                "id": "F001",
                "title": "Division by zero",
                "category": "BUG",
                "severity": "CRITICAL",
                "start_line": 1,
                "end_line": 1,
                "confidence": 0.99,
            }
        ],
        "summary": {
            "status": "PASS",  # Should be FAIL because of CRITICAL severity!
            "total_findings": 1,
            "critical_count": 1,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "info_count": 0,
        },
    }
    is_compliant, violations = validate_invariants(payload_wrong_gate, code=code, expected_http_status=200)
    assert is_compliant is False
    assert any("status 'PASS' does not match expected 'FAIL'" in v for v in violations)

    # Count mismatch: 1 finding present, but summary claims 5
    payload_count_mismatch = {
        "findings": [
            {
                "id": "F001",
                "title": "Division by zero",
                "category": "BUG",
                "severity": "CRITICAL",
                "start_line": 1,
                "end_line": 1,
                "confidence": 0.99,
            }
        ],
        "summary": {
            "status": "FAIL",
            "total_findings": 5,  # Mismatch
            "critical_count": 1,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "info_count": 0,
        },
    }
    is_compliant, violations = validate_invariants(payload_count_mismatch, code=code, expected_http_status=200)
    assert is_compliant is False
    assert any("total_findings (5) != actual findings count (1)" in v for v in violations)


def test_validate_invariants_confidence_bounds():
    code = "x = 1\n"
    payload = {
        "findings": [
            {
                "id": "F001",
                "title": "High confidence error",
                "category": "BUG",
                "severity": "LOW",
                "start_line": 1,
                "end_line": 1,
                "confidence": 1.5,  # Out of bounds!
            }
        ],
        "summary": {"status": "PASS", "total_findings": 1, "low_count": 1},
    }
    is_compliant, violations = validate_invariants(payload, code=code, expected_http_status=200)
    assert is_compliant is False
    assert any("confidence (1.5) out of [0.0, 1.0]" in v for v in violations)


def test_validate_invariants_secret_leak_in_error():
    code = 'GROQ_API_KEY = "gsk_supersecretkey1234567890abcdef"\n'
    leaking_error = {
        "error_code": "SECRET_DETECTED",
        "message": "Found key: gsk_supersecretkey1234567890abcdef",  # Leaked!
        "status_code": 422,
    }
    is_compliant, violations = validate_invariants(leaking_error, code=code, expected_http_status=422)
    assert is_compliant is False
    assert any("credential pattern was echoed" in v.lower() for v in violations)
