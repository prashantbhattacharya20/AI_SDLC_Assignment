"""Integration tests for FastAPI application initialization, CORS, and route mounting (T009)."""

from fastapi.testclient import TestClient


def test_fastapi_app_initialization(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_api_key_1234567890abcdef")
    from src.main import app

    client = TestClient(app)

    # Verify OpenAPI documentation is served
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert schema["info"]["title"] == "AI Code Review Assistant"
    assert "/api/v1/review" in schema["paths"]
    assert "/api/v1/health" in schema["paths"]


def test_cors_headers(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_api_key_1234567890abcdef")
    from src.main import app

    client = TestClient(app)
    resp = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code in [200, 204]
    assert "access-control-allow-origin" in resp.headers


def test_health_endpoint_integration(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_api_key_1234567890abcdef")
    from src.main import app

    client = TestClient(app)
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
