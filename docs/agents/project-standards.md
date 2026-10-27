# Project Standards

These are the accepted implementation conventions for the first version of the RAGAnchor service. Treat `pyproject.toml`, the source tree, and test configuration as the executable source of truth once they exist; this document records the conventions and the reasons an agent cannot infer from those files.

## Python project shape

Keep the repository organized around a single Python package:

- `pyproject.toml`: package metadata, dependencies, tool configuration, and canonical development commands.
- `src/rag_anchor/`: application code and domain interfaces.
- `tests/`: automated tests, grouped by test layer.
- `scripts/`: small local-development and evaluation entry points.
- `docs/`: ADRs and agent-facing project documentation.
- `.env.example`: names and safe examples for required configuration; never put credentials in the repository.

Use `uv` for environment and dependency management, Ruff for formatting and linting, pytest for tests, and Pyright for static type checking. Keep vendor-specific LLM, embedding, and knowledge-source code behind adapters so the core domain speaks in project terms rather than provider terms.

## Vector storage

Use PostgreSQL with the `pgvector` extension as the first vector-storage implementation. Keep document metadata, revisions, chunks, embeddings, and retrieval filters in the same database so indexing and permission-scope constraints can be tested together. Hide the implementation behind a small `VectorStore` interface; a dedicated vector backend is a later replacement option, not a first-version dependency.

Start with exact nearest-neighbor search for small local fixtures and benchmark the transition to an approximate index before enabling it in production. Any approximate index must be evaluated together with source-scope filters because filtering strategy affects recall.

Do not introduce a dedicated vector backend until measurements show that PostgreSQL + pgvector is the bottleneck. The migration trigger is one or more sustained signals: retrieval latency or error rate misses the agreed SLO, vector storage/index building competes materially with transactional workloads, filtered retrieval loses recall at the target scale, or the deployment needs independent vector scaling, sharding, or replication. Record the benchmark and run a shadow-read or backfill comparison before switching the active backend.

## Test layers

Every behavior change must be covered at the narrowest useful public boundary:

1. Unit tests cover deterministic domain behavior, chunking, ranking orchestration, error mapping, and answer/citation rules.
2. Integration tests cover PostgreSQL/pgvector, job execution, and the HTTP boundary using controlled local dependencies.
3. Contract tests cover the Wiki/cloud-document adapter against recorded or fixture responses and verify source identity, revisions, and permission-scope handling.
4. RAG evaluation tests use the versioned `RAG 评估集` to detect retrieval, grounding, citation, and no-answer regressions.

Prefer testing public interfaces and observable outcomes. Do not make tests depend on private implementation details when a stable interface can express the same behavior.

## API contract and interface tests

Treat the HTTP interface and its OpenAPI document as one contract. FastAPI exposes `/docs`, `/redoc`, and `/openapi.json` by default because this is an open-source service and the user has chosen an openly discoverable API surface. Deployments may add gateway-level protection later, but the application must not depend on a hidden documentation route.

Every public route needs typed request and response models, a stable tag, a concise summary, documented validation and error responses, and an explicit authentication scheme in OpenAPI. The authentication scheme must describe the actual runtime dependency; a Swagger button must never imply access that the route does not enforce.

Unless a future ADR changes this decision, API responses follow the established project envelope: `code`, `msg`, `trace_id`, and `data`. HTTP status codes still communicate transport-level success or failure; the business code remains stable for clients that consume the envelope.

For each route family, add interface tests with FastAPI's test client or ASGI client. The tests should cover successful input, validation failure, authentication/authorization failure, not-found or no-answer behavior, and upstream failure mapping. Add OpenAPI tests that verify expected paths, methods, request/response schemas, security requirements, and the absence of unresolved local schema references.

Swagger is a manual test surface, not a replacement for automated interface tests. Keep examples safe and synthetic; never place real access tokens, source content, or production credentials in the schema or test fixtures. The initial administrator credential is supplied at first-run configuration time and is never embedded in Swagger examples.

## Error and answer semantics

- Invalid request data is a client error with a stable 4xx response.
- Missing or insufficient application access is an explicit authorization error; do not silently broaden the knowledge scope.
- Temporary source or infrastructure failures are observable and retryable where safe.
- A `无答案` result is a normal business outcome, not an exception and not an invitation to guess.
- Every non-empty answer must expose citations that point back to the original source document and location when the source provides one.

## Logging and data handling

Use structured logs with request identity, request ID, latency, document/chunk identifiers, retrieval and model versions, error type, and citation count where relevant. Keep raw source text, access tokens, secrets, and unnecessary sensitive content out of normal logs. Redact values at the boundary before they enter logs, traces, or error messages.

## RAG quality gates

Before a change is considered ready, verify all of the following:

- relevant documents are retrieved for representative questions;
- answers are grounded in retrieved evidence;
- citations resolve to the original source document or source location;
- the service returns `无答案` when evidence is insufficient;
- retrieval stays inside the `受控共享知识空间` boundary;
- type checking, linting, formatting, unit/integration tests, and applicable evaluation tests pass.

When a gate cannot run locally, record the exact missing dependency or environment assumption instead of treating the change as verified.
