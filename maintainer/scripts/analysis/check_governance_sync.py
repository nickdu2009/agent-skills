#!/usr/bin/env python3
"""Lint governance sync between templates and rendered AGENTS.md / CLAUDE.md.

The repository contract (AGENTS.md §Behavioral Guidelines §3 + Governance Chain
Trigger Fix Plan) treats ``templates/governance/AGENTS-template.md`` as the
source of truth for the governance section list. The repo-root ``AGENTS.md``
and ``CLAUDE.md`` may add project-specific content but must contain every H2
section the template defines, in the same order.

This lint enforces three invariants:

1. ``AGENTS-template.md`` and ``CLAUDE-template.md`` define the same H2 set
   (they are documented as byte-mirrors with different headers).
2. The H2 set of the template is a contiguous, in-order subsequence of the
   root ``AGENTS.md`` and ``CLAUDE.md`` H2 set.
3. Root ``AGENTS.md`` and ``CLAUDE.md`` have identical content (mirror).

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


def extract_h2(path: Path) -> list[str]:
    """Return ordered list of '## ...' headings in *path*."""
    if not path.exists():
        return []
    headings: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            headings.append(line[3:].strip())
    return headings


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
    template_agents = extract_h2(TEMPLATE_AGENTS)
    template_claude = extract_h2(TEMPLATE_CLAUDE)
    root_agents = extract_h2(ROOT_AGENTS)
    root_claude = extract_h2(ROOT_CLAUDE)

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

    # Invariant 3: AGENTS.md == CLAUDE.md (after stripping the leading H1).
    # We compare the whole file body so any drift (typo, missing bullet) is
    # caught even if the H2 set still matches.
    if ROOT_AGENTS.exists() and ROOT_CLAUDE.exists():
        agents_body = ROOT_AGENTS.read_text(encoding="utf-8")
        claude_body = ROOT_CLAUDE.read_text(encoding="utf-8")
        if agents_body != claude_body:
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
