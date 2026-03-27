#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Run a minimal execution preflight for a schema-first phase wave."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _shared_phase_tools import find_wave, infer_phase, load_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run execution preflight checks for a schema-first phase.")
    parser.add_argument("--plan", required=True, help="Path to docs/phaseN-plan.yaml")
    parser.add_argument("--docs-dir", required=True, help="Directory containing the strict four-file phase doc set")
    parser.add_argument("--phase", required=True, help="Phase prefix such as phase13")
    parser.add_argument("--wave", type=int, help="Optional wave id to validate for execution readiness")
    parser.add_argument(
        "--contract-scripts",
        help="Optional path to the phase-contract-tools scripts directory",
    )
    return parser.parse_args()


def default_contract_scripts() -> Path:
    return Path(__file__).resolve().parent


def run_script(script: Path, *args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["uv", "run", str(script), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def print_stream(prefix: str, text: str, stream) -> None:
    if not text.strip():
        return
    for line in text.rstrip().splitlines():
        print(f"[{prefix}] {line}", file=stream)


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    docs_dir = Path(args.docs_dir).expanduser().resolve()
    scripts_dir = (
        Path(args.contract_scripts).expanduser().resolve()
        if args.contract_scripts
        else default_contract_scripts()
    )

    validate_schema = scripts_dir / "validate_phase_execution_schema.py"
    validate_doc_set = scripts_dir / "validate_phase_doc_set.py"
    missing = [path for path in (validate_schema, validate_doc_set) if not path.exists()]
    if missing:
        print(
            "ERROR preflight-phase-execution: missing phase-contract-tools helper scripts: "
            + ", ".join(str(path) for path in missing),
            file=sys.stderr,
        )
        return 1

    exit_code = 0

    schema_rc, schema_out, schema_err = run_script(validate_schema, "--plan", str(plan_path))
    print_stream("validate_phase_execution_schema", schema_out, sys.stdout)
    print_stream("validate_phase_execution_schema", schema_err, sys.stderr)
    exit_code = max(exit_code, schema_rc)

    doc_rc, doc_out, doc_err = run_script(
        validate_doc_set,
        "--docs-dir",
        str(docs_dir),
        "--phase",
        args.phase,
    )
    print_stream("validate_phase_doc_set", doc_out, sys.stdout)
    print_stream("validate_phase_doc_set", doc_err, sys.stderr)
    exit_code = max(exit_code, doc_rc)

    if exit_code != 0:
        return exit_code

    try:
        data = load_plan(plan_path)
        phase = infer_phase(plan_path, data)
        if args.wave is None:
            print(f"OK preflight-phase-execution: {phase} doc set and schema validation passed.")
            return 0

        wave = find_wave(data, args.wave)
        required_fields = ("control_pr", "prs", "merge_order", "lane_setup")
        missing_fields = [field for field in required_fields if not wave.get(field)]
        if missing_fields:
            print(
                "ERROR preflight-phase-execution: selected wave is missing required execution fields: "
                + ", ".join(missing_fields),
                file=sys.stderr,
            )
            return 1
        pr_map = {pr["id"]: pr for pr in data.get("prs", []) if isinstance(pr, dict) and isinstance(pr.get("id"), str)}
        role_map = {}
        for role in wave.get("roles", []):
            if isinstance(role, dict) and isinstance(role.get("id"), str):
                role_map[role["id"]] = role
        blocked_lanes = []
        for item in wave.get("lane_setup", []):
            if not isinstance(item, dict):
                continue
            ref_kind = item.get("ref_kind")
            ref = item.get("ref")
            start_condition = None
            if ref_kind == "pr":
                pr = pr_map.get(ref)
                if pr and isinstance(pr.get("start_condition"), dict):
                    start_condition = pr["start_condition"]
            elif ref_kind == "role":
                role = role_map.get(ref)
                if role and isinstance(role.get("start_condition"), dict):
                    start_condition = role["start_condition"]
            if not start_condition:
                continue
            gate = start_condition.get("gate")
            refs = start_condition.get("refs", [])
            if gate == "after_prs" and refs:
                blocked_lanes.append(f"{item.get('lane')} (waiting on PRs {refs})")
            elif gate == "after_waves" and refs:
                blocked_lanes.append(f"{item.get('lane')} (waiting on waves {refs})")
        if blocked_lanes:
            print(
                f"WARN preflight-phase-execution: {len(blocked_lanes)} lane(s) have unresolved start conditions: "
                + "; ".join(blocked_lanes),
            )
        lane_count = len([item for item in wave.get("lane_setup", []) if isinstance(item, dict)])
        print(
            f"OK preflight-phase-execution: {phase} wave {args.wave} ready for execution "
            f"(control_pr={wave.get('control_pr')}, lanes={lane_count})."
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR preflight-phase-execution: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
