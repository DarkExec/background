#!/usr/bin/env python3
"""Validate the portable Background projection schema and compatibility fixtures."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "darkexec-background-projection.v1.schema.json"
FIXTURES = sorted((ROOT / "examples" / "projections").glob("*.json"))
FORBIDDEN_KEYS = {
    "prompt",
    "promptBody",
    "transcript",
    "toolArguments",
    "credentials",
    "targetPayload",
    "commandOutput",
    "rawJson",
}


def walk(value: object) -> None:
    if isinstance(value, dict):
        forbidden = FORBIDDEN_KEYS.intersection(value)
        assert not forbidden, f"forbidden projection keys: {sorted(forbidden)}"
        for child in value.values():
            walk(child)
    elif isinstance(value, list):
        for child in value:
            walk(child)


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text())
    assert schema["$id"].endswith("darkexec-background-projection.v1.schema.json")
    assert schema["additionalProperties"] is False
    assert FIXTURES, "projection fixtures missing"

    try:
        import jsonschema
    except ImportError:
        jsonschema = None

    statuses = set()
    for fixture_path in FIXTURES:
        fixture = json.loads(fixture_path.read_text())
        walk(fixture)
        assert fixture["schema"] == "darkexec.background.projection/v1"
        assert len(fixture["timeline"]) <= 32
        assert set(fixture["outputs"]) == {"product", "harness", "notification"}
        statuses.add(fixture["execution"]["status"])
        if jsonschema is not None:
            jsonschema.Draft202012Validator(schema).validate(fixture)

    assert {"completed", "not_dispatched"}.issubset(statuses)
    print("background projection contract tests passed")


if __name__ == "__main__":
    main()
