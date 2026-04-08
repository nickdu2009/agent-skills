#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Render an agent prompt from a phase execution schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml
from _shared_phase_tools import (
    accepted_contract_gaps,
    collect_required_contracts_for_pr,
    contract_map,
    find_pr,
    find_wave,
    infer_phase,
    load_plan,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a PR or lane prompt from a phase execution schema.")
    parser.add_argument("--plan", required=True, help="Path to a phase plan file such as docs/phases/phase13/plan.yaml")
    parser.add_argument("--pr", help="Render the prompt for one PR id")
    parser.add_argument("--wave", type=int, help="Wave id for lane-based rendering")
    parser.add_argument("--lane", help="Lane label for lane-based rendering")
    args = parser.parse_args()
    if bool(args.pr) == bool(args.wave or args.lane):
        parser.error("Use either --pr or the pair --wave/--lane.")
    if (args.wave is None) != (args.lane is None):
        parser.error("Both --wave and --lane are required for lane-based rendering.")
    return args


def expand_validation(entries: list[dict[str, Any]], data: dict[str, Any]) -> list[str]:
    profiles = data.get("validation_profiles", {})
    placeholders = data.get("placeholder_conventions", {})
    placeholder_map = {}
    if isinstance(placeholders, dict):
        for item in placeholders.values():
            if isinstance(item, dict) and isinstance(item.get("token"), str):
                placeholder_map[item["token"]] = item.get("meaning", "")

    expanded: list[str] = []
    for entry in entries:
        emitted: list[str] = []
        if entry.get("kind") == "profile":
            profile_id = str(entry.get("ref", ""))
            profile = profiles.get(profile_id, {})
            if isinstance(profile, dict):
                command = profile.get("command", "")
                description = profile.get("description", "")
                if description:
                    emitted.append(f"profile:{profile_id} - {description}")
                if command:
                    emitted.append(command)
            else:
                emitted.append(f"profile:{profile_id}")
        elif entry.get("kind") == "command":
            emitted.append(str(entry.get("command", "")))
        for token, meaning in placeholder_map.items():
            if any(token in line for line in emitted):
                emitted.append(f"{token} -> {meaning}")
        expanded.extend(emitted)
    return dedupe(expanded)


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def render_list(title: str, items: list[str]) -> list[str]:
    if not items:
        return []
    lines = [f"{title}:"]
    lines.extend(f"- {item}" for item in items)
    return lines


def render_read_first(entries: list[dict[str, Any]]) -> list[str]:
    rendered: list[str] = []
    for entry in entries:
        path = str(entry.get("path", ""))
        section = entry.get("section")
        if section:
            rendered.append(f"{path} ({section})")
        else:
            rendered.append(path)
    return rendered


def render_start_condition(start_condition: dict[str, Any]) -> list[str]:
    gate = start_condition.get("gate")
    refs = start_condition.get("refs", [])
    note = start_condition.get("note")
    if gate == "immediate":
        base = "Start condition: immediate"
    elif gate == "after_prs":
        base = f"Start condition: after accepted PRs {', '.join(str(ref) for ref in refs)}"
    elif gate == "after_waves":
        base = f"Start condition: after accepted waves {', '.join(f'Wave {ref}' for ref in refs)}"
    else:
        base = f"Start condition: {gate}"
    lines = [base]
    if note:
        lines.append(f"Start note: {note}")
    return lines


def render_contract_constraints(data: dict[str, Any], pr: dict[str, Any]) -> list[str]:
    contract_ids = collect_required_contracts_for_pr(pr)
    if not contract_ids:
        return []
    contracts = contract_map(data)
    gaps = accepted_contract_gaps(data)
    lines = ["External contract authority:"]
    for contract_id in contract_ids:
        contract = contracts.get(contract_id, {})
        path = contract.get("path", "")
        kind = contract.get("kind", "")
        lines.append(f"- {contract_id}: {path} ({kind})".rstrip())
        owned_scope = contract.get("owned_scope", {})
        if isinstance(owned_scope, dict):
            include = [str(item) for item in owned_scope.get("include", []) if str(item)]
            exclude = [str(item) for item in owned_scope.get("exclude", []) if str(item)]
            mode = owned_scope.get("mode")
            if mode:
                lines.append(f"- {contract_id} owned scope mode: {mode}")
            if include:
                lines.append(f"- {contract_id} owned include: {', '.join(include)}")
            if exclude:
                lines.append(f"- {contract_id} owned exclude: {', '.join(exclude)}")
        matching_gaps = [
            gap for gap in gaps if gap.get("contract") == contract_id
        ]
        if matching_gaps:
            for gap in matching_gaps:
                label = str(gap.get("id") or gap.get("scope") or contract_id)
                prefix = "blocking gap" if bool(gap.get("blocking")) else "accepted gap"
                reason = str(gap.get("reason", "")).strip()
                detail = f"{label} - {reason}" if reason else label
                lines.append(f"- {contract_id} {prefix}: {detail}")
    lines.extend(f"- contract guardrail: {item}" for item in pr.get("contract_guardrails", []) if isinstance(item, str))
    lines.extend(f"- contract done check: {item}" for item in pr.get("contract_done_when", []) if isinstance(item, str))
    return lines


def render_pr_prompt(plan_path: Path, data: dict[str, Any], pr: dict[str, Any], wave: dict[str, Any] | None = None, lane: dict[str, Any] | None = None) -> str:
    phase = infer_phase(plan_path, data)
    wave_label = wave.get("label") if isinstance(wave, dict) else f"Wave {pr.get('wave')}"
    lines = [f"Implement {pr['id']} {pr['title']} for {phase}, {wave_label}."]
    if lane:
        lines.append(f"Lane: {lane.get('lane')} ({lane.get('owner')})")
    depends_on = [str(item) for item in pr.get("depends_on", [])]
    if depends_on:
        lines.append(f"Depends on: {', '.join(depends_on)}")
        lines.append("Do not start implementation until those dependencies are accepted.")
    lines.append("")
    lines.extend(render_list("Phase hard rules", [str(item) for item in data.get("hard_rules", [])]))
    lines.extend([""])
    lines.extend(render_list("Read first in order", render_read_first([item for item in pr.get("read_first", []) if isinstance(item, dict)])))
    if isinstance(pr.get("start_condition"), dict):
        lines.extend([""])
        lines.extend(render_start_condition(pr["start_condition"]))
    allow = [str(item) for item in pr.get("scope", {}).get("allow", [])]
    deny = [str(item) for item in pr.get("scope", {}).get("deny", [])]
    lines.extend([""])
    lines.extend(render_list("You may change", allow))
    lines.extend([""])
    lines.extend(render_list("Do not touch", deny))
    lines.extend(["", f"Goal: {pr.get('goal', '')}"])
    lines.extend([""])
    lines.extend(render_list("Files likely involved", [str(item) for item in pr.get("files", [])]))
    lines.extend([""])
    lines.extend(render_list("Expected changes", [str(item) for item in pr.get("expected_changes", [])]))
    lines.extend([""])
    lines.extend(render_list("Guardrails", [str(item) for item in pr.get("guardrails", [])]))
    lines.extend([""])
    lines.extend(render_contract_constraints(data, pr))
    lines.extend([""])
    lines.extend(render_list("Non-goals", [str(item) for item in pr.get("non_goals", [])]))
    lines.extend([""])
    lines.extend(render_list("Validation", expand_validation([item for item in pr.get("validation", []) if isinstance(item, dict)], data)))
    lines.extend([""])
    lines.extend(render_list("Done when all are true", [str(item) for item in pr.get("done_when", [])]))
    lines.extend([""])
    lines.extend(render_list("Contract done when all are true", [str(item) for item in pr.get("contract_done_when", []) if isinstance(item, str)]))
    return "\n".join(line for line in lines if line is not None)


def render_role_prompt(plan_path: Path, data: dict[str, Any], wave: dict[str, Any], role: dict[str, Any], lane: dict[str, Any]) -> str:
    phase = infer_phase(plan_path, data)
    lines = [f"Act on role {role['id']} for {phase}, {wave['label']}."]
    lines.append(f"Lane: {lane.get('lane')} ({lane.get('owner')})")
    if role.get("kind"):
        lines.append(f"Role kind: {role.get('kind')}")
    lines.append("")
    lines.extend(render_list("Phase hard rules", [str(item) for item in data.get("hard_rules", [])]))
    lines.extend([""])
    read_first = [item for item in role.get("read_first", []) if isinstance(item, dict)]
    lines.extend(render_list("Read first in order", render_read_first(read_first)))
    if isinstance(role.get("start_condition"), dict):
        lines.extend([""])
        lines.extend(render_start_condition(role["start_condition"]))
    allow = [str(item) for item in role.get("scope", {}).get("allow", [])]
    deny = [str(item) for item in role.get("scope", {}).get("deny", [])]
    lines.extend([""])
    lines.extend(render_list("You may change", allow))
    lines.extend([""])
    lines.extend(render_list("Do not touch", deny))
    lines.extend(["", f"Goal: {role.get('goal', '')}"])
    lines.extend([""])
    lines.extend(render_list("Guardrails", [str(item) for item in role.get("guardrails", [])]))
    lines.extend([""])
    lines.extend(render_list("Validation", expand_validation([item for item in role.get("validation", []) if isinstance(item, dict)], data)))
    lines.extend([""])
    lines.extend(render_list("Done when all are true", [str(item) for item in role.get("done_when", [])]))
    return "\n".join(line for line in lines if line is not None)


def render_for_lane(plan_path: Path, data: dict[str, Any], wave_id: int, lane_name: str) -> str:
    wave = find_wave(data, wave_id)
    lane = next(
        (
            item
            for item in wave.get("lane_setup", [])
            if isinstance(item, dict) and str(item.get("lane", "")).lower() == lane_name.lower()
        ),
        None,
    )
    if lane is None:
        raise KeyError(f"unknown lane `{lane_name}` in wave {wave_id}")
    ref_kind = lane.get("ref_kind")
    ref = lane.get("ref")
    if ref_kind == "pr":
        pr = find_pr(data, str(ref))
        return render_pr_prompt(plan_path, data, pr, wave=wave, lane=lane)
    if ref_kind == "role":
        role = next(
            (
                item
                for item in wave.get("roles", [])
                if isinstance(item, dict) and item.get("id") == ref
            ),
            None,
        )
        if role is None:
            raise KeyError(f"unknown role `{ref}` in wave {wave_id}")
        return render_role_prompt(plan_path, data, wave, role, lane)
    raise KeyError(f"unsupported ref_kind `{ref_kind}`")


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    try:
        data = load_plan(plan_path)
        if args.pr:
            pr = find_pr(data, args.pr)
            wave = find_wave(data, int(pr.get("wave")))
            print(render_pr_prompt(plan_path, data, pr, wave=wave))
        else:
            print(render_for_lane(plan_path, data, args.wave, args.lane))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR render-agent-prompt: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
