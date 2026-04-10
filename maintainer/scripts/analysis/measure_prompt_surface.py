#!/usr/bin/env python3
"""Measure prompt surface area for token efficiency tracking.

This script measures the size of governance templates, generated governance,
evaluation prompts, and skill documentation to establish a baseline for
token efficiency optimization.

Usage:
    python3 maintainer/scripts/analysis/measure_prompt_surface.py
    python3 maintainer/scripts/analysis/measure_prompt_surface.py --json
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = REPO_ROOT / "templates" / "governance"
SKILLS_DIR = REPO_ROOT / "skills"


def measure_file(file_path: Path) -> dict[str, Any]:
    """Measure a single file's size metrics."""
    if not file_path.exists():
        return {
            "path": str(file_path),
            "exists": False,
            "lines": 0,
            "chars": 0,
            "bytes": 0,
        }

    content = file_path.read_text(encoding="utf-8")
    return {
        "path": str(file_path.relative_to(REPO_ROOT)),
        "exists": True,
        "lines": len(content.splitlines()),
        "chars": len(content),
        "bytes": len(content.encode("utf-8")),
    }


def measure_governance_templates() -> dict[str, Any]:
    """Measure governance template files."""
    agents_template = TEMPLATES_DIR / "AGENTS-template.md"
    claude_template = TEMPLATES_DIR / "CLAUDE-template.md"

    agents_metrics = measure_file(agents_template)
    claude_metrics = measure_file(claude_template)

    return {
        "agents_template": agents_metrics,
        "claude_template": claude_metrics,
        "total_lines": agents_metrics["lines"] + claude_metrics["lines"],
        "total_chars": agents_metrics["chars"] + claude_metrics["chars"],
        "total_bytes": agents_metrics["bytes"] + claude_metrics["bytes"],
    }


def measure_generated_governance() -> dict[str, Any]:
    """Measure generated governance files in a temp project simulation.

    For now, this measures the actual root AGENTS.md and CLAUDE.md files
    as a proxy for generated governance size.
    """
    agents_file = REPO_ROOT / "AGENTS.md"
    claude_file = REPO_ROOT / "CLAUDE.md"

    agents_metrics = measure_file(agents_file)
    claude_metrics = measure_file(claude_file)

    return {
        "agents_generated": agents_metrics,
        "claude_generated": claude_metrics,
        "total_lines": agents_metrics["lines"] + claude_metrics["lines"],
        "total_chars": agents_metrics["chars"] + claude_metrics["chars"],
        "total_bytes": agents_metrics["bytes"] + claude_metrics["bytes"],
        "note": "Measured from root AGENTS.md and CLAUDE.md as proxy for generated governance",
    }


def measure_skill_files() -> dict[str, Any]:
    """Measure all SKILL.md files."""
    skill_metrics = []
    total_lines = 0
    total_chars = 0
    total_bytes = 0

    if not SKILLS_DIR.exists():
        return {
            "skills": [],
            "count": 0,
            "total_lines": 0,
            "total_chars": 0,
            "total_bytes": 0,
            "note": f"Skills directory not found: {SKILLS_DIR}",
        }

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        metrics = measure_file(skill_file)
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
        metrics["body_lines"] = len(body_lines)
        metrics["body_chars"] = len("\n".join(body_lines))
        metrics["over_500_lines"] = metrics["body_lines"] > 500

        skill_metrics.append(metrics)
        total_lines += metrics["lines"]
        total_chars += metrics["chars"]
        total_bytes += metrics["bytes"]

    return {
        "skills": skill_metrics,
        "count": len(skill_metrics),
        "total_lines": total_lines,
        "total_chars": total_chars,
        "total_bytes": total_bytes,
        "avg_lines_per_skill": total_lines / len(skill_metrics) if skill_metrics else 0,
        "max_body_lines": max((s["body_lines"] for s in skill_metrics), default=0),
        "over_500_count": sum(s["over_500_lines"] for s in skill_metrics),
    }


def measure_evaluation_prompts() -> dict[str, Any]:
    """Measure evaluation prompt structure.

    This examines the trigger test builder to estimate prompt size.
    """
    eval_dir = REPO_ROOT / "maintainer" / "scripts" / "evaluation"
    trigger_test_file = eval_dir / "run_trigger_tests.py"

    if not trigger_test_file.exists():
        return {
            "note": "Trigger test file not found",
            "lines": 0,
            "chars": 0,
        }

    metrics = measure_file(trigger_test_file)

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
    args = parser.parse_args()

    results = {
        "timestamp": "2026-04-11",
        "governance_templates": measure_governance_templates(),
        "generated_governance": measure_generated_governance(),
        "skill_files": measure_skill_files(),
        "evaluation_prompts": measure_evaluation_prompts(),
    }

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 80)
        print("Token Efficiency Baseline Measurement")
        print("=" * 80)
        print()

        print("Governance Templates:")
        print(f"  AGENTS-template.md: {results['governance_templates']['agents_template']['lines']} lines, "
              f"{results['governance_templates']['agents_template']['chars']} chars")
        print(f"  CLAUDE-template.md: {results['governance_templates']['claude_template']['lines']} lines, "
              f"{results['governance_templates']['claude_template']['chars']} chars")
        print(f"  Total: {results['governance_templates']['total_lines']} lines, "
              f"{results['governance_templates']['total_chars']} chars")
        print()

        print("Generated Governance:")
        print(f"  AGENTS.md: {results['generated_governance']['agents_generated']['lines']} lines, "
              f"{results['generated_governance']['agents_generated']['chars']} chars")
        print(f"  CLAUDE.md: {results['generated_governance']['claude_generated']['lines']} lines, "
              f"{results['generated_governance']['claude_generated']['chars']} chars")
        print(f"  Total: {results['generated_governance']['total_lines']} lines, "
              f"{results['generated_governance']['total_chars']} chars")
        print(f"  Note: {results['generated_governance']['note']}")
        print()

        print("Skill Files:")
        print(f"  Count: {results['skill_files']['count']}")
        print(f"  Total: {results['skill_files']['total_lines']} lines, "
              f"{results['skill_files']['total_chars']} chars")
        print(f"  Average per skill: {results['skill_files']['avg_lines_per_skill']:.1f} lines")
        print(f"  Max body lines: {results['skill_files']['max_body_lines']}")
        print(f"  Skills over 500 lines: {results['skill_files']['over_500_count']}")
        print()

        print("Skills by size (body lines):")
        for skill in sorted(results['skill_files']['skills'],
                           key=lambda s: s['body_lines'],
                           reverse=True)[:10]:
            marker = " [OVER 500]" if skill['over_500_lines'] else ""
            print(f"  {skill['skill_name']:30s}: {skill['body_lines']:4d} lines{marker}")
        print()

        print("Evaluation Prompts:")
        print(f"  Trigger test script: {results['evaluation_prompts']['trigger_test_script']['lines']} lines")
        print(f"  {results['evaluation_prompts']['note']}")
        print()


if __name__ == "__main__":
    main()
