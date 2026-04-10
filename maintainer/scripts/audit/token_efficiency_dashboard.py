#!/usr/bin/env python3
"""Real-time token efficiency monitoring dashboard.

This script provides a real-time status dashboard for all optimization metrics,
with color-coded health indicators and comparison to targets and baselines.

Features:
- Color-coded health indicators (green/yellow/red)
- Compare to targets and baselines
- Terminal dashboard (ASCII art) or markdown report
- Quick status overview

Usage:
    python3 maintainer/scripts/audit/token_efficiency_dashboard.py
    python3 maintainer/scripts/audit/token_efficiency_dashboard.py --markdown
    python3 maintainer/scripts/audit/token_efficiency_dashboard.py --no-color
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "maintainer" / "scripts"
ANALYSIS_DIR = SCRIPTS_DIR / "analysis"


# Baseline targets
TARGETS = {
    "quality_pass_rate": 100,  # 18/18 skills (100%)
    "total_skill_tokens": 41783,
    "avg_tokens_per_skill": 2321,
    "cross_references_broken": 0,
    "skills_over_500_lines": 0,
}


# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def run_command(cmd: list[str]) -> dict[str, Any]:
    """Run a command and return parsed JSON output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}", file=sys.stderr)
        print(f"Error: {e.stderr}", file=sys.stderr)
        return {}
    except json.JSONDecodeError:
        return {}


def get_quality_status(use_color: bool = True) -> dict[str, Any]:
    """Get quality metrics status."""
    data = run_command([
        sys.executable,
        str(ANALYSIS_DIR / "check_skill_quality.py"),
        "--json",
    ])

    if not data:
        return {"error": "Failed to collect quality metrics"}

    total = len(data)
    passing = sum(1 for s in data if s.get("overall_pass", False))
    pass_rate = (passing / total * 100) if total > 0 else 0

    # Determine health
    if pass_rate >= TARGETS["quality_pass_rate"]:
        health = "green"
        status = "PASS"
    elif pass_rate >= 90:
        health = "yellow"
        status = "WARN"
    else:
        health = "red"
        status = "FAIL"

    return {
        "total": total,
        "passing": passing,
        "failing": total - passing,
        "pass_rate": pass_rate,
        "target": TARGETS["quality_pass_rate"],
        "health": health,
        "status": status,
    }


def get_token_status(use_color: bool = True) -> dict[str, Any]:
    """Get token metrics status."""
    data = run_command([
        sys.executable,
        str(ANALYSIS_DIR / "measure_prompt_surface.py"),
        "--actual-tokens",
        "--json",
    ])

    if not data:
        return {"error": "Failed to collect token metrics"}

    skills = data["skill_files"]
    total_tokens = skills["total_tokens"]
    avg_tokens = skills["avg_tokens_per_skill"]
    over_500 = skills["over_500_count"]

    # Calculate delta from baseline
    delta_total = total_tokens - TARGETS["total_skill_tokens"]
    delta_pct = (delta_total / TARGETS["total_skill_tokens"] * 100) if TARGETS["total_skill_tokens"] > 0 else 0

    # Determine health
    if delta_pct <= 0:
        health = "green"
        status = "PASS"
    elif delta_pct <= 5:
        health = "yellow"
        status = "WARN"
    else:
        health = "red"
        status = "FAIL"

    return {
        "total_tokens": total_tokens,
        "avg_tokens": avg_tokens,
        "over_500": over_500,
        "baseline_total": TARGETS["total_skill_tokens"],
        "baseline_avg": TARGETS["avg_tokens_per_skill"],
        "delta_total": delta_total,
        "delta_pct": delta_pct,
        "health": health,
        "status": status,
    }


def get_cross_ref_status(use_color: bool = True) -> dict[str, Any]:
    """Get cross-reference integrity status."""
    try:
        result = subprocess.run(
            [sys.executable, str(ANALYSIS_DIR / "check_cross_references.py"), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            broken = len(data.get("broken_references", []))
        else:
            # Try to parse error output
            import re
            match = re.search(r'(\d+)\s+broken', result.stdout)
            broken = int(match.group(1)) if match else 0

    except Exception:
        broken = 0

    # Determine health
    if broken == 0:
        health = "green"
        status = "PASS"
    elif broken <= 3:
        health = "yellow"
        status = "WARN"
    else:
        health = "red"
        status = "FAIL"

    return {
        "broken": broken,
        "target": TARGETS["cross_references_broken"],
        "health": health,
        "status": status,
    }


def colorize(text: str, health: str, use_color: bool = True) -> str:
    """Colorize text based on health status."""
    if not use_color:
        return text

    color_map = {
        "green": Colors.GREEN,
        "yellow": Colors.YELLOW,
        "red": Colors.RED,
    }

    color = color_map.get(health, "")
    return f"{color}{text}{Colors.END}" if color else text


def format_delta(value: float, is_percentage: bool = False, invert: bool = False) -> str:
    """Format a delta value with appropriate sign."""
    if value == 0:
        return "±0" + ("%" if is_percentage else "")

    sign = "-" if (value < 0) != invert else "+"
    abs_value = abs(value)

    if is_percentage:
        return f"{sign}{abs_value:.1f}%"
    else:
        return f"{sign}{abs_value:.0f}"


def print_terminal_dashboard(
    quality: dict[str, Any],
    tokens: dict[str, Any],
    cross_refs: dict[str, Any],
    use_color: bool = True,
) -> None:
    """Print ASCII art dashboard to terminal."""
    width = 80
    sep = "=" * width

    print()
    print(sep)
    print(f"{Colors.BOLD if use_color else ''}TOKEN EFFICIENCY DASHBOARD{Colors.END if use_color else ''}".center(width + (len(Colors.BOLD) + len(Colors.END) if use_color else 0)))
    print(sep)
    print()

    # Quality section
    print(f"{Colors.BOLD if use_color else ''}📊 QUALITY METRICS{Colors.END if use_color else ''}")
    print()

    quality_status = colorize(quality["status"], quality["health"], use_color)
    quality_indicator = colorize("●", quality["health"], use_color)

    print(f"  {quality_indicator} Pass Rate: {quality['passing']}/{quality['total']} skills "
          f"({quality['pass_rate']:.0f}%) - Target: {quality['target']}%")
    print(f"     Status: {quality_status}")

    if quality['failing'] > 0:
        print(f"     {colorize('⚠', 'yellow', use_color)} {quality['failing']} skills need attention")
    print()

    # Token section
    print(f"{Colors.BOLD if use_color else ''}💾 TOKEN METRICS{Colors.END if use_color else ''}")
    print()

    token_status = colorize(tokens["status"], tokens["health"], use_color)
    token_indicator = colorize("●", tokens["health"], use_color)

    delta_str = format_delta(tokens["delta_total"])
    delta_pct_str = format_delta(tokens["delta_pct"], is_percentage=True)

    print(f"  {token_indicator} Total Skill Tokens: {tokens['total_tokens']:,} "
          f"({delta_str} / {delta_pct_str} from baseline)")
    print(f"     Baseline: {tokens['baseline_total']:,}")
    print(f"     Average/Skill: {tokens['avg_tokens']:.0f} "
          f"(baseline: {tokens['baseline_avg']})")
    print(f"     Status: {token_status}")

    if tokens['over_500'] > 0:
        print(f"     {colorize('⚠', 'yellow', use_color)} {tokens['over_500']} skills over 500 lines")
    print()

    # Cross-reference section
    print(f"{Colors.BOLD if use_color else ''}🔗 CROSS-REFERENCE INTEGRITY{Colors.END if use_color else ''}")
    print()

    cross_ref_status = colorize(cross_refs["status"], cross_refs["health"], use_color)
    cross_ref_indicator = colorize("●", cross_refs["health"], use_color)

    print(f"  {cross_ref_indicator} Broken References: {cross_refs['broken']} "
          f"(target: {cross_refs['target']})")
    print(f"     Status: {cross_ref_status}")
    print()

    # Overall health
    print(sep)
    all_health = [quality["health"], tokens["health"], cross_refs["health"]]
    if all(h == "green" for h in all_health):
        overall = colorize("✓ ALL SYSTEMS HEALTHY", "green", use_color)
    elif any(h == "red" for h in all_health):
        overall = colorize("✗ CRITICAL ISSUES DETECTED", "red", use_color)
    else:
        overall = colorize("⚠ WARNINGS PRESENT", "yellow", use_color)

    print(f"Overall: {overall}")
    print(sep)
    print()


def print_markdown_dashboard(
    quality: dict[str, Any],
    tokens: dict[str, Any],
    cross_refs: dict[str, Any],
) -> None:
    """Print markdown-formatted dashboard."""
    print("# Token Efficiency Dashboard")
    print()
    print("## Status Overview")
    print()

    # Status table
    print("| Component | Status | Current | Target | Health |")
    print("|-----------|--------|---------|--------|--------|")

    # Quality
    quality_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}[quality["health"]]
    print(f"| Quality | {quality['status']} | {quality['passing']}/{quality['total']} ({quality['pass_rate']:.0f}%) | {quality['target']}% | {quality_emoji} |")

    # Tokens
    token_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}[tokens["health"]]
    delta_str = format_delta(tokens["delta_pct"], is_percentage=True)
    print(f"| Tokens | {tokens['status']} | {tokens['total_tokens']:,} ({delta_str}) | {tokens['baseline_total']:,} | {token_emoji} |")

    # Cross-refs
    cross_ref_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}[cross_refs["health"]]
    print(f"| Cross-refs | {cross_refs['status']} | {cross_refs['broken']} broken | {cross_refs['target']} | {cross_ref_emoji} |")

    print()
    print("## Detailed Metrics")
    print()

    # Quality details
    print("### Quality Metrics")
    print()
    print(f"- **Passing skills:** {quality['passing']}/{quality['total']} ({quality['pass_rate']:.1f}%)")
    print(f"- **Failing skills:** {quality['failing']}")
    print(f"- **Target:** {quality['target']}%")
    print()

    # Token details
    print("### Token Metrics")
    print()
    print(f"- **Total skill tokens:** {tokens['total_tokens']:,}")
    print(f"- **Baseline:** {tokens['baseline_total']:,}")
    print(f"- **Delta:** {format_delta(tokens['delta_total'])} tokens ({format_delta(tokens['delta_pct'], is_percentage=True)})")
    print(f"- **Average per skill:** {tokens['avg_tokens']:.0f} (baseline: {tokens['baseline_avg']})")
    print(f"- **Skills over 500 lines:** {tokens['over_500']}")
    print()

    # Cross-ref details
    print("### Cross-Reference Integrity")
    print()
    print(f"- **Broken references:** {cross_refs['broken']}")
    print(f"- **Target:** {cross_refs['target']}")
    print()

    # Overall
    all_health = [quality["health"], tokens["health"], cross_refs["health"]]
    if all(h == "green" for h in all_health):
        overall = "✅ All systems healthy"
    elif any(h == "red" for h in all_health):
        overall = "❌ Critical issues detected"
    else:
        overall = "⚠️ Warnings present"

    print("## Overall Status")
    print()
    print(f"**{overall}**")
    print()


def main() -> None:
    """Display token efficiency dashboard."""
    parser = argparse.ArgumentParser(
        description="Display real-time token efficiency monitoring dashboard"
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Output markdown format instead of terminal dashboard",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable color output in terminal mode",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON data",
    )
    args = parser.parse_args()

    use_color = not args.no_color and not args.markdown and not args.json

    # Collect metrics
    quality = get_quality_status(use_color)
    tokens = get_token_status(use_color)
    cross_refs = get_cross_ref_status(use_color)

    # Output
    if args.json:
        data = {
            "quality": quality,
            "tokens": tokens,
            "cross_refs": cross_refs,
        }
        print(json.dumps(data, indent=2))
    elif args.markdown:
        print_markdown_dashboard(quality, tokens, cross_refs)
    else:
        print_terminal_dashboard(quality, tokens, cross_refs, use_color)


if __name__ == "__main__":
    main()
