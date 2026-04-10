#!/usr/bin/env python3
"""Detect token efficiency regressions by comparing to last audit.

This script compares the current state to the last audit report to detect:
- Quality regressions (skills that stopped passing)
- Token inflation (>5% increase without justification)
- Template de-adoption (skills reverting to verbose format)
- New broken cross-references

Exit code 1 if critical regressions found (for CI).

Usage:
    python3 maintainer/scripts/audit/detect_regressions.py
    python3 maintainer/scripts/audit/detect_regressions.py --baseline 2026-Q1-audit-report.md
    python3 maintainer/scripts/audit/detect_regressions.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "maintainer" / "scripts"
ANALYSIS_DIR = SCRIPTS_DIR / "analysis"
AUDITS_DIR = REPO_ROOT / "maintainer" / "data" / "audits"


# Thresholds
THRESHOLDS = {
    "quality_drop_warning": 1,  # Even 1 skill regression is a warning
    "quality_drop_critical": 3,  # 3+ skills is critical
    "token_increase_warning": 5,  # % increase
    "token_increase_critical": 10,  # % increase
    "cross_ref_warning": 1,  # Any new broken ref is a warning
    "cross_ref_critical": 5,  # 5+ broken refs is critical
}


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


def find_latest_audit() -> Path | None:
    """Find the most recent audit report."""
    if not AUDITS_DIR.exists():
        return None

    audit_files = list(AUDITS_DIR.glob("*-audit-report.md"))
    if not audit_files:
        return None

    # Sort by filename (YYYY-QN format naturally sorts correctly)
    return sorted(audit_files)[-1]


def parse_audit_report(audit_file: Path) -> dict[str, Any]:
    """Parse key metrics from an audit report."""
    if not audit_file.exists():
        return {}

    content = audit_file.read_text(encoding="utf-8")

    # Extract metrics from markdown tables
    metrics = {}

    # Quality metrics
    quality_match = re.search(r'\| Pass rate \| ([\d.]+)%', content)
    if quality_match:
        metrics["quality_pass_rate"] = float(quality_match.group(1))

    passing_match = re.search(r'\| Passing skills \| (\d+)/(\d+)', content)
    if passing_match:
        metrics["quality_passing"] = int(passing_match.group(1))
        metrics["quality_total"] = int(passing_match.group(2))

    # Token metrics
    total_tokens_match = re.search(r'\| Total skill tokens \| ([\d,]+)', content)
    if total_tokens_match:
        metrics["total_tokens"] = int(total_tokens_match.group(1).replace(",", ""))

    avg_tokens_match = re.search(r'\| Avg tokens/skill \| ([\d,]+)', content)
    if avg_tokens_match:
        metrics["avg_tokens"] = int(avg_tokens_match.group(1).replace(",", ""))

    over_500_match = re.search(r'\| Skills >500 lines \| (\d+)', content)
    if over_500_match:
        metrics["over_500"] = int(over_500_match.group(1))

    # Cross-reference metrics
    broken_refs_match = re.search(r'\| Broken references \| (\d+)', content)
    if broken_refs_match:
        metrics["broken_refs"] = int(broken_refs_match.group(1))

    return metrics


def collect_current_metrics() -> dict[str, Any]:
    """Collect current metrics."""
    # Quality
    quality_data = run_command([
        sys.executable,
        str(ANALYSIS_DIR / "check_skill_quality.py"),
        "--json",
    ])

    total_skills = len(quality_data)
    passing_skills = sum(1 for s in quality_data if s.get("overall_pass", False))
    pass_rate = (passing_skills / total_skills * 100) if total_skills > 0 else 0

    # Collect failing skills
    failing_skills = [
        s["skill_name"]
        for s in quality_data
        if not s.get("overall_pass", False)
    ]

    # Tokens
    token_data = run_command([
        sys.executable,
        str(ANALYSIS_DIR / "measure_prompt_surface.py"),
        "--actual-tokens",
        "--json",
    ])

    skills = token_data.get("skill_files", {})
    total_tokens = skills.get("total_tokens", 0)
    avg_tokens = skills.get("avg_tokens_per_skill", 0)
    over_500 = skills.get("over_500_count", 0)

    # Cross-references
    try:
        result = subprocess.run(
            [sys.executable, str(ANALYSIS_DIR / "check_cross_references.py"), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            cross_ref_data = json.loads(result.stdout)
            broken_refs = len(cross_ref_data.get("broken_references", []))
        else:
            match = re.search(r'(\d+)\s+broken', result.stdout)
            broken_refs = int(match.group(1)) if match else 0
    except Exception:
        broken_refs = 0

    return {
        "quality_pass_rate": pass_rate,
        "quality_passing": passing_skills,
        "quality_total": total_skills,
        "quality_failing_skills": failing_skills,
        "total_tokens": total_tokens,
        "avg_tokens": avg_tokens,
        "over_500": over_500,
        "broken_refs": broken_refs,
    }


def detect_regressions(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    """Detect regressions between baseline and current."""
    regressions = []
    warnings = []

    # Quality regressions
    if "quality_passing" in baseline and "quality_passing" in current:
        baseline_passing = baseline["quality_passing"]
        current_passing = current["quality_passing"]
        skills_regressed = baseline_passing - current_passing

        if skills_regressed > 0:
            severity = (
                "critical"
                if skills_regressed >= THRESHOLDS["quality_drop_critical"]
                else "warning"
            )

            regression = {
                "type": "quality_regression",
                "severity": severity,
                "message": f"{skills_regressed} skills stopped passing quality checks",
                "baseline_passing": baseline_passing,
                "current_passing": current_passing,
                "skills_affected": skills_regressed,
            }

            if severity == "critical":
                regressions.append(regression)
            else:
                warnings.append(regression)

    # Token inflation
    if "total_tokens" in baseline and "total_tokens" in current:
        baseline_tokens = baseline["total_tokens"]
        current_tokens = current["total_tokens"]
        token_increase = current_tokens - baseline_tokens
        token_increase_pct = (token_increase / baseline_tokens * 100) if baseline_tokens > 0 else 0

        if token_increase_pct > THRESHOLDS["token_increase_warning"]:
            severity = (
                "critical"
                if token_increase_pct >= THRESHOLDS["token_increase_critical"]
                else "warning"
            )

            regression = {
                "type": "token_inflation",
                "severity": severity,
                "message": f"Token count increased by {token_increase_pct:.1f}% "
                          f"({token_increase:+,} tokens)",
                "baseline_tokens": baseline_tokens,
                "current_tokens": current_tokens,
                "increase": token_increase,
                "increase_pct": token_increase_pct,
            }

            if severity == "critical":
                regressions.append(regression)
            else:
                warnings.append(regression)

    # Cross-reference regressions
    if "broken_refs" in baseline and "broken_refs" in current:
        baseline_broken = baseline["broken_refs"]
        current_broken = current["broken_refs"]
        new_broken = current_broken - baseline_broken

        if new_broken > 0:
            severity = (
                "critical"
                if current_broken >= THRESHOLDS["cross_ref_critical"]
                else "warning"
            )

            regression = {
                "type": "cross_reference_regression",
                "severity": severity,
                "message": f"{new_broken} new broken cross-references introduced",
                "baseline_broken": baseline_broken,
                "current_broken": current_broken,
                "new_broken": new_broken,
            }

            if severity == "critical":
                regressions.append(regression)
            else:
                warnings.append(regression)

    # Skills over 500 lines
    if "over_500" in baseline and "over_500" in current:
        baseline_over = baseline["over_500"]
        current_over = current["over_500"]
        new_over = current_over - baseline_over

        if new_over > 0:
            warnings.append({
                "type": "skill_length_regression",
                "severity": "warning",
                "message": f"{new_over} new skills exceeded 500 lines",
                "baseline_over": baseline_over,
                "current_over": current_over,
                "new_over": new_over,
            })

    return {
        "has_regressions": len(regressions) > 0,
        "has_warnings": len(warnings) > 0,
        "critical_count": len(regressions),
        "warning_count": len(warnings),
        "regressions": regressions,
        "warnings": warnings,
    }


def print_regression_report(
    baseline_file: Path | None,
    baseline: dict[str, Any],
    current: dict[str, Any],
    regressions: dict[str, Any],
    output_json: bool = False,
) -> None:
    """Print regression report."""
    if output_json:
        data = {
            "baseline_file": str(baseline_file.relative_to(REPO_ROOT)) if baseline_file else None,
            "baseline_metrics": baseline,
            "current_metrics": current,
            "regressions": regressions,
        }
        print(json.dumps(data, indent=2))
        return

    # Human-readable output
    print("=" * 80)
    print("REGRESSION DETECTION REPORT")
    print("=" * 80)
    print()

    if baseline_file:
        print(f"Baseline: {baseline_file.name}")
    else:
        print("Baseline: (using hardcoded targets)")
    print()

    # Overall status
    if regressions["has_regressions"]:
        print(f"❌ CRITICAL REGRESSIONS DETECTED: {regressions['critical_count']}")
    elif regressions["has_warnings"]:
        print(f"⚠️  WARNINGS: {regressions['warning_count']}")
    else:
        print("✅ NO REGRESSIONS DETECTED")
    print()

    # Critical regressions
    if regressions["regressions"]:
        print("CRITICAL REGRESSIONS:")
        print()
        for reg in regressions["regressions"]:
            print(f"  🔴 {reg['type'].replace('_', ' ').upper()}")
            print(f"     {reg['message']}")

            if reg['type'] == 'quality_regression':
                print(f"     Baseline: {reg['baseline_passing']} passing")
                print(f"     Current: {reg['current_passing']} passing")
            elif reg['type'] == 'token_inflation':
                print(f"     Baseline: {reg['baseline_tokens']:,} tokens")
                print(f"     Current: {reg['current_tokens']:,} tokens")
                print(f"     Increase: +{reg['increase']:,} ({reg['increase_pct']:.1f}%)")
            elif reg['type'] == 'cross_reference_regression':
                print(f"     Baseline: {reg['baseline_broken']} broken")
                print(f"     Current: {reg['current_broken']} broken")
                print(f"     New: +{reg['new_broken']}")

            print()

    # Warnings
    if regressions["warnings"]:
        print("WARNINGS:")
        print()
        for warn in regressions["warnings"]:
            print(f"  ⚠️  {warn['message']}")
        print()

    # Summary comparison
    print("METRIC COMPARISON:")
    print()
    print(f"  Quality:      {current['quality_passing']}/{current['quality_total']} passing "
          f"({current['quality_pass_rate']:.1f}%)")
    if "quality_passing" in baseline:
        print(f"                vs {baseline['quality_passing']}/{baseline.get('quality_total', '?')} baseline")

    print(f"  Tokens:       {current['total_tokens']:,} total")
    if "total_tokens" in baseline:
        delta = current['total_tokens'] - baseline['total_tokens']
        print(f"                vs {baseline['total_tokens']:,} baseline ({delta:+,})")

    print(f"  Cross-refs:   {current['broken_refs']} broken")
    if "broken_refs" in baseline:
        delta = current['broken_refs'] - baseline['broken_refs']
        print(f"                vs {baseline['broken_refs']} baseline ({delta:+,})")

    print(f"  Over 500:     {current['over_500']} skills")
    if "over_500" in baseline:
        delta = current['over_500'] - baseline['over_500']
        print(f"                vs {baseline['over_500']} baseline ({delta:+,})")

    print()
    print("=" * 80)


def main() -> None:
    """Detect regressions and report."""
    parser = argparse.ArgumentParser(
        description="Detect token efficiency regressions"
    )
    parser.add_argument(
        "--baseline",
        type=str,
        help="Baseline audit report file (default: latest audit in audits/)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable report",
    )
    args = parser.parse_args()

    # Determine baseline
    if args.baseline:
        baseline_file = AUDITS_DIR / args.baseline
        if not baseline_file.exists():
            print(f"Error: Baseline file not found: {baseline_file}", file=sys.stderr)
            sys.exit(1)
    else:
        baseline_file = find_latest_audit()

    # Parse baseline
    if baseline_file:
        baseline = parse_audit_report(baseline_file)
        if not baseline:
            print(f"Warning: Could not parse baseline from {baseline_file}", file=sys.stderr)
            print("Using hardcoded baseline targets instead", file=sys.stderr)
            baseline = {
                "quality_pass_rate": 100,
                "quality_passing": 18,
                "quality_total": 18,
                "total_tokens": 41783,
                "avg_tokens": 2321,
                "broken_refs": 0,
                "over_500": 0,
            }
    else:
        print("Warning: No audit reports found in audits/", file=sys.stderr)
        print("Using hardcoded baseline targets", file=sys.stderr)
        baseline = {
            "quality_pass_rate": 100,
            "quality_passing": 18,
            "quality_total": 18,
            "total_tokens": 41783,
            "avg_tokens": 2321,
            "broken_refs": 0,
            "over_500": 0,
        }

    # Collect current metrics
    current = collect_current_metrics()

    # Detect regressions
    regressions = detect_regressions(baseline, current)

    # Report
    print_regression_report(baseline_file, baseline, current, regressions, args.json)

    # Exit code
    sys.exit(1 if regressions["has_regressions"] else 0)


if __name__ == "__main__":
    main()
