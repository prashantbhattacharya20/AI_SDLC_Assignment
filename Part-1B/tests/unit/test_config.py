"""Unit tests for application configuration settings (T005)."""

import pytest
from pydantic import ValidationError


def test_settings_default_values(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_api_key_1234567890abcdef")
    from src.config import Settings

    settings = Settings()
    assert settings.MODEL_ID == "openai/gpt-oss-120b"
    assert settings.APP_ENV in ["development", "staging", "production", "test"]
    assert settings.APP_PORT == 8000
    assert settings.MAX_PAYLOAD_LINES == 1000
    assert settings.MAX_PAYLOAD_BYTES == 65536
    assert settings.GROQ_MAX_RETRIES == 2
    assert settings.GROQ_BACKOFF_FACTOR == 1.0
    assert settings.PROMPT_VERSION == "v1.0.0"


def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_custom_key_xyz")
    monkeypatch.setenv("APP_PORT", "9000")
    monkeypatch.setenv("APP_ENV", "production")
    from src.config import Settings

    settings = Settings()
    assert settings.GROQ_API_KEY.get_secret_value() == "gsk_custom_key_xyz"
    assert settings.APP_PORT == 9000
    assert settings.APP_ENV == "production"


def test_settings_missing_groq_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    from src.config import Settings

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
