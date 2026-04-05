#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "maintainer" / "data"
sys.path.insert(0, str(DATA_DIR))

from skill_test_data import EXAMPLE_CASES, GLOBAL_RUBRIC_DIMENSIONS, SKILL_RUBRICS


EXAMPLES_DIR = REPO_ROOT / "examples"
SYNC_SCRIPT = REPO_ROOT / "maintainer" / "scripts" / "install" / "manage-governance.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print the skill test matrix and optionally generate a Markdown report skeleton."
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format for the scenario matrix.",
    )
    parser.add_argument(
        "--check-sync",
        action="store_true",
        help="Run the local Cursor mirror sync check before printing the matrix.",
    )
    parser.add_argument(
        "--write-report",
        type=Path,
        help="Write a Markdown report skeleton to the given path.",
    )
    parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("REPORT_A", "REPORT_B"),
        help="Compare two filled-in Markdown reports and print score differences.",
    )
    return parser.parse_args()


def validate_examples_exist() -> None:
    missing = [case.file_name for case in EXAMPLE_CASES if not (EXAMPLES_DIR / case.file_name).exists()]
    if missing:
        missing_text = ", ".join(missing)
        raise FileNotFoundError(f"Missing example files referenced by the report generator: {missing_text}")


def run_sync_check() -> int:
    result = subprocess.run(
        [sys.executable, str(SYNC_SCRIPT), "--check-local", "cursor"],
        cwd=REPO_ROOT,
        check=False,
    )
    return result.returncode


def render_markdown_matrix() -> str:
    lines = [
        "# Skill Test Matrix",
        "",
        "| Example | Scenario | Skills | Expectations |",
        "| --- | --- | --- | --- |",
    ]

    for case in EXAMPLE_CASES:
        skills = "<br>".join(f"`{skill}`" for skill in case.skills)
        expectations = "<br>".join(case.expectations)
        lines.append(
            f"| `{case.file_name}` | {case.scenario} | {skills} | {expectations} |"
        )

    return "\n".join(lines)


def render_json_matrix() -> str:
    payload = [
        {
            "file_name": case.file_name,
            "title": case.title,
            "scenario": case.scenario,
            "skills": list(case.skills),
            "expectations": list(case.expectations),
            "skill_rubrics": {skill: list(SKILL_RUBRICS.get(skill, ())) for skill in case.skills},
        }
        for case in EXAMPLE_CASES
    ]
    return json.dumps(payload, indent=2)


def render_report() -> str:
    lines = [
        "# Skill Test Report",
        "",
        "## Run Metadata",
        "",
        "- Date:",
        "- Tester:",
        "- Agent / model:",
        "- Repository revision:",
        "- Mirror sync status:",
        "",
        "## Global Notes",
        "",
        "- Goal of this pass:",
        "- Risks under review:",
        "- Known limitations:",
        "",
        "## Scoring Scale",
        "",
        "- `2`: clearly demonstrated and materially useful.",
        "- `1`: partially demonstrated, ambiguous, or inconsistently applied.",
        "- `0`: missing, contradicted, or replaced by the opposite behavior.",
        "",
        "## Global Rubric",
        "",
        "| Dimension | Score | Notes |",
        "| --- | --- | --- |",
    ]

    for dimension in GLOBAL_RUBRIC_DIMENSIONS:
        lines.append(f"| {dimension} |  |  |")

    lines.extend(
        [
            "",
        "## Scenario Results",
        ]
    )

    for case in EXAMPLE_CASES:
        lines.extend(
            [
                "",
                f"### {case.title}",
                "",
                f"- Example file: `{case.file_name}`",
                f"- Scenario: {case.scenario}",
                f"- Skill composition: {', '.join(f'`{skill}`' for skill in case.skills)}",
                "- Pass / fail:",
                "- Scenario score:",
                "- Observed behavior:",
                "- Expectations met:",
            ]
        )
        lines.extend([f"  - {expectation}" for expectation in case.expectations])
        lines.append("- Skill-specific checks:")
        for skill in case.skills:
            lines.append(f"  - `{skill}`")
            for check in SKILL_RUBRICS.get(skill, ()):
                lines.append(f"    - {check}")
        lines.extend(
            [
                "- Failures or drift:",
                "- Residual risk:",
                "- Follow-up:",
            ]
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            "- Overall result:",
            "- Skills needing revision:",
            "- Suggested next run:",
        ]
    )

    return "\n".join(lines) + "\n"


def write_report(path: Path) -> None:
    output_path = path if path.is_absolute() else REPO_ROOT / path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report(), encoding="utf-8")


_SCORE_RE = re.compile(
    r"^\|\s*(?P<dimension>.+?)\s*\|\s*(?P<score>[012])\s*\|",
    re.MULTILINE,
)


def extract_scores(report_text: str) -> dict[str, int]:
    """Extract dimension/skill → score mappings from a filled-in report."""
    scores: dict[str, int] = {}
    for m in _SCORE_RE.finditer(report_text):
        dim = m.group("dimension").strip().strip("`")
        score = int(m.group("score"))
        if dim in ("Dimension", "---"):
            continue
        scores[dim] = score
    return scores


def compare_reports(path_a: str, path_b: str) -> str:
    file_a = Path(path_a) if Path(path_a).is_absolute() else REPO_ROOT / path_a
    file_b = Path(path_b) if Path(path_b).is_absolute() else REPO_ROOT / path_b

    text_a = file_a.read_text(encoding="utf-8")
    text_b = file_b.read_text(encoding="utf-8")

    scores_a = extract_scores(text_a)
    scores_b = extract_scores(text_b)

    all_dims = sorted(set(scores_a) | set(scores_b))
    if not all_dims:
        return "No scored dimensions found in either report. Are the reports filled in?"

    lines = [
        "# Score Comparison",
        "",
        f"- Report A: `{path_a}`",
        f"- Report B: `{path_b}`",
        "",
        "| Dimension | A | B | Delta |",
        "| --- | --- | --- | --- |",
    ]

    regressions = 0
    improvements = 0
    for dim in all_dims:
        sa = scores_a.get(dim, "-")
        sb = scores_b.get(dim, "-")
        if isinstance(sa, int) and isinstance(sb, int):
            delta = sb - sa
            delta_str = f"+{delta}" if delta > 0 else str(delta)
            if delta < 0:
                regressions += 1
            elif delta > 0:
                improvements += 1
        else:
            delta_str = "n/a"
        lines.append(f"| {dim} | {sa} | {sb} | {delta_str} |")

    lines.extend([
        "",
        f"Improvements: {improvements}  |  Regressions: {regressions}  |  Unchanged: {len(all_dims) - improvements - regressions}",
    ])

    return "\n".join(lines)


def main() -> int:
    args = parse_args()

    if args.compare:
        print(compare_reports(args.compare[0], args.compare[1]))
        return 0

    try:
        validate_examples_exist()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.check_sync:
        sync_exit_code = run_sync_check()
        if sync_exit_code != 0:
            return sync_exit_code

    if args.write_report:
        write_report(args.write_report)

    if args.format == "json":
        print(render_json_matrix())
    else:
        print(render_markdown_matrix())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
