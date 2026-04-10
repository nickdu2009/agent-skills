#!/usr/bin/env python3
"""Check for token efficiency baseline regressions.

Compares current metrics against baseline and reports regressions.

Usage:
    python3 maintainer/scripts/analysis/check_baseline_regression.py \\
        --baseline maintainer/data/token_efficiency_baseline.md \\
        --current current_metrics.json

    python3 maintainer/scripts/analysis/check_baseline_regression.py \\
        --baseline maintainer/data/token_efficiency_baseline.md \\
        --current current_metrics.json \\
        --fail-on-regression
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]


def parse_baseline_from_markdown(baseline_path: Path) -> dict[str, Any]:
    """Extract baseline metrics from token_efficiency_baseline.md.

    This is a simplified parser that extracts key numbers from the markdown.
    For a real implementation, you'd parse the tables more carefully.
    """
    if not baseline_path.exists():
        return {}

    content = baseline_path.read_text(encoding="utf-8")
    baseline = {}

    # Extract governance templates total
    match = re.search(r"Governance templates tokens.*?~(\d+)", content)
    if match:
        baseline["governance_templates_tokens"] = int(match.group(1))

    # Extract average skill tokens
    match = re.search(r"Average skill tokens.*?~(\d+)", content)
    if match:
        baseline["avg_skill_tokens"] = int(match.group(1))

    # Extract max skill body tokens
    match = re.search(r"Max skill body tokens.*?~(\d+)", content)
    if match:
        baseline["max_skill_body_tokens"] = int(match.group(1))

    # Alternative: try to find in the baseline table section
    # Look for "Governance templates tokens | ~4,556"
    match = re.search(r"\|\s*Governance templates tokens\s*\|\s*~?(\d+(?:,\d+)?)", content)
    if match:
        baseline["governance_templates_tokens"] = int(match.group(1).replace(",", ""))

    match = re.search(r"\|\s*Average skill tokens\s*\|\s*~?(\d+(?:,\d+)?)", content)
    if match:
        baseline["avg_skill_tokens"] = int(match.group(1).replace(",", ""))

    match = re.search(r"\|\s*Max skill body tokens\s*\|\s*~?(\d+(?:,\d+)?)", content)
    if match:
        baseline["max_skill_body_tokens"] = int(match.group(1).replace(",", ""))

    return baseline


def check_regression(
    baseline: dict,
    current: dict,
    *,
    threshold: float = 0.20,
    warning_threshold: float = 0.10,
) -> tuple[int, list[str], list[str]]:
    """Compare current metrics against baseline.

    Args:
        baseline: Baseline metrics (can be from JSON or parsed from markdown)
        current: Current metrics from measure_prompt_surface.py --json
        threshold: Fail threshold (default: 0.20 = 20%)
        warning_threshold: Warning threshold (default: 0.10 = 10%)

    Returns:
        (exit_code, failures, warnings) where:
        - exit_code: 0 if no regression, 1 if regression detected
        - failures: List of failure messages
        - warnings: List of warning messages
    """
    failures = []
    warnings = []

    # Extract current metrics
    current_gov_tokens = current.get("governance_templates", {}).get("total_tokens", 0)
    current_avg_skill = current.get("skill_files", {}).get("avg_tokens_per_skill", 0)
    current_max_body = max(
        (skill.get("body_tokens", 0) for skill in current.get("skill_files", {}).get("skills", [])),
        default=0
    )
    current_over_500 = current.get("skill_files", {}).get("over_500_count", 0)

    # Extract baseline metrics
    baseline_gov = baseline.get("governance_templates_tokens", 0)
    baseline_avg = baseline.get("avg_skill_tokens", 0)
    baseline_max = baseline.get("max_skill_body_tokens", 0)

    # If baseline is from measure_prompt_surface.py --json (nested structure)
    if "governance_templates" in baseline:
        baseline_gov = baseline.get("governance_templates", {}).get("total_tokens", baseline_gov)
        baseline_avg = baseline.get("skill_files", {}).get("avg_tokens_per_skill", baseline_avg)
        baseline_skills = baseline.get("skill_files", {}).get("skills", [])
        if baseline_skills:
            baseline_max = max((s.get("body_tokens", 0) for s in baseline_skills), default=baseline_max)

    # Check governance templates
    if baseline_gov > 0:
        fail_limit = baseline_gov * (1 + threshold)
        warn_limit = baseline_gov * (1 + warning_threshold)

        if current_gov_tokens > fail_limit:
            failures.append(
                f"Governance templates: {current_gov_tokens} tokens > {fail_limit:.0f} "
                f"(baseline {baseline_gov}, +{threshold*100:.0f}% threshold)"
            )
        elif current_gov_tokens > warn_limit:
            warnings.append(
                f"Governance templates: {current_gov_tokens} tokens > {warn_limit:.0f} "
                f"(baseline {baseline_gov}, +{warning_threshold*100:.0f}% warning)"
            )

    # Check average skill size
    if baseline_avg > 0:
        fail_limit = baseline_avg * (1 + threshold)
        warn_limit = baseline_avg * (1 + warning_threshold)

        if current_avg_skill > fail_limit:
            failures.append(
                f"Average skill: {current_avg_skill:.0f} tokens > {fail_limit:.0f} "
                f"(baseline {baseline_avg:.0f}, +{threshold*100:.0f}% threshold)"
            )
        elif current_avg_skill > warn_limit:
            warnings.append(
                f"Average skill: {current_avg_skill:.0f} tokens > {warn_limit:.0f} "
                f"(baseline {baseline_avg:.0f}, +{warning_threshold*100:.0f}% warning)"
            )

    # Check max skill body tokens
    if baseline_max > 0:
        fail_limit = baseline_max * (1 + threshold)
        warn_limit = baseline_max * (1 + warning_threshold)

        if current_max_body > fail_limit:
            failures.append(
                f"Max skill body: {current_max_body} tokens > {fail_limit:.0f} "
                f"(baseline {baseline_max}, +{threshold*100:.0f}% threshold)"
            )
        elif current_max_body > warn_limit:
            warnings.append(
                f"Max skill body: {current_max_body} tokens > {warn_limit:.0f} "
                f"(baseline {baseline_max}, +{warning_threshold*100:.0f}% warning)"
            )

    # Check skills over 500 lines (hard limit)
    if current_over_500 > 1:
        failures.append(f"Skills over 500 lines: {current_over_500} > 1 (hard limit)")
    elif current_over_500 > 0:
        warnings.append(f"Skills over 500 lines: {current_over_500} (target: 0)")

    exit_code = 1 if failures else 0
    return exit_code, failures, warnings


def main() -> int:
    """Run baseline regression check."""
    parser = argparse.ArgumentParser(
        description="Check for token efficiency baseline regressions"
    )
    parser.add_argument(
        "--baseline",
        required=True,
        help="Path to baseline metrics (JSON or markdown)",
    )
    parser.add_argument(
        "--current",
        required=True,
        help="Path to current metrics JSON (from measure_prompt_surface.py --json)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.20,
        help="Regression fail threshold (default: 0.20 = 20%%)",
    )
    parser.add_argument(
        "--warning-threshold",
        type=float,
        default=0.10,
        help="Warning threshold (default: 0.10 = 10%%)",
    )
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit with non-zero status if regression detected",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Exit with non-zero status even on warnings",
    )
    args = parser.parse_args()

    baseline_path = Path(args.baseline)
    current_path = Path(args.current)

    if not baseline_path.exists():
        print(f"Error: Baseline file not found: {baseline_path}", file=sys.stderr)
        return 1

    if not current_path.exists():
        print(f"Error: Current metrics file not found: {current_path}", file=sys.stderr)
        return 1

    # Load baseline (JSON or markdown)
    if baseline_path.suffix == ".json":
        baseline = json.loads(baseline_path.read_text())
    else:
        baseline = parse_baseline_from_markdown(baseline_path)

    # Load current metrics
    current = json.loads(current_path.read_text())

    # Check for regressions
    exit_code, failures, warnings = check_regression(
        baseline,
        current,
        threshold=args.threshold,
        warning_threshold=args.warning_threshold,
    )

    # Report results
    print("=" * 80)
    print("Baseline Regression Check")
    print("=" * 80)
    print()

    if failures:
        print("✗ REGRESSIONS DETECTED:")
        for failure in failures:
            print(f"  - {failure}")
        print()

    if warnings:
        print("⚠ WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
        print()

    if not failures and not warnings:
        print("✓ No baseline regression detected")
        print()

    # Determine exit code
    if args.fail_on_regression and failures:
        return 1
    if args.fail_on_warning and (failures or warnings):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
