# RAG Query Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic local-fixture RAG query endpoint with grounded answers, citations, no-answer semantics, and OpenAPI coverage.

**Architecture:** Keep the HTTP route thin and put the query behavior behind small `KnowledgeSource`, `Retriever`, and `AnswerGenerator` seams. The first adapters read repository Markdown fixtures, score lexical overlap, and return retrieved evidence verbatim; later adapters can replace these implementations without changing the HTTP contract.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, pytest, HTTPX, Ruff, Pyright, repository Markdown fixtures.

**Spec:** `docs/superpowers/specs/2026-11-04-rag-query-vertical-slice-design.md`

## Global Constraints

- Keep the public repository vendor-neutral and use only synthetic local fixture content.
- Preserve the response envelope `{code, msg, trace_id, data}`.
- Do not add model, embedding, database, vector-store, external connector, or secret dependencies.
- Treat no-answer as a normal HTTP 200 business result with no citations.
- Test the public HTTP seam; do not couple tests to private implementation details.
- Keep Swagger/OpenAPI openly discoverable and accurately describe the public route.

## Review Focus

- Empty or overlong questions must return validation errors rather than triggering retrieval.
- `top_k` values outside 1–5 must be rejected and valid values must cap returned citations.
- Queries with no matching evidence must not produce an answer or fabricated citation.
- Fixture source failures or malformed Markdown must not silently expand the knowledge scope.
- OpenAPI must expose the request/response models and a public security declaration without unresolved local references.

### Task 1: Define the query contract and failing HTTP tests

**Files:**
- Create: `tests/api/test_query.py`
- Modify: `tests/api/test_openapi.py`

**Interfaces:**
- `POST /api/v1/query` accepts `question` and optional `top_k`.
- A successful response uses `ResponseResult[QueryData]` with `answer`, `citations`, and `no_answer`.

- [ ] **Step 1: Write the failing successful-query test**

  Use `TestClient(create_app())` to post a known question from the local fixture. Assert HTTP 200, `code == 10000`, a non-empty `trace_id`, `no_answer is False`, a non-empty answer, and a citation containing the expected document ID and source URL.

- [ ] **Step 2: Run the focused test and verify the expected failure**

  Run: `uv run pytest tests/api/test_query.py::test_query_returns_grounded_answer_and_citation -v`

  Expected: FAIL because the query route and fixture-backed service do not exist.

- [ ] **Step 3: Write the failing no-answer and validation tests**

  Add tests for an unknown question (`no_answer is True`, `answer is None`, empty citations), an empty question, and `top_k=0`.

- [ ] **Step 4: Run the focused contract tests and verify failure**

  Run: `uv run pytest tests/api/test_query.py -v`

  Expected: FAIL until the route, models, and query service are implemented.

### Task 2: Implement the local fixture query seam

**Files:**
- Create: `fixtures/knowledge/rag-anchor-baseline.md`
- Create: `tests/test_source.py`
- Create: `src/rag_anchor/rag/__init__.py`
- Create: `src/rag_anchor/rag/models.py`
- Create: `src/rag_anchor/rag/source.py`
- Create: `src/rag_anchor/rag/retrieval.py`
- Create: `src/rag_anchor/rag/query.py`
- Create: `src/rag_anchor/api/query.py`
- Modify: `src/rag_anchor/app.py`

**Interfaces:**
- `KnowledgeSource.load_documents() -> tuple[Document, ...]`.
- `Retriever.retrieve(question: str, top_k: int) -> tuple[RetrievedChunk, ...]`.
- `AnswerGenerator.generate(question: str, evidence: tuple[RetrievedChunk, ...]) -> str`.
- `QueryService.query(question: str, top_k: int) -> QueryResult`.
- `create_app(query_service: QueryService | None = None) -> FastAPI`.

- [ ] **Step 1: Implement the smallest fixture-backed path for the successful-query test**

  Add typed domain models, a Markdown fixture source, deterministic paragraph chunking, lexical overlap retrieval, and a deterministic answer generator that returns the top evidence text. Keep the default fixture path repository-relative and inject `QueryService` through `create_app` for tests.

- [ ] **Step 2: Run the successful-query test and verify it passes**

  Run: `uv run pytest tests/api/test_query.py::test_query_returns_grounded_answer_and_citation -v`

  Expected: PASS.

- [ ] **Step 3: Add the no-answer and request validation behavior**

  Add Pydantic request/response models with `question` length 1–2000 and `top_k` range 1–5, return the normal no-answer result when retrieval is empty, and preserve the response envelope and trace ID.

- [ ] **Step 4: Run the query contract tests and verify they pass**

  Run: `uv run pytest tests/api/test_query.py -v`

  Expected: PASS.

### Task 3: Publish and verify the OpenAPI query contract

**Files:**
- Modify: `src/rag_anchor/api/query.py`
- Modify: `src/rag_anchor/app.py`
- Modify: `tests/api/test_openapi.py`

**Interfaces:**
- The query operation is tagged `query`, has summary `Query the knowledge base`, declares its typed 200 response, and declares `security: []`.

- [ ] **Step 1: Write the failing OpenAPI assertions**

  Assert the query path/method, tag, summary, request body schema, response envelope schema, query data fields, and public security declaration. Resolve local `$ref` values before asserting nested properties.

- [ ] **Step 2: Run the OpenAPI test and verify the expected failure**

  Run: `uv run pytest tests/api/test_openapi.py -v`

  Expected: FAIL until route metadata and typed models are registered.

- [ ] **Step 3: Add route metadata and register the typed response model**

  Add the route to the application with the exact path, tag, summary, response model, and public security metadata; do not hand-write the schema.

- [ ] **Step 4: Run the full quality suite**

  Run: `uv run ruff format --check .`, `uv run ruff check .`, `uv run pyright`, and `uv run pytest`.

  Expected: all checks PASS.

- [ ] **Step 5: Commit the vertical slice**

  Run: `git add fixtures src tests docs && git commit -m "feat: add local RAG query vertical slice"`.

  Expected: one local commit contains the query slice, contract tests, fixture, and design/plan docs.
