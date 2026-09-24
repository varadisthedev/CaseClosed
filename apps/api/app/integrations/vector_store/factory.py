from app.core.config import Settings, get_settings
from app.integrations.vector_store.in_memory import InMemoryVectorStore
from app.integrations.vector_store.pgvector import PgVectorStore


def get_vector_store(
    settings: Settings | None = None,
) -> InMemoryVectorStore | PgVectorStore:
    """Select the vector store by config.

    # PLACEHOLDER(integration-selection): switch VECTOR_BACKEND=memory|pgvector
    """
    settings = settings or get_settings()
    if settings.VECTOR_BACKEND == "pgvector":
        return PgVectorStore(dsn=settings.VECTOR_STORE_URL)
    return InMemoryVectorStore()