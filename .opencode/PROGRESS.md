# CaseClosed FastAPI Backend — Progress

Source of truth: `AGENTS.md`. Task spec: `PROMPT_FASTAPI_BACKEND.md`.

## Decisions log
See `apps/api/docs/DECISIONS.md`.

## Phases

- [x] 1. Scaffold `apps/api/` structure, `requirements.txt`, config, logging, app factory, `/health`, test harness
- [x] 2. Schemas (case, evidence, risk, action) and DB models, session, repositories
- [ ] 3. Integration Protocols plus placeholder implementations (graph, MCP skeleton, LLM, vector store) and ML wrapper with stub fallback
- [ ] 4. Evidence service, `as_of` helper, provenance rules
- [ ] 5. Policy engine with versioned rules and audit logging
- [ ] 6. Mock actions with idempotency, approval flow
- [ ] 7. Risk service, RAG service with fixtures, investigation service
- [ ] 8. LangGraph agent (nodes, state, prompts, loop limit) running end to end on placeholders
- [ ] 9. All routes wired, error handling, CORS, optional API-key check
- [ ] 10. Full test suite green, end-to-end smoke flow, `README.md`, `PLACEHOLDERS.md`, `.env.example`
- [ ] 11. Final review against AGENTS.md sections 12, 13, 16 to 21 and 24 to 26; fix any deviation

## Notes
- Pre-existing (committed earlier): layered dir scaffold, async SQLAlchemy models + Alembic (Postgres), docker setup, case-pack seed.
- This task: portable SQLAlchemy (SQLite default for dev/tests), sync sessions, all services/integrations/agent/routes/tests.
- Phase 1 done: config (placeholders + SQLite default + backend switches), request-context logging, error hierarchy (`AppError`/404/409/422/401), `security.py` API-key gate, sync portable `db/session.py` (+`init_db`), portable models (JSON + non-native Enum, new `audit_events`, evidence provenance fields), app factory with request-id middleware + error handlers + CORS, `conftest.py` + `test_health.py` (4 passing).
- Known gap: route handlers still stubs (wired in Phase 9). Models changed vs committed Postgres-native versions; a portable Alembic migration will be regenerated later (Phase 10/11).
- Phase 2 done: Pydantic schemas (case w/ `attributes` bag, evidence w/ provenance fields, risk w/ `calibrated` flag, action/policy, investigation result), repositories (case/evidence/action/run) with autoflush-enabled sync session. Note: switched sessionmaker to `autoflush=True` so `get_by_id` sees pending rows before commit.