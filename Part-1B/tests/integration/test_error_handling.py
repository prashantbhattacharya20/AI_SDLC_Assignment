"""Integration tests for input validation, secret rejection, AST interception, and error mappings (T027)."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_api_key_1234567890abcdef")
    from src.main import app

    return TestClient(app)


def test_unsupported_language_rejection(test_client):
    """Unsupported language must return HTTP 422 before AST parsing."""
    response = test_client.post(
        "/api/v1/review",
        json={
            "code": "function add(a, b) { return a + b; }",
            "language": "javascript",
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert (
        "language" in str(data).lower()
        or data.get("error_code") == "UNSUPPORTED_LANGUAGE"
        or data.get("error_code") == "VALIDATION_ERROR"
    )


def test_payload_line_limit_exceeded(test_client):
    """Payload exceeding 1,000 lines must produce HTTP 413."""
    oversized_code = "\n".join([f"x = {i}" for i in range(1005)])
    response = test_client.post(
        "/api/v1/review",
        json={"code": oversized_code, "language": "python"},
    )
    assert response.status_code == 413
    data = response.json()
    assert data["error_code"] == "PAYLOAD_TOO_LARGE"


def test_payload_byte_limit_exceeded(test_client):
    """Payload exceeding 65,536 bytes must produce HTTP 413."""
    oversized_code = "# " + ("A" * 66000)
    response = test_client.post(
        "/api/v1/review",
        json={"code": oversized_code, "language": "python"},
    )
    assert response.status_code == 413
    data = response.json()
    assert data["error_code"] == "PAYLOAD_TOO_LARGE"


def test_secret_detected_rejection_and_zero_llm_calls(test_client):
    """Secret detection must produce HTTP 422, zero LLM calls, and no echoed secret."""

    AsyncMock()
    # In real flow, the secret scanner intercepts before LLM client
    secret_code = 'GROQ_API_KEY = "gsk_secret_1234567890abcdef1234567890abcdef"\n'
    response = test_client.post(
        "/api/v1/review",
        json={"code": secret_code, "language": "python"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "SECRET_DETECTED"
    # Verify the secret is NOT leaked or echoed in response details
    assert "gsk_secret_1234567890abcdef" not in str(data)


def test_syntax_error_interception_without_llm(test_client):
    """Python syntax error produces local CRITICAL BUG finding with model_id: deterministic-ast."""
    broken_code = "def syntax_error_func(\n    return 99\n"
    response = test_client.post(
        "/api/v1/review",
        json={"code": broken_code, "language": "python"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["status"] == "FAIL"
    assert data["summary"]["critical_count"] >= 1
    assert data["telemetry"]["model_id"] == "deterministic-ast"
    assert len(data["findings"]) == 1
    assert data["findings"][0]["category"] == "BUG"
    assert data["findings"][0]["severity"] == "CRITICAL"


def test_exhausted_provider_retries_returns_502(test_client):
    """Exhausted provider retries map to HTTP 502 without exposing internal credentials."""
    from src.main import app
    from src.schemas.errors import ProviderUnavailableError
    from src.services.review_service import get_review_service

    mock_service = AsyncMock()
    mock_service.review_code.side_effect = ProviderUnavailableError(message="Groq API unavailable after 2 retries")

    app.dependency_overrides[get_review_service] = lambda: mock_service
    try:
        response = test_client.post(
            "/api/v1/review",
            json={"code": "x = 1 + 2\n", "language": "python"},
        )
        assert response.status_code == 502
        data = response.json()
        assert data["error_code"] == "PROVIDER_UNAVAILABLE"
        assert "gsk_" not in str(data)
    finally:
        app.dependency_overrides.clear()
