#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml", "openai>=1.0", "python-dotenv>=1.0"]
# ///
"""Run trigger tests against skill descriptions.

Modes:
  --mode prompt   Print evaluation prompts for manual LLM assessment
  --mode api      Call LLM API to evaluate automatically (needs API key)
  --mode report   Print the test matrix as a readable checklist (default)

API Configuration:
  Uses OpenAI SDK with standard environment variables:
  - OPENAI_API_KEY: Your API key (OpenAI, z.ai, or any OpenAI-compatible service)
  - OPENAI_BASE_URL: Custom endpoint URL (optional, for non-OpenAI services)
  - OPENAI_MODEL: Default model name (optional, can be overridden by --model)

Filter:
  --category <name>   Run only one category
  --case <id>         Run only one case

Usage Examples:
  # View test matrix
  python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report

  # Use OpenAI API
  export OPENAI_API_KEY="sk-..."
  python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api --model gpt-4

  # Use z.ai (OpenAI-compatible)
  export OPENAI_API_KEY="your-z-ai-key"
  export OPENAI_BASE_URL="https://api.z.ai/v1"
  export OPENAI_MODEL="deepseek-chat"
  python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api

  # Custom base URL
  python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api --base-url https://custom.api.com/v1
"""

from __future__ import annotations

import argparse
import concurrent.futures
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
from skill_protocol_v1 import collect_skill_document_checks


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


def print_protocol_readiness_report() -> int:
    """Print static Skill Protocol v1 readiness for all skills."""
    checks = collect_skill_document_checks(SKILLS_DIR)
    missing_count = 0
    print(f"\n{'='*60}")
    print("  Skill Protocol v1 Readiness")
    print(f"{'='*60}")
    for check in checks:
        if check.missing_sections:
            missing_count += 1
        status = "ok" if not check.missing_sections else "missing"
        missing = ", ".join(check.missing_sections) or "-"
        legacy = "yes" if check.has_legacy_contract else "no"
        print(
            f"  [{status:7}] {check.skill:24} "
            f"family={check.family:13} missing={missing} legacy_contract={legacy}"
        )
    print(f"\nSkills with missing required protocol sections: {missing_count} / {len(checks)}")
    return missing_count


def mode_report(cases: list[TriggerCase], *, include_protocol_readiness: bool) -> int:
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
    if include_protocol_readiness:
        return print_protocol_readiness_report()
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
    print("  COPY THE PROMPT BELOW INTO ANY LLM")
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


DEFAULT_MODEL = "gpt-5.4"


def _eval_single_case(client, model: str, case: TriggerCase, skills_block: str) -> dict:
    """Evaluate a single trigger case against the LLM. Thread-safe."""
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
        raw = "{}"
        return {
            "id": case.id,
            "verdict": "fail",
            "actual": [],
            "expected": list(case.expected_triggers),
            "non_expected": list(case.expected_non_triggers),
            "issues": [f"API error: {e}"],
            "reasoning": "",
        }

    try:
        parsed = json.loads(raw)
        actual = parsed.get("triggers", [])
        reasoning = parsed.get("reasoning", "")
    except json.JSONDecodeError:
        actual = []
        reasoning = f"JSON parse error: {raw[:200]}"

    verdict, issues = score_result(case, actual)
    return {
        "id": case.id,
        "verdict": verdict,
        "actual": actual,
        "expected": list(case.expected_triggers),
        "non_expected": list(case.expected_non_triggers),
        "issues": issues,
        "reasoning": reasoning,
    }


def mode_api(
    cases: list[TriggerCase],
    skills_block: str,
    *,
    model: str = DEFAULT_MODEL,
    base_url: str | None = None,
    concurrency: int = 1,
) -> None:
    """Call LLM API to evaluate trigger accuracy.

    Uses OpenAI SDK with standard environment variables:
    - OPENAI_API_KEY: API key (required)
    - OPENAI_BASE_URL: Custom endpoint (optional, for z.ai or other OpenAI-compatible services)
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set. Use --mode prompt instead.", file=sys.stderr)
        print("\nSet your API key:", file=sys.stderr)
        print("  # For OpenAI:", file=sys.stderr)
        print("  export OPENAI_API_KEY='sk-...'", file=sys.stderr)
        print("\n  # For z.ai (OpenAI-compatible):", file=sys.stderr)
        print("  export OPENAI_API_KEY='your-z-ai-key'", file=sys.stderr)
        print("  export OPENAI_BASE_URL='https://api.z.ai/v1'", file=sys.stderr)
        sys.exit(1)

    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai package not installed. Run: uv pip install openai", file=sys.stderr)
        sys.exit(1)

    # Use base_url from command line, or fall back to OPENAI_BASE_URL env var
    if base_url is None:
        base_url = os.environ.get("OPENAI_BASE_URL")

    # Create client - OpenAI SDK handles env vars natively
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    client = OpenAI(**client_kwargs)

    # Display configuration
    if base_url:
        print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    if concurrency > 1:
        print(f"  Concurrency: {concurrency}")
    print()

    results: list[dict] = []
    pass_count = 0
    partial_count = 0
    fail_count = 0

    if concurrency <= 1:
        # Serial execution
        for case in cases:
            result = _eval_single_case(client, model, case, skills_block)
            results.append(result)
            verdict = result["verdict"]
            if verdict == "pass":
                pass_count += 1
            elif verdict == "partial":
                partial_count += 1
            else:
                fail_count += 1
            icon = {"pass": "✓", "partial": "~", "fail": "✗"}[verdict]
            print(f"  {icon} [{result['id']}] {verdict}")
            for issue in result["issues"]:
                print(f"      {issue}")
    else:
        # Parallel execution
        completed = 0
        total = len(cases)
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_case = {
                executor.submit(_eval_single_case, client, model, case, skills_block): case
                for case in cases
            }
            for future in concurrent.futures.as_completed(future_to_case):
                result = future.result()
                results.append(result)
                verdict = result["verdict"]
                if verdict == "pass":
                    pass_count += 1
                elif verdict == "partial":
                    partial_count += 1
                else:
                    fail_count += 1
                completed += 1
                icon = {"pass": "✓", "partial": "~", "fail": "✗"}[verdict]
                print(f"  {icon} [{result['id']}] {verdict}  ({completed}/{total})")
                for issue in result["issues"]:
                    print(f"      {issue}")

    print(f"\nResults: {pass_count} pass, {partial_count} partial, {fail_count} fail out of {len(cases)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run trigger tests against skill descriptions.")
    parser.add_argument("--mode", choices=["prompt", "api", "report"], default="report")
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL),
        help=f"LLM model for --mode api (default: $OPENAI_MODEL or {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Custom API base URL (overrides $OPENAI_BASE_URL)",
    )
    parser.add_argument("--category", choices=list(CATEGORIES), default=None)
    parser.add_argument("--case", default=None)
    parser.add_argument(
        "--concurrency", "-j",
        type=int,
        default=1,
        help="Number of parallel API calls for --mode api (default: 1, serial)",
    )
    parser.add_argument(
        "--skip-protocol-readiness",
        action="store_true",
        help="Skip the static Skill Protocol v1 readiness report in --mode report.",
    )
    parser.add_argument(
        "--fail-on-protocol-issues",
        action="store_true",
        help="Return a non-zero exit code when a skill document is missing required v1 sections.",
    )
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
    protocol_missing = 0

    if args.mode == "report":
        protocol_missing = mode_report(
            cases,
            include_protocol_readiness=not args.skip_protocol_readiness,
        )
    elif args.mode == "prompt":
        mode_prompt(cases, skills_block)
    elif args.mode == "api":
        mode_api(
            cases,
            skills_block,
            model=args.model,
            base_url=args.base_url,
            concurrency=args.concurrency,
        )

    if args.fail_on_protocol_issues and protocol_missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
