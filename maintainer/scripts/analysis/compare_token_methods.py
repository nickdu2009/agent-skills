#!/usr/bin/env python3
"""Compare character-based token estimates vs actual tiktoken counts.

Usage:
    python3 maintainer/scripts/analysis/compare_token_methods.py \\
        --estimate metrics_char_estimate.json \\
        --actual metrics_actual_tokens.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def compare_metrics(estimate: dict, actual: dict) -> None:
    """Compare and report differences between estimation methods."""
    print("=" * 80)
    print("Token Counting Method Comparison")
    print("=" * 80)
    print()

    # Governance templates
    print("Governance Templates:")
    est_gov = estimate["governance_templates"]
    act_gov = actual["governance_templates"]

    est_total = est_gov["total_chars"] // 4  # Character-based estimate
    act_total = act_gov["total_tokens"]
    accuracy = (est_total / act_total * 100) if act_total > 0 else 0
    error = abs(est_total - act_total)

    print(f"  Character estimate: {est_total:,} tokens ({est_gov['total_chars']:,} chars ÷ 4)")
    print(f"  Actual (tiktoken):  {act_total:,} tokens")
    print(f"  Accuracy: {accuracy:.1f}%  |  Error: {error:,} tokens ({error/act_total*100:.1f}%)")
    print()

    # Generated governance
    print("Generated Governance:")
    est_gen = estimate["generated_governance"]
    act_gen = actual["generated_governance"]

    est_total = est_gen["total_chars"] // 4
    act_total = act_gen["total_tokens"]
    accuracy = (est_total / act_total * 100) if act_total > 0 else 0
    error = abs(est_total - act_total)

    print(f"  Character estimate: {est_total:,} tokens ({est_gen['total_chars']:,} chars ÷ 4)")
    print(f"  Actual (tiktoken):  {act_total:,} tokens")
    print(f"  Accuracy: {accuracy:.1f}%  |  Error: {error:,} tokens ({error/act_total*100:.1f}%)")
    print()

    # Skill files
    print("Skill Files:")
    est_skills = estimate["skill_files"]
    act_skills = actual["skill_files"]

    est_total = est_skills["total_chars"] // 4
    act_total = act_skills["total_tokens"]
    accuracy = (est_total / act_total * 100) if act_total > 0 else 0
    error = abs(est_total - act_total)

    print(f"  Character estimate: {est_total:,} tokens ({est_skills['total_chars']:,} chars ÷ 4)")
    print(f"  Actual (tiktoken):  {act_total:,} tokens")
    print(f"  Accuracy: {accuracy:.1f}%  |  Error: {error:,} tokens ({error/act_total*100:.1f}%)")
    print()

    est_avg = est_skills["total_chars"] // 4 / est_skills["count"]
    act_avg = act_skills["avg_tokens_per_skill"]
    print(f"  Average per skill:")
    print(f"    Character estimate: {est_avg:,.0f} tokens")
    print(f"    Actual (tiktoken):  {act_avg:,.0f} tokens")
    print(f"    Accuracy: {est_avg/act_avg*100:.1f}%")
    print()

    # Top 5 skills with largest estimation errors
    print("Skills with Largest Estimation Errors:")
    skill_errors = []
    for est_skill in est_skills["skills"]:
        skill_name = est_skill["skill_name"]
        act_skill = next(
            (s for s in act_skills["skills"] if s["skill_name"] == skill_name),
            None
        )
        if act_skill and "body_tokens" in act_skill:
            est_tokens = est_skill["body_chars"] // 4
            act_tokens = act_skill["body_tokens"]
            error = abs(est_tokens - act_tokens)
            error_pct = error / act_tokens * 100 if act_tokens > 0 else 0
            skill_errors.append({
                "name": skill_name,
                "est": est_tokens,
                "act": act_tokens,
                "error": error,
                "error_pct": error_pct,
            })

    skill_errors.sort(key=lambda x: x["error_pct"], reverse=True)
    for skill in skill_errors[:5]:
        print(f"  {skill['name']:30s}: est {skill['est']:4d}, act {skill['act']:4d}, "
              f"error {skill['error']:4d} ({skill['error_pct']:5.1f}%)")
    print()

    # Summary
    print("=" * 80)
    print("Summary:")
    print()

    # Overall accuracy
    total_est = (est_gov["total_chars"] + est_gen["total_chars"] + est_skills["total_chars"]) // 4
    total_act = act_gov["total_tokens"] + act_gen["total_tokens"] + act_skills["total_tokens"]
    overall_accuracy = (total_est / total_act * 100) if total_act > 0 else 0
    overall_error = abs(total_est - total_act)

    print(f"  Overall character-based estimate accuracy: {overall_accuracy:.1f}%")
    print(f"  Total error: {overall_error:,} tokens ({overall_error/total_act*100:.1f}%)")
    print()

    # Character-to-token ratio (actual observed)
    total_chars = est_gov["total_chars"] + est_gen["total_chars"] + est_skills["total_chars"]
    actual_ratio = total_chars / total_act if total_act > 0 else 0
    print(f"  Observed character-to-token ratio: {actual_ratio:.2f} chars/token")
    print(f"  (vs assumed 4.0 chars/token in character-based estimate)")
    print()

    print("Recommendation:")
    if abs(overall_accuracy - 100) < 5:
        print("  ✓ Character-based estimate is accurate enough for rough sizing")
        print("  ✓ Use --actual-tokens for precise baselines and CI enforcement")
    elif overall_accuracy < 100:
        print("  ⚠ Character-based estimate UNDERESTIMATES token count")
        print("  ⚠ Use --actual-tokens for accurate measurements")
    else:
        print("  ⚠ Character-based estimate OVERESTIMATES token count")
        print("  ✓ Provides conservative upper bound")
        print("  ✓ Use --actual-tokens for precise baselines")
    print()


def main() -> int:
    """Run comparison."""
    parser = argparse.ArgumentParser(
        description="Compare character-based token estimates vs actual tiktoken counts"
    )
    parser.add_argument(
        "--estimate",
        required=True,
        help="Path to metrics JSON with character-based estimates",
    )
    parser.add_argument(
        "--actual",
        required=True,
        help="Path to metrics JSON with actual tiktoken counts",
    )
    args = parser.parse_args()

    estimate_path = Path(args.estimate)
    actual_path = Path(args.actual)

    if not estimate_path.exists():
        print(f"Error: Estimate file not found: {estimate_path}", file=sys.stderr)
        return 1

    if not actual_path.exists():
        print(f"Error: Actual metrics file not found: {actual_path}", file=sys.stderr)
        return 1

    estimate = json.loads(estimate_path.read_text())
    actual = json.loads(actual_path.read_text())

    compare_metrics(estimate, actual)
    return 0


if __name__ == "__main__":
    sys.exit(main())
