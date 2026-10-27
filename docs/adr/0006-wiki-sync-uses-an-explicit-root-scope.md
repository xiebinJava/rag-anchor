---
status: accepted
---

# Scope Wiki/cloud-document synchronization to a dedicated space and optional root node

The first Wiki/cloud-document adapter accepts a `source_space_id` and an optional `source_root_id`. The production configuration should point at a dedicated controlled shared knowledge space and, where practical, a dedicated root node; the adapter must not discover or index content outside that configured scope.

The root-node scope reduces accidental ingestion while preserving the ability to use an entire dedicated space when the root node is omitted. Sync configuration, document identity, and document revisions remain explicit so incremental synchronization can be idempotent and auditable.
