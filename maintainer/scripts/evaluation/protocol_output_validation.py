#!/usr/bin/env python3
"""Client-independent validation for Skill Protocol output blocks."""

from __future__ import annotations

import re
from typing import Literal

from skill_protocol import validate_protocol_text
from skill_protocol_unified import parse_protocol, validate_protocol_lifecycle


ValidationStatus = Literal["pass", "fail"]
ARTIFACT_REVIEW_SKILL = "artifact-review-loop"
REQUIRED_REVIEW_HEADINGS: tuple[str, ...] = (
    "Review Result",
    "Issues",
    "Changes Made",
    "Validation",
    "Residual Assumptions",
    "Clarification Questions",
)
ARTIFACT_TYPES = frozenset({"requirements", "design", "plan", "code", "tests"})
ARTIFACT_SUBTYPES: dict[str, frozenset[str]] = {
    "requirements": frozenset(
        {"requirement-spec", "prd", "user-story", "acceptance-criteria"}
    ),
    "design": frozenset(
        {"architecture", "adr-rfc", "interface", "data-model", "technical-proposal"}
    ),
    "plan": frozenset(
        {"implementation-plan", "migration-plan", "roadmap", "task-sequence"}
    ),
    "code": frozenset(
        {
            "working-tree-diff",
            "staged-diff",
            "commit",
            "commit-range",
            "pull-request",
            "source-files",
            "implementation",
        }
    ),
    "tests": frozenset(
        {"test-cases", "test-files", "test-strategy", "coverage-matrix", "fixtures"}
    ),
}
REQUIRED_COMPACT_FIELDS: tuple[str, ...] = (
    "review_result",
    "artifact_type",
    "artifact_subtype",
    "secondary_types",
    "review_context",
    "mode",
    "authorization_source",
    "write_scope",
    "issues",
    "changes",
    "validation",
)
REVIEW_RESULT_FIELDS: tuple[str, ...] = (
    "review_result",
    "artifact_type",
    "artifact_subtype",
    "secondary_types",
    "review_context",
    "mode",
    "authorization_source",
    "write_scope",
)
ISSUE_SEVERITIES: tuple[str, ...] = ("blocking", "warning", "low-risk")
ISSUE_FIELDS: tuple[str, ...] = (
    "severity",
    "area",
    "problem",
    "impact",
    "required_fix",
)


def validate_protocol_output(text: str) -> tuple[ValidationStatus, list[str], list[str]]:
    """Validate legacy or unified Skill Protocol blocks in model output."""

    legacy_result = validate_protocol_text(text)
    parsed = parse_protocol(text)
    review_outputs = [
        block
        for block in parsed.get("outputs", [])
        if getattr(block, "skill_name", "") == ARTIFACT_REVIEW_SKILL
    ]
    artifact_output_markers = re.findall(
        rf"(?m)^\s*\[output:\s*{re.escape(ARTIFACT_REVIEW_SKILL)}"
        rf"(?=\s|\||\])",
        text,
    )
    artifact_validation_markers = re.findall(
        rf"(?m)^\s*\[validate:\s*{re.escape(ARTIFACT_REVIEW_SKILL)}"
        rf"(?=\s|\||\])",
        text,
    )
    artifact_heading_intent = bool(
        re.search(r"(?im)^##\s+Review Result\s*$", text)
    )
    artifact_review_intent = bool(
        artifact_output_markers
        or artifact_validation_markers
        or artifact_heading_intent
    )
    if legacy_result.blocks and not artifact_review_intent:
        protocol_blocks = [block.raw_tag for block in legacy_result.blocks]
        status: ValidationStatus = "pass" if legacy_result.status == "pass" else "fail"
        return status, protocol_blocks, list(legacy_result.issues)

    if parsed.get("detected_format", "none") == "none":
        if artifact_review_intent:
            return "fail", [], [
                "Artifact review intent requires exactly one parsed compact output block."
            ]
        return "fail", [], ["No Skill Protocol blocks detected in output."]

    protocol_blocks: list[str] = [
        block.raw_tag for block in legacy_result.blocks
    ]
    for key in (
        "task_validation",
        "triggers",
        "prechecks",
        "outputs",
        "validations",
        "deactivations",
        "loops",
    ):
        protocol_blocks.extend(
            getattr(block, "raw", repr(block)) for block in parsed.get(key, [])
        )

    issues = list(legacy_result.issues) if legacy_result.blocks else []
    if len(artifact_output_markers) != len(review_outputs):
        issues.append(
            "Artifact review compact output marker count does not match parsed blocks; "
            "at least one block is malformed."
        )
    if artifact_review_intent and len(review_outputs) != 1:
        issues.append(
            "Artifact review intent requires exactly one parsed compact output block."
        )
    issues.extend(validate_protocol_lifecycle(parsed))
    issues.extend(validate_review_loop_output_contract(text, parsed))
    status = "pass" if not issues else "fail"
    return status, protocol_blocks, issues


def validate_review_loop_output_contract(text: str, parsed: dict) -> list[str]:
    """Validate the Markdown and compact unified artifact review contract."""

    issues: list[str] = []
    review_outputs = [
        block
        for block in parsed.get("outputs", [])
        if getattr(block, "skill_name", "") == ARTIFACT_REVIEW_SKILL
    ]
    if not review_outputs:
        return issues

    heading_positions: list[int] = []
    for heading in REQUIRED_REVIEW_HEADINGS:
        matches = list(re.finditer(rf"(?im)^##\s+{re.escape(heading)}\s*$", text))
        if not matches:
            issues.append(f"Artifact review output is missing `## {heading}` section.")
        elif len(matches) > 1:
            issues.append(f"Artifact review output repeats `## {heading}` section.")
        else:
            heading_positions.append(matches[0].start())
    if len(heading_positions) == len(REQUIRED_REVIEW_HEADINGS) and heading_positions != sorted(
        heading_positions
    ):
        issues.append("Artifact review Markdown sections are out of contract order.")

    if len(review_outputs) != 1:
        issues.append("Artifact review output must contain exactly one compact output block.")
        return issues
    block = review_outputs[0]
    if getattr(block, "status", None) != "completed":
        issues.append("Artifact review compact output status must be `completed`.")
    if getattr(block, "confidence", None) not in {"high", "medium", "low"}:
        issues.append(
            "Artifact review compact output confidence must be high, medium, or low."
        )
    review_validations = [
        validation
        for validation in parsed.get("validations", [])
        if getattr(validation, "skill_name", "") == ARTIFACT_REVIEW_SKILL
    ]
    if len(review_validations) != 1:
        issues.append(
            "Artifact review output requires exactly one matching validation block."
        )
    else:
        validation = review_validations[0]
        if getattr(validation, "result", None) != "PASS":
            issues.append("Artifact review validation result must be `PASS`.")
        if getattr(validation, "checks", None) != ["contract"]:
            issues.append(
                "Artifact review validation checks must be exactly `contract`."
            )
    compact = getattr(block, "outputs", {})
    for field in REQUIRED_COMPACT_FIELDS:
        if field not in compact:
            issues.append(f"[output: {ARTIFACT_REVIEW_SKILL}] is missing required `{field}` field.")

    markdown_fields, result_section_issues = _parse_review_result_section(
        _section_body(text, "Review Result")
    )
    issues.extend(result_section_issues)

    markdown_issue_counts, issue_section_issues = _parse_issues_section(
        _section_body(text, "Issues")
    )
    issues.extend(issue_section_issues)
    changes, changes_issues = _parse_structured_list(
        _section_body(text, "Changes Made"),
        fields=("file", "summary"),
        section="Changes Made",
    )
    issues.extend(changes_issues)
    _validation, validation_issues = _parse_simple_list(
        _section_body(text, "Validation"),
        section="Validation",
    )
    issues.extend(validation_issues)
    assumptions, assumption_issues = _parse_structured_list(
        _section_body(text, "Residual Assumptions"),
        fields=("assumption", "validation_method"),
        section="Residual Assumptions",
    )
    issues.extend(assumption_issues)
    questions, question_issues = _parse_structured_list(
        _section_body(text, "Clarification Questions"),
        fields=("question", "why_blocked"),
        section="Clarification Questions",
    )
    issues.extend(question_issues)

    artifact_type = markdown_fields["artifact_type"]
    artifact_subtype = markdown_fields["artifact_subtype"]
    if artifact_type is not None and artifact_type not in ARTIFACT_TYPES:
        issues.append(f"Invalid artifact_type: {artifact_type!r}.")
    elif (
        artifact_type is not None
        and artifact_subtype is not None
        and artifact_subtype not in ARTIFACT_SUBTYPES[artifact_type]
    ):
        issues.append(
            f"artifact_subtype {artifact_subtype!r} is invalid for {artifact_type!r}."
        )

    secondary = _parse_secondary_types(markdown_fields["secondary_types"])
    if secondary is None and markdown_fields["secondary_types"] is not None:
        issues.append("Markdown secondary_types must be [] or a bracketed type list.")
    elif secondary is not None:
        if len(secondary) != len(set(secondary)):
            issues.append("secondary_types contains duplicates.")
        if any(item not in ARTIFACT_TYPES for item in secondary):
            issues.append("secondary_types contains an invalid artifact type.")
        if artifact_type in secondary:
            issues.append("secondary_types must not repeat artifact_type.")

    for field, markdown_value in markdown_fields.items():
        if field == "secondary_types":
            compact_secondary = _parse_compact_secondary(compact.get(field))
            if secondary is not None and compact_secondary != secondary:
                issues.append("Compact secondary_types does not match Markdown.")
        elif markdown_value is not None and compact.get(field) != markdown_value:
            issues.append(f"Compact {field} does not match Markdown.")

    compact_issue_counts, compact_issue_error = _parse_compact_issue_counts(
        compact.get("issues")
    )
    if compact_issue_error:
        issues.append(compact_issue_error)
    elif (
        markdown_issue_counts is not None
        and compact_issue_counts != markdown_issue_counts
    ):
        issues.append("Compact issues counts do not match Markdown Issues findings.")

    review_context = markdown_fields["review_context"]
    mode = markdown_fields["mode"]
    source = markdown_fields["authorization_source"]
    scope = markdown_fields["write_scope"]
    if review_context == "self-delivery":
        if (
            artifact_type != "code"
            or mode != "review-and-revise"
            or source != "inherited-current-task"
            or scope != "current-task-diff"
        ):
            issues.append("Self-delivery routing violates strict revision authority.")
    elif review_context == "requested":
        if mode == "review-only":
            if source != "none" or scope != "none":
                issues.append("Requested review-only output must have zero write authority.")
            if changes:
                issues.append("Requested review-only output must report no changes.")
            if compact.get("changes") != "none":
                issues.append("Requested review-only compact output must use changes:\"none\".")
        elif mode == "review-and-revise":
            expected_scope = (
                "reviewed-implementation"
                if artifact_type == "code"
                else "reviewed-artifact"
            )
            if source != "explicit-user-request" or scope != expected_scope:
                issues.append(
                    "Requested revision lacks the exact explicit write scope."
                )
        elif mode is not None:
            issues.append(f"Invalid mode: {mode!r}.")
    elif review_context is not None:
        issues.append(f"Invalid review_context: {review_context!r}.")

    review_result = markdown_fields["review_result"]
    if review_result not in {
        None,
        "clean",
        "clean_with_assumptions",
        "needs_clarification",
        "issues_found",
    }:
        issues.append(f"Invalid review_result: {review_result!r}.")

    if markdown_issue_counts is not None:
        total_findings = sum(markdown_issue_counts.values())
        if review_result == "clean":
            if total_findings:
                issues.append("clean review_result requires zero Issues findings.")
            if assumptions:
                issues.append("clean review_result requires no residual assumptions.")
            if questions:
                issues.append("clean review_result requires no clarification questions.")
        elif review_result == "clean_with_assumptions":
            if total_findings:
                issues.append(
                    "clean_with_assumptions review_result requires zero Issues findings."
                )
            if not assumptions:
                issues.append(
                    "clean_with_assumptions requires at least one residual assumption."
                )
            if questions:
                issues.append(
                    "clean_with_assumptions requires no clarification questions."
                )
        elif review_result == "issues_found" and total_findings == 0:
            issues.append("issues_found review_result requires at least one finding.")
        elif review_result == "needs_clarification":
            if total_findings == 0:
                issues.append(
                    "needs_clarification review_result requires at least one finding."
                )
            if not questions:
                issues.append(
                    "needs_clarification review_result requires at least one structured question."
                )
    return issues


def _parse_review_result_section(
    body: str | None,
) -> tuple[dict[str, str | None], list[str]]:
    values: dict[str, str | None] = {
        field: None for field in REVIEW_RESULT_FIELDS
    }
    issues: list[str] = []
    if body is None:
        return values, issues

    seen: set[str] = set()
    for line in body.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"\s*([a-z_]+)\s*:\s*(.*?)\s*", line)
        if not match:
            issues.append(f"Review Result contains malformed line: {line.strip()!r}.")
            continue
        field, value = match.groups()
        if field not in values:
            issues.append(f"Review Result contains unexpected `{field}:` field.")
            continue
        if field in seen:
            issues.append(f"Review Result repeats `{field}:` field.")
            continue
        seen.add(field)
        if not _scalar_is_nonempty(value):
            issues.append(f"Review Result `{field}:` value must be nonempty.")
            continue
        values[field] = value.strip()

    for field, value in values.items():
        if value is None and field not in seen:
            issues.append(f"Artifact review output is missing Markdown `{field}:` line.")
    return values, issues


def _section_body(text: str, heading: str) -> str | None:
    match = re.search(
        rf"(?ims)^##\s+{re.escape(heading)}\s*$\n"
        rf"(.*?)(?=^##\s+|^\[(?:task-validation|triggers|precheck|output|"
        rf"validate|drop|loop):|^\[(?:task-input-validation|trigger-evaluation|"
        rf"precondition-check|skill-output|output-validation|"
        rf"skill-deactivation|loop-detected)(?::|\])|\Z)",
        text,
    )
    return match.group(1).strip() if match else None


def _parse_issues_section(
    body: str | None,
) -> tuple[dict[str, int] | None, list[str]]:
    if body is None:
        return None, []

    issues: list[str] = []
    bucket_matches = list(
        re.finditer(r"(?m)^([a-z][a-z-]*):[ \t]*$", body)
    )
    bucket_names = [match.group(1) for match in bucket_matches]
    if bucket_names != list(ISSUE_SEVERITIES):
        issues.append(
            "Issues section must contain exactly three buckets in order: "
            "blocking, warning, low-risk."
        )
        return None, issues
    if body[: bucket_matches[0].start()].strip():
        issues.append("Issues section contains content before the blocking bucket.")

    counts: dict[str, int] = {}
    for index, (severity, match) in enumerate(zip(ISSUE_SEVERITIES, bucket_matches)):
        end = (
            bucket_matches[index + 1].start()
            if index + 1 < len(bucket_matches)
            else len(body)
        )
        bucket_body = body[match.end() : end].strip()
        findings, finding_issues = _parse_structured_list(
            bucket_body,
            fields=ISSUE_FIELDS,
            section=f"Issues {severity} bucket",
        )
        issues.extend(finding_issues)
        counts[severity] = len(findings)
        for finding in findings:
            finding_severity = _unquote_scalar(finding.get("severity", ""))
            if finding_severity != severity:
                issues.append(
                    f"Issues {severity} bucket finding severity must be {severity!r}, "
                    f"got {finding_severity!r}."
                )
    return counts, issues


def _parse_structured_list(
    body: str | None,
    *,
    fields: tuple[str, ...],
    section: str,
) -> tuple[list[dict[str, str]], list[str]]:
    if body is None:
        return [], []
    stripped = body.strip()
    if stripped == "- None":
        return [], []
    if not stripped:
        return [], [f"{section} must use `- None` or structured entries."]
    if re.search(r"(?m)^\s*-\s+None\s*$", stripped):
        none_issue = [f"{section} may use `- None` only as its single body item."]
    else:
        none_issue = []

    entries: list[dict[str, str]] = []
    issues = list(none_issue)
    current: dict[str, str] | None = None

    def finish_current() -> None:
        if current is None:
            return
        for field in fields:
            if field not in current:
                issues.append(f"{section} entry is missing `{field}:`.")
            elif not _scalar_is_nonempty(current[field]):
                issues.append(f"{section} entry `{field}:` value must be nonempty.")
        entries.append(current)

    for line in stripped.splitlines():
        if not line.strip():
            continue
        start = re.fullmatch(r"-\s+([a-z_][a-z0-9_-]*)\s*:\s*(.*)", line)
        continuation = re.fullmatch(
            r"\s{2,}([a-z_][a-z0-9_-]*)\s*:\s*(.*)", line
        )
        if start:
            finish_current()
            field, value = start.groups()
            current = {}
            if field != fields[0]:
                issues.append(
                    f"{section} entry must start with `{fields[0]}:`, got `{field}:`."
                )
            if field not in fields:
                issues.append(f"{section} entry contains unexpected `{field}:` field.")
            else:
                current[field] = value.strip()
            continue
        if continuation:
            field, value = continuation.groups()
            if current is None:
                issues.append(
                    f"{section} field `{field}:` appears before an entry start."
                )
            elif field not in fields:
                issues.append(f"{section} entry contains unexpected `{field}:` field.")
            elif field in current:
                issues.append(f"{section} entry repeats `{field}:` field.")
            else:
                current[field] = value.strip()
            continue
        issues.append(f"{section} contains malformed line: {line.strip()!r}.")

    finish_current()
    if not entries:
        issues.append(f"{section} must use `- None` or one or more structured entries.")
    return entries, issues


def _parse_simple_list(
    body: str | None,
    *,
    section: str,
) -> tuple[list[str], list[str]]:
    if body is None:
        return [], []
    stripped = body.strip()
    if stripped == "- None":
        return [], []
    if not stripped:
        return [], [f"{section} must use `- None` or nonempty list items."]

    values: list[str] = []
    issues: list[str] = []
    for line in stripped.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"-\s+(.+?)\s*", line)
        if not match:
            issues.append(f"{section} contains malformed line: {line.strip()!r}.")
            continue
        value = match.group(1)
        if value == "None":
            issues.append(f"{section} may use `- None` only as its single body item.")
        elif not _scalar_is_nonempty(value):
            issues.append(f"{section} list items must be nonempty.")
        else:
            values.append(value.strip())
    if not values:
        issues.append(f"{section} must use `- None` or nonempty list items.")
    return values, issues


def _parse_compact_issue_counts(
    value: str | None,
) -> tuple[dict[str, int] | None, str | None]:
    if value is None:
        return None, None
    if value == "none":
        return {severity: 0 for severity in ISSUE_SEVERITIES}, None
    match = re.fullmatch(
        r"(\d+) blocking, (\d+) warning, (\d+) low-risk",
        value,
    )
    if not match:
        return None, (
            "Compact issues must be `none` or exact counts formatted as "
            "`<n> blocking, <n> warning, <n> low-risk`."
        )
    return {
        severity: int(count)
        for severity, count in zip(ISSUE_SEVERITIES, match.groups())
    }, None


def _scalar_is_nonempty(value: str) -> bool:
    return bool(_unquote_scalar(value).strip())


def _unquote_scalar(value: str) -> str:
    stripped = value.strip()
    if (
        len(stripped) >= 2
        and stripped[0] == stripped[-1]
        and stripped[0] in {'"', "'"}
    ):
        return stripped[1:-1]
    return stripped


def _parse_secondary_types(value: str | None) -> tuple[str, ...] | None:
    if value is None:
        return None
    if value == "[]":
        return ()
    match = re.fullmatch(r"\[\s*([^]]+?)\s*\]", value)
    if not match:
        return None
    return tuple(item.strip() for item in match.group(1).split(",") if item.strip())


def _parse_compact_secondary(value: str | None) -> tuple[str, ...] | None:
    if value is None:
        return None
    if value == "none":
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())
