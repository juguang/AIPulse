from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./aipulse.db"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    ENV: str = "development"

    # DeepSeek API
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-v4-flash"

    # LLM retry and pipeline settings
    MAX_RETRIES: int = 3
    AI_PIPELINE_BATCH_SIZE: int = 5
    AI_PIPELINE_POLL_INTERVAL: int = 60

    # Default crawler interval (minutes)
    CRAWL_INTERVAL_MINUTES: int = 30
    CRAWL_MAX_AGE_DAYS: int = 3

    # AI pipeline interval (minutes); defaults to half of CRAWL_INTERVAL_MINUTES
    AI_PIPELINE_INTERVAL_MINUTES: int = 0  # 0 means auto-derive

    # APScheduler sync DSN; auto-derived from DATABASE_URL if empty
    SCHEDULER_DATABASE_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
