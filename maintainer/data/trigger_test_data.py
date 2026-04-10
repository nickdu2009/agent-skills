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
    TriggerCase(
        id="bug-production-critical",
        prompt="Users can't log in! The auth service is returning 401 for every request since 10 minutes ago. We need to fix this immediately.",
        expected_triggers=("bugfix-workflow",),
        expected_non_triggers=("safe-refactor", "design-before-plan"),
        category="task-type",
        notes="High-urgency production incident. bugfix-workflow should trigger; no time for design or refactoring.",
    ),
    TriggerCase(
        id="refactor-frontend",
        prompt="Extract the user profile display logic from the Dashboard component into a reusable ProfileCard component. Keep the same props interface.",
        expected_triggers=("safe-refactor",),
        expected_non_triggers=("bugfix-workflow",),
        category="task-type",
        notes="Frontend component extraction refactor. safe-refactor should trigger for structural cleanup.",
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
    TriggerCase(
        id="ambiguous-requirement",
        prompt="Make the system faster.",
        expected_triggers=("scoped-tasking",),
        expected_non_triggers=(),
        category="agents-md-boundary",
        notes="Extremely vague requirement. scoped-tasking should trigger and its Step 0 should fire clarification questions.",
    ),
    TriggerCase(
        id="irreversible-operation",
        prompt="Drop the legacy_users table and migrate all data to the new users table.",
        expected_triggers=("plan-before-action",),
        expected_non_triggers=(),
        category="agents-md-boundary",
        notes="Irreversible database operation. plan-before-action should trigger to ensure a staged plan before destructive changes.",
    ),
    TriggerCase(
        id="validation-failure-diagnosis",
        prompt="The checkout integration test failed after my change. I could re-run the full suite, run just the checkout unit tests, or manually test the payment step. What should I do first to narrow it down?",
        expected_triggers=("targeted-validation",),
        expected_non_triggers=(),
        category="agents-md-boundary",
        notes="Multiple validation options after a failure. targeted-validation should trigger to select the cheapest diagnostic path.",
    ),
    TriggerCase(
        id="minimal-competing-strategies",
        prompt="I need to add input sanitization to the form handler. I could modify the handler directly, add a middleware, or use a decorator. Each approach touches different files. Which is the smallest safe change?",
        expected_triggers=("minimal-change-strategy",),
        expected_non_triggers=(),
        category="agents-md-boundary",
        notes="Multiple edit strategies competing. minimal-change-strategy should trigger to select the smallest viable approach.",
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
    TriggerCase(
        id="context-multi-hypothesis",
        prompt="The login failure could be a database connection timeout, a Redis session expiry bug, an OAuth token validation issue, or a firewall rule blocking the callback. I haven't gathered evidence to rule any of them out yet.",
        expected_triggers=("context-budget-awareness",),
        expected_non_triggers=(),
        category="context-budget",
        notes="4 active hypotheses without evidence ranking. Matches the '3+ hypotheses active without ranking evidence' trigger.",
    ),
    TriggerCase(
        id="context-stalled-actions",
        prompt="I just read auth.ts again — nothing new. Then I checked the session log — no relevant errors. Then I re-read auth.ts a third time and still have no leads. I feel like I'm going in circles.",
        expected_triggers=("context-budget-awareness",),
        expected_non_triggers=(),
        category="context-budget",
        notes="Last 3+ actions did not advance the stated objective. Matches the 'last 3 actions did not advance' trigger.",
    ),
    TriggerCase(
        id="context-7-files-no-trigger",
        prompt="I've looked at 7 files so far tracing this request path. I think I'm getting close — the middleware chain is auth.ts, session.ts, rate-limit.ts, cors.ts, logger.ts, validator.ts, and router.ts.",
        expected_triggers=(),
        expected_non_triggers=("context-budget-awareness",),
        category="context-budget",
        notes="7 files is below the 8-file threshold. context-budget-awareness should NOT trigger while still making progress.",
    ),
    TriggerCase(
        id="context-9-files-trigger",
        prompt="I've now read through 9 files tracing this request lifecycle and I'm still not sure where the latency spike originates. Each file I open raises new questions.",
        expected_triggers=("context-budget-awareness",),
        expected_non_triggers=(),
        category="context-budget",
        notes="9 files exceeds the 8-file threshold without convergence. context-budget-awareness SHOULD trigger.",
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
    TriggerCase(
        id="conflicting-hypotheses",
        prompt="The payment timeout could be caused by network latency or a database deadlock. Both explanations fit the logs equally well but they lead to completely different fixes. How do I decide?",
        expected_triggers=("conflict-resolution",),
        expected_non_triggers=(),
        category="multi-agent",
        notes="Two competing hypotheses with equal evidence. conflict-resolution should trigger for arbitration.",
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
        id="review-phase-plan",
        prompt="Review the accepted phase 2 plan before execution starts. I need blocking issues, alignment findings, and an approval decision.",
        expected_triggers=("phase-plan-review",),
        expected_non_triggers=("phase-plan", "phase-execute", "phase-contract-tools"),
        category="phase",
        notes="Plan review before execution. phase-plan-review should trigger on its own.",
    ),
    TriggerCase(
        id="contract-tools-direct",
        prompt="Fix a validation error in the phase schema validator script.",
        expected_triggers=("phase-contract-tools",),
        expected_non_triggers=("phase-plan", "phase-execute"),
        category="phase",
        notes="Working on the tools themselves. Only case where phase-contract-tools should trigger directly.",
    ),
    TriggerCase(
        id="phase-review-not-needed",
        prompt="Review my one-file change to the user profile handler before I run tests.",
        expected_triggers=(),
        expected_non_triggers=("phase-plan-review", "phase-plan"),
        category="phase",
        notes="Small single-file review. self-review may apply but phase-plan-review should NOT trigger for non-phase work.",
    ),
)


# ---------------------------------------------------------------------------
# Category 7: Pre-phase skill triggers
# ---------------------------------------------------------------------------

PRE_PHASE_CASES: tuple[TriggerCase, ...] = (
    # --- design-before-plan ---
    TriggerCase(
        id="design-multiple-approaches",
        prompt="Add caching to the product recommendation engine. We could use Redis, Memcached, or an in-memory LRU cache. Each has different trade-offs for our scale and consistency requirements.",
        expected_triggers=("design-before-plan",),
        expected_non_triggers=("plan-before-action",),
        category="pre-phase",
        notes="Multiple implementation approaches with explicit trade-offs. design-before-plan should trigger to compare alternatives before planning.",
    ),
    TriggerCase(
        id="design-api-contract",
        prompt="Design a new webhook API for third-party integrations. We need to define the payload format, authentication scheme, retry semantics, and versioning strategy before implementation.",
        expected_triggers=("design-before-plan",),
        expected_non_triggers=("plan-before-action",),
        category="pre-phase",
        notes="Public API design with contract decisions. design-before-plan should trigger to establish interface contracts.",
    ),
    TriggerCase(
        id="design-unclear-acceptance",
        prompt="Make the checkout flow faster. Users are complaining but we don't have specific performance targets or clear success criteria yet.",
        expected_triggers=("design-before-plan",),
        expected_non_triggers=("scoped-tasking",),
        category="pre-phase",
        notes="Missing acceptance criteria. design-before-plan should trigger to establish measurable criteria before planning.",
    ),
    TriggerCase(
        id="design-cross-module-contract",
        prompt="Refactor the authentication layer to support both session-based and token-based auth. This will change the interface between the auth module, API handlers, and frontend.",
        expected_triggers=("design-before-plan",),
        expected_non_triggers=(),
        category="pre-phase",
        notes="Cross-module contract change. design-before-plan should trigger to define interface contracts.",
    ),
    TriggerCase(
        id="design-not-needed-clear-path",
        prompt="Add a new field 'emailVerified' (boolean) to the User model and display it on the admin dashboard user detail page.",
        expected_triggers=(),
        expected_non_triggers=("design-before-plan",),
        category="pre-phase",
        notes="Single clear implementation path with no design alternatives. design-before-plan should NOT trigger.",
    ),
    TriggerCase(
        id="design-not-needed-documented",
        prompt="Implement the notification preferences API according to the design doc at docs/api/notifications-v2.md. The interface contracts and acceptance criteria are already defined.",
        expected_triggers=(),
        expected_non_triggers=("design-before-plan",),
        category="pre-phase",
        notes="Design already documented and frozen. design-before-plan should NOT trigger.",
    ),
    TriggerCase(
        id="design-not-needed-bugfix",
        prompt="Fix the null pointer exception in the email service when the recipient list is empty.",
        expected_triggers=("bugfix-workflow",),
        expected_non_triggers=("design-before-plan",),
        category="pre-phase",
        notes="Pure bug fix with no design decisions. design-before-plan should NOT trigger.",
    ),
    # --- impact-analysis ---
    TriggerCase(
        id="impact-public-api-change",
        prompt="I need to change the return type of the getUserProfile function. It's called by at least 5 other modules including the admin dashboard and the mobile API.",
        expected_triggers=("impact-analysis",),
        expected_non_triggers=("phase-plan",),
        category="pre-phase",
        notes="Public interface change with many callers. impact-analysis should trigger to assess blast radius.",
    ),
    TriggerCase(
        id="impact-not-needed-single-file",
        prompt="Rename a local variable inside the calculateTax helper function. Nothing else references it.",
        expected_triggers=(),
        expected_non_triggers=("impact-analysis",),
        category="pre-phase",
        notes="Single-file internal change, no exported symbol change. impact-analysis should NOT trigger.",
    ),
    TriggerCase(
        id="impact-data-model-change",
        prompt="Add a new required field to the Order model. This is an ORM model used across billing, shipping, and reporting.",
        expected_triggers=("impact-analysis",),
        expected_non_triggers=(),
        category="pre-phase",
        notes="Data model change affecting 3+ modules. impact-analysis should trigger.",
    ),
    # --- incremental-delivery ---
    TriggerCase(
        id="incremental-multi-pr-task",
        prompt="Implement the new notification system: add the data model, create the service layer, build the API endpoints, and update the frontend. This will be 3 separate PRs.",
        expected_triggers=("incremental-delivery",),
        expected_non_triggers=("phase-plan",),
        category="pre-phase",
        notes="Explicit 3-PR task. incremental-delivery should trigger, not phase-plan.",
    ),
    TriggerCase(
        id="incremental-not-needed-single-pr",
        prompt="Add a new endpoint for password reset. It's a single PR with model, handler, and test.",
        expected_triggers=(),
        expected_non_triggers=("incremental-delivery", "phase-plan"),
        category="pre-phase",
        notes="Single PR task. Neither incremental-delivery nor phase-plan needed.",
    ),
    TriggerCase(
        id="incremental-upgrade-to-phase",
        prompt="Migrate the entire auth system from session-based to JWT. This spans 8 services, needs parallel work streams, and must align with the external OAuth2 spec.",
        expected_triggers=("phase-plan",),
        expected_non_triggers=("incremental-delivery",),
        category="pre-phase",
        notes="8 services + parallel + external spec. Should escalate to phase-plan, not stay at incremental-delivery.",
    ),
    # --- self-review ---
    TriggerCase(
        id="self-review-after-edit",
        prompt="I just finished implementing the feature. Can you review the diff before I run tests?",
        expected_triggers=("self-review",),
        expected_non_triggers=("targeted-validation",),
        category="pre-phase",
        notes="Explicit diff review request before testing. self-review should trigger.",
    ),
    TriggerCase(
        id="self-review-not-needed-test-request",
        prompt="Run the unit tests for the auth module.",
        expected_triggers=(),
        expected_non_triggers=("self-review",),
        category="pre-phase",
        notes="Direct test command. self-review should NOT trigger.",
    ),
    TriggerCase(
        id="self-review-multi-file-change",
        prompt="I've made changes across 5 files to add the new payment flow. Before running the test suite, let me check if the diff looks clean.",
        expected_triggers=("self-review",),
        expected_non_triggers=(),
        category="pre-phase",
        notes="Multi-file change with explicit intent to review diff before testing.",
    ),
    # --- incremental-delivery / phase-plan PR boundary ---
    TriggerCase(
        id="incremental-4pr",
        prompt="Implement the new analytics pipeline: data ingestion, transformation rules, storage layer, and dashboard integration. Each layer is a separate PR — 4 PRs total.",
        expected_triggers=("incremental-delivery",),
        expected_non_triggers=("phase-plan",),
        category="pre-phase",
        notes="4 PRs is within the 2-4 PR range. incremental-delivery should trigger, not phase-plan.",
    ),
    TriggerCase(
        id="phase-5pr-boundary",
        prompt="Modernize the legacy reporting system. This involves migrating 5 services, rewriting the data pipeline, updating the API layer, adding new dashboards, and creating integration tests. Each is its own PR with cross-service dependencies.",
        expected_triggers=("phase-plan",),
        expected_non_triggers=("incremental-delivery",),
        category="pre-phase",
        notes="5+ PRs with cross-service dependencies exceeds incremental-delivery scope. phase-plan should trigger.",
    ),
    # --- chain triggers (skill A output → skill B activation) ---
    TriggerCase(
        id="design-after-scoping",
        prompt="We've narrowed the task to the notification subsystem, but there are still open design questions: should notifications be push-based or pull-based, and what delivery guarantees do we need?",
        expected_triggers=("design-before-plan",),
        expected_non_triggers=("scoped-tasking",),
        category="pre-phase",
        notes="Scope is already defined but design decisions remain. Matches 'scoped-tasking identified the boundary but design decisions remain open'.",
    ),
    TriggerCase(
        id="locate-then-impact",
        prompt="read-and-locate found that the pricing logic touches pricing/engine.ts, discount/rules.ts, checkout/summary.ts, and billing/invoice.ts. Now I need to understand which of these will break if I change the base price calculation.",
        expected_triggers=("impact-analysis",),
        expected_non_triggers=("read-and-locate",),
        category="pre-phase",
        notes="read-and-locate produced 4 candidate files. impact-analysis should now assess the blast radius. Matches 'read-and-locate produced 3+ tentative leads'.",
    ),
)


# ---------------------------------------------------------------------------
# Category 8: Baseline control (no skill should trigger)
# ---------------------------------------------------------------------------

BASELINE_CONTROL_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id="doc-only-change",
        prompt="Update the README to add installation instructions for the new CLI tool.",
        expected_triggers=(),
        expected_non_triggers=("design-before-plan", "plan-before-action", "safe-refactor"),
        category="baseline-control",
        notes="Pure documentation change. No skill should be required.",
    ),
    TriggerCase(
        id="info-query",
        prompt="What database does this project use? I see references to both PostgreSQL and Redis in the config.",
        expected_triggers=(),
        expected_non_triggers=("read-and-locate", "scoped-tasking", "impact-analysis"),
        category="baseline-control",
        notes="Information query with no intent to change code. No skill needed.",
    ),
    TriggerCase(
        id="git-operation",
        prompt="Commit my current changes and push to the feature branch.",
        expected_triggers=(),
        expected_non_triggers=("plan-before-action", "self-review", "targeted-validation"),
        category="baseline-control",
        notes="Git housekeeping. Exempt from skill activation.",
    ),
)


# ---------------------------------------------------------------------------
# Category 9: Confusion boundary (distinguishing easily confused skills)
# ---------------------------------------------------------------------------

CONFUSION_BOUNDARY_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id="scope-vs-locate",
        prompt="Users are complaining that search is broken across three modules — product search, user search, and log search. I don't know which module is actually affected. Can you help narrow it down?",
        expected_triggers=("scoped-tasking",),
        expected_non_triggers=("read-and-locate",),
        category="confusion-boundary",
        notes="Multiple modules mentioned, real target unclear. scoped-tasking should trigger to narrow scope, not read-and-locate.",
    ),
    TriggerCase(
        id="locate-vs-scope",
        prompt="Trace how the payment webhook flows through the billing module — I need to find the entry point, the validation step, and where it writes to the database.",
        expected_triggers=("read-and-locate",),
        expected_non_triggers=("scoped-tasking",),
        category="confusion-boundary",
        notes="Path tracing task across multiple steps. read-and-locate should trigger, not scoped-tasking.",
    ),
    TriggerCase(
        id="minimal-vs-refactor",
        prompt="While fixing the null check in the order validator, I noticed 200 lines of dead comments, 3 unused imports, and inconsistent naming. I want to clean it all up but the task is just the null check fix.",
        expected_triggers=("minimal-change-strategy",),
        expected_non_triggers=("safe-refactor",),
        category="confusion-boundary",
        notes="Cleanup temptation beyond task scope. minimal-change-strategy should constrain, not safe-refactor.",
    ),
    TriggerCase(
        id="refactor-vs-minimal",
        prompt="Simplify the three duplicate error-handling blocks in the API handlers into a shared middleware. Keep the external interface unchanged.",
        expected_triggers=("safe-refactor",),
        expected_non_triggers=("minimal-change-strategy",),
        category="confusion-boundary",
        notes="Intentional structural cleanup is a refactor goal. safe-refactor should guide it, not minimal-change-strategy.",
    ),
    TriggerCase(
        id="scope-vs-plan",
        prompt="The ticket says 'improve error handling across the backend' but that could mean dozens of files. Before we plan anything, what are we actually trying to change here?",
        expected_triggers=("scoped-tasking",),
        expected_non_triggers=("plan-before-action",),
        category="confusion-boundary",
        notes="Task boundary is undefined — must scope first. plan-before-action is premature until the target is narrowed.",
    ),
    TriggerCase(
        id="plan-vs-scope",
        prompt="The scope is clear: add retry logic to the three API clients in pkg/http/. I need to figure out the right order of changes and what assumptions to validate first.",
        expected_triggers=("plan-before-action",),
        expected_non_triggers=("scoped-tasking",),
        category="confusion-boundary",
        notes="Scope is already defined (3 files in pkg/http/). Sequencing and assumptions need a plan, not further scoping.",
    ),
)


# ---------------------------------------------------------------------------
# Category 10: Combo triggers (multiple skills should activate together)
# ---------------------------------------------------------------------------

COMBO_TRIGGER_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id="discover-analyze-plan",
        prompt="I need to modify user authentication in this unfamiliar codebase. I don't know where the auth code lives, the change touches a shared interface with multiple callers across several modules, and I'll need a plan before I start editing.",
        expected_triggers=("read-and-locate", "impact-analysis", "plan-before-action"),
        expected_non_triggers=("phase-plan",),
        category="combo-trigger",
        notes="Unfamiliar codebase + shared interface with multiple callers + multi-step edit. Three skills should co-activate.",
    ),
    TriggerCase(
        id="refactor-with-constraint",
        prompt="Clean up the duplicate validation logic across the three form handlers, but don't change any public API signatures and don't touch anything outside the forms directory.",
        expected_triggers=("safe-refactor",),
        expected_non_triggers=("design-before-plan",),
        category="combo-trigger",
        notes="Structural cleanup with explicit user-provided scope constraint. safe-refactor should trigger; minimal-change-strategy is not needed because the user already constrains the scope.",
    ),
    TriggerCase(
        id="design-impact-incremental",
        prompt="Add a refund capability to the order system. We need to decide between a state-machine approach and an event-sourcing approach, assess which existing payment flows are affected, and deliver it in 3 PRs.",
        expected_triggers=("design-before-plan", "impact-analysis", "incremental-delivery"),
        expected_non_triggers=("phase-plan",),
        category="combo-trigger",
        notes="Design choice + blast radius assessment + multi-PR delivery. Three skills should co-activate.",
    ),
)


# ---------------------------------------------------------------------------
# Category 11: Numeric boundary triggers (threshold precision tests)
# ---------------------------------------------------------------------------

NUMERIC_BOUNDARY_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id="impact-2-callers",
        prompt="Change the return type of formatDate. It's only called by the UserProfile component and the AdminPanel component — two callers total.",
        expected_triggers=(),
        expected_non_triggers=("impact-analysis",),
        category="numeric-boundary",
        notes="2 callers is below the 3-caller threshold. impact-analysis should NOT trigger.",
    ),
    TriggerCase(
        id="impact-3-callers",
        prompt="Change the return type of formatDate. It's called by UserProfile, AdminPanel, and ReportExporter — three separate modules depend on it.",
        expected_triggers=("impact-analysis",),
        expected_non_triggers=(),
        category="numeric-boundary",
        notes="Exactly 3 callers matches the threshold. impact-analysis SHOULD trigger.",
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
    *PRE_PHASE_CASES,
    *BASELINE_CONTROL_CASES,
    *CONFUSION_BOUNDARY_CASES,
    *COMBO_TRIGGER_CASES,
    *NUMERIC_BOUNDARY_CASES,
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
    "pre-phase",
    "baseline-control",
    "confusion-boundary",
    "combo-trigger",
    "numeric-boundary",
)


def cases_by_category(category: str) -> tuple[TriggerCase, ...]:
    return tuple(c for c in ALL_TRIGGER_CASES if c.category == category)


def resolve_trigger_case(identifier: str) -> TriggerCase:
    if identifier in ALL_TRIGGER_CASES_BY_ID:
        return ALL_TRIGGER_CASES_BY_ID[identifier]
    available = ", ".join(ALL_TRIGGER_CASES_BY_ID)
    raise KeyError(f"Unknown trigger case '{identifier}'. Available: {available}")
