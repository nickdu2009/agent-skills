#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = REPO_ROOT / "skills"
TARGET_DIR = REPO_ROOT / ".cursor" / "skills"
SKILL_FILE = "SKILL.md"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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


def discover_target_skills() -> list[Path]:
    if not TARGET_DIR.exists():
        return []

    skill_dirs: list[Path] = []
    for child in sorted(TARGET_DIR.iterdir()):
        if child.is_dir():
            skill_dirs.append(child)
    return skill_dirs


def collect_rel_files(root: Path) -> dict[str, Path]:
    if not root.exists():
        return {}
    out: dict[str, Path] = {}
    for path in root.rglob("*"):
        if path.is_file():
            out[path.relative_to(root).as_posix()] = path
    return out


def check_sync(skill_dirs: list[Path]) -> int:
    drift_found = False
    source_names = {skill_dir.name for skill_dir in skill_dirs}

    for skill_dir in sorted(skill_dirs, key=lambda p: p.name):
        dst_root = TARGET_DIR / skill_dir.name
        src_files = collect_rel_files(skill_dir)
        dst_files = collect_rel_files(dst_root) if dst_root.exists() else {}

        src_keys = set(src_files.keys())
        dst_keys = set(dst_files.keys())

        for rel in sorted(src_keys - dst_keys):
            drift_found = True
            print(f"MISSING {dst_root.relative_to(REPO_ROOT) / rel}")

        for rel in sorted(dst_keys - src_keys):
            drift_found = True
            print(f"EXTRA {dst_root.relative_to(REPO_ROOT) / rel}")

        for rel in sorted(src_keys & dst_keys):
            if file_sha256(src_files[rel]) != file_sha256(dst_files[rel]):
                drift_found = True
                print(f"OUTDATED {dst_root.relative_to(REPO_ROOT) / rel}")

    for target_dir in sorted(discover_target_skills(), key=lambda p: p.name):
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
        dst = TARGET_DIR / skill_dir.name
        shutil.copytree(skill_dir, dst, dirs_exist_ok=True)
        synced += 1
        print(f"SYNCED {dst.relative_to(REPO_ROOT)}")

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
