# AGENTS.md

# CaseClosed — Shared Project Context

This file is the common source of truth for every team member and AI coding agent working on CaseClosed.
Read this before making architectural, data, API, or infrastructure changes.

## 1. Project

**Project:** CaseClosed

**Hackathon:** TigerGraph Agentic Fraud Investigation Hackathon (HHGOA)

CaseClosed is an agentic fraud-investigation system. It uses TigerGraph for relationship-based investigation, an ML model for risk assessment, GraphRAG for grounded evidence, deterministic policy rules for action authorization, LangGraph for agent orchestration, and a Next.js analyst UI.

The goal is not simply to predict fraud. The system should investigate a case, collect and explain evidence, assess uncertainty, recommend a next-best action, apply policy/approval rules, execute a simulated action where permitted, and record the result.

## 2. Core Architecture Decision

Use a **monorepo**.

Keep the frontend and Python backend in the same repository, while keeping their responsibilities clearly separated.

Use a **layered architecture inside the Python backend** rather than splitting the backend into many microservices.

This is the preferred architecture for the hackathon because it gives the team:

- one repository and one shared project context
- simple local development
- clean separation of responsibilities
- easy deployment
- fewer networking/configuration problems
- enough modularity without unnecessary microservices

Do NOT create separate services for every component unless a real deployment or scaling requirement appears.

## 3. High-Level System

The major system flow is:

Dataset
→ Google Drive
→ Google Colab preprocessing
→ processed CSVs + ML Parquet
→ ML model
→ TigerGraph graph
→ GSQL/graph algorithms
→ TigerGraph MCP
→ FastAPI backend
→ GraphRAG + Policy Engine + Mock Actions + Neon PostgreSQL
→ LangGraph + LLM
→ Next.js analyst UI
→ 20-case evaluation

The important architectural distinction is:

**Next.js = presentation**

**FastAPI = application/control layer**

**LangGraph = agent orchestration**

**TigerGraph = graph investigation/evidence**

**ML = risk signal**

**GraphRAG = grounded retrieval**

**Policy Engine = deterministic authorization**

**Neon PostgreSQL = application state**

**LLM = reasoning/synthesis/explanation**

## 4. Dataset

The hackathon dataset is already provided.

Known files:

- `transactions.csv`
  - 590,742 rows
  - 397 columns
- `identity.csv`
  - 144,432 rows
  - 41 columns
- `closed_cases_history.csv`
  - 5,565 historical cases
- `case_pack.csv`
  - 20 benchmark cases

The benchmark cases are used to evaluate the completed agent.

Do not invent meanings for anonymous columns or relationships. Verify the dataset documentation/README before making dataset-specific assumptions.

## 5. Data Storage and Preprocessing

Use **Google Drive + Google Colab** for the data-preparation workflow.

Google Drive stores:

- original/raw dataset files
- processed CSVs
- ML Parquet files
- preprocessing outputs

Google Colab performs:

- data profiling
- cleaning
- normalization
- entity resolution
- relationship extraction
- feature engineering
- ML training/validation

Preferred preprocessing stack:

- Python
- Pandas
- optionally Polars if useful
- PyArrow/Parquet

**DuckDB is optional, not required.**

Do not introduce DuckDB unless it solves an actual performance or analytical-query problem.

## 6. Data Pipeline Outputs

The preprocessing pipeline produces two primary outputs.

### TigerGraph CSVs

Create clean CSVs representing graph vertices and edges.

Conceptual vertices may include:

- Customer
- Card
- Transaction
- Device
- FraudCase
- FraudPattern
- Policy
- Evidence
- Document/DocChunk where required

Conceptual edges may include:

- Customer → Card
- Card → Transaction
- Customer → Transaction
- Transaction → Device
- Customer → Device
- FraudCase → Customer
- FraudCase → Card
- FraudCase → Transaction
- FraudCase → FraudPattern
- FraudCase → similar historical cases where applicable

Exact fields and relationships must come from the real dataset.

### ML Parquet

Create a Parquet feature dataset for model training.

Possible features:

- transaction attributes
- bank risk score
- transaction velocity
- device/network signals
- graph-derived features
- historical case signals
- pattern-related features

Do not remove useful raw features simply because they are not used in TigerGraph.

## 7. TigerGraph

TigerGraph is the primary fraud relationship and graph-investigation layer.

Responsibilities:

- store fraud entities and relationships
- perform graph traversals
- detect suspicious relationship patterns
- investigate shared infrastructure
- find related transactions
- find historical/similar cases
- calculate graph-derived signals
- support investigation queries

Use GSQL and appropriate graph algorithms.

Core principle:

**TigerGraph = relationship analysis + investigation evidence.**

TigerGraph is not responsible for LLM reasoning or final action authorization.

## 8. TigerGraph MCP

TigerGraph MCP is the controlled bridge between the application/agent and TigerGraph.

Expose well-defined investigation capabilities such as:

- transaction context
- customer profile
- card network
- shared-device investigation
- related transactions
- fraud proximity
- historical/similar cases
- pattern detection
- graph risk signals
- case graph writes

Do not give the LLM unrestricted database access.

MCP integration belongs in the backend infrastructure/integration layer.

## 9. ML Risk Model

Use an interpretable model initially with **scikit-learn**.

Train it using the processed Parquet dataset and appropriate historical closed-case information.

Potential features:

- transaction attributes
- bank risk score
- velocity
- device signals
- graph-derived signals
- historical case signals
- pattern signals

The model produces a risk assessment used as one investigation signal.

The ML model must NOT directly authorize or execute an action.

Do not describe an output as a perfectly calibrated fraud probability unless calibration has actually been demonstrated.

## 10. GraphRAG

GraphRAG combines graph evidence with relevant textual knowledge.

Potential sources:

- fraud policies
- documented fraud patterns
- regulatory references
- historical analyst notes
- historical case summaries
- approved project documents

Expected process:

1. Resolve case/entities.
2. Retrieve bounded graph evidence.
3. Retrieve relevant documents/historical cases.
4. Preserve provenance.
5. Build grounded context.
6. Give the context to the LLM.
7. Generate an evidence-based explanation.

The LLM must not invent evidence.

For vector storage, prefer the simplest working implementation. **Neon PostgreSQL + pgvector** may be used if TigerGraph vector functionality is inconvenient.

## 11. Neon PostgreSQL

Use **Neon PostgreSQL** for application state.

TigerGraph and PostgreSQL have different responsibilities.

### TigerGraph

Stores:

- graph entities
- relationships
- graph investigation information
- graph-derived evidence

### Neon PostgreSQL

Stores:

- active cases
- evidence records
- investigation results
- LangGraph checkpoints/state where appropriate
- approvals
- mock action results
- audit/history
- case summaries
- vector embeddings if pgvector is used

PostgreSQL is not a replacement for TigerGraph.

## 12. FastAPI Backend

FastAPI is the main application/control layer.

It integrates:

- TigerGraph MCP
- ML model
- GraphRAG
- Policy Engine
- Mock Actions
- Neon PostgreSQL
- LangGraph
- LLM provider

FastAPI handles:

- API validation
- authentication/authorization as required
- orchestration boundaries
- persistence
- controlled tool execution
- frontend APIs
- agent-facing tools

Suggested conceptual endpoints:

- `POST /api/cases`
- `GET /api/cases/{case_id}`
- `POST /api/cases/{case_id}/investigate`
- `GET /api/cases/{case_id}/evidence`
- `GET /api/cases/{case_id}/graph`
- `GET /api/cases/{case_id}/risk`
- `GET /api/cases/{case_id}/patterns`
- `GET /api/cases/{case_id}/similar-cases`
- `GET /api/cases/{case_id}/next-action`
- `POST /api/cases/{case_id}/evidence/request`
- `POST /api/cases/{case_id}/actions/approve`
- `POST /api/cases/{case_id}/actions/execute`

Exact endpoints may evolve.

## 13. FastAPI Layered Architecture

Use a layered architecture inside the Python backend.

Recommended structure:

```text
apps/api/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── cases.py
│   │   │   ├── investigation.py
│   │   │   ├── risk.py
│   │   │   ├── actions.py
│   │   │   └── agent.py
│   │   └── dependencies.py
│   │
│   ├── schemas/
│   │   ├── case.py
│   │   ├── evidence.py
│   │   ├── risk.py
│   │   └── action.py
│   │
│   ├── services/
│   │   ├── investigation_service.py
│   │   ├── risk_service.py
│   │   ├── evidence_service.py
│   │   ├── rag_service.py
│   │   ├── policy_service.py
│   │   └── action_service.py
│   │
│   ├── agent/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes/
│   │   └── prompts/
│   │
│   ├── integrations/
│   │   ├── tigergraph/
│   │   ├── mcp/
│   │   ├── llm/
│   │   └── vector_store/
│   │
│   ├── repositories/
│   │   ├── case_repository.py
│   │   ├── evidence_repository.py
│   │   └── action_repository.py
│   │
│   ├── db/
│   │   ├── session.py
│   │   └── models/
│   │
│   ├── ml/
│   │   ├── model.py
│   │   ├── predictor.py
│   │   └── artifacts/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   │
│   └── tests/
│
└── requirements.txt
```

### Layer responsibilities

**Routes**
- HTTP only.
- Validate requests.
- Call services.
- Return responses.
- Do not contain business logic.

**Schemas**
- Pydantic request/response models.

**Services**
- Business logic and orchestration.
- Coordinate repositories and integrations.

**Repositories**
- Database persistence.
- No business decisions.

**Integrations**
- External systems such as TigerGraph, MCP, LLM and vector storage.

**Agent**
- LangGraph state and workflow.
- Uses service/integration tools.
- Does not directly access database internals.

**ML**
- Model loading and prediction.
- No direct action execution.

**Core**
- configuration, logging, security and shared infrastructure.

This is a logical layering, not a requirement to create a class for every function.

## 14. Monorepo Architecture

Use a monorepo with two main applications.

Recommended structure:

```text
CaseClosed/
│
├── apps/
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── hooks/
│   │   └── ...
│   │
│   └── api/
│       ├── app/
│       ├── tests/
│       └── requirements.txt
│
├── data/
│   ├── README.md
│   └── .gitkeep
│
├── preprocessing/
│   ├── notebooks/
│   ├── scripts/
│   └── README.md
│
├── graph/
│   ├── schema/
│   ├── loaders/
│   ├── queries/
│   └── README.md
│
├── ml/
│   ├── training/
│   ├── evaluation/
│   └── README.md
│
├── evaluation/
│   ├── benchmark/
│   └── README.md
│
├── docs/
│   ├── architecture/
│   ├── api/
│   └── decisions/
│
├── .env.example
├── .gitignore
├── README.md
└── AGENTS.md
```

The exact directory structure can evolve, but responsibilities must remain clear.

## 15. Frontend

Use:

- Next.js
- TypeScript
- Tailwind CSS
- graph visualization library as required

The frontend is an **analyst dashboard**, not a customer application.

Important UI information:

- Case ID
- transaction details
- risk assessment
- evidence confidence
- investigation evidence
- graph/network visualization
- similar historical cases
- detected patterns
- missing evidence
- contradictions
- next-best action
- approval requirement
- action result
- investigation timeline

The UI should make the investigation explainable rather than simply display a score.

## 16. LangGraph Agent

LangGraph is the orchestration layer inside the Python backend.

It manages investigation state and workflow.

Conceptual workflow:

1. Case intake
2. Investigation planning
3. Graph investigation
4. Evidence compilation
5. GraphRAG/document retrieval
6. ML risk assessment
7. Pattern/policy evaluation
8. Evidence sufficiency/uncertainty assessment
9. Request additional evidence if needed
10. Generate next-best action
11. Policy/approval check
12. Execute approved action
13. Update case
14. Explain findings
15. Persist investigation state

The agent should be a controlled workflow, not an unrestricted autonomous system.

## 17. LLM Responsibilities

The LLM is responsible for:

- reasoning over retrieved evidence
- selecting available investigation tools
- generating hypotheses
- synthesizing evidence
- identifying contradictions
- explaining findings
- proposing next-best actions
- communicating results

The LLM is NOT responsible for:

- unrestricted database queries
- bypassing policy
- deciding authorization alone
- inventing evidence
- replacing graph algorithms
- replacing the ML model
- executing unrestricted actions

## 18. Policy Engine

Policy decisions must be deterministic.

The LLM can propose an action, but the Policy Engine determines:

- whether the action is allowed
- whether approval is required
- which approval route applies
- whether the action can execute

Conceptual states:

- RECOMMENDED
- HUMAN_APPROVAL_REQUIRED
- AUTHORIZED
- EXECUTABLE

Example actions:

- block card
- step-up authentication
- contact customer
- file SAR
- close case

Policy rules should be versioned and auditable.

## 19. Mock Actions

The hackathon does not require real banking actions.

Implement simulated APIs for:

- block card
- step-up authentication
- contact customer
- create/update case
- SAR filing

Mock actions should be idempotent where practical and return a clear result that is persisted in Neon PostgreSQL.

## 20. Evidence and Provenance

Every important investigation conclusion should be traceable to evidence.

Evidence can come from:

- transaction data
- graph queries
- historical cases
- fraud-pattern documents
- policy documents
- ML output
- analyst input
- simulated customer response

Prefer stable evidence IDs and source metadata so the frontend can display why a conclusion was reached.

## 21. Time and Data Leakage

Historical information must respect the investigation timestamp (`as_of`) where required.

Do not allow future benchmark information to leak into an earlier investigation.

Historical confirmed outcomes may be used as evidence only when they would have been available at the investigation time.

Agent-generated provisional conclusions must not become confirmed training labels.

## 22. Evaluation

The completed system must be tested against all 20 benchmark cases.

For each case capture:

- investigation findings
- evidence
- detected patterns
- risk assessment
- decision/disposition
- next-best action
- approval route
- action result
- SAR requirement where applicable
- explanation

Create a repeatable evaluation script.

Evaluation is part of the product, not an afterthought.

## 23. Development Order

Follow this order unless there is a strong implementation reason to change it:

1. Understand and profile dataset
2. Build Colab preprocessing pipeline
3. Generate processed CSVs
4. Generate ML Parquet
5. Train and validate ML model
6. Design TigerGraph schema
7. Load TigerGraph
8. Implement and test GSQL queries
9. Connect TigerGraph MCP
10. Set up Neon PostgreSQL
11. Build FastAPI layered backend
12. Implement GraphRAG
13. Implement Policy Engine
14. Implement Mock Actions
15. Implement LangGraph agent
16. Connect LLM
17. Build Next.js analyst UI
18. Integrate frontend with backend
19. Run all 20 benchmark cases
20. Improve accuracy and explainability
21. Prepare demo and technical documentation

## 24. Engineering Principles

### Keep the architecture simple

This is a hackathon.

Prefer one FastAPI application with clear modules over multiple microservices.

Do not introduce Redis, Kafka, separate audit services, separate approval services, separate action brokers, or other infrastructure unless a real requirement appears.

### Separation of concerns

Keep:

- graph logic in TigerGraph/GSQL
- ML logic in ML modules
- persistence in repositories
- external systems in integrations
- business logic in services
- agent workflow in LangGraph
- HTTP concerns in routes
- UI concerns in Next.js

### Deterministic where it matters

Graph queries, ML scoring, policy checks and action authorization should be deterministic and testable.

### LLM where it adds value

Use the LLM for reasoning, tool selection, synthesis and explanation.

### Evidence first

Do not make unsupported claims.

### Reproducibility

Preprocessing and ML training should be reproducible from the source dataset and documented configuration.

### Secrets

Never commit:

- API keys
- passwords
- database credentials
- TigerGraph credentials
- LLM credentials
- `.env` files containing secrets

Commit `.env.example` instead.

### Data

Do not commit the full raw hackathon dataset to GitHub unless the competition explicitly permits it and the repository requirements call for it.

Google Drive is the working location for raw/processed datasets during preprocessing.

## 25. Team Workflow

Before changing architecture:

1. Read this file.
2. Check the existing implementation.
3. Check existing API/data contracts.
4. Avoid duplicating functionality.
5. Document important architectural changes.
6. Keep commits focused.
7. Update documentation when changing contracts.

When implementing a feature, identify which layer owns it before writing code.

Do not put business logic into frontend components or FastAPI route handlers.

## 26. Definition of Done

A feature is not complete merely because it works locally.

For important components verify:

- input/output contract
- error handling
- reproducibility
- integration with the rest of the system
- evidence/provenance where relevant
- tests where practical
- benchmark impact where relevant

The final system should demonstrate a complete investigation from benchmark case intake through evidence gathering, risk assessment, next-best-action recommendation, policy/approval, simulated execution, and explainable case history.
