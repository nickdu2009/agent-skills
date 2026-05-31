#!/usr/bin/env python3
"""Compare governance health snapshots against a recorded baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BOOL_METRICS = {
    "projection_sync_ok",
    "smoke_pass",
    "cross_ref_ok",
}

COUNT_METRICS = {
    "sync_issue_count",
    "mirror_drift_event_count",
    "broken_reference_count",
    "eval_error_count",
}

RATE_METRICS = {
    "eval_pass_rate",
    "eval_calibration_rate",
}

EVAL_SCOPE_FIELDS = (
    "requested_cli_names",
    "requested_case_ids",
    "runs_override",
    "model_override",
    "skip_preflight",
)


def load_snapshot(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"snapshot not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def snapshot_metrics(snapshot: dict[str, Any]) -> dict[str, Any]:
    metrics = snapshot.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("snapshot missing top-level metrics object")
    return metrics


def evaluation_block(snapshot: dict[str, Any]) -> dict[str, Any]:
    checks = snapshot.get("checks", {})
    if not isinstance(checks, dict):
        return {}
    evaluation = checks.get("evaluation", {})
    return evaluation if isinstance(evaluation, dict) else {}


def extract_eval_scope(evaluation: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    scope: dict[str, Any] = {}
    missing: list[str] = []
    for field in EVAL_SCOPE_FIELDS:
        value = evaluation.get(field)
        if field in {"requested_cli_names", "requested_case_ids"}:
            if not isinstance(value, list):
                missing.append(field)
                continue
            scope[field] = list(value)
            continue
        if value is None:
            missing.append(field)
            continue
        scope[field] = value

    if missing:
        return None, missing
    return scope, []


def compare_metrics(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> tuple[list[str], list[str], list[str]]:
    regressions: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    baseline_metrics = snapshot_metrics(baseline)
    current_metrics = snapshot_metrics(current)

    for metric in sorted(BOOL_METRICS):
        baseline_value = baseline_metrics.get(metric)
        current_value = current_metrics.get(metric)
        if baseline_value is True and current_value is False:
            regressions.append(f"{metric}: baseline=true, current=false")
        elif baseline_value != current_value:
            notes.append(f"{metric}: baseline={baseline_value!r}, current={current_value!r}")

    for metric in sorted(COUNT_METRICS):
        baseline_value = baseline_metrics.get(metric)
        current_value = current_metrics.get(metric)
        if isinstance(baseline_value, int) and isinstance(current_value, int):
            if current_value > baseline_value:
                regressions.append(
                    f"{metric}: baseline={baseline_value}, current={current_value}"
                )
            elif current_value < baseline_value:
                notes.append(f"{metric}: baseline={baseline_value}, current={current_value}")
        elif baseline_value != current_value:
            notes.append(f"{metric}: baseline={baseline_value!r}, current={current_value!r}")

    baseline_eval = evaluation_block(baseline)
    current_eval = evaluation_block(current)
    baseline_eval_status = baseline.get("summary", {}).get("eval_status")
    current_eval_status = current.get("summary", {}).get("eval_status")

    if baseline_eval_status == "included" and current_eval_status != "included":
        warnings.append(
            "current snapshot does not include eval metrics while baseline did; "
            "deterministic comparison still applies"
        )
    elif baseline_eval_status != "included" and current_eval_status == "included":
        notes.append("current snapshot includes eval metrics that were absent from baseline")
    elif baseline_eval_status == "included" and current_eval_status == "included":
        baseline_scope, baseline_missing = extract_eval_scope(baseline_eval)
        current_scope, current_missing = extract_eval_scope(current_eval)

        if baseline_missing or current_missing:
            warnings.append(
                "eval scope metadata missing; skipping eval rate regression check "
                f"(baseline missing={baseline_missing or 'none'}; "
                f"current missing={current_missing or 'none'})"
            )
        elif baseline_scope != current_scope:
            warnings.append(
                "eval scope mismatch; skipping eval rate regression check "
                f"(baseline scope={baseline_scope}; current scope={current_scope})"
            )
        else:
            for metric in sorted(RATE_METRICS):
                baseline_value = baseline_metrics.get(metric)
                current_value = current_metrics.get(metric)
                if baseline_value is None or current_value is None:
                    warnings.append(f"{metric}: missing eval rate in one snapshot")
                elif current_value < baseline_value:
                    regressions.append(
                        f"{metric}: baseline={baseline_value:.3f}, current={current_value:.3f}"
                    )
                elif current_value > baseline_value:
                    notes.append(
                        f"{metric}: baseline={baseline_value:.3f}, current={current_value:.3f}"
                    )

    return regressions, warnings, notes


def build_payload(
    baseline_path: Path,
    current_path: Path,
    regressions: list[str],
    warnings: list[str],
    notes: list[str],
) -> dict[str, Any]:
    status = "pass"
    if regressions:
        status = "fail"
    elif warnings:
        status = "warn"

    return {
        "status": status,
        "baseline": str(baseline_path),
        "current": str(current_path),
        "regressions": regressions,
        "warnings": warnings,
        "notes": notes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare governance health baseline")
    parser.add_argument("--baseline", type=Path, required=True, help="Baseline snapshot JSON")
    parser.add_argument("--current", type=Path, required=True, help="Current snapshot JSON")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit non-zero when regression is detected",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Exit non-zero when warnings are present",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        baseline = load_snapshot(args.baseline)
        current = load_snapshot(args.current)
        regressions, warnings, notes = compare_metrics(baseline, current)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    payload = build_payload(args.baseline, args.current, regressions, warnings, notes)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("=" * 80)
        print("Governance Health Baseline Compare")
        print("=" * 80)
        print()
        print(f"Baseline: {args.baseline}")
        print(f"Current:  {args.current}")
        print(f"Status:   {payload['status'].upper()}")
        print()
        if regressions:
            print("Regressions:")
            for item in regressions:
                print(f"  - {item}")
            print()
        if warnings:
            print("Warnings:")
            for item in warnings:
                print(f"  - {item}")
            print()
        if notes:
            print("Notes:")
            for item in notes:
                print(f"  - {item}")
            print()
        if not regressions and not warnings and not notes:
            print("No regression detected.")

    if regressions and args.fail_on_regression:
        return 1
    if warnings and args.fail_on_warning:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
