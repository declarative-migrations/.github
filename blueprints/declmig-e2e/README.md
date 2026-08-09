# `declmig-e2e` repository blueprint

This directory is the reviewable bootstrap source for two repositories with the same name and different trust roles:

- `declarative-migrations-test/declmig-e2e`: candidate and destructive fleet orchestration against ephemeral or explicitly disposable targets.
- `declarative-migrations/declmig-e2e`: stable promotion orchestration that consumes exact evidence from the test organization and never targets destructive infrastructure.

## Bootstrap

1. Create the target repository with the default branch `main`, issues enabled, secret scanning enabled, and no initial generated files.
2. Copy `common/` to the repository root.
3. For the production organization, copy `production/config/repository.json` to `config/repository.json`.
4. For the test organization, copy `test/config/repository.json` to `config/repository.json`.
5. Open the first change as a pull request. Do not push bootstrap files directly to a protected `main` branch.
6. Require the `contract` and `postgres-smoke` jobs before merge.
7. Update `pins/source.json` only through a reviewed pull request; `source_commit` must remain a full 40-character commit SHA.

The common smoke lane checks out the exact `declarative-postgres-migrate.rs` commit, starts an isolated PostgreSQL service, produces a deterministic plan, rehearses it with `dpm verify`, applies it to a disposable target, and requires `dpm diff --fail-on-diff` to report convergence. It emits an evidence JSON document and SHA-256-addressed artifacts.

## Trust separation

The same files do not imply the same permissions.

- Pull-request jobs receive no repository or cloud secrets.
- The test repository may add scheduled/protected environments for engine matrices, fault injection, concurrency, and destructive rollback/forward-fix scenarios. It must reject production credentials and production database targets.
- The production repository may read an exact evidence bundle from the test organization, but it may not dispatch destructive test targets or trust mutable branches/artifacts.
- All Actions are pinned by immutable commit SHA and checkout credentials are not persisted.

## Product-service scenarios added by the aggregate test repository

The specialized fleet remains authoritative for engine and failure scenarios. The aggregate repository adds cross-repository certification for:

- one `*-lib-core` persistence authority and generated-adapter digest parity;
- API `__api_rw`, web `__web_ro`, isolated web-state `__web_state_rw`, and migrator `__migrator` database permissions;
- browser product mutations traversing the generated API client;
- Shared Auth audience, actor, tenant, expiry, and revocation handoff without product-database access;
- serialized DPM execution and an empty post-apply diff;
- immutable Zed package publication, installation, and lock behavior;
- exact evidence generation for production promotion.

The source of truth for the overall contract is `e2e/declmig-e2e.contract.json` in the organization `.github` repository.
