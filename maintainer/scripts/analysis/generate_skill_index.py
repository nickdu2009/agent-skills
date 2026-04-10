#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Generate compact skill metadata index from SKILL.md files.

This script extracts minimal metadata from SKILL.md frontmatter and generates
a compact JSON index for use in evaluation and testing workflows.

Purpose:
  - Reduce token usage in trigger evaluation prompts (60-80% reduction)
  - Provide fast skill metadata lookup without parsing full SKILL.md files
  - Enable efficient skill categorization and family classification

Input:
  - SKILL.md files in skills/ directory (frontmatter with name, description, metadata)
  - skill_protocol_v1.py (for family classification)

Output:
  - maintainer/data/skill_index.json (compact metadata index)

Usage:
  python3 maintainer/scripts/analysis/generate_skill_index.py
  python3 maintainer/scripts/analysis/generate_skill_index.py --output /path/to/output.json
  python3 maintainer/scripts/analysis/generate_skill_index.py --verbose
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
DATA_DIR = REPO_ROOT / "maintainer" / "data"
DEFAULT_OUTPUT = DATA_DIR / "skill_index.json"

# Import skill family mapping from evaluation scripts
sys.path.insert(0, str(REPO_ROOT / "maintainer" / "scripts" / "evaluation"))
from skill_protocol_v1 import SKILL_FAMILY


def extract_frontmatter(skill_file: Path) -> dict[str, str | dict]:
    """Extract YAML frontmatter from SKILL.md file.

    Returns dict with fields: name, description, metadata (if present)
    """
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        return {}

    frontmatter_lines: list[str] = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if i == 0:
            in_frontmatter = True
            continue
        if line.strip() == "---":
            break
        if in_frontmatter:
            frontmatter_lines.append(line)

    # Parse frontmatter manually (simple YAML subset)
    result: dict[str, str | dict] = {}
    current_key = None
    current_value_lines: list[str] = []
    in_metadata = False
    metadata: dict[str, str] = {}

    for line in frontmatter_lines:
        if line.startswith("metadata:"):
            in_metadata = True
            if current_key:
                result[current_key] = " ".join(current_value_lines).strip()
            current_key = None
            current_value_lines = []
            continue

        if in_metadata:
            # Parse metadata fields (simple key: "value" format)
            if line.strip().startswith("version:") or line.strip().startswith("tags:"):
                key_part, _, value_part = line.partition(":")
                key = key_part.strip()
                value = value_part.strip().strip('"')
                metadata[key] = value
            continue

        if line.startswith(" ") or line.startswith("\t"):
            # Continuation of previous value
            current_value_lines.append(line.strip())
        else:
            # New key
            if current_key:
                result[current_key] = " ".join(current_value_lines).strip()

            key_part, _, value_part = line.partition(":")
            current_key = key_part.strip()
            current_value_lines = [value_part.strip()]

    # Handle last key
    if current_key:
        result[current_key] = " ".join(current_value_lines).strip()

    if metadata:
        result["metadata"] = metadata

    return result


def generate_skill_index(skills_dir: Path, *, verbose: bool = False) -> dict:
    """Generate compact skill metadata index from SKILL.md files."""
    skills: list[dict] = []

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

        # Get family classification from skill_protocol_v1
        family = SKILL_FAMILY.get(skill_name, "unknown")

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

    # Build index
    index = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
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
    args = parser.parse_args()

    if args.verbose:
        print(f"Extracting metadata from {SKILLS_DIR}", file=sys.stderr)

    index = generate_skill_index(SKILLS_DIR, verbose=args.verbose)

    if args.verbose:
        print(f"\nGenerated index with {len(index['skills'])} skills", file=sys.stderr)

    output_json = format_json(index, compact=args.compact)

    if args.dry_run:
        print(output_json)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_json + "\n", encoding="utf-8")
        if args.verbose or True:  # Always report output location
            print(f"Wrote skill index to {args.output.relative_to(REPO_ROOT)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
