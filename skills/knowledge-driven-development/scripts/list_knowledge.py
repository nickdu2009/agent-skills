#!/usr/bin/env python3
"""Search project knowledge Markdown files with lightweight local matching."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_ROOT = Path("docs/knowledge-driven-development")
VALID_SCOPES = ("project", "local", "all")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Knowledge root.")
    parser.add_argument("--query", required=True, help="Case-insensitive search query.")
    parser.add_argument("--scope", choices=VALID_SCOPES, default="project", help="Search scope.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum matches to print.")
    return parser.parse_args()


def scope_roots(root: Path, scope: str) -> list[Path]:
    if scope == "all":
        return [root / "project", root / "local"]
    return [root / scope]


def heading_for(lines: list[str], index: int) -> str:
    for line in reversed(lines[: index + 1]):
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return "(no heading)"


def main() -> int:
    args = parse_args()
    query = args.query.lower()
    count = 0

    for scope_root in scope_roots(args.root, args.scope):
        if not scope_root.exists():
            continue
        for path in sorted(scope_root.rglob("*.md")):
            lines = path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines):
                if query in line.lower():
                    print(f"{path}:{index + 1}: {heading_for(lines, index)}")
                    print(f"  {line.strip()}")
                    count += 1
                    if count >= args.limit:
                        return 0
                    break

    if count == 0:
        print("No knowledge matches found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
