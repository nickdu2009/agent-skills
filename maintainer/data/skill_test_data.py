#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExampleCase:
    file_name: str
    title: str
    scenario: str
    skills: tuple[str, ...]
    expectations: tuple[str, ...]


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
    'phase-contract-tools': (
        'Pass if contract authority stays centralized and smoke checks pass after any script change.',
        'Fail if contract rules are duplicated in sibling skills or golden files drift without update.',
    ),
    'phase-execute': (
        'Pass if execution reads from the accepted schema, respects lane isolation, and reports wave state per contract.',
        'Fail if the agent reopens planning during execution, paraphrases lane contracts, or skips validation.',
    ),
    'phase-plan': (
        'Pass if the execution schema is the authority, the per-phase strict four-file doc set is produced, the phase-root README is maintained, and validators run.',
        'Fail if Markdown redefines YAML-owned fields, extra phase-local planning docs are created, the phase-root README is missing, or validators are skipped.',
    ),
    'plan-before-action': (
        'Pass if the goal, assumptions, intended files, and next actions are stated before non-trivial edits.',
        'Fail if editing starts while the plan or file list is still fuzzy.',
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
            'plan-before-action',
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
            'plan-before-action',
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
            'plan-before-action',
            'multi-agent-protocol',
            'targeted-validation',
        ),
        expectations=(
            'parallel work is justified explicitly',
            'subtasks are clearly separated',
            'findings are merged without collapsing uncertainty too early',
        ),
    ),
    ExampleCase(
        file_name='phased-migration-planning.md',
        title='Phased Migration Planning',
        scenario='Break a cross-service database schema migration into a phased execution plan with wave sequencing, hotspot ownership, and schema-first doc set.',
        skills=(
            'phase-plan',
            'phase-contract-tools',
            'scoped-tasking',
            'plan-before-action',
        ),
        expectations=(
            'docs/phases/phase1/plan.yaml is the execution authority, not Markdown',
            'the per-phase strict four-file doc set is produced without extra phase-local planning docs',
            'docs/phases/README.md includes a concise summary for phase1',
            'validators run immediately after YAML is produced',
            'hotspot ownership is explicit in the plan',
        ),
    ),
)
