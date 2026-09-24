# Placeholders

Every external dependency is behind a clean interface with a working placeholder,
so `uvicorn` and `pytest` run on a clean machine with no credentials. Real
implementations must satisfy the same interface (Protocol) so swapping is a
config change plus filling in one class.

Conventions (PROMPT_FASTAPI_BACKEND.md §2):

- Each placeholder carries a greppable comment: `# PLACEHOLDER(<area>): ...`.
- Every placeholder response, evidence record and log line sets `source="placeholder"`
  (real sources set `source="tigergraph"`, `"ml_model"`, `"llm"`, etc.).
- Placeholder evidence is never presented as real evidence.

| # | Area | Placeholder file | Interface contract | Config switch | Real replacement must |
|---|------|------------------|--------------------|----------------|------------------------|
| 1 | Graph / TigerGraph | `app/integrations/tigergraph/placeholder.py` (`PlaceholderGraphClient`) | `GraphClient` Protocol in `app/integrations/tigergraph/graph_client.py`: `transaction_context`, `customer_profile`, `card_network`, `shared_device_investigation`, `related_transactions`, `fraud_proximity`, `similar_historical_cases`, `pattern_detection`, `graph_risk_signals`, `case_graph_write`. All methods take `as_of` and must not return data after it. | `GRAPH_BACKEND=placeholder\|mcp` | TigerGraph MCP client with the real GSQL queries, respecting `as_of` |
| 2 | TigerGraph MCP | `app/integrations/mcp/graph_client.py` (`McpGraphClient`) | Same `GraphClient` Protocol; currently raises `NotImplementedError("PLACEHOLDER...")` | `GRAPH_BACKEND=mcp` | Wire to TigerGraph MCP server |
| 3 | LLM | `app/integrations/llm/placeholder.py` (`PlaceholderLLMClient`) | `LLMClient` Protocol in `app/integrations/llm/client.py`: `generate(messages, response_schema=None) -> str`; deterministic templated text built only from evidence IDs passed in | `LLM_BACKEND=placeholder\|openai_compatible` | Real provider call (Gemini / OpenAI-compatible) at `app/integrations/llm/openai_compatible.py` |
| 4 | Vector store | `app/integrations/vector_store/in_memory.py` (`InMemoryVectorStore`) | `VectorStore` Protocol in `app/integrations/vector_store/client.py`: `upsert(doc_id, payload, embedding, as_of)`, `search(query, embedding, top_k, as_of)`. Keyword scoring only. Respects `as_of`. | `VECTOR_BACKEND=memory\|pgvector` | Neon pgvector at `app/integrations/vector_store/pgvector.py` |
| 5 | ML model artifact | `app/ml/model.py` (`RiskModel`) | `RiskModel.predict(features) -> {score, band, top_factors, model_version, calibrated, fallback_used}`, `RiskPredictor.assess(...) -> RiskAssessment` | `ML_MODEL_PATH` | Train a real scikit-learn model, save joblib artifact; wrapper loads it automatically |
| 6 | RAG knowledge documents | `app/services/fixtures/` | RAG service (`app/services/rag_service.py`) loads these synthetic documents | (none) | Real policy/pattern/regulatory docs + embeddings |
| 7 | Neon PostgreSQL | `app/db/session.py` | SQLAlchemy 2.x sync engine from `DATABASE_URL`; default local SQLite file; models Postgres-compatible | `DATABASE_URL` | Neon Postgres DSN + Alembic migrations |
| 8 | LangGraph checkpointer | `app/agent/graph.py` | In-memory saver by default | (config for Postgres saver) | LangGraph `AsyncPostgresSaver` for Neon |
| 9 | Benchmark case pack + dataset columns | `app/schemas/case.py` | Stable IDs + `attributes: dict[str, Any]` bag; no invented column meanings | (none) | Real `case_pack.csv` loader respecting column docs |

## Selecting placeholders vs real backends

Placeholders are the defaults. To use a real integration set the matching env var:

```bash
GRAPH_BACKEND=mcp          # wire TigerGraph MCP (implement McpGraphClient)
LLM_BACKEND=openai_compatible  # provide LLM_BASE_URL + LLM_API_KEY
VECTOR_BACKEND=pgvector        # provide VECTOR_STORE_URL
ML_MODEL_PATH=/path/to/model.joblib
```