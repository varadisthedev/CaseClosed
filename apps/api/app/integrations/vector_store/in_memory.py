from datetime import datetime
from typing import Any

from app.core.context import get_case_id


class InMemoryVectorStore:
    """Trivial keyword-scoring in-memory vector store.

    # PLACEHOLDER(vector-store): replaced by Neon pgvector once embeddings are
    # available. Keyword scoring only; do not present results as semantic.
    """

    source = "placeholder"

    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}

    def upsert(
        self,
        doc_id: str,
        payload: dict[str, Any],
        embedding: list[float] | None = None,
        as_of: datetime | None = None,
    ) -> None:
        record = {
            "doc_id": doc_id,
            "payload": payload,
            "embedding": embedding,
            "as_of": as_of,
        }
        self._records[doc_id] = record

    def search(
        self,
        query: str,
        embedding: list[float] | None = None,
        top_k: int = 5,
        as_of: datetime | None = None,
    ) -> list[dict[str, Any]]:
        q = query.lower().split()
        scored: list[tuple[float, dict[str, Any]]] = []
        for doc_id, record in self._records.items():
            # temporal filter: exclude docs observed after as_of
            rec_time = record.get("as_of")
            if as_of is not None and rec_time is not None and rec_time > as_of:
                continue
            text = _text_of(record["payload"])
            score = sum(1 for term in q if term in text)
            if score == 0:
                continue
            scored.append(
                (
                    score,
                    {
                        "doc_id": doc_id,
                        "score": score,
                        "payload": record["payload"],
                        "source": self.source,
                        "case_id": get_case_id(),
                    },
                )
            )
        scored.sort(key=lambda t: t[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    def clear(self) -> None:
        self._records.clear()

    def __len__(self) -> int:
        return len(self._records)


def _text_of(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, value in payload.items():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, (int, float)):
            parts.append(str(value))
        elif isinstance(value, list):
            parts.extend(str(v) for v in value)
    return " ".join(parts).lower()