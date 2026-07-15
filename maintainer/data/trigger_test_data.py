#!/usr/bin/env python3
"""Trigger test matrix for evaluating current skill triggerability."""

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


TASK_TYPE_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='bug-explicit',
        prompt='The login page returns a 500 error when users type a special character in the password field.',
        expected_triggers=(
        'bugfix-workflow',
    ),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='task-type',
        notes='Explicit bug report with symptom. bugfix-workflow should trigger immediately.',
    ),
    TriggerCase(
        id='bug-implicit',
        prompt='Something is wrong with the invoice export — it hangs for about 30 seconds before timing out.',
        expected_triggers=(
        'bugfix-workflow',
    ),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='task-type',
        notes="Implicit bug (symptom without the word 'bug'). Tests keyword coverage beyond literal 'bug'.",
    ),
    TriggerCase(
        id='refactor-explicit',
        prompt='Extract the duplicate request-normalization logic from three handlers into a shared helper.',
        expected_triggers=(
        'safe-refactor',
    ),
        expected_non_triggers=(
        'bugfix-workflow',
    ),
        category='task-type',
        notes='Explicit refactor request. safe-refactor should trigger; bugfix-workflow should not.',
    ),
    TriggerCase(
        id='feature-not-bug',
        prompt='Add a dark mode toggle to the settings page.',
        expected_triggers=(),
        expected_non_triggers=(
        'bugfix-workflow',
        'safe-refactor',
    ),
        category='task-type',
        notes='Pure additive feature. Neither bugfix nor refactor skills should trigger.',
    ),
    TriggerCase(
        id='bug-production-critical',
        prompt="Users can't log in! The auth service is returning 401 for every request since 10 minutes ago. We need to fix this immediately.",
        expected_triggers=(
        'bugfix-workflow',
    ),
        expected_non_triggers=(
        'safe-refactor',
        'design-before-plan',
    ),
        category='task-type',
        notes='High-urgency production incident. bugfix-workflow should trigger; no time for design or refactoring.',
    ),
    TriggerCase(
        id='refactor-frontend',
        prompt='Extract the user profile display logic from the Dashboard component into a reusable ProfileCard component. Keep the same props interface.',
        expected_triggers=(
        'safe-refactor',
    ),
        expected_non_triggers=(
        'bugfix-workflow',
    ),
        category='task-type',
        notes='Frontend component extraction refactor. safe-refactor should trigger for structural cleanup.',
    ),
)


BOUNDARY_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='simple-one-file-fix',
        prompt='Change the return status from 500 to 404 in the profile handler.',
        expected_triggers=(),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='agents-md-boundary',
        notes='Tiny single-file fix. AGENTS.md rules suffice. No skill should be loaded.',
    ),
    TriggerCase(
        id='implementation-planning-not-needed-single-file',
        prompt='Update the error message string in auth/errors.ts to match the product copy change. No other files or behavior need to change.',
        expected_triggers=(),
        expected_non_triggers=(
        'implementation-planning',
    ),
        category='agents-md-boundary',
        notes='Tiny single-file text change. This should stay in AGENTS.md §4 short planning, not escalate to durable implementation planning.',
    ),
    TriggerCase(
        id='multi-file-uncertain',
        prompt="Add retry logic to the payment service — I'm not sure if the retry config lives in the service layer or the client wrapper, and the tests will need updating too.",
        expected_triggers=(
    ),
        expected_non_triggers=(),
        category='agents-md-boundary',
        notes='3+ files, uncertainty about structure. Implementation should follow AGENTS.md Behavioral Guidelines §4 plan.',
    ),
    TriggerCase(
        id='broad-request-small-surface',
        prompt='Look into the performance issues across the reporting, billing, and notification systems — users say the daily summary email is slow.',
        expected_triggers=(
        'scoped-tasking',
    ),
        expected_non_triggers=(),
        category='agents-md-boundary',
        notes='Broad request but likely narrow edit surface. scoped-tasking should narrow it down.',
    ),
    TriggerCase(
        id='temptation-to-cleanup',
        prompt="Fix the date parsing bug in the import adapter. The surrounding code is pretty messy but let's not touch it right now.",
        expected_triggers=(
        'bugfix-workflow',
    ),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='agents-md-boundary',
        notes="Bug fix with explicit don't-clean-up instruction. AGENTS.md Change Rules handle the cleanup restraint; smallest-change discipline is optional.",
    ),
    TriggerCase(
        id='what-to-test-after-patch',
        prompt="I just fixed the CSV import adapter. What's the right way to test this without running the full 20-minute integration suite?",
        expected_triggers=(
        'targeted-validation',
    ),
        expected_non_triggers=(),
        category='agents-md-boundary',
        notes='Explicit validation question. targeted-validation should trigger.',
    ),
    TriggerCase(
        id='simple-test-request',
        prompt='Run the tests for this file.',
        expected_triggers=(),
        expected_non_triggers=(
        'targeted-validation',
    ),
        category='agents-md-boundary',
        notes='Simple command. AGENTS.md Validation Rules suffice.',
    ),
    TriggerCase(
        id='ambiguous-requirement',
        prompt='Make the system faster.',
        expected_triggers=(
        'scoped-tasking',
    ),
        expected_non_triggers=(),
        category='agents-md-boundary',
        notes='Extremely vague requirement. scoped-tasking should trigger and its Step 0 should fire clarification questions.',
    ),
    TriggerCase(
        id='validation-failure-diagnosis',
        prompt='The checkout integration test failed after my change. I could re-run the full suite, run just the checkout unit tests, or manually test the payment step. What should I do first to narrow it down?',
        expected_triggers=(
        'targeted-validation',
    ),
        expected_non_triggers=(),
        category='agents-md-boundary',
        notes='Multiple validation options after a failure. targeted-validation should trigger to select the cheapest diagnostic path.',
    ),
)


DISCOVERY_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='known-file',
        prompt='Fix the typo on line 42 of src/utils/format.ts.',
        expected_triggers=(),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='discovery',
        notes='Exact file and line known. No discovery or scoping skill needed.',
    ),
)


CONTEXT_BUDGET_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='short-task-no-noise',
        prompt='Add a comment to the calculateTotal function.',
        expected_triggers=(),
        expected_non_triggers=(),
        category='context-budget',
        notes='Trivial short task. No context management needed.',
    ),
    TriggerCase(
        id='repeated-hypothesis',
        prompt="We already checked the cache layer twice and the queue config three times. Each time it looked fine. I'm not sure what else to try.",
        expected_triggers=(),
        expected_non_triggers=(),
        category='context-budget',
        notes="Multiple re-reads of the same areas without progress. Matches the 'same file read more than twice' trigger.",
    ),
    TriggerCase(
        id='medium-session-focused',
        prompt="We've been working on this for a while but we're making steady progress. The auth middleware is fixed, now let's update the session expiry check in the same file.",
        expected_triggers=(),
        expected_non_triggers=(),
        category='context-budget',
        notes='Medium-length session but focused and progressing. No context compression needed.',
    ),
    TriggerCase(
        id='context-multi-hypothesis',
        prompt="The login failure could be a database connection timeout, a Redis session expiry bug, an OAuth token validation issue, or a firewall rule blocking the callback. I haven't gathered evidence to rule any of them out yet.",
        expected_triggers=(),
        expected_non_triggers=(),
        category='context-budget',
        notes="4 active hypotheses without evidence ranking. Matches the '3+ hypotheses active without ranking evidence' trigger.",
    ),
    TriggerCase(
        id='context-stalled-actions',
        prompt="I just read auth.ts again — nothing new. Then I checked the session log — no relevant errors. Then I re-read auth.ts a third time and still have no leads. I feel like I'm going in circles.",
        expected_triggers=(),
        expected_non_triggers=(),
        category='context-budget',
        notes="Last 3+ actions did not advance the stated objective. Matches the 'last 3 actions did not advance' trigger.",
    ),
)


MULTI_AGENT_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='parallel-investigation',
        prompt='Investigate the auth middleware, session storage, and role checking in parallel to understand the full auth flow.',
        expected_triggers=(
        'multi-agent-protocol',
    ),
        expected_non_triggers=(),
        category='multi-agent',
        notes='Explicit parallel request. multi-agent-protocol should trigger. multi-agent synthesis only after results conflict.',
    ),
    TriggerCase(
        id='implicit-parallel-opportunity',
        prompt='We need to understand the full payment flow: how the API handler validates requests, how the billing service calculates charges, and how the notification service sends receipts. These three areas are owned by different teams.',
        expected_triggers=(
        'multi-agent-protocol',
    ),
        expected_non_triggers=(),
        category='multi-agent',
        notes="No explicit 'parallel' keyword. Three independent, team-separated investigation areas imply parallelism. Tests whether the agent recognizes the opportunity from task structure alone.",
    ),
    TriggerCase(
        id='serial-single-file',
        prompt='Fix the off-by-one error in pkg/runtime/replay.go.',
        expected_triggers=(),
        expected_non_triggers=(
        'multi-agent-protocol',
    ),
        category='multi-agent',
        notes='Single-file fix. multi-agent-protocol should NOT trigger (exemption applies).',
    ),
)


PHASE_CASES: tuple[TriggerCase, ...] = ()


PRE_PHASE_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='design-multiple-approaches',
        prompt='Add caching to the product recommendation engine. We could use Redis, Memcached, or an in-memory LRU cache. Each has different trade-offs for our scale and consistency requirements.',
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='Multiple implementation approaches with explicit trade-offs. design-before-plan should trigger to compare alternatives before planning.',
    ),
    TriggerCase(
        id='design-api-contract',
        prompt='Design a new webhook API for third-party integrations. We need to define the payload format, authentication scheme, retry semantics, and versioning strategy before implementation.',
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='Public API design with contract decisions. design-before-plan should trigger to establish interface contracts.',
    ),
    TriggerCase(
        id='design-unclear-acceptance',
        prompt="Make the checkout flow faster. Users are complaining but we don't have specific performance targets or clear success criteria yet.",
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='pre-phase',
        notes='Missing acceptance criteria. design-before-plan should trigger to establish measurable criteria before planning.',
    ),
    TriggerCase(
        id='design-cross-module-contract',
        prompt='Refactor the authentication layer to support both session-based and token-based auth. This will change the interface between the auth module, API handlers, and frontend.',
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(),
        category='pre-phase',
        notes='Cross-module contract change. design-before-plan should trigger to define interface contracts.',
    ),
    TriggerCase(
        id='design-not-needed-clear-path',
        prompt="Add a new field 'emailVerified' (boolean) to the User model and display it on the admin dashboard user detail page.",
        expected_triggers=(),
        expected_non_triggers=(
        'design-before-plan',
    ),
        category='pre-phase',
        notes='Single clear implementation path with no design alternatives. design-before-plan should NOT trigger.',
    ),
    TriggerCase(
        id='design-not-needed-documented',
        prompt='Implement the notification preferences API according to the design doc at docs/api/notifications-v2.md. The interface contracts and acceptance criteria are already defined.',
        expected_triggers=(),
        expected_non_triggers=(
        'design-before-plan',
    ),
        category='pre-phase',
        notes='Design already documented and frozen. design-before-plan should NOT trigger.',
    ),
    TriggerCase(
        id='architecture-design-separate-adr-artifacts',
        prompt='Design a new notification subsystem with a dispatcher, channel adapters, preference storage, and a queue technology choice. Produce the architecture document and separate ADR artifacts for long-lived decisions.',
        expected_triggers=(
            'architecture-design',
        ),
        expected_non_triggers=(
            'implementation-planning',
        ),
        category='pre-phase',
        notes='System/subsystem design with 3+ components and technology selection should trigger architecture-design and its ADR artifact contract.',
    ),
    TriggerCase(
        id='implementation-planning-accepted-adr',
        prompt='ADR-0042 is Accepted and active, and the design is settled. Create a multi-file implementation plan that cites ADR-0042 in Sources and Alignment and in every constrained step.',
        expected_triggers=(
            'implementation-planning',
        ),
        expected_non_triggers=(
            'design-before-plan',
        ),
        category='pre-phase',
        notes='An active Accepted ADR is a frozen planning input and should be traced into implementation steps.',
    ),
    TriggerCase(
        id='implementation-planning-proposed-adr-blocked',
        prompt='ADR-0043 is still Proposed, but implementation depends on its queue choice. Review and settle the ADR before making an implementation plan.',
        expected_triggers=(
            'design-review-loop',
        ),
        expected_non_triggers=(
            'implementation-planning',
        ),
        category='pre-phase',
        notes='A Proposed ADR cannot constrain implementation planning and must return to design review.',
    ),
    TriggerCase(
        id='implementation-planning-from-requirement-doc',
        prompt='The requirement doc at docs/requirements/notification-preferences.md already fixes the endpoint shape, additive schema change, validation rules, and acceptance criteria. Please turn it into a 2-PR implementation plan before coding starts.',
        expected_triggers=(
        'implementation-planning',
    ),
        expected_non_triggers=(
        'design-before-plan',
    ),
        category='pre-phase',
        notes='Requirement documentation already carries a settled design direction. implementation-planning should trigger directly instead of reopening design.',
    ),
    TriggerCase(
        id='implementation-planning-blocked-by-open-design',
        prompt='We have a requirement doc for notification preferences, but it still leaves the storage model open (user table vs separate preferences service) and the API payload shape undecided. Before coding, help me figure out the plan.',
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
        'implementation-planning',
    ),
        category='pre-phase',
        notes='The user asks for a plan, but design choices remain open. design-before-plan must trigger before implementation-planning.',
    ),
    TriggerCase(
        id='design-not-needed-bugfix',
        prompt='Fix the null pointer exception in the email service when the recipient list is empty.',
        expected_triggers=(
        'bugfix-workflow',
    ),
        expected_non_triggers=(
        'design-before-plan',
    ),
        category='pre-phase',
        notes='Pure bug fix with no design decisions. design-before-plan should NOT trigger.',
    ),
    TriggerCase(
        id='impact-public-api-change',
        prompt="I need to change the return type of the getUserProfile function. It's called by at least 5 other modules including the admin dashboard and the mobile API.",
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='Public interface change with many callers. impact-analysis should trigger to assess blast radius.',
    ),
    TriggerCase(
        id='impact-not-needed-single-file',
        prompt='Rename a local variable inside the calculateTax helper function. Nothing else references it.',
        expected_triggers=(),
        expected_non_triggers=(
        'impact-analysis',
    ),
        category='pre-phase',
        notes='Single-file internal change, no exported symbol change. impact-analysis should NOT trigger.',
    ),
    TriggerCase(
        id='impact-data-model-change',
        prompt='Add a new required field to the Order model. This is an ORM model used across billing, shipping, and reporting.',
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(),
        category='pre-phase',
        notes='Data model change affecting 3+ modules. impact-analysis should trigger.',
    ),
    TriggerCase(
        id='incremental-multi-pr-task',
        prompt='Implement the new notification system: add the data model, create the service layer, build the API endpoints, and update the frontend. This will be 3 separate PRs.',
        expected_triggers=(),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='Explicit 3-PR task. Incremental delivery should apply; no phase escalation needed.',
    ),
    TriggerCase(
        id='incremental-not-needed-single-pr',
        prompt="Add a new endpoint for password reset. It's a single PR with model, handler, and test.",
        expected_triggers=(),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='Single PR task. No incremental delivery or phase planning needed.',
    ),
    TriggerCase(
        id='self-review-after-edit',
        prompt='I just finished implementing the feature. Can you review the diff before I run tests?',
        expected_triggers=(
        'self-review',
    ),
        expected_non_triggers=(
        'targeted-validation',
    ),
        category='pre-phase',
        notes='Explicit diff review request before testing. self-review should trigger.',
    ),
    TriggerCase(
        id='self-review-not-needed-test-request',
        prompt='Run the unit tests for the auth module.',
        expected_triggers=(),
        expected_non_triggers=(
        'self-review',
    ),
        category='pre-phase',
        notes='Direct test command. self-review should NOT trigger.',
    ),
    TriggerCase(
        id='self-review-multi-file-change',
        prompt="I've made changes across 5 files to add the new payment flow. Before running the test suite, let me check if the diff looks clean.",
        expected_triggers=(
        'self-review',
    ),
        expected_non_triggers=(),
        category='pre-phase',
        notes='Multi-file change with explicit intent to review diff before testing.',
    ),
    TriggerCase(
        id='incremental-4pr',
        prompt='Implement the new analytics pipeline: data ingestion, transformation rules, storage layer, and dashboard integration. Each layer is a separate PR — 4 PRs total.',
        expected_triggers=(),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='4 PRs is within the 2-4 PR range. Incremental delivery should apply; no phase escalation needed.',
    ),
    TriggerCase(
        id='design-after-scoping',
        prompt="We've narrowed the task to the notification subsystem, but there are still open design questions: should notifications be push-based or pull-based, and what delivery guarantees do we need?",
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='pre-phase',
        notes="Scope is already defined but design decisions remain. Matches 'scoped-tasking identified the boundary but design decisions remain open'.",
    ),
    TriggerCase(
        id='locate-then-impact',
        prompt='built-in code search found that the pricing logic touches pricing/engine.ts, discount/rules.ts, checkout/summary.ts, and billing/invoice.ts. Now I need to understand which of these will break if I change the base price calculation.',
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(),
        category='pre-phase',
        notes="built-in code search produced 4 candidate files. impact-analysis should now assess the blast radius. Matches 'built-in code search produced 3+ tentative leads'.",
    ),
    TriggerCase(
        id='requirement-vague-feature',
        prompt='给我们的系统加一个审批功能。',
        expected_triggers=(
        'requirement-interview',
    ),
        expected_non_triggers=(
        'design-before-plan',
    ),
        category='pre-phase',
        notes='Vague feature request missing business goal, roles, main flow, scope, and acceptance criteria. requirement-interview should trigger to clarify before scoping or design; design-before-plan should NOT trigger yet.',
    ),
    TriggerCase(
        id='requirement-not-needed-clear-spec',
        prompt='Add an "emailVerified" boolean field to the User model and show it on the admin user detail page, defaulting to false.',
        expected_triggers=(),
        expected_non_triggers=(
        'requirement-interview',
    ),
        category='pre-phase',
        notes='Feature request is concrete with clear object, behavior, and acceptance. requirement-interview should NOT trigger.',
    ),
)


CHAIN_TRIGGER_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='chain-scope-to-locate',
        prompt="We've narrowed the task to the auth module, but I don't know which file handles token refresh.",
        expected_triggers=(),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='chain-trigger',
        notes='Scope is narrowed (auth module) but exact location unknown. Should chain from scoping to built-in code search.',
    ),
    TriggerCase(
        id='chain-locate-to-plan',
        prompt='built-in code search found the edit points: auth/token.ts and auth/session.ts. Now I need a plan for the changes.',
        expected_triggers=(
        'implementation-planning',
    ),
        expected_non_triggers=(),
        category='chain-trigger',
        notes='Location discovery complete, now needs durable sequencing and verification. implementation-planning should trigger.',
    ),
    TriggerCase(
        id='chain-bugfix-to-cba',
        prompt="I've been diagnosing this bug for a while, checked 10 files, and I have 4 competing theories but no evidence to rank them.",
        expected_triggers=(),
        expected_non_triggers=(
        'bugfix-workflow',
    ),
        category='chain-trigger',
        notes='Bug diagnosis has consumed too much context without convergence. Should chain from bugfix-workflow to context discipline.',
    ),
    TriggerCase(
        id='chain-review-to-validation',
        prompt='Self-review is clean -- no blocking issues in the diff. What should I test?',
        expected_triggers=(
        'targeted-validation',
    ),
        expected_non_triggers=(
        'self-review',
    ),
        category='chain-trigger',
        notes='Review complete, now needs test selection. Should chain from self-review to targeted-validation.',
    ),
    TriggerCase(
        id='chain-plan-to-design',
        prompt="I tried to plan the implementation but realized I can't sequence the steps because there are two competing design approaches.",
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
    ),
        category='chain-trigger',
        notes='Planning blocked by unresolved design choice. design-before-plan should trigger.',
    ),
    TriggerCase(
        id='chain-minimal-to-impact',
        prompt='I was making a small fix to the validator, but it turns out 5 other modules import this function.',
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(),
        category='chain-trigger',
        notes='Small patch discovered to have wide blast radius. Should escalate from smallest-change discipline to impact-analysis.',
    ),
    TriggerCase(
        id='chain-refactor-to-design',
        prompt="I started extracting the shared helper but realized the refactor changes the module's public interface.",
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='chain-trigger',
        notes='Refactor touches public contract. Should escalate from safe-refactor to design-before-plan.',
    ),
    TriggerCase(
        id='chain-parallel-to-conflict',
        prompt='Two subagents disagree: one says the timeout is in the client, the other blames the server.',
        expected_triggers=(),
        expected_non_triggers=(
        'multi-agent-protocol',
    ),
        category='chain-trigger',
        notes='Parallel investigation produced conflicting results. Should chain from multi-agent-protocol to multi-agent synthesis.',
    ),
)


BASELINE_CONTROL_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='doc-only-change',
        prompt='Update the README to add installation instructions for the new CLI tool.',
        expected_triggers=(),
        expected_non_triggers=(
        'design-before-plan',
        'safe-refactor',
    ),
        category='baseline-control',
        notes='Pure documentation change. No skill should be required.',
    ),
    TriggerCase(
        id='info-query',
        prompt='What database does this project use? I see references to both PostgreSQL and Redis in the config.',
        expected_triggers=(),
        expected_non_triggers=(
        'scoped-tasking',
        'impact-analysis',
    ),
        category='baseline-control',
        notes='Information query with no intent to change code. No skill needed.',
    ),
    TriggerCase(
        id='git-operation',
        prompt='Commit my current changes and push to the feature branch.',
        expected_triggers=(),
        expected_non_triggers=(
        'self-review',
        'targeted-validation',
    ),
        category='baseline-control',
        notes='Git housekeeping. Exempt from skill activation.',
    ),
)


CONFUSION_BOUNDARY_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='scope-vs-locate',
        prompt="Users are complaining that search is broken, but I don't know if they mean the product search, the user search, or the log search. Can you help figure out which one?",
        expected_triggers=(
        'scoped-tasking',
    ),
        expected_non_triggers=(),
        category='confusion-boundary',
        notes='Ambiguous scope needs narrowing, not code discovery. scoped-tasking should trigger to clarify which subsystem.',
    ),
    TriggerCase(
        id='locate-vs-scope',
        prompt='Find where the payment webhook handler is defined. I know it exists somewhere in the billing module but I need the exact file.',
        expected_triggers=(),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='confusion-boundary',
        notes='Clear scope (billing module), unclear location. built-in code search should trigger, not scoped-tasking.',
    ),
    TriggerCase(
        id='minimal-vs-refactor',
        prompt='While fixing the null check in the order validator, I noticed 200 lines of dead comments, 3 unused imports, and inconsistent naming. I want to clean it all up but the task is just the null check fix.',
        expected_triggers=(),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='confusion-boundary',
        notes='Cleanup temptation beyond task scope. smallest-change discipline should constrain, not safe-refactor.',
    ),
    TriggerCase(
        id='refactor-vs-minimal',
        prompt='Simplify the three duplicate error-handling blocks in the API handlers into a shared middleware. Keep the external interface unchanged.',
        expected_triggers=(
        'safe-refactor',
    ),
        expected_non_triggers=(),
        category='confusion-boundary',
        notes='Intentional structural cleanup is a refactor goal. safe-refactor should guide it, not smallest-change discipline.',
    ),
    TriggerCase(
        id='scope-vs-plan',
        prompt="The ticket says 'improve error handling across the backend' but that could mean dozens of files. Before we plan anything, what are we actually trying to change here?",
        expected_triggers=(
        'scoped-tasking',
    ),
        expected_non_triggers=(
    ),
        category='confusion-boundary',
        notes='Task boundary is undefined — must scope first.',
    ),
    TriggerCase(
        id='plan-vs-scope',
        prompt='The scope is clear: add retry logic to the three API clients in pkg/http/. I need to figure out the right order of changes and what assumptions to validate first.',
        expected_triggers=(
        'implementation-planning',
    ),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='confusion-boundary',
        notes='Scope is already defined (3 files in pkg/http/). Sequencing and assumptions now belong to implementation-planning, not further scoping.',
    ),
)


COMBO_TRIGGER_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='discover-analyze-plan',
        prompt="I need to modify user authentication in this unfamiliar codebase. I don't know where the auth code lives, the change might affect several modules, and I'll need a plan before I start editing.",
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(
    ),
        category='combo-trigger',
        notes='Unfamiliar codebase + multi-module impact + multi-step edit. Three skills should co-activate.',
    ),
    TriggerCase(
        id='refactor-with-constraint',
        prompt="Clean up the duplicate validation logic across the three form handlers, but don't change any public API signatures and don't touch anything outside the forms directory.",
        expected_triggers=(
        'safe-refactor',
    ),
        expected_non_triggers=(
        'design-before-plan',
    ),
        category='combo-trigger',
        notes='Structural cleanup with explicit scope constraint. Both safe-refactor and smallest-change discipline should co-activate.',
    ),
    TriggerCase(
        id='design-impact-incremental',
        prompt='Add a refund capability to the order system. We need to decide between a state-machine approach and an event-sourcing approach, assess which existing payment flows are affected, and deliver it in 3 PRs.',
        expected_triggers=(
        'design-before-plan',
        'impact-analysis',
    ),
        expected_non_triggers=(
    ),
        category='combo-trigger',
        notes='Design choice + blast radius assessment + multi-PR delivery. Three skills should co-activate.',
    ),
)


NUMERIC_BOUNDARY_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='impact-2-callers',
        prompt="Change the return type of formatDate. It's only called by the UserProfile component and the AdminPanel component — two callers total.",
        expected_triggers=(),
        expected_non_triggers=(
        'impact-analysis',
    ),
        category='numeric-boundary',
        notes='2 callers is below the 3-caller threshold. impact-analysis should NOT trigger.',
    ),
    TriggerCase(
        id='impact-3-callers',
        prompt="Change the return type of formatDate. It's called by UserProfile, AdminPanel, and ReportExporter — three separate modules depend on it.",
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(),
        category='numeric-boundary',
        notes='Exactly 3 callers matches the threshold. impact-analysis SHOULD trigger.',
    ),
)


KNOWLEDGE_DRIVEN_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='knowledge-init-project-kb',
        prompt='This repo still has docs/durable project knowledge. Dry-run a migration into Worktrail and tell me what would become pending candidates.',
        expected_triggers=(),
        expected_non_triggers=(
    ),
        category='knowledge-driven',
        notes='Explicit request to bridge legacy KDD docs into Worktrail. durable project knowledge should trigger.',
    ),
    TriggerCase(
        id='knowledge-capture-runbook',
        prompt='Worktrail is not available in this old repo. We just learned the staging API requires a special base path and a keyauth header. Please capture that as reusable project knowledge after the fix is verified.',
        expected_triggers=(),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='knowledge-driven',
        notes='Reusable implementation finding should use the legacy KDD fallback when Worktrail is unavailable.',
    ),
    TriggerCase(
        id='knowledge-agents-required',
        prompt='AGENTS.md says this repo uses docs/durable project knowledge. Before changing the payment adapter, read the relevant legacy project knowledge and migrate it with worktrail import kdd if the user approves.',
        expected_triggers=(),
        expected_non_triggers=(
    ),
        category='knowledge-driven',
        notes='Project governance explicitly references legacy KDD and should trigger the bridge workflow.',
    ),
    TriggerCase(
        id='knowledge-local-private-context',
        prompt='Record my local staging project IDs and temporary request IDs for this debugging session, but keep them out of shared docs and version control.',
        expected_triggers=(),
        expected_non_triggers=(
        'self-review',
    ),
        category='knowledge-driven',
        notes='Local-only knowledge should use local active log, not shared project docs.',
    ),
    TriggerCase(
        id='knowledge-control-simple-question',
        prompt='What is the difference between project documentation and local notes?',
        expected_triggers=(),
        expected_non_triggers=(),
        category='knowledge-driven',
        notes='Conceptual one-off question. No repository knowledge workflow is needed.',
    ),
)


ALL_TRIGGER_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='bug-explicit',
        prompt='The login page returns a 500 error when users type a special character in the password field.',
        expected_triggers=(
        'bugfix-workflow',
    ),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='task-type',
        notes='Explicit bug report with symptom. bugfix-workflow should trigger immediately.',
    ),
    TriggerCase(
        id='bug-implicit',
        prompt='Something is wrong with the invoice export — it hangs for about 30 seconds before timing out.',
        expected_triggers=(
        'bugfix-workflow',
    ),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='task-type',
        notes="Implicit bug (symptom without the word 'bug'). Tests keyword coverage beyond literal 'bug'.",
    ),
    TriggerCase(
        id='refactor-explicit',
        prompt='Extract the duplicate request-normalization logic from three handlers into a shared helper.',
        expected_triggers=(
        'safe-refactor',
    ),
        expected_non_triggers=(
        'bugfix-workflow',
    ),
        category='task-type',
        notes='Explicit refactor request. safe-refactor should trigger; bugfix-workflow should not.',
    ),
    TriggerCase(
        id='feature-not-bug',
        prompt='Add a dark mode toggle to the settings page.',
        expected_triggers=(),
        expected_non_triggers=(
        'bugfix-workflow',
        'safe-refactor',
    ),
        category='task-type',
        notes='Pure additive feature. Neither bugfix nor refactor skills should trigger.',
    ),
    TriggerCase(
        id='bug-production-critical',
        prompt="Users can't log in! The auth service is returning 401 for every request since 10 minutes ago. We need to fix this immediately.",
        expected_triggers=(
        'bugfix-workflow',
    ),
        expected_non_triggers=(
        'safe-refactor',
        'design-before-plan',
    ),
        category='task-type',
        notes='High-urgency production incident. bugfix-workflow should trigger; no time for design or refactoring.',
    ),
    TriggerCase(
        id='refactor-frontend',
        prompt='Extract the user profile display logic from the Dashboard component into a reusable ProfileCard component. Keep the same props interface.',
        expected_triggers=(
        'safe-refactor',
    ),
        expected_non_triggers=(
        'bugfix-workflow',
    ),
        category='task-type',
        notes='Frontend component extraction refactor. safe-refactor should trigger for structural cleanup.',
    ),
    TriggerCase(
        id='simple-one-file-fix',
        prompt='Change the return status from 500 to 404 in the profile handler.',
        expected_triggers=(),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='agents-md-boundary',
        notes='Tiny single-file fix. AGENTS.md rules suffice. No skill should be loaded.',
    ),
    TriggerCase(
        id='implementation-planning-not-needed-single-file',
        prompt='Update the error message string in auth/errors.ts to match the product copy change. No other files or behavior need to change.',
        expected_triggers=(),
        expected_non_triggers=(
        'implementation-planning',
    ),
        category='agents-md-boundary',
        notes='Tiny single-file text change. This should stay in AGENTS.md §4 short planning, not escalate to durable implementation planning.',
    ),
    TriggerCase(
        id='multi-file-uncertain',
        prompt="Add retry logic to the payment service — I'm not sure if the retry config lives in the service layer or the client wrapper, and the tests will need updating too.",
        expected_triggers=(
    ),
        expected_non_triggers=(),
        category='agents-md-boundary',
        notes='3+ files, uncertainty about structure. Implementation should follow AGENTS.md Behavioral Guidelines §4 plan.',
    ),
    TriggerCase(
        id='broad-request-small-surface',
        prompt='Look into the performance issues across the reporting, billing, and notification systems — users say the daily summary email is slow.',
        expected_triggers=(
        'scoped-tasking',
    ),
        expected_non_triggers=(),
        category='agents-md-boundary',
        notes='Broad request but likely narrow edit surface. scoped-tasking should narrow it down.',
    ),
    TriggerCase(
        id='temptation-to-cleanup',
        prompt="Fix the date parsing bug in the import adapter. The surrounding code is pretty messy but let's not touch it right now.",
        expected_triggers=(
        'bugfix-workflow',
    ),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='agents-md-boundary',
        notes="Bug fix with explicit don't-clean-up instruction. AGENTS.md Change Rules handle the cleanup restraint; smallest-change discipline is optional.",
    ),
    TriggerCase(
        id='what-to-test-after-patch',
        prompt="I just fixed the CSV import adapter. What's the right way to test this without running the full 20-minute integration suite?",
        expected_triggers=(
        'targeted-validation',
    ),
        expected_non_triggers=(),
        category='agents-md-boundary',
        notes='Explicit validation question. targeted-validation should trigger.',
    ),
    TriggerCase(
        id='simple-test-request',
        prompt='Run the tests for this file.',
        expected_triggers=(),
        expected_non_triggers=(
        'targeted-validation',
    ),
        category='agents-md-boundary',
        notes='Simple command. AGENTS.md Validation Rules suffice.',
    ),
    TriggerCase(
        id='ambiguous-requirement',
        prompt='Make the system faster.',
        expected_triggers=(
        'scoped-tasking',
    ),
        expected_non_triggers=(),
        category='agents-md-boundary',
        notes='Extremely vague requirement. scoped-tasking should trigger and its Step 0 should fire clarification questions.',
    ),
    TriggerCase(
        id='validation-failure-diagnosis',
        prompt='The checkout integration test failed after my change. I could re-run the full suite, run just the checkout unit tests, or manually test the payment step. What should I do first to narrow it down?',
        expected_triggers=(
        'targeted-validation',
    ),
        expected_non_triggers=(),
        category='agents-md-boundary',
        notes='Multiple validation options after a failure. targeted-validation should trigger to select the cheapest diagnostic path.',
    ),
    TriggerCase(
        id='known-file',
        prompt='Fix the typo on line 42 of src/utils/format.ts.',
        expected_triggers=(),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='discovery',
        notes='Exact file and line known. No discovery or scoping skill needed.',
    ),
    TriggerCase(
        id='short-task-no-noise',
        prompt='Add a comment to the calculateTotal function.',
        expected_triggers=(),
        expected_non_triggers=(),
        category='context-budget',
        notes='Trivial short task. No context management needed.',
    ),
    TriggerCase(
        id='repeated-hypothesis',
        prompt="We already checked the cache layer twice and the queue config three times. Each time it looked fine. I'm not sure what else to try.",
        expected_triggers=(),
        expected_non_triggers=(),
        category='context-budget',
        notes="Multiple re-reads of the same areas without progress. Matches the 'same file read more than twice' trigger.",
    ),
    TriggerCase(
        id='medium-session-focused',
        prompt="We've been working on this for a while but we're making steady progress. The auth middleware is fixed, now let's update the session expiry check in the same file.",
        expected_triggers=(),
        expected_non_triggers=(),
        category='context-budget',
        notes='Medium-length session but focused and progressing. No context compression needed.',
    ),
    TriggerCase(
        id='context-multi-hypothesis',
        prompt="The login failure could be a database connection timeout, a Redis session expiry bug, an OAuth token validation issue, or a firewall rule blocking the callback. I haven't gathered evidence to rule any of them out yet.",
        expected_triggers=(),
        expected_non_triggers=(),
        category='context-budget',
        notes="4 active hypotheses without evidence ranking. Matches the '3+ hypotheses active without ranking evidence' trigger.",
    ),
    TriggerCase(
        id='context-stalled-actions',
        prompt="I just read auth.ts again — nothing new. Then I checked the session log — no relevant errors. Then I re-read auth.ts a third time and still have no leads. I feel like I'm going in circles.",
        expected_triggers=(),
        expected_non_triggers=(),
        category='context-budget',
        notes="Last 3+ actions did not advance the stated objective. Matches the 'last 3 actions did not advance' trigger.",
    ),
    TriggerCase(
        id='parallel-investigation',
        prompt='Investigate the auth middleware, session storage, and role checking in parallel to understand the full auth flow.',
        expected_triggers=(
        'multi-agent-protocol',
    ),
        expected_non_triggers=(),
        category='multi-agent',
        notes='Explicit parallel request. multi-agent-protocol should trigger. multi-agent synthesis only after results conflict.',
    ),
    TriggerCase(
        id='implicit-parallel-opportunity',
        prompt='We need to understand the full payment flow: how the API handler validates requests, how the billing service calculates charges, and how the notification service sends receipts. These three areas are owned by different teams.',
        expected_triggers=(
        'multi-agent-protocol',
    ),
        expected_non_triggers=(),
        category='multi-agent',
        notes="No explicit 'parallel' keyword. Three independent, team-separated investigation areas imply parallelism. Tests whether the agent recognizes the opportunity from task structure alone.",
    ),
    TriggerCase(
        id='serial-single-file',
        prompt='Fix the off-by-one error in pkg/runtime/replay.go.',
        expected_triggers=(),
        expected_non_triggers=(
        'multi-agent-protocol',
    ),
        category='multi-agent',
        notes='Single-file fix. multi-agent-protocol should NOT trigger (exemption applies).',
    ),
    TriggerCase(
        id='design-multiple-approaches',
        prompt='Add caching to the product recommendation engine. We could use Redis, Memcached, or an in-memory LRU cache. Each has different trade-offs for our scale and consistency requirements.',
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='Multiple implementation approaches with explicit trade-offs. design-before-plan should trigger to compare alternatives before planning.',
    ),
    TriggerCase(
        id='design-api-contract',
        prompt='Design a new webhook API for third-party integrations. We need to define the payload format, authentication scheme, retry semantics, and versioning strategy before implementation.',
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='Public API design with contract decisions. design-before-plan should trigger to establish interface contracts.',
    ),
    TriggerCase(
        id='design-unclear-acceptance',
        prompt="Make the checkout flow faster. Users are complaining but we don't have specific performance targets or clear success criteria yet.",
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='pre-phase',
        notes='Missing acceptance criteria. design-before-plan should trigger to establish measurable criteria before planning.',
    ),
    TriggerCase(
        id='design-cross-module-contract',
        prompt='Refactor the authentication layer to support both session-based and token-based auth. This will change the interface between the auth module, API handlers, and frontend.',
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(),
        category='pre-phase',
        notes='Cross-module contract change. design-before-plan should trigger to define interface contracts.',
    ),
    TriggerCase(
        id='design-not-needed-clear-path',
        prompt="Add a new field 'emailVerified' (boolean) to the User model and display it on the admin dashboard user detail page.",
        expected_triggers=(),
        expected_non_triggers=(
        'design-before-plan',
    ),
        category='pre-phase',
        notes='Single clear implementation path with no design alternatives. design-before-plan should NOT trigger.',
    ),
    TriggerCase(
        id='design-not-needed-documented',
        prompt='Implement the notification preferences API according to the design doc at docs/api/notifications-v2.md. The interface contracts and acceptance criteria are already defined.',
        expected_triggers=(),
        expected_non_triggers=(
        'design-before-plan',
    ),
        category='pre-phase',
        notes='Design already documented and frozen. design-before-plan should NOT trigger.',
    ),
    TriggerCase(
        id='implementation-planning-from-requirement-doc',
        prompt='The requirement doc at docs/requirements/notification-preferences.md already fixes the endpoint shape, additive schema change, validation rules, and acceptance criteria. Please turn it into a 2-PR implementation plan before coding starts.',
        expected_triggers=(
        'implementation-planning',
    ),
        expected_non_triggers=(
        'design-before-plan',
    ),
        category='pre-phase',
        notes='Requirement documentation already carries a settled design direction. implementation-planning should trigger directly instead of reopening design.',
    ),
    TriggerCase(
        id='implementation-planning-blocked-by-open-design',
        prompt='We have a requirement doc for notification preferences, but it still leaves the storage model open (user table vs separate preferences service) and the API payload shape undecided. Before coding, help me figure out the plan.',
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
        'implementation-planning',
    ),
        category='pre-phase',
        notes='The user asks for a plan, but design choices remain open. design-before-plan must trigger before implementation-planning.',
    ),
    TriggerCase(
        id='design-not-needed-bugfix',
        prompt='Fix the null pointer exception in the email service when the recipient list is empty.',
        expected_triggers=(
        'bugfix-workflow',
    ),
        expected_non_triggers=(
        'design-before-plan',
    ),
        category='pre-phase',
        notes='Pure bug fix with no design decisions. design-before-plan should NOT trigger.',
    ),
    TriggerCase(
        id='impact-public-api-change',
        prompt="I need to change the return type of the getUserProfile function. It's called by at least 5 other modules including the admin dashboard and the mobile API.",
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='Public interface change with many callers. impact-analysis should trigger to assess blast radius.',
    ),
    TriggerCase(
        id='impact-not-needed-single-file',
        prompt='Rename a local variable inside the calculateTax helper function. Nothing else references it.',
        expected_triggers=(),
        expected_non_triggers=(
        'impact-analysis',
    ),
        category='pre-phase',
        notes='Single-file internal change, no exported symbol change. impact-analysis should NOT trigger.',
    ),
    TriggerCase(
        id='impact-data-model-change',
        prompt='Add a new required field to the Order model. This is an ORM model used across billing, shipping, and reporting.',
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(),
        category='pre-phase',
        notes='Data model change affecting 3+ modules. impact-analysis should trigger.',
    ),
    TriggerCase(
        id='incremental-multi-pr-task',
        prompt='Implement the new notification system: add the data model, create the service layer, build the API endpoints, and update the frontend. This will be 3 separate PRs.',
        expected_triggers=(),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='Explicit 3-PR task. Incremental delivery should apply; no phase escalation needed.',
    ),
    TriggerCase(
        id='incremental-not-needed-single-pr',
        prompt="Add a new endpoint for password reset. It's a single PR with model, handler, and test.",
        expected_triggers=(),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='Single PR task. No incremental delivery or phase planning needed.',
    ),
    TriggerCase(
        id='self-review-after-edit',
        prompt='I just finished implementing the feature. Can you review the diff before I run tests?',
        expected_triggers=(
        'self-review',
    ),
        expected_non_triggers=(
        'targeted-validation',
    ),
        category='pre-phase',
        notes='Explicit diff review request before testing. self-review should trigger.',
    ),
    TriggerCase(
        id='self-review-not-needed-test-request',
        prompt='Run the unit tests for the auth module.',
        expected_triggers=(),
        expected_non_triggers=(
        'self-review',
    ),
        category='pre-phase',
        notes='Direct test command. self-review should NOT trigger.',
    ),
    TriggerCase(
        id='self-review-multi-file-change',
        prompt="I've made changes across 5 files to add the new payment flow. Before running the test suite, let me check if the diff looks clean.",
        expected_triggers=(
        'self-review',
    ),
        expected_non_triggers=(),
        category='pre-phase',
        notes='Multi-file change with explicit intent to review diff before testing.',
    ),
    TriggerCase(
        id='incremental-4pr',
        prompt='Implement the new analytics pipeline: data ingestion, transformation rules, storage layer, and dashboard integration. Each layer is a separate PR — 4 PRs total.',
        expected_triggers=(),
        expected_non_triggers=(
    ),
        category='pre-phase',
        notes='4 PRs is within the 2-4 PR range. Incremental delivery should apply; no phase escalation needed.',
    ),
    TriggerCase(
        id='design-after-scoping',
        prompt="We've narrowed the task to the notification subsystem, but there are still open design questions: should notifications be push-based or pull-based, and what delivery guarantees do we need?",
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='pre-phase',
        notes="Scope is already defined but design decisions remain. Matches 'scoped-tasking identified the boundary but design decisions remain open'.",
    ),
    TriggerCase(
        id='locate-then-impact',
        prompt='built-in code search found that the pricing logic touches pricing/engine.ts, discount/rules.ts, checkout/summary.ts, and billing/invoice.ts. Now I need to understand which of these will break if I change the base price calculation.',
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(),
        category='pre-phase',
        notes="built-in code search produced 4 candidate files. impact-analysis should now assess the blast radius. Matches 'built-in code search produced 3+ tentative leads'.",
    ),
    TriggerCase(
        id='chain-scope-to-locate',
        prompt="We've narrowed the task to the auth module, but I don't know which file handles token refresh.",
        expected_triggers=(),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='chain-trigger',
        notes='Scope is narrowed (auth module) but exact location unknown. Should chain from scoping to built-in code search.',
    ),
    TriggerCase(
        id='chain-locate-to-plan',
        prompt='built-in code search found the edit points: auth/token.ts and auth/session.ts. Now I need a plan for the changes.',
        expected_triggers=(
        'implementation-planning',
    ),
        expected_non_triggers=(),
        category='chain-trigger',
        notes='Location discovery complete, now needs durable sequencing and verification. implementation-planning should trigger.',
    ),
    TriggerCase(
        id='chain-bugfix-to-cba',
        prompt="I've been diagnosing this bug for a while, checked 10 files, and I have 4 competing theories but no evidence to rank them.",
        expected_triggers=(),
        expected_non_triggers=(
        'bugfix-workflow',
    ),
        category='chain-trigger',
        notes='Bug diagnosis has consumed too much context without convergence. Should chain from bugfix-workflow to context discipline.',
    ),
    TriggerCase(
        id='chain-review-to-validation',
        prompt='Self-review is clean -- no blocking issues in the diff. What should I test?',
        expected_triggers=(
        'targeted-validation',
    ),
        expected_non_triggers=(
        'self-review',
    ),
        category='chain-trigger',
        notes='Review complete, now needs test selection. Should chain from self-review to targeted-validation.',
    ),
    TriggerCase(
        id='chain-plan-to-design',
        prompt="I tried to plan the implementation but realized I can't sequence the steps because there are two competing design approaches.",
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
    ),
        category='chain-trigger',
        notes='Planning blocked by unresolved design choice. design-before-plan should trigger.',
    ),
    TriggerCase(
        id='chain-minimal-to-impact',
        prompt='I was making a small fix to the validator, but it turns out 5 other modules import this function.',
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(),
        category='chain-trigger',
        notes='Small patch discovered to have wide blast radius. Should escalate from smallest-change discipline to impact-analysis.',
    ),
    TriggerCase(
        id='chain-refactor-to-design',
        prompt="I started extracting the shared helper but realized the refactor changes the module's public interface.",
        expected_triggers=(
        'design-before-plan',
    ),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='chain-trigger',
        notes='Refactor touches public contract. Should escalate from safe-refactor to design-before-plan.',
    ),
    TriggerCase(
        id='chain-parallel-to-conflict',
        prompt='Two subagents disagree: one says the timeout is in the client, the other blames the server.',
        expected_triggers=(),
        expected_non_triggers=(
        'multi-agent-protocol',
    ),
        category='chain-trigger',
        notes='Parallel investigation produced conflicting results. Should chain from multi-agent-protocol to multi-agent synthesis.',
    ),
    TriggerCase(
        id='doc-only-change',
        prompt='Update the README to add installation instructions for the new CLI tool.',
        expected_triggers=(),
        expected_non_triggers=(
        'design-before-plan',
        'safe-refactor',
    ),
        category='baseline-control',
        notes='Pure documentation change. No skill should be required.',
    ),
    TriggerCase(
        id='info-query',
        prompt='What database does this project use? I see references to both PostgreSQL and Redis in the config.',
        expected_triggers=(),
        expected_non_triggers=(
        'scoped-tasking',
        'impact-analysis',
    ),
        category='baseline-control',
        notes='Information query with no intent to change code. No skill needed.',
    ),
    TriggerCase(
        id='git-operation',
        prompt='Commit my current changes and push to the feature branch.',
        expected_triggers=(),
        expected_non_triggers=(
        'self-review',
        'targeted-validation',
    ),
        category='baseline-control',
        notes='Git housekeeping. Exempt from skill activation.',
    ),
    TriggerCase(
        id='scope-vs-locate',
        prompt="Users are complaining that search is broken, but I don't know if they mean the product search, the user search, or the log search. Can you help figure out which one?",
        expected_triggers=(
        'scoped-tasking',
    ),
        expected_non_triggers=(),
        category='confusion-boundary',
        notes='Ambiguous scope needs narrowing, not code discovery. scoped-tasking should trigger to clarify which subsystem.',
    ),
    TriggerCase(
        id='locate-vs-scope',
        prompt='Find where the payment webhook handler is defined. I know it exists somewhere in the billing module but I need the exact file.',
        expected_triggers=(),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='confusion-boundary',
        notes='Clear scope (billing module), unclear location. built-in code search should trigger, not scoped-tasking.',
    ),
    TriggerCase(
        id='minimal-vs-refactor',
        prompt='While fixing the null check in the order validator, I noticed 200 lines of dead comments, 3 unused imports, and inconsistent naming. I want to clean it all up but the task is just the null check fix.',
        expected_triggers=(),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='confusion-boundary',
        notes='Cleanup temptation beyond task scope. smallest-change discipline should constrain, not safe-refactor.',
    ),
    TriggerCase(
        id='refactor-vs-minimal',
        prompt='Simplify the three duplicate error-handling blocks in the API handlers into a shared middleware. Keep the external interface unchanged.',
        expected_triggers=(
        'safe-refactor',
    ),
        expected_non_triggers=(),
        category='confusion-boundary',
        notes='Intentional structural cleanup is a refactor goal. safe-refactor should guide it, not smallest-change discipline.',
    ),
    TriggerCase(
        id='scope-vs-plan',
        prompt="The ticket says 'improve error handling across the backend' but that could mean dozens of files. Before we plan anything, what are we actually trying to change here?",
        expected_triggers=(
        'scoped-tasking',
    ),
        expected_non_triggers=(
    ),
        category='confusion-boundary',
        notes='Task boundary is undefined — must scope first.',
    ),
    TriggerCase(
        id='plan-vs-scope',
        prompt='The scope is clear: add retry logic to the three API clients in pkg/http/. I need to figure out the right order of changes and what assumptions to validate first.',
        expected_triggers=(
        'implementation-planning',
    ),
        expected_non_triggers=(
        'scoped-tasking',
    ),
        category='confusion-boundary',
        notes='Scope is already defined (3 files in pkg/http/). Sequencing and assumptions now belong to implementation-planning, not further scoping.',
    ),
    TriggerCase(
        id='discover-analyze-plan',
        prompt="I need to modify user authentication in this unfamiliar codebase. I don't know where the auth code lives, the change might affect several modules, and I'll need a plan before I start editing.",
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(
    ),
        category='combo-trigger',
        notes='Unfamiliar codebase + multi-module impact + multi-step edit. Three skills should co-activate.',
    ),
    TriggerCase(
        id='refactor-with-constraint',
        prompt="Clean up the duplicate validation logic across the three form handlers, but don't change any public API signatures and don't touch anything outside the forms directory.",
        expected_triggers=(
        'safe-refactor',
    ),
        expected_non_triggers=(
        'design-before-plan',
    ),
        category='combo-trigger',
        notes='Structural cleanup with explicit scope constraint. Both safe-refactor and smallest-change discipline should co-activate.',
    ),
    TriggerCase(
        id='design-impact-incremental',
        prompt='Add a refund capability to the order system. We need to decide between a state-machine approach and an event-sourcing approach, assess which existing payment flows are affected, and deliver it in 3 PRs.',
        expected_triggers=(
        'design-before-plan',
        'impact-analysis',
    ),
        expected_non_triggers=(
    ),
        category='combo-trigger',
        notes='Design choice + blast radius assessment + multi-PR delivery. Three skills should co-activate.',
    ),
    TriggerCase(
        id='impact-2-callers',
        prompt="Change the return type of formatDate. It's only called by the UserProfile component and the AdminPanel component — two callers total.",
        expected_triggers=(),
        expected_non_triggers=(
        'impact-analysis',
    ),
        category='numeric-boundary',
        notes='2 callers is below the 3-caller threshold. impact-analysis should NOT trigger.',
    ),
    TriggerCase(
        id='impact-3-callers',
        prompt="Change the return type of formatDate. It's called by UserProfile, AdminPanel, and ReportExporter — three separate modules depend on it.",
        expected_triggers=(
        'impact-analysis',
    ),
        expected_non_triggers=(),
        category='numeric-boundary',
        notes='Exactly 3 callers matches the threshold. impact-analysis SHOULD trigger.',
    ),
    TriggerCase(
        id='knowledge-init-project-kb',
        prompt='This repo still has docs/durable project knowledge. Dry-run a migration into Worktrail and tell me what would become pending candidates.',
        expected_triggers=(),
        expected_non_triggers=(
    ),
        category='knowledge-driven',
        notes='Explicit request to bridge legacy KDD docs into Worktrail. durable project knowledge should trigger.',
    ),
    TriggerCase(
        id='knowledge-capture-runbook',
        prompt='Worktrail is not available in this old repo. We just learned the staging API requires a special base path and a keyauth header. Please capture that as reusable project knowledge after the fix is verified.',
        expected_triggers=(),
        expected_non_triggers=(
        'safe-refactor',
    ),
        category='knowledge-driven',
        notes='Reusable implementation finding should use the legacy KDD fallback when Worktrail is unavailable.',
    ),
    TriggerCase(
        id='knowledge-agents-required',
        prompt='AGENTS.md says this repo uses docs/durable project knowledge. Before changing the payment adapter, read the relevant legacy project knowledge and migrate it with worktrail import kdd if the user approves.',
        expected_triggers=(),
        expected_non_triggers=(
    ),
        category='knowledge-driven',
        notes='Project governance explicitly references legacy KDD and should trigger the bridge workflow.',
    ),
    TriggerCase(
        id='knowledge-local-private-context',
        prompt='Record my local staging project IDs and temporary request IDs for this debugging session, but keep them out of shared docs and version control.',
        expected_triggers=(),
        expected_non_triggers=(
        'self-review',
    ),
        category='knowledge-driven',
        notes='Local-only knowledge should use local active log, not shared project docs.',
    ),
    TriggerCase(
        id='knowledge-control-simple-question',
        prompt='What is the difference between project documentation and local notes?',
        expected_triggers=(),
        expected_non_triggers=(),
        category='knowledge-driven',
        notes='Conceptual one-off question. No repository knowledge workflow is needed.',
    ),
)


REVIEW_LOOP_MAINCHAIN_CASES: tuple[TriggerCase, ...] = (
    TriggerCase(
        id='req-review-explicit',
        prompt='评审一下这份需求文档，看看完整性和可验证性如何',
        expected_triggers=('requirements-review-loop',),
        expected_non_triggers=('design-review-loop', 'plan-review-loop', 'code-review-loop', 'test-review-loop'),
        category='review-loop-mainchain',
        notes='Explicit requirements review request.',
    ),
    TriggerCase(
        id='req-review-prd',
        prompt='Review this PRD to check if all acceptance criteria are clear and verifiable.',
        expected_triggers=('requirements-review-loop',),
        expected_non_triggers=('design-review-loop', 'code-review-loop'),
        category='review-loop-mainchain',
        notes='PRD review with focus on acceptance criteria.',
    ),
    TriggerCase(
        id='req-review-user-story',
        prompt='帮我审核用户故事的边界条件和失败场景是否齐全',
        expected_triggers=('requirements-review-loop',),
        expected_non_triggers=('design-review-loop', 'plan-review-loop'),
        category='review-loop-mainchain',
        notes='User story review focused on completeness.',
    ),
    TriggerCase(
        id='design-review-rfc',
        prompt='Review this RFC for architecture soundness and rollback design',
        expected_triggers=('design-review-loop',),
        expected_non_triggers=('requirements-review-loop', 'plan-review-loop', 'code-review-loop'),
        category='review-loop-mainchain',
        notes='RFC review.',
    ),
    TriggerCase(
        id='design-review-adr-contract',
        prompt='Review ADR-0042 for required sections, decision drivers, realistic alternatives, positive and negative consequences, status, supersedes links, and revisit conditions.',
        expected_triggers=('design-review-loop',),
        expected_non_triggers=('plan-review-loop', 'code-review-loop'),
        category='review-loop-mainchain',
        notes='ADR content review should use the adr-rfc design review path.',
    ),
    TriggerCase(
        id='design-review-interface',
        prompt='帮我评审这个接口设计，看看契约定义是否清晰',
        expected_triggers=('design-review-loop',),
        expected_non_triggers=('code-review-loop',),
        category='review-loop-mainchain',
        notes='Interface design review.',
    ),
    TriggerCase(
        id='design-review-fang-an',
        prompt='评审一下我的技术方案，看看有没有遗漏失败处理',
        expected_triggers=('design-review-loop',),
        expected_non_triggers=('plan-review-loop', 'requirements-review-loop'),
        category='review-loop-mainchain',
        notes='Disambiguation: bare 方案 belongs to design.',
    ),
    TriggerCase(
        id='plan-review-migration',
        prompt='Review this migration plan for executability and rollback safety',
        expected_triggers=('plan-review-loop',),
        expected_non_triggers=('design-review-loop', 'code-review-loop'),
        category='review-loop-mainchain',
        notes='Migration plan review.',
    ),
    TriggerCase(
        id='plan-review-impl',
        prompt='评审一下实施方案，确认顺序和验证步骤都清楚',
        expected_triggers=('plan-review-loop',),
        expected_non_triggers=('design-review-loop',),
        category='review-loop-mainchain',
        notes='Disambiguation: 实施方案 belongs to plan, not design.',
    ),
    TriggerCase(
        id='plan-review-task',
        prompt='帮我评审实施计划是否每一步都有具体文件落点',
        expected_triggers=('plan-review-loop',),
        expected_non_triggers=('requirements-review-loop', 'code-review-loop'),
        category='review-loop-mainchain',
        notes='Task plan review on file-level landing.',
    ),
    TriggerCase(
        id='plan-review-adr-alignment',
        prompt='Review this implementation plan against Accepted ADR-0042 and verify that every constrained step cites it while Proposed and superseded ADRs are excluded.',
        expected_triggers=('plan-review-loop',),
        expected_non_triggers=('design-review-loop', 'code-review-loop'),
        category='review-loop-mainchain',
        notes='Plan review should include active Accepted ADR alignment and traceability.',
    ),
    TriggerCase(
        id='code-review-diff',
        prompt='Review the working tree diff for correctness, regressions, and scope control',
        expected_triggers=('code-review-loop',),
        expected_non_triggers=('plan-review-loop', 'test-review-loop'),
        category='review-loop-mainchain',
        notes='Code diff review.',
    ),
    TriggerCase(
        id='code-review-commit',
        prompt='帮我 review 一下这次 commit，看看有没有 bug 或安全问题',
        expected_triggers=('code-review-loop',),
        expected_non_triggers=('design-review-loop', 'test-review-loop'),
        category='review-loop-mainchain',
        notes='Commit-level code review.',
    ),
    TriggerCase(
        id='code-review-pr',
        prompt='Review this pull request: check description quality, CI status, and the diff itself',
        expected_triggers=('code-review-loop',),
        expected_non_triggers=('plan-review-loop',),
        category='review-loop-mainchain',
        notes='PR-level review (covers Optional checks).',
    ),
    TriggerCase(
        id='test-review-cases',
        prompt='评审测试用例的覆盖度和断言质量，看看是否有 flaky 风险',
        expected_triggers=('test-review-loop',),
        expected_non_triggers=('code-review-loop',),
        category='review-loop-mainchain',
        notes='Test case review.',
    ),
    TriggerCase(
        id='test-review-coverage',
        prompt='Review the coverage matrix and test strategy for completeness',
        expected_triggers=('test-review-loop',),
        expected_non_triggers=('requirements-review-loop', 'code-review-loop'),
        category='review-loop-mainchain',
        notes='Coverage and strategy review.',
    ),
    TriggerCase(
        id='test-review-not-code',
        prompt='帮我看看新加的单元测试，断言够不够强',
        expected_triggers=('test-review-loop',),
        expected_non_triggers=('code-review-loop',),
        category='review-loop-mainchain',
        notes='Distinguish reviewing tests vs reviewing code under test.',
    ),
    TriggerCase(
        id='disambig-fang-an',
        prompt='评审一下方案',
        expected_triggers=('design-review-loop',),
        expected_non_triggers=('code-review-loop', 'requirements-review-loop'),
        category='review-loop-mainchain',
        notes='Bare 方案 → design.',
    ),
    TriggerCase(
        id='disambig-shi-shi-fang-an',
        prompt='评审一下实施方案',
        expected_triggers=('plan-review-loop',),
        expected_non_triggers=('design-review-loop',),
        category='review-loop-mainchain',
        notes='实施方案 → plan.',
    ),
    TriggerCase(
        id='disambig-jie-kou-design',
        prompt='评审一下我设计的接口',
        expected_triggers=('design-review-loop',),
        expected_non_triggers=('code-review-loop',),
        category='review-loop-mainchain',
        notes='Interface design phase → design, not code.',
    ),
    TriggerCase(
        id='disambig-bei-ce-dai-ma',
        prompt='评审一下被测代码',
        expected_triggers=('code-review-loop',),
        expected_non_triggers=('test-review-loop',),
        category='review-loop-mainchain',
        notes='Code under test → code-review-loop, not test-review-loop.',
    ),
    TriggerCase(
        id='disambig-bare-review-no-target',
        prompt='帮我评审一下',
        expected_triggers=(),
        expected_non_triggers=('requirements-review-loop', 'design-review-loop', 'plan-review-loop', 'code-review-loop', 'test-review-loop'),
        category='review-loop-mainchain',
        notes='Bare 评审 without target → no main-chain skill should auto-trigger; ask for clarification.',
    ),
)


ALL_CASES: tuple[TriggerCase, ...] = (
    *TASK_TYPE_CASES,
    *BOUNDARY_CASES,
    *DISCOVERY_CASES,
    *CONTEXT_BUDGET_CASES,
    *MULTI_AGENT_CASES,
    *PHASE_CASES,
    *PRE_PHASE_CASES,
    *CHAIN_TRIGGER_CASES,
    *BASELINE_CONTROL_CASES,
    *CONFUSION_BOUNDARY_CASES,
    *COMBO_TRIGGER_CASES,
    *NUMERIC_BOUNDARY_CASES,
    *KNOWLEDGE_DRIVEN_CASES,
    *REVIEW_LOOP_MAINCHAIN_CASES,
    *ALL_TRIGGER_CASES,
)


CATEGORIES: tuple[str, ...] = tuple(sorted({c.category for c in ALL_CASES}))


def cases_by_category(category: str) -> tuple[TriggerCase, ...]:
    """Return all TriggerCases whose `category` field matches."""
    return tuple(c for c in ALL_CASES if c.category == category)


def resolve_trigger_case(case_id: str) -> TriggerCase:
    """Look up a single TriggerCase by its `id`. Raises KeyError if absent."""
    for c in ALL_CASES:
        if c.id == case_id:
            return c
    raise KeyError(f'no TriggerCase with id={case_id!r}')

    raise KeyError(f'no TriggerCase with id={case_id!r}')




