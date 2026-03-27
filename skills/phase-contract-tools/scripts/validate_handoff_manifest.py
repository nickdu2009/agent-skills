#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "jsonschema",
#   "pyyaml",
# ]
# ///
"""Validate a handoff manifest or handoff artifact against the machine schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a handoff manifest or handoff artifact.")
    parser.add_argument("--handoff", help="Path to a markdown or YAML handoff artifact.")
    parser.add_argument("--manifest", help="Path to a standalone manifest file.")
    parser.add_argument("--schema", help="Optional path to handoff-manifest.schema.json")
    args = parser.parse_args()
    if bool(args.handoff) == bool(args.manifest):
        parser.error("Use either --handoff or --manifest.")
    return args


def default_schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "handoff-manifest.schema.json"


def parse_markdown_payload(text: str) -> dict[str, Any]:
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise ValueError("markdown handoff must start with YAML frontmatter")
    marker = "\n---\n"
    end = normalized.find(marker, 4)
    if end == -1:
        raise ValueError("markdown handoff frontmatter is not closed")
    manifest = yaml.safe_load(normalized[4:end])
    if not isinstance(manifest, dict):
        raise ValueError("handoff frontmatter must decode to a mapping")
    return manifest


def load_manifest(args: argparse.Namespace) -> dict[str, Any]:
    if args.manifest:
        data = yaml.safe_load(Path(args.manifest).expanduser().resolve().read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("manifest file must decode to a mapping")
        return data
    handoff_text = Path(args.handoff).expanduser().resolve().read_text(encoding="utf-8")
    stripped = handoff_text.lstrip()
    if stripped.startswith("---\n"):
        return parse_markdown_payload(stripped)
    data = yaml.safe_load(handoff_text)
    if not isinstance(data, dict):
        raise ValueError("yaml handoff must decode to a mapping")
    manifest = data.get("manifest")
    if not isinstance(manifest, dict):
        raise ValueError("yaml handoff must contain a manifest mapping")
    return manifest


def main() -> int:
    args = parse_args()
    schema_path = Path(args.schema).expanduser().resolve() if args.schema else default_schema_path()
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        manifest = load_manifest(args)
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(manifest), key=lambda item: list(item.path))
        if errors:
            print("Handoff manifest validation failed:")
            for error in errors:
                path = ".".join(str(part) for part in error.path) or "<root>"
                print(f"ERROR {path}: {error.message}")
            return 1
        print("Handoff manifest validation passed.")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR validate-handoff-manifest: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
