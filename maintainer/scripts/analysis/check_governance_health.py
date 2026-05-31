#!/usr/bin/env python3
"""Aggregate governance health checks into a single snapshot."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_DIR = REPO_ROOT / "maintainer" / "scripts" / "analysis"
INSTALL_DIR = REPO_ROOT / "maintainer" / "scripts" / "install"
GOVERNANCE_EVAL_DIR = REPO_ROOT / "maintainer" / "governance_eval"

EVAL_PAYLOAD_SPEC = importlib.util.spec_from_file_location(
    "governance_eval_eval_payload",
    GOVERNANCE_EVAL_DIR / "eval_payload.py",
)
if EVAL_PAYLOAD_SPEC is None or EVAL_PAYLOAD_SPEC.loader is None:
    raise ImportError("unable to load maintainer/governance_eval/eval_payload.py")
EVAL_PAYLOAD_MODULE = importlib.util.module_from_spec(EVAL_PAYLOAD_SPEC)
EVAL_PAYLOAD_SPEC.loader.exec_module(EVAL_PAYLOAD_MODULE)
load_eval_payload = EVAL_PAYLOAD_MODULE.load_eval_payload
merge_eval_payloads = EVAL_PAYLOAD_MODULE.merge_eval_payloads


def run_json_command(command: list[str]) -> tuple[dict[str, Any] | None, subprocess.CompletedProcess[str]]:
    """Run a command expected to emit JSON on stdout."""
    proc = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if not proc.stdout.strip():
        return None, proc
    try:
        return json.loads(proc.stdout), proc
    except json.JSONDecodeError:
        return None, proc


def run_text_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a command that only signals via text + exit code."""
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def is_mirror_drift_issue(issue: str) -> bool:
    """Return whether a sync issue represents mirror drift."""
    return (
        "AGENTS-template.md and CLAUDE-template.md" in issue
        or "root AGENTS.md and CLAUDE.md content diverged (mirror drift)" in issue
    )


def collect_sync_status() -> dict[str, Any]:
    data, proc = run_json_command(
        [sys.executable, str(ANALYSIS_DIR / "check_governance_sync.py"), "--json"]
    )
    if data is None:
        return {
            "status": "blocked",
            "ok": False,
            "issue_count": 0,
            "mirror_drift_event_count": 0,
            "issues": [],
            "returncode": proc.returncode,
            "stderr": proc.stderr.strip(),
            "stdout": proc.stdout.strip(),
        }

    issues = data.get("issues", [])
    return {
        "status": "pass" if data.get("ok") else "fail",
        "ok": bool(data.get("ok")),
        "issue_count": len(issues),
        "mirror_drift_event_count": sum(1 for issue in issues if is_mirror_drift_issue(issue)),
        "issues": issues,
        "template_sections": data.get("template_sections", []),
        "agents_sections": data.get("agents_sections", []),
        "claude_sections": data.get("claude_sections", []),
        "returncode": proc.returncode,
    }


def collect_smoke_status() -> dict[str, Any]:
    proc = run_text_command(
        [sys.executable, str(INSTALL_DIR / "run_manage_governance_smoke.py")]
    )
    return {
        "status": "pass" if proc.returncode == 0 else "fail",
        "pass": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def collect_cross_ref_status() -> dict[str, Any]:
    data, proc = run_json_command(
        [sys.executable, str(ANALYSIS_DIR / "check_cross_references.py"), "--json"]
    )
    if data is None:
        return {
            "status": "blocked",
            "ok": False,
            "broken_reference_count": 0,
            "returncode": proc.returncode,
            "stderr": proc.stderr.strip(),
            "stdout": proc.stdout.strip(),
        }

    summary = data.get("summary", {})
    broken_reference_count = int(summary.get("total_broken_references", 0))
    return {
        "status": "pass" if summary.get("status") == "pass" else "fail",
        "ok": summary.get("status") == "pass",
        "broken_reference_count": broken_reference_count,
        "returncode": proc.returncode,
    }


def load_eval_status(paths: list[Path]) -> dict[str, Any]:
    try:
        payloads = [load_eval_payload(path) for path in paths]
        payload = merge_eval_payloads(payloads)
    except ValueError as exc:
        return {
            "status": "blocked",
            "error": str(exc),
        }

    summary = payload["summary"]
    results = payload["results"]
    config = payload["config"]
    requested_cli_names = list(config.get("requested_clis", list(results)))
    requested_case_ids = list(config.get("requested_case_ids", []))
    runs_override = config.get("runs_override")
    model_override = config.get("model_override")
    skip_preflight = config.get("skip_preflight")
    executed_case_count = int(summary.get("executed_case_count", 0))
    if executed_case_count == 0:
        return {
            "status": "skipped",
            "sources": [str(path) for path in paths],
            "attached_eval_json_count": len(paths),
            "cli_names": list(results),
            "requested_cli_names": requested_cli_names,
            "requested_cli_count": summary.get("requested_cli_count", 0),
            "requested_case_ids": requested_case_ids,
            "requested_case_count": summary.get("requested_case_count", 0),
            "runs_override": runs_override,
            "model_override": model_override,
            "skip_preflight": skip_preflight,
            "skipped_cli_count": int(summary.get("skipped_cli_count", 0)),
            "executed_case_count": 0,
            "pass_count": 0,
            "fail_count": 0,
            "error_count": 0,
            "calibrated_count": 0,
            "miscalibrated_count": 0,
            "pass_rate": None,
            "calibration_rate": None,
            "run_eval_status": summary.get("status", "pass"),
        }

    pass_count = int(summary.get("pass_count", 0))
    fail_count = int(summary.get("fail_count", 0))
    error_count = int(summary.get("error_count", 0))
    calibrated_count = int(summary.get("calibrated_count", 0))
    miscalibrated_count = int(summary.get("miscalibrated_count", 0))
    return {
        "status": "included",
        "sources": [str(path) for path in paths],
        "attached_eval_json_count": len(paths),
        "cli_names": list(results),
        "requested_cli_names": requested_cli_names,
        "requested_cli_count": int(summary.get("requested_cli_count", len(results))),
        "requested_case_ids": requested_case_ids,
        "requested_case_count": int(summary.get("requested_case_count", 0)),
        "runs_override": runs_override,
        "model_override": model_override,
        "skip_preflight": skip_preflight,
        "skipped_cli_count": int(summary.get("skipped_cli_count", 0)),
        "executed_case_count": executed_case_count,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "error_count": error_count,
        "calibrated_count": calibrated_count,
        "miscalibrated_count": miscalibrated_count,
        "pass_rate": pass_count / executed_case_count,
        "calibration_rate": calibrated_count / executed_case_count,
        "run_eval_status": summary.get("status", "fail"),
    }


def collect_health(eval_json_paths: list[Path] | None = None) -> dict[str, Any]:
    sync = collect_sync_status()
    smoke = collect_smoke_status()
    cross_ref = collect_cross_ref_status()

    if not eval_json_paths:
        evaluation = {"status": "not_included"}
    else:
        evaluation = load_eval_status(eval_json_paths)

    deterministic_ok = sync["ok"] and smoke["pass"] and cross_ref["ok"]
    overall_status = "pass"
    if not deterministic_ok:
        overall_status = "fail"
    elif evaluation["status"] == "blocked":
        overall_status = "fail"
    elif evaluation["status"] == "skipped":
        overall_status = "warn"
    elif evaluation["status"] == "included" and evaluation["run_eval_status"] != "pass":
        overall_status = "fail"

    return {
        "metrics": {
            "projection_sync_ok": sync["ok"],
            "sync_issue_count": sync["issue_count"],
            "mirror_drift_event_count": sync["mirror_drift_event_count"],
            "smoke_pass": smoke["pass"],
            "cross_ref_ok": cross_ref["ok"],
            "broken_reference_count": cross_ref["broken_reference_count"],
            "eval_pass_rate": evaluation.get("pass_rate"),
            "eval_calibration_rate": evaluation.get("calibration_rate"),
            "eval_error_count": evaluation.get("error_count"),
        },
        "checks": {
            "sync": sync,
            "smoke": smoke,
            "cross_references": cross_ref,
            "evaluation": evaluation,
        },
        "summary": {
            "status": overall_status,
            "deterministic_status": "pass" if deterministic_ok else "fail",
            "eval_status": evaluation["status"],
            "included_eval": evaluation["status"] in {"included", "skipped", "blocked"},
        },
    }


def format_rate(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def print_summary(snapshot: dict[str, Any]) -> None:
    metrics = snapshot["metrics"]
    summary = snapshot["summary"]
    evaluation = snapshot["checks"]["evaluation"]

    print("=" * 80)
    print("Governance Health Snapshot")
    print("=" * 80)
    print()
    print(f"Overall status: {summary['status'].upper()}")
    print(f"Deterministic status: {summary['deterministic_status'].upper()}")
    print(f"Eval status: {summary['eval_status']}")
    print()
    print("Deterministic metrics:")
    print(f"  - projection_sync_ok: {metrics['projection_sync_ok']}")
    print(f"  - sync_issue_count: {metrics['sync_issue_count']}")
    print(f"  - mirror_drift_event_count: {metrics['mirror_drift_event_count']}")
    print(f"  - smoke_pass: {metrics['smoke_pass']}")
    print(f"  - cross_ref_ok: {metrics['cross_ref_ok']}")
    print(f"  - broken_reference_count: {metrics['broken_reference_count']}")
    print()
    print("Eval metrics:")
    print(f"  - eval_pass_rate: {format_rate(metrics['eval_pass_rate'])}")
    print(f"  - eval_calibration_rate: {format_rate(metrics['eval_calibration_rate'])}")
    print(
        f"  - eval_error_count: "
        f"{metrics['eval_error_count'] if metrics['eval_error_count'] is not None else 'n/a'}"
    )
    if evaluation["status"] in {"blocked", "skipped"} and evaluation.get("error"):
        print(f"  - eval_note: {evaluation['error']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate governance health checks")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--eval-json",
        type=Path,
        action="append",
        default=None,
        help="Optional path(s) to run_eval.py --json output to include eval metrics",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = collect_health(args.eval_json)

    if args.json:
        print(json.dumps(snapshot, indent=2))
    else:
        print_summary(snapshot)

    return 0 if snapshot["summary"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
