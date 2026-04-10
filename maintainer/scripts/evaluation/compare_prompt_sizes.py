#!/usr/bin/env python3
"""Compare prompt sizes between verbose and compact modes.

This script measures the token reduction achieved by using the compact
skill_index.json instead of parsing full SKILL.md frontmatter.

Usage:
  python3 maintainer/scripts/evaluation/compare_prompt_sizes.py
  python3 maintainer/scripts/evaluation/compare_prompt_sizes.py --case bug-explicit
  python3 maintainer/scripts/evaluation/compare_prompt_sizes.py --detailed
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "maintainer" / "data"

sys.path.insert(0, str(DATA_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from trigger_test_data import ALL_TRIGGER_CASES, resolve_trigger_case
from run_trigger_tests import (
    extract_descriptions,
    load_skill_index,
    build_available_skills_block,
    build_eval_prompt,
    calculate_prompt_size,
)


def compare_modes(case_id: str | None = None, *, detailed: bool = False) -> None:
    """Compare verbose and compact mode prompt sizes."""

    # Select test case
    if case_id:
        cases = [resolve_trigger_case(case_id)]
    else:
        # Use a representative subset for quick comparison
        cases = [case for case in ALL_TRIGGER_CASES if case.id in [
            "bug-explicit", "refactor-explicit", "multi-file-uncertain",
            "unfamiliar-codebase", "parallel-investigation"
        ]]

    # Load descriptions using both methods
    verbose_descriptions = extract_descriptions()
    compact_descriptions = load_skill_index()

    # Build skills blocks
    verbose_block = build_available_skills_block(verbose_descriptions)
    compact_block = build_available_skills_block(compact_descriptions)

    # Note: In current implementation, both load from the same source
    # The real difference would be if verbose mode loaded full SKILL.md content
    # versus compact mode using only the index

    print("=" * 70)
    print("  Prompt Size Comparison: Verbose vs Compact Mode")
    print("=" * 70)
    print()

    # Calculate sizes for skills blocks
    verbose_block_size = calculate_prompt_size(verbose_block)
    compact_block_size = calculate_prompt_size(compact_block)

    print("Skills block (metadata only):")
    print(f"  Verbose: {verbose_block_size['characters']:6,} chars, ~{verbose_block_size['tokens_estimate']:5,} tokens")
    print(f"  Compact: {compact_block_size['characters']:6,} chars, ~{compact_block_size['tokens_estimate']:5,} tokens")

    if verbose_block_size['characters'] == compact_block_size['characters']:
        print("  Note: Both modes currently use skill_index.json (same size)")
    else:
        reduction_pct = ((verbose_block_size['tokens_estimate'] - compact_block_size['tokens_estimate']) /
                         verbose_block_size['tokens_estimate'] * 100)
        print(f"  Reduction: {reduction_pct:.1f}%")

    print()

    # Calculate sizes for full evaluation prompts
    if cases:
        print(f"Full evaluation prompts ({len(cases)} test cases):")
        print()

        total_verbose_tokens = 0
        total_compact_tokens = 0

        for case in cases:
            verbose_prompt = build_eval_prompt(case, verbose_block)
            compact_prompt = build_eval_prompt(case, compact_block)

            verbose_size = calculate_prompt_size(verbose_prompt)
            compact_size = calculate_prompt_size(compact_prompt)

            total_verbose_tokens += verbose_size['tokens_estimate']
            total_compact_tokens += compact_size['tokens_estimate']

            if detailed:
                print(f"  [{case.id}]")
                print(f"    Verbose: {verbose_size['characters']:6,} chars, ~{verbose_size['tokens_estimate']:5,} tokens")
                print(f"    Compact: {compact_size['characters']:6,} chars, ~{compact_size['tokens_estimate']:5,} tokens")
                if verbose_size['tokens_estimate'] != compact_size['tokens_estimate']:
                    reduction = verbose_size['tokens_estimate'] - compact_size['tokens_estimate']
                    reduction_pct = (reduction / verbose_size['tokens_estimate'] * 100)
                    print(f"    Saved: {reduction:,} tokens ({reduction_pct:.1f}%)")
                print()

        avg_verbose = total_verbose_tokens // len(cases) if cases else 0
        avg_compact = total_compact_tokens // len(cases) if cases else 0

        print(f"  Average per case:")
        print(f"    Verbose: ~{avg_verbose:,} tokens")
        print(f"    Compact: ~{avg_compact:,} tokens")

        if avg_verbose != avg_compact:
            avg_reduction = avg_verbose - avg_compact
            avg_reduction_pct = (avg_reduction / avg_verbose * 100)
            print(f"    Saved: ~{avg_reduction:,} tokens ({avg_reduction_pct:.1f}%)")

    print()
    print("=" * 70)
    print()
    print("Implementation notes:")
    print("  - Compact mode uses pre-generated skill_index.json")
    print("  - Verbose mode parses SKILL.md frontmatter on-demand")
    print("  - Current implementation: both modes use index (for consistency)")
    print("  - Size reduction comes from avoiding full SKILL.md parsing overhead")
    print("  - Index generation: maintainer/scripts/analysis/generate_skill_index.py")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare prompt sizes between verbose and compact modes."
    )
    parser.add_argument(
        "--case",
        help="Specific test case to compare (default: representative subset)",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show per-case breakdown",
    )
    args = parser.parse_args()

    compare_modes(args.case, detailed=args.detailed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
