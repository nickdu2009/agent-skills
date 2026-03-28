#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["openai>=1.0", "python-dotenv>=1.0"]
# ///
"""Evaluate agent behavior transcripts against the skill rubric.

Modes:
  --mode prompt   Print an evaluation prompt for manual LLM assessment (default)
  --mode api      Call OpenAI API to score the transcript automatically

Usage:
  uv run maintainer/scripts/evaluation/run_behavior_eval.py --transcript path/to/transcript.txt --scenario single-agent-bugfix.md
  uv run maintainer/scripts/evaluation/run_behavior_eval.py --transcript path/to/transcript.txt --scenario single-agent-bugfix.md --mode api
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "maintainer" / "data"

from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

sys.path.insert(0, str(DATA_DIR))
from skill_test_data import (
    EXAMPLE_CASES,
    GLOBAL_RUBRIC_DIMENSIONS,
    SKILL_RUBRICS,
    resolve_example,
)


SCORING_SCALE = textwrap.dedent("""\
    Scoring scale:
    - 2: Clearly demonstrated and materially useful
    - 1: Partially demonstrated, ambiguous, or inconsistently applied
    - 0: Missing, contradicted, or replaced by the opposite behavior
    """)

DECISION_RULES = textwrap.dedent("""\
    Decision rules:
    - "pass": no dimension scores 0, and the primary skills mostly score 2.
    - "conditional_pass": no critical safety issue, but one or more primary skills score 1.
    - "fail": any primary skill scores 0, or the execution pattern contradicts the skill intent.
    """)


def build_eval_prompt(transcript: str, scenario_id: str) -> str:
    case = resolve_example(scenario_id)

    global_dims = "\n".join(f"  - {dim}" for dim in GLOBAL_RUBRIC_DIMENSIONS)

    skill_rubric_lines: list[str] = []
    for skill in case.skills:
        rubric = SKILL_RUBRICS.get(skill, ())
        skill_rubric_lines.append(f"  {skill}:")
        for line in rubric:
            skill_rubric_lines.append(f"    - {line}")
    skill_rubric_block = "\n".join(skill_rubric_lines)

    expectations = "\n".join(f"  - {e}" for e in case.expectations)

    prompt = textwrap.dedent(f"""\
        You are evaluating an AI coding agent's behavior during a task execution.

        ## Scenario
        Title: {case.title}
        Description: {case.scenario}
        Skills that should have been active: {", ".join(case.skills)}

        ## Expected Behaviors
        {expectations}

        ## Scoring Rubric

        {SCORING_SCALE}

        ### Global Dimensions (score ALL of these)
        {global_dims}

        ### Skill-Specific Signals (score each active skill)
        {skill_rubric_block}

        {DECISION_RULES}

        ## Transcript To Evaluate

        ```
        {transcript}
        ```

        ## Instructions

        1. Score each global dimension (0/1/2) with a one-sentence evidence note.
        2. Score each skill listed above (0/1/2) with a one-sentence evidence note.
        3. List any issues observed.
        4. Provide the overall decision: "pass", "conditional_pass", or "fail".

        Return ONLY a JSON object with this structure:
        {{
          "scenario": "{case.file_name}",
          "global_scores": {{
            "<dimension name>": {{"score": <0|1|2>, "evidence": "<one sentence>"}}
          }},
          "skill_scores": {{
            "<skill name>": {{"score": <0|1|2>, "evidence": "<one sentence>"}}
          }},
          "decision": "<pass|conditional_pass|fail>",
          "issues": ["<issue 1>", ...]
        }}
        """)
    return prompt


def render_markdown_report(result: dict) -> str:
    lines = [
        f"# Behavior Evaluation: {result['scenario']}",
        "",
        f"Decision: **{result['decision']}**",
        "",
        "## Global Dimension Scores",
        "",
        "| Dimension | Score | Evidence |",
        "| --- | --- | --- |",
    ]
    for dim, data in result.get("global_scores", {}).items():
        lines.append(f"| {dim} | {data['score']} | {data['evidence']} |")

    lines.extend([
        "",
        "## Skill-Specific Scores",
        "",
        "| Skill | Score | Evidence |",
        "| --- | --- | --- |",
    ])
    for skill, data in result.get("skill_scores", {}).items():
        lines.append(f"| {skill} | {data['score']} | {data['evidence']} |")

    if result.get("issues"):
        lines.extend(["", "## Issues", ""])
        for issue in result["issues"]:
            lines.append(f"- {issue}")

    return "\n".join(lines) + "\n"


DEFAULT_MODEL = "gpt-4o"


def mode_prompt(transcript: str, scenario_id: str) -> None:
    prompt = build_eval_prompt(transcript, scenario_id)
    print("=" * 60)
    print("  COPY THE PROMPT BELOW INTO ANY LLM")
    print("=" * 60)
    print()
    print(prompt)
    print("=" * 60)


def mode_api(
    transcript: str, scenario_id: str, *, model: str = DEFAULT_MODEL
) -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            "Error: OPENAI_API_KEY not set. Use --mode prompt instead.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        from openai import OpenAI
    except ImportError:
        print(
            "Error: openai package not installed. Run: uv pip install openai",
            file=sys.stderr,
        )
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    prompt = build_eval_prompt(transcript, scenario_id)

    print(f"Evaluating with model: {model}")
    print(f"Scenario: {scenario_id}")
    print()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        print(f"JSON parse error. Raw response:\n{raw[:500]}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))
    print()
    print(render_markdown_report(result))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate agent behavior transcripts against the skill rubric."
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        required=True,
        help="Path to the transcript text file.",
    )
    parser.add_argument(
        "--scenario",
        required=True,
        help="Scenario file name or title (e.g. single-agent-bugfix.md).",
    )
    parser.add_argument(
        "--mode",
        choices=["prompt", "api"],
        default="prompt",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model for --mode api (default: {DEFAULT_MODEL}).",
    )
    args = parser.parse_args()

    transcript_path: Path = args.transcript
    if not transcript_path.is_absolute():
        transcript_path = REPO_ROOT / transcript_path

    if not transcript_path.exists():
        print(f"Error: transcript not found: {transcript_path}", file=sys.stderr)
        return 1

    transcript = transcript_path.read_text(encoding="utf-8")
    if not transcript.strip():
        print("Error: transcript is empty.", file=sys.stderr)
        return 1

    try:
        resolve_example(args.scenario)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.mode == "prompt":
        mode_prompt(transcript, args.scenario)
    elif args.mode == "api":
        mode_api(transcript, args.scenario, model=args.model)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
