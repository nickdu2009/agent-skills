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
BASELINE_FILE = REPO_ROOT / "maintainer" / "data" / "token_efficiency_baseline.json"
EXPECTED_MEASUREMENT_IDENTITY: dict[str, str] = {
    "measurement_contract_version": "1.0",
    "token_counter": "tiktoken",
    "counter_version": "0.13.0",
    "tokenizer": "o200k_base",
}


class MeasurementIdentityError(RuntimeError):
    """The dashboard cannot compare measurements under the locked contract."""


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


def load_targets(path: Path | None = None) -> dict[str, Any]:
    path = BASELINE_FILE if path is None else path
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_measurement_identity(data, source=f"baseline {path}")
    return data


# Loaded by main() after argument parsing so an invalid baseline is reported as
# an operational exit (2), rather than an import-time traceback.
TARGETS: dict[str, Any] = {}


# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def status_for_count(count: int, critical_at: int) -> tuple[str, str]:
    """Map a zero-target count to the shared PASS/WARN/FAIL contract."""
    if count == 0:
        return "green", "PASS"
    if count < critical_at:
        return "yellow", "WARN"
    return "red", "FAIL"


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


def get_quality_status(use_color: bool = True) -> dict[str, Any]:
    """Get quality metrics status."""
    data = run_command([
        sys.executable,
        str(ANALYSIS_DIR / "check_skill_quality.py"),
        "--json",
    ])
    if not data:
        raise RuntimeError("quality checker returned no skills")

    total = len(data)
    passing = sum(1 for s in data if s.get("overall_pass", False))
    pass_rate = (passing / total * 100) if total > 0 else 0

    failing = total - passing
    health, status = status_for_count(failing, critical_at=3)

    return {
        "total": total,
        "passing": passing,
        "failing": failing,
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
    baseline_identity = validate_measurement_identity(TARGETS, source="baseline")
    current_identity = validate_measurement_identity(
        data,
        source="current token measurement",
    )
    if current_identity != baseline_identity:
        raise MeasurementIdentityError(
            "baseline and current measurement identities differ"
        )
    if data.get("token_counting_method") != current_identity["tokenizer"]:
        raise MeasurementIdentityError(
            "current token measurement token_counting_method mismatch: "
            f"expected {current_identity['tokenizer']!r}, "
            f"got {data.get('token_counting_method')!r}"
        )

    skills = data["skill_files"]
    governance = data["repository_governance"]
    total_tokens = skills["total_tokens"]
    avg_tokens = skills["avg_tokens_per_skill"]
    over_500 = skills["over_500_count"]
    max_body_tokens = max(
        (skill.get("body_tokens", 0) for skill in skills.get("skills", [])),
        default=0,
    )
    package_tokens = skills["all_packages_tokens_upper_bound"]
    governance_tokens = governance["tokens"]

    def surface(current: int | float, baseline_key: str) -> dict[str, float]:
        baseline = TARGETS[baseline_key]
        delta = current - baseline
        delta_pct = (delta / baseline * 100) if baseline > 0 else 0
        return {
            "current": current,
            "baseline": baseline,
            "delta": delta,
            "delta_pct": delta_pct,
        }

    surfaces = {
        "skill_main": surface(total_tokens, "total_skill_tokens"),
        "skill_average": surface(avg_tokens, "avg_tokens_per_skill"),
        "skill_max_body": surface(max_body_tokens, "max_skill_body_tokens"),
        "all_packages": surface(package_tokens, "all_packages_tokens_upper_bound"),
        "repository_governance": surface(
            governance_tokens,
            "repository_governance_tokens",
        ),
    }
    max_delta_pct = max(item["delta_pct"] for item in surfaces.values())

    if max_delta_pct <= 5:
        health = "green"
        status = "PASS"
    elif max_delta_pct < 10:
        health = "yellow"
        status = "WARN"
    else:
        health = "red"
        status = "FAIL"

    length_health, length_status = status_for_count(over_500, critical_at=2)
    health_rank = {"green": 0, "yellow": 1, "red": 2}
    if health_rank[length_health] > health_rank[health]:
        health, status = length_health, length_status

    return {
        **current_identity,
        "total_tokens": total_tokens,
        "avg_tokens": avg_tokens,
        "max_skill_body_tokens": max_body_tokens,
        "over_500": over_500,
        "baseline_total": TARGETS["total_skill_tokens"],
        "baseline_avg": TARGETS["avg_tokens_per_skill"],
        "delta_total": surfaces["skill_main"]["delta"],
        "delta_pct": surfaces["skill_main"]["delta_pct"],
        "discovery_metadata_tokens": skills["discovery_metadata"]["tokens"],
        "supporting_tokens": skills["supporting_files"]["tokens"],
        "all_packages_tokens_upper_bound": package_tokens,
        "repository_governance_tokens": governance_tokens,
        "everything_tokens_upper_bound": package_tokens + governance_tokens,
        "surfaces": surfaces,
        "health": health,
        "status": status,
    }


def get_cross_ref_status(use_color: bool = True) -> dict[str, Any]:
    """Get cross-reference integrity status."""
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
    broken = summary["total_broken_references"]

    health, status = status_for_count(broken, critical_at=4)

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
    max_body = tokens["surfaces"]["skill_max_body"]
    print(
        f"     Largest Skill body: {max_body['current']:,.0f} "
        f"({format_delta(max_body['delta_pct'], is_percentage=True)} from baseline)"
    )
    for label, key in (
        ("All package text", "all_packages"),
        ("Repository governance", "repository_governance"),
    ):
        metric = tokens["surfaces"][key]
        print(
            f"     {label}: {metric['current']:,.0f} "
            f"({format_delta(metric['delta_pct'], is_percentage=True)} from baseline)"
        )
    print(f"     Discovery metadata: {tokens['discovery_metadata_tokens']:,}")
    print(f"     Supporting files: {tokens['supporting_tokens']:,}")
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
    print(f"| Token surfaces | {tokens['status']} | {tokens['total_tokens']:,} SKILL.md ({delta_str}) | {tokens['baseline_total']:,} | {token_emoji} |")

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
    max_body = tokens["surfaces"]["skill_max_body"]
    print(
        f"- **Largest Skill body:** {max_body['current']:,.0f} "
        f"(baseline: {max_body['baseline']:,.0f}, "
        f"{format_delta(max_body['delta_pct'], is_percentage=True)})"
    )
    print(f"- **Discovery metadata:** {tokens['discovery_metadata_tokens']:,}")
    print(f"- **Supporting files:** {tokens['supporting_tokens']:,}")
    for label, key in (
        ("All package text", "all_packages"),
        ("Repository governance", "repository_governance"),
    ):
        metric = tokens["surfaces"][key]
        print(
            f"- **{label}:** {metric['current']:,.0f} "
            f"(baseline: {metric['baseline']:,.0f}, "
            f"{format_delta(metric['delta_pct'], is_percentage=True)})"
        )
    print(f"- **Everything upper bound:** {tokens['everything_tokens_upper_bound']:,}")
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
    global TARGETS

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

    try:
        TARGETS = load_targets()
        quality = get_quality_status(use_color)
        tokens = get_token_status(use_color)
        cross_refs = get_cross_ref_status(use_color)
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

    # Output
    if args.json:
        data = {
            "measurement_identity": {
                field: tokens[field]
                for field in EXPECTED_MEASUREMENT_IDENTITY
            },
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
