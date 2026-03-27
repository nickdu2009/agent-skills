#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""List the declared lanes for one wave from a phase execution schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _shared_phase_tools import find_wave, load_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List lanes for one wave from a phase execution schema.")
    parser.add_argument("--plan", required=True, help="Path to docs/phaseN-plan.yaml")
    parser.add_argument("--wave", required=True, type=int, help="Wave id")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of line-oriented text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    try:
        data = load_plan(plan_path)
        wave = find_wave(data, args.wave)
        lanes = []
        for item in wave.get("lane_setup", []):
            if not isinstance(item, dict):
                continue
            lanes.append(
                {
                    "lane": item.get("lane"),
                    "owner": item.get("owner"),
                    "ref_kind": item.get("ref_kind"),
                    "ref": item.get("ref"),
                }
            )
        if args.json:
            print(json.dumps(lanes, indent=2))
        else:
            for lane in lanes:
                print(
                    f"{lane['lane']}: owner={lane['owner']} ref_kind={lane['ref_kind']} ref={lane['ref']}"
                )
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR list-wave-lanes: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
