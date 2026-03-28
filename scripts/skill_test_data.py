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
    "Scope discipline: stayed inside the smallest justified boundary.",
    "Planning discipline: stated assumptions, working set, and intended sequence before edits.",
    "Change discipline: preferred the smallest viable change or recommendation.",
    "Validation discipline: chose the narrowest meaningful check first.",
    "Uncertainty handling: preserved ambiguity and residual risk instead of overclaiming.",
    "Skill lifecycle: loaded skills on demand, dropped them when their phase ended, and kept no more than 4 active simultaneously without justification.",
)


SKILL_RUBRICS: dict[str, tuple[str, ...]] = {
    "scoped-tasking": (
        "Pass if the agent proposes a bounded initial working set and explains each scope expansion.",
        "Fail if the agent drifts into broad repository exploration without evidence.",
    ),
    "plan-before-action": (
        "Pass if the goal, assumptions, intended files, and next actions are stated before non-trivial edits.",
        "Fail if editing starts while the plan or file list is still fuzzy.",
    ),
    "minimal-change-strategy": (
        "Pass if the chosen patch is local, reviewable, and avoids unrelated cleanup.",
        "Fail if the task is bundled with opportunistic refactors or cosmetic rewrites.",
    ),
    "targeted-validation": (
        "Pass if the first validation step is directly tied to the changed surface.",
        "Fail if the agent defaults to broad suites without explicit risk justification.",
    ),
    "context-budget-awareness": (
        "Pass if stale hypotheses are dropped and the session is compressed into a clear current-state summary.",
        "Fail if old dead ends continue to drive reading, reasoning, or validation.",
    ),
    "read-and-locate": (
        "Pass if the strongest clue is used first and likely edit points are identified without repo-wide drift.",
        "Fail if the agent reads large unrelated areas before mapping the local path.",
    ),
    "safe-refactor": (
        "Pass if invariants are stated and the refactor proceeds in behavior-preserving small steps.",
        "Fail if the refactor silently changes interfaces, outputs, or error behavior.",
    ),
    "bugfix-workflow": (
        "Pass if the symptom and fault domain are evidenced before the fix is applied.",
        "Fail if the agent patches speculative causes without confirming the failure path.",
    ),
    "multi-agent-protocol": (
        "Pass if tiered parallelism is used appropriately with clear assignments, Tier 2 gate declarations, and structured merge.",
        "Fail if the task is split despite heavy overlap, the Tier 2 gate is skipped, or write scopes overlap without explicit management.",
    ),
    "conflict-resolution": (
        "Pass if overlapping findings are compared by evidence quality and uncertainty is preserved.",
        "Fail if conflicting findings are flattened into one answer without adjudication.",
    ),
    "phase-plan": (
        "Pass if the execution schema is the authority and the strict four-file doc set is produced with validators run.",
        "Fail if Markdown redefines YAML-owned fields, extra planning docs are created, or validators are skipped.",
    ),
    "phase-execute": (
        "Pass if execution reads from the accepted schema, respects lane isolation, and reports wave state per contract.",
        "Fail if the agent reopens planning during execution, paraphrases lane contracts, or skips validation.",
    ),
    "phase-contract-tools": (
        "Pass if contract authority stays centralized and smoke checks pass after any script change.",
        "Fail if contract rules are duplicated in sibling skills or golden files drift without update.",
    ),
}


EXAMPLE_CASES: tuple[ExampleCase, ...] = (
    ExampleCase(
        file_name="single-agent-bugfix.md",
        title="Single-Agent Bugfix",
        scenario="Diagnose a bounded bug, plan before editing, apply the smallest viable fix, and validate narrowly.",
        skills=(
            "scoped-tasking",
            "plan-before-action",
            "bugfix-workflow",
            "minimal-change-strategy",
            "targeted-validation",
        ),
        expectations=(
            "symptom is stated clearly before edits",
            "fault domain is narrowed before patching",
            "the fix stays local",
            "validation targets only the affected path",
        ),
    ),
    ExampleCase(
        file_name="read-and-locate.md",
        title="Read and Locate",
        scenario="Discover the likely edit points in an unfamiliar codebase without drifting into a repo-wide scan.",
        skills=(
            "scoped-tasking",
            "read-and-locate",
            "plan-before-action",
        ),
        expectations=(
            "the strongest clue is used first",
            "discovery stays near the entry point",
            "likely edit points are identified explicitly",
        ),
    ),
    ExampleCase(
        file_name="safe-refactor.md",
        title="Safe Refactor",
        scenario="Extract duplicated logic while preserving signatures, output shape, and existing behavior.",
        skills=(
            "scoped-tasking",
            "read-and-locate",
            "plan-before-action",
            "safe-refactor",
            "targeted-validation",
        ),
        expectations=(
            "invariants are stated before refactoring",
            "the refactor proceeds in small steps",
            "validation follows meaningful structural changes",
        ),
    ),
    ExampleCase(
        file_name="context-budgeted-debugging.md",
        title="Context-Budgeted Debugging",
        scenario="Recover from a noisy debugging session by compressing state, dropping stale hypotheses, and resuming inside a smaller fault domain.",
        skills=(
            "context-budget-awareness",
            "bugfix-workflow",
            "scoped-tasking",
            "targeted-validation",
        ),
        expectations=(
            "stale hypotheses are removed",
            "the session is compressed into a short current-state summary",
            "the next step targets the remaining uncertainty",
        ),
    ),
    ExampleCase(
        file_name="multi-agent-root-cause-analysis.md",
        title="Multi-Agent Root Cause Analysis",
        scenario="Split a low-coupling investigation into parallel lines of analysis, merge evidence, and preserve uncertainty before recommending action.",
        skills=(
            "scoped-tasking",
            "plan-before-action",
            "multi-agent-protocol",
            "conflict-resolution",
            "targeted-validation",
        ),
        expectations=(
            "parallel work is justified explicitly",
            "subtasks are clearly separated",
            "findings are merged without collapsing uncertainty too early",
        ),
    ),
    ExampleCase(
        file_name="phased-migration-planning.md",
        title="Phased Migration Planning",
        scenario="Break a cross-service database schema migration into a phased execution plan with wave sequencing, hotspot ownership, and schema-first doc set.",
        skills=(
            "phase-plan",
            "phase-contract-tools",
            "scoped-tasking",
            "plan-before-action",
        ),
        expectations=(
            "phase1-plan.yaml is the execution authority, not Markdown",
            "the strict four-file doc set is produced without extra planning docs",
            "validators run immediately after YAML is produced",
            "hotspot ownership is explicit in the plan",
        ),
    ),
)


EXAMPLE_CASES_BY_FILE: dict[str, ExampleCase] = {case.file_name: case for case in EXAMPLE_CASES}
ALL_SKILLS: tuple[str, ...] = tuple(sorted(SKILL_RUBRICS))


def resolve_example(identifier: str) -> ExampleCase:
    for case in EXAMPLE_CASES:
        if identifier == case.file_name or identifier == case.title:
            return case
    available = ", ".join(case.file_name for case in EXAMPLE_CASES)
    raise KeyError(f"Unknown example '{identifier}'. Available examples: {available}")
