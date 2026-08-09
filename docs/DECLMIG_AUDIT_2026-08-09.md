# Declarative Migrations organization audit — 2026-08-09

## Scope

Production organization:

- `.github`
- `declarative-postgres-migrate.rs`
- `declarative-migrations.github.io`
- `homebrew-tap`
- private `declarative-migrations-mcp-server.rs`

Paired test organization:

- governance repository plus the public specialized migration, drift, failure, lock, compatibility, installation, security, upgrade, fuzz, and recovery repositories represented by `declarative-migrations-test/.github/e2e/declmig-e2e.portfolio.json`.

## Positive findings

- The Rust product repository uses read-only workflow permissions and pins GitHub Actions by full commit SHA.
- Checkout credentials are already disabled in the Rust product workflows.
- The product has broad Rust, PostgreSQL, CockroachDB, CLI, package, formal-plan, and independent cross-check coverage.
- The organization `.github` repository already enforces immutable Actions and Docker references through a reusable policy.
- The test organization has substantial specialized coverage rather than one monolithic happy-path test.
- The adopted Linear architecture already defines one `*-lib-core` persistence authority, API-owned product writes, bounded web reads, separate web-state writes, Shared Auth isolation, and a discrete migrator identity.

## Findings and actions

### 1. Aggregate promotion was missing

Neither organization had a `declmig-e2e` repository. This branch adds:

- a machine-readable production/test promotion contract;
- a validator and required workflow;
- a full runnable repository bootstrap scaffold;
- distinct production and test repository configurations;
- an exact source pin and PostgreSQL diff → verify → apply → empty-post-diff lane;
- SHA-256 evidence generation.

Repository provisioning is tracked in `.github#11`, `declarative-migrations-test/.github#13`, and the factory change in `zed-pkg-test/zed-pkg-e2e#163`.

### 2. Test fleet drift reporting was stale

The 2026-08-05 report listed seven repositories as missing even though they now exist, and listed `cli-plan-e2e` plus `postgres-zero-downtime-e2e` as present even though they do not resolve. The paired test-org governance change reconciles this as explicit drift without redefining the central factory manifest.

### 3. Test governance used a mutable Action tag

`declarative-migrations-test/.github` used `actions/checkout@v4` in the portfolio policy. The paired hardening change pins checkout by full SHA, disables persisted credentials, pins the runner, adds concurrency/timeout bounds, expands secret detection, and rejects `pull_request_target` plus `permissions: write-all`.

### 4. Website and tap checkout credentials persisted

The website and Homebrew tap workflows used immutable Action SHAs but did not explicitly disable checkout credential persistence. Separate review branches add `persist-credentials: false`, shallow checkout, hidden progress, and pinned runner labels.

### 5. Cross-checker installation is not reproducible

The Rust repository's seven-tool cross-check matrix still uses mutable Go `@latest` selectors, an Atlas remote installer pipe, unpinned Python packages, and unverified Liquibase/Flyway archives. This is tracked in `declarative-postgres-migrate.rs#33`; aggregate evidence must not imply this debt is already remediated.

## Service/data ownership decision

- `*-lib-core` is the sole persistence/schema/migration/ORM-generation authority and is published as an immutable Zed package.
- API and web install the same package digest but select different capability profiles and receive different database principals.
- API is the sole request-serving product-domain writer and normally owns sensitive/composite reads.
- Web may perform approved bounded direct reads through `__web_ro`; all product mutations use the generated API client.
- Web-only session/PKCE/CSRF/cache state uses an isolated `__web_state_rw` schema and identity.
- Ordinary web/API replicas have no DDL; the serialized one-shot `__migrator` job runs reviewed DPM plans and requires an empty post-apply diff.
- Shared Auth owns identity/session/token assurance but has no product-domain database access.

## Promotion model

1. Pin the candidate source by full commit SHA.
2. Run the test-org aggregate contract.
3. Run required specialized test-org scenario lanes.
4. Produce immutable evidence with source/workflow commits, run ID, engine, result, timestamps, and artifact SHA-256.
5. Let the production aggregate consume that exact evidence.
6. Release only after required evidence passes.

Destructive testing never moves into the production organization merely for convenience.
