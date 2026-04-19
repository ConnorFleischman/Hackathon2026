"""Application settings loaded from environment."""

from functools import lru_cache
from typing import Any, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration; keep secrets out of code — use .env / injected env vars."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = Field(default="development", description="e.g. development, staging, production")

    DATABASE_URL: str = Field(
        default="",
        description="SQLAlchemy URL for PostgreSQL (required only when using the database)",
    )
    REDIS_URL: str = Field(default="", description="Redis connection URL")

    JWT_SECRET: str = Field(default="", description="Signing secret for access tokens")
    JWT_REFRESH_SECRET: str = Field(default="", description="Signing secret for refresh tokens")

    EMAIL_PROVIDER_KEY: str = Field(default="", description="API key for transactional email provider")
    MODERATION_PROVIDER_KEY: str = Field(
        default="",
        description="API key for moderation/abuse provider",
    )

    CORS_ALLOWED_ORIGINS: str = Field(
        default="",
        description='Comma-separated origins, e.g. "http://localhost:3000,https://app.example.com"',
    )

    @field_validator(
        "DATABASE_URL",
        "REDIS_URL",
        "JWT_SECRET",
        "JWT_REFRESH_SECRET",
        "EMAIL_PROVIDER_KEY",
        "MODERATION_PROVIDER_KEY",
        "CORS_ALLOWED_ORIGINS",
        mode="before",
    )
    @classmethod
    def strip_optional_strings(cls, v: Any) -> str:
        if v is None:
            return ""
        if isinstance(v, str):
            return v.strip()
        raise ValueError("Expected string or empty value")

    @property
    def cors_origins(self) -> list[str]:
        if not self.CORS_ALLOWED_ORIGINS:
            return []
        return [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    @model_validator(mode="after")
    def enforce_production_secrets(self) -> Self:
        if self.is_production:
            if not self.JWT_SECRET:
                raise ValueError("JWT_SECRET is required when APP_ENV is production")
            if not self.JWT_REFRESH_SECRET:
                raise ValueError("JWT_REFRESH_SECRET is required when APP_ENV is production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
