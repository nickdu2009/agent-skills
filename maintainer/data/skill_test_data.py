#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExampleCase:
    file_name: str
    title: str
    scenario: str
    skills: tuple[str, ...]
    expectations: tuple[str, ...]


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"

# Keep evaluation consumers aligned with the canonical skills tree.
ALL_SKILLS: tuple[str, ...] = tuple(
    sorted(skill_dir.name for skill_dir in SKILLS_DIR.iterdir() if (skill_dir / "SKILL.md").exists())
)


GLOBAL_RUBRIC_DIMENSIONS: tuple[str, ...] = (
    'Scope discipline: stayed inside the smallest justified boundary.',
    'Planning discipline: stated assumptions, working set, and intended sequence before edits.',
    'Change discipline: preferred the smallest viable change or recommendation.',
    'Validation discipline: chose the narrowest meaningful check first.',
    'Uncertainty handling: preserved ambiguity and residual risk instead of overclaiming.',
    'Skill lifecycle: loaded skills on demand, dropped them when their phase ended, and kept no more than 4 active simultaneously without justification.',
)


SKILL_RUBRICS: dict[str, tuple[str, ...]] = {
    'bugfix-workflow': (
        'Pass if the symptom and fault domain are evidenced before the fix is applied.',
        'Fail if the agent patches speculative causes without confirming the failure path.',
    ),
    'design-before-plan': (
        'Pass if the agent compares plausible designs, states the chosen design, and freezes acceptance criteria before planning or editing.',
        'Fail if the agent jumps into implementation while design alternatives or contracts are still unresolved.',
    ),
    'impact-analysis': (
        'Pass if shared callers, contracts, and data-flow impact are identified before planning.',
        'Fail if a shared change proceeds without checking affected dependents.',
    ),
    'code-review-loop': (
        'Pass if code issues are reviewed, fixed, validated, and re-reviewed until clean.',
        'Fail if findings are only reported or unrelated code is changed while fixing them.',
    ),
    'multi-agent-protocol': (
        'Pass if tiered parallelism is used appropriately with clear assignments, Tier 2 gate declarations, and structured merge.',
        'Fail if the task is split despite heavy overlap, the Tier 2 gate is skipped, or write scopes overlap without explicit management.',
    ),
    'plan-review-loop': (
        'Pass if plan issues are revised in the target plan and re-reviewed until executable.',
        'Fail if the agent stops after reporting issues or edits unrelated artifacts.',
    ),
    'safe-refactor': (
        'Pass if invariants are stated and the refactor proceeds in behavior-preserving small steps.',
        'Fail if the refactor silently changes interfaces, outputs, or error behavior.',
    ),
    'scoped-tasking': (
        'Pass if the agent proposes a bounded initial working set and explains each scope expansion.',
        'Fail if the agent drifts into broad repository exploration without evidence.',
    ),
    'self-review': (
        'Pass if the completed diff is checked for correctness, scope, residuals, and validation fit.',
        'Fail if obvious debug leftovers, scope drift, or mismatched docs are missed.',
    ),
    'targeted-validation': (
        'Pass if the first validation step is directly tied to the changed surface.',
        'Fail if the agent defaults to broad suites without explicit risk justification.',
    ),
}


EXAMPLE_CASES: tuple[ExampleCase, ...] = (
    ExampleCase(
        file_name='single-agent-bugfix.md',
        title='Single-Agent Bugfix',
        scenario='Diagnose a bounded bug, plan before editing, apply the smallest viable fix, and validate narrowly.',
        skills=(
            'scoped-tasking',
            'bugfix-workflow',
            'targeted-validation',
        ),
        expectations=(
            'symptom is stated clearly before edits',
            'fault domain is narrowed before patching',
            'the fix stays local',
            'validation targets only the affected path',
        ),
    ),
    ExampleCase(
        file_name='safe-refactor.md',
        title='Safe Refactor',
        scenario='Extract duplicated logic while preserving signatures, output shape, and existing behavior.',
        skills=(
            'scoped-tasking',
            'safe-refactor',
            'targeted-validation',
        ),
        expectations=(
            'invariants are stated before refactoring',
            'the refactor proceeds in small steps',
            'validation follows meaningful structural changes',
        ),
    ),
    ExampleCase(
        file_name='multi-agent-root-cause-analysis.md',
        title='Multi-Agent Root Cause Analysis',
        scenario='Split a low-coupling investigation into parallel lines of analysis, merge evidence, and preserve uncertainty before recommending action.',
        skills=(
            'scoped-tasking',
            'multi-agent-protocol',
            'targeted-validation',
        ),
        expectations=(
            'parallel work is justified explicitly',
            'subtasks are clearly separated',
            'findings are merged without collapsing uncertainty too early',
        ),
    ),
)


def resolve_example(example_id: str) -> ExampleCase:
    for example in EXAMPLE_CASES:
        if example.file_name == example_id:
            return example

    available = ", ".join(example.file_name for example in EXAMPLE_CASES)
    raise KeyError(f"Unknown example '{example_id}'. Available: {available}")
