# `declmig-e2e` repository blueprint

This directory is the reviewable bootstrap and synchronization source for two repositories with the same name and different trust roles:

- `declarative-migrations-test/declmig-e2e`: candidate and destructive fleet orchestration against ephemeral or explicitly disposable targets.
- `declarative-migrations/declmig-e2e`: stable promotion orchestration that consumes exact evidence from the test organization and never targets destructive infrastructure.

Both repositories were provisioned on 2026-08-09 and their initial implementations remain reviewable pull requests. Future changes to common files should be applied symmetrically unless a difference is explicitly part of `config/repository.json`.

## Bootstrap or reconciliation

1. Create or verify the target repository with the default branch `main`, issues enabled, secret scanning enabled, and no unreviewed generated files.
2. Copy `common/` to the repository root.
3. For the production organization, copy `production/config/repository.json` to `config/repository.json`.
4. For the test organization, copy `test/config/repository.json` to `config/repository.json`.
5. Open changes as a pull request. Do not push bootstrap files directly to a protected `main` branch.
6. Require the `contract` and `postgres-smoke` jobs before merge.
7. Update `pins/source.json` only through a reviewed pull request; `source_commit` must remain a full 40-character commit SHA and must have successful required source-repository checks.

The common smoke lane checks out the exact `declarative-postgres-migrate.rs` commit, runs library/property tests, builds the exact `dpm` binary, starts a digest-pinned isolated PostgreSQL service, produces a deterministic plan, rehearses it with `dpm verify`, applies it to a disposable target, and requires `dpm diff --fail-on-diff` to report convergence.

Formatting and strict Clippy remain source-repository gates. The aggregate harness must not reformat an immutable historical source tree with a newer moving formatter, because that makes old commits fail for reasons unrelated to their runtime behavior. Aggregate E2E owns black-box build/integration/promotion evidence instead.

Successful evidence records the exact source SHA, harness head SHA, run ID and attempt, PostgreSQL image digest, `dpm` binary SHA-256, test/build logs, migration plan, post-apply diff, and catalog assertions. Failed runs upload diagnostics separately and never create a passing evidence bundle.

## Trust separation

The same common files do not imply the same permissions.

- Pull-request jobs receive no repository or cloud secrets.
- The test repository may add scheduled/protected environments for engine matrices, fault injection, concurrency, and destructive rollback/forward-fix scenarios. It must reject production credentials and production database targets.
- The production repository may read an exact evidence bundle from the test organization, but it may not dispatch destructive test targets or trust mutable branches/artifacts.
- All Actions, the Rust toolchain, and the database image are immutable pins; checkout credentials are not persisted.
- Evidence uses the actual pull-request head commit rather than GitHub's ephemeral merge commit.

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
