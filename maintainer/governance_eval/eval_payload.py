"""Shared helpers for governance eval JSON payloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def summarize_cli_results(cli_results: list[dict[str, Any]], *, skipped: bool = False) -> dict[str, Any]:
    """Return summary counts for one CLI."""
    if skipped:
        return {
            "status": "skipped",
            "pass_count": 0,
            "fail_count": 0,
            "error_count": 0,
            "calibrated_count": 0,
            "miscalibrated_count": 0,
            "executed_case_count": 0,
        }

    pass_count = sum(1 for result in cli_results if result["verdict"] == "PASS")
    fail_count = sum(1 for result in cli_results if result["verdict"] == "FAIL")
    error_count = sum(1 for result in cli_results if result["verdict"] == "ERROR")
    calibrated_count = sum(1 for result in cli_results if result["calibrated"])
    miscalibrated_count = len(cli_results) - calibrated_count
    status = "pass" if all(result["calibrated"] for result in cli_results) else "fail"
    return {
        "status": status,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "error_count": error_count,
        "calibrated_count": calibrated_count,
        "miscalibrated_count": miscalibrated_count,
        "executed_case_count": len(cli_results),
    }


def summarize_overall_results(
    results: dict[str, dict[str, Any]],
    requested_case_count: int,
) -> dict[str, Any]:
    """Return aggregate summary across all requested CLIs."""
    executed = [case for cli_data in results.values() for case in cli_data["cases"]]
    pass_count = sum(1 for result in executed if result["verdict"] == "PASS")
    fail_count = sum(1 for result in executed if result["verdict"] == "FAIL")
    error_count = sum(1 for result in executed if result["verdict"] == "ERROR")
    calibrated_count = sum(1 for result in executed if result["calibrated"])
    miscalibrated_count = len(executed) - calibrated_count
    skipped_cli_count = sum(1 for cli_data in results.values() if cli_data["skipped_preflight"])
    if skipped_cli_count:
        status = "blocked"
    else:
        status = "pass" if all(result["calibrated"] for result in executed) else "fail"
    return {
        "status": status,
        "requested_case_count": requested_case_count,
        "requested_cli_count": len(results),
        "skipped_cli_count": skipped_cli_count,
        "executed_case_count": len(executed),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "error_count": error_count,
        "calibrated_count": calibrated_count,
        "miscalibrated_count": miscalibrated_count,
    }


def load_eval_payload(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"eval JSON not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid eval JSON in {path}: {exc}") from exc

    summary = payload.get("summary")
    results = payload.get("results")
    config = payload.get("config")
    if not isinstance(summary, dict) or not isinstance(results, dict) or not isinstance(config, dict):
        raise ValueError(f"eval JSON missing config/results/summary payload: {path}")
    return payload


def merge_eval_payloads(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    if not payloads:
        raise ValueError("at least one eval payload is required for merge")

    merged_results: dict[str, dict[str, Any]] = {}
    requested_case_ids: list[str] | None = None
    runs_override: int | None = None
    skip_preflight: bool | None = None
    model_override: str | None = None

    for payload in payloads:
        config = payload["config"]
        payload_case_ids = config.get("requested_case_ids")
        if not isinstance(payload_case_ids, list):
            raise ValueError("eval payload missing requested_case_ids")
        if requested_case_ids is None:
            requested_case_ids = list(payload_case_ids)
        elif requested_case_ids != list(payload_case_ids):
            raise ValueError("cannot merge eval payloads with different requested_case_ids")

        payload_runs = config.get("runs_override")
        if runs_override is None:
            runs_override = payload_runs
        elif runs_override != payload_runs:
            raise ValueError("cannot merge eval payloads with different runs_override")

        payload_skip_preflight = config.get("skip_preflight")
        if skip_preflight is None:
            skip_preflight = payload_skip_preflight
        elif skip_preflight != payload_skip_preflight:
            raise ValueError("cannot merge eval payloads with different skip_preflight values")

        payload_model = config.get("model_override")
        if model_override is None:
            model_override = payload_model
        elif model_override != payload_model:
            raise ValueError("cannot merge eval payloads with different model_override values")

        for cli_name, cli_payload in payload["results"].items():
            if cli_name in merged_results:
                raise ValueError(f"duplicate CLI in merged eval payloads: {cli_name}")
            merged_results[cli_name] = cli_payload

    assert requested_case_ids is not None
    merged_config = {
        "model_override": model_override,
        "requested_clis": list(merged_results),
        "requested_case_ids": requested_case_ids,
        "runs_override": runs_override,
        "skip_preflight": skip_preflight,
    }
    merged_summary = summarize_overall_results(merged_results, len(requested_case_ids))
    return {
        "config": merged_config,
        "results": merged_results,
        "summary": merged_summary,
    }
