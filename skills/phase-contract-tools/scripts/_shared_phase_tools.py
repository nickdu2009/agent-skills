"""Shared helpers for schema-first phase contract scripts."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml


PHASE_FILES = {
    "roadmap": "roadmap.md",
    "plan": "plan.yaml",
    "wave_guide": "wave-guide.md",
    "execution_index": "execution-index.md",
}

PHASE_ROOT_README = "README.md"
PHASE_SUMMARIES_HEADING = "## Phase Summaries"
VALID_PHASE_STATUSES = ("proposed", "active", "blocked", "done")
PHASE_SUMMARY_LINE_RE = re.compile(
    r"^\-\s+`?(?P<phase>[^`:\s]+)`?\s*:\s*"
    r"goal:\s*(?P<goal>[^;\n]+?)\s*;\s*"
    r"scope:\s*(?P<scope>[^;\n]+?)\s*;\s*"
    r"status:\s*(?P<status>[A-Za-z_][A-Za-z0-9_-]*)\s*$",
    re.IGNORECASE,
)
PHASE_ID_RE = re.compile(r"^phase(?P<number>\d+)$", re.IGNORECASE)


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


def resolve_phase_root(explicit: Path | None = None) -> Path:
    """Resolve the phase docs root from an explicit path, env var, or default."""

    if explicit is not None:
        return explicit.expanduser().resolve()
    env_root = os.environ.get("PHASE_DOCS_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return (Path.cwd() / "docs" / "phases").resolve()


def phase_dir(phase_root: Path, phase: str) -> Path:
    """Return the directory for one phase doc set."""

    return phase_root / phase


def phase_file(phase_root: Path, phase: str, filename: str) -> Path:
    """Return one file path inside a phase doc directory."""

    return phase_dir(phase_root, phase) / filename


def phase_doc_paths(phase_root: Path, phase: str) -> dict[str, Path]:
    """Return the canonical four-file path set for a phase."""

    return {name: phase_file(phase_root, phase, filename) for name, filename in PHASE_FILES.items()}


def phase_root_readme_path(phase_root: Path) -> Path:
    """Return the canonical phase-root summary README path."""

    return phase_root / PHASE_ROOT_README


def normalize_phase_id(value: str) -> str:
    return value.strip().lower()


def phase_sort_key(phase_id: str) -> tuple[int, int | str, str]:
    normalized = normalize_phase_id(phase_id)
    match = PHASE_ID_RE.match(normalized)
    if match:
        return (0, int(match.group("number")), normalized)
    return (1, normalized, normalized)


def iter_phase_dirs(phase_root: Path) -> list[Path]:
    """Return phase directories under the phase root that contain plan.yaml."""

    phase_dirs: list[Path] = []
    if not phase_root.exists():
        return phase_dirs
    for child in phase_root.iterdir():
        if child.is_dir() and (child / PHASE_FILES["plan"]).is_file():
            phase_dirs.append(child)
    return sorted(phase_dirs, key=lambda path: phase_sort_key(path.name))


def discover_phase_ids(phase_root: Path) -> list[str]:
    """Return normalized phase ids discovered from directories under the phase root."""

    return [normalize_phase_id(path.name) for path in iter_phase_dirs(phase_root)]


def render_phase_summary_line(phase: str, goal: str, scope: str, status: str) -> str:
    """Render one canonical phase summary line for the root README."""

    return f"- `{normalize_phase_id(phase)}`: goal: {goal.strip()}; scope: {scope.strip()}; status: {status.strip().lower()}"


def infer_phase(plan_path: Path, data: dict[str, Any]) -> str:
    phase = data.get("phase")
    if isinstance(phase, str) and phase:
        return normalize_phase_id(phase)
    if plan_path.name == PHASE_FILES["plan"]:
        return normalize_phase_id(plan_path.parent.name)
    stem = plan_path.stem
    return normalize_phase_id(stem[:-5] if stem.endswith("-plan") else stem)


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
