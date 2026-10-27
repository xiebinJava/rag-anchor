# RAGAnchor

RAGAnchor is a vendor-neutral retrieval-augmented generation service scaffold.
It starts with a small, testable HTTP boundary so contributors can add
retrieval, source adapters, and answer generation incrementally.

## Local development

The project targets Python 3.12 and uses `uv` for dependency management.

```bash
uv sync --dev
uv run uvicorn rag_anchor.app:app --reload
```

The health endpoint is available at `http://127.0.0.1:8000/health`.
Interactive API documentation is available at `/docs`, the ReDoc view at
`/redoc`, and the machine-readable OpenAPI document at `/openapi.json`.

Run the local quality checks with:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

## Project boundaries

The initial scaffold does not require model credentials, external source
credentials, or a database. Provider-specific model, embedding, and knowledge
source integrations are optional extensions behind stable application seams;
the public core remains vendor-neutral.

Never commit a real `.env` file, access token, source document, or production
configuration. Use synthetic fixtures and placeholders in examples and tests.

## License

RAGAnchor is released under the Apache License 2.0. See [LICENSE](LICENSE).
