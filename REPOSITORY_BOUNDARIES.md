# Repository boundaries

Each repository should have one primary responsibility and an explicit dependency direction.

- `*-interfaces`: public wire schemas, protocol contracts, events, error envelopes, and stable cross-language boundaries.
- `*-lib-core`: the sole human-authored persistence authority for product JSON Schema, desired SQL, declarative migration inputs, generator configuration, generated ORM adapters, named database operations, conformance fixtures, and immutable Zed-package provenance.
- `*-lib`: reusable domain logic built on interfaces; it must not become a second schema, ORM, or migration authority.
- `*-clients`: client SDKs and transport adapters generated from or checked against `*-interfaces`.
- `*-sync`: synchronization and offline/replication behavior.
- `*-cli`: command-line workflows composed from clients, interfaces, and libraries.
- Rust API server: the default request-serving owner of product-domain reads and writes. It consumes `*-lib-core/read` and `*-lib-core/write`, owns authorization and transaction policy, and has DML but no broad DDL.
- Rust web server: browser presentation/BFF tier. It calls the API for product mutations and normally for authorization-sensitive reads. Approved direct database reads use only `*-lib-core/read` and a database-enforced read-only principal. It may write only isolated web/session state through a separate schema and principal.
- Shared Auth server: identity, token, session, and assurance plane. It does not own or mutate another product's domain database.
- migrator job: the only ordinary production workload with product-schema DDL. It consumes `*-lib-core/migrator` and executes reviewed declarative-migrations plans as a serialized one-shot job.
- `*-e2e`: black-box and integration verification, not production implementation.

The API and web server may install the same immutable `*-lib-core` Zed package, but they select different capability profiles and receive different database principals. Shared code is not permission to share a writer credential.

For declarative-migrations specifically:

- `declarative-migrations-test` is the destructive, failure-injection, engine-compatibility, and candidate certification environment.
- `declarative-migrations/declmig-e2e` is the stable promotion orchestrator and consumes exact, immutable evidence produced by the test organization.
- `declarative-migrations-test/declmig-e2e` is the aggregate test-fleet orchestrator and may exercise ephemeral databases, candidate commits, rollback/forward-fix paths, lock contention, drift, and fault injection.
- Production promotion never trusts an unpinned branch, mutable artifact, or workflow tag.

When repositories overlap, choose a canonical home, reconcile histories semantically, migrate callers, preserve attribution and useful history, and leave a clear deprecation pointer. Generated ORM output is derived; hand-edited generated files must fail conformance checks.
