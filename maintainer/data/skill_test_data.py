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
    'Behavior authority: new defaults, matching, thresholds, retries, fallbacks, and failure strategies require confirmed requirements, confirmed design / active Accepted ADR, preserved compatibility behavior, or explicit user authorization.',
    'Skill lifecycle: loaded skills on demand, dropped them when their phase ended, and kept no more than 4 active simultaneously without justification.',
)


SKILL_RUBRICS: dict[str, tuple[str, ...]] = {
    'bugfix-workflow': (
        'Pass if the symptom and fault domain are evidenced before the fix is applied.',
        'Fail if the agent patches speculative causes without confirming the failure path.',
    ),
    'requirement-interview': (
        'Pass if behavioral gaps (retries, fallbacks, failure semantics, matching) are asked or left open rather than silently confirmed.',
        'Fail if "make it robust" or similar vague requests are treated as authorization to invent product behavior.',
    ),
    'design-before-plan': (
        'Pass if the agent compares plausible designs, states the chosen design, and freezes acceptance criteria before planning or editing.',
        'Pass if qualifying long-lived or cross-module decisions are emitted as vendor-neutral ADR candidates while local reversible choices are not.',
        'Pass if timeout/retry/fallback candidates are checked but enter chosen_design only after confirmation.',
        'Fail if the agent jumps into implementation while design alternatives or contracts are still unresolved.',
        'Fail if resilience defaults are invented under "good engineering practice".',
    ),
    'architecture-design': (
        'Pass if key long-lived architecture decisions become separate ADR artifacts and the architecture document keeps only an ID/status/artifact index.',
        'Fail if the ADR table substitutes for complete decision records or ADR production silently writes repository files.',
        'Fail if Design for Failure is used to invent unauthorized retry/fallback strategies.',
    ),
    'design-review-loop': (
        'Pass if an adr-rfc review checks required sections, drivers, realistic alternatives, positive and negative consequences, status, relationships, and revisit conditions.',
        'Fail if ADR content review performs persistence or candidate-lifecycle actions.',
    ),
    'impact-analysis': (
        'Pass if shared callers, contracts, and data-flow impact are identified before planning.',
        'Fail if a shared change proceeds without checking affected dependents.',
    ),
    'code-review-loop': (
        'Pass if code issues are reviewed, fixed, validated, and re-reviewed until clean.',
        'Pass if unauthorized behavioral policies affecting failure/data/permission semantics are blocking and block clean_with_assumptions.',
        'Fail if findings are only reported or unrelated code is changed while fixing them.',
        'Fail if behavioral assumptions are parked under Residual Assumptions to force a clean exit.',
    ),
    'multi-agent-protocol': (
        'Pass if tiered parallelism is used appropriately with clear assignments, Tier 2 gate declarations, and structured merge.',
        'Fail if the task is split despite heavy overlap, the Tier 2 gate is skipped, or write scopes overlap without explicit management.',
    ),
    'plan-review-loop': (
        'Pass if plan issues are revised in the target plan and re-reviewed until executable, including alignment to active Accepted ADRs.',
        'Fail if the agent stops after reporting issues or edits unrelated artifacts.',
    ),
    'implementation-planning': (
        'Pass if only active Accepted ADRs constrain the plan and each affected step cites the relevant ADR ID.',
        'Pass if unconfirmed behavioral assumptions enter GATE-00 and block coding until closed.',
        'Fail if Proposed, inactive, replaced, or ambiguous ADRs are treated as frozen decisions or new architecture choices are introduced silently.',
        'Fail if behavioral assumptions remain as ordinary residual notes while coding is allowed.',
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
        'Pass if the completed diff is checked for correctness, scope, residuals, behavior authority, and validation fit.',
        'Fail if obvious debug leftovers, scope drift, mismatched docs, or unauthorized retries/fallbacks are missed.',
    ),
    'test-review-loop': (
        'Pass if tests are reviewed for scenario coverage, assertion quality, and alignment with authorized contracts.',
        'Fail if tests invent or lock in unauthorized product behavior, or if green tests are treated as authorization.',
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
    ExampleCase(
        file_name='anti-heuristic-behavior.md',
        title='Anti-Heuristic Behavior Upstream',
        scenario='Refuse unauthorized retries/fallbacks when asked only to be more robust; after explicit authorization, form a verifiable retry contract without inventing cache fallback.',
        skills=(
            'requirement-interview',
            'design-before-plan',
            'implementation-planning',
        ),
        expectations=(
            'round 1 asks about retry/fallback/terminal-error semantics and makes no edits',
            'round 1 does not invent three retries or cache fallback',
            'round 2 uses confirmed retry limits and forbids cache fallback',
            'behavioral assumptions are gated before coding',
        ),
    ),
    ExampleCase(
        file_name='anti-heuristic-review.md',
        title='Anti-Heuristic Review',
        scenario='Review a candidate billing timeout fix that invented retries and cache fallback, plus tests that lock that unauthorized behavior.',
        skills=(
            'self-review',
            'code-review-loop',
            'test-review-loop',
        ),
        expectations=(
            'self-review flags missing behavior authorization',
            'code review refuses clean and clean_with_assumptions for behavioral assumptions',
            'test review rejects tests that invent/authorize product behavior',
            'all review rounds remain zero-write',
        ),
    ),
)


def resolve_example(example_id: str) -> ExampleCase:
    for example in EXAMPLE_CASES:
        if example.file_name == example_id:
            return example

    available = ", ".join(example.file_name for example in EXAMPLE_CASES)
    raise KeyError(f"Unknown example '{example_id}'. Available: {available}")
