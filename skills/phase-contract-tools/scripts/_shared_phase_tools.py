"""Shared helpers for schema-first phase contract scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class Issue:
    """Structured validation finding used by all contract validators."""

    def __init__(
        self,
        path: str,
        message: str,
        expected: str | None,
        location: str,
        repair: str | None = None,
    ) -> None:
        self.path = path
        self.message = message
        self.expected = expected
        self.location = location
        self.repair = repair

    def render(self, level: str) -> str:
        lines = [f"{level} {self.path}: {self.message}"]
        if self.expected:
            lines.append(f"expected: {self.expected}")
        if self.repair:
            lines.append(f"repair: {self.repair}")
        lines.append(f"location: {self.location}")
        return "\n".join(lines)


def load_plan(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Top-level YAML value must be a mapping.")
    return data


def infer_phase(plan_path: Path, data: dict[str, Any]) -> str:
    phase = data.get("phase")
    if isinstance(phase, str) and phase:
        return phase
    stem = plan_path.stem
    return stem[:-5] if stem.endswith("-plan") else stem


def find_pr(data: dict[str, Any], pr_id: str) -> dict[str, Any]:
    for pr in data.get("prs", []):
        if isinstance(pr, dict) and pr.get("id") == pr_id:
            return pr
    raise KeyError(f"unknown PR id: {pr_id}")


def find_wave(data: dict[str, Any], wave_id: int) -> dict[str, Any]:
    for wave in data.get("waves", []):
        if isinstance(wave, dict) and wave.get("id") == wave_id:
            return wave
    raise KeyError(f"unknown wave id: {wave_id}")


def find_lane(wave: dict[str, Any], lane_name: str) -> dict[str, Any]:
    for lane in wave.get("lane_setup", []):
        if isinstance(lane, dict) and str(lane.get("lane", "")).lower() == lane_name.lower():
            return lane
    raise KeyError(f"unknown lane `{lane_name}` in wave {wave.get('id')}")


def contract_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    contracts: dict[str, dict[str, Any]] = {}
    for item in data.get("external_contracts", []):
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            contracts[item["id"]] = item
    return contracts


def accepted_contract_gaps(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in data.get("accepted_contract_gaps", []) if isinstance(item, dict)]


def collect_required_contracts_for_pr(pr: dict[str, Any]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for item in pr.get("required_contracts", []):
        if isinstance(item, str) and item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def collect_required_contracts_for_wave(data: dict[str, Any], wave: dict[str, Any]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    pr_lookup = {pr["id"]: pr for pr in data.get("prs", []) if isinstance(pr, dict) and isinstance(pr.get("id"), str)}
    for pr_id in wave.get("prs", []):
        if not isinstance(pr_id, str):
            continue
        for contract_id in collect_required_contracts_for_pr(pr_lookup.get(pr_id, {})):
            if contract_id not in seen:
                seen.add(contract_id)
                ordered.append(contract_id)
    return ordered


def contract_gaps_for_ids(data: dict[str, Any], contract_ids: list[str]) -> tuple[list[str], list[str]]:
    blocking: list[str] = []
    accepted: list[str] = []
    contract_set = set(contract_ids)
    for gap in accepted_contract_gaps(data):
        contract_id = gap.get("contract")
        if contract_id not in contract_set:
            continue
        label = str(gap.get("id") or gap.get("scope") or contract_id)
        if bool(gap.get("blocking")):
            blocking.append(label)
        else:
            accepted.append(label)
    return blocking, accepted
