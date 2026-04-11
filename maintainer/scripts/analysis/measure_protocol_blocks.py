#!/usr/bin/env python3
"""Measure token count for protocol blocks in example and governance files.

Extracts protocol blocks (v1 or v2 format) from markdown files and counts tokens.

Usage:
    python3 measure_protocol_blocks.py <file_path>
    python3 measure_protocol_blocks.py --all-examples
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parents[3]

def count_tokens(text: str) -> int:
    """Count tokens using tiktoken or character estimate."""
    if TIKTOKEN_AVAILABLE:
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except Exception:
            pass
    # Fallback: ~4 characters per token
    return len(text) // 4

def extract_protocol_blocks_v1(content: str) -> str:
    """Extract v1 protocol blocks (verbose YAML format) from content."""
    # Match blocks like [task-input-validation] ... [/task-input-validation]
    block_types = [
        'task-input-validation',
        'trigger-evaluation',
        'precondition-check',
        'skill-output',
        'output-validation',
        'skill-deactivation',
        'loop-detected'
    ]

    blocks = []
    for block_type in block_types:
        pattern = rf'\[{block_type}\].*?\[/{block_type}\]'
        found = re.findall(pattern, content, re.DOTALL)
        blocks.extend(found)

    return '\n\n'.join(blocks) if blocks else ''

def extract_protocol_blocks_v2(content: str) -> str:
    """Extract v2 protocol blocks (compact inline format) from content."""
    # Match blocks like [task-validation: ...], [triggers: ...], etc.
    pattern = r'\[(?:task-validation|triggers|precheck|output|validate|drop|loop):.*?\]'
    blocks = re.findall(pattern, content)
    return '\n'.join(blocks) if blocks else ''

def extract_protocol_blocks(content: str) -> tuple[str, str]:
    """Extract both v1 and v2 protocol blocks and determine which format is used."""
    v1_blocks = extract_protocol_blocks_v1(content)
    v2_blocks = extract_protocol_blocks_v2(content)

    if v1_blocks and not v2_blocks:
        return v1_blocks, 'v1'
    elif v2_blocks and not v1_blocks:
        return v2_blocks, 'v2'
    elif v1_blocks and v2_blocks:
        return v1_blocks + '\n\n' + v2_blocks, 'mixed'
    else:
        return '', 'none'

def extract_protocol_section_by_lines(content: str, start_line: int, end_line: int) -> str:
    """Extract specific line range from content (1-indexed)."""
    lines = content.split('\n')
    # Convert to 0-indexed
    return '\n'.join(lines[start_line-1:end_line])

def measure_file(file_path: Path) -> dict:
    """Measure protocol blocks in a file."""
    content = file_path.read_text(encoding='utf-8')

    # Try automatic extraction first
    protocol_text, format_type = extract_protocol_blocks(content)

    # Get relative path, handling files outside REPO_ROOT
    try:
        relative_path = str(file_path.relative_to(REPO_ROOT))
    except ValueError:
        # File is outside repo, use absolute path
        relative_path = str(file_path)

    result = {
        'file': relative_path,
        'format': format_type,
        'protocol_chars': len(protocol_text),
        'protocol_tokens': count_tokens(protocol_text),
        'total_chars': len(content),
        'total_tokens': count_tokens(content),
    }

    if protocol_text:
        result['protocol_percentage'] = (len(protocol_text) / len(content)) * 100
    else:
        result['protocol_percentage'] = 0

    return result

def measure_all_examples() -> list[dict]:
    """Measure all example files."""
    examples_dir = REPO_ROOT / 'examples'
    results = []

    for example_file in sorted(examples_dir.glob('*.md')):
        results.append(measure_file(example_file))

    return results

def main():
    parser = argparse.ArgumentParser(description='Measure protocol block tokens')
    parser.add_argument('file', nargs='?', help='File to measure')
    parser.add_argument('--all-examples', action='store_true', help='Measure all example files')
    parser.add_argument('--lines', help='Line range (e.g., "57-135")')

    args = parser.parse_args()

    if args.all_examples:
        results = measure_all_examples()

        print("Protocol Block Token Measurements")
        print("=" * 80)
        print(f"{'File':<45} {'Format':<8} {'Tokens':<8} {'% of Total'}")
        print("-" * 80)

        total_tokens = 0
        for r in results:
            filename = Path(r['file']).name
            total_tokens += r['protocol_tokens']
            pct = f"{r['protocol_percentage']:.1f}%" if r['protocol_percentage'] > 0 else "N/A"
            print(f"{filename:<45} {r['format']:<8} {r['protocol_tokens']:<8} {pct}")

        print("-" * 80)
        print(f"Total protocol tokens across all examples: {total_tokens}")
        print()
        print(f"Token counting method: {'tiktoken' if TIKTOKEN_AVAILABLE else 'character estimate (~4 chars/token)'}")

    elif args.file:
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = REPO_ROOT / args.file

        if not file_path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        file_path = file_path.resolve()

        if args.lines:
            # Extract specific line range
            match = re.match(r'(\d+)-(\d+)', args.lines)
            if not match:
                print(f"Error: Invalid line range format. Use: 57-135", file=sys.stderr)
                sys.exit(1)

            start, end = int(match.group(1)), int(match.group(2))
            content = file_path.read_text(encoding='utf-8')
            protocol_text = extract_protocol_section_by_lines(content, start, end)

            result = {
                'file': str(file_path.relative_to(REPO_ROOT)),
                'lines': f'{start}-{end}',
                'protocol_chars': len(protocol_text),
                'protocol_tokens': count_tokens(protocol_text),
            }

            print(f"File: {result['file']}")
            print(f"Lines: {result['lines']}")
            print(f"Characters: {result['protocol_chars']}")
            print(f"Tokens: {result['protocol_tokens']}")
            print(f"Token counting: {'tiktoken' if TIKTOKEN_AVAILABLE else 'character estimate'}")
        else:
            result = measure_file(file_path)

            print(f"File: {result['file']}")
            print(f"Format: {result['format']}")
            print(f"Protocol blocks:")
            print(f"  Characters: {result['protocol_chars']}")
            print(f"  Tokens: {result['protocol_tokens']}")
            print(f"  Percentage of total: {result['protocol_percentage']:.1f}%")
            print(f"Total file:")
            print(f"  Characters: {result['total_chars']}")
            print(f"  Tokens: {result['total_tokens']}")
            print(f"Token counting: {'tiktoken' if TIKTOKEN_AVAILABLE else 'character estimate'}")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
