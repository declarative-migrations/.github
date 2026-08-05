<!-- ore-org-baseline:begin -->
# Repository relationships for `declarative-migrations`

This file is rendered from `repository-relationships.json`. The JSON registry is authoritative.

- Audience: `public`
- Repositories represented: **4**
- Relationships represented: **4**
- Inventory digest: `sha256:8139e59c36b21bed1a2b337cb7ae0211e3166581381ac4f4aa9b20594fe24db7`

## Immutable routing identity

| Field | Value |
|---|---|
| Mapping ID | `context:declarative-migrations` |
| GitHub owner ID | `304551819` |
| Linear project ID | `78d51c47-c6ac-472c-ba3e-525461971027` |
| Linear team ID | `eb8ab169-5afe-4b6f-9cab-3f2aa3e887dc` |

## Repositories

| Repository | Visibility | Roles | Archived |
|---|---|---|---|
| `declarative-migrations/.github` | `public` | `community-health`, `governance`, `relationship-registry` | no |
| `declarative-migrations/declarative-migrations.github.io` | `public` | `documentation-site` | no |
| `declarative-migrations/declarative-postgres-migrate.rs` | `public` | `repository` | no |
| `declarative-migrations/homebrew-tap` | `public` | `repository` | no |

## Relationships

| From | Type | To | Status | Required |
|---|---|---|---|---|
| `declarative-migrations/.github` | `governs` | `declarative-migrations/declarative-migrations.github.io` | `declared` | yes |
| `declarative-migrations/.github` | `governs` | `declarative-migrations/declarative-postgres-migrate.rs` | `declared` | yes |
| `declarative-migrations/.github` | `governs` | `declarative-migrations/homebrew-tap` | `declared` | yes |
| `declarative-migrations/declarative-migrations.github.io` | `documents` | `declarative-migrations/.github` | `inferred` | no |

## Editing relationships

Put reviewed public declarations in `repository-relationships.manual.json`; do not edit the generated registry directly.
Private repository names and private-only relationships belong in the private `ORESoftware/project-registry` mirror.
Inferred edges are advisory and must remain visibly labeled until reviewed.
<!-- ore-org-baseline:end -->
