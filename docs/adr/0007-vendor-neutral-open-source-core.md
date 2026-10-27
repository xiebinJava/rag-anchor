---
status: accepted
---

# Keep the public core vendor-neutral and isolate private connectors

The public repository contains the domain model, generic Wiki/cloud-document interfaces, local Markdown fixtures, HTTP API, CLI, evaluation workflow, and reference adapters that do not require private deployment context. A concrete vendor connector is optional and must be supplied as an independent extension or by the deploying project; the public core must not require a company-specific SDK, URL, identifier, permission service, or naming convention.

This keeps the project reusable outside one organization and prevents private deployment assumptions from leaking into the core interfaces. The `KnowledgeSource` seam is the extension point for later connectors, while the first version remains testable entirely with local fixtures and recorded adapter responses.
