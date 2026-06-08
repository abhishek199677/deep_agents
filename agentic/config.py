from __future__ import annotations

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
        if self.openai_api_key:
            return "openai:gpt-4.1"
        if self.groq_api_key:
            return "groq:qwen/qwen3-32b"
        return "openai:gpt-4.1"


settings = Settings()
