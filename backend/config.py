"""
Application configuration via environment variables.
Uses pydantic-settings for validation and type coercion.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from pathlib import Path

# Always load from project root .env, regardless of CWD
_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    """All application settings, loaded from environment variables or .env file."""

    # --- Application ---
    APP_NAME: str = "Cold Outreach Pipeline"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./coldoutreach.db"
    DATABASE_URL_SYNC: str = "sqlite:///./coldoutreach.db"


    # --- API Keys ---
    OCEAN_IO_API_KEY: str = ""
    PROSPEO_API_KEY: str = ""
    EAZYREACH_API_KEY: str = ""
    BREVO_API_KEY: str = ""

    # --- API Base URLs ---
    OCEAN_IO_BASE_URL: str = "https://api.ocean.io/v1"
    PROSPEO_BASE_URL: str = "https://api.prospeo.io"
    EAZYREACH_BASE_URL: str = "https://api.eazyreach.app/v3"
    BREVO_BASE_URL: str = "https://api.brevo.com/v3"

    # --- Rate Limits (requests per minute) ---
    OCEAN_IO_RATE_LIMIT: int = 100
    PROSPEO_RATE_LIMIT: int = 10
    EAZYREACH_DAILY_QUOTA: int = 200
    BREVO_RATE_LIMIT: int = 100

    # --- Email Sending ---
    SENDER_EMAIL: str = "outreach@yourdomain.com"
    SENDER_NAME: str = "Outreach Team"

    # --- Pipeline Defaults ---
    OCEAN_IO_COMPANY_LIMIT: int = 50
    MIN_EMPLOYEE_COUNT: int = 50
    MAX_EMPLOYEE_COUNT: int = 5000
    EMAIL_CONFIDENCE_THRESHOLD: float = 0.7
    TARGET_JOB_TITLES: list = [
        "CEO", "CTO", "CFO", "COO", "CMO",
        "VP Engineering", "VP Sales", "VP Marketing",
        "VP Product", "VP Operations",
        "Chief Technology Officer", "Chief Executive Officer",
        "Chief Financial Officer", "Chief Operating Officer",
        "Chief Marketing Officer",
        "Head of Engineering", "Head of Sales",
        "Director of Engineering", "Director of Sales",
    ]
    EXCLUDED_TITLE_KEYWORDS: list = [
        "Junior", "Associate", "Coordinator",
        "Assistant", "Intern", "Trainee",
    ]

    # --- CORS ---
    CORS_ORIGINS: list = [
        "*"
    ]

    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once per process."""
    return Settings()
