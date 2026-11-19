"""Application configuration settings for AI Code Review Assistant."""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=(str(ENV_PATH), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Groq API Configuration
    GROQ_API_KEY: SecretStr = Field(
        ...,
        description="Groq Cloud API key (required, masked in logs)",
    )
    MODEL_ID: str = Field(
        default="openai/gpt-oss-120b",
        description="Configured Groq model identifier",
    )
    GROQ_MAX_RETRIES: int = Field(
        default=2,
        description="Maximum retry attempts after initial request",
    )
    GROQ_BACKOFF_FACTOR: float = Field(
        default=1.0,
        description="Base backoff multiplier in seconds (approx 1s, 2s)",
    )

    # Application Configuration
    APP_ENV: str = Field(
        default="development",
        description="Application environment: development, staging, production, test",
    )
    APP_HOST: str = Field(
        default="127.0.0.1",
        description="Server host bind address",
    )
    APP_PORT: int = Field(
        default=8000,
        description="Server port bind address",
    )

    # Payload & Rate Guardrails
    MAX_PAYLOAD_LINES: int = Field(
        default=1000,
        description="Maximum lines of code per review submission",
    )
    MAX_PAYLOAD_BYTES: int = Field(
        default=65536,
        description="Maximum UTF-8 payload size in bytes (64 KB)",
    )

    # Prompt Configuration
    PROMPT_VERSION: str = Field(
        default="v1.0.0",
        description="Active version of system review prompt",
    )


# Global settings singleton
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the cached settings singleton or instantiate a new one."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
