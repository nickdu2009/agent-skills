#!/usr/bin/env python3
"""Run comprehensive quarterly token efficiency audit.

This script generates a comprehensive audit report comparing current metrics
to the baseline established in maintainer/data/token_efficiency_baseline.md.

Features:
- Quality pass rate measurement
- Token count tracking and trend analysis
- Template adoption verification
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
BASELINE_FILE = REPO_ROOT / "maintainer" / "data" / "token_efficiency_baseline.md"


# Baseline targets (from token_efficiency_baseline.md)
BASELINE_TARGETS = {
    "quality_pass_rate": 100,  # 18/18 skills passing (100%)
    "total_skill_tokens": 41783,  # Current baseline
    "avg_tokens_per_skill": 2321,  # Current baseline
    "max_skill_tokens": 5177,  # phase-plan-review
    "governance_tokens": 5912,  # Generated governance
    "template_tokens": 4556,  # Templates
    "cross_references_broken": 0,  # Target: 0 broken refs
    "skills_over_500_lines": 0,  # Target: 0 skills
}

THRESHOLDS = {
    "quality_drop_critical": 5,  # % drop in quality pass rate
    "token_increase_warning": 5,  # % increase in token count
    "token_increase_critical": 10,  # % increase triggers failure
}


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
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}", file=sys.stderr)
        print(f"Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from command: {' '.join(cmd)}", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


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

    skills = token_data["skill_files"]
    governance = token_data["generated_governance"]
    templates = token_data["governance_templates"]

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
        "total_skill_tokens": total_skill_tokens,
        "avg_tokens_per_skill": avg_skill_tokens,
        "max_skill_tokens": max_skill_tokens,
        "max_skill_name": max_skill_name,
        "max_skill_body_tokens": max_skill_body_tokens,
        "skills_over_500_lines": skills["over_500_count"],
        "governance_tokens": governance["total_tokens"],
        "template_tokens": templates["total_tokens"],
        "total_prompt_surface": total_skill_tokens + governance["total_tokens"],
    }


def collect_cross_reference_metrics() -> dict[str, Any]:
    """Collect cross-reference integrity metrics."""
    try:
        result = subprocess.run(
            [sys.executable, str(ANALYSIS_DIR / "check_cross_references.py"), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,  # Don't fail if there are broken refs
        )

        if result.returncode != 0:
            # Parse output for broken reference count
            lines = result.stdout.strip().splitlines()
            for line in lines:
                if "broken reference" in line.lower():
                    # Try to extract count
                    import re
                    match = re.search(r'(\d+)\s+broken', line)
                    if match:
                        return {
                            "broken_references": int(match.group(1)),
                            "status": "has_issues",
                        }

            return {
                "broken_references": 0,  # Couldn't parse, assume none
                "status": "unknown",
            }

        # Success - parse JSON output
        data = json.loads(result.stdout)
        return {
            "broken_references": len(data.get("broken_references", [])),
            "status": "ok",
        }
    except Exception as e:
        print(f"Warning: Could not collect cross-reference metrics: {e}", file=sys.stderr)
        return {
            "broken_references": 0,
            "status": "error",
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
    quality_baseline = BASELINE_TARGETS["quality_pass_rate"]
    quality_current = quality["pass_rate"]
    quality_drop = quality_baseline - quality_current

    if quality_drop > THRESHOLDS["quality_drop_critical"]:
        regressions.append({
            "type": "quality",
            "severity": "critical",
            "message": f"Quality pass rate dropped by {quality_drop:.1f}% "
                      f"({quality_current:.1f}% vs {quality_baseline}% baseline)",
            "baseline": quality_baseline,
            "current": quality_current,
        })
    elif quality_drop > 0:
        warnings.append({
            "type": "quality",
            "severity": "warning",
            "message": f"Quality pass rate dropped by {quality_drop:.1f}%",
            "baseline": quality_baseline,
            "current": quality_current,
        })

    # Token increase check
    token_baseline = BASELINE_TARGETS["total_skill_tokens"]
    token_current = tokens["total_skill_tokens"]
    token_increase_pct = ((token_current - token_baseline) / token_baseline * 100) if token_baseline > 0 else 0

    if token_increase_pct > THRESHOLDS["token_increase_critical"]:
        regressions.append({
            "type": "token_inflation",
            "severity": "critical",
            "message": f"Total skill tokens increased by {token_increase_pct:.1f}% "
                      f"({token_current} vs {token_baseline} baseline)",
            "baseline": token_baseline,
            "current": token_current,
        })
    elif token_increase_pct > THRESHOLDS["token_increase_warning"]:
        warnings.append({
            "type": "token_inflation",
            "severity": "warning",
            "message": f"Total skill tokens increased by {token_increase_pct:.1f}%",
            "baseline": token_baseline,
            "current": token_current,
        })

    # Cross-reference integrity check
    broken_refs_baseline = BASELINE_TARGETS["cross_references_broken"]
    broken_refs_current = cross_refs["broken_references"]

    if broken_refs_current > broken_refs_baseline:
        regressions.append({
            "type": "cross_references",
            "severity": "critical" if broken_refs_current > 5 else "warning",
            "message": f"Found {broken_refs_current} broken cross-references "
                      f"(baseline: {broken_refs_baseline})",
            "baseline": broken_refs_baseline,
            "current": broken_refs_current,
        })

    # Skills over 500 lines check
    over_500_baseline = BASELINE_TARGETS["skills_over_500_lines"]
    over_500_current = tokens["skills_over_500_lines"]

    if over_500_current > over_500_baseline:
        warnings.append({
            "type": "skill_length",
            "severity": "warning",
            "message": f"{over_500_current} skills over 500 lines "
                      f"(baseline: {over_500_baseline})",
            "baseline": over_500_baseline,
            "current": over_500_current,
        })

    return {
        "has_regressions": len(regressions) > 0,
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
            f"- Consider applying token efficiency templates to reduce "
            f"{token_current - token_baseline} excess tokens"
        )

    # Template adoption
    recommendations.append(
        "- Continue applying chain aliases and contract templates for available savings"
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
        f"**Quarter:** {audit_data['metadata']['quarter']}  ",
        f"**Date:** {audit_data['metadata']['date']}  ",
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
        f"| Pass rate | {audit_data['metrics']['quality']['pass_rate']:.1f}% | {BASELINE_TARGETS['quality_pass_rate']}% | {'✓' if audit_data['metrics']['quality']['pass_rate'] >= BASELINE_TARGETS['quality_pass_rate'] - THRESHOLDS['quality_drop_critical'] else '✗'} |",
        f"| Passing skills | {audit_data['metrics']['quality']['passing_skills']}/{audit_data['metrics']['quality']['total_skills']} | 18/18 | {'✓' if audit_data['metrics']['quality']['pass_rate'] >= 90 else '✗'} |",
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
        f"| Total skill tokens | {audit_data['metrics']['tokens']['total_skill_tokens']:,} | {BASELINE_TARGETS['total_skill_tokens']:,} | {'✓' if audit_data['metrics']['tokens']['total_skill_tokens'] <= BASELINE_TARGETS['total_skill_tokens'] * 1.1 else '✗'} |",
        f"| Avg tokens/skill | {audit_data['metrics']['tokens']['avg_tokens_per_skill']:.0f} | {BASELINE_TARGETS['avg_tokens_per_skill']} | {'✓' if audit_data['metrics']['tokens']['avg_tokens_per_skill'] <= BASELINE_TARGETS['avg_tokens_per_skill'] * 1.1 else '✗'} |",
        f"| Max skill tokens | {audit_data['metrics']['tokens']['max_skill_body_tokens']:,} ({audit_data['metrics']['tokens']['max_skill_name']}) | {BASELINE_TARGETS['max_skill_tokens']:,} | {'✓' if audit_data['metrics']['tokens']['max_skill_body_tokens'] <= BASELINE_TARGETS['max_skill_tokens'] * 1.1 else '✗'} |",
        f"| Skills >500 lines | {audit_data['metrics']['tokens']['skills_over_500_lines']} | {BASELINE_TARGETS['skills_over_500_lines']} | {'✓' if audit_data['metrics']['tokens']['skills_over_500_lines'] == 0 else '✗'} |",
        f"| Governance tokens | {audit_data['metrics']['tokens']['governance_tokens']:,} | {BASELINE_TARGETS['governance_tokens']:,} | {'✓' if audit_data['metrics']['tokens']['governance_tokens'] <= BASELINE_TARGETS['governance_tokens'] * 1.1 else '✗'} |",
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

    # Collect metrics
    print("Collecting quality metrics...", file=sys.stderr)
    quality = collect_quality_metrics()

    print("Collecting token metrics...", file=sys.stderr)
    tokens = collect_token_metrics()

    print("Collecting cross-reference metrics...", file=sys.stderr)
    cross_refs = collect_cross_reference_metrics()

    print("Analyzing regressions...", file=sys.stderr)
    regressions = calculate_regressions(quality, tokens, cross_refs)

    print("Generating recommendations...", file=sys.stderr)
    recommendations = generate_recommendations(quality, tokens, cross_refs, regressions)

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
