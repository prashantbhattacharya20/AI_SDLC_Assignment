"""Automated execution and verification of Quickstart validation scenarios (T054).

Cites: Part-1B/specs/001-code-review-assistant/quickstart.md
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.review_service import get_review_service


@pytest.fixture
def client():
    return TestClient(app)


def test_quickstart_scenario_1_healthcheck(client):
    """Scenario 1: Healthcheck verification."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["provider"] == "groq"
    assert data["version"] == "1.0.0"


def test_quickstart_scenario_2_normal_defect_detection(client):
    """Scenario 2: Normal Code Review (Defect Detection with mocked LLM)."""
    canned_result = {
        "findings": [
            {
                "id": "F001",
                "title": "SQL Injection Vulnerability",
                "category": "SECURITY",
                "severity": "CRITICAL",
                "start_line": 2,
                "end_line": 2,
                "description": "Raw string concatenation in SQL execute query",
                "recommendation": "Use parameterized queries",
                "confidence": 0.98,
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
            "prompt_version": "v1.0.0",
            "latency_ms": 320,
            "prompt_tokens": 150,
            "completion_tokens": 80,
            "total_tokens": 230,
            "retry_count": 0,
        },
        "markdown_report": "# Code Review Report\n...",
    }

    mock_service = AsyncMock()
    mock_service.review_code.return_value = canned_result

    app.dependency_overrides[get_review_service] = lambda: mock_service
    try:
        resp = client.post(
            "/api/v1/review",
            json={
                "code": "def get_user(db, username):\n    query = f\"SELECT * FROM users WHERE name = '{username}'\"\n    return db.execute(query).fetchone()",
                "file_path": "services/user_service.py",
                "language": "python",
                "include_markdown": True,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["status"] == "FAIL"
        assert len(data["findings"]) == 1
        assert data["findings"][0]["category"] == "SECURITY"
        assert data["findings"][0]["severity"] == "CRITICAL"
        assert data["telemetry"]["model_id"] == "openai/gpt-oss-120b"
    finally:
        app.dependency_overrides.clear()


def test_quickstart_scenario_3_clean_code(client):
    """Scenario 3: Clean Code Submission."""
    canned_result = {
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
            "latency_ms": 110,
            "prompt_tokens": 90,
            "completion_tokens": 15,
            "total_tokens": 105,
            "retry_count": 0,
        },
        "markdown_report": "# Code Review Report\n- Status: PASS",
    }

    mock_service = AsyncMock()
    mock_service.review_code.return_value = canned_result

    app.dependency_overrides[get_review_service] = lambda: mock_service
    try:
        resp = client.post(
            "/api/v1/review",
            json={
                "code": "def calculate_rectangle_area(width: float, height: float) -> float:\n    return width * height\n",
                "file_path": "utils/geometry.py",
                "language": "python",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["status"] == "PASS"
        assert data["summary"]["total_findings"] == 0
        assert len(data["findings"]) == 0
    finally:
        app.dependency_overrides.clear()


def test_quickstart_scenario_4_secret_detection_rejection(client):
    """Scenario 4: Secret Detection Rejection (Security Hygiene)."""
    resp = client.post(
        "/api/v1/review",
        json={
            "code": 'GROQ_KEY = "gsk_abcdefghijklmnopqrstuvwxyz012345678901234567890123"\nclient = Groq(api_key=GROQ_KEY)',
            "language": "python",
        },
    )
    assert resp.status_code == 422
    data = resp.json()
    assert data["error_code"] == "SECRET_DETECTED"
    assert "gsk_abcdefghijklmnopqrstuvwxyz" not in str(data)


def test_quickstart_scenario_5_deterministic_syntax_error(client):
    """Scenario 5: Deterministic Syntax Error Interception without LLM."""
    resp = client.post(
        "/api/v1/review",
        json={
            "code": 'def broken_func(:\n    print("Hello world")',
            "language": "python",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"]["status"] == "FAIL"
    assert data["telemetry"]["model_id"] == "deterministic-ast"
    assert len(data["findings"]) == 1
    assert data["findings"][0]["category"] == "BUG"
    assert data["findings"][0]["severity"] == "CRITICAL"


def test_quickstart_scenario_6_unsupported_language_rejection(client):
    """Scenario 6: Unsupported Language Rejection."""
    resp = client.post(
        "/api/v1/review",
        json={
            "code": 'console.log("Hello world");',
            "language": "javascript",
        },
    )
    assert resp.status_code == 422
    data = resp.json()
    assert (
        "language" in str(data).lower()
        or data.get("error_code") == "UNSUPPORTED_LANGUAGE"
        or data.get("error_code") == "VALIDATION_ERROR"
    )


def test_quickstart_scenario_7_oversized_payload_rejection(client):
    """Scenario 7: Oversized Payload Rejection."""
    oversized_lines = "\n".join([f"x_{i} = {i}" for i in range(1050)])
    resp = client.post(
        "/api/v1/review",
        json={
            "code": oversized_lines,
            "language": "python",
        },
    )
    assert resp.status_code == 413
    data = resp.json()
    assert data["error_code"] == "PAYLOAD_TOO_LARGE"
