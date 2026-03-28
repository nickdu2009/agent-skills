#!/usr/bin/env python3
"""Trigger test matrix for evaluating skill triggerability.

Each TriggerCase pairs a simulated user prompt with the skills that
should (and should NOT) be triggered.  The matrix covers three risk
areas:

1. Post-rewrite trigger accuracy — do new descriptions still match the
   right user intents?
2. AGENTS.md vs full-skill boundary — do short/simple tasks stay at the
   AGENTS.md level while complex tasks escalate to the full skill?
3. Chain and library triggers — do internal skills (conflict-resolution,
   phase-contract-tools) only activate through their intended entry
   points?
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TriggerCase:
    id: str
    prompt: str
    expected_triggers: tuple[str, ...]
    expected_non_triggers: tuple[str, ...]
    category: str
    notes: str


# ---------------------------------------------------------------------------
# Category 1: Task-type triggers (direct user intent → skill)
# ---------------------------------------------------------------------------

TASK_TYPE_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id="bug-explicit",
        prompt="The login page returns a 500 error when users type a special character in the password field.",
        expected_triggers=("bugfix-workflow",),
        expected_non_triggers=("safe-refactor", "phase-plan"),
        category="task-type",
        notes="Explicit bug report with symptom. bugfix-workflow should trigger immediately.",
    ),
    TriggerCase(
        id="bug-implicit",
        prompt="Something is wrong with the invoice export — it hangs for about 30 seconds before timing out.",
        expected_triggers=("bugfix-workflow",),
        expected_non_triggers=("safe-refactor",),
        category="task-type",
        notes="Implicit bug (symptom without the word 'bug'). Tests keyword coverage beyond literal 'bug'.",
    ),
    TriggerCase(
        id="refactor-explicit",
        prompt="Extract the duplicate request-normalization logic from three handlers into a shared helper.",
        expected_triggers=("safe-refactor",),
        expected_non_triggers=("bugfix-workflow",),
        category="task-type",
        notes="Explicit refactor request. safe-refactor should trigger; bugfix-workflow should not.",
    ),
    TriggerCase(
        id="feature-not-bug",
        prompt="Add a dark mode toggle to the settings page.",
        expected_triggers=(),
        expected_non_triggers=("bugfix-workflow", "safe-refactor"),
        category="task-type",
        notes="Pure additive feature. Neither bugfix nor refactor skills should trigger.",
    ),
)


# ---------------------------------------------------------------------------
# Category 2: AGENTS.md boundary (short tasks stay at AGENTS.md level)
# ---------------------------------------------------------------------------

BOUNDARY_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id="simple-one-file-fix",
        prompt="Change the return status from 500 to 404 in the profile handler.",
        expected_triggers=(),
        expected_non_triggers=("plan-before-action", "scoped-tasking", "minimal-change-strategy"),
        category="agents-md-boundary",
        notes="Tiny single-file fix. AGENTS.md rules suffice. No skill should be loaded.",
    ),
    TriggerCase(
        id="multi-file-uncertain",
        prompt="Add retry logic to the payment service — I'm not sure if the retry config lives in the service layer or the client wrapper, and the tests will need updating too.",
        expected_triggers=("plan-before-action",),
        expected_non_triggers=(),
        category="agents-md-boundary",
        notes="3+ files, uncertainty about structure. plan-before-action should trigger.",
    ),
    TriggerCase(
        id="broad-request-small-surface",
        prompt="Look into the performance issues across the reporting, billing, and notification systems — users say the daily summary email is slow.",
        expected_triggers=("scoped-tasking",),
        expected_non_triggers=(),
        category="agents-md-boundary",
        notes="Broad request but likely narrow edit surface. scoped-tasking should narrow it down.",
    ),
    TriggerCase(
        id="temptation-to-cleanup",
        prompt="Fix the date parsing bug in the import adapter. The surrounding code is pretty messy but let's not touch it right now.",
        expected_triggers=("bugfix-workflow",),
        expected_non_triggers=("safe-refactor",),
        category="agents-md-boundary",
        notes="Bug fix with explicit don't-clean-up instruction. AGENTS.md Change Rules handle the cleanup restraint; minimal-change-strategy is optional.",
    ),
    TriggerCase(
        id="diff-growing-beyond-task",
        prompt="I asked you to fix the null check, but the diff now includes 4 renamed functions and reformatted imports. Can you undo the extra changes?",
        expected_triggers=("minimal-change-strategy",),
        expected_non_triggers=(),
        category="agents-md-boundary",
        notes="Diff grew beyond task. This is when minimal-change-strategy adds value beyond AGENTS.md.",
    ),
    TriggerCase(
        id="what-to-test-after-patch",
        prompt="I just fixed the CSV import adapter. What's the right way to test this without running the full 20-minute integration suite?",
        expected_triggers=("targeted-validation",),
        expected_non_triggers=(),
        category="agents-md-boundary",
        notes="Explicit validation question. targeted-validation should trigger.",
    ),
    TriggerCase(
        id="simple-test-request",
        prompt="Run the tests for this file.",
        expected_triggers=(),
        expected_non_triggers=("targeted-validation",),
        category="agents-md-boundary",
        notes="Simple command. AGENTS.md Validation Rules suffice.",
    ),
)


# ---------------------------------------------------------------------------
# Category 3: Discovery and navigation triggers
# ---------------------------------------------------------------------------

DISCOVERY_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id="unfamiliar-codebase",
        prompt="I need to change how invoices are generated but I'm not sure where that code lives.",
        expected_triggers=("read-and-locate",),
        expected_non_triggers=(),
        category="discovery",
        notes="Agent doesn't know where to edit. read-and-locate should trigger.",
    ),
    TriggerCase(
        id="known-file",
        prompt="Fix the typo on line 42 of src/utils/format.ts.",
        expected_triggers=(),
        expected_non_triggers=("read-and-locate", "scoped-tasking"),
        category="discovery",
        notes="Exact file and line known. No discovery or scoping skill needed.",
    ),
    TriggerCase(
        id="partial-path-known",
        prompt="The rate limiter config is somewhere in the networking module but I don't know which file owns the per-endpoint limits.",
        expected_triggers=("read-and-locate",),
        expected_non_triggers=(),
        category="discovery",
        notes="Module known but exact file unknown. Boundary case: enough uncertainty to justify read-and-locate.",
    ),
    TriggerCase(
        id="grep-sufficient",
        prompt="Find all callers of the function validateOAuthToken and update the second argument from string to OAuthScope.",
        expected_triggers=(),
        expected_non_triggers=("read-and-locate",),
        category="discovery",
        notes="Exact function name provided. A grep/find-references operation suffices; read-and-locate adds no value.",
    ),
)


# ---------------------------------------------------------------------------
# Category 4: Context budget triggers (self-management)
# ---------------------------------------------------------------------------

CONTEXT_BUDGET_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id="long-session-refocus",
        prompt="We've been going back and forth on this for a while. Let's step back and figure out what we actually know so far.",
        expected_triggers=("context-budget-awareness",),
        expected_non_triggers=(),
        category="context-budget",
        notes="User signals session fatigue. context-budget-awareness should trigger.",
    ),
    TriggerCase(
        id="short-task-no-noise",
        prompt="Add a comment to the calculateTotal function.",
        expected_triggers=(),
        expected_non_triggers=("context-budget-awareness",),
        category="context-budget",
        notes="Trivial short task. No context management needed.",
    ),
    TriggerCase(
        id="many-files-opened",
        prompt="I've read through about 12 files trying to trace this logging issue and I still can't find the root cause. The error appears in the output but I can't connect it to any of the handlers I've checked.",
        expected_triggers=("context-budget-awareness",),
        expected_non_triggers=(),
        category="context-budget",
        notes="Working set exceeds 8 files without convergence. Matches the quantitative trigger threshold in context-budget-awareness.",
    ),
    TriggerCase(
        id="repeated-hypothesis",
        prompt="We already checked the cache layer twice and the queue config three times. Each time it looked fine. I'm not sure what else to try.",
        expected_triggers=("context-budget-awareness",),
        expected_non_triggers=(),
        category="context-budget",
        notes="Multiple re-reads of the same areas without progress. Matches the 'same file read more than twice' trigger.",
    ),
    TriggerCase(
        id="medium-session-focused",
        prompt="We've been working on this for a while but we're making steady progress. The auth middleware is fixed, now let's update the session expiry check in the same file.",
        expected_triggers=(),
        expected_non_triggers=("context-budget-awareness",),
        category="context-budget",
        notes="Medium-length session but focused and progressing. No context compression needed.",
    ),
)


# ---------------------------------------------------------------------------
# Category 5: Multi-agent and chain triggers
# ---------------------------------------------------------------------------

MULTI_AGENT_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id="parallel-investigation",
        prompt="Investigate the auth middleware, session storage, and role checking in parallel to understand the full auth flow.",
        expected_triggers=("multi-agent-protocol",),
        expected_non_triggers=("conflict-resolution",),
        category="multi-agent",
        notes="Explicit parallel request. multi-agent-protocol should trigger. conflict-resolution only after results conflict.",
    ),
    TriggerCase(
        id="implicit-parallel-opportunity",
        prompt="We need to understand the full payment flow: how the API handler validates requests, how the billing service calculates charges, and how the notification service sends receipts. These three areas are owned by different teams.",
        expected_triggers=("multi-agent-protocol",),
        expected_non_triggers=("conflict-resolution",),
        category="multi-agent",
        notes="No explicit 'parallel' keyword. Three independent, team-separated investigation areas imply parallelism. Tests whether the agent recognizes the opportunity from task structure alone.",
    ),
    TriggerCase(
        id="serial-single-file",
        prompt="Fix the off-by-one error in pkg/runtime/replay.go.",
        expected_triggers=(),
        expected_non_triggers=("multi-agent-protocol",),
        category="multi-agent",
        notes="Single-file fix. multi-agent-protocol should NOT trigger (exemption applies).",
    ),
    TriggerCase(
        id="conflicting-subagent-results",
        prompt="Two subagents disagree: one says the cache invalidation path is broken, the other blames clock skew in expiry logic. Which is right?",
        expected_triggers=("conflict-resolution",),
        expected_non_triggers=(),
        category="multi-agent",
        notes="Explicit conflicting findings. conflict-resolution should trigger even standalone.",
    ),
)


# ---------------------------------------------------------------------------
# Category 6: Phase system triggers
# ---------------------------------------------------------------------------

PHASE_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id="plan-large-migration",
        prompt="Break down this database migration into phases. We need sequenced waves with clear ownership so multiple agents can work in parallel.",
        expected_triggers=("phase-plan",),
        expected_non_triggers=("phase-contract-tools",),
        category="phase",
        notes="Large task needing phased execution. phase-plan should trigger; phase-contract-tools should NOT trigger standalone.",
    ),
    TriggerCase(
        id="execute-wave",
        prompt="Execute wave 2 of the phase 3 plan.",
        expected_triggers=("phase-execute",),
        expected_non_triggers=("phase-plan", "phase-contract-tools"),
        category="phase",
        notes="Explicit wave execution. phase-execute only.",
    ),
    TriggerCase(
        id="contract-tools-direct",
        prompt="Fix a validation error in the phase schema validator script.",
        expected_triggers=("phase-contract-tools",),
        expected_non_triggers=("phase-plan", "phase-execute"),
        category="phase",
        notes="Working on the tools themselves. Only case where phase-contract-tools should trigger directly.",
    ),
)


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

ALL_TRIGGER_CASES: tuple[TriggerCase, ...] = (
    *TASK_TYPE_CASES,
    *BOUNDARY_CASES,
    *DISCOVERY_CASES,
    *CONTEXT_BUDGET_CASES,
    *MULTI_AGENT_CASES,
    *PHASE_CASES,
)

ALL_TRIGGER_CASES_BY_ID: dict[str, TriggerCase] = {
    case.id: case for case in ALL_TRIGGER_CASES
}

CATEGORIES: tuple[str, ...] = (
    "task-type",
    "agents-md-boundary",
    "discovery",
    "context-budget",
    "multi-agent",
    "phase",
)


def cases_by_category(category: str) -> tuple[TriggerCase, ...]:
    return tuple(c for c in ALL_TRIGGER_CASES if c.category == category)


def resolve_trigger_case(identifier: str) -> TriggerCase:
    if identifier in ALL_TRIGGER_CASES_BY_ID:
        return ALL_TRIGGER_CASES_BY_ID[identifier]
    available = ", ".join(ALL_TRIGGER_CASES_BY_ID)
    raise KeyError(f"Unknown trigger case '{identifier}'. Available: {available}")
