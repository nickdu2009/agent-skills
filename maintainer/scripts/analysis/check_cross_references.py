#!/usr/bin/env python3
"""Check cross-reference integrity across documentation.

This script validates:
1. All skill chain aliases referenced in skill-chain-aliases.md exist as skills
2. All skill references in SKILL.md files point to valid skills
3. All documentation cross-references resolve correctly

Usage:
    python3 maintainer/scripts/analysis/check_cross_references.py
    python3 maintainer/scripts/analysis/check_cross_references.py --json
    python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
DOCS_MAINTAINER_DIR = REPO_ROOT / "docs" / "maintainer"
SKILL_CHAIN_ALIASES = DOCS_MAINTAINER_DIR / "skill-chain-aliases.md"

MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REPO_PATH_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_.-])"
    r"((?:docs|examples|maintainer|skills|templates)/"
    r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\."
    r"(?:md|py|json|ya?ml|txt|sh|go|tsx?))"
)
REFERENCE_HEADING_PATTERN = re.compile(
    r"^#{1,6}\s+(?:cross[- ]references|references|related (?:documents|files|resources)|see also)\s*$",
    re.IGNORECASE,
)

# Non-skill terms that look like skill names but aren't (field names, placeholders, etc.)
NON_SKILL_TERMS = {
    "re-reads",            # Field name in context discipline
    "best-of-n-runner",    # Subagent type in multi-agent-protocol
    "low-risk",            # Review severity label, not a skill
    "review-only",         # artifact review mode, not a skill
    "review-and-revise",   # artifact review mode, not a skill
    "adr-rfc",             # artifact subtype, not a skill
    "data-model",          # artifact subtype, not a skill
    "technical-proposal",  # artifact subtype, not a skill
    "self-delivery",       # artifact-review-loop context, not a skill
    "current-agent-task",  # trusted provenance value, not a skill
    "user-or-external",    # provenance value, not a skill
    "current-task-diff",   # bounded write scope, not a skill
}


def get_valid_skills() -> set[str]:
    """Return set of valid skill names from skills directory."""
    valid_skills = set()
    if not SKILLS_DIR.exists():
        return valid_skills

    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            valid_skills.add(skill_dir.name)

    return valid_skills


def get_valid_chain_aliases() -> set[str]:
    """Extract valid chain alias names from skill-chain-aliases.md.

    Returns canonical chain names like bugfix-standard, refactor-safe, etc.
    """
    if not SKILL_CHAIN_ALIASES.exists():
        return set()

    content = SKILL_CHAIN_ALIASES.read_text(encoding="utf-8")
    aliases = set()

    # Pattern: Look for h3 headers (### name) in the "Canonical Chain Definitions" section
    in_canonical_section = False
    for line in content.splitlines():
        if "## Canonical Chain Definitions" in line:
            in_canonical_section = True
            continue
        if in_canonical_section and line.startswith("## "):
            # End of canonical section
            break
        if in_canonical_section and line.startswith("### "):
            # Extract alias name
            alias_name = line.replace("###", "").strip()
            if alias_name:
                aliases.add(alias_name)

    return aliases


def extract_skill_references(text: str, *, exclude_avoid_sections: bool = False, exclude_naming_examples: bool = False) -> set[str]:
    """Extract skill name references from text.

    Matches patterns like:
    - `skill-name` (backticked)
    - skill-name (in chain arrows like → skill-name →)

    Args:
        text: Text to search
        exclude_avoid_sections: If True, skip references in "Avoid:" sections
        exclude_naming_examples: If True, skip references in naming convention examples
    """
    references = set()

    # If requested, remove "Avoid:" sections before extraction
    search_text = text
    if exclude_avoid_sections:
        # Remove content between "Avoid:" and next section header
        search_text = re.sub(
            r"Avoid:.*?(?=\n##|\Z)",
            "",
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

    # If requested, remove naming convention example sections
    if exclude_naming_examples:
        # Remove lines with "e.g." which are usually examples, not actual references
        search_text = re.sub(
            r"^.*\(e\.g\.,.*\).*$",
            "",
            search_text,
            flags=re.MULTILINE
        )

    # Pattern 1: backticked skill names (common in documentation)
    backtick_pattern = r"`([a-z][a-z0-9-]+)`"
    for match in re.finditer(backtick_pattern, search_text):
        candidate = match.group(1)
        # Filter to likely skill names (contain hyphens, reasonable length)
        if "-" in candidate and 5 <= len(candidate) <= 40:
            references.add(candidate)

    # Pattern 2: skill names in chain arrows (→ skill-name →)
    arrow_pattern = r"→\s*([a-z][a-z0-9-]+)\s*(?:→|$|\+)"
    for match in re.finditer(arrow_pattern, search_text):
        candidate = match.group(1)
        if "-" in candidate and 5 <= len(candidate) <= 40:
            references.add(candidate)

    # Pattern 3: skill names after "Combine with:" or similar composition sections
    composition_pattern = r"(?:Combine with|Escalate to|Handoff to|Load|Activate).*?:\s*\n((?:\s*-\s*`[^`]+`\s*\n)+)"
    for match in re.finditer(composition_pattern, search_text, re.IGNORECASE | re.MULTILINE):
        section = match.group(1)
        for skill_match in re.finditer(r"`([a-z][a-z0-9-]+)`", section):
            candidate = skill_match.group(1)
            if "-" in candidate and 5 <= len(candidate) <= 40:
                references.add(candidate)

    return references


def check_skill_chain_aliases() -> dict[str, Any]:
    """Check that all skills mentioned in skill-chain-aliases.md exist."""
    if not SKILL_CHAIN_ALIASES.exists():
        return {
            "file": str(SKILL_CHAIN_ALIASES.relative_to(REPO_ROOT)),
            "exists": False,
            "broken_references": [],
            "note": "File not found",
        }

    valid_skills = get_valid_skills()
    valid_aliases = get_valid_chain_aliases()
    content = SKILL_CHAIN_ALIASES.read_text(encoding="utf-8")

    # Extract references but exclude "Avoid:" sections and naming convention examples
    referenced_skills = extract_skill_references(
        content,
        exclude_avoid_sections=True,
        exclude_naming_examples=True
    )

    broken_refs = []
    for skill_ref in sorted(referenced_skills):
        if skill_ref in NON_SKILL_TERMS:
            continue
        # Skip if it's a known chain alias (not a skill)
        if skill_ref in valid_aliases:
            continue
        if skill_ref not in valid_skills:
            broken_refs.append({
                "reference": skill_ref,
                "context": "skill-chain-aliases.md",
            })

    return {
        "file": str(SKILL_CHAIN_ALIASES.relative_to(REPO_ROOT)),
        "exists": True,
        "total_references": len(referenced_skills),
        "valid_chain_aliases": sorted(valid_aliases),
        "broken_references": broken_refs,
        "broken_count": len(broken_refs),
    }


def check_skill_md_references() -> dict[str, Any]:
    """Check that all skill references in SKILL.md files point to valid skills."""
    valid_skills = get_valid_skills()
    valid_aliases = get_valid_chain_aliases()
    all_broken_refs = []

    if not SKILLS_DIR.exists():
        return {
            "skills_dir": str(SKILLS_DIR),
            "exists": False,
            "broken_references": [],
            "note": "Skills directory not found",
        }

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8")
        referenced_skills = extract_skill_references(content)

        for skill_ref in referenced_skills:
            # Skip self-references
            if skill_ref == skill_dir.name:
                continue

            # Skip if it's a known chain alias
            if skill_ref in valid_aliases:
                continue

            # Skip non-skill terms (field names, status values, etc.)
            if skill_ref in NON_SKILL_TERMS:
                continue

            if skill_ref not in valid_skills:
                all_broken_refs.append({
                    "reference": skill_ref,
                    "context": f"{skill_dir.name}/SKILL.md",
                    "source_skill": skill_dir.name,
                })

    return {
        "skills_dir": str(SKILLS_DIR.relative_to(REPO_ROOT)),
        "exists": True,
        "skills_checked": len(list(SKILLS_DIR.glob("*/SKILL.md"))),
        "broken_references": all_broken_refs,
        "broken_count": len(all_broken_refs),
    }


def tracked_markdown_files() -> list[Path]:
    """Return existing tracked Markdown files, with an archive fallback."""
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z"],
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        paths = []
        for raw_path in result.stdout.decode("utf-8").split("\0"):
            path = REPO_ROOT / raw_path
            if raw_path.endswith(".md") and path.is_file():
                paths.append(path)
        return sorted(paths)

    roots = [REPO_ROOT / name for name in ("docs", "examples", "maintainer", "skills", "templates")]
    paths = [path for root in roots if root.exists() for path in root.rglob("*.md")]
    paths.extend(path for path in REPO_ROOT.glob("*.md") if path.is_file())
    return sorted(set(paths))


def markdown_link_target(payload: str) -> str:
    """Remove an optional Markdown title from a link payload."""
    payload = payload.strip()
    if payload.startswith("<") and ">" in payload:
        return payload[1:payload.index(">")]
    return payload.split(maxsplit=1)[0] if payload else ""


def is_external_or_placeholder(target: str) -> bool:
    """Return whether a target is intentionally outside repository validation."""
    lowered = target.lower()
    return (
        not target
        or target.startswith("#")
        or lowered.startswith(("http://", "https://", "mailto:", "data:"))
        or any(marker in target for marker in ("{", "}", "*", "$"))
    )


def resolve_doc_target(source: Path, target: str, *, repo_relative: bool) -> Path | None:
    """Resolve a documentation target, returning None for external placeholders."""
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if is_external_or_placeholder(target):
        return None
    if target.startswith("/") or repo_relative:
        return REPO_ROOT / target.lstrip("/")
    return source.parent / target


def check_doc_file_references() -> dict[str, Any]:
    """Check live Markdown links and explicit paths in reference sections."""
    broken_refs: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    files = tracked_markdown_files()

    for source in files:
        content = source.read_text(encoding="utf-8")
        candidates: list[tuple[str, int, bool]] = []
        in_fence = False
        in_reference_section = False
        for line_number, line_text in enumerate(content.splitlines(), start=1):
            stripped = line_text.strip()
            if stripped.startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if stripped.startswith("#"):
                in_reference_section = bool(REFERENCE_HEADING_PATTERN.match(stripped))

            for match in MARKDOWN_LINK_PATTERN.finditer(line_text):
                candidates.append((markdown_link_target(match.group(1)), line_number, False))
            if in_reference_section:
                for match in REPO_PATH_PATTERN.finditer(line_text):
                    candidates.append((match.group(1), line_number, True))

        for target, line, repo_relative in candidates:
            resolved = resolve_doc_target(source, target, repo_relative=repo_relative)
            if resolved is None or resolved.exists():
                continue
            context = str(source.relative_to(REPO_ROOT))
            key = (context, line, target)
            if key in seen:
                continue
            seen.add(key)
            try:
                expected = str(resolved.resolve().relative_to(REPO_ROOT.resolve()))
            except ValueError:
                expected = str(resolved.resolve())
            broken_refs.append({
                "reference": target,
                "context": f"{context}:{line}",
                "expected_path": expected,
            })

    return {
        "files_checked": len(files),
        "broken_references": broken_refs,
        "broken_count": len(broken_refs),
    }


def main() -> int:
    """Run all cross-reference checks and report results."""
    parser = argparse.ArgumentParser(
        description="Check cross-reference integrity across documentation"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of human-readable format",
    )
    parser.add_argument(
        "--fail-on-broken",
        action="store_true",
        help="Exit with non-zero status if broken references are found",
    )
    args = parser.parse_args()

    results = {
        "timestamp": "2026-04-11",
        "valid_skills": sorted(get_valid_skills()),
        "skill_chain_aliases": check_skill_chain_aliases(),
        "skill_md_references": check_skill_md_references(),
        "doc_file_references": check_doc_file_references(),
    }

    # Calculate total broken references
    total_broken = (
        results["skill_chain_aliases"]["broken_count"]
        + results["skill_md_references"]["broken_count"]
        + results["doc_file_references"]["broken_count"]
    )

    results["summary"] = {
        "total_broken_references": total_broken,
        "status": "pass" if total_broken == 0 else "fail",
    }

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 80)
        print("Cross-Reference Integrity Check")
        print("=" * 80)
        print()

        print(f"Valid skills found: {len(results['valid_skills'])}")
        print()

        # Skill chain aliases check
        sca = results["skill_chain_aliases"]
        if sca["exists"]:
            print(f"Skill Chain Aliases ({sca['file']}):")
            print(f"  Total references: {sca['total_references']}")
            print(f"  Broken references: {sca['broken_count']}")
            if sca["broken_references"]:
                for ref in sca["broken_references"]:
                    print(f"    ✗ {ref['reference']}")
            else:
                print("    ✓ All references valid")
        else:
            print(f"Skill Chain Aliases: {sca['note']}")
        print()

        # SKILL.md references check
        skr = results["skill_md_references"]
        if skr["exists"]:
            print(f"SKILL.md References ({skr['skills_checked']} files checked):")
            print(f"  Broken references: {skr['broken_count']}")
            if skr["broken_references"]:
                for ref in skr["broken_references"]:
                    print(f"    ✗ {ref['reference']} (in {ref['context']})")
            else:
                print("    ✓ All references valid")
        else:
            print(f"SKILL.md References: {skr['note']}")
        print()

        # Doc file references check
        dfr = results["doc_file_references"]
        print("Documentation File References:")
        print(f"  Broken references: {dfr['broken_count']}")
        if dfr["broken_references"]:
            for ref in dfr["broken_references"]:
                print(f"    ✗ {ref['reference']} (in {ref['context']}) -> {ref['expected_path']}")
        else:
            print("    ✓ All references valid")
        print()

        # Summary
        print("=" * 80)
        status_icon = "✓" if total_broken == 0 else "✗"
        print(f"{status_icon} Summary: {total_broken} broken reference(s) found")
        print("=" * 80)

    if args.fail_on_broken and total_broken > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
