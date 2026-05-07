#!/usr/bin/env python3
"""Append a knowledge entry to a project or local active knowledge log."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


DEFAULT_ROOT = Path("docs/knowledge-driven-development")
VALID_SCOPES = ("project", "local")
VALID_STATUSES = ("candidate", "verified", "deprecated", "contradicted")
VALID_EVIDENCE = (
    "Source Code Verified",
    "Live Environment Verified",
    "Test Verified",
    "User Confirmed",
    "Pending Verification",
)

SECRET_PATTERNS = (
    re.compile(r"(?i)(api[-_ ]?key|secret|token|cookie|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-./+=]{12,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-./+=]{12,}"),
    re.compile(r"(?i)(dsn|database_url)\s*[:=]\s*['\"]?[^\s]+"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Knowledge root.")
    parser.add_argument("--scope", choices=VALID_SCOPES, required=True, help="Knowledge scope.")
    parser.add_argument("--title", required=True, help="Short entry title.")
    parser.add_argument("--evidence", choices=VALID_EVIDENCE, default="Pending Verification", help="Evidence label.")
    parser.add_argument("--status", choices=VALID_STATUSES, default="candidate", help="Entry status.")
    parser.add_argument("--source", action="append", default=[], help="Evidence source. May be repeated.")
    parser.add_argument("--conclusion", required=True, help="Executable conclusion.")
    parser.add_argument("--impact", required=True, help="Development impact.")
    parser.add_argument("--dry-run", action="store_true", help="Print the entry without writing.")
    return parser.parse_args()


def contains_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def render_entry(args: argparse.Namespace) -> str:
    sources = args.source or ["Pending source"]
    source_lines = "\n".join(f"  - {source}" for source in sources)
    return f"""
## {args.title}

- Scope: {args.scope}
- Status: {args.status}
- Evidence: {args.evidence}
- Last verified: {date.today().isoformat()}
- Source:
{source_lines}
- Conclusion:
  - {args.conclusion}
- Development impact:
  - {args.impact}
"""


def main() -> int:
    args = parse_args()
    entry = render_entry(args)

    if args.scope == "project" and contains_secret(entry):
        raise SystemExit(
            "Refusing to write likely secret material to project knowledge. "
            "Use variable names or sanitized descriptions instead."
        )

    log_path = args.root / args.scope / "active-knowledge-log.md"
    if args.dry_run:
        print(entry.strip())
        return 0

    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("# Active Knowledge Log\n", encoding="utf-8")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    print(f"appended knowledge entry to {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
