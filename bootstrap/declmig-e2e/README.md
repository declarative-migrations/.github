# declmig-e2e production bootstrap

Production-owned release orchestrator for the `declarative-migrations` organization.

This tree is ready to become `declarative-migrations/declmig-e2e`. It pins the hardened migration engine head, defines the release gate, encodes web/API/`*-lib-core` ownership, and provides credential-free contract CI plus manual/scheduled exact-head database certification.

The production orchestrator must consume matching evidence from `declarative-migrations-test/declmig-e2e`; it cannot replace that independent trust domain.

Current source pin: `declarative-migrations/declarative-postgres-migrate.rs@b829384df970e3b9415b566ef9d87511bdc163c7`.
