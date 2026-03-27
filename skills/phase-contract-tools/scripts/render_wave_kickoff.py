#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Render a human-facing wave kickoff summary from a phase execution schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml
from _shared_phase_tools import find_wave, infer_phase, load_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a wave kickoff summary from a phase execution schema.")
    parser.add_argument("--plan", required=True, help="Path to docs/phaseN-plan.yaml")
    parser.add_argument("--wave", required=True, type=int, help="Wave id to render")
    return parser.parse_args()


def pr_title_map(data: dict[str, Any]) -> dict[str, str]:
    titles: dict[str, str] = {}
    for pr in data.get("prs", []):
        if isinstance(pr, dict) and isinstance(pr.get("id"), str):
            titles[pr["id"]] = str(pr.get("title", pr["id"]))
    return titles


def render_wave(plan_path: Path, data: dict[str, Any], wave: dict[str, Any]) -> str:
    phase = infer_phase(plan_path, data)
    titles = pr_title_map(data)
    lines = [f"{phase} {wave['label']} kickoff", ""]
    lines.append(f"Goal: {wave.get('goal', '')}")
    lines.append(f"Control PR: {wave.get('control_pr', '')}")
    lines.append("")
    lines.append("Phase hard rules:")
    for item in data.get("hard_rules", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Lane setup:")
    for lane in wave.get("lane_setup", []):
        if not isinstance(lane, dict):
            continue
        ref = str(lane.get("ref", ""))
        ref_kind = str(lane.get("ref_kind", ""))
        if ref_kind == "pr":
            label = f"{ref} {titles.get(ref, '')}".strip()
        else:
            label = ref
        lines.append(f"- {lane.get('lane')}: {lane.get('owner')} -> {ref_kind} {label}")
    roles = [role for role in wave.get("roles", []) if isinstance(role, dict)]
    if roles:
        lines.append("")
        lines.append("Wave roles:")
        for role in roles:
            lines.append(f"- {role.get('id')}: {role.get('owner')} -> {role.get('kind')} - {role.get('goal')}")
    lines.append("")
    lines.append("Merge order:")
    for idx, batch in enumerate(wave.get("merge_order", []), start=1):
        if isinstance(batch, list):
            pretty = ", ".join(f"{pr_id} {titles.get(pr_id, '')}".strip() for pr_id in batch)
            lines.append(f"{idx}. {pretty}")
    lines.append("")
    lines.append("Constraints:")
    for item in wave.get("constraints", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Integrator checklist:")
    for item in wave.get("integrator_checklist", []):
        lines.append(f"- {item}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    try:
        data = load_plan(plan_path)
        wave = find_wave(data, args.wave)
        print(render_wave(plan_path, data, wave))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR render-wave-kickoff: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
