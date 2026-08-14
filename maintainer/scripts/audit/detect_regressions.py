#!/usr/bin/env python3
"""Detect token efficiency regressions against the operational baseline.

This script compares the current state to the last audit report to detect:
- Quality regressions (skills that stopped passing)
- Token inflation (>5% increase without justification)
- Template de-adoption (skills reverting to verbose format)
- New broken cross-references

Exit code 1 if critical regressions found (for CI).

Usage:
    python3 maintainer/scripts/audit/detect_regressions.py
    python3 maintainer/scripts/audit/detect_regressions.py --baseline 2026-Q3-audit-report.md
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
BASELINE_FILE = REPO_ROOT / "maintainer" / "data" / "token_efficiency_baseline.json"
EXPECTED_MEASUREMENT_IDENTITY: dict[str, str] = {
    "measurement_contract_version": "1.0",
    "token_counter": "tiktoken",
    "counter_version": "0.13.0",
    "tokenizer": "o200k_base",
}


class MeasurementIdentityError(RuntimeError):
    """A token surface is legacy, incompatible, or unverifiable."""


def validate_measurement_identity(
    data: dict[str, Any],
    *,
    source: str,
) -> dict[str, str]:
    """Require the complete locked measurement identity."""

    if not isinstance(data, dict):
        raise MeasurementIdentityError(f"{source} must be an object")
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
    validate_measurement_identity(baseline, source="baseline")
    validate_measurement_identity(current, source="current metrics")


def _file_baseline(path: Path | None = None) -> dict[str, Any]:
    """Load the fallback baseline from the shared machine-readable source."""
    path = BASELINE_FILE if path is None else path
    data = json.loads(path.read_text(encoding="utf-8"))
    identity = validate_measurement_identity(data, source=f"baseline {path}")
    return {
        **identity,
        "quality_pass_rate": data["quality_pass_rate"],
        "quality_passing": data["quality_passing"],
        "quality_total": data["quality_total"],
        "total_tokens": data["total_skill_tokens"],
        "avg_tokens": data["avg_tokens_per_skill"],
        "max_skill_body_tokens": data["max_skill_body_tokens"],
        "discovery_metadata_tokens": data["discovery_metadata_tokens"],
        "supporting_tokens": data["supporting_file_tokens"],
        "all_packages_tokens_upper_bound": data["all_packages_tokens_upper_bound"],
        "repository_governance_tokens": data["repository_governance_tokens"],
        "everything_tokens_upper_bound": data["everything_tokens_upper_bound"],
        "broken_refs": data["cross_references_broken"],
        "over_500": data["skills_over_500_lines"],
    }


# Thresholds
THRESHOLDS = {
    "quality_drop_warning": 1,  # Even 1 skill regression is a warning
    "quality_drop_critical": 3,  # 3+ skills is critical
    "token_increase_warning": 5,  # % increase
    "token_increase_critical": 10,  # % increase
    "cross_ref_warning": 1,  # Any new broken ref is a warning
    "cross_ref_critical": 4,  # 4+ broken refs is critical
    "skill_length_critical": 2,  # 2+ skills over 500 lines is critical
}

REQUIRED_HISTORICAL_BASELINE_FIELDS = frozenset({
    "tokenizer",
    "quality_pass_rate",
    "quality_passing",
    "quality_total",
    "total_tokens",
    "avg_tokens",
    "max_skill_body_tokens",
    "all_packages_tokens_upper_bound",
    "repository_governance_tokens",
    "broken_refs",
    "over_500",
})


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
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}: {e.stderr.strip()}"
        ) from e
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"command returned invalid JSON: {' '.join(cmd)}") from exc


def parse_audit_report(audit_file: Path) -> dict[str, Any]:
    """Parse key metrics from an audit report."""
    if not audit_file.exists():
        raise FileNotFoundError(f"audit baseline not found: {audit_file}")

    content = audit_file.read_text(encoding="utf-8")

    # Extract metrics from markdown tables
    metrics = {}

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
            metrics[field] = match.group(1)
    validate_measurement_identity(
        metrics,
        source=f"historical Markdown baseline {audit_file}",
    )

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

    max_tokens_match = re.search(r'\| Max skill tokens \| ([\d,]+)', content)
    if max_tokens_match:
        metrics["max_skill_body_tokens"] = int(
            max_tokens_match.group(1).replace(",", "")
        )

    package_tokens_match = re.search(r'\| All-package upper bound \| ([\d,]+)', content)
    if package_tokens_match:
        metrics["all_packages_tokens_upper_bound"] = int(
            package_tokens_match.group(1).replace(",", "")
        )

    governance_tokens_match = re.search(r'\| Repository governance \| ([\d,]+)', content)
    if governance_tokens_match:
        metrics["repository_governance_tokens"] = int(
            governance_tokens_match.group(1).replace(",", "")
        )

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
    identity = validate_measurement_identity(
        token_data,
        source="current token measurement",
    )
    if token_data.get("token_counting_method") != identity["tokenizer"]:
        raise RuntimeError(
            "token measurement method mismatch: "
            f"expected {identity['tokenizer']}, "
            f"got {token_data.get('token_counting_method')!r}"
        )

    skills = token_data.get("skill_files")
    if not isinstance(skills, dict):
        raise RuntimeError("token measurement is missing skill_files")
    required_skill_metrics = {
        "total_tokens",
        "avg_tokens_per_skill",
        "over_500_count",
        "discovery_metadata",
        "supporting_files",
        "all_packages_tokens_upper_bound",
    }
    missing_skill_metrics = sorted(required_skill_metrics - set(skills))
    if missing_skill_metrics:
        raise RuntimeError(
            "token measurement is missing metrics: " + ", ".join(missing_skill_metrics)
        )
    discovery = skills["discovery_metadata"]
    supporting = skills["supporting_files"]
    governance = token_data.get("repository_governance")
    if not isinstance(discovery, dict) or "tokens" not in discovery:
        raise RuntimeError("token measurement is missing discovery metadata tokens")
    if not isinstance(supporting, dict) or "tokens" not in supporting:
        raise RuntimeError("token measurement is missing supporting-file tokens")
    if not isinstance(governance, dict) or "tokens" not in governance:
        raise RuntimeError("token measurement is missing repository governance tokens")

    total_tokens = skills["total_tokens"]
    avg_tokens = skills["avg_tokens_per_skill"]
    over_500 = skills["over_500_count"]
    discovery_tokens = discovery["tokens"]
    supporting_tokens = supporting["tokens"]
    all_packages_tokens = skills["all_packages_tokens_upper_bound"]
    governance_tokens = governance["tokens"]

    # Cross-references fail closed: a broken checker is not a passing result.
    result = subprocess.run(
        [sys.executable, str(ANALYSIS_DIR / "check_cross_references.py"), "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "cross-reference checker failed")
    cross_ref_data = json.loads(result.stdout)
    summary = cross_ref_data.get("summary")
    if not isinstance(summary, dict) or "total_broken_references" not in summary:
        raise RuntimeError("cross-reference checker returned incomplete JSON")
    broken_refs = summary["total_broken_references"]

    return {
        **identity,
        "quality_pass_rate": pass_rate,
        "quality_passing": passing_skills,
        "quality_total": total_skills,
        "quality_failing_skills": failing_skills,
        "total_tokens": total_tokens,
        "avg_tokens": avg_tokens,
        "max_skill_body_tokens": max(
            (skill.get("body_tokens", 0) for skill in skills.get("skills", [])),
            default=0,
        ),
        "discovery_metadata_tokens": discovery_tokens,
        "supporting_tokens": supporting_tokens,
        "all_packages_tokens_upper_bound": all_packages_tokens,
        "repository_governance_tokens": governance_tokens,
        "everything_tokens_upper_bound": all_packages_tokens + governance_tokens,
        "over_500": over_500,
        "broken_refs": broken_refs,
    }


def detect_regressions(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    """Detect regressions between baseline and current."""
    validate_measurement_pair(baseline, current)
    regressions = []
    warnings = []

    # Quality regressions. Compare failing count as well as pass rate so adding
    # one failing Skill (17/17 -> 17/18) cannot look healthy.
    quality_keys = {"quality_pass_rate", "quality_passing", "quality_total"}
    if quality_keys <= baseline.keys() and quality_keys <= current.keys():
        baseline_passing = baseline["quality_passing"]
        current_passing = current["quality_passing"]
        baseline_failing = baseline["quality_total"] - baseline_passing
        current_failing = current["quality_total"] - current_passing
        new_failing = current_failing - baseline_failing
        pass_rate_drop = baseline["quality_pass_rate"] - current["quality_pass_rate"]

        if new_failing > 0 or pass_rate_drop > 0:
            skills_regressed = max(new_failing, baseline_passing - current_passing, 1)
            severity = (
                "critical"
                if skills_regressed >= THRESHOLDS["quality_drop_critical"]
                else "warning"
            )

            regression = {
                "type": "quality_regression",
                "severity": severity,
                "message": (
                    f"quality dropped to {current['quality_passing']}/"
                    f"{current['quality_total']} passing "
                    f"({current['quality_pass_rate']:.1f}%)"
                ),
                "baseline_passing": baseline_passing,
                "current_passing": current_passing,
                "baseline_total": baseline["quality_total"],
                "current_total": current["quality_total"],
                "skills_affected": skills_regressed,
            }

            if severity == "critical":
                regressions.append(regression)
            else:
                warnings.append(regression)

    # Token inflation across both distributable packages and repository-only
    # governance. Discovery/supporting metrics are retained for diagnosis; the
    # all-package ceiling prevents moving required content into references from
    # being reported as a saving.
    token_surfaces = (
        ("total_tokens", "token_inflation", "All SKILL.md files"),
        ("avg_tokens", "average_skill_token_inflation", "Average SKILL.md"),
        (
            "max_skill_body_tokens",
            "max_skill_body_token_inflation",
            "Largest Skill body",
        ),
        (
            "all_packages_tokens_upper_bound",
            "package_token_inflation",
            "All Agent Skills package text",
        ),
        (
            "repository_governance_tokens",
            "governance_token_inflation",
            "Repository AGENTS.md",
        ),
    )
    for metric, regression_type, label in token_surfaces:
        if metric not in baseline or metric not in current:
            continue
        baseline_tokens = baseline[metric]
        current_tokens = current[metric]
        token_increase = current_tokens - baseline_tokens
        token_increase_pct = (token_increase / baseline_tokens * 100) if baseline_tokens > 0 else 0

        if token_increase_pct > THRESHOLDS["token_increase_warning"]:
            severity = (
                "critical"
                if token_increase_pct >= THRESHOLDS["token_increase_critical"]
                else "warning"
            )

            regression = {
                "type": regression_type,
                "severity": severity,
                "message": f"{label} increased by {token_increase_pct:.1f}% "
                          f"({token_increase:+,} tokens)",
                "metric": metric,
                "label": label,
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
            severity = (
                "critical"
                if current_over >= THRESHOLDS["skill_length_critical"]
                else "warning"
            )
            finding = {
                "type": "skill_length_regression",
                "severity": severity,
                "message": f"{new_over} new skills exceeded 500 lines",
                "baseline_over": baseline_over,
                "current_over": current_over,
                "new_over": new_over,
            }
            if severity == "critical":
                regressions.append(finding)
            else:
                warnings.append(finding)

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
        print(f"Baseline: {BASELINE_FILE.relative_to(REPO_ROOT)}")
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
            elif reg['type'].endswith('token_inflation'):
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

    for metric, label in (
        ("all_packages_tokens_upper_bound", "Packages"),
        ("repository_governance_tokens", "Governance"),
        ("everything_tokens_upper_bound", "Everything"),
    ):
        print(f"  {label + ':':14} {current[metric]:,} tokens")
        if metric in baseline:
            delta = current[metric] - baseline[metric]
            print(f"                vs {baseline[metric]:,} baseline ({delta:+,})")

    print(f"  Discovery:     {current['discovery_metadata_tokens']:,} tokens")
    print(f"  Supporting:    {current['supporting_tokens']:,} tokens")

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
        help="Current-format historical audit filename (default: operational baseline JSON)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable report",
    )
    args = parser.parse_args()

    # The shared JSON is the default source of truth. An explicit audit file is
    # supported only for intentional historical comparison.
    try:
        if args.baseline:
            baseline_file = AUDITS_DIR / args.baseline
            if not baseline_file.exists():
                raise RuntimeError(f"baseline file not found: {baseline_file}")
            baseline = parse_audit_report(baseline_file)
            missing = sorted(REQUIRED_HISTORICAL_BASELINE_FIELDS - baseline.keys())
            if missing:
                raise RuntimeError(
                    f"baseline {baseline_file} is missing metrics: {', '.join(missing)}"
                )
        else:
            baseline = _file_baseline()
            baseline_file = None

        current = collect_current_metrics()
    except (OSError, KeyError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    # Detect regressions
    regressions = detect_regressions(baseline, current)

    # Report
    print_regression_report(baseline_file, baseline, current, regressions, args.json)

    # Exit code
    sys.exit(1 if regressions["has_regressions"] else 0)


if __name__ == "__main__":
    main()
