---
status: accepted
---

# Use a stable response envelope and an openly discoverable OpenAPI surface

The HTTP API uses the response envelope `{code, msg, trace_id, data}` for compatibility with existing client expectations. Typed request and response models remain the source of the OpenAPI schema, and HTTP status codes continue to represent transport-level outcomes.

The service exposes `/docs`, `/redoc`, and `/openapi.json` without application-level protection in the first version. Swagger examples and fixtures must use synthetic values; credentials, access tokens, and source content must not be embedded in the schema.
