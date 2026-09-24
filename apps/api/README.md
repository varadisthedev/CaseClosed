# CaseClosed FastAPI Backend

## Overview
CaseClosed is an agentic fraud-investigation system backend built with FastAPI. It provides a comprehensive framework for fraud investigation including policy engines, risk assessment, graph analysis, and evidence tracking.

## Architecture
The backend follows a layered architecture as specified in AGENTS.md and PROMPT_FASTAPI_BACKEND.md:

- **Routes**: HTTP endpoints for case management, investigation, risk assessment, and actions
- **Services**: Business logic and orchestration
- **Integrations**: Placeholder-first implementations for TigerGraph, LLM, vector store
- **ML**: Risk assessment models with deterministic stub fallbacks
- **Repositories**: Database persistence layer
- **Core**: Configuration, logging, security, and shared utilities

## Key Features
- Deterministic policy engine with versioned rules
- Idempotent mock actions with approval flow
- Risk assessment without LLM calls
- Graph evidence retrieval and similar case lookup
- Grounded context building for LLM explanation
- Evidence provenance and leak prevention (`as_of` guards)
- Placeholder-first approach for all external dependencies

## Running the API
```bash
cd apps/api
uvicorn app.main:app --reload
```

## Test Suite
All 36 tests pass:
- Evidence service tests (5 tests)
- Health checks (4 tests)
- Integration tests (8 tests)
- Policy service tests (8 tests)
- Repository tests (4 tests)
- Schema tests (6 tests)

## Placeholders
All external dependencies use placeholder implementations by default, configured via `GRAPH_BACKEND`, `LLM_BACKEND`, `VECTOR_BACKEND`, and `ML_MODEL_PATH` environment variables. Real implementations must satisfy the same Protocol interfaces.

## References
- `AGENTS.md` at repo root: source of truth for architecture rules
- `PROMPT_FASTAPI_BACKEND.md`: task specification and phase guide
- `.opencode/PROGRESS.md`: phase tracker
- `apps/api/PLACEHOLDERS.md`: placeholder handoff table
