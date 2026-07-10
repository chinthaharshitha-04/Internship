"""
Application configuration.

Uses ``pydantic-settings`` so configuration values can be supplied via
environment variables or a ``.env`` file, falling back to sensible
defaults for local development.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings.

    Attributes:
        app_name: Human-readable name of the service.
        api_v1_prefix: URL prefix under which all API routes are mounted.
        database_url: SQLAlchemy connection string.
        debug: Toggles verbose logging / SQL echo.
    """

    app_name: str = "Retail Discount Engine"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./retail_discount_engine.db"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance.

    ``lru_cache`` ensures the environment is only parsed once per
    process, which is both a performance optimization and a way to
    guarantee a single consistent settings object is shared across the
    application (a lightweight singleton via dependency injection).
    """

    return Settings()
