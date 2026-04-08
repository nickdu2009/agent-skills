#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# ///
"""Migrate legacy flat phase docs into per-phase directories."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


CANONICAL_DOCS = {
    "roadmap.md": "roadmap.md",
    "plan.yaml": "plan.yaml",
    "wave-guide.md": "wave-guide.md",
    "execution-index.md": "execution-index.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate flat phase docs into per-phase directories.")
    parser.add_argument("--source", required=True, help="Legacy docs directory that contains phaseN-* files")
    parser.add_argument("--target", required=True, help="Phase docs root, usually docs/phases")
    parser.add_argument("--phase", help="Only migrate one phase id")
    parser.add_argument("--dry-run", action="store_true", help="Print the migration plan without moving files")
    return parser.parse_args()


def split_phase_prefix(filename: str) -> tuple[str, str] | None:
    if "-" not in filename or not filename.startswith("phase"):
        return None
    phase, remainder = filename.split("-", 1)
    if not phase or not remainder:
        return None
    return phase, remainder


def discover_legacy_docs(source: Path) -> dict[str, list[tuple[str, Path]]]:
    phases: dict[str, list[tuple[str, Path]]] = {}
    for path in sorted(source.iterdir()):
        if not path.is_file():
            continue
        result = split_phase_prefix(path.name)
        if result is None:
            continue
        phase, remainder = result
        phases.setdefault(phase, []).append((remainder, path))
    return phases


def planned_moves(entries: list[tuple[str, Path]], target_dir: Path) -> list[tuple[Path, Path]]:
    moves: list[tuple[Path, Path]] = []
    for remainder, source in sorted(entries, key=lambda item: item[0]):
        if remainder in CANONICAL_DOCS:
            destination = target_dir / CANONICAL_DOCS[remainder]
        else:
            destination = target_dir / "legacy" / remainder
        moves.append((source, destination))
    return moves


def migrate_phase(phase: str, entries: list[tuple[str, Path]], target_root: Path, dry_run: bool) -> None:
    target_dir = target_root / phase
    moves = planned_moves(entries, target_dir)
    remainders = {remainder for remainder, _ in entries}
    present_canonical = sorted(remainder for remainder in remainders if remainder in CANONICAL_DOCS)
    missing_canonical = sorted(set(CANONICAL_DOCS) - remainders)
    legacy_remainders = sorted(remainder for remainder in remainders if remainder not in CANONICAL_DOCS)

    destination_map: dict[Path, Path] = {}
    duplicate_destinations: list[str] = []
    for src, dst in moves:
        if dst in destination_map:
            duplicate_destinations.append(f"{src} and {destination_map[dst]} -> {dst}")
        else:
            destination_map[dst] = src
    if duplicate_destinations:
        raise ValueError(f"{phase}: duplicate destination paths: {duplicate_destinations}")

    collisions = [str(dst) for _, dst in moves if dst.exists()]
    if collisions:
        raise ValueError(f"{phase}: target files already exist: {collisions}")

    print(f"[phase] {phase}")
    if present_canonical:
        print(f"  canonical: {', '.join(present_canonical)}")
    if missing_canonical:
        print(f"  missing canonical: {', '.join(missing_canonical)}")
    if legacy_remainders:
        print(f"  legacy: {', '.join(legacy_remainders)}")
    for src, dst in moves:
        print(f"  {src} -> {dst}")
    if dry_run:
        return

    target_dir.mkdir(parents=True, exist_ok=True)
    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))


def main() -> int:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    target = Path(args.target).expanduser().resolve()

    if not source.exists():
        print(f"ERROR migrate-phase-docs: source directory not found: {source}", file=sys.stderr)
        return 1
    if not source.is_dir():
        print(f"ERROR migrate-phase-docs: source is not a directory: {source}", file=sys.stderr)
        return 1

    try:
        phases = discover_legacy_docs(source)
        if args.phase:
            phases = {phase: entries for phase, entries in phases.items() if phase == args.phase}
        if not phases:
            print("No legacy phase docs found.")
            return 0

        for phase, entries in phases.items():
            migrate_phase(phase, entries, target, args.dry_run)
        print(
            "Dry run complete." if args.dry_run else f"Migrated {len(phases)} phase doc set(s)."
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR migrate-phase-docs: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
