#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Render the phase-root README summary from discovered phase plans."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _shared_phase_tools import (
    PHASE_FILES,
    PHASE_SUMMARIES_HEADING,
    VALID_PHASE_STATUSES,
    iter_phase_dirs,
    load_plan,
    render_phase_summary_line,
    resolve_phase_root,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the phase-root README summary from discovered phase plans.")
    parser.add_argument("--phase-root", help="Root directory that contains per-phase doc directories.")
    parser.add_argument("--write", help="Optional output path")
    return parser.parse_args()


def roadmap_section_text(roadmap_text: str, heading: str) -> str:
    marker = f"## {heading}"
    lines = roadmap_text.splitlines()
    start = None
    collected: list[str] = []
    for idx, line in enumerate(lines):
        if line.strip() == marker:
            start = idx + 1
            break
    if start is None:
        return ""
    for line in lines[start:]:
        if line.startswith("## "):
            break
        collected.append(line.rstrip())
    return "\n".join(collected).strip()


def first_goal_from_roadmap(roadmap_path: Path) -> str | None:
    if not roadmap_path.exists():
        return None
    goals_text = roadmap_section_text(roadmap_path.read_text(encoding="utf-8"), "Goals")
    if not goals_text:
        return None
    for raw_line in goals_text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("- "):
            return stripped[2:].strip()
        if stripped:
            return stripped
    return None


def derive_goal(plan: dict, roadmap_path: Path) -> str:
    roadmap_goal = first_goal_from_roadmap(roadmap_path)
    if roadmap_goal:
        return roadmap_goal
    prs = plan.get("prs", [])
    if isinstance(prs, list):
        for pr in prs:
            if isinstance(pr, dict):
                goal = pr.get("goal")
                if isinstance(goal, str) and goal.strip():
                    return goal.strip()
    waves = plan.get("waves", [])
    if isinstance(waves, list):
        for wave in waves:
            if isinstance(wave, dict):
                goal = wave.get("goal")
                if isinstance(goal, str) and goal.strip():
                    return goal.strip()
    scope = plan.get("scope")
    if isinstance(scope, str) and scope.strip():
        return scope.strip()
    return "summary unavailable"


def derive_scope(plan: dict) -> str:
    scope = plan.get("scope")
    if isinstance(scope, str) and scope.strip():
        return scope.strip()
    return "scope unavailable"


def derive_status(plan: dict) -> str:
    status = plan.get("status")
    if isinstance(status, str) and status.strip().lower() in VALID_PHASE_STATUSES:
        return status.strip().lower()
    return "proposed"


def render_readme(phase_root: Path) -> str:
    lines = [
        "# Phase Index",
        "",
        PHASE_SUMMARIES_HEADING,
        "",
    ]
    for phase_dir in iter_phase_dirs(phase_root):
        plan_path = phase_dir / PHASE_FILES["plan"]
        roadmap_path = phase_dir / PHASE_FILES["roadmap"]
        plan = load_plan(plan_path)
        lines.append(
            render_phase_summary_line(
                phase=phase_dir.name,
                goal=derive_goal(plan, roadmap_path),
                scope=derive_scope(plan),
                status=derive_status(plan),
            )
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    phase_root = resolve_phase_root(Path(args.phase_root) if args.phase_root else None)
    if not phase_root.exists():
        print(f"ERROR render-phase-root-readme: phase root directory not found: {phase_root}", file=sys.stderr)
        return 1
    try:
        payload = render_readme(phase_root)
        if args.write:
            output_path = Path(args.write).expanduser().resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR render-phase-root-readme: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
