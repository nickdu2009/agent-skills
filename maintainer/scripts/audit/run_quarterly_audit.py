#!/usr/bin/env python3
"""Run comprehensive quarterly token efficiency audit.

This script generates a comprehensive audit report comparing current metrics
to the baseline established in maintainer/data/token_efficiency_baseline.json.

Features:
- Quality pass rate measurement
- Token count tracking and trend analysis
- Progressive-loading and package-size tracking
- Cross-reference integrity check
- Regression detection and action recommendations

Usage:
    python3 maintainer/scripts/audit/run_quarterly_audit.py
    python3 maintainer/scripts/audit/run_quarterly_audit.py --output 2026-Q2-audit-report.md
    python3 maintainer/scripts/audit/run_quarterly_audit.py --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
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
    """The audit cannot compare measurements under the locked contract."""


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


def load_baseline_targets(path: Path | None = None) -> dict[str, Any]:
    """Load the single machine-readable portable package baseline."""
    path = BASELINE_FILE if path is None else path
    data = json.loads(path.read_text(encoding="utf-8"))
    identity = validate_measurement_identity(data, source=f"baseline {path}")
    return {
        **identity,
        "quality_pass_rate": data["quality_pass_rate"],
        "quality_passing": data["quality_passing"],
        "quality_total": data["quality_total"],
        "total_skill_tokens": data["total_skill_tokens"],
        "avg_tokens_per_skill": data["avg_tokens_per_skill"],
        "max_skill_tokens": data["max_skill_body_tokens"],
        "discovery_metadata_tokens": data["discovery_metadata_tokens"],
        "supporting_file_tokens": data["supporting_file_tokens"],
        "all_packages_tokens_upper_bound": data["all_packages_tokens_upper_bound"],
        "repository_governance_tokens": data["repository_governance_tokens"],
        "everything_tokens_upper_bound": data["everything_tokens_upper_bound"],
        "cross_references_broken": data["cross_references_broken"],
        "skills_over_500_lines": data["skills_over_500_lines"],
    }


# Loaded by main() after argument parsing so an invalid baseline is reported as
# an operational exit (2), rather than an import-time traceback.
BASELINE_TARGETS: dict[str, Any] = {}

THRESHOLDS = {
    "quality_failure_critical": 3,  # 3+ failing skills is critical
    "token_increase_warning": 5,  # % increase in token count
    "token_increase_critical": 10,  # % increase triggers failure
    "cross_ref_critical": 4,  # 4+ broken references is critical
    "skill_length_critical": 2,  # 2+ skills over 500 lines is critical
}


def token_surface_status(current: int | float, baseline: int | float) -> str:
    """Render the shared <=5% / <10% / >=10% token thresholds."""
    increase_pct = ((current - baseline) / baseline * 100) if baseline > 0 else 0
    if increase_pct >= THRESHOLDS["token_increase_critical"]:
        return "✗"
    if increase_pct > THRESHOLDS["token_increase_warning"]:
        return "⚠"
    return "✓"


def run_command(cmd: list[str], cwd: Path | None = None) -> dict[str, Any]:
    """Run a command and return parsed JSON output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}: {exc.stderr.strip()}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"command returned invalid JSON: {' '.join(cmd)}"
        ) from exc


def collect_quality_metrics() -> dict[str, Any]:
    """Collect quality metrics from check_skill_quality.py."""
    quality_data = run_command([
        sys.executable,
        str(ANALYSIS_DIR / "check_skill_quality.py"),
        "--json",
    ])

    total_skills = len(quality_data)
    passing_skills = sum(1 for skill in quality_data if skill.get("overall_pass", False))
    pass_rate = (passing_skills / total_skills * 100) if total_skills > 0 else 0

    # Collect failing skills with details
    failing_skills = []
    for skill in quality_data:
        if not skill.get("overall_pass", False):
            issues = []
            checks = skill.get("checks", {})
            if not checks.get("description_what_when", {}).get("pass"):
                issues.append("missing what/when")
            if not checks.get("third_person", {}).get("pass"):
                issues.append("not third-person")
            if not checks.get("body_length", {}).get("pass"):
                over_by = checks["body_length"].get("over_by", 0)
                issues.append(f"over 500 lines (+{over_by})")
            if not checks.get("shallow_structure", {}).get("pass"):
                issues.append("deep structure")

            failing_skills.append({
                "name": skill["skill_name"],
                "issues": issues,
            })

    return {
        "total_skills": total_skills,
        "passing_skills": passing_skills,
        "failing_skills": len(failing_skills),
        "pass_rate": pass_rate,
        "failing_skill_details": failing_skills,
    }


def collect_token_metrics() -> dict[str, Any]:
    """Collect token metrics from measure_prompt_surface.py."""
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
        raise MeasurementIdentityError(
            "current token measurement token_counting_method mismatch: "
            f"expected {identity['tokenizer']!r}, "
            f"got {token_data.get('token_counting_method')!r}"
        )

    skills = token_data["skill_files"]
    governance = token_data["repository_governance"]

    # Calculate skill token statistics
    skill_tokens = [s["tokens"] for s in skills["skills"]]
    total_skill_tokens = sum(skill_tokens)
    avg_skill_tokens = total_skill_tokens / len(skill_tokens) if skill_tokens else 0
    max_skill_tokens = max(skill_tokens) if skill_tokens else 0

    # Find skill with max tokens
    max_skill_name = ""
    max_skill_body_tokens = 0
    for s in skills["skills"]:
        if s.get("body_tokens", 0) > max_skill_body_tokens:
            max_skill_body_tokens = s["body_tokens"]
            max_skill_name = s["skill_name"]

    return {
        **identity,
        "total_skill_tokens": total_skill_tokens,
        "avg_tokens_per_skill": avg_skill_tokens,
        "max_skill_tokens": max_skill_tokens,
        "max_skill_name": max_skill_name,
        "max_skill_body_tokens": max_skill_body_tokens,
        "skills_over_500_lines": skills["over_500_count"],
        "supporting_tokens": skills["supporting_files"]["tokens"],
        "discovery_metadata_tokens": skills["discovery_metadata"]["tokens"],
        "all_packages_tokens_upper_bound": skills["all_packages_tokens_upper_bound"],
        "repository_governance_tokens": governance["tokens"],
        "everything_tokens_upper_bound": (
            skills["all_packages_tokens_upper_bound"] + governance["tokens"]
        ),
    }


def collect_cross_reference_metrics() -> dict[str, Any]:
    """Collect cross-reference integrity metrics."""
    result = subprocess.run(
        [sys.executable, str(ANALYSIS_DIR / "check_cross_references.py"), "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "cross-reference checker failed")
    data = json.loads(result.stdout)
    summary = data.get("summary")
    if not isinstance(summary, dict) or "total_broken_references" not in summary:
        raise RuntimeError("cross-reference checker returned incomplete JSON")
    return {
        "broken_references": summary["total_broken_references"],
        "status": "ok",
    }


def calculate_regressions(
    quality: dict[str, Any],
    tokens: dict[str, Any],
    cross_refs: dict[str, Any],
) -> dict[str, Any]:
    """Calculate regressions from baseline."""
    regressions = []
    warnings = []

    # Quality regression check
    baseline_failing = (
        BASELINE_TARGETS["quality_total"] - BASELINE_TARGETS["quality_passing"]
    )
    current_failing = quality["failing_skills"]
    if current_failing > baseline_failing:
        severity = (
            "critical"
            if current_failing >= THRESHOLDS["quality_failure_critical"]
            else "warning"
        )
        finding = {
            "type": "quality",
            "severity": severity,
            "message": (
                f"{current_failing} skills failing quality checks "
                f"({quality['pass_rate']:.1f}% pass rate)"
            ),
            "baseline": baseline_failing,
            "current": current_failing,
        }
        if severity == "critical":
            regressions.append(finding)
        else:
            warnings.append(finding)

    # Token increase checks cover activated main files, complete portable
    # packages, and repository-only governance.
    token_surfaces = (
        ("total_skill_tokens", "total_skill_tokens", "token_inflation", "All SKILL.md files"),
        (
            "avg_tokens_per_skill",
            "avg_tokens_per_skill",
            "average_skill_token_inflation",
            "Average SKILL.md",
        ),
        (
            "max_skill_body_tokens",
            "max_skill_tokens",
            "max_skill_body_token_inflation",
            "Largest Skill body",
        ),
        (
            "all_packages_tokens_upper_bound",
            "all_packages_tokens_upper_bound",
            "package_token_inflation",
            "All Agent Skills package text",
        ),
        (
            "repository_governance_tokens",
            "repository_governance_tokens",
            "governance_token_inflation",
            "Repository AGENTS.md",
        ),
    )
    for current_key, baseline_key, finding_type, label in token_surfaces:
        token_baseline = BASELINE_TARGETS[baseline_key]
        token_current = tokens[current_key]
        token_increase_pct = (
            (token_current - token_baseline) / token_baseline * 100
            if token_baseline > 0
            else 0
        )
        finding = {
            "type": finding_type,
            "message": f"{label} increased by {token_increase_pct:.1f}% "
                       f"({token_current} vs {token_baseline} baseline)",
            "baseline": token_baseline,
            "current": token_current,
        }
        if token_increase_pct >= THRESHOLDS["token_increase_critical"]:
            regressions.append({**finding, "severity": "critical"})
        elif token_increase_pct > THRESHOLDS["token_increase_warning"]:
            warnings.append({**finding, "severity": "warning"})

    # Cross-reference integrity check
    broken_refs_baseline = BASELINE_TARGETS["cross_references_broken"]
    broken_refs_current = cross_refs["broken_references"]

    if broken_refs_current > broken_refs_baseline:
        finding = {
            "type": "cross_references",
            "severity": (
                "critical"
                if broken_refs_current >= THRESHOLDS["cross_ref_critical"]
                else "warning"
            ),
            "message": f"Found {broken_refs_current} broken cross-references "
                      f"(baseline: {broken_refs_baseline})",
            "baseline": broken_refs_baseline,
            "current": broken_refs_current,
        }
        if finding["severity"] == "critical":
            regressions.append(finding)
        else:
            warnings.append(finding)

    # Skills over 500 lines check
    over_500_baseline = BASELINE_TARGETS["skills_over_500_lines"]
    over_500_current = tokens["skills_over_500_lines"]

    if over_500_current > over_500_baseline:
        severity = (
            "critical"
            if over_500_current >= THRESHOLDS["skill_length_critical"]
            else "warning"
        )
        finding = {
            "type": "skill_length",
            "severity": severity,
            "message": f"{over_500_current} skills over 500 lines "
                      f"(baseline: {over_500_baseline})",
            "baseline": over_500_baseline,
            "current": over_500_current,
        }
        if severity == "critical":
            regressions.append(finding)
        else:
            warnings.append(finding)

    return {
        "has_regressions": len(regressions) > 0,
        "has_warnings": len(warnings) > 0,
        "critical_count": len([r for r in regressions if r["severity"] == "critical"]),
        "warning_count": len(warnings),
        "regressions": regressions,
        "warnings": warnings,
    }


def generate_recommendations(
    quality: dict[str, Any],
    tokens: dict[str, Any],
    cross_refs: dict[str, Any],
    regressions: dict[str, Any],
) -> list[str]:
    """Generate actionable recommendations based on findings."""
    recommendations = []

    # Critical regressions need immediate action
    if regressions["has_regressions"]:
        recommendations.append("**IMMEDIATE ACTION REQUIRED:**")
        for reg in regressions["regressions"]:
            if reg["severity"] == "critical":
                if reg["type"] == "quality":
                    recommendations.append(
                        f"- Fix quality issues in {quality['failing_skills']} skills to restore "
                        f"{BASELINE_TARGETS['quality_pass_rate']}% pass rate"
                    )
                elif reg["type"] == "token_inflation":
                    recommendations.append(
                        "- Review recent skill changes for unnecessary verbosity or duplication"
                    )
                elif reg["type"] == "cross_references":
                    recommendations.append(
                        f"- Fix {cross_refs['broken_references']} broken cross-references immediately"
                    )

    # Quality improvements
    if quality["failing_skills"] > 0:
        recommendations.append(
            f"- Address quality issues in {quality['failing_skills']} skills "
            f"(see failing_skills section for details)"
        )

    # Token efficiency
    token_current = tokens["total_skill_tokens"]
    token_baseline = BASELINE_TARGETS["total_skill_tokens"]
    if token_current > token_baseline:
        recommendations.append(
            f"- Consider progressive disclosure and content deduplication to reduce "
            f"{token_current - token_baseline} excess tokens"
        )

    # Progressive-loading discipline
    recommendations.append(
        "- Keep required constraints in SKILL.md and move only genuinely optional material to supporting files"
    )

    # General maintenance
    if not recommendations:
        recommendations.append("- All metrics within target ranges. Continue quarterly monitoring.")

    return recommendations


def generate_markdown_report(audit_data: dict[str, Any]) -> str:
    """Generate markdown audit report."""
    lines = [
        f"# Token Efficiency Audit Report",
        "",
        f"**Quarter:** {audit_data['metadata']['quarter']}",
        f"**Date:** {audit_data['metadata']['date']}",
        "**Measurement contract version:** "
        f"`{audit_data['metadata']['measurement_contract_version']}`",
        f"**Token counter:** `{audit_data['metadata']['token_counter']}`",
        f"**Counter version:** `{audit_data['metadata']['counter_version']}`",
        f"**Tokenizer:** `{audit_data['metadata']['tokenizer']}`",
        f"**Status:** {audit_data['summary']['status']}",
        "",
        "## Executive Summary",
        "",
    ]

    # Overall status
    summary = audit_data["summary"]
    if summary["status"] == "PASS":
        lines.append("✓ All metrics within acceptable ranges.")
    elif summary["status"] == "WARN":
        lines.append(f"⚠ {summary['warning_count']} warnings detected.")
    else:
        lines.append(f"✗ {summary['critical_count']} critical regressions detected.")

    lines.extend([
        "",
        f"- Quality: {audit_data['metrics']['quality']['passing_skills']}/{audit_data['metrics']['quality']['total_skills']} skills passing ({audit_data['metrics']['quality']['pass_rate']:.1f}%)",
        f"- Tokens: {audit_data['metrics']['tokens']['total_skill_tokens']:,} total skill tokens",
        f"- Cross-refs: {audit_data['metrics']['cross_refs']['broken_references']} broken references",
        "",
    ])

    # Detailed metrics
    lines.extend([
        "## Metrics Detail",
        "",
        "### Quality Metrics",
        "",
        f"| Metric | Current | Baseline | Status |",
        f"|--------|---------|----------|--------|",
        f"| Pass rate | {audit_data['metrics']['quality']['pass_rate']:.1f}% | {BASELINE_TARGETS['quality_pass_rate']}% | {'✓' if audit_data['metrics']['quality']['failing_skills'] == 0 else '✗'} |",
        f"| Passing skills | {audit_data['metrics']['quality']['passing_skills']}/{audit_data['metrics']['quality']['total_skills']} | {BASELINE_TARGETS['quality_passing']}/{BASELINE_TARGETS['quality_total']} | {'✓' if audit_data['metrics']['quality']['pass_rate'] >= 90 else '✗'} |",
        f"| Failing skills | {audit_data['metrics']['quality']['failing_skills']} | 0 | {'✓' if audit_data['metrics']['quality']['failing_skills'] == 0 else '✗'} |",
        "",
    ])

    # Failing skills details
    if audit_data['metrics']['quality']['failing_skills'] > 0:
        lines.extend([
            "#### Failing Skills",
            "",
        ])
        for skill in audit_data['metrics']['quality']['failing_skill_details']:
            lines.append(f"- **{skill['name']}**: {', '.join(skill['issues'])}")
        lines.append("")

    lines.extend([
        "### Token Metrics",
        "",
        f"| Metric | Current | Baseline | Status |",
        f"|--------|---------|----------|--------|",
        f"| Total skill tokens | {audit_data['metrics']['tokens']['total_skill_tokens']:,} | {BASELINE_TARGETS['total_skill_tokens']:,} | {token_surface_status(audit_data['metrics']['tokens']['total_skill_tokens'], BASELINE_TARGETS['total_skill_tokens'])} |",
        f"| Avg tokens/skill | {audit_data['metrics']['tokens']['avg_tokens_per_skill']:.0f} | {BASELINE_TARGETS['avg_tokens_per_skill']} | {token_surface_status(audit_data['metrics']['tokens']['avg_tokens_per_skill'], BASELINE_TARGETS['avg_tokens_per_skill'])} |",
        f"| Max skill tokens | {audit_data['metrics']['tokens']['max_skill_body_tokens']:,} ({audit_data['metrics']['tokens']['max_skill_name']}) | {BASELINE_TARGETS['max_skill_tokens']:,} | {token_surface_status(audit_data['metrics']['tokens']['max_skill_body_tokens'], BASELINE_TARGETS['max_skill_tokens'])} |",
        f"| Skills >500 lines | {audit_data['metrics']['tokens']['skills_over_500_lines']} | {BASELINE_TARGETS['skills_over_500_lines']} | {'✓' if audit_data['metrics']['tokens']['skills_over_500_lines'] == 0 else '✗'} |",
        f"| Discovery metadata tokens | {audit_data['metrics']['tokens']['discovery_metadata_tokens']:,} | {BASELINE_TARGETS['discovery_metadata_tokens']:,} | — |",
        f"| Supporting-file tokens | {audit_data['metrics']['tokens']['supporting_tokens']:,} | {BASELINE_TARGETS['supporting_file_tokens']:,} | — |",
        f"| All-package upper bound | {audit_data['metrics']['tokens']['all_packages_tokens_upper_bound']:,} | {BASELINE_TARGETS['all_packages_tokens_upper_bound']:,} | {token_surface_status(audit_data['metrics']['tokens']['all_packages_tokens_upper_bound'], BASELINE_TARGETS['all_packages_tokens_upper_bound'])} |",
        f"| Repository governance | {audit_data['metrics']['tokens']['repository_governance_tokens']:,} | {BASELINE_TARGETS['repository_governance_tokens']:,} | {token_surface_status(audit_data['metrics']['tokens']['repository_governance_tokens'], BASELINE_TARGETS['repository_governance_tokens'])} |",
        f"| Everything upper bound | {audit_data['metrics']['tokens']['everything_tokens_upper_bound']:,} | {BASELINE_TARGETS['everything_tokens_upper_bound']:,} | — |",
        "",
        "### Cross-Reference Integrity",
        "",
        f"| Metric | Current | Baseline | Status |",
        f"|--------|---------|----------|--------|",
        f"| Broken references | {audit_data['metrics']['cross_refs']['broken_references']} | {BASELINE_TARGETS['cross_references_broken']} | {'✓' if audit_data['metrics']['cross_refs']['broken_references'] == 0 else '✗'} |",
        "",
    ])

    # Regressions
    if audit_data['regressions']['has_regressions']:
        lines.extend([
            "## Regressions Detected",
            "",
        ])
        for reg in audit_data['regressions']['regressions']:
            icon = "🔴" if reg['severity'] == "critical" else "⚠️"
            lines.append(f"### {icon} {reg['type'].replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"**Severity:** {reg['severity']}")
            lines.append(f"**Message:** {reg['message']}")
            lines.append("")

    # Warnings
    if audit_data['regressions']['warning_count'] > 0:
        lines.extend([
            "## Warnings",
            "",
        ])
        for warn in audit_data['regressions']['warnings']:
            lines.append(f"- ⚠️ {warn['message']}")
        lines.append("")

    # Recommendations
    lines.extend([
        "## Recommendations",
        "",
    ])
    lines.extend(audit_data['recommendations'])
    lines.append("")

    # Footer
    lines.extend([
        "---",
        "",
        "**Audit completed:** " + audit_data['metadata']['date'],
        "**Scripts used:**",
        "- `maintainer/scripts/analysis/check_skill_quality.py`",
        "- `maintainer/scripts/analysis/measure_prompt_surface.py`",
        "- `maintainer/scripts/analysis/check_cross_references.py`",
        "- `maintainer/scripts/audit/run_quarterly_audit.py`",
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    """Run quarterly audit and generate report."""
    global BASELINE_TARGETS

    parser = argparse.ArgumentParser(
        description="Run comprehensive quarterly token efficiency audit"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output filename (default: YYYY-QN-audit-report.md based on current date)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON data instead of markdown report",
    )
    parser.add_argument(
        "--quarter",
        type=str,
        help="Quarter identifier (e.g., 2026-Q2). Auto-detected if not provided.",
    )
    args = parser.parse_args()

    # Determine quarter
    if args.quarter:
        quarter = args.quarter
    else:
        today = datetime.now()
        q = (today.month - 1) // 3 + 1
        quarter = f"{today.year}-Q{q}"

    try:
        BASELINE_TARGETS = load_baseline_targets()
        baseline_identity = {
            key: BASELINE_TARGETS[key]
            for key in EXPECTED_MEASUREMENT_IDENTITY
        }

        print("Collecting quality metrics...", file=sys.stderr)
        quality = collect_quality_metrics()

        print("Collecting token metrics...", file=sys.stderr)
        tokens = collect_token_metrics()
        current_identity = validate_measurement_identity(
            tokens,
            source="current token metrics",
        )
        if current_identity != baseline_identity:
            raise MeasurementIdentityError(
                "baseline and current measurement identities differ"
            )

        print("Collecting cross-reference metrics...", file=sys.stderr)
        cross_refs = collect_cross_reference_metrics()

        print("Analyzing regressions...", file=sys.stderr)
        regressions = calculate_regressions(quality, tokens, cross_refs)

        print("Generating recommendations...", file=sys.stderr)
        recommendations = generate_recommendations(
            quality, tokens, cross_refs, regressions
        )
    except (
        KeyError,
        OSError,
        UnicodeDecodeError,
        ValueError,
        RuntimeError,
        json.JSONDecodeError,
    ) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    # Determine overall status
    if regressions["critical_count"] > 0:
        status = "FAIL"
    elif regressions["warning_count"] > 0:
        status = "WARN"
    else:
        status = "PASS"

    # Assemble audit data
    audit_data = {
        "metadata": {
            "quarter": quarter,
            "date": datetime.now().strftime("%Y-%m-%d"),
            **baseline_identity,
            "baseline_file": str(BASELINE_FILE.relative_to(REPO_ROOT)),
        },
        "summary": {
            "status": status,
            "critical_count": regressions["critical_count"],
            "warning_count": regressions["warning_count"],
        },
        "metrics": {
            "quality": quality,
            "tokens": tokens,
            "cross_refs": cross_refs,
        },
        "regressions": regressions,
        "recommendations": recommendations,
    }

    # Output
    if args.json:
        print(json.dumps(audit_data, indent=2))
    else:
        report = generate_markdown_report(audit_data)

        if args.output:
            output_file = AUDITS_DIR / args.output
        else:
            output_file = AUDITS_DIR / f"{quarter}-audit-report.md"

        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write report
        output_file.write_text(report, encoding="utf-8")
        print(f"Audit report written to: {output_file.relative_to(REPO_ROOT)}", file=sys.stderr)

        # Print summary to stdout
        print(report)

    # Exit with appropriate code
    sys.exit(1 if regressions["critical_count"] > 0 else 0)


if __name__ == "__main__":
    main()
