#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "skills"
TARGET_DIR = REPO_ROOT / ".cursor" / "skills"
SKILL_FILE = "SKILL.md"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def discover_source_skills() -> list[Path]:
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"Source skills directory not found: {SOURCE_DIR}")

    skill_dirs: list[Path] = []
    for child in sorted(SOURCE_DIR.iterdir()):
        if not child.is_dir():
            continue
        if (child / SKILL_FILE).exists():
            skill_dirs.append(child)
    return skill_dirs


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def discover_target_skills() -> list[Path]:
    if not TARGET_DIR.exists():
        return []

    skill_dirs: list[Path] = []
    for child in sorted(TARGET_DIR.iterdir()):
        if child.is_dir():
            skill_dirs.append(child)
    return skill_dirs


def target_skill_file(skill_dir: Path) -> Path:
    return TARGET_DIR / skill_dir.name / SKILL_FILE


def check_sync(skill_dirs: list[Path]) -> int:
    drift_found = False
    source_names = {skill_dir.name for skill_dir in skill_dirs}

    for skill_dir in skill_dirs:
        source_file = skill_dir / SKILL_FILE
        target_file = target_skill_file(skill_dir)

        if not target_file.exists():
            drift_found = True
            print(f"MISSING {target_file.relative_to(REPO_ROOT)}")
            continue

        source_hash = sha256_text(read_text(source_file))
        target_hash = sha256_text(read_text(target_file))

        if source_hash != target_hash:
            drift_found = True
            print(f"OUTDATED {target_file.relative_to(REPO_ROOT)}")

    for target_dir in discover_target_skills():
        if target_dir.name not in source_names:
            drift_found = True
            print(f"EXTRA {target_dir.relative_to(REPO_ROOT)}")

    if drift_found:
        print("Cursor skill mirror is out of sync.")
        return 1

    print("Cursor skill mirror is up to date.")
    return 0


def remove_stale_target_skills(skill_dirs: list[Path]) -> None:
    source_names = {skill_dir.name for skill_dir in skill_dirs}

    for target_dir in discover_target_skills():
        if target_dir.name in source_names:
            continue

        # The Cursor mirror is a generated artifact, so stale mirrored skills are safe to remove.
        shutil.rmtree(target_dir)
        print(f"REMOVED {target_dir.relative_to(REPO_ROOT)}")


def sync_skills(skill_dirs: list[Path]) -> int:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    remove_stale_target_skills(skill_dirs)
    synced = 0

    for skill_dir in skill_dirs:
        source_file = skill_dir / SKILL_FILE
        target_file = target_skill_file(skill_dir)

        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(read_text(source_file), encoding="utf-8")
        synced += 1
        print(f"SYNCED {target_file.relative_to(REPO_ROOT)}")

    print(f"Synced {synced} Cursor skill(s).")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a local .cursor/skills mirror from the canonical skills/ source."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether .cursor/skills is in sync with skills/ without writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        skill_dirs = discover_source_skills()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not skill_dirs:
        print(f"No source skills found in {SOURCE_DIR}", file=sys.stderr)
        return 2

    if args.check:
        return check_sync(skill_dirs)

    return sync_skills(skill_dirs)


if __name__ == "__main__":
    raise SystemExit(main())
