#!/usr/bin/env python3
"""Parse and validate Skill Protocol v2 (compact inline format) blocks.

Parses v2 protocol blocks:
- [task-validation: PASS | clarity:✓ scope:✓ safety:✓ skill_match:✓ | action:proceed]
- [triggers: scoped-tasking bugfix-workflow | defer: read-and-locate]
- [precheck: skill-name | PASS | checks:field1 field2]
- [output: skill-name | completed high | key:"value" | next:downstream]
- [validate: skill-name | PASS | checks:field1 field2]
- [drop: skill-name | reason:"text" | active: skill1 skill2]
- [loop: skill-name | reason:"text"]

Mirrors skill_protocol_v1.py structure for consistency.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskValidation:
    """Parsed [task-validation: ...] block."""
    result: str  # PASS | WARN | REJECT
    clarity: str  # ✓ | ✗ | ⚠
    scope: str
    safety: str
    skill_match: str
    action: str  # proceed | ask_clarification | reject
    raw: str = ""


@dataclass
class TriggerEvaluation:
    """Parsed [triggers: ...] block."""
    triggered: list[str] = field(default_factory=list)
    deferred: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    raw: str = ""


@dataclass
class PreconditionCheck:
    """Parsed [precheck: skill-name | ...] block."""
    skill_name: str
    result: str  # PASS | FAIL
    checks: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    raw: str = ""


@dataclass
class SkillOutput:
    """Parsed [output: skill-name | ...] block."""
    skill_name: str
    status: str  # completed | partial | failed
    confidence: str  # high | medium | low
    outputs: dict[str, str] = field(default_factory=dict)
    next_skill: str | None = None
    raw: str = ""


@dataclass
class OutputValidation:
    """Parsed [validate: skill-name | ...] block."""
    skill_name: str
    result: str  # PASS | FAIL
    checks: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    raw: str = ""


@dataclass
class SkillDeactivation:
    """Parsed [drop: skill-name | ...] block."""
    skill_name: str
    reason: str
    active: list[str] = field(default_factory=list)
    raw: str = ""


@dataclass
class LoopDetection:
    """Parsed [loop: skill-name | ...] block."""
    skill_name: str
    reason: str
    raw: str = ""


def normalize_status_symbol(symbol: str) -> str:
    """Convert status symbols to standard form."""
    mapping = {
        '✓': 'PASS',
        '✗': 'FAIL',
        '⚠': 'WARN',
        '⏸': 'DEFER',
        'PASS': 'PASS',
        'FAIL': 'FAIL',
        'WARN': 'WARN',
        'DEFER': 'DEFER',
    }
    return mapping.get(symbol, symbol)


def parse_field_value_pairs(text: str) -> dict[str, str]:
    """Parse field:value pairs from pipe-separated text.

    Examples:
        "clarity:✓ scope:✓" → {"clarity": "✓", "scope": "✓"}
        "key:\"quoted value\" other:simple" → {"key": "quoted value", "other": "simple"}
    """
    pairs = {}

    # Match field:value patterns, handling quoted values
    pattern = r'(\w+):((?:"[^"]*")|(?:[^\s|]+))'
    matches = re.findall(pattern, text)

    for field, value in matches:
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        pairs[field] = value

    return pairs


def parse_space_delimited_list(text: str) -> list[str]:
    """Parse space-delimited list of identifiers.

    Example: "skill1 skill2 skill3" → ["skill1", "skill2", "skill3"]
    """
    return [item.strip() for item in text.split() if item.strip()]


def parse_task_validation(block: str) -> TaskValidation | None:
    """Parse [task-validation: PASS | clarity:✓ ... | action:proceed]."""
    pattern = r'\[task-validation:\s*([^|]+)\s*\|(.*?)\]'
    match = re.search(pattern, block)

    if not match:
        return None

    result = match.group(1).strip()
    fields_text = match.group(2).strip()

    fields = parse_field_value_pairs(fields_text)

    return TaskValidation(
        result=normalize_status_symbol(result),
        clarity=normalize_status_symbol(fields.get('clarity', '')),
        scope=normalize_status_symbol(fields.get('scope', '')),
        safety=normalize_status_symbol(fields.get('safety', '')),
        skill_match=normalize_status_symbol(fields.get('skill_match', '')),
        action=fields.get('action', ''),
        raw=block
    )


def parse_triggers(block: str) -> TriggerEvaluation | None:
    """Parse [triggers: skill1 skill2 | defer: skill3 | skip: skill4]."""
    pattern = r'\[triggers:\s*(.*?)\]'
    match = re.search(pattern, block)

    if not match:
        return None

    content = match.group(1)
    parts = [p.strip() for p in content.split('|')]

    triggered = []
    deferred = []
    skipped = []

    for part in parts:
        if ':' in part:
            key, value = part.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            skills = parse_space_delimited_list(value)

            if key == 'defer':
                deferred.extend(skills)
            elif key == 'skip':
                skipped.extend(skills)
        else:
            # Direct skill names (triggered)
            triggered.extend(parse_space_delimited_list(part))

    return TriggerEvaluation(
        triggered=triggered,
        deferred=deferred,
        skipped=skipped,
        raw=block
    )


def parse_precheck(block: str) -> PreconditionCheck | None:
    """Parse [precheck: skill-name | PASS | checks:field1 field2]."""
    pattern = r'\[precheck:\s*([^|]+)\s*\|\s*([^|]+)(.*?)\]'
    match = re.search(pattern, block)

    if not match:
        return None

    skill_name = match.group(1).strip()
    result = normalize_status_symbol(match.group(2).strip())
    rest = match.group(3).strip()

    fields = parse_field_value_pairs(rest) if rest else {}

    checks_str = fields.get('checks', '')
    checks = parse_space_delimited_list(checks_str) if checks_str else []

    failed_str = fields.get('failed', '')
    failed = parse_space_delimited_list(failed_str) if failed_str else []

    return PreconditionCheck(
        skill_name=skill_name,
        result=result,
        checks=checks,
        failed=failed,
        raw=block
    )


def parse_output(block: str) -> SkillOutput | None:
    """Parse [output: skill-name | completed high | key:"value" | next:skill]."""
    pattern = r'\[output:\s*([^|]+)\s*\|\s*([^|]+)(.*?)\]'
    match = re.search(pattern, block)

    if not match:
        return None

    skill_name = match.group(1).strip()
    status_confidence = match.group(2).strip().split()
    rest = match.group(3).strip()

    status = status_confidence[0] if len(status_confidence) > 0 else ''
    confidence = status_confidence[1] if len(status_confidence) > 1 else ''

    # Parse remaining fields
    fields = {}
    next_skill = None

    if rest:
        # Split by | but preserve quoted strings
        parts = [p.strip() for p in rest.split('|') if p.strip()]

        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]

                if key == 'next':
                    next_skill = value
                else:
                    fields[key] = value

    return SkillOutput(
        skill_name=skill_name,
        status=status,
        confidence=confidence,
        outputs=fields,
        next_skill=next_skill,
        raw=block
    )


def parse_validate(block: str) -> OutputValidation | None:
    """Parse [validate: skill-name | PASS | checks:field1 field2]."""
    pattern = r'\[validate:\s*([^|]+)\s*\|\s*([^|]+)(.*?)\]'
    match = re.search(pattern, block)

    if not match:
        return None

    skill_name = match.group(1).strip()
    result = normalize_status_symbol(match.group(2).strip())
    rest = match.group(3).strip()

    fields = parse_field_value_pairs(rest) if rest else {}

    checks_str = fields.get('checks', '')
    checks = parse_space_delimited_list(checks_str) if checks_str else []

    failed_str = fields.get('failed', '')
    failed = parse_space_delimited_list(failed_str) if failed_str else []

    missing_str = fields.get('missing', '')
    missing = parse_space_delimited_list(missing_str) if missing_str else []

    return OutputValidation(
        skill_name=skill_name,
        result=result,
        checks=checks,
        failed=failed,
        missing=missing,
        raw=block
    )


def parse_drop(block: str) -> SkillDeactivation | None:
    """Parse [drop: skill-name | reason:"text" | active: skill1 skill2]."""
    pattern = r'\[drop:\s*([^|]+)(.*?)\]'
    match = re.search(pattern, block)

    if not match:
        return None

    skill_name = match.group(1).strip()
    rest = match.group(2).strip()

    fields = parse_field_value_pairs(rest) if rest else {}

    reason = fields.get('reason', '')

    active_str = fields.get('active', '')
    active = parse_space_delimited_list(active_str) if active_str else []

    return SkillDeactivation(
        skill_name=skill_name,
        reason=reason,
        active=active,
        raw=block
    )


def parse_loop(block: str) -> LoopDetection | None:
    """Parse [loop: skill-name | reason:"text"]."""
    pattern = r'\[loop:\s*([^|]+)\s*\|(.*?)\]'
    match = re.search(pattern, block)

    if not match:
        return None

    skill_name = match.group(1).strip()
    rest = match.group(2).strip()

    fields = parse_field_value_pairs(rest) if rest else {}
    reason = fields.get('reason', rest)  # Fallback to raw text if not field:value format

    # Remove quotes if present
    if reason.startswith('"') and reason.endswith('"'):
        reason = reason[1:-1]

    return LoopDetection(
        skill_name=skill_name,
        reason=reason,
        raw=block
    )


def extract_protocol_blocks(text: str) -> list[str]:
    """Extract all v2 protocol blocks from text."""
    pattern = r'\[(?:task-validation|triggers|precheck|output|validate|drop|loop):.*?\]'
    return re.findall(pattern, text, re.DOTALL)


def parse_protocol_blocks(text: str) -> dict[str, list[Any]]:
    """Parse all v2 protocol blocks in text."""
    blocks = extract_protocol_blocks(text)

    result = {
        'task_validation': [],
        'triggers': [],
        'prechecks': [],
        'outputs': [],
        'validations': [],
        'deactivations': [],
        'loops': [],
    }

    for block in blocks:
        if block.startswith('[task-validation:'):
            parsed = parse_task_validation(block)
            if parsed:
                result['task_validation'].append(parsed)
        elif block.startswith('[triggers:'):
            parsed = parse_triggers(block)
            if parsed:
                result['triggers'].append(parsed)
        elif block.startswith('[precheck:'):
            parsed = parse_precheck(block)
            if parsed:
                result['prechecks'].append(parsed)
        elif block.startswith('[output:'):
            parsed = parse_output(block)
            if parsed:
                result['outputs'].append(parsed)
        elif block.startswith('[validate:'):
            parsed = parse_validate(block)
            if parsed:
                result['validations'].append(parsed)
        elif block.startswith('[drop:'):
            parsed = parse_drop(block)
            if parsed:
                result['deactivations'].append(parsed)
        elif block.startswith('[loop:'):
            parsed = parse_loop(block)
            if parsed:
                result['loops'].append(parsed)

    return result


if __name__ == '__main__':
    # Simple test
    test_text = """
    [task-validation: PASS | clarity:✓ scope:✓ safety:✓ skill_match:✓ | action:proceed]
    [triggers: scoped-tasking bugfix-workflow | defer: read-and-locate]
    [precheck: bugfix-workflow | PASS | checks:symptom root_cause]
    [output: bugfix-workflow | completed high | root_cause:"timeout in session.py:42" | next:minimal-change-strategy]
    [validate: bugfix-workflow | PASS | checks:root_cause fix_location]
    [drop: bugfix-workflow | reason:"root cause found" | active: minimal-change-strategy]
    """

    parsed = parse_protocol_blocks(test_text)

    print("Task Validation:", parsed['task_validation'])
    print("Triggers:", parsed['triggers'])
    print("Prechecks:", parsed['prechecks'])
    print("Outputs:", parsed['outputs'])
    print("Validations:", parsed['validations'])
    print("Deactivations:", parsed['deactivations'])
