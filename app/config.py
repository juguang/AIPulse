from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://aihot:aihot@db:5432/aihot"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    ENV: str = "development"

    # LLM API keys — from environment variables only
    # OPENAI_API_KEY and ANTHROPIC_API_KEY must be set in .env or environment
    # for the AI Pipeline to function. Missing keys cause silent fallback.
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Model selection
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20260514"
    SENTENCE_TRANSFORMERS_MODEL: str = "all-MiniLM-L6-v2"

    # LLM retry and pipeline settings
    MAX_RETRIES: int = 3
    AI_PIPELINE_BATCH_SIZE: int = 5
    AI_PIPELINE_POLL_INTERVAL: int = 60

    # Default crawler interval (minutes)
    # Per-source override available in source_configs table.
    CRAWL_INTERVAL_MINUTES: int = 30

    # APScheduler sync DSN; auto-derived from DATABASE_URL if empty
    # Uses postgresql:// (non-async) driver for SQLAlchemyJobStore.
    SCHEDULER_DATABASE_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
