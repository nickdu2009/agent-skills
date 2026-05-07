#!/usr/bin/env python3
"""Initialize a project knowledge-driven-development directory."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_ROOT = Path("docs/knowledge-driven-development")


FILES: dict[str, str] = {
    "README.md": """# Knowledge-Driven Development

This directory is the project knowledge root for agent-assisted development.

Start here before non-trivial work:

- Read `project/README.md` for shared knowledge categories.
- Read relevant documents under `project/`.
- Read `local/` only for current-developer environment, live systems, temporary scopes, or private notes.

`project/` is versioned shared knowledge. `local/` is developer-local and must stay ignored by version control.
""",
    "project/README.md": """# Project Knowledge

Shared knowledge in this directory should be reusable by all contributors.

Categories:

- `architecture/`: system boundaries, contracts, and data flow.
- `decisions/`: accepted tradeoffs and decision records.
- `runbooks/`: repeatable procedures.
- `integrations/`: external systems and API behavior.
- `validation/`: test and acceptance strategy.
- `glossary/`: terms and abbreviations.

Use `active-knowledge-log.md` for candidate knowledge before promotion.
""",
    "project/active-knowledge-log.md": """# Active Knowledge Log

Use this file for candidate shared knowledge before it is verified and promoted.
""",
    "local/README.md": """# Local Knowledge

This directory is for current-developer notes only. It must not enter version control.

Use it for:

- local environment details
- temporary live-system IDs
- personal debugging notes
- sensitive-context pointers without raw secrets

Do not store raw credentials.
""",
    "local/active-knowledge-log.md": """# Local Active Knowledge Log

Use this file for current-developer candidate knowledge that should stay out of version control.
""",
}


DIRECTORIES = (
    "project/architecture",
    "project/decisions",
    "project/runbooks",
    "project/integrations",
    "project/validation",
    "project/glossary",
    "local/notes",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Knowledge root to initialize.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes without writing files.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing template files.")
    parser.add_argument("--no-gitignore", action="store_true", help="Do not add the local knowledge path to .gitignore.")
    return parser.parse_args()


def write_file(path: Path, content: str, *, force: bool, dry_run: bool) -> None:
    if path.exists() and not force:
        print(f"skip existing file: {path}")
        return
    if dry_run:
        action = "overwrite" if path.exists() else "create"
        print(f"{action} file: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote file: {path}")


def ensure_directory(path: Path, *, dry_run: bool) -> None:
    if dry_run:
        print(f"ensure directory: {path}")
        return
    path.mkdir(parents=True, exist_ok=True)


def ensure_gitignore(root: Path, *, dry_run: bool) -> None:
    gitignore = Path(".gitignore")
    ignore_entry = f"{root.as_posix().rstrip('/')}/local/"
    existing = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.exists() else []
    if ignore_entry in existing:
        print(f"gitignore already contains: {ignore_entry}")
        return
    if dry_run:
        print(f"append to .gitignore: {ignore_entry}")
        return
    with gitignore.open("a", encoding="utf-8") as handle:
        if existing and existing[-1] != "":
            handle.write("\n")
        handle.write(f"{ignore_entry}\n")
    print(f"updated .gitignore: {ignore_entry}")


def main() -> int:
    args = parse_args()
    root: Path = args.root

    for directory in DIRECTORIES:
        ensure_directory(root / directory, dry_run=args.dry_run)
    for relative, content in FILES.items():
        write_file(root / relative, content, force=args.force, dry_run=args.dry_run)
    if not args.no_gitignore:
        ensure_gitignore(root, dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
