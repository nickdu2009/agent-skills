#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Validate the schema-first phase doc set against the execution schema."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from _shared_phase_tools import Issue, PHASE_FILES, phase_doc_paths, resolve_phase_root


PR_ID_RE = re.compile(r"\bP\d+-\d+\b")
WAVE_HEADING_RE = re.compile(r"^## Wave (\d+):\s*(.+)$", re.MULTILINE)
WAVE_SUMMARY_ROW_RE = re.compile(r"^\|\s*Wave (\d+)\s*\|.*\|\s*(P\d+-\d+)\s*\|$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a schema-first phase doc set.")
    parser.add_argument("--phase-root", help="Root directory that contains per-phase doc directories.")
    parser.add_argument("--phase", required=True, help="Phase prefix such as phase13.")
    return parser.parse_args()


def normalize_phase(raw: str) -> str:
    phase = raw.strip().lower()
    if phase.endswith(".md"):
        phase = phase[:-3]
    return phase.rstrip("-")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(read_text(path))
    if not isinstance(data, dict):
        raise ValueError("Top-level YAML value must be a mapping.")
    return data


def line_of(text: str, needle: str) -> int | None:
    for idx, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return idx
    return None


def add_issue(
    bucket: list[Issue],
    path: str,
    message: str,
    expected: str | None,
    location: str,
    repair: str | None = None,
) -> None:
    bucket.append(Issue(path, message, expected, location, repair))


def section_text(text: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def validate_doc_set(phase_root: Path, phase: str) -> tuple[list[Issue], list[Issue]]:
    errors: list[Issue] = []
    warnings: list[Issue] = []

    phase_paths = phase_doc_paths(phase_root, phase)
    phase_path = phase_paths["plan"].parent
    roadmap_path = phase_paths["roadmap"]
    plan_path = phase_paths["plan"]
    wave_guide_path = phase_paths["wave_guide"]
    index_path = phase_paths["execution_index"]

    required = [roadmap_path, plan_path, wave_guide_path, index_path]
    allowed_names = {path.name for path in required}
    for path in required:
        if not path.exists():
            add_issue(errors, path.name, "required phase doc is missing.", expected=path.name, location=str(path), repair=f"create `{path.name}` so the strict four-file set is complete")
    if errors:
        return errors, warnings

    phase_files = {path.name for path in phase_path.iterdir() if path.is_file()}
    extra_phase_files = sorted(phase_files - allowed_names)
    if extra_phase_files:
        add_issue(
            errors,
            "doc-set.extra-files",
            f"found extra phase docs outside the strict four-file model: {extra_phase_files}.",
            expected=f"only {sorted(allowed_names)}",
            location=str(phase_path),
            repair="delete the extra phase files or fold their content into roadmap, plan.yaml, wave-guide, or execution-index",
        )

    roadmap_text = read_text(roadmap_path)
    plan = load_yaml(plan_path)
    wave_guide_text = read_text(wave_guide_path)
    index_text = read_text(index_path)
    external_contracts = [item for item in plan.get("external_contracts", []) if isinstance(item, dict)]

    pr_ids = {pr["id"] for pr in plan.get("prs", []) if isinstance(pr, dict) and isinstance(pr.get("id"), str)}
    waves = {wave["id"]: wave for wave in plan.get("waves", []) if isinstance(wave, dict) and isinstance(wave.get("id"), int)}
    control_prs = {wave_id: wave.get("control_pr") for wave_id, wave in waves.items()}

    index_start_here = section_text(index_text, "Start Here")
    for expected_name in (roadmap_path.name, plan_path.name, wave_guide_path.name):
        if expected_name not in index_start_here:
            location = f"{index_path}:{line_of(index_text, '## Start Here') or 1}"
            add_issue(errors, "execution-index.start-here", f"missing `{expected_name}` in Start Here.", expected=f"include `{expected_name}`", location=location, repair=f"add `{expected_name}` to the Start Here list")

    wave_guide_intro_line = line_of(wave_guide_text, plan_path.name)
    if wave_guide_intro_line is None:
        add_issue(
            errors,
            "wave-guide.schema-reference",
            f"missing reference to `{plan_path.name}`.",
            expected=f"mention `{plan_path.name}` as the machine-readable source",
            location=str(wave_guide_path),
            repair=f"add an intro line that points readers to `{plan_path.name}`",
        )

    authority_section = section_text(index_text, "Execution Authority")
    if authority_section:
        yaml_pos = authority_section.find(plan_path.name)
        roadmap_pos = authority_section.find(roadmap_path.name)
        if yaml_pos == -1:
            add_issue(
                errors,
                "execution-index.authority",
                f"`{plan_path.name}` is not listed in Execution Authority.",
                expected=f"list `{plan_path.name}` as the execution authority",
                location=f"{index_path}:{line_of(index_text, '## Execution Authority') or 1}",
                repair=f"add `{plan_path.name}` as the first authority item",
            )
        elif roadmap_pos != -1 and yaml_pos > roadmap_pos:
            add_issue(
                errors,
                "execution-index.authority",
                f"`{plan_path.name}` appears after `{roadmap_path.name}` in Execution Authority.",
                expected=f"list `{plan_path.name}` before markdown docs",
                location=f"{index_path}:{line_of(index_text, '## Execution Authority') or 1}",
                repair=f"move `{plan_path.name}` ahead of markdown docs in Execution Authority",
            )
    else:
        add_issue(
            warnings,
            "execution-index.authority",
            "Execution Authority section is missing.",
            expected="add an Execution Authority section",
            location=str(index_path),
            repair="add an Execution Authority section that lists plan.yaml first",
        )

    wave_headings = {int(number): label.strip() for number, label in WAVE_HEADING_RE.findall(wave_guide_text)}
    if set(wave_headings) != set(waves):
        add_issue(
            errors,
            "wave-guide.wave-headings",
            f"wave headings {sorted(wave_headings)} do not match schema waves {sorted(waves)}.",
            expected=f"one heading per schema wave {sorted(waves)}",
            location=str(wave_guide_path),
            repair="add or remove wave sections so the wave-guide has exactly one section per schema wave",
        )

    wave_guide_prs = set(PR_ID_RE.findall(wave_guide_text))
    unknown_wave_guide_prs = sorted(wave_guide_prs - pr_ids)
    if unknown_wave_guide_prs:
        add_issue(
            errors,
            "wave-guide.pr-refs",
            f"wave guide references unknown PR ids {unknown_wave_guide_prs}.",
            expected=f"one of {sorted(pr_ids)}",
            location=str(wave_guide_path),
            repair="replace the unknown PR ids with PR ids that exist in plan.yaml",
        )

    summary_rows = {int(wave_id): control_pr for wave_id, control_pr in WAVE_SUMMARY_ROW_RE.findall(index_text)}
    if summary_rows and set(summary_rows) != set(waves):
        add_issue(
            errors,
            "execution-index.wave-summary",
            f"Wave Summary rows {sorted(summary_rows)} do not match schema waves {sorted(waves)}.",
            expected=f"rows for waves {sorted(waves)}",
            location=f"{index_path}:{line_of(index_text, '## Wave Summary') or 1}",
            repair="make the Wave Summary table contain one row per schema wave",
        )
    for wave_id, control_pr in summary_rows.items():
        expected_control = control_prs.get(wave_id)
        if expected_control and control_pr != expected_control:
            add_issue(
                errors,
                "execution-index.wave-summary",
                f"Wave {wave_id} control PR `{control_pr}` does not match schema `{expected_control}`.",
                expected=expected_control,
                location=f"{index_path}:{line_of(index_text, f'| Wave {wave_id} ') or line_of(index_text, f'| Wave {wave_id}|') or 1}",
                repair=f"change the Wave {wave_id} control PR to `{expected_control}`",
            )

    if plan_path.name not in index_text:
        add_issue(
            errors,
            "execution-index.plan-ref",
            f"`{plan_path.name}` is not referenced anywhere in the execution index.",
            expected=f"reference `{plan_path.name}`",
            location=str(index_path),
            repair=f"reference `{plan_path.name}` in the execution index reading path and authority section",
        )

    deprecated_names = (
        "first-wave-pr-breakdown.md",
        "parallel-matrix.md",
        "pr-delivery-plan.md",
        "pr-parallelization-plan.md",
        "pr-plan.md",
        f"{phase}-first-wave-pr-breakdown.md",
        f"{phase}-parallel-matrix.md",
        f"{phase}-pr-delivery-plan.md",
        f"{phase}-pr-parallelization-plan.md",
        f"{phase}-pr-plan.md",
    )
    for deprecated in deprecated_names:
        if deprecated in index_text or deprecated in wave_guide_text:
            location_file = index_path if deprecated in index_text else wave_guide_path
            line = line_of(index_text if location_file == index_path else wave_guide_text, deprecated) or 1
            add_issue(
                errors,
                "deprecated-doc-ref",
                f"deprecated execution doc `{deprecated}` is still referenced.",
                expected="remove the reference and keep only roadmap, plan.yaml, wave-guide, and execution-index",
                location=f"{location_file}:{line}",
                repair=f"remove `{deprecated}` and replace it with one of the four allowed phase files",
            )

    roadmap_done_when_line = line_of(roadmap_text, "## Phase Done-When") or line_of(roadmap_text, "## Done-When")
    if roadmap_done_when_line is None:
        add_issue(
            warnings,
            "roadmap.done-when",
            "roadmap is missing a clear done-when section.",
            expected="add `## Phase Done-When` or `## Done-When`",
            location=str(roadmap_path),
            repair="add a final done-when section to the roadmap",
        )

    if external_contracts:
        external_contract_section = section_text(roadmap_text, "External Contract Authority")
        if not external_contract_section:
            add_issue(
                errors,
                "roadmap.external-contract-authority",
                "roadmap is missing an External Contract Authority section for a contract-bound phase.",
                expected="add `## External Contract Authority`",
                location=str(roadmap_path),
                repair="add an External Contract Authority section that names the contract source and owned subset",
            )
        else:
            lowered_contract_section = external_contract_section.lower()
            if "owned subset" not in lowered_contract_section:
                add_issue(
                    errors,
                    "roadmap.external-contract-authority",
                    "roadmap External Contract Authority section does not describe the owned subset.",
                    expected="mention the owned subset explicitly",
                    location=f"{roadmap_path}:{line_of(roadmap_text, '## External Contract Authority') or 1}",
                    repair="add an owned subset line to the roadmap External Contract Authority section",
                )
            if "excluded subset" not in lowered_contract_section:
                add_issue(
                    errors,
                    "roadmap.external-contract-authority",
                    "roadmap External Contract Authority section does not describe the excluded subset.",
                    expected="mention the excluded subset explicitly",
                    location=f"{roadmap_path}:{line_of(roadmap_text, '## External Contract Authority') or 1}",
                    repair="add an excluded subset line to the roadmap External Contract Authority section",
                )
        goals_section = section_text(roadmap_text, "Goals").lower()
        done_when_section = (section_text(roadmap_text, "Phase Done-When") or section_text(roadmap_text, "Done-When")).lower()
        if "contract" not in goals_section and "align" not in goals_section:
            add_issue(
                errors,
                "roadmap.goals.contract-alignment",
                "roadmap goals do not mention contract alignment for a contract-bound phase.",
                expected="mention contract alignment in roadmap goals",
                location=f"{roadmap_path}:{line_of(roadmap_text, '## Goals') or 1}",
                repair="add a goal that names the external contract alignment outcome",
            )
        if "contract" not in done_when_section and "align" not in done_when_section:
            add_issue(
                errors,
                "roadmap.done-when.contract-alignment",
                "roadmap done-when does not mention contract alignment for a contract-bound phase.",
                expected="mention contract alignment in Phase Done-When",
                location=f"{roadmap_path}:{roadmap_done_when_line or 1}",
                repair="add a done-when item that states the owned subset is aligned or only accepted non-blocking gaps remain",
            )
        for contract in external_contracts:
            contract_path_value = contract.get("path")
            if isinstance(contract_path_value, str) and contract_path_value not in roadmap_text:
                add_issue(
                    errors,
                    "roadmap.external-contract-authority",
                    f"roadmap does not mention contract source `{contract_path_value}`.",
                    expected=f"mention `{contract_path_value}` in the External Contract Authority section",
                    location=str(roadmap_path),
                    repair=f"reference `{contract_path_value}` in the roadmap contract authority section",
                )

    return errors, warnings


def main() -> int:
    args = parse_args()
    phase_root = resolve_phase_root(Path(args.phase_root) if args.phase_root else None)
    phase = normalize_phase(args.phase)
    if not phase_root.exists():
        print(f"ERROR phase-root: phase root directory not found.\nlocation: {phase_root}")
        return 1

    try:
        errors, warnings = validate_doc_set(phase_root, phase)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR doc-set: unable to validate doc set: {exc}\nlocation: {phase_root / phase}")
        return 1

    if errors:
        print("Doc-set validation failed:")
        for issue in errors:
            print(issue.render("ERROR"))
        for issue in warnings:
            print(issue.render("WARN"))
        return 1

    print("Doc-set validation passed.")
    for issue in warnings:
        print(issue.render("WARN"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
