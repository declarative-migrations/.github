#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sha="${DPM_SOURCE_SHA:-$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["sources"][0]["commit"])' "$root/source-pins.json") }"
sha="${sha% }"
[[ "$sha" =~ ^[0-9a-f]{40}$ ]] || { echo 'DPM_SOURCE_SHA must be exact 40-hex' >&2; exit 64; }
rm -rf "$root/vendor/dpm"
git init -q "$root/vendor/dpm"
git -C "$root/vendor/dpm" remote add origin https://github.com/declarative-migrations/declarative-postgres-migrate.rs.git
git -C "$root/vendor/dpm" fetch --no-tags --depth=1 origin "$sha"
git -C "$root/vendor/dpm" checkout -q --detach FETCH_HEAD
[[ "$(git -C "$root/vendor/dpm" rev-parse HEAD)" == "$sha" ]]
(
  cd "$root/vendor/dpm"
  cargo fmt --all -- --check
  cargo clippy --locked --all-targets -- -D warnings
  cargo test --locked --test apply_lease_wiring
  cargo test --locked --lib
)
case "${DECLMIG_ENGINE:-contract-only}" in
  postgres-16|postgres-17)
    : "${DPM_TEST_DATABASE_URL:?required}"
    (cd "$root/vendor/dpm" && cargo test --locked --test lease_contract -- --test-threads=1)
    (cd "$root/vendor/dpm" && cargo test --locked --test convergence -- --test-threads=1)
    ;;
  cockroach-25.2.4)
    : "${DPM_TEST_COCKROACH_DATABASE_URL:?required}"
    (cd "$root/vendor/dpm" && cargo test --locked --test cockroach -- --test-threads=1)
    ;;
  contract-only) ;;
  *) echo 'unknown DECLMIG_ENGINE' >&2; exit 64 ;;
esac
