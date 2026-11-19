"""Contract conformance tests for POST /api/v1/review (T017).

Validates against OpenAPI 3.1 specification at:
Part-1B/specs/001-code-review-assistant/contracts/code-review-api.yaml
"""

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

CONTRACT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "specs"
    / "001-code-review-assistant"
    / "contracts"
    / "code-review-api.yaml"
)


def test_openapi_contract_file_exists():
    assert CONTRACT_PATH.exists(), f"OpenAPI contract not found at {CONTRACT_PATH}"
    with open(CONTRACT_PATH, encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    assert spec["openapi"].startswith("3.1")
    assert "/api/v1/review" in spec["paths"]
    assert "post" in spec["paths"]["/api/v1/review"]


def test_post_review_contract_response_structure(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_api_key_1234567890abcdef")
    from unittest.mock import AsyncMock

    from src.main import app
    from src.services.review_service import get_review_service

    client = TestClient(app)
    payload = {
        "code": "def add(a: int, b: int) -> int:\n    return a + b\n",
        "file_path": "math_utils.py",
        "language": "python",
        "include_markdown": True,
    }

    mock_service = AsyncMock()
    mock_service.review_code.return_value = {
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
            "prompt_version": "v1.0.0",
            "latency_ms": 100,
            "prompt_tokens": 50,
            "completion_tokens": 10,
            "total_tokens": 60,
            "retry_count": 0,
        },
        "markdown_report": "Report",
    }

    app.dependency_overrides[get_review_service] = lambda: mock_service
    try:
        response = client.post("/api/v1/review", json=payload)
        assert response.status_code == 200
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    # Verify top-level contract properties
    assert "findings" in data
    assert "summary" in data
    assert "telemetry" in data
    assert isinstance(data["findings"], list)
    assert isinstance(data["summary"], dict)
    assert isinstance(data["telemetry"], dict)

    # Verify summary fields
    summary = data["summary"]
    for field in [
        "status",
        "total_findings",
        "critical_count",
        "high_count",
        "medium_count",
        "low_count",
        "info_count",
    ]:
        assert field in summary

    # Verify telemetry fields
    telemetry = data["telemetry"]
    for field in [
        "model_id",
        "prompt_version",
        "latency_ms",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "retry_count",
    ]:
        assert field in telemetry
