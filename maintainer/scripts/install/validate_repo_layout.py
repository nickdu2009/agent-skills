#!/usr/bin/env python3
"""Fail fast when non-skill repository layout drifts from documented boundaries.

Uses git for the repository root allowlist so local gitignored directories do not
create false positives. Root entries are derived from `git ls-files` (the index),
so `git add` your layout changes before expecting a clean local run. Still checks
the filesystem for forbidden legacy paths.

Run from repo root:
  python3 maintainer/scripts/install/validate_repo_layout.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

# Top-level tracked names (git ls-tree --name-only HEAD). .git is never listed.
ALLOWED_TOP_LEVEL_NAMES = frozenset({
    ".github",
    "skills",
    "examples",
    "templates",
    "docs",
    "maintainer",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "SECURITY.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".gitignore",
    "phase-toolchain-optimization-zh.md",
})

REQUIRED_TOP_LEVEL_NAMES = frozenset({
    "skills",
    "examples",
    "templates",
    "docs",
    "maintainer",
})

REQUIRED_INSTALL_FILES = (
    REPO_ROOT / "maintainer" / "scripts" / "install" / "manage-governance.py",
    REPO_ROOT / "maintainer" / "scripts" / "install" / "validate_repo_layout.py",
)


def err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def git_top_level_names() -> set[str]:
    r = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "git ls-files failed")
    roots: set[str] = set()
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        roots.add(line.split("/", 1)[0])
    return roots


def require_exact_subdirs(parent: Path, expected: frozenset[str], label: str) -> list[str]:
    issues: list[str] = []
    if not parent.is_dir():
        issues.append(f"missing directory: {parent.relative_to(REPO_ROOT)}")
        return issues
    actual = {p.name for p in parent.iterdir() if p.is_dir()}
    for name in sorted(expected - actual):
        issues.append(f"{label}: missing subdirectory {name}/")
    for name in sorted(actual - expected):
        issues.append(f"{label}: unexpected subdirectory {name}/")
    return issues


def main() -> int:
    issues: list[str] = []

    try:
        tracked = git_top_level_names()
    except RuntimeError as exc:
        err(str(exc))
        return 1

    for name in sorted(tracked):
        if name not in ALLOWED_TOP_LEVEL_NAMES:
            issues.append(f"unexpected top-level tracked entry: {name}")
    for name in sorted(REQUIRED_TOP_LEVEL_NAMES):
        if name not in tracked:
            issues.append(f"missing required top-level tracked entry: {name}")

    for required in ("skills", "examples", "templates", "docs", "maintainer"):
        p = REPO_ROOT / required
        if not p.is_dir():
            issues.append(f"missing required directory on disk: {required}/")

    issues.extend(
        require_exact_subdirs(
            REPO_ROOT / "docs",
            frozenset({"user", "maintainer"}),
            "docs/",
        )
    )
    issues.extend(
        require_exact_subdirs(
            REPO_ROOT / "templates",
            frozenset({"governance", "evaluation"}),
            "templates/",
        )
    )
    issues.extend(
        require_exact_subdirs(
            REPO_ROOT / "maintainer" / "scripts",
            frozenset({"install", "evaluation"}),
            "maintainer/scripts/",
        )
    )
    issues.extend(
        require_exact_subdirs(
            REPO_ROOT / "maintainer" / "reports",
            frozenset({"baselines", "runs"}),
            "maintainer/reports/",
        )
    )

    forbidden_roots = (
        REPO_ROOT / "scripts",
        REPO_ROOT / "reports",
    )
    for p in forbidden_roots:
        if p.exists():
            issues.append(
                f"forbidden path exists (use maintainer/ instead): {p.relative_to(REPO_ROOT)}/"
            )

    for f in REQUIRED_INSTALL_FILES:
        if not f.is_file():
            issues.append(f"missing required file: {f.relative_to(REPO_ROOT)}")

    gitkeep = REPO_ROOT / "maintainer" / "reports" / "runs" / ".gitkeep"
    if not gitkeep.is_file():
        issues.append("maintainer/reports/runs/.gitkeep must exist to anchor the runs directory")

    if issues:
        for line in issues:
            err(line)
        return 1

    print("OK: repository layout matches enforced boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
