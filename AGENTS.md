## Agent skills

### Issue tracker

Issues and specs live as local Markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repo. See `GLOSSARY.md` and `docs/adr/` as described in `docs/agents/domain.md`.

### Project standards

When adding or changing Python code, tests, API behavior, ingestion, retrieval, answer generation, or observability, read `docs/agents/project-standards.md` before editing. It contains the required project layout, toolchain, test layers, error semantics, logging rules, and RAG quality gates.

### Open-source hygiene

Keep this repository public-safe and vendor-neutral. Do not add organization names, internal project names or codes, private URLs, tenant or employee identifiers, credentials, proprietary system names, or company-specific abbreviations to code, documentation, configuration, logs, or fixtures. Prefer generic terms such as `wiki`, `cloud_docs`, and `external_source`; use synthetic examples. Put vendor-specific or private deployment integrations behind optional adapters or outside this repository.
