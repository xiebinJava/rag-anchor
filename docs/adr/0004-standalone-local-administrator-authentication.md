---
status: accepted
---

# Use standalone local administrator authentication for the open-source service

The project is an open-source service and will not depend on an organization SSO, an external permission platform, or an internal tenant/RBAC system in the first version. The service will bootstrap one local administrator from deployment configuration. Credentials are supplied at first run or through environment/secret configuration; a fixed username/password is never committed to the repository.

This keeps the project runnable outside any one deployment environment while leaving the authentication seam open for a later SSO or gateway adapter. The local administrator protects management and synchronization operations; it is separate from the external knowledge-source identity used to read the controlled shared knowledge space.
