#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Render a machine-readable wave status snapshot from the accepted phase plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from _shared_phase_tools import find_wave, infer_phase, load_plan


VALID_WAVE_STATES = {"blocked", "active", "merge_ready", "next_wave_ready"}
VALID_EXECUTION_MODES = {"serial", "parallel"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a wave status snapshot from a phase execution schema.")
    parser.add_argument("--plan", required=True, help="Path to docs/phaseN-plan.yaml")
    parser.add_argument("--wave", required=True, type=int, help="Wave id")
    parser.add_argument("--format", choices=("yaml", "json"), default="yaml", help="Output format")
    parser.add_argument("--execution-mode", choices=sorted(VALID_EXECUTION_MODES), default="serial", help="Execution mode override")
    parser.add_argument("--wave-state", choices=sorted(VALID_WAVE_STATES), default="blocked", help="Wave state override")
    parser.add_argument("--write", help="Optional output path")
    return parser.parse_args()


def render_snapshot(plan_path: Path, data: dict[str, Any], wave: dict[str, Any], execution_mode: str, wave_state: str) -> dict[str, Any]:
    lanes = []
    for entry in wave.get("lane_setup", []):
        if not isinstance(entry, dict):
            continue
        lanes.append(
            {
                "lane_ref": str(entry.get("lane", "")),
                "ref_kind": str(entry.get("ref_kind", "")),
                "ref": str(entry.get("ref", "")),
                "lane_state": "not_started",
                "owner": str(entry.get("owner", "")),
                "blockers": [],
                "validation_status": "not_run",
                "evidence_refs": [],
            }
        )

    return {
        "phase_id": infer_phase(plan_path, data),
        "wave_id": int(wave.get("id")),
        "execution_mode": execution_mode,
        "wave_state": wave_state,
        "control_pr": str(wave.get("control_pr", "")),
        "lanes": lanes,
        "validation": {
            "lane_checks": [],
            "seam_checks": [],
            "status": "not_run",
        },
        "next_action": "",
        "planning_escalation": {
            "needed": False,
            "reason": "",
        },
    }


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    try:
        data = load_plan(plan_path)
        wave = find_wave(data, args.wave)
        snapshot = render_snapshot(plan_path, data, wave, args.execution_mode, args.wave_state)
        if args.format == "json":
            payload = json.dumps(snapshot, indent=2) + "\n"
        else:
            payload = yaml.safe_dump(snapshot, sort_keys=False)
        if args.write:
            output_path = Path(args.write).expanduser().resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR render-wave-status-snapshot: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
