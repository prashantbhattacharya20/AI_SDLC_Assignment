from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Expense Management System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./expenses.db"
    DEFAULT_CURRENCY: str = "INR"
    MAX_EXPENSE_AMOUNT: float = 1_000_000.00
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
