# `declarative-migrations` repository relationships

Generated from reviewed policy and the current **public** repository inventory.

- Public repositories declared: **4**
- Private repository names withheld: **1**
- Relationship edges: **4**

## Repository roles

| Repository | Role | Lifecycle |
|---|---|---|
| [`.github`](https://github.com/declarative-migrations/.github) | `organization_governance` | `active` |
| [`declarative-migrations.github.io`](https://github.com/declarative-migrations/declarative-migrations.github.io) | `site` | `active` |
| [`declarative-postgres-migrate.rs`](https://github.com/declarative-migrations/declarative-postgres-migrate.rs) | `library` | `active` |
| [`homebrew-tap`](https://github.com/declarative-migrations/homebrew-tap) | `uncategorized` | `active` |

## Declared edges

| From | Relationship | To | Status/basis |
|---|---|---|---|
| `declarative-migrations/.github` | `governs` | `declarative-migrations/declarative-migrations.github.io` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `declarative-migrations/.github` | `governs` | `declarative-migrations/declarative-postgres-migrate.rs` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `declarative-migrations/.github` | `governs` | `declarative-migrations/homebrew-tap` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `organization://declarative-migrations` | `packaged_via` | `platform://zed-pkg` | `platform-default` / `platform-policy`: Zed resolves artifacts while submodules compose editable source |

## Composition, service, and observability contract

Git submodules compose editable source; Zed packages resolve packages/artifacts; dual-managed commits must match. Production deploys immutable image digests, not runtime source builds. Cross-service access uses APIs/SDKs/events rather than another service database. MCP uses the product API/SDK. Services emit OpenTelemetry traces, bounded metrics, and correlated structured logs.

## Privacy boundary

This public registry deliberately omits private repository names and edges; the count above makes the boundary explicit.
