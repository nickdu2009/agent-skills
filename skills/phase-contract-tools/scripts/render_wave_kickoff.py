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
from _shared_phase_tools import contract_gaps_for_ids, contract_map, collect_required_contracts_for_wave, find_wave, infer_phase, load_plan


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


def wave_contract_guardrails(data: dict[str, Any], wave: dict[str, Any]) -> list[str]:
    pr_lookup = {pr["id"]: pr for pr in data.get("prs", []) if isinstance(pr, dict) and isinstance(pr.get("id"), str)}
    ordered: list[str] = []
    seen: set[str] = set()
    for pr_id in wave.get("prs", []):
        pr = pr_lookup.get(pr_id, {})
        for item in pr.get("contract_guardrails", []):
            if isinstance(item, str) and item not in seen:
                seen.add(item)
                ordered.append(item)
    return ordered


def render_wave(plan_path: Path, data: dict[str, Any], wave: dict[str, Any]) -> str:
    phase = infer_phase(plan_path, data)
    titles = pr_title_map(data)
    required_contracts = collect_required_contracts_for_wave(data, wave)
    contracts = contract_map(data)
    blocking_gaps, accepted_gaps = contract_gaps_for_ids(data, required_contracts)
    contract_guardrails = wave_contract_guardrails(data, wave)
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
    if required_contracts:
        lines.append("")
        lines.append("External contracts:")
        for contract_id in required_contracts:
            contract = contracts.get(contract_id, {})
            detail = f"{contract.get('path', '')} ({contract.get('kind', '')})".rstrip()
            lines.append(f"- {contract_id}: {detail}")
            owned_scope = contract.get("owned_scope", {})
            if isinstance(owned_scope, dict):
                include = [str(item) for item in owned_scope.get("include", []) if str(item)]
                exclude = [str(item) for item in owned_scope.get("exclude", []) if str(item)]
                if include:
                    lines.append(f"- {contract_id} owned include: {', '.join(include)}")
                if exclude:
                    lines.append(f"- {contract_id} owned exclude: {', '.join(exclude)}")
        if blocking_gaps:
            lines.append("- blocking gaps: " + ", ".join(blocking_gaps))
        if accepted_gaps:
            lines.append("- accepted gaps: " + ", ".join(accepted_gaps))
        if contract_guardrails:
            lines.append("Contract guardrails:")
            for item in contract_guardrails:
                lines.append(f"- {item}")
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
