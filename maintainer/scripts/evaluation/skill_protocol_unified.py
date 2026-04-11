#!/usr/bin/env python3
"""Unified parser for Skill Protocol v1 and v2 formats.

Auto-detects format and delegates to appropriate parser.
Returns normalized data structures compatible with both versions.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Import both parsers
try:
    import skill_protocol_v1 as v1_parser
except ImportError:
    # Try relative import
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    import skill_protocol_v1 as v1_parser

import skill_protocol_v2 as v2_parser


def detect_protocol_format(text: str) -> str:
    """Detect whether text contains v1, v2, or mixed protocol blocks.

    Returns: 'v1', 'v2', 'mixed', or 'none'
    """
    # v1 pattern: [block-name] ... [/block-name]
    v1_pattern = r'\[(?:task-input-validation|trigger-evaluation|precondition-check|skill-output|output-validation|skill-deactivation|loop-detected)\].*?\[/'
    v1_matches = re.findall(v1_pattern, text, re.DOTALL)

    # v2 pattern: [block-name: ...]
    v2_pattern = r'\[(?:task-validation|triggers|precheck|output|validate|drop|loop):'
    v2_matches = re.findall(v2_pattern, text)

    has_v1 = len(v1_matches) > 0
    has_v2 = len(v2_matches) > 0

    if has_v1 and has_v2:
        return 'mixed'
    elif has_v1:
        return 'v1'
    elif has_v2:
        return 'v2'
    else:
        return 'none'


def normalize_v1_to_common(v1_data: dict) -> dict[str, list[Any]]:
    """Normalize v1 parser output to common format."""
    # v1_parser returns different structure, map to common format
    # This is a simplified mapping - expand as needed
    return {
        'task_validation': v1_data.get('task_validations', []),
        'triggers': v1_data.get('trigger_evaluations', []),
        'prechecks': v1_data.get('precondition_checks', []),
        'outputs': v1_data.get('skill_outputs', []),
        'validations': v1_data.get('output_validations', []),
        'deactivations': v1_data.get('skill_deactivations', []),
        'loops': v1_data.get('loop_detections', []),
        'format': 'v1'
    }


def normalize_v2_to_common(v2_data: dict) -> dict[str, list[Any]]:
    """Normalize v2 parser output to common format."""
    v2_data['format'] = 'v2'
    return v2_data


def parse_protocol(text: str, force_format: str | None = None) -> dict[str, Any]:
    """Parse protocol blocks, auto-detecting format.

    Args:
        text: Content to parse
        force_format: Override auto-detection with 'v1' or 'v2'

    Returns:
        Dictionary with normalized protocol blocks and metadata
    """
    if force_format:
        format_type = force_format
    else:
        format_type = detect_protocol_format(text)

    result = {
        'detected_format': format_type,
        'task_validation': [],
        'triggers': [],
        'prechecks': [],
        'outputs': [],
        'validations': [],
        'deactivations': [],
        'loops': [],
    }

    if format_type == 'v1':
        # Use v1 parser
        if hasattr(v1_parser, 'parse_protocol_blocks'):
            v1_data = v1_parser.parse_protocol_blocks(text)
            result.update(normalize_v1_to_common(v1_data))
        else:
            # Fallback: assume v1_parser has individual parse functions
            result['format'] = 'v1'
            result['parse_error'] = 'v1_parser module structure incompatible'

    elif format_type == 'v2':
        # Use v2 parser
        v2_data = v2_parser.parse_protocol_blocks(text)
        result.update(normalize_v2_to_common(v2_data))

    elif format_type == 'mixed':
        # Parse both, return separate results
        v1_data = {}
        v2_data = {}

        if hasattr(v1_parser, 'parse_protocol_blocks'):
            v1_data = v1_parser.parse_protocol_blocks(text)

        v2_data = v2_parser.parse_protocol_blocks(text)

        # Merge results
        result['format'] = 'mixed'
        result['v1_blocks'] = normalize_v1_to_common(v1_data) if v1_data else {}
        result['v2_blocks'] = normalize_v2_to_common(v2_data)

        # Combine into main result (prefer v2 for overlaps)
        for key in ['task_validation', 'triggers', 'prechecks', 'outputs', 'validations', 'deactivations', 'loops']:
            combined = []
            if v1_data:
                combined.extend(result['v1_blocks'].get(key, []))
            combined.extend(result['v2_blocks'].get(key, []))
            result[key] = combined

    return result


def validate_protocol_lifecycle(parsed: dict) -> list[str]:
    """Validate protocol lifecycle rules.

    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Extract skill names from outputs
    output_skills = {block.skill_name for block in parsed.get('outputs', [])}

    # Check: every output must have matching validate
    validate_skills = {block.skill_name for block in parsed.get('validations', [])}
    for skill in output_skills:
        if skill not in validate_skills:
            errors.append(f"Skill '{skill}' has output but no matching validation")

    # Check: every activated skill should eventually be dropped
    triggered_skills = set()
    for trigger_block in parsed.get('triggers', []):
        if hasattr(trigger_block, 'triggered'):
            triggered_skills.update(trigger_block.triggered)
        elif isinstance(trigger_block, dict):
            triggered_skills.update(trigger_block.get('activated_now', []))

    dropped_skills = {block.skill_name for block in parsed.get('deactivations', [])}
    for skill in triggered_skills:
        if skill not in dropped_skills:
            errors.append(f"Skill '{skill}' was triggered but never dropped")

    return errors


def get_statistics(parsed: dict) -> dict[str, Any]:
    """Get statistics about parsed protocol blocks."""
    return {
        'format': parsed.get('detected_format', 'unknown'),
        'task_validations': len(parsed.get('task_validation', [])),
        'trigger_blocks': len(parsed.get('triggers', [])),
        'prechecks': len(parsed.get('prechecks', [])),
        'outputs': len(parsed.get('outputs', [])),
        'validations': len(parsed.get('validations', [])),
        'deactivations': len(parsed.get('deactivations', [])),
        'loops': len(parsed.get('loops', [])),
        'total_blocks': sum([
            len(parsed.get('task_validation', [])),
            len(parsed.get('triggers', [])),
            len(parsed.get('prechecks', [])),
            len(parsed.get('outputs', [])),
            len(parsed.get('validations', [])),
            len(parsed.get('deactivations', [])),
            len(parsed.get('loops', []))
        ])
    }


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        if file_path.exists():
            text = file_path.read_text(encoding='utf-8')

            # Parse
            parsed = parse_protocol(text)

            # Display results
            print(f"File: {file_path}")
            print(f"Detected format: {parsed['detected_format']}")
            print()

            # Statistics
            stats = get_statistics(parsed)
            print("Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            print()

            # Validation
            errors = validate_protocol_lifecycle(parsed)
            if errors:
                print("Lifecycle validation errors:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print("✓ Lifecycle validation passed")
        else:
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
    else:
        # Test with sample data
        test_v2 = """
        [task-validation: PASS | clarity:✓ scope:✓ safety:✓ skill_match:✓ | action:proceed]
        [triggers: scoped-tasking bugfix-workflow]
        [precheck: scoped-tasking | PASS]
        [output: scoped-tasking | completed high | boundary:"auth module" | next:bugfix-workflow]
        [validate: scoped-tasking | PASS]
        [drop: scoped-tasking | reason:"boundary confirmed" | active: bugfix-workflow]
        """

        print("Testing v2 format:")
        parsed = parse_protocol(test_v2)
        print(f"Format: {parsed['detected_format']}")
        print(f"Blocks: {get_statistics(parsed)}")
        print(f"Validation: {validate_protocol_lifecycle(parsed)}")
