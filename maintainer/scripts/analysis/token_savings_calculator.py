#!/usr/bin/env python3
"""Calculate token savings between before/after versions of files.

This script uses tiktoken for accurate token counting and computes
the difference and percentage reduction between two versions.

Usage:
    python3 maintainer/scripts/analysis/token_savings_calculator.py \
        --before file_before.md --after file_after.md

    python3 maintainer/scripts/analysis/token_savings_calculator.py \
        --before-text "Long verbose text..." --after-text "Short text"

    python3 maintainer/scripts/analysis/token_savings_calculator.py \
        --before-dir skills_before/ --after-dir skills_after/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import tiktoken
except ImportError:
    print("Error: tiktoken is required. Install with: pip install tiktoken", file=sys.stderr)
    sys.exit(1)


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens in text using tiktoken."""
    encoder = tiktoken.get_encoding(encoding_name)
    return len(encoder.encode(text))


def calculate_savings(before: str, after: str, encoding_name: str = "cl100k_base") -> dict[str, Any]:
    """Calculate token savings between before and after text."""
    before_tokens = count_tokens(before, encoding_name)
    after_tokens = count_tokens(after, encoding_name)

    savings = before_tokens - after_tokens
    percent_reduction = (savings / before_tokens * 100) if before_tokens > 0 else 0

    return {
        "before_tokens": before_tokens,
        "after_tokens": after_tokens,
        "savings": savings,
        "percent_reduction": percent_reduction,
        "before_chars": len(before),
        "after_chars": len(after),
        "char_savings": len(before) - len(after),
    }


def compare_files(before_file: Path, after_file: Path, encoding_name: str = "cl100k_base") -> dict[str, Any]:
    """Compare two files and return token savings."""
    if not before_file.exists():
        print(f"Error: Before file not found: {before_file}", file=sys.stderr)
        sys.exit(1)

    if not after_file.exists():
        print(f"Error: After file not found: {after_file}", file=sys.stderr)
        sys.exit(1)

    before_text = before_file.read_text(encoding="utf-8")
    after_text = after_file.read_text(encoding="utf-8")

    results = calculate_savings(before_text, after_text, encoding_name)
    results["before_file"] = str(before_file)
    results["after_file"] = str(after_file)

    return results


def compare_directories(before_dir: Path, after_dir: Path, pattern: str = "**/*.md", encoding_name: str = "cl100k_base") -> dict[str, Any]:
    """Compare all matching files in two directories."""
    if not before_dir.exists():
        print(f"Error: Before directory not found: {before_dir}", file=sys.stderr)
        sys.exit(1)

    if not after_dir.exists():
        print(f"Error: After directory not found: {after_dir}", file=sys.stderr)
        sys.exit(1)

    before_files = sorted(before_dir.glob(pattern))
    results = []
    total_before = 0
    total_after = 0

    for before_file in before_files:
        relative_path = before_file.relative_to(before_dir)
        after_file = after_dir / relative_path

        if not after_file.exists():
            print(f"Warning: Skipping {relative_path} (not found in after directory)", file=sys.stderr)
            continue

        before_text = before_file.read_text(encoding="utf-8")
        after_text = after_file.read_text(encoding="utf-8")

        file_results = calculate_savings(before_text, after_text, encoding_name)
        file_results["file"] = str(relative_path)
        results.append(file_results)

        total_before += file_results["before_tokens"]
        total_after += file_results["after_tokens"]

    total_savings = total_before - total_after
    total_percent = (total_savings / total_before * 100) if total_before > 0 else 0

    return {
        "files": results,
        "total_before_tokens": total_before,
        "total_after_tokens": total_after,
        "total_savings": total_savings,
        "total_percent_reduction": total_percent,
        "file_count": len(results),
    }


def format_results(results: dict[str, Any]) -> str:
    """Format results for human-readable output."""
    if "file" in results or "before_file" in results:
        # Single file results
        output = []
        output.append("=" * 80)
        output.append("Token Savings Calculation")
        output.append("=" * 80)
        output.append("")

        if "before_file" in results:
            output.append(f"Before: {results['before_file']}")
            output.append(f"After:  {results['after_file']}")

        output.append("")
        output.append(f"Before: {results['before_tokens']:,} tokens ({results['before_chars']:,} chars)")
        output.append(f"After:  {results['after_tokens']:,} tokens ({results['after_chars']:,} chars)")
        output.append("")
        output.append(f"Savings: {results['savings']:,} tokens ({results['percent_reduction']:.1f}% reduction)")
        output.append(f"         {results['char_savings']:,} characters")
        output.append("")

        return "\n".join(output)

    elif "files" in results:
        # Directory comparison results
        output = []
        output.append("=" * 80)
        output.append("Token Savings Calculation (Directory Comparison)")
        output.append("=" * 80)
        output.append("")
        output.append(f"Files compared: {results['file_count']}")
        output.append("")
        output.append(f"Total before: {results['total_before_tokens']:,} tokens")
        output.append(f"Total after:  {results['total_after_tokens']:,} tokens")
        output.append("")
        output.append(f"Total savings: {results['total_savings']:,} tokens ({results['total_percent_reduction']:.1f}% reduction)")
        output.append("")
        output.append("Per-file breakdown:")
        output.append("")

        # Sort by savings (largest first)
        sorted_files = sorted(results["files"], key=lambda x: x["savings"], reverse=True)

        for file_result in sorted_files:
            savings_sign = "+" if file_result["savings"] < 0 else "-"
            output.append(f"  {file_result['file']}")
            output.append(f"    {file_result['before_tokens']:,} → {file_result['after_tokens']:,} tokens "
                         f"({savings_sign}{abs(file_result['savings']):,} tokens, {file_result['percent_reduction']:.1f}%)")

        output.append("")
        return "\n".join(output)

    else:
        # Text comparison results
        output = []
        output.append("=" * 80)
        output.append("Token Savings Calculation")
        output.append("=" * 80)
        output.append("")
        output.append(f"Before: {results['before_tokens']:,} tokens ({results['before_chars']:,} chars)")
        output.append(f"After:  {results['after_tokens']:,} tokens ({results['after_chars']:,} chars)")
        output.append("")
        output.append(f"Savings: {results['savings']:,} tokens ({results['percent_reduction']:.1f}% reduction)")
        output.append(f"         {results['char_savings']:,} characters")
        output.append("")

        return "\n".join(output)


def main() -> None:
    """Run token savings calculator."""
    parser = argparse.ArgumentParser(
        description="Calculate token savings between before/after versions"
    )

    parser.add_argument(
        "--before",
        type=str,
        help="Before file path",
    )
    parser.add_argument(
        "--after",
        type=str,
        help="After file path",
    )
    parser.add_argument(
        "--before-text",
        type=str,
        help="Before text (alternative to --before file)",
    )
    parser.add_argument(
        "--after-text",
        type=str,
        help="After text (alternative to --after file)",
    )
    parser.add_argument(
        "--before-dir",
        type=str,
        help="Before directory (for bulk comparison)",
    )
    parser.add_argument(
        "--after-dir",
        type=str,
        help="After directory (for bulk comparison)",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="**/*.md",
        help="File pattern for directory comparison (default: **/*.md)",
    )
    parser.add_argument(
        "--encoding",
        type=str,
        default="cl100k_base",
        help="Tiktoken encoding to use (default: cl100k_base)",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.before_dir and args.after_dir:
        # Directory comparison
        results = compare_directories(
            Path(args.before_dir),
            Path(args.after_dir),
            args.pattern,
            args.encoding,
        )
    elif args.before and args.after:
        # File comparison
        results = compare_files(
            Path(args.before),
            Path(args.after),
            args.encoding,
        )
    elif args.before_text and args.after_text:
        # Text comparison
        results = calculate_savings(args.before_text, args.after_text, args.encoding)
    else:
        parser.print_help()
        print("\nError: Must specify either:", file=sys.stderr)
        print("  - --before and --after (file comparison)", file=sys.stderr)
        print("  - --before-text and --after-text (text comparison)", file=sys.stderr)
        print("  - --before-dir and --after-dir (directory comparison)", file=sys.stderr)
        sys.exit(1)

    # Output results
    print(format_results(results))


if __name__ == "__main__":
    main()
