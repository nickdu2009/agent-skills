#!/usr/bin/env python3
"""Validate governance follow-on compare and observability contracts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
BASELINES_DIR = REPO_ROOT / "maintainer" / "reports" / "baselines"
OBSERVABILITY_DIR = REPO_ROOT / "maintainer" / "governance_observability"
GOVERNANCE_EVAL_DIR = REPO_ROOT / "maintainer" / "governance_eval"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_scope_mismatch_check() -> dict[str, Any]:
    baseline_path = BASELINES_DIR / "governance-health-baseline-2026-05-31-cross-cli.json"
    baseline = load_json(baseline_path)
    current = json.loads(json.dumps(baseline))
    current["checks"]["evaluation"]["model_override"] = "scope-mismatch-fixture"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        fixture_baseline = temp_dir_path / "baseline.json"
        fixture_current = temp_dir_path / "current.json"
        fixture_baseline.write_text(json.dumps(baseline), encoding="utf-8")
        fixture_current.write_text(json.dumps(current), encoding="utf-8")

        proc = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("compare_governance_health_baseline.py")),
                "--baseline",
                str(fixture_baseline),
                "--current",
                str(fixture_current),
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    payload = json.loads(proc.stdout)
    ok = (
        proc.returncode == 0
        and payload.get("status") == "warn"
        and any("eval scope mismatch" in warning for warning in payload.get("warnings", []))
    )
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "status": payload.get("status"),
        "warnings": payload.get("warnings", []),
    }


def run_observability_mapping_check() -> dict[str, Any]:
    cases_text = (GOVERNANCE_EVAL_DIR / "cases.yaml").read_text(encoding="utf-8")
    mapping_text = (OBSERVABILITY_DIR / "from_governance_eval_map.yaml").read_text(encoding="utf-8")
    case_ids = set(re.findall(r"^- id: ([A-Za-z0-9_-]+)$", cases_text, flags=re.MULTILINE))
    mapped_case_ids = re.findall(
        r"^\s*governance_eval_case: ([A-Za-z0-9_-]+)$",
        mapping_text,
        flags=re.MULTILINE,
    )
    missing = [
        {"governance_eval_case": case_id}
        for case_id in mapped_case_ids
        if case_id not in case_ids
    ]
    return {
        "ok": not missing,
        "link_count": len(mapped_case_ids),
        "missing": missing,
    }


def build_payload() -> dict[str, Any]:
    scope_mismatch = run_scope_mismatch_check()
    observability_mapping = run_observability_mapping_check()
    ok = scope_mismatch["ok"] and observability_mapping["ok"]
    return {
        "status": "pass" if ok else "fail",
        "checks": {
            "scope_mismatch_warning": scope_mismatch,
            "observability_mapping": observability_mapping,
        },
    }


def print_text(payload: dict[str, Any]) -> None:
    print("=" * 80)
    print("Governance Follow-on Contracts")
    print("=" * 80)
    print()
    print(f"Overall status: {payload['status'].upper()}")
    print()
    scope_mismatch = payload["checks"]["scope_mismatch_warning"]
    print(
        "Scope mismatch fixture: "
        f"{'PASS' if scope_mismatch['ok'] else 'FAIL'} "
        f"(status={scope_mismatch['status']}, returncode={scope_mismatch['returncode']})"
    )
    observability_mapping = payload["checks"]["observability_mapping"]
    print(
        "Observability mapping: "
        f"{'PASS' if observability_mapping['ok'] else 'FAIL'} "
        f"(links={observability_mapping['link_count']}, "
        f"missing={len(observability_mapping['missing'])})"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate governance follow-on contracts")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_text(payload)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
