"""Unit tests for evaluation harness runner and gate enforcement (T043)."""

import json
from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_evaluation_runner_execution_and_threshold_check(tmp_path):
    from evals.runner import EvaluationRunner

    dataset_file = tmp_path / "dataset.json"
    dataset_file.write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "cases": [
                    {
                        "id": "C1",
                        "category": "normal",
                        "code": "def clean(): pass\n",
                        "language": "python",
                        "is_clean": True,
                        "expected_status": "PASS",
                    },
                    {
                        "id": "C2",
                        "category": "normal",
                        "code": "def bug(): return 1 / 0\n",
                        "language": "python",
                        "is_clean": False,
                        "expected_status": "FAIL",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "benchmark_version": "1.0.0",
                "model_id": "openai/gpt-oss-120b",
                "thresholds": {
                    "schema_adherence_min": 1.0,
                    "invariant_compliance_min": 1.0,
                    "precision_min": 0.80,
                    "recall_min": 0.80,
                    "f1_score_min": 0.80,
                    "false_positive_rate_max": 0.15,
                },
            }
        ),
        encoding="utf-8",
    )

    runner = EvaluationRunner(dataset_path=dataset_file, config_path=config_file)

    mock_service = AsyncMock()
    mock_service.prompt_version = "v2.1.0"
    mock_service.review_code.side_effect = [
        # Case 1: clean code -> PASS
        {
            "findings": [],
            "summary": {
                "status": "PASS",
                "total_findings": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "info_count": 0,
            },
            "telemetry": {
                "model_id": "openai/gpt-oss-120b",
                "prompt_version": "v2.1.0",
                "latency_ms": 100,
            },
        },
        # Case 2: bug code -> FAIL
        {
            "findings": [
                {
                    "id": "F001",
                    "title": "ZeroDivisionError",
                    "category": "BUG",
                    "severity": "HIGH",
                    "start_line": 1,
                    "end_line": 1,
                    "description": "Zero division error",
                    "recommendation": "Check denominator before division",
                    "confidence": 0.95,
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
            "telemetry": {
                "model_id": "openai/gpt-oss-120b",
                "prompt_version": "v2.1.0",
                "latency_ms": 120,
            },
        },
    ]

    report = await runner.run_benchmark(review_service=mock_service)
    assert report["summary"]["total_cases"] == 2
    assert report["metrics"]["schema_adherence"] == 1.0
    assert report["metrics"]["invariant_compliance"] == 1.0
    assert report["metrics"]["precision"] == 1.0
    assert report["metrics"]["recall"] == 1.0
    assert report["metrics"]["f1_score"] == 1.0
    assert report["metrics"]["false_positive_rate"] == 0.0
    assert report["status"] == "PASS"


@pytest.mark.asyncio
async def test_evaluation_runner_schema_failure_causes_fail_gate(tmp_path):
    from evals.runner import EvaluationRunner

    dataset_file = tmp_path / "dataset.json"
    dataset_file.write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "cases": [
                    {
                        "id": "C1",
                        "category": "normal",
                        "code": "def clean(): pass\n",
                        "language": "python",
                        "is_clean": True,
                        "expected_status": "PASS",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "benchmark_version": "1.0.0",
                "model_id": "openai/gpt-oss-120b",
                "thresholds": {"schema_adherence_min": 1.0},
            }
        ),
        encoding="utf-8",
    )

    runner = EvaluationRunner(dataset_path=dataset_file, config_path=config_file)
    mock_service = AsyncMock()
    mock_service.prompt_version = "v2.1.0"
    # Service returns malformed schema (missing 'findings' and 'summary')
    mock_service.review_code.return_value = {"invalid_key": 123}

    report = await runner.run_benchmark(review_service=mock_service)
    assert report["metrics"]["schema_adherence"] == 0.0
    assert report["threshold_eval"]["schema_adherence"] is False
    assert report["status"] == "FAIL"
    assert len(report["case_results"][0]["schema_errors"]) > 0


@pytest.mark.asyncio
async def test_evaluation_runner_invariant_failure_causes_fail_gate(tmp_path):
    from evals.runner import EvaluationRunner

    dataset_file = tmp_path / "dataset.json"
    dataset_file.write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "cases": [
                    {
                        "id": "C1",
                        "category": "normal",
                        "code": "def clean(): pass\n",  # 1 line of code
                        "language": "python",
                        "is_clean": False,
                        "expected_status": "FAIL",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "benchmark_version": "1.0.0",
                "model_id": "openai/gpt-oss-120b",
                "thresholds": {"invariant_compliance_min": 1.0},
            }
        ),
        encoding="utf-8",
    )

    runner = EvaluationRunner(dataset_path=dataset_file, config_path=config_file)
    mock_service = AsyncMock()
    mock_service.prompt_version = "v2.1.0"
    # Valid schema, but line number invariant violated (end_line = 99 exceeds 1 line)
    mock_service.review_code.return_value = {
        "findings": [
            {
                "id": "F001",
                "title": "Bug",
                "category": "BUG",
                "severity": "HIGH",
                "start_line": 1,
                "end_line": 99,
                "description": "Desc",
                "recommendation": "Fix",
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
        "telemetry": {"model_id": "openai/gpt-oss-120b", "latency_ms": 50},
    }

    report = await runner.run_benchmark(review_service=mock_service)
    assert report["metrics"]["schema_adherence"] == 1.0
    assert report["metrics"]["invariant_compliance"] == 0.0
    assert report["threshold_eval"]["invariant_compliance"] is False
    assert report["status"] == "FAIL"
    assert any("exceeds total code lines" in err for err in report["case_results"][0]["invariant_errors"])


@pytest.mark.asyncio
async def test_evaluation_runner_expected_http_deterministic_validation(tmp_path):
    from evals.runner import EvaluationRunner
    from src.schemas.errors import SecretDetectedError

    dataset_file = tmp_path / "dataset.json"
    dataset_file.write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "cases": [
                    {
                        "id": "TC-ADV-02",
                        "category": "adversarial",
                        "code": 'GROQ_API_KEY = "gsk_test1234567890abcdef"\n',
                        "language": "python",
                        "is_clean": False,
                        "expected_http_status": 422,
                        "expected_status": "ERROR",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "benchmark_version": "1.0.0",
                "model_id": "openai/gpt-oss-120b",
                "thresholds": {
                    "schema_adherence_min": 1.0,
                    "invariant_compliance_min": 1.0,
                    "precision_min": 0.80,
                    "recall_min": 0.80,
                    "f1_score_min": 0.80,
                    "false_positive_rate_max": 0.15,
                },
            }
        ),
        encoding="utf-8",
    )

    runner = EvaluationRunner(dataset_path=dataset_file, config_path=config_file)
    mock_service = AsyncMock()
    mock_service.prompt_version = "v2.1.0"
    mock_service.review_code.side_effect = SecretDetectedError(
        message="Secret pattern detected in submitted source code.",
        details=[{"issue": "Detected pattern: Groq API Key (masked)", "line": 1}],
    )

    report = await runner.run_benchmark(review_service=mock_service)
    assert report["metrics"]["schema_adherence"] == 1.0
    assert report["metrics"]["invariant_compliance"] == 1.0
    assert report["metrics"]["evaluated_cases_count"] == 1
    assert report["metrics"]["unevaluable_cases_count"] == 0
    assert report["metrics"]["confusion_matrix"]["tp"] == 1
    assert report["case_results"][0]["is_schema_valid"] is True
    assert report["case_results"][0]["is_invariant_compliant"] is True
    assert report["case_results"][0]["error_code"] == "SECRET_DETECTED"


@pytest.mark.asyncio
async def test_evaluation_runner_provider_error_handling(tmp_path):
    from evals.runner import EvaluationRunner
    from src.schemas.errors import CodeReviewException

    dataset_file = tmp_path / "dataset.json"
    dataset_file.write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "cases": [
                    {
                        "id": "C1",
                        "category": "normal",
                        "code": "def clean(): pass\n",
                        "language": "python",
                        "is_clean": True,
                        "expected_status": "PASS",
                        "expected_http_status": 200,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "benchmark_version": "1.0.0",
                "model_id": "test-model",
                "thresholds": {"schema_adherence_min": 1.0},
            }
        ),
        encoding="utf-8",
    )

    runner = EvaluationRunner(dataset_path=dataset_file, config_path=config_file)
    mock_service = AsyncMock()
    mock_service.prompt_version = "v2.1.0"
    mock_service.review_code.side_effect = CodeReviewException(
        status_code=502,
        error_code="PROVIDER_UNAVAILABLE",
        message="Groq upstream failure",
    )

    report = await runner.run_benchmark(review_service=mock_service)
    assert report["status"] == "FAIL"
    assert report["metrics"]["unevaluable_cases_count"] == 1
    assert report["metrics"]["evaluated_cases_count"] == 0
    assert len(report["metrics"]["provider_errors"]) == 1
    assert report["threshold_eval"]["zero_provider_errors"] is False
    assert report["case_results"][0]["is_unevaluable"] is True
    assert report["case_results"][0]["is_provider_error"] is True
    assert report["case_results"][0]["is_schema_valid"] is False
    assert report["case_results"][0]["is_invariant_compliant"] is False
    assert report["metrics"]["schema_adherence"] == 0.0
    assert report["metrics"]["invariant_compliance"] == 0.0
    # Provider error isolated from confusion matrix
    assert report["metrics"]["confusion_matrix"]["tp"] == 0
    assert report["metrics"]["confusion_matrix"]["fp"] == 0
    assert report["metrics"]["confusion_matrix"]["fn"] == 0
    assert report["metrics"]["confusion_matrix"]["tn"] == 0


def test_save_results_and_harness_log(tmp_path):
    from evals.runner import EvaluationRunner

    results = {
        "status": "PASS",
        "benchmark_version": "1.0.0",
        "model_id": "openai/gpt-oss-120b",
        "prompt_version": "v1.0.0",
        "metrics": {
            "schema_adherence": 1.0,
            "invariant_compliance": 1.0,
            "precision": 0.85,
            "recall": 0.90,
            "f1_score": 0.87,
            "false_positive_rate": 0.10,
        },
        "summary": {
            "total_cases": 18,
            "passed_cases": 18,
            "failed_cases": 0,
        },
        "case_results": [],
    }

    out_json = tmp_path / "eval-results.json"
    out_md = tmp_path / "harness-log.md"

    EvaluationRunner.save_results(results, out_json)
    EvaluationRunner.save_harness_log(results, out_md)

    assert out_json.exists()
    assert out_md.exists()
    assert "openai/gpt-oss-120b" in out_md.read_text()
    assert "0.87" in out_json.read_text()
