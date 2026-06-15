from __future__ import annotations

import os
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Deep Agents"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"

    # LLM Providers
    openai_api_key: str = ""
    groq_api_key: str = ""
    anthropic_api_key: str = ""

    # Web search
    tavily_api_key: str = ""

    # Database
    database_url: str = "postgresql+psycopg://agentic:agentic@localhost:5432/agentic"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 72

    # Sentry
    sentry_dsn: str = ""

    # Rate limiting
    rate_limit_per_minute: int = 30
    rate_limit_per_day: int = 500

    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def default_model(self) -> str:
        return "openai:gpt-4o-mini"

    def validate_production(self) -> None:
        if self.app_env != "production":
            return
        errors = []
        if not self.jwt_secret or self.jwt_secret == "change-me":
            errors.append("JWT_SECRET must be set to a strong random value in production")
        if not self.openai_api_key and not self.groq_api_key and not self.anthropic_api_key:
            errors.append("At least one LLM API key (OPENAI_API_KEY, GROQ_API_KEY, ANTHROPIC_API_KEY) must be set in production")
        if self.sentry_dsn:
            try:
                import sentry_sdk
                sentry_sdk.init(
                    dsn=self.sentry_dsn,
                    environment=self.app_env,
                    traces_sample_rate=0.1,
                )
            except Exception:
                pass
        if errors:
            for err in errors:
                print(f"[CRITICAL] {err}", file=sys.stderr)
            sys.exit(1)


settings = Settings()

# Export to os.environ so libraries (langchain-openai, etc.) can find them
for key in ("openai_api_key", "groq_api_key", "anthropic_api_key", "tavily_api_key"):
    value = getattr(settings, key, "")
    if value:
        os.environ.setdefault(key.upper(), value)
