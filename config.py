from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API
    APP_NAME: str = "Test Data Generator API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour

    # Output
    MAX_GENERATION_COUNT: int = 10000
    DEFAULT_LOCALE: str = "en_US"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_prefix = "TDG_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
