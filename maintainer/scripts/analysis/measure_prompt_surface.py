#!/usr/bin/env python3
"""Measure prompt surface area for token efficiency tracking.

This script measures the size of governance templates, generated governance,
evaluation prompts, and skill documentation to establish a baseline for
token efficiency optimization.

Usage:
    python3 maintainer/scripts/analysis/measure_prompt_surface.py
    python3 maintainer/scripts/analysis/measure_prompt_surface.py --json
    python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens

Token Counting:
    By default, uses character-based proxy (~4 chars per token) for fast estimates.
    With --actual-tokens, uses tiktoken cl100k_base encoding for precise counts.
    Install tiktoken with: pip install tiktoken
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

# Optional tiktoken import - graceful fallback if not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = REPO_ROOT / "templates" / "governance"
SKILLS_DIR = REPO_ROOT / "skills"


def count_tokens_tiktoken(text: str) -> int:
    """Count tokens using tiktoken cl100k_base encoding.

    Falls back to character-based estimate if tiktoken not available.
    """
    if not TIKTOKEN_AVAILABLE:
        # Fallback: ~4 characters per token (rough estimate)
        return len(text) // 4

    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Fallback on any error
        return len(text) // 4


def measure_file(file_path: Path, *, use_actual_tokens: bool = False) -> dict[str, Any]:
    """Measure a single file's size metrics."""
    if not file_path.exists():
        result = {
            "path": str(file_path),
            "exists": False,
            "lines": 0,
            "chars": 0,
            "bytes": 0,
        }
        if use_actual_tokens:
            result["tokens"] = 0
            result["tokens_estimate"] = 0
        return result

    content = file_path.read_text(encoding="utf-8")
    result = {
        "path": str(file_path.relative_to(REPO_ROOT)),
        "exists": True,
        "lines": len(content.splitlines()),
        "chars": len(content),
        "bytes": len(content.encode("utf-8")),
    }

    if use_actual_tokens:
        result["tokens"] = count_tokens_tiktoken(content)
        result["tokens_estimate"] = len(content) // 4

    return result


def measure_governance_templates(*, use_actual_tokens: bool = False) -> dict[str, Any]:
    """Measure governance template files."""
    agents_template = TEMPLATES_DIR / "AGENTS-template.md"
    claude_template = TEMPLATES_DIR / "CLAUDE-template.md"

    agents_metrics = measure_file(agents_template, use_actual_tokens=use_actual_tokens)
    claude_metrics = measure_file(claude_template, use_actual_tokens=use_actual_tokens)

    result = {
        "agents_template": agents_metrics,
        "claude_template": claude_metrics,
        "total_lines": agents_metrics["lines"] + claude_metrics["lines"],
        "total_chars": agents_metrics["chars"] + claude_metrics["chars"],
        "total_bytes": agents_metrics["bytes"] + claude_metrics["bytes"],
    }

    if use_actual_tokens:
        result["total_tokens"] = agents_metrics["tokens"] + claude_metrics["tokens"]
        result["total_tokens_estimate"] = agents_metrics["tokens_estimate"] + claude_metrics["tokens_estimate"]

    return result


def measure_generated_governance(*, use_actual_tokens: bool = False) -> dict[str, Any]:
    """Measure generated governance files in a temp project simulation.

    For now, this measures the actual root AGENTS.md and CLAUDE.md files
    as a proxy for generated governance size.
    """
    agents_file = REPO_ROOT / "AGENTS.md"
    claude_file = REPO_ROOT / "CLAUDE.md"

    agents_metrics = measure_file(agents_file, use_actual_tokens=use_actual_tokens)
    claude_metrics = measure_file(claude_file, use_actual_tokens=use_actual_tokens)

    result = {
        "agents_generated": agents_metrics,
        "claude_generated": claude_metrics,
        "total_lines": agents_metrics["lines"] + claude_metrics["lines"],
        "total_chars": agents_metrics["chars"] + claude_metrics["chars"],
        "total_bytes": agents_metrics["bytes"] + claude_metrics["bytes"],
        "note": "Measured from root AGENTS.md and CLAUDE.md as proxy for generated governance",
    }

    if use_actual_tokens:
        result["total_tokens"] = agents_metrics["tokens"] + claude_metrics["tokens"]
        result["total_tokens_estimate"] = agents_metrics["tokens_estimate"] + claude_metrics["tokens_estimate"]

    return result


def measure_skill_files(*, use_actual_tokens: bool = False) -> dict[str, Any]:
    """Measure all SKILL.md files."""
    skill_metrics = []
    total_lines = 0
    total_chars = 0
    total_bytes = 0
    total_tokens = 0
    total_tokens_estimate = 0

    if not SKILLS_DIR.exists():
        result = {
            "skills": [],
            "count": 0,
            "total_lines": 0,
            "total_chars": 0,
            "total_bytes": 0,
            "note": f"Skills directory not found: {SKILLS_DIR}",
        }
        if use_actual_tokens:
            result["total_tokens"] = 0
            result["total_tokens_estimate"] = 0
        return result

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        metrics = measure_file(skill_file, use_actual_tokens=use_actual_tokens)
        metrics["skill_name"] = skill_dir.name

        # Measure body length (exclude frontmatter)
        content = skill_file.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Find frontmatter boundaries
        frontmatter_end = 0
        in_frontmatter = False
        for i, line in enumerate(lines):
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    frontmatter_end = i + 1
                    break

        body_lines = lines[frontmatter_end:]
        body_text = "\n".join(body_lines)
        metrics["body_lines"] = len(body_lines)
        metrics["body_chars"] = len(body_text)
        metrics["over_500_lines"] = metrics["body_lines"] > 500

        if use_actual_tokens:
            metrics["body_tokens"] = count_tokens_tiktoken(body_text)
            metrics["body_tokens_estimate"] = len(body_text) // 4

        skill_metrics.append(metrics)
        total_lines += metrics["lines"]
        total_chars += metrics["chars"]
        total_bytes += metrics["bytes"]
        if use_actual_tokens:
            total_tokens += metrics["tokens"]
            total_tokens_estimate += metrics["tokens_estimate"]

    result = {
        "skills": skill_metrics,
        "count": len(skill_metrics),
        "total_lines": total_lines,
        "total_chars": total_chars,
        "total_bytes": total_bytes,
        "avg_lines_per_skill": total_lines / len(skill_metrics) if skill_metrics else 0,
        "max_body_lines": max((s["body_lines"] for s in skill_metrics), default=0),
        "over_500_count": sum(s["over_500_lines"] for s in skill_metrics),
    }

    if use_actual_tokens:
        result["total_tokens"] = total_tokens
        result["total_tokens_estimate"] = total_tokens_estimate
        result["avg_tokens_per_skill"] = total_tokens / len(skill_metrics) if skill_metrics else 0

    return result


def measure_evaluation_prompts(*, use_actual_tokens: bool = False) -> dict[str, Any]:
    """Measure evaluation prompt structure.

    This examines the trigger test builder to estimate prompt size.
    """
    eval_dir = REPO_ROOT / "maintainer" / "scripts" / "evaluation"
    trigger_test_file = eval_dir / "run_trigger_tests.py"

    if not trigger_test_file.exists():
        result = {
            "note": "Trigger test file not found",
            "lines": 0,
            "chars": 0,
        }
        if use_actual_tokens:
            result["tokens"] = 0
        return result

    metrics = measure_file(trigger_test_file, use_actual_tokens=use_actual_tokens)

    # Look for prompt construction logic
    content = trigger_test_file.read_text(encoding="utf-8")
    has_prompt_construction = "def build_prompt" in content or "prompt" in content.lower()

    return {
        "trigger_test_script": metrics,
        "has_prompt_construction": has_prompt_construction,
        "note": "Full prompt size depends on runtime test data",
    }


def main() -> None:
    """Run all measurements and output results."""
    parser = argparse.ArgumentParser(
        description="Measure prompt surface area for token efficiency"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of human-readable format",
    )
    parser.add_argument(
        "--actual-tokens",
        action="store_true",
        help="Use tiktoken cl100k_base encoding for precise token counts (slower but accurate)",
    )
    args = parser.parse_args()

    # Check tiktoken availability if --actual-tokens requested
    if args.actual_tokens and not TIKTOKEN_AVAILABLE:
        print("Warning: --actual-tokens requires tiktoken package", file=sys.stderr)
        print("Install with: pip install tiktoken", file=sys.stderr)
        print("Falling back to character-based estimates...", file=sys.stderr)
        print()

    results = {
        "timestamp": "2026-04-11",
        "token_counting_method": "tiktoken_cl100k_base" if (args.actual_tokens and TIKTOKEN_AVAILABLE) else "character_estimate",
        "governance_templates": measure_governance_templates(use_actual_tokens=args.actual_tokens),
        "generated_governance": measure_generated_governance(use_actual_tokens=args.actual_tokens),
        "skill_files": measure_skill_files(use_actual_tokens=args.actual_tokens),
        "evaluation_prompts": measure_evaluation_prompts(use_actual_tokens=args.actual_tokens),
    }

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 80)
        print("Token Efficiency Baseline Measurement")
        print("=" * 80)
        print(f"Token counting: {results['token_counting_method']}")
        print()

        print("Governance Templates:")
        agents_t = results['governance_templates']['agents_template']
        claude_t = results['governance_templates']['claude_template']
        gov_tmpl = results['governance_templates']

        if args.actual_tokens and TIKTOKEN_AVAILABLE:
            print(f"  AGENTS-template.md: {agents_t['lines']} lines, "
                  f"{agents_t['chars']} chars, {agents_t['tokens']} tokens")
            print(f"  CLAUDE-template.md: {claude_t['lines']} lines, "
                  f"{claude_t['chars']} chars, {claude_t['tokens']} tokens")
            print(f"  Total: {gov_tmpl['total_lines']} lines, "
                  f"{gov_tmpl['total_chars']} chars, {gov_tmpl['total_tokens']} tokens")
        else:
            print(f"  AGENTS-template.md: {agents_t['lines']} lines, {agents_t['chars']} chars")
            print(f"  CLAUDE-template.md: {claude_t['lines']} lines, {claude_t['chars']} chars")
            print(f"  Total: {gov_tmpl['total_lines']} lines, {gov_tmpl['total_chars']} chars")
        print()

        print("Generated Governance:")
        agents_g = results['generated_governance']['agents_generated']
        claude_g = results['generated_governance']['claude_generated']
        gen_gov = results['generated_governance']

        if args.actual_tokens and TIKTOKEN_AVAILABLE:
            print(f"  AGENTS.md: {agents_g['lines']} lines, {agents_g['chars']} chars, {agents_g['tokens']} tokens")
            print(f"  CLAUDE.md: {claude_g['lines']} lines, {claude_g['chars']} chars, {claude_g['tokens']} tokens")
            print(f"  Total: {gen_gov['total_lines']} lines, {gen_gov['total_chars']} chars, {gen_gov['total_tokens']} tokens")
        else:
            print(f"  AGENTS.md: {agents_g['lines']} lines, {agents_g['chars']} chars")
            print(f"  CLAUDE.md: {claude_g['lines']} lines, {claude_g['chars']} chars")
            print(f"  Total: {gen_gov['total_lines']} lines, {gen_gov['total_chars']} chars")
        print(f"  Note: {gen_gov['note']}")
        print()

        print("Skill Files:")
        skill_f = results['skill_files']
        print(f"  Count: {skill_f['count']}")
        if args.actual_tokens and TIKTOKEN_AVAILABLE:
            print(f"  Total: {skill_f['total_lines']} lines, {skill_f['total_chars']} chars, {skill_f['total_tokens']} tokens")
            print(f"  Average per skill: {skill_f['avg_lines_per_skill']:.1f} lines, {skill_f['avg_tokens_per_skill']:.1f} tokens")
        else:
            print(f"  Total: {skill_f['total_lines']} lines, {skill_f['total_chars']} chars")
            print(f"  Average per skill: {skill_f['avg_lines_per_skill']:.1f} lines")
        print(f"  Max body lines: {skill_f['max_body_lines']}")
        print(f"  Skills over 500 lines: {skill_f['over_500_count']}")
        print()

        print("Skills by size (body lines):")
        for skill in sorted(results['skill_files']['skills'],
                           key=lambda s: s['body_lines'],
                           reverse=True)[:10]:
            marker = " [OVER 500]" if skill['over_500_lines'] else ""
            if args.actual_tokens and TIKTOKEN_AVAILABLE and 'body_tokens' in skill:
                print(f"  {skill['skill_name']:30s}: {skill['body_lines']:4d} lines, {skill['body_tokens']:4d} tokens{marker}")
            else:
                print(f"  {skill['skill_name']:30s}: {skill['body_lines']:4d} lines{marker}")
        print()

        print("Evaluation Prompts:")
        print(f"  Trigger test script: {results['evaluation_prompts']['trigger_test_script']['lines']} lines")
        print(f"  {results['evaluation_prompts']['note']}")
        print()


if __name__ == "__main__":
    main()
