"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Settings consumed by the running API and its tests."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = Field(default="development", description="Application environment name")
    APP_NAME: str = Field(default="Campus Social API", description="Service name used in metadata and logs")
    LOG_LEVEL: str = Field(default="INFO", description="Root logger level")
    LOG_JSON: bool = Field(default=False, description="Emit structured JSON logs")
    DATABASE_URL: str = Field(default="", description="SQLAlchemy database URL")
    JWT_SECRET: str = Field(default="", description="Signing secret for access tokens")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_ACCESS_EXPIRE_MINUTES: int = Field(default=30, ge=1, description="Access token lifetime in minutes")
    CORS_ALLOWED_ORIGINS: str = Field(
        default="",
        description='Comma-separated origin list such as "http://localhost:3000"',
    )

    @field_validator(
        "APP_ENV",
        "APP_NAME",
        "LOG_LEVEL",
        "DATABASE_URL",
        "JWT_SECRET",
        "JWT_ALGORITHM",
        "CORS_ALLOWED_ORIGINS",
        mode="before",
    )
    @classmethod
    def strip_optional_strings(cls, value: Any) -> Any:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        return value

    @property
    def cors_origins(self) -> list[str]:
        """Return normalized CORS origins suitable for FastAPI middleware."""
        if not self.CORS_ALLOWED_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """True when the process is running in the production environment."""
        return self.APP_ENV.lower() == "production"

    @model_validator(mode="after")
    def validate_production_settings(self) -> Self:
        """Require the access-token secret outside local development."""
        if self.is_production and not self.JWT_SECRET:
            raise ValueError("JWT_SECRET is required when APP_ENV is production")
        return self


@lru_cache
def get_settings() -> Settings:
    """Cache settings so each process reads configuration once."""
    return Settings()


settings = get_settings()
