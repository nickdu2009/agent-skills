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

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
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
from skill_protocol import collect_skill_document_checks


def extract_descriptions() -> dict[str, str]:
    """Extract the description field from each SKILL.md frontmatter."""
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError(
            "prompt/api modes require PyYAML to parse Agent Skills frontmatter"
        ) from exc

    descriptions: dict[str, str] = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        lines = skill_file.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0].strip() != "---":
            continue
        try:
            end = next(
                index
                for index, line in enumerate(lines[1:], start=1)
                if line.strip() == "---"
            )
        except StopIteration:
            continue
        frontmatter = yaml.safe_load("\n".join(lines[1:end])) or {}
        description = frontmatter.get("description") if isinstance(frontmatter, dict) else None
        if isinstance(description, str) and description:
            descriptions[skill_dir.name] = description
    return descriptions


def load_skill_index(*, strict: bool = False) -> dict[str, str]:
    """Load skill descriptions from compact skill_index.json.

    Runtime callers fall back to frontmatter when the index is unavailable.
    Validation callers use strict=True so a stale/missing index fails closed.
    Returns dict mapping skill name to description.
    """
    skill_index_path = DATA_DIR / "skill_index.json"

    if not skill_index_path.exists():
        if strict:
            raise RuntimeError(f"Skill index not found at {skill_index_path}")
        print(f"Warning: Skill index not found at {skill_index_path}", file=sys.stderr)
        print("Falling back to SKILL.md frontmatter parsing...", file=sys.stderr)
        return extract_descriptions()

    try:
        with open(skill_index_path, encoding="utf-8") as f:
            index_data = json.load(f)

        skills = index_data.get("skills")
        if not isinstance(skills, list):
            raise ValueError("skills must be an array")
        descriptions: dict[str, str] = {}
        for index, skill in enumerate(skills):
            if not isinstance(skill, dict):
                raise ValueError(f"skills[{index}] must be an object")
            name = skill.get("name")
            description = skill.get("description")
            if not isinstance(name, str) or not isinstance(description, str):
                raise ValueError(f"skills[{index}] requires string name and description")
            if name in descriptions:
                raise ValueError(f"duplicate Skill name in index: {name}")
            descriptions[name] = description

        return descriptions
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        if strict:
            raise RuntimeError(f"Failed to parse Skill index: {e}") from e
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
    """Legacy function for backward compatibility (--mode prompt)."""
    return (
        SYSTEM_TEMPLATE.format(skills_block=skills_block)
        + f"\nUser prompt: \"{case.prompt}\"\n"
    )


def build_eval_messages(
    case: TriggerCase,
    skills_block: str,
    *,
    enable_cache: bool = False,
) -> list[dict]:
    """Build structured messages for Chat Completions API.

    Args:
        case: Test case containing the user prompt
        skills_block: Formatted skill descriptions
        enable_cache: If True, add cache_control to system message (for explicit caching)

    Returns:
        List of message dicts with proper role separation
    """
    system_content = SYSTEM_TEMPLATE.format(skills_block=skills_block)

    if enable_cache:
        # Explicit caching format (OpenAI-compatible)
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_content,
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
            },
            {
                "role": "user",
                "content": f'User prompt: "{case.prompt}"'
            }
        ]
    else:
        # Standard format (implicit caching)
        messages = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": f'User prompt: "{case.prompt}"'
            }
        ]

    return messages


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
    """Print Skill document protocol readiness for all skills."""
    checks = collect_skill_document_checks(SKILLS_DIR)
    missing_count = 0
    print(f"\n{'='*60}")
    print("  Skill Document Protocol Readiness")
    print(f"{'='*60}")
    for check in checks:
        if check.missing_sections:
            missing_count += 1
        status = "ok" if not check.missing_sections else "missing"
        missing = ", ".join(check.missing_sections) or "-"
        print(
            f"  [{status:7}] {check.skill:24} "
            f"family={check.family:13} missing={missing}"
        )
    print(f"\nSkills with missing required protocol sections: {missing_count} / {len(checks)}")
    return missing_count


def validate_trigger_matrix(cases: tuple[TriggerCase, ...]) -> list[str]:
    """Validate the single trigger matrix before filtering or reporting it."""
    issues: list[str] = []
    known_skills = {path.parent.name for path in SKILLS_DIR.glob("*/SKILL.md")}
    ids: dict[str, int] = {}
    referenced_skills: set[str] = set()
    positive_coverage: set[str] = set()

    for case in cases:
        ids[case.id] = ids.get(case.id, 0) + 1
        triggers = set(case.expected_triggers)
        non_triggers = set(case.expected_non_triggers)
        overlap = sorted(triggers & non_triggers)
        if overlap:
            issues.append(
                f"case {case.id!r} both triggers and excludes: {', '.join(overlap)}"
            )
        referenced_skills.update(triggers | non_triggers)
        positive_coverage.update(triggers)

    duplicates = sorted(case_id for case_id, count in ids.items() if count > 1)
    if duplicates:
        issues.append("duplicate case IDs: " + ", ".join(duplicates))

    unknown = sorted(referenced_skills - known_skills)
    if unknown:
        issues.append("cases reference unknown Skills: " + ", ".join(unknown))

    uncovered = sorted(known_skills - positive_coverage)
    if uncovered:
        issues.append("Skills without a positive trigger case: " + ", ".join(uncovered))

    return issues


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
    enable_cache: bool = False,
) -> dict:
    """Evaluate a single trigger case against the LLM. Thread-safe.

    Args:
        client: OpenAI client instance
        model: Model name
        case: Test case to evaluate
        skills_block: Formatted skill descriptions
        extra_body: Extra API parameters (e.g., thinking control)
        enable_cache: Whether to use explicit caching (requires compatible model)

    Returns:
        Dict with verdict, actual triggers, and metadata
    """
    messages = build_eval_messages(case, skills_block, enable_cache=enable_cache)
    try:
        create_kwargs: dict = {
            "model": model,
            "messages": messages,
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
    enable_cache: bool = False,
) -> None:
    """Call LLM API to evaluate trigger accuracy.

    Uses OpenAI SDK with standard environment variables (can be overridden by CLI args):
    - OPENAI_API_KEY: API key (required, or use --api-key)
    - OPENAI_BASE_URL: Custom endpoint (optional, or use --base-url)
    - OPENAI_EXTRA_BODY: Optional JSON for provider-specific fields (or use --extra-body)

    Args:
        enable_cache: Enable explicit caching (requires compatible model like qwen3-coder-plus)
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
    if enable_cache:
        print(f"  Caching: explicit (cache_control enabled)")
    else:
        print(f"  Caching: implicit (auto)")
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
                client, model, case, skills_block,
                extra_body=extra_body,
                enable_cache=enable_cache
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
                    enable_cache=enable_cache,
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
        help="Load the same Skill descriptions from skill_index.json instead of parsing SKILL.md frontmatter.",
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
        help="Skip the Skill document protocol readiness report in --mode report.",
    )
    parser.add_argument(
        "--fail-on-protocol-issues",
        action="store_true",
        help="Return a non-zero exit code when a Skill document is missing required protocol sections.",
    )
    parser.add_argument(
        "--enable-cache",
        action="store_true",
        help="Enable explicit caching (adds cache_control to system message). Requires compatible models like qwen3-coder-plus. GLM models only support implicit caching.",
    )
    args = parser.parse_args()

    matrix_issues = validate_trigger_matrix(ALL_TRIGGER_CASES)
    if matrix_issues:
        for issue in matrix_issues:
            print(f"Error: {issue}", file=sys.stderr)
        return 2

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

    protocol_missing = 0

    if args.mode == "report":
        protocol_missing = mode_report(
            cases,
            include_protocol_readiness=not args.skip_protocol_readiness,
        )
    elif args.mode == "prompt":
        descriptions = load_skill_index() if args.compact_mode else extract_descriptions()
        skills_block = build_available_skills_block(descriptions)
        mode_prompt(cases, skills_block, compact_mode=args.compact_mode)
    elif args.mode == "api":
        descriptions = load_skill_index() if args.compact_mode else extract_descriptions()
        skills_block = build_available_skills_block(descriptions)
        mode_api(
            cases,
            skills_block,
            model=args.model,
            base_url=args.base_url,
            api_key=args.api_key,
            extra_body=extra_body_dict,
            concurrency=args.concurrency,
            compact_mode=args.compact_mode,
            enable_cache=args.enable_cache,
        )

    if args.fail_on_protocol_issues and protocol_missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
