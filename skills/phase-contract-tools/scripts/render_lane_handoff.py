#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Render an immutable lane handoff artifact for a schema-first wave."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from typing import Any

import yaml
from _shared_phase_tools import find_lane, find_wave, infer_phase, load_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an immutable lane handoff artifact.")
    parser.add_argument("--plan", required=True, help="Path to docs/phaseN-plan.yaml")
    parser.add_argument("--wave", required=True, type=int, help="Wave id")
    parser.add_argument("--lane", required=True, help="Lane name from wave.lane_setup")
    parser.add_argument("--format", choices=("markdown", "yaml"), default="markdown", help="Output format")
    parser.add_argument("--stdout-only-body", action="store_true", help="Print only the lane prompt body")
    parser.add_argument("--write", help="Optional output path for the rendered artifact")
    parser.add_argument(
        "--contract-scripts",
        help="Optional path to the phase-contract-tools scripts directory",
    )
    return parser.parse_args()


def default_contract_scripts() -> Path:
    return Path(__file__).resolve().parent


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render_prompt(
    contract_scripts: Path,
    plan_path: Path,
    wave_id: int,
    lane_name: str,
) -> str:
    script = contract_scripts / "render_agent_prompt.py"
    if not script.exists():
        raise FileNotFoundError(f"missing render helper: {script}")
    proc = subprocess.run(
        ["uv", "run", str(script), "--plan", str(plan_path), "--wave", str(wave_id), "--lane", lane_name],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit code {proc.returncode}"
        raise RuntimeError(f"render_agent_prompt failed: {detail}")
    return proc.stdout.rstrip() + "\n"


def build_manifest(plan_path: Path, data: dict[str, Any], wave: dict[str, Any], lane: dict[str, Any], body: str) -> dict[str, Any]:
    plan_text = plan_path.read_text(encoding="utf-8")
    return {
        "handoff_schema_version": "1.0",
        "phase": infer_phase(plan_path, data),
        "wave_id": wave.get("id"),
        "wave_label": wave.get("label"),
        "lane": lane.get("lane"),
        "owner": lane.get("owner"),
        "ref_kind": lane.get("ref_kind"),
        "ref": lane.get("ref"),
        "plan_path": str(plan_path),
        "plan_sha256": sha256_text(plan_text),
        "body_sha256": sha256_text(body),
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def render_markdown(manifest: dict[str, Any], body: str) -> str:
    frontmatter = yaml.safe_dump(manifest, sort_keys=False).strip()
    return f"---\n{frontmatter}\n---\n\n{body}"


def render_yaml_payload(manifest: dict[str, Any], body: str) -> str:
    return yaml.safe_dump({"manifest": manifest, "body": body}, sort_keys=False)


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    contract_scripts = (
        Path(args.contract_scripts).expanduser().resolve()
        if args.contract_scripts
        else default_contract_scripts()
    )

    try:
        data = load_plan(plan_path)
        wave = find_wave(data, args.wave)
        lane = find_lane(wave, args.lane)
        body = render_prompt(contract_scripts, plan_path, args.wave, args.lane)
        if args.stdout_only_body:
            payload = body
        else:
            manifest = build_manifest(plan_path, data, wave, lane, body)
            payload = render_markdown(manifest, body) if args.format == "markdown" else render_yaml_payload(manifest, body)
        if args.write:
            output_path = Path(args.write).expanduser().resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR render-lane-handoff: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
