# RAGAnchor Initialisation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a runnable, vendor-neutral RAGAnchor Python scaffold with a minimal FastAPI health endpoint, stable response envelope, OpenAPI tests, and a GitHub Actions quality gate.

**Architecture:** Keep the initial application small and dependency-light. `src/rag_anchor/app.py` owns application construction, `src/rag_anchor/api/response.py` owns the public response envelope, and tests cross the HTTP interface through FastAPI's test client. RAG adapters, database modules, and provider implementations remain future seams rather than placeholder code in this initialization.

**Tech Stack:** Python 3.12, `uv`, FastAPI, Pydantic, pytest, Ruff, Pyright, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-27-rag-anchor-initialization-design.md`

## Global Constraints

- Use `RAGAnchor`, `rag_anchor`, and `rag-anchor` as the project identifiers.
- Keep the public repository vendor-neutral; use no private connectors, private URLs, internal identifiers, credentials, or real source content.
- Use the response envelope `{code, msg, trace_id, data}` for HTTP responses.
- Keep `/health` public and make the OpenAPI document describe the actual route security.
- CI runs checks only; it does not deploy, call real models, or require secrets.
- Use `uv run ruff format --check .`, `uv run ruff check .`, `uv run pyright`, and `uv run pytest` as the canonical checks.

## Review Focus

- A clean Python 3.12 environment can install the project and run every check without private configuration; test in Task 1 and Task 3.
- The health response always contains a non-empty `trace_id` and the required envelope fields; test in Task 2.
- The OpenAPI schema exposes the health route, response model, and public security declaration without unresolved local references; test in Task 2.
- CI does not accidentally require model keys, external source credentials, or deployment permissions; inspect and run the workflow checks in Task 3.
- The package, import path, README, and workflow consistently use the new project name; verify in Task 1 and Task 3.

### Task 1: Establish package metadata and local development tooling

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `README.md`
- Create: `LICENSE`

**Interfaces:**
- Package metadata exposes project name `rag-anchor` and import package `rag_anchor`.
- Development dependencies and tool configuration support the canonical commands from the spec.
- README documents local setup, the health endpoint, Swagger URLs, and the fact that private connectors are external extensions.

- [ ] **Step 1: Add package metadata and development dependencies**

  Configure Python `>=3.12,<3.13`, the `src` layout, runtime dependencies for FastAPI/Pydantic, and development dependencies for pytest, HTTPX, Ruff, and Pyright. Add Ruff and Pyright configuration without model or connector dependencies.

- [ ] **Step 2: Add safe repository defaults**

  Add `.python-version`, `.env.example` with placeholder administrator/model variable names only, `.gitignore` for environments and secrets, Apache-2.0 `LICENSE`, and a README with no private deployment references.

- [ ] **Step 3: Resolve and inspect dependencies**

  Run: `uv lock` and `uv sync --dev`.

  Expected: a reproducible `uv.lock` is generated and the environment installs without external credentials.

- [ ] **Step 4: Run the local toolchain before application code exists**

  Run: `uv run ruff format --check .`, `uv run ruff check .`, `uv run pyright`, and `uv run pytest`.

  Expected: commands that have no source/tests yet complete without configuration errors; any missing-test behavior is recorded and resolved in Task 2.

### Task 2: Build the minimal FastAPI application and prove its HTTP contract

**Files:**
- Create: `src/rag_anchor/__init__.py`
- Create: `src/rag_anchor/app.py`
- Create: `src/rag_anchor/api/__init__.py`
- Create: `src/rag_anchor/api/response.py`
- Create: `tests/test_health.py`
- Create: `tests/api/__init__.py`
- Create: `tests/api/test_openapi.py`

**Interfaces:**
- `create_app() -> FastAPI` in `src/rag_anchor/app.py`.
- `app = create_app()` in `src/rag_anchor/app.py` for local ASGI execution.
- `ResponseResult[T]` in `src/rag_anchor/api/response.py` with `code: int`, `msg: str`, `trace_id: str`, and `data: T | None`.
- `GET /health` returns HTTP 200 and the response envelope with `data.status == "ok"`.

- [ ] **Step 1: Write the failing health contract test**

  Add `test_health_returns_the_public_response_envelope` using `TestClient(create_app())`. Assert HTTP 200, `code == 10000`, a non-empty `trace_id`, and `data.status == "ok"`.

- [ ] **Step 2: Run the focused test and verify the expected failure**

  Run: `uv run pytest tests/test_health.py::test_health_returns_the_public_response_envelope -v`

  Expected: FAIL because the package and application do not exist yet.

- [ ] **Step 3: Implement the response model and application factory**

  Add the generic Pydantic response model, generate a request trace ID at the HTTP boundary, create the FastAPI app with title `RAGAnchor`, register a tagged `/health` route, and return the required envelope.

- [ ] **Step 4: Run the focused test and verify it passes**

  Run: `uv run pytest tests/test_health.py::test_health_returns_the_public_response_envelope -v`

  Expected: PASS.

- [ ] **Step 5: Write the failing OpenAPI contract tests**

  Add tests that assert `/health` exists, its operation has the `system` tag, its response schema is present, public routes have an empty security requirement, and the serialized schema contains no unresolved `#/$defs/` references.

- [ ] **Step 6: Run the OpenAPI tests and verify the expected failure**

  Run: `uv run pytest tests/api/test_openapi.py -v`

  Expected: FAIL until the route metadata and response model are complete.

- [ ] **Step 7: Add route metadata and schema-safe response models**

  Add a concise summary, explicit response model, and public security metadata to the health route. Keep the schema generated from the typed Pydantic model rather than hand-written JSON.

- [ ] **Step 8: Run the full local quality suite**

  Run: `uv run ruff format --check .`, `uv run ruff check .`, `uv run pyright`, and `uv run pytest`.

  Expected: all checks PASS.

### Task 3: Add and verify the minimal GitHub Actions CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Workflow triggers on `push`, `pull_request`, and `workflow_dispatch`.
- Workflow uses a clean Ubuntu runner and Python 3.12.
- Workflow runs the same `uv` commands documented for local development.
- Workflow permissions are read-only and no secrets are required.

- [ ] **Step 1: Write the workflow**

  Configure checkout, Python setup, `uv` setup, dependency installation, and checks for format, lint, type checking, and tests. Add concurrency cancellation for superseded pull-request runs.

- [ ] **Step 2: Validate the workflow commands locally**

  Run the same commands from the workflow: `uv run ruff format --check .`, `uv run ruff check .`, `uv run pyright`, and `uv run pytest`.

  Expected: all commands PASS without environment secrets.

- [ ] **Step 3: Inspect the final diff and repository hygiene**

  Run: `git diff --check`, `git status --short`, and a repository scan for private names, URLs, credentials, and real source content.

  Expected: no whitespace errors, no private deployment data, and only intended project files are modified.

- [ ] **Step 4: Commit the initialization**

  Run: `git add . && git commit -m "chore: initialize RAGAnchor project"`.

  Expected: one local commit contains the scaffold and CI configuration.

- [ ] **Step 5: Push the initial commit**

  Run: `git push -u origin main`.

  Expected: GitHub shows the initial commit and starts the CI workflow successfully.
