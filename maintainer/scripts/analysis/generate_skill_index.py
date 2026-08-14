#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Generate compact skill metadata index from SKILL.md files.

This script extracts minimal metadata from SKILL.md frontmatter and generates
a compact JSON index for use in evaluation and testing workflows.

Purpose:
  - Provide fast, deterministic metadata lookup without parsing all SKILL.md files
  - Preserve byte-equivalent discovery content across both loading modes
  - Enable efficient skill categorization and family classification

Input:
  - SKILL.md files in skills/ directory (frontmatter with name, description, metadata)
  - skill_protocol.py (for family classification)

Output:
  - maintainer/data/skill_index.json (compact metadata index)

Usage:
  python3 maintainer/scripts/analysis/generate_skill_index.py
  python3 maintainer/scripts/analysis/generate_skill_index.py --output /path/to/output.json
  python3 maintainer/scripts/analysis/generate_skill_index.py --verbose
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
DATA_DIR = REPO_ROOT / "maintainer" / "data"
DEFAULT_OUTPUT = DATA_DIR / "skill_index.json"
SCHEMA_VERSION = "0.2.0"
CATALOG_PATH = DATA_DIR / "skill_catalog.json"

# Import skill family mapping from evaluation scripts
sys.path.insert(0, str(REPO_ROOT / "maintainer" / "scripts" / "evaluation"))
from skill_protocol import SKILL_FAMILY


def _display_path(path: Path) -> str:
    """Render repo-relative output paths when possible."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def extract_frontmatter(skill_file: Path) -> dict[str, str | dict]:
    """Extract standards-compliant YAML frontmatter from a Skill package."""
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}
    data = yaml.safe_load("\n".join(lines[1:end])) or {}
    return data if isinstance(data, dict) else {}


def generate_skill_index(
    skills_dir: Path,
    *,
    verbose: bool = False,
    catalog_path: Path = CATALOG_PATH,
) -> dict:
    """Generate compact skill metadata index from SKILL.md files."""
    skills: list[dict] = []
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load Skill catalog: {exc}") from exc
    core = catalog.get("core_skill_names")
    optional = catalog.get("optional_skill_names")
    if not isinstance(core, list) or not isinstance(optional, list):
        raise ValueError("Skill catalog must define core_skill_names and optional_skill_names")
    active_names = set(core) | set(optional)

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            if verbose:
                print(f"  Skipping {skill_dir.name}: no SKILL.md found", file=sys.stderr)
            continue

        frontmatter = extract_frontmatter(skill_file)

        if not frontmatter or "name" not in frontmatter or "description" not in frontmatter:
            if verbose:
                print(f"  Warning: {skill_dir.name}/SKILL.md missing required frontmatter", file=sys.stderr)
            continue

        skill_name = frontmatter["name"]
        if skill_name not in active_names:
            continue

        # Get family classification from skill_protocol
        family = SKILL_FAMILY.get(skill_name)
        if family is None and skill_name == "artifact-review-loop":
            family = "execution"
        if family is None:
            raise ValueError(f"unknown Skill family for {skill_name!r}")

        # Build skill metadata entry
        skill_metadata = {
            "name": skill_name,
            "description": frontmatter["description"],
            "directory": f"skills/{skill_dir.name}",
            "family": family,
        }

        # Add optional metadata fields if present
        if isinstance(frontmatter.get("metadata"), dict):
            metadata = frontmatter["metadata"]
            if "version" in metadata:
                skill_metadata["version"] = metadata["version"]
            if "tags" in metadata:
                skill_metadata["tags"] = metadata["tags"].split(", ")

        skills.append(skill_metadata)

        if verbose:
            print(f"  Extracted: {skill_name} ({family} family)", file=sys.stderr)

    canonical_source = json.dumps(
        skills,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    # source_digest covers the normalized metadata used to build the index.
    # It is deliberately independent of output whitespace and wall-clock time.
    index = {
        "schema_version": SCHEMA_VERSION,
        "source_digest": hashlib.sha256(canonical_source).hexdigest(),
        "skills": skills,
    }

    return index


def format_json(data: dict, *, compact: bool = False) -> str:
    """Format JSON output with optional compactness."""
    if compact:
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate compact skill metadata index from SKILL.md files."
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output path for skill index (default: {DEFAULT_OUTPUT.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Generate compact JSON without indentation",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print extraction progress to stderr",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print to stdout instead of writing file",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the checked-in index differs from canonical Skill metadata",
    )
    args = parser.parse_args()

    if args.verbose:
        print(f"Extracting metadata from {SKILLS_DIR}", file=sys.stderr)

    try:
        index = generate_skill_index(SKILLS_DIR, verbose=args.verbose)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"\nGenerated index with {len(index['skills'])} skills", file=sys.stderr)

    output_json = format_json(index, compact=args.compact)

    if args.check:
        if args.dry_run:
            parser.error("--check and --dry-run are mutually exclusive")
        if not args.output.is_file():
            print(f"ERROR: skill index not found: {_display_path(args.output)}", file=sys.stderr)
            return 1
        expected = output_json + "\n"
        if args.output.read_text(encoding="utf-8") != expected:
            print(
                "ERROR: compact skill index is stale; run "
                "python3 maintainer/scripts/analysis/generate_skill_index.py",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {_display_path(args.output)} matches canonical Skill metadata")
    elif args.dry_run:
        print(output_json)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_json + "\n", encoding="utf-8")
        if args.verbose or True:  # Always report output location
            print(f"Wrote skill index to {_display_path(args.output)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
