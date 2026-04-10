from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


EXECUTION_SKILLS: tuple[str, ...] = (
    "scoped-tasking",
    "design-before-plan",
    "minimal-change-strategy",
    "plan-before-action",
    "targeted-validation",
    "context-budget-awareness",
    "read-and-locate",
    "safe-refactor",
    "bugfix-workflow",
    "impact-analysis",
    "self-review",
    "incremental-delivery",
)

ORCHESTRATION_SKILLS: tuple[str, ...] = (
    "multi-agent-protocol",
    "conflict-resolution",
)

PHASE_SKILLS: tuple[str, ...] = (
    "phase-plan",
    "phase-execute",
    "phase-plan-review",
    "phase-contract-tools",
)

SKILL_FAMILY: dict[str, str] = {
    **{skill: "execution" for skill in EXECUTION_SKILLS},
    **{skill: "orchestration" for skill in ORCHESTRATION_SKILLS},
    **{skill: "phase" for skill in PHASE_SKILLS},
}

SKILL_REQUIRED_SECTIONS: dict[str, tuple[str, ...]] = {
    **{
        skill: (
            "Contract",
            "Failure Handling",
            "Output Example",
            "Deactivation Trigger",
        )
        for skill in EXECUTION_SKILLS
    },
    "multi-agent-protocol": (
        "Delegation Contract",
        "Synthesis Contract",
        "Failure Handling",
        "Deactivation Trigger",
    ),
    "conflict-resolution": (
        "Contract",
        "Failure Handling",
        "Deactivation Trigger",
    ),
    **{
        skill: (
            "Artifact Contract",
            "Gate Contract",
            "Failure Handling",
            "Lifecycle",
        )
        for skill in PHASE_SKILLS
    },
}

SKILL_OUTPUT_FIELDS: dict[str, tuple[str, ...]] = {
    "scoped-tasking": ("objective", "analysis_boundary", "excluded_areas"),
    "design-before-plan": ("requirements", "alternatives", "chosen_design", "acceptance_criteria"),
    "minimal-change-strategy": ("change_boundary", "scope_guardrails", "stop_conditions"),
    "plan-before-action": ("assumptions", "working_set", "sequence", "validation_boundary"),
    "targeted-validation": ("checks_to_run", "risks_not_covered", "pass_criteria"),
    "context-budget-awareness": ("current_state", "dropped_hypotheses", "open_questions"),
    "read-and-locate": ("entry_points", "candidate_files", "edit_points"),
    "safe-refactor": ("behavior_invariants", "refactor_boundary", "rollback_notes"),
    "bugfix-workflow": ("symptom", "repro", "fault_domain", "fix_hypothesis"),
    "impact-analysis": ("affected_callers", "contracts", "compatibility_risks"),
    "self-review": ("findings", "residual_risks", "scope_violations"),
    "incremental-delivery": ("increments", "merge_order", "gates"),
    "multi-agent-protocol": ("split_dimension", "lanes", "integration_plan", "synthesis"),
    "conflict-resolution": ("claims", "evidence", "resolution", "residual_uncertainty"),
    "phase-plan": ("plan_artifacts", "waves", "gates", "ownership"),
    "phase-execute": ("wave_status", "lane_results", "gate_outcomes", "rollback_state"),
    "phase-plan-review": ("alignment_findings", "blocking_issues", "approval_status"),
    "phase-contract-tools": ("schema_checks", "rendered_views", "contract_issues"),
}

STANDARD_BLOCK_FIELDS: dict[str, tuple[str, ...]] = {
    "task-input-validation": ("clarity", "scope", "safety", "skill_match", "result", "action"),
    "trigger-evaluation": ("evaluated", "activated_now", "deferred"),
    "precondition-check": ("checks", "result"),
    "skill-output": ("status", "confidence", "outputs", "signals", "recommendations"),
    "output-validation": ("checks", "result"),
    "skill-deactivation": ("reason", "outputs_consumed_by", "remaining_active"),
}

BLOCK_SEQUENCE: tuple[str, ...] = (
    "task-input-validation",
    "trigger-evaluation",
    "precondition-check",
    "skill-output",
    "output-validation",
    "skill-deactivation",
)

BLOCK_START_RE = re.compile(
    r"^\[(?P<tag>"
    r"task-input-validation"
    r"|trigger-evaluation"
    r"|precondition-check: [^\]]+"
    r"|skill-output: [^\]]+"
    r"|output-validation: [^\]]+"
    r"|loop-detected: [^\]]+"
    r"|skill-deactivation: [^\]]+"
    r")\]\s*$"
)
HEADING_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$", re.MULTILINE)
FIELD_RE_TEMPLATE = r"(^|\n)\s*{field}\s*:"


@dataclass(frozen=True)
class SkillDocumentCheck:
    skill: str
    family: str
    required_sections: tuple[str, ...]
    present_sections: tuple[str, ...]
    missing_sections: tuple[str, ...]
    has_legacy_contract: bool


@dataclass(frozen=True)
class ProtocolBlock:
    kind: str
    skill: str | None
    raw_tag: str
    start_line: int
    end_line: int
    body: str


@dataclass(frozen=True)
class ProtocolValidationResult:
    blocks: tuple[ProtocolBlock, ...]
    issues: tuple[str, ...]
    active_skills_left: tuple[str, ...]
    budget_violations: tuple[str, ...]
    missing_family_fields: tuple[str, ...]
    status: str


def skill_family(skill: str) -> str:
    return SKILL_FAMILY[skill]


def required_sections_for_skill(skill: str) -> tuple[str, ...]:
    return SKILL_REQUIRED_SECTIONS[skill]


def collect_skill_document_checks(skills_dir: Path) -> list[SkillDocumentCheck]:
    checks: list[SkillDocumentCheck] = []
    for skill in sorted(SKILL_FAMILY):
        skill_file = skills_dir / skill / "SKILL.md"
        if not skill_file.exists():
            continue
        checks.append(inspect_skill_document(skill, skill_file))
    return checks


def inspect_skill_document(skill: str, path: Path) -> SkillDocumentCheck:
    text = path.read_text(encoding="utf-8")
    present = tuple(match.group("title").strip() for match in HEADING_RE.finditer(text))
    present_set = {title.lower() for title in present}
    required = required_sections_for_skill(skill)
    missing = tuple(section for section in required if section.lower() not in present_set)
    return SkillDocumentCheck(
        skill=skill,
        family=skill_family(skill),
        required_sections=required,
        present_sections=present,
        missing_sections=missing,
        has_legacy_contract="# Input Contract" in text or "# Output Contract" in text,
    )


def validate_protocol_text(text: str) -> ProtocolValidationResult:
    blocks = tuple(_extract_protocol_blocks(text))
    issues: list[str] = []
    active_skills: set[str] = set()
    budget_violations: list[str] = []
    missing_family_fields: list[str] = []

    if not blocks:
        return ProtocolValidationResult(
            blocks=(),
            issues=("No Skill Protocol v1 blocks detected in output.",),
            active_skills_left=(),
            budget_violations=(),
            missing_family_fields=(),
            status="fail",
        )

    indices_by_kind: dict[str, list[int]] = {}
    for index, block in enumerate(blocks):
        indices_by_kind.setdefault(block.kind, []).append(index)
        issues.extend(_validate_block_fields(block))

    if "task-input-validation" not in indices_by_kind:
        issues.append("Missing required block [task-input-validation].")
    if "trigger-evaluation" not in indices_by_kind:
        issues.append("Missing required block [trigger-evaluation].")
    if (
        "task-input-validation" in indices_by_kind
        and "trigger-evaluation" in indices_by_kind
        and indices_by_kind["task-input-validation"][0] > indices_by_kind["trigger-evaluation"][0]
    ):
        issues.append("[task-input-validation] must appear before [trigger-evaluation].")

    output_indices_by_skill: dict[str, list[int]] = {}
    validation_indices_by_skill: dict[str, list[int]] = {}
    deactivation_indices_by_skill: dict[str, list[int]] = {}
    precondition_indices_by_skill: dict[str, list[int]] = {}

    for index, block in enumerate(blocks):
        if block.kind == "precondition-check" and block.skill:
            precondition_indices_by_skill.setdefault(block.skill, []).append(index)
            if block.skill not in active_skills:
                active_skills.add(block.skill)
                budget_violations.extend(_validate_family_budgets(active_skills))
        elif block.kind == "skill-output" and block.skill:
            output_indices_by_skill.setdefault(block.skill, []).append(index)
            missing_family_fields.extend(_validate_skill_output_fields(block))
        elif block.kind == "output-validation" and block.skill:
            validation_indices_by_skill.setdefault(block.skill, []).append(index)
        elif block.kind == "skill-deactivation" and block.skill:
            deactivation_indices_by_skill.setdefault(block.skill, []).append(index)
            active_skills.discard(block.skill)

    for skill, output_indices in output_indices_by_skill.items():
        for output_index in output_indices:
            if not any(idx < output_index for idx in precondition_indices_by_skill.get(skill, [])):
                issues.append(f"[skill-output: {skill}] is missing a preceding [precondition-check: {skill}].")
            if not any(idx > output_index for idx in validation_indices_by_skill.get(skill, [])):
                issues.append(f"[skill-output: {skill}] is missing a matching [output-validation: {skill}].")
            if not any(idx > output_index for idx in deactivation_indices_by_skill.get(skill, [])):
                issues.append(f"[skill-output: {skill}] is missing a trailing [skill-deactivation: {skill}].")

    active_skills_left = tuple(sorted(active_skills))
    if active_skills_left:
        issues.append(
            "Skills left active without explicit deactivation: "
            + ", ".join(active_skills_left)
        )

    issues.extend(budget_violations)
    issues.extend(missing_family_fields)
    status = "pass" if not issues else "fail"
    return ProtocolValidationResult(
        blocks=blocks,
        issues=tuple(issues),
        active_skills_left=active_skills_left,
        budget_violations=tuple(budget_violations),
        missing_family_fields=tuple(missing_family_fields),
        status=status,
    )


def _extract_protocol_blocks(text: str) -> list[ProtocolBlock]:
    lines = text.splitlines()
    blocks: list[ProtocolBlock] = []
    line_index = 0
    while line_index < len(lines):
        stripped = lines[line_index].strip()
        match = BLOCK_START_RE.match(stripped)
        if not match:
            line_index += 1
            continue
        raw_tag = match.group("tag")
        closing = f"[/{raw_tag}]"
        body_lines: list[str] = []
        end_index = line_index
        probe = line_index + 1
        while probe < len(lines):
            if lines[probe].strip() == closing:
                end_index = probe
                break
            body_lines.append(lines[probe])
            probe += 1
        else:
            end_index = len(lines) - 1
            probe = len(lines)

        kind, skill = _parse_block_tag(raw_tag)
        blocks.append(
            ProtocolBlock(
                kind=kind,
                skill=skill,
                raw_tag=raw_tag,
                start_line=line_index + 1,
                end_line=end_index + 1,
                body="\n".join(body_lines).strip(),
            )
        )
        line_index = probe + 1
    return blocks


def _parse_block_tag(raw_tag: str) -> tuple[str, str | None]:
    if ": " not in raw_tag:
        return raw_tag, None
    kind, skill = raw_tag.split(": ", 1)
    return kind, skill.strip()


def _validate_block_fields(block: ProtocolBlock) -> list[str]:
    fields = STANDARD_BLOCK_FIELDS.get(block.kind, ())
    issues: list[str] = []
    for field in fields:
        pattern = FIELD_RE_TEMPLATE.format(field=re.escape(field))
        if not re.search(pattern, block.body, re.MULTILINE):
            issues.append(f"[{block.raw_tag}] is missing field `{field}`.")
    return issues


def _validate_skill_output_fields(block: ProtocolBlock) -> list[str]:
    if not block.skill or block.skill not in SKILL_OUTPUT_FIELDS:
        return []
    issues: list[str] = []
    for field in SKILL_OUTPUT_FIELDS[block.skill]:
        pattern = FIELD_RE_TEMPLATE.format(field=re.escape(field))
        if not re.search(pattern, block.body, re.MULTILINE):
            issues.append(f"[skill-output: {block.skill}] is missing family field `{field}`.")
    return issues


def _validate_family_budgets(active_skills: set[str]) -> list[str]:
    issues: list[str] = []
    execution_active = sorted(skill for skill in active_skills if SKILL_FAMILY.get(skill) == "execution")
    orchestration_active = sorted(skill for skill in active_skills if SKILL_FAMILY.get(skill) == "orchestration")
    primary_phase_active = sorted(
        skill for skill in active_skills if skill in PHASE_SKILLS and skill != "phase-contract-tools"
    )
    contract_tool_active = "phase-contract-tools" in active_skills

    if len(execution_active) > 4:
        issues.append(
            "Execution family budget exceeded: "
            + ", ".join(execution_active)
        )
    if len(orchestration_active) > 1:
        issues.append(
            "Orchestration family budget exceeded: "
            + ", ".join(orchestration_active)
        )
    if len(primary_phase_active) > 1:
        issues.append(
            "Primary phase family budget exceeded: "
            + ", ".join(primary_phase_active)
        )
    if contract_tool_active and len(primary_phase_active) > 1:
        issues.append(
            "`phase-contract-tools` may coexist with at most one primary phase skill."
        )

    return issues
