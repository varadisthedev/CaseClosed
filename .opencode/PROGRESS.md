# CaseClosed FastAPI Backend — Progress

Source of truth: `AGENTS.md`. Task spec: `PROMPT_FASTAPI_BACKEND.md`.

## Decisions log
See `apps/api/docs/DECISIONS.md`.

## Phases

- [x] 1. Scaffold `apps/api/` structure, `requirements.txt`, config, logging, app factory, `/health`, test harness
- [x] 2. Schemas (case, evidence, risk, action) and DB models, session, repositories
- [x] 3. Integration Protocols plus placeholder implementations (graph, MCP skeleton, LLM, vector store) and ML wrapper with stub fallback
- [x] 4. Evidence service, `as_of` helpers with leak guards + tests
- [x] 5. Policy engine with versioned rules and audit logging
- [x] 6. Mock actions with idempotency, approval flow
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
- Phase 3 done: `GraphClient` Protocol `as_of`-aware (10 capabilities) + `PlaceholderGraphClient` (deterministic fixtures, `source="placeholder"`) + `McpGraphClient` skeleton raising `NotImplementedError`; `LLMClient` Protocol + `PlaceholderLLMClient` (templates only cited evidence IDs) + `OpenAiCompatibleClient` skeleton; `VectorStore` Protocol + `InMemoryVectorStore` (keyword, `as_of` filter) + `PgVectorStore` skeleton; `RiskModel` joblib load w/ deterministic hash stub (`calibrated=false`, no claim of calibration) + `RiskPredictor`; config factories `get_graph_client/get_llm_client/get_vector_store`; wrote `apps/api/PLACEHOLDERS.md`.
- Phase 4 done: Evidence service with provenance tracking, `as_of` helpers with leak guards (`guard_record`, `filter_after`, `epoch_utc`), tests covering future-data rejection and evidence ID validation.
- Phase 5 done: Policy engine with versioned rules (`POLICY_VERSION="1.0"`), 6 default rules (R-1..R-6) seeded in DB, deterministic rule matching (`_rule_applies`) supporting conditions for fraud_probability, verdict, pattern (any/eq/none), exposure, risk_score, evidence_count. State machine: RECOMMENDED -> HUMAN_APPROVAL_REQUIRED -> AUTHORIZED -> EXECUTABLE. Approval routes L1/L2/AUTO with priority resolution. Audit logging of decisions via `AuditEvent`. 8 tests passing.
- Phase 6 done: Mock actions with idempotency and approval flow. Actions: block_card, step_up_authentication, contact_customer, file_sar, create_case. Each action uses idempotency key for deterministic repeatable results, persisted in ActionExecution. Actions EXECUTABLE only after policy approval. Approval recorded via policy_service.request_approval(). New functions: _generate_execution_id, _generate_idempotency_key, _now_utc.
- Phase 7 in progress: Risk service, RAG service with fixtures, investigation service. Risk service provides deterministic risk assessment without LLM calls. RAG service provides entity resolution, graph evidence retrieval, similar case lookup, and grounded context building for LLM explanation with provenance preservation and evidence ID validation. Investigation service coordinates the full workflow: policy evaluation, risk assessment, evidence retrieval, similar case lookup, and context building.
- Phase 6 in progress: Mock actions (block card, step-up authentication, contact customer, file SAR, create case) with idempotency keys, persisted results, and approval flow. Actions can only execute when policy state is EXECUTABLE. Approval must be recorded before execution when required.