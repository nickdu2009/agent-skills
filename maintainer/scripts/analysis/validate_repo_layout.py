#!/usr/bin/env python3
"""Fail fast when repository layout drifts from documented boundaries.

Uses git for the repository root allowlist so local ignored or untracked
directories do not create false positives. Deleted tracked paths are filtered
through the current working tree, so validation does not require staging.

Run from repo root:
  python3 maintainer/scripts/analysis/validate_repo_layout.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

ALLOWED_TOP_LEVEL_NAMES = frozenset({
    ".github",
    ".env.example",
    "skills",
    "examples",
    "templates",
    "docs",
    "maintainer",
    "README.md",
    "CHANGELOG.md",
    "CHANGELOG-trigger-optimization.md",
    "LICENSE",
    "SECURITY.md",
    "AGENTS.md",
    "Makefile",
    ".gitignore",
    "phase-toolchain-optimization-zh.md",
    "scripts",
})

REQUIRED_TOP_LEVEL_NAMES = frozenset({
    "skills",
    "examples",
    "templates",
    "docs",
    "maintainer",
})

REQUIRED_ANALYSIS_FILES = (
    REPO_ROOT / "maintainer" / "scripts" / "analysis" / "validate_repo_layout.py",
    REPO_ROOT / "maintainer" / "scripts" / "analysis" / "validate_agent_skills.py",
)

FORBIDDEN_ADAPTER_ROOTS = (
    REPO_ROOT / "maintainer" / "runtime-adapters",
    REPO_ROOT / "maintainer" / "client-adapters",
    REPO_ROOT / "templates" / "governance",
)

def err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def git_top_level_names() -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")

    roots: set[str] = set()
    for line in result.stdout.splitlines():
        line = line.strip()
        if line and (REPO_ROOT / line).exists():
            roots.add(line.split("/", 1)[0])
    return roots


def tracked_existing_files(pathspec: str) -> set[str]:
    """Return tracked files in a pathspec that still exist in the working tree."""
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", pathspec],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return {
        line
        for line in result.stdout.splitlines()
        if line and (REPO_ROOT / line).is_file()
    }


def require_exact_subdirs(parent: Path, expected: frozenset[str], label: str) -> list[str]:
    if not parent.is_dir():
        return [f"missing directory: {parent.relative_to(REPO_ROOT)}"]
    actual = {path.name for path in parent.iterdir() if path.is_dir()}
    issues = [f"{label}: missing subdirectory {name}/" for name in sorted(expected - actual)]
    issues.extend(
        f"{label}: unexpected subdirectory {name}/" for name in sorted(actual - expected)
    )
    return issues


def main() -> int:
    issues: list[str] = []
    try:
        tracked = git_top_level_names()
    except RuntimeError as exc:
        err(str(exc))
        return 1

    issues.extend(
        f"unexpected top-level tracked entry: {name}"
        for name in sorted(tracked - ALLOWED_TOP_LEVEL_NAMES)
    )
    issues.extend(
        f"missing required top-level tracked entry: {name}"
        for name in sorted(REQUIRED_TOP_LEVEL_NAMES - tracked)
    )

    for required in REQUIRED_TOP_LEVEL_NAMES:
        if not (REPO_ROOT / required).is_dir():
            issues.append(f"missing required directory on disk: {required}/")

    issues.extend(
        require_exact_subdirs(
            REPO_ROOT / "docs",
            frozenset({"manual", "user", "maintainer"}),
            "docs/",
        )
    )
    issues.extend(
        require_exact_subdirs(
            REPO_ROOT / "templates",
            frozenset({"evaluation"}),
            "templates/",
        )
    )
    issues.extend(
        require_exact_subdirs(
            REPO_ROOT / "maintainer" / "scripts",
            frozenset({"analysis", "audit", "evaluation"}),
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

    if (REPO_ROOT / "reports").exists():
        issues.append("forbidden path exists (use maintainer/ instead): reports/")

    for required_file in REQUIRED_ANALYSIS_FILES:
        if not required_file.is_file():
            issues.append(f"missing required file: {required_file.relative_to(REPO_ROOT)}")

    for forbidden_root in FORBIDDEN_ADAPTER_ROOTS:
        if forbidden_root.exists():
            issues.append(f"forbidden runtime-adapter path exists: {forbidden_root.relative_to(REPO_ROOT)}")

    for skill_dir in sorted((REPO_ROOT / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        agents_dir = skill_dir / "agents"
        if agents_dir.exists():
            issues.append(f"forbidden runtime-specific Skill sidecar directory exists: {agents_dir.relative_to(REPO_ROOT)}")

    gitkeep = REPO_ROOT / "maintainer" / "reports" / "runs" / ".gitkeep"
    if not gitkeep.is_file():
        issues.append("maintainer/reports/runs/.gitkeep must exist to anchor the runs directory")

    try:
        tracked_runs = tracked_existing_files("maintainer/reports/runs")
    except RuntimeError as exc:
        issues.append(str(exc))
    else:
        unexpected_runs = tracked_runs - {"maintainer/reports/runs/.gitkeep"}
        issues.extend(
            f"tracked run artifact must not be committed: {path}"
            for path in sorted(unexpected_runs)
        )

    if issues:
        for issue in issues:
            err(issue)
        return 1

    print("OK: repository layout matches enforced boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
