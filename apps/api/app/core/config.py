from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Defaults are chosen so the API and the test suite run on a clean machine
    with no external services and no credentials.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- App ---
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "CaseClosed API"
    APP_VERSION: str = "0.1.0"

    # --- Database ---
    # Portable default: SQLite file so dev/tests need no Postgres/Neon.
    # Production / Docker overrides this with a postgresql+psycopg:// URL.
    DATABASE_URL: str = "sqlite:///./caseclosed_dev.sqlite"
    SQL_ECHO: bool = False

    # --- Backend selection (placeholders are the defaults) ---
    # PLACEHOLDER(integration-selection): config switch for each external system
    USE_PLACEHOLDERS: bool = True
    GRAPH_BACKEND: str = "placeholder"  # placeholder | mcp
    LLM_BACKEND: str = "placeholder"  # placeholder | openai_compatible
    VECTOR_BACKEND: str = "memory"  # memory | pgvector

    # --- ML ---
    # PLACEHOLDER(ml-model): path to a joblib artifact; absent -> deterministic stub
    ML_MODEL_PATH: str = "app/ml/artifacts/model.joblib"

    # --- TigerGraph / MCP (real integration, not required) ---
    TIGERGRAPH_HOST: str | None = None
    TIGERGRAPH_USERNAME: str | None = None
    TIGERGRAPH_PASSWORD: str | None = None
    TIGERGRAPH_GRAPHNAME: str | None = None
    MCP_SERVER_URL: str | None = None

    # --- LLM (real provider, not required) ---
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_BASE_URL: str | None = None
    LLM_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    GROK_API_KEY: str | None = None

    # --- Vector store ---
    VECTOR_STORE_URL: str | None = None

    # --- Security ---
    # Empty key disables the API-key check (development default).
    API_KEY: str | None = None

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000"

    # --- Agent / policy ---
    POLICY_VERSION: str = "1.0"
    AGENT_MAX_EVIDENCE_LOOPS: int = 2

    # --- Paths ---
    CASE_PACK_PATH: str | None = None
    RAG_FIXTURES_DIR: str = "app/services/fixtures"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()