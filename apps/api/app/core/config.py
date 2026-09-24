from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str

    TIGERGRAPH_HOST: str | None = None
    TIGERGRAPH_USERNAME: str | None = None
    TIGERGRAPH_PASSWORD: str | None = None
    TIGERGRAPH_GRAPHNAME: str | None = None

    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str | None = None
    GROK_API_KEY: str | None = None

    VECTOR_STORE_URL: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()