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
  Uses OpenAI SDK with standard environment variables (can be overridden by CLI args):
  - OPENAI_API_KEY: Your API key (can be overridden by --api-key)
  - OPENAI_BASE_URL: Custom endpoint URL (can be overridden by --base-url)
  - OPENAI_MODEL: Default model name (can be overridden by --model)
  - OPENAI_EXTRA_BODY: Extra parameters as JSON string (can be overridden by --extra-body)

Filter:
  --category <name>   Run only one category
  --case <id>         Run only one case

Usage Examples:
  # View test matrix
  python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report

  # Use OpenAI API (from .env)
  python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api --model gpt-4

  # Override with command line args (no .env changes needed)
  python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api \
    --api-key sk-... \
    --model gpt-5.4

  # Use z.ai with CLI args
  python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api \
    --api-key your-z-ai-key \
    --base-url https://api.z.ai/v1 \
    --model GLM-5.1 \
    --extra-body '{"thinking":{"type":"disabled"}}'

  # Use GLM-5 via aliyun
  python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api \
    --api-key sk-... \
    --base-url https://dashscope.aliyuncs.com/compatible-mode/v1 \
    --model glm-5 \
    --extra-body '{"enable_thinking":false}'
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


def load_skill_index() -> dict[str, str]:
    """Load skill descriptions from compact skill_index.json.

    Falls back to extract_descriptions() if index doesn't exist.
    Returns dict mapping skill name to description.
    """
    skill_index_path = DATA_DIR / "skill_index.json"

    if not skill_index_path.exists():
        print(f"Warning: Skill index not found at {skill_index_path}", file=sys.stderr)
        print("Falling back to SKILL.md frontmatter parsing...", file=sys.stderr)
        return extract_descriptions()

    try:
        with open(skill_index_path, encoding="utf-8") as f:
            index_data = json.load(f)

        descriptions: dict[str, str] = {}
        for skill in index_data.get("skills", []):
            descriptions[skill["name"]] = skill["description"]

        return descriptions
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Failed to parse skill index: {e}", file=sys.stderr)
        print("Falling back to SKILL.md frontmatter parsing...", file=sys.stderr)
        return extract_descriptions()


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


def calculate_prompt_size(prompt: str) -> dict[str, int]:
    """Calculate prompt size metrics (characters, tokens estimate, lines)."""
    chars = len(prompt)
    # Rough token estimate: ~4 chars per token for English text
    # This is approximate - actual tokenization varies by model
    tokens_estimate = chars // 4
    lines = prompt.count('\n') + 1
    return {
        "characters": chars,
        "tokens_estimate": tokens_estimate,
        "lines": lines,
    }


def mode_prompt(cases: list[TriggerCase], skills_block: str, *, compact_mode: bool = False) -> None:
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

    # Calculate and report prompt size
    size_info = calculate_prompt_size(full_prompt)
    mode_label = "compact" if compact_mode else "verbose"

    print("=" * 60)
    print("  COPY THE PROMPT BELOW INTO ANY LLM")
    print("=" * 60)
    print(f"  Mode: {mode_label}")
    print(f"  Size: {size_info['characters']:,} chars, ~{size_info['tokens_estimate']:,} tokens, {size_info['lines']:,} lines")
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


def _eval_single_case(
    client,
    model: str,
    case: TriggerCase,
    skills_block: str,
    *,
    extra_body: dict | None = None,
) -> dict:
    """Evaluate a single trigger case against the LLM. Thread-safe."""
    prompt = build_eval_prompt(case, skills_block)
    try:
        create_kwargs: dict = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        if extra_body:
            create_kwargs["extra_body"] = extra_body
        response = client.chat.completions.create(**create_kwargs)
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
    api_key: str | None = None,
    extra_body: dict | None = None,
    concurrency: int = 1,
    compact_mode: bool = False,
) -> None:
    """Call LLM API to evaluate trigger accuracy.

    Uses OpenAI SDK with standard environment variables (can be overridden by CLI args):
    - OPENAI_API_KEY: API key (required, or use --api-key)
    - OPENAI_BASE_URL: Custom endpoint (optional, or use --base-url)
    - OPENAI_EXTRA_BODY: Optional JSON for provider-specific fields (or use --extra-body)
    """
    # Use command line argument if provided, otherwise fall back to env var
    if api_key is None:
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

    # Parse extra_body from command line argument or OPENAI_EXTRA_BODY env var
    if extra_body is None:
        extra_body_str = os.environ.get("OPENAI_EXTRA_BODY")
        if extra_body_str:
            try:
                extra_body = json.loads(extra_body_str)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse OPENAI_EXTRA_BODY: {e}", file=sys.stderr)
                extra_body = None

    # Create client - OpenAI SDK handles env vars natively
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    client = OpenAI(**client_kwargs)

    # Calculate and report prompt size for a typical evaluation
    sample_prompt = build_eval_prompt(cases[0] if cases else TriggerCase(
        id="sample", category="sample", prompt="sample",
        expected_triggers=[], expected_non_triggers=[], notes=""
    ), skills_block)
    size_info = calculate_prompt_size(sample_prompt)
    mode_label = "compact" if compact_mode else "verbose"

    # Display configuration
    print(f"  Mode: {mode_label}")
    print(f"  Prompt size (per case): ~{size_info['tokens_estimate']:,} tokens")
    if base_url:
        print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    if extra_body:
        print(f"  extra_body: {json.dumps(extra_body)}")
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
            result = _eval_single_case(
                client, model, case, skills_block, extra_body=extra_body
            )
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
                executor.submit(
                    _eval_single_case,
                    client,
                    model,
                    case,
                    skills_block,
                    extra_body=extra_body,
                ): case
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
        "--compact-mode",
        action="store_true",
        help="Use compact skill_index.json instead of parsing full SKILL.md frontmatter (reduces prompt size by 60-80%%)",
    )
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
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (overrides $OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--extra-body",
        default=None,
        help="Extra body JSON string (overrides $OPENAI_EXTRA_BODY), e.g. '{\"enable_thinking\":false}'",
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

    # Parse --extra-body JSON string if provided
    extra_body_dict = None
    if args.extra_body:
        try:
            extra_body_dict = json.loads(args.extra_body)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON for --extra-body: {e}", file=sys.stderr)
            return 1

    if args.case:
        cases = [resolve_trigger_case(args.case)]
    elif args.category:
        cases = list(cases_by_category(args.category))
    else:
        cases = list(ALL_TRIGGER_CASES)

    if not cases:
        print("No matching cases found.", file=sys.stderr)
        return 1

    # Load skill descriptions based on mode
    if args.compact_mode:
        descriptions = load_skill_index()
    else:
        descriptions = extract_descriptions()

    skills_block = build_available_skills_block(descriptions)
    protocol_missing = 0

    if args.mode == "report":
        protocol_missing = mode_report(
            cases,
            include_protocol_readiness=not args.skip_protocol_readiness,
        )
    elif args.mode == "prompt":
        mode_prompt(cases, skills_block, compact_mode=args.compact_mode)
    elif args.mode == "api":
        mode_api(
            cases,
            skills_block,
            model=args.model,
            base_url=args.base_url,
            api_key=args.api_key,
            extra_body=extra_body_dict,
            concurrency=args.concurrency,
            compact_mode=args.compact_mode,
        )

    if args.fail_on_protocol_issues and protocol_missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
