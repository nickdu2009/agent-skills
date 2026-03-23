#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from skill_test_data import EXAMPLE_CASES, GLOBAL_RUBRIC_DIMENSIONS, SKILL_RUBRICS


REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync-cursor-skills.py"


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
    return parser.parse_args()


def validate_examples_exist() -> None:
    missing = [case.file_name for case in EXAMPLE_CASES if not (EXAMPLES_DIR / case.file_name).exists()]
    if missing:
        missing_text = ", ".join(missing)
        raise FileNotFoundError(f"Missing example files referenced by the report generator: {missing_text}")


def run_sync_check() -> int:
    result = subprocess.run(
        [sys.executable, str(SYNC_SCRIPT), "--check"],
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


def main() -> int:
    args = parse_args()

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
