"""Integration tests for POST /api/v1/review endpoint (T019)."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_review_orchestrator(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_api_key_1234567890abcdef")


def test_review_endpoint_defect_detection(mock_review_orchestrator):
    from src.main import app
    from src.services.review_service import get_review_service

    client = TestClient(app)

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
            "latency_ms": 120,
            "prompt_tokens": 150,
            "completion_tokens": 80,
            "total_tokens": 230,
            "retry_count": 0,
        },
        "markdown_report": "### Code Review Report\n...",
    }

    mock_service = AsyncMock()
    mock_service.review_code.return_value = canned_result

    app.dependency_overrides[get_review_service] = lambda: mock_service

    try:
        response = client.post(
            "/api/v1/review",
            json={
                "code": "cursor.execute('SELECT * FROM users WHERE id = ' + user_id)\n",
                "file_path": "query.py",
                "language": "python",
                "include_markdown": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["status"] == "FAIL"
        assert len(data["findings"]) == 1
        assert data["findings"][0]["category"] == "SECURITY"
        assert data["findings"][0]["severity"] == "CRITICAL"
    finally:
        app.dependency_overrides.clear()


def test_review_endpoint_clean_code(mock_review_orchestrator):
    from src.main import app
    from src.services.review_service import get_review_service

    client = TestClient(app)

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
            "latency_ms": 95,
            "prompt_tokens": 80,
            "completion_tokens": 20,
            "total_tokens": 100,
            "retry_count": 0,
        },
        "markdown_report": "### Code Review Report\n- Status: PASS\n- Findings: 0",
    }

    mock_service = AsyncMock()
    mock_service.review_code.return_value = canned_result

    app.dependency_overrides[get_review_service] = lambda: mock_service

    try:
        response = client.post(
            "/api/v1/review",
            json={
                "code": "def square(n: int) -> int:\n    return n * n\n",
                "language": "python",
                "include_markdown": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["status"] == "PASS"
        assert len(data["findings"]) == 0
    finally:
        app.dependency_overrides.clear()


def test_review_endpoint_telemetry_and_markdown(mock_review_orchestrator):
    from src.main import app
    from src.services.review_service import get_review_service

    client = TestClient(app)

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
            "latency_ms": 250,
            "prompt_tokens": 120,
            "completion_tokens": 40,
            "total_tokens": 160,
            "retry_count": 0,
        },
        "markdown_report": "# Custom Markdown Report",
    }

    mock_service = AsyncMock()
    mock_service.review_code.return_value = canned_result

    app.dependency_overrides[get_review_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/review",
            json={"code": "x = 42\n", "include_markdown": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["telemetry"]["model_id"] == "openai/gpt-oss-120b"
        assert data["telemetry"]["latency_ms"] == 250
        assert data["telemetry"]["total_tokens"] == 160
        assert data["markdown_report"] == "# Custom Markdown Report"
    finally:
        app.dependency_overrides.clear()


def test_review_endpoint_omit_markdown(mock_review_orchestrator):
    from src.main import app
    from src.services.review_service import get_review_service

    client = TestClient(app)

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
            "prompt_tokens": 50,
            "completion_tokens": 10,
            "total_tokens": 60,
            "retry_count": 0,
        },
        "markdown_report": None,
    }

    mock_service = AsyncMock()
    mock_service.review_code.return_value = canned_result

    app.dependency_overrides[get_review_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/review",
            json={"code": "x = 42\n", "include_markdown": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["markdown_report"] is None
    finally:
        app.dependency_overrides.clear()
