#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "jsonschema",
#   "pyyaml",
# ]
# ///
"""Validate a wave status snapshot against the machine schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a wave status snapshot.")
    parser.add_argument("--snapshot", required=True, help="Path to a YAML or JSON snapshot file, or - for stdin.")
    parser.add_argument("--schema", help="Optional path to wave-status-snapshot.schema.json")
    return parser.parse_args()


def default_schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "wave-status-snapshot.schema.json"


def load_snapshot(path_arg: str) -> dict[str, Any]:
    if path_arg == "-":
        text = sys.stdin.read()
    else:
        text = Path(path_arg).expanduser().resolve().read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("snapshot must decode to a mapping")
    return data


def main() -> int:
    args = parse_args()
    schema_path = Path(args.schema).expanduser().resolve() if args.schema else default_schema_path()
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        snapshot = load_snapshot(args.snapshot)
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(snapshot), key=lambda item: list(item.path))
        if errors:
            print("Wave status snapshot validation failed:")
            for error in errors:
                path = ".".join(str(part) for part in error.path) or "<root>"
                print(f"ERROR {path}: {error.message}")
            return 1
        print("Wave status snapshot validation passed.")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR validate-wave-status-snapshot: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
