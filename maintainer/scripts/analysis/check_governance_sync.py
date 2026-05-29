#!/usr/bin/env python3
"""Lint governance sync between templates and root AGENTS.md / CLAUDE.md.

The repository contract treats ``templates/governance/*.md`` as the shared
governance source of truth. Repo-root ``AGENTS.md`` / ``CLAUDE.md`` may carry
small repo-only overlay blocks, but those overlays must be explicitly marked
and the remaining shared governance body must stay synchronized with the
templates.

This lint enforces four invariants:

1. ``AGENTS-template.md`` and ``CLAUDE-template.md`` define the same H2 set.
2. Root ``AGENTS.md`` and ``CLAUDE.md`` contain that H2 set in order.
3. After stripping repo-overlay blocks from the root files, every governance
   section body matches the corresponding template section body exactly.
4. Root ``AGENTS.md`` and ``CLAUDE.md`` remain identical mirrors.

Usage::

    python3 maintainer/scripts/analysis/check_governance_sync.py
    python3 maintainer/scripts/analysis/check_governance_sync.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_AGENTS = REPO_ROOT / "templates" / "governance" / "AGENTS-template.md"
TEMPLATE_CLAUDE = REPO_ROOT / "templates" / "governance" / "CLAUDE-template.md"
ROOT_AGENTS = REPO_ROOT / "AGENTS.md"
ROOT_CLAUDE = REPO_ROOT / "CLAUDE.md"
REPO_OVERLAY_CONTRACT_PREFIX = "<!-- Repo overlay contract:"
REPO_OVERLAY_START = "<!-- repo-overlay:start "
REPO_OVERLAY_END = "<!-- repo-overlay:end "


def extract_h2_from_text(text: str) -> list[str]:
    """Return ordered list of '## ...' headings in *text*."""
    headings: list[str] = []
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            headings.append(line[3:].strip())
    return headings


def extract_h2(path: Path) -> list[str]:
    if not path.exists():
        return []
    return extract_h2_from_text(path.read_text(encoding="utf-8"))


def extract_sections_from_text(text: str) -> dict[str, str]:
    """Return mapping of H2 section name -> full section body."""
    sections: dict[str, str] = {}
    current_section: str | None = None
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            if current_section is not None:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = line[3:].strip()
            current_lines = [line]
            continue
        if current_section is not None:
            current_lines.append(line)
    if current_section is not None:
        sections[current_section] = "\n".join(current_lines).strip()
    return sections


def normalize_text_block(text: str) -> str:
    """Normalize blank-line noise introduced by stripping overlay blocks."""
    normalized_lines: list[str] = []
    blank_run = 0
    for line in text.splitlines():
        stripped_line = line.rstrip()
        if stripped_line == "":
            blank_run += 1
            if blank_run > 1:
                continue
            normalized_lines.append("")
            continue
        blank_run = 0
        normalized_lines.append(stripped_line)
    return "\n".join(normalized_lines).strip()


def _parse_overlay_name(line: str, prefix: str) -> str:
    remainder = line.strip()[len(prefix):]
    if remainder.endswith("-->"):
        remainder = remainder[:-3]
    return remainder.strip()


def strip_repo_overlay(text: str) -> tuple[str, list[str]]:
    """Strip explicit repo-overlay blocks from root governance files."""
    issues: list[str] = []
    stripped_lines: list[str] = []
    current_overlay: str | None = None
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith(REPO_OVERLAY_CONTRACT_PREFIX):
            continue
        if stripped.startswith(REPO_OVERLAY_START):
            overlay_name = _parse_overlay_name(stripped, REPO_OVERLAY_START)
            if current_overlay is not None:
                issues.append(
                    f"nested repo-overlay start at line {line_no}: "
                    f"{overlay_name} inside {current_overlay}"
                )
            current_overlay = overlay_name
            continue
        if stripped.startswith(REPO_OVERLAY_END):
            overlay_name = _parse_overlay_name(stripped, REPO_OVERLAY_END)
            if current_overlay is None:
                issues.append(
                    f"repo-overlay end without start at line {line_no}: {overlay_name}"
                )
            elif current_overlay != overlay_name:
                issues.append(
                    f"repo-overlay end mismatch at line {line_no}: "
                    f"expected {current_overlay}, got {overlay_name}"
                )
                current_overlay = None
            else:
                current_overlay = None
            continue
        if current_overlay is not None:
            continue
        stripped_lines.append(line)
    if current_overlay is not None:
        issues.append(f"repo-overlay start without end: {current_overlay}")
    return ("\n".join(stripped_lines).strip() + "\n", issues)


def is_ordered_subsequence(needle: list[str], haystack: list[str]) -> tuple[bool, list[str]]:
    """Check if *needle* appears as an in-order subsequence of *haystack*.

    Returns ``(ok, missing)`` where *missing* lists template sections that did
    not appear in order. Ordering matters: each template section must appear at
    or after the position of the previous match.
    """
    pos = 0
    missing: list[str] = []
    for section in needle:
        try:
            idx = haystack.index(section, pos)
            pos = idx + 1
        except ValueError:
            missing.append(section)
    return (not missing, missing)


def check() -> dict[str, Any]:
    template_agents_text = TEMPLATE_AGENTS.read_text(encoding="utf-8") if TEMPLATE_AGENTS.exists() else ""
    template_claude_text = TEMPLATE_CLAUDE.read_text(encoding="utf-8") if TEMPLATE_CLAUDE.exists() else ""
    root_agents_text = ROOT_AGENTS.read_text(encoding="utf-8") if ROOT_AGENTS.exists() else ""
    root_claude_text = ROOT_CLAUDE.read_text(encoding="utf-8") if ROOT_CLAUDE.exists() else ""

    template_agents = extract_h2_from_text(template_agents_text)
    template_claude = extract_h2_from_text(template_claude_text)
    root_agents = extract_h2_from_text(root_agents_text)
    root_claude = extract_h2_from_text(root_claude_text)

    issues: list[str] = []

    if not TEMPLATE_AGENTS.exists():
        issues.append(f"missing template: {TEMPLATE_AGENTS.relative_to(REPO_ROOT)}")
    if not TEMPLATE_CLAUDE.exists():
        issues.append(f"missing template: {TEMPLATE_CLAUDE.relative_to(REPO_ROOT)}")
    if not ROOT_AGENTS.exists():
        issues.append("missing root AGENTS.md")
    if not ROOT_CLAUDE.exists():
        issues.append("missing root CLAUDE.md")

    # Invariant 1: template mirror parity
    if template_agents != template_claude:
        issues.append(
            "template H2 mismatch between AGENTS-template.md and CLAUDE-template.md: "
            f"agents={template_agents} claude={template_claude}"
        )

    # Invariant 2a: template ⊆ root AGENTS.md (in order)
    ok, missing = is_ordered_subsequence(template_agents, root_agents)
    if not ok:
        issues.append(
            "AGENTS.md is missing template sections (in order): " + ", ".join(missing)
        )

    # Invariant 2b: template ⊆ root CLAUDE.md (in order)
    ok, missing = is_ordered_subsequence(template_claude, root_claude)
    if not ok:
        issues.append(
            "CLAUDE.md is missing template sections (in order): " + ", ".join(missing)
        )

    # Invariant 3: shared governance body matches template after stripping
    # explicit repo-only overlay blocks from root files.
    if ROOT_AGENTS.exists():
        stripped_root_agents, overlay_issues = strip_repo_overlay(root_agents_text)
        issues.extend(f"AGENTS.md {issue}" for issue in overlay_issues)
        template_sections = extract_sections_from_text(template_agents_text)
        root_sections = extract_sections_from_text(stripped_root_agents)
        for section_name, template_body in template_sections.items():
            root_body = root_sections.get(section_name)
            if root_body is None:
                issues.append(f"AGENTS.md missing section body after overlay stripping: {section_name}")
                continue
            if normalize_text_block(root_body) != normalize_text_block(template_body):
                issues.append(
                    f"AGENTS.md section body diverged from template: {section_name}"
                )

    if ROOT_CLAUDE.exists():
        stripped_root_claude, overlay_issues = strip_repo_overlay(root_claude_text)
        issues.extend(f"CLAUDE.md {issue}" for issue in overlay_issues)
        template_sections = extract_sections_from_text(template_claude_text)
        root_sections = extract_sections_from_text(stripped_root_claude)
        for section_name, template_body in template_sections.items():
            root_body = root_sections.get(section_name)
            if root_body is None:
                issues.append(f"CLAUDE.md missing section body after overlay stripping: {section_name}")
                continue
            if normalize_text_block(root_body) != normalize_text_block(template_body):
                issues.append(
                    f"CLAUDE.md section body diverged from template: {section_name}"
                )

    # Invariant 4: root AGENTS.md == root CLAUDE.md verbatim.
    if ROOT_AGENTS.exists() and ROOT_CLAUDE.exists():
        if root_agents_text != root_claude_text:
            issues.append("root AGENTS.md and CLAUDE.md content diverged (mirror drift)")

    return {
        "ok": not issues,
        "issues": issues,
        "template_sections": template_agents,
        "agents_sections": root_agents,
        "claude_sections": root_claude,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lint governance sync between templates and root AGENTS.md / CLAUDE.md"
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    result = check()

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["ok"] else 1)

    print("=" * 80)
    print("Governance Sync Check")
    print("=" * 80)
    print()
    print(f"Template sections ({len(result['template_sections'])}):")
    for section in result["template_sections"]:
        print(f"  - {section}")
    print()
    print(f"Root AGENTS.md sections ({len(result['agents_sections'])}):")
    for section in result["agents_sections"]:
        print(f"  - {section}")
    print()
    print(f"Root CLAUDE.md sections ({len(result['claude_sections'])}):")
    for section in result["claude_sections"]:
        print(f"  - {section}")
    print()

    if result["ok"]:
        print("✓ Governance sync OK")
        sys.exit(0)

    print(f"✗ {len(result['issues'])} issue(s):")
    for issue in result["issues"]:
        print(f"  - {issue}")
    sys.exit(1)


if __name__ == "__main__":
    main()
