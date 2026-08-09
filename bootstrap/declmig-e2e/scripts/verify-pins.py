#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    print(f"pin-policy: {message}", file=sys.stderr)
    raise SystemExit(1)


document = json.loads((ROOT / "source-pins.json").read_text())
if document.get("schema_version") != 1:
    fail("unsupported schema version")
if document.get("policy", {}).get("allow_mutable_refs") is not False:
    fail("mutable refs must be disabled")
sources = document.get("sources")
if not isinstance(sources, list) or not sources:
    fail("at least one required source is needed")
for source in sources:
    repository = source.get("repository", "")
    commit = source.get("commit", "")
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", repository):
        fail(f"invalid repository: {repository!r}")
    if not SHA.fullmatch(commit):
        fail(f"{repository} is not pinned to a 40-hex commit")
    print(f"pin-policy: exact {repository}@{commit}")
