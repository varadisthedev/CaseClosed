# CaseClosed Backend — Decisions

Records choices made autonomously while following `PROMPT_FASTAPI_BACKEND.md`.
Format: decision, rationale, date, phase.

## D-001: Sync SQLAlchemy with SQLite default

**Decision.** Use synchronous SQLAlchemy (`psycopg` for Postgres, SQLite by default)
instead of the pre-existing async (`asyncpg`) setup.

**Rationale.** `PROMPT_FASTAPI_BACKEND.md` section 4 explicitly permits sync and lists
`psycopg[binary]` (a sync driver) in the required dependency set. Section 2 requires
`pytest`/`uvicorn` to work on a clean machine with no external services, so the default
`DATABASE_URL` is a local SQLite file. Sync keeps the service, policy and agent code
free of `await` noise and is ample for a hackathon backend.

**Consequence.** Models use portable SQLAlchemy types (`JSON` instead of `JSONB`,
`Enum(native_enum=False)` instead of native PG enums) so the same schema runs on both
SQLite and PostgreSQL. Docker/Alembic URLs switch from `postgresql+asyncpg://` to
`postgresql+psycopg://`.

## D-002: Placeholder-first integration layer

**Decision.** Every external dependency (TigerGraph/MCP, LLM, vector store, ML artifact)
is defined as a `Protocol` with a deterministic placeholder implementation selected by
config (`*_BACKEND`), defaulting to placeholders.

**Rationale.** Mandated by `PROMPT_FASTAPI_BACKEND.md` section 2. Enables end-to-end
tests and a working agent before real integrations exist.

## D-003: API-key auth disabled when unset

**Decision.** `security.py` enforces an `X-API-Key` header only when `API_KEY` is
configured; otherwise requests pass through.

**Rationale.** Keeps local/demo usage frictionless while allowing a minimal gate in
deployed environments.