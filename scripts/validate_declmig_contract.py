#!/usr/bin/env python3
"""Validate the declarative-migrations aggregate E2E and service-boundary contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

EXPECTED_AGGREGATES = {
    "declarative-migrations/declmig-e2e": {
        "role": "stable-promotion-orchestrator",
        "accepts_destructive_targets": False,
    },
    "declarative-migrations-test/declmig-e2e": {
        "role": "candidate-and-destructive-fleet-orchestrator",
        "accepts_destructive_targets": True,
    },
}

MINIMUM_SCENARIOS = {
    "forward-and-rollback",
    "idempotent-replay",
    "schema-drift-detection",
    "data-preservation",
    "failure-atomicity",
    "concurrent-migrator-locking",
    "cross-engine-compatibility",
    "security-boundary",
    "lib-core-schema-and-generated-adapter-parity",
    "api-write-web-read-only-permissions",
    "shared-auth-to-product-api-handoff",
}

SECRET_PATTERNS = (
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"lin_api_[A-Za-z0-9]{20,}"),
    re.compile(r"cfat_[A-Za-z0-9_-]{20,}"),
    re.compile(r"BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY"),
)


class ContractError(ValueError):
    """Raised when the contract violates a required invariant."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def require_unique_strings(value: Any, path: str) -> list[str]:
    require(isinstance(value, list), f"{path} must be an array")
    require(all(isinstance(item, str) and item for item in value), f"{path} must contain non-empty strings")
    require(len(value) == len(set(value)), f"{path} contains duplicates")
    return value


def walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for key, item in value.items():
            result.extend(walk_strings(key))
            result.extend(walk_strings(item))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(walk_strings(item))
        return result
    return []


def validate(contract: dict[str, Any]) -> None:
    require(contract.get("schema_version") == 1, "schema_version must be 1")
    require(contract.get("contract_id") == "declmig-e2e", "contract_id must be declmig-e2e")
    require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(contract.get("audited_at", ""))) is not None, "audited_at must be YYYY-MM-DD")

    organizations = contract.get("organizations")
    require(isinstance(organizations, dict), "organizations must be an object")
    require(organizations.get("production") == "declarative-migrations", "production organization mismatch")
    require(organizations.get("test") == "declarative-migrations-test", "test organization mismatch")

    aggregates = contract.get("aggregate_repositories")
    require(isinstance(aggregates, list), "aggregate_repositories must be an array")
    require(len(aggregates) == len(EXPECTED_AGGREGATES), "both aggregate repositories are required")
    by_name = {item.get("full_name"): item for item in aggregates if isinstance(item, dict)}
    require(set(by_name) == set(EXPECTED_AGGREGATES), "aggregate repository names do not match the contract")
    for name, expected in EXPECTED_AGGREGATES.items():
        item = by_name[name]
        require(item.get("required_visibility") == "public", f"{name} must be public")
        require(item.get("role") == expected["role"], f"{name} role mismatch")
        require(item.get("accepts_destructive_targets") is expected["accepts_destructive_targets"], f"{name} destructive-target policy mismatch")

    sources = contract.get("source_repositories")
    require(isinstance(sources, list) and len(sources) == 1, "exactly one canonical product source is expected")
    source = sources[0]
    require(source.get("full_name") == "declarative-migrations/declarative-postgres-migrate.rs", "canonical source repository mismatch")
    require(source.get("artifact") == "dpm", "canonical artifact must be dpm")
    require(source.get("ref_policy") == "full-commit-sha", "source refs must be full commit SHAs")
    require_unique_strings(source.get("required_checks"), "source_repositories[0].required_checks")

    boundary = contract.get("service_data_boundary")
    require(isinstance(boundary, dict), "service_data_boundary must be an object")

    lib_core = boundary.get("lib_core")
    require(isinstance(lib_core, dict), "service_data_boundary.lib_core must be an object")
    require(lib_core.get("authority") == "sole-human-authored-persistence-source", "*-lib-core must be the sole persistence authority")
    require(set(require_unique_strings(lib_core.get("required_profiles"), "lib_core.required_profiles")) == {"contracts", "read", "write", "migrator"}, "lib-core capability profiles must be contracts/read/write/migrator")
    require(lib_core.get("distribution") == "immutable-zed-package", "lib-core must be distributed as an immutable Zed package")
    required_adapters = set(require_unique_strings(lib_core.get("required_adapters"), "lib_core.required_adapters"))
    require({"rust-seaorm", "typescript-drizzle"}.issubset(required_adapters), "Rust SeaORM and TypeScript Drizzle are required adapters")

    api = boundary.get("api_server")
    require(isinstance(api, dict), "api_server boundary missing")
    require(set(api.get("product_domain_access", [])) == {"read", "write"}, "API must own product reads and writes")
    require(api.get("database_role_suffix") == "__api_rw", "API role must end in __api_rw")
    require(api.get("ddl") is False, "request-serving API must not have broad DDL")
    require(api.get("request_serving_product_writer") is True, "API must be the request-serving product writer")

    web = boundary.get("web_server")
    require(isinstance(web, dict), "web_server boundary missing")
    require(web.get("product_domain_access") == ["approved-bounded-read"], "web product access must be bounded read-only")
    require(web.get("database_role_suffix") == "__web_ro", "web role must end in __web_ro")
    require(web.get("product_writes_route") == "generated-api-client", "web product writes must route through the API client")
    require(web.get("isolated_state_role_suffix") == "__web_state_rw", "web-owned state must use an isolated role")
    require(web.get("ddl") is False, "web must not have product DDL")
    require(web.get("request_serving_product_writer") is False, "web must not be a product writer")

    migrator = boundary.get("migrator")
    require(isinstance(migrator, dict), "migrator boundary missing")
    require(migrator.get("database_role_suffix") == "__migrator", "migrator role mismatch")
    require(migrator.get("execution") == "serialized-one-shot-job", "migrations must run as a serialized one-shot job")
    require(migrator.get("requires_empty_post_apply_diff") is True, "migrator must require an empty post-apply diff")

    shared_auth = boundary.get("shared_auth")
    require(isinstance(shared_auth, dict), "shared_auth boundary missing")
    require(shared_auth.get("product_domain_database_access") is False, "Shared Auth must not access product-domain databases")

    order = require_unique_strings(contract.get("promotion_order"), "promotion_order")
    require(order.index("test-org-aggregate-contract") < order.index("production-aggregate-promotion"), "test-org certification must precede production promotion")
    require(order[-1] == "release", "release must be the final promotion step")

    scenarios = set(require_unique_strings(contract.get("required_scenario_classes"), "required_scenario_classes"))
    require(MINIMUM_SCENARIOS.issubset(scenarios), "required scenario coverage is incomplete")

    repositories = require_unique_strings(contract.get("required_test_repositories"), "required_test_repositories")
    require(len(repositories) >= 12, "the aggregate contract must cover at least 12 specialized test repositories")
    require(all(name.startswith("declarative-migrations-test/") for name in repositories), "all specialized repositories must be in the test organization")
    require("declarative-migrations-test/declmig-e2e" not in repositories, "the aggregate repository must not list itself as a specialized lane")

    evidence = contract.get("evidence")
    require(isinstance(evidence, dict), "evidence must be an object")
    require(evidence.get("schema_version") == 1, "evidence schema_version must be 1")
    require_unique_strings(evidence.get("required_fields"), "evidence.required_fields")
    re.compile(evidence.get("source_commit_pattern", ""))
    re.compile(evidence.get("artifact_digest_pattern", ""))
    require(evidence.get("mutable_branch_evidence_allowed") is False, "mutable branch evidence must be forbidden")

    supply_chain = contract.get("supply_chain")
    require(isinstance(supply_chain, dict), "supply_chain must be an object")
    require(supply_chain.get("github_actions") == "full-commit-sha-only", "Actions must be pinned by full SHA")
    require(supply_chain.get("checkout_persist_credentials") is False, "checkout credentials must not persist")
    require(supply_chain.get("production_images") == "digest-only", "production images must use digests")
    require(supply_chain.get("remote_install_scripts") == "forbidden", "remote install scripts must be forbidden")
    require(supply_chain.get("latest_version_selectors") == "forbidden", "latest selectors must be forbidden")
    require(supply_chain.get("archives_require_checksum") is True, "downloaded archives must be checksummed")
    require(supply_chain.get("secrets_in_pull_request_workflows") is False, "pull-request workflows must not receive secrets")

    for text in walk_strings(contract):
        for pattern in SECRET_PATTERNS:
            require(pattern.search(text) is None, "contract contains secret-like material")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", nargs="?", default="e2e/declmig-e2e.contract.json")
    args = parser.parse_args()

    path = Path(args.contract)
    try:
        raw = path.read_text(encoding="utf-8")
        parsed = json.loads(raw)
        require(isinstance(parsed, dict), "contract root must be an object")
        validate(parsed)
    except (OSError, json.JSONDecodeError, ContractError, re.error) as exc:
        print(f"declmig contract validation failed: {exc}", file=sys.stderr)
        return 1

    print(
        "declmig contract valid: "
        f"{len(parsed['required_scenario_classes'])} scenario classes, "
        f"{len(parsed['required_test_repositories'])} specialized repositories"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
