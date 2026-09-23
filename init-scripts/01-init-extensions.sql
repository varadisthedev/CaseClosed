-- CaseClosed database initialization.
-- Runs once on first PostgreSQL container start.

-- pgvector for GraphRAG embeddings (AGENTS.md §10, §11)
CREATE EXTENSION IF NOT EXISTS vector;
