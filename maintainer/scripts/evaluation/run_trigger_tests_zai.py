#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml", "openai>=1.0", "python-dotenv>=1.0"]
# ///
"""Run trigger tests using z.ai models.

This is an adapter for run_trigger_tests.py that uses z.ai's OpenAI-compatible API.

Environment variables:
  ZAI_API_KEY      - Your z.ai API key (required)
  ZAI_BASE_URL     - z.ai API base URL (default: https://api.z.ai/v1)
  ZAI_MODEL        - z.ai model name (default: deepseek-chat)

Usage:
  export ZAI_API_KEY="your-api-key"
  python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode report
  python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode api
  python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode api --model deepseek-chat
  python3 maintainer/scripts/evaluation/run_trigger_tests_zai.py --mode api --category pre-phase
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
DATA_DIR = REPO_ROOT / "maintainer" / "data"

from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

sys.path.insert(0, str(DATA_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from trigger_test_data import (
    ALL_TRIGGER_CASES,
    CATEGORIES,
    TriggerCase,
    cases_by_category,
    resolve_trigger_case,
)


def extract_descriptions() -> dict[str, str]:
    """Extract the description field from each SKILL.md frontmatter."""
    descriptions: dict[str, str] = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        text = skill_file.read_text(encoding="utf-8")
        in_frontmatter = False
        desc_lines: list[str] = []
        for line in text.splitlines():
            if line.strip() == "---":
                if in_frontmatter:
                    break
                in_frontmatter = True
                continue
            if in_frontmatter and line.startswith("description:"):
                desc_lines.append(line[len("description:"):].strip())
        if desc_lines:
            descriptions[skill_dir.name] = " ".join(desc_lines)
    return descriptions


def build_available_skills_block(descriptions: dict[str, str]) -> str:
    lines = []
    for name, desc in sorted(descriptions.items()):
        lines.append(f"- {name}: {desc}")
    return "\n".join(lines)


SYSTEM_TEMPLATE = textwrap.dedent("""\
    You are evaluating which agent skills should be triggered by a user prompt.

    Below is the list of available skills with their descriptions. For each user
    prompt, decide which skills (if any) the agent should load. Return ONLY a
    JSON object with two fields:
      "triggers": [list of skill names to load]
      "reasoning": "one sentence explaining the decision"

    Available skills:
    {skills_block}
    """)


def build_eval_prompt(case: TriggerCase, skills_block: str) -> str:
    return (
        SYSTEM_TEMPLATE.format(skills_block=skills_block)
        + f"\nUser prompt: \"{case.prompt}\"\n"
    )


def score_result(
    case: TriggerCase, actual_triggers: list[str]
) -> tuple[str, list[str]]:
    """Return (verdict, issues)."""
    issues: list[str] = []
    actual_set = set(actual_triggers)

    for expected in case.expected_triggers:
        if expected not in actual_set:
            issues.append(f"FALSE NEGATIVE: expected {expected} but not triggered")

    for non_expected in case.expected_non_triggers:
        if non_expected in actual_set:
            issues.append(f"FALSE POSITIVE: {non_expected} triggered but should not")

    if not issues:
        return "pass", issues
    has_fn = any("FALSE NEGATIVE" in i for i in issues)
    has_fp = any("FALSE POSITIVE" in i for i in issues)
    if has_fn:
        return "fail", issues
    if has_fp:
        return "partial", issues
    return "fail", issues


def mode_report(cases: list[TriggerCase]) -> int:
    """Print the test matrix as a readable checklist."""
    current_cat = ""
    for case in cases:
        if case.category != current_cat:
            current_cat = case.category
            print(f"\n{'='*60}")
            print(f"  Category: {current_cat}")
            print(f"{'='*60}")
        print(f"\n  [{case.id}]")
        print(f"  Prompt: {case.prompt}")
        print(f"  Should trigger:     {', '.join(case.expected_triggers) or '(none)'}")
        print(f"  Should NOT trigger: {', '.join(case.expected_non_triggers) or '(none)'}")
        print(f"  Notes: {case.notes}")
    print(f"\nTotal: {len(cases)} cases")
    return 0


def mode_prompt(cases: list[TriggerCase], skills_block: str) -> None:
    """Print evaluation prompts for manual LLM assessment."""
    batch_prompts: list[dict] = []
    for case in cases:
        batch_prompts.append({
            "id": case.id,
            "prompt": case.prompt,
        })

    full_prompt = SYSTEM_TEMPLATE.format(skills_block=skills_block)
    full_prompt += "\nEvaluate each of the following user prompts. Return a JSON array where each element has: {\"id\": \"...\", \"triggers\": [...], \"reasoning\": \"...\"}.\n\n"
    for i, bp in enumerate(batch_prompts):
        full_prompt += f"{i+1}. [{bp['id']}] \"{bp['prompt']}\"\n"

    print("=" * 60)
    print("  COPY THE PROMPT BELOW INTO z.ai OR ANY LLM")
    print("=" * 60)
    print()
    print(full_prompt)
    print("=" * 60)
    print()
    print("After getting the LLM response, compare each result against:")
    print()
    for case in cases:
        exp = ", ".join(case.expected_triggers) or "(none)"
        non = ", ".join(case.expected_non_triggers) or "(none)"
        print(f"  [{case.id}] should trigger: {exp}  |  should NOT: {non}")


DEFAULT_ZAI_BASE_URL = "https://api.z.ai/v1"
DEFAULT_ZAI_MODEL = "deepseek-chat"


def mode_api(cases: list[TriggerCase], skills_block: str, *, model: str, base_url: str) -> None:
    """Call z.ai API to evaluate trigger accuracy."""
    api_key = os.environ.get("ZAI_API_KEY")
    if not api_key:
        print("Error: ZAI_API_KEY not set. Use --mode prompt instead.", file=sys.stderr)
        print("\nTo set up z.ai API access:", file=sys.stderr)
        print("  export ZAI_API_KEY='your-api-key'", file=sys.stderr)
        print(f"  export ZAI_BASE_URL='{base_url}'  # optional", file=sys.stderr)
        print(f"  export ZAI_MODEL='{model}'        # optional", file=sys.stderr)
        sys.exit(1)

    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=base_url)
    print(f"  z.ai Base URL: {base_url}")
    print(f"  Model: {model}\n")

    results: list[dict] = []
    pass_count = 0
    partial_count = 0
    fail_count = 0

    for case in cases:
        prompt = build_eval_prompt(case, skills_block)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or "{}"
        except Exception as e:
            print(f"  ✗ [{case.id}] API error: {e}")
            raw = "{}"

        try:
            parsed = json.loads(raw)
            actual = parsed.get("triggers", [])
            reasoning = parsed.get("reasoning", "")
        except json.JSONDecodeError:
            actual = []
            reasoning = f"JSON parse error: {raw[:200]}"

        verdict, issues = score_result(case, actual)
        if verdict == "pass":
            pass_count += 1
        elif verdict == "partial":
            partial_count += 1
        else:
            fail_count += 1

        icon = {"pass": "✓", "partial": "~", "fail": "✗"}[verdict]
        results.append({
            "id": case.id,
            "verdict": verdict,
            "actual": actual,
            "expected": list(case.expected_triggers),
            "non_expected": list(case.expected_non_triggers),
            "issues": issues,
            "reasoning": reasoning,
        })
        print(f"  {icon} [{case.id}] {verdict}")
        for issue in issues:
            print(f"      {issue}")

    print(f"\nResults: {pass_count} pass, {partial_count} partial, {fail_count} fail out of {len(cases)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run trigger tests using z.ai models.")
    parser.add_argument("--mode", choices=["prompt", "api", "report"], default="report")
    parser.add_argument(
        "--model",
        default=os.environ.get("ZAI_MODEL", DEFAULT_ZAI_MODEL),
        help=f"z.ai model name (default: {DEFAULT_ZAI_MODEL} or $ZAI_MODEL)"
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("ZAI_BASE_URL", DEFAULT_ZAI_BASE_URL),
        help=f"z.ai API base URL (default: {DEFAULT_ZAI_BASE_URL} or $ZAI_BASE_URL)"
    )
    parser.add_argument("--category", choices=list(CATEGORIES), default=None)
    parser.add_argument("--case", default=None)
    args = parser.parse_args()

    if args.case:
        cases = [resolve_trigger_case(args.case)]
    elif args.category:
        cases = list(cases_by_category(args.category))
    else:
        cases = list(ALL_TRIGGER_CASES)

    if not cases:
        print("No matching cases found.", file=sys.stderr)
        return 1

    descriptions = extract_descriptions()
    skills_block = build_available_skills_block(descriptions)

    if args.mode == "report":
        return mode_report(cases)
    elif args.mode == "prompt":
        mode_prompt(cases, skills_block)
        return 0
    elif args.mode == "api":
        mode_api(cases, skills_block, model=args.model, base_url=args.base_url)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
