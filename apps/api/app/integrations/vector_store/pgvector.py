from datetime import datetime
from typing import Any


class PgVectorStore:
    """Skeleton for the Neon PostgreSQL + pgvector store.

    # PLACEHOLDER(vector-store-pgvector): replace with a real pgvector-backed
    # implementation (upsert embeddings, execute nearest-neighbour search) once
    # embeddings exist. Neon PostgreSQL is the target (AGENTS.md section 10).
    """

    source = "pgvector"

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn

    def upsert(
        self,
        doc_id: str,
        payload: dict[str, Any],
        embedding: list[float] | None = None,
        as_of: datetime | None = None,
    ) -> None:
        raise NotImplementedError(
            "PLACEHOLDER(vector-store-pgvector): pgvector store not wired yet"
        )

    def search(
        self,
        query: str,
        embedding: list[float] | None = None,
        top_k: int = 5,
        as_of: datetime | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError(
            "PLACEHOLDER(vector-store-pgvector): pgvector store not wired yet"
        )