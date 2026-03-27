"""Shared helpers for schema-first phase contract scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


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
