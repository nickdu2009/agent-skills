#!/usr/bin/env python3
"""Check for token efficiency baseline regressions.

Compares current metrics against baseline and reports regressions.

Usage:
    python3 maintainer/scripts/analysis/check_baseline_regression.py \\
        --baseline maintainer/data/token_efficiency_baseline.json \\
        --current current_metrics.json

    python3 maintainer/scripts/analysis/check_baseline_regression.py \\
        --baseline maintainer/data/token_efficiency_baseline.json \\
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
EXPECTED_MEASUREMENT_IDENTITY: dict[str, str] = {
    "measurement_contract_version": "1.0",
    "token_counter": "tiktoken",
    "counter_version": "0.13.0",
    "tokenizer": "o200k_base",
}


class MeasurementIdentityError(RuntimeError):
    """A token measurement cannot be compared under the locked contract."""


def validate_measurement_identity(
    data: dict[str, Any],
    *,
    source: str,
) -> dict[str, str]:
    """Require the complete, exact token measurement identity."""

    if not isinstance(data, dict):
        raise MeasurementIdentityError(f"{source} must be a JSON/object mapping")
    missing = [
        field for field in EXPECTED_MEASUREMENT_IDENTITY if field not in data
    ]
    if missing:
        raise MeasurementIdentityError(
            f"{source} is legacy or unsupported: missing measurement identity "
            + ", ".join(missing)
        )
    mismatches = [
        f"{field}: expected {expected!r}, got {data.get(field)!r}"
        for field, expected in EXPECTED_MEASUREMENT_IDENTITY.items()
        if data.get(field) != expected
    ]
    if mismatches:
        raise MeasurementIdentityError(
            f"{source} measurement identity mismatch: " + "; ".join(mismatches)
        )
    return dict(EXPECTED_MEASUREMENT_IDENTITY)


def validate_measurement_pair(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> None:
    """Fail closed unless both inputs use the locked measurement identity."""

    validate_measurement_identity(baseline, source="baseline")
    validate_measurement_identity(current, source="current metrics")
    current_method = current.get("token_counting_method")
    if current_method != EXPECTED_MEASUREMENT_IDENTITY["tokenizer"]:
        raise MeasurementIdentityError(
            "current metrics token_counting_method mismatch: "
            f"expected {EXPECTED_MEASUREMENT_IDENTITY['tokenizer']!r}, "
            f"got {current_method!r}"
        )


def parse_baseline_from_markdown(baseline_path: Path) -> dict[str, Any]:
    """Extract baseline metrics from token_efficiency_baseline.md.

    This is a simplified parser that extracts key numbers from the markdown.
    For a real implementation, you'd parse the tables more carefully.
    """
    if not baseline_path.exists():
        raise FileNotFoundError(f"baseline file not found: {baseline_path}")

    content = baseline_path.read_text(encoding="utf-8")
    baseline = {}

    identity_labels = {
        "measurement_contract_version": "Measurement contract version",
        "token_counter": "Token counter",
        "counter_version": "Counter version",
        "tokenizer": "Tokenizer",
    }
    for field, label in identity_labels.items():
        match = re.search(
            rf"\*\*{re.escape(label)}:\*\* `([^`]+)`",
            content,
            re.IGNORECASE,
        )
        if match:
            baseline[field] = match.group(1)
    validate_measurement_identity(
        baseline,
        source=f"Markdown baseline {baseline_path}",
    )

    match = re.search(r"Average `SKILL\.md` size is ([\d,]+) tokens", content)
    if match:
        baseline["avg_skill_tokens"] = int(match.group(1).replace(",", ""))

    match = re.search(r"Largest Skill body is ([\d,]+) tokens", content, re.IGNORECASE)
    if match:
        baseline["max_skill_body_tokens"] = int(match.group(1).replace(",", ""))

    match = re.search(r"\|\s*All \d+ `SKILL\.md` files\s*\|\s*([\d,]+)", content)
    if match:
        baseline["total_skill_tokens"] = int(match.group(1).replace(",", ""))

    for label, key in (
        (r"All package text", "all_packages_tokens_upper_bound"),
        (r"Root `AGENTS\.md`", "repository_governance_tokens"),
    ):
        match = re.search(rf"\|\s*{label}\s*\|\s*([\d,]+)", content)
        if match:
            baseline[key] = int(match.group(1).replace(",", ""))

    return baseline


def check_regression(
    baseline: dict,
    current: dict,
    *,
    threshold: float = 0.10,
    warning_threshold: float = 0.05,
) -> tuple[int, list[str], list[str]]:
    """Compare current metrics against baseline.

    Args:
        baseline: Baseline metrics (can be from JSON or parsed from markdown)
        current: Current metrics from measure_prompt_surface.py --json
        threshold: Fail threshold (default: 0.10 = 10%)
        warning_threshold: Warning threshold (default: 0.05 = 5%)

    Returns:
        (exit_code, failures, warnings) where:
        - exit_code: 0 if no regression, 1 if regression detected
        - failures: List of failure messages
        - warnings: List of warning messages
    """
    validate_measurement_pair(baseline, current)
    failures = []
    warnings = []

    # Extract current metrics
    current_avg_skill = current.get("skill_files", {}).get("avg_tokens_per_skill", 0)
    current_total_skill = current.get("skill_files", {}).get("total_tokens", 0)
    current_max_body = max(
        (skill.get("body_tokens", 0) for skill in current.get("skill_files", {}).get("skills", [])),
        default=0
    )
    current_over_500 = current.get("skill_files", {}).get("over_500_count", 0)
    current_package_tokens = current.get("skill_files", {}).get(
        "all_packages_tokens_upper_bound",
        0,
    )
    current_governance_tokens = current.get("repository_governance", {}).get("tokens", 0)

    # Extract baseline metrics
    baseline_avg = baseline.get("avg_skill_tokens", 0)
    baseline_max = baseline.get("max_skill_body_tokens", 0)
    baseline_total_skill = baseline.get("total_skill_tokens", 0)
    baseline_package_tokens = baseline.get("all_packages_tokens_upper_bound", 0)
    baseline_governance_tokens = baseline.get("repository_governance_tokens", 0)

    # If baseline is from measure_prompt_surface.py --json (nested structure)
    if "skill_files" in baseline:
        baseline_avg = baseline.get("skill_files", {}).get("avg_tokens_per_skill", baseline_avg)
        baseline_total_skill = baseline.get("skill_files", {}).get("total_tokens", baseline_total_skill)
        baseline_package_tokens = baseline.get("skill_files", {}).get(
            "all_packages_tokens_upper_bound",
            baseline_package_tokens,
        )
        baseline_governance_tokens = baseline.get("repository_governance", {}).get(
            "tokens",
            baseline_governance_tokens,
        )
        baseline_skills = baseline.get("skill_files", {}).get("skills", [])
        if baseline_skills:
            baseline_max = max((s.get("body_tokens", 0) for s in baseline_skills), default=baseline_max)

    if baseline_total_skill > 0:
        fail_limit = baseline_total_skill * (1 + threshold)
        warn_limit = baseline_total_skill * (1 + warning_threshold)
        if current_total_skill >= fail_limit:
            failures.append(
                f"All SKILL.md files: {current_total_skill} tokens > {fail_limit:.0f} "
                f"(baseline {baseline_total_skill}, +{threshold*100:.0f}% threshold)"
            )
        elif current_total_skill > warn_limit:
            warnings.append(
                f"All SKILL.md files: {current_total_skill} tokens > {warn_limit:.0f} "
                f"(baseline {baseline_total_skill}, +{warning_threshold*100:.0f}% warning)"
            )

    for label, current_value, baseline_value in (
        ("All package text", current_package_tokens, baseline_package_tokens),
        ("Repository governance", current_governance_tokens, baseline_governance_tokens),
    ):
        if baseline_value <= 0:
            continue
        fail_limit = baseline_value * (1 + threshold)
        warn_limit = baseline_value * (1 + warning_threshold)
        if current_value >= fail_limit:
            failures.append(
                f"{label}: {current_value} tokens >= {fail_limit:.0f} "
                f"(baseline {baseline_value}, +{threshold*100:.0f}% threshold)"
            )
        elif current_value > warn_limit:
            warnings.append(
                f"{label}: {current_value} tokens > {warn_limit:.0f} "
                f"(baseline {baseline_value}, +{warning_threshold*100:.0f}% warning)"
            )

    # Check average skill size
    if baseline_avg > 0:
        fail_limit = baseline_avg * (1 + threshold)
        warn_limit = baseline_avg * (1 + warning_threshold)

        if current_avg_skill >= fail_limit:
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

        if current_max_body >= fail_limit:
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
        default=0.10,
        help="Regression fail threshold (default: 0.10 = 10%%)",
    )
    parser.add_argument(
        "--warning-threshold",
        type=float,
        default=0.05,
        help="Warning threshold (default: 0.05 = 5%%)",
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

    try:
        if not baseline_path.exists():
            raise FileNotFoundError(f"baseline file not found: {baseline_path}")
        if not current_path.exists():
            raise FileNotFoundError(f"current metrics file not found: {current_path}")

        if baseline_path.suffix == ".json":
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            if not isinstance(baseline, dict):
                raise ValueError("baseline JSON must contain an object")
            if "skill_files" not in baseline:
                baseline = {
                    **baseline,
                    "avg_skill_tokens": baseline.get("avg_tokens_per_skill"),
                }
        elif baseline_path.suffix.lower() in {".md", ".markdown"}:
            baseline = parse_baseline_from_markdown(baseline_path)
        else:
            raise ValueError(
                f"unsupported baseline format: {baseline_path.suffix or '<none>'}"
            )

        required_baseline_fields = {
            "avg_skill_tokens",
            "all_packages_tokens_upper_bound",
            "max_skill_body_tokens",
            "repository_governance_tokens",
            "total_skill_tokens",
        }
        if "skill_files" not in baseline:
            missing = sorted(required_baseline_fields - set(baseline))
            if missing:
                raise ValueError(
                    "baseline is missing required metrics: " + ", ".join(missing)
                )

        current = json.loads(current_path.read_text(encoding="utf-8"))
        if not isinstance(current, dict):
            raise ValueError("current metrics JSON must contain an object")
        validate_measurement_pair(baseline, current)

        current_skills = current.get("skill_files")
        current_governance = current.get("repository_governance")
        if not isinstance(current_skills, dict) or not isinstance(
            current_governance, dict
        ):
            raise ValueError(
                "current metrics are missing skill_files or repository_governance"
            )
        required_current_skill_fields = {
            "avg_tokens_per_skill",
            "all_packages_tokens_upper_bound",
            "over_500_count",
            "skills",
            "total_tokens",
        }
        missing_current = sorted(
            required_current_skill_fields - current_skills.keys()
        )
        if missing_current or "tokens" not in current_governance:
            details = missing_current + (
                ["repository_governance.tokens"]
                if "tokens" not in current_governance
                else []
            )
            raise ValueError(
                "current metrics are missing: " + ", ".join(details)
            )

        exit_code, failures, warnings = check_regression(
            baseline,
            current,
            threshold=args.threshold,
            warning_threshold=args.warning_threshold,
        )
    except (
        FileNotFoundError,
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        MeasurementIdentityError,
        ValueError,
    ) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

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
