# Canonical declarative-migrations E2E architecture

Status on 2026-08-09: the target repositories `declarative-migrations/declmig-e2e` and `declarative-migrations-test/declmig-e2e` do not yet exist. The reviewed bootstrap trees live under each organization’s `.github` repository until provisioning is available.

## Trust domains

`declarative-migrations/declmig-e2e` is the production-owned release orchestrator. It assembles exact-head core, packaging, MCP, database-engine, and independent test-organization evidence. It must not self-attest the hostile-consumer gate.

`declarative-migrations-test/declmig-e2e` is an independent consumer. It tests immutable production commits with synthetic data and ephemeral PostgreSQL/CockroachDB instances. A missing dependency, secret, or protected lane is `blocked`, never `passed`.

## Database and runtime ownership

Every application organization should publish an exact version and digest of `*-lib-core` as a Zed package. That package owns persistence JSON Schema, desired SQL, declarative-migration inputs, generated ORM adapters, named operations, and conformance fixtures. It is a source artifact, not a privileged runtime service.

The default runtime split is:

- one-shot serialized migrator: DDL and migration ledger only;
- API server: named product reads and product writes; no DDL;
- web server: bounded product reads through a read-only identity; product writes call the API;
- optional web-state identity: writes only isolated web-owned state such as encrypted sessions or UI preferences;
- Shared Auth: authentication, sessions, token issue/revocation; resource API: business authorization.

Direct web product writes require a time-bounded ADR, a named operation, a separate least-privilege principal, audit evidence, and an expiry date.

## Promotion invariant

A release is promotable only when production and independent test evidence bind to the same 40-hex source commit, every required result is `passed`, artifact SHA-256 digests are present, and no source/action/package/container input is mutable. Blocked evidence cannot satisfy the gate.
