from datetime import datetime
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class VectorStore(Protocol):
    """Contract for embedding-backed retrieval (Neon pgvector / in-memory)."""

    def upsert(
        self,
        doc_id: str,
        payload: dict[str, Any],
        embedding: list[float] | None = None,
        as_of: datetime | None = None,
    ) -> None: ...

    def search(
        self,
        query: str,
        embedding: list[float] | None = None,
        top_k: int = 5,
        as_of: datetime | None = None,
    ) -> list[dict[str, Any]]: ...