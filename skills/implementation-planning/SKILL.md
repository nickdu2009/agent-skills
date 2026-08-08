---
name: implementation-planning
description: "Guide implementation planning by turning a settled requirement/design into a concrete plan that is sequenced, file-grounded, verifiable, and reviewable. The skill writes or proposes a plan document, not production code. Use when a task is ready to implement but still needs explicit execution ordering, per-step validation, rollback thinking, or multi-file / multi-PR coordination. Accepts either a design brief or a requirement document whose design direction is already clear. Do NOT use for small single-file edits where AGENTS.md §4 short planning is enough, or when major design choices are still open (use design-before-plan first)."
metadata:
  version: "0.2.0"
  tags: "coding, agents, orchestration, planning"
---

# implementation-planning

Create a durable implementation plan before coding when lightweight inline planning is no longer enough.

This skill exists to handle the gap between "the design direction is settled" and "implementation can proceed safely." It produces a reviewable plan artifact with explicit sequencing, file-level landing, verification, and rollback notes.

# Purpose

Translate a settled requirement and/or design direction into an executable implementation plan. Core goals:

- Convert vague "we should do this next" thinking into ordered, verifiable steps.
- Ground each step in concrete files, modules, or interfaces rather than abstract intent.
- Preserve traceability from requirements / acceptance criteria to implementation steps.
- Preserve explicit authorization, ownership, and source-of-truth boundaries before execution starts.
- Make risks, rollback points, and sequencing explicit before code changes begin.
- Produce a plan artifact that can be handed to `plan-review-loop` or implementation directly.

Success criterion: on exit, the agent has produced a plan document specific enough that another agent could implement it without reopening major sequencing or ownership questions.

# When to Use

- The task spans multiple files, modules, or PR-sized increments.
- The design direction is already settled, but implementation ordering still matters.
- The user asks for an implementation plan / execution plan / task breakdown / 实施计划 / 执行计划.
- The work needs a written plan artifact before coding or review.
- Impact analysis has clarified the blast radius and now the changes must be sequenced.
- Requirements are clear enough to implement, but validation, rollback, or file landing is still implicit.

# When Not to Use

- For trivial or single-file edits where `AGENTS.md` Behavioral Guidelines §4 short planning is sufficient.
- When major design choices, contracts, or acceptance criteria are still unresolved — use `design-before-plan`.
- When the requirement itself is still vague or contradictory — use `requirement-interview`.
- When the user only wants artifact review of an existing plan — use `plan-review-loop`.
- When the user explicitly wants exploratory implementation ("try it first and see").

Boundary rule: this skill plans *how to execute an already-understood change*. It does not own business clarification or design comparison.

# Core Rules

- Do not write production code while planning.
- Completing a plan does not authorize coding in the same turn when the user asked for design/plan only, contract formation, or work "before coding". Stop after the plan artifact and wait for an explicit implement / proceed-with-coding request (or hand off to `plan-review-loop`).
- Confirmed behavior authorization settles product semantics for the plan; it is not by itself a coding start signal while the ask remains plan-scoped.
- Do not reopen settled design questions unless a blocking inconsistency is discovered.
- Do not treat lightweight §4 short planning as a reason to activate this skill; this skill is for durable, reviewable planning.
- Every implementation step must name its landing surface and its verification.
- Every acceptance criterion must be covered by at least one planned step.
- Every non-trivial risk must have a mitigation or rollback note.
- Treat only active ADRs with `Status: Accepted` as frozen decisions; Proposed, Deprecated, Superseded, historical, retired, or replaced ADRs are not implementation constraints.
- Never introduce a new architecture decision silently inside an implementation step.
- A plan being accepted means "this is a valid execution source"; it does not by itself authorize code edits, schema changes, dependency/tooling changes, external service access, deployment, commits, pushes, destructive cleanup, or production data access.
- Name the business/source-of-truth owner. UI state, streams, generated artifacts, logs, caches, and mock data are not truth unless an accepted design explicitly says so.
- Shared write surfaces such as public contracts, migrations, package/lock files, root config, app composition, and test configuration need a single named owner.
- If a plan delegates work to coding agents, each task card must include these fields: goal, prerequisites, must-read, owns, must-not-touch, actions, expected outputs, verify, done conditions, stop/escalate conditions, and handoff.

# Execution Pattern

0. **Check whether durable planning is actually needed**:
   - If the task is small, local, and obvious, defer to `AGENTS.md` §4 short planning instead of activating this skill.
   - If the task needs a real plan artifact, continue.

1. **Validate planning inputs**:
   - Collect available design brief, requirement doc, scoped boundary, impact summary, and ADR artifacts/paths.
   - Decide whether the design direction is already settled enough to plan.
   - Resolve the active Accepted ADR set using [upstream-artifacts.md](upstream-artifacts.md).
   - Send Proposed, conflicting, or activity-ambiguous decisions back to design/review.
   - If not settled, hand off to `design-before-plan` or `requirement-interview`.

2. **Lock execution authority and source boundaries**:
   - Record the formal input documents and accepted decisions that govern the plan.
   - State the selected compatibility strategy: clean-state, additive compatibility, dual-read/write, or migration bridge. If the strategy is not explicit, ask instead of assuming.
   - Identify truth owners and non-truth surfaces, especially across UI / API / worker / database / generated artifact boundaries.
   - List actions that require separate authorization before execution, such as dependency installs, schema migrations, external services, deploys, commits, pushes, deletes, or production-like validation.

3. **Run the planning-clarification gate when needed**:
   - Ask only planning-layer questions first: increment boundaries, sequencing, validation preference, risk tolerance, rollback expectations, and plan file location.
   - Ask at most 3-5 questions per round.
   - If a major design or requirement gap is discovered, stop and hand back upstream instead of silently planning through it.

4. **Build the acceptance map**:
   - List the requirement / design acceptance criteria that must be covered.
   - Assign short identifiers (for example `AC1`, `AC2`) so steps can trace back to them.

5. **Decide the implementation structure**:
   - Determine whether the work is one pass, phased, or split into 2-4 mergeable increments.
   - Fill the §4-style `[parallelism: ...]` block for independent lanes, blockers, shared write surfaces, and delegation stance.
   - Add a `GATE-00` or equivalent pre-coding gate when contracts, schema, security, dependencies, external services, runtime environment conditions, or unconfirmed behavioral assumptions (defaults, matching, thresholds, retries, fallbacks, failure semantics) must be closed before production code changes.
   - Classify residual assumptions: mechanical (paths, commands, internal landing) may continue with a validation method; behavioral assumptions must enter `GATE-00` with `source` / `owner decision` / `done condition` and block coding until closed.

6. **Draft the executable steps**:
   - For each step, record: landing files/modules, dependency, action summary, verification check, and covered acceptance criteria.
   - Cite every constraining ADR ID in `Sources and Alignment` and in each affected step.
   - Keep steps implementation-facing, not design-theory-facing.
   - For multi-agent execution, write task cards with explicit ownership and stop conditions rather than generic task bullets.

7. **Add risk and rollback coverage**:
   - Identify critical failure points, sequencing hazards, compatibility risks, and rollback boundaries.
   - Add concrete mitigation and rollback notes to the plan artifact.

8. **Write or update the plan artifact**:
   - Prefer a dedicated Markdown plan file.
   - Default location: `.plans/<topic>-plan.md` unless the user specifies another path.

9. **Recommend the next step**:
   - Suggest `plan-review-loop` when the plan is non-trivial or high impact.
   - If the current ask is plan-only / "before coding", stop after the plan; do not start production edits.
   - Only hand off to implementation in the same turn when the user explicitly asked to implement or proceed with coding; keep risks explicit.

# Input Contract

Provide one or more of:

- a settled design brief from `design-before-plan`
- a requirement document / PRD / requirement-clarification result whose design direction is already clear
- a scoped boundary from `scoped-tasking`
- an impact summary from `impact-analysis`
- active Accepted ADR artifacts or paths

Optional but helpful:

- preferred plan path or file location
- preferred validation style (unit / integration / manual)
- rollout / rollback constraints
- multi-PR or increment expectations

If the user provides only a file path to a requirement or design document, read that file before planning.
For upstream artifact and ADR activity rules, read [upstream-artifacts.md](upstream-artifacts.md).

# Output Contract

Return:

- `sequence`: ordered implementation steps and dependency structure
- `file_landing`: the concrete files, modules, or interfaces each step touches
- `verify`: per-step and overall validation checks
- `risks`: rollback, mitigation, and residual implementation risks
- `traceability`: mapping from acceptance criteria to implementation steps
- `authorization`: explicit non-authorized actions and required approval gates
- `truth_ownership`: source-of-truth owner and non-truth surfaces
- `task_cards`: optional task-card matrix for delegated or multi-agent execution

The plan file includes:

- sources and alignment, including constraining ADR IDs
- authorization boundaries and source-of-truth ownership
- acceptance criteria and traceability
- the `[parallelism: ...]` block
- pre-coding gate(s) for unresolved contracts, security, schema, dependencies, or external services
- ordered steps with landing, dependency, action, verify, ACs, and ADR IDs
- task cards when execution will be delegated
- risks, mitigation, and rollback
- coverage check and residual assumptions
- next handoff

Use [plan-template.md](plan-template.md) for the complete user-facing shape.

# Guardrails

- Do not activate this skill just to produce a 2-3 bullet short plan; that belongs to `AGENTS.md` §4.
- Do not silently make business or design decisions under the label of planning.
- Do not treat unconfirmed behavioral assumptions as residual notes that still allow coding; put them in `GATE-00`.
- Do not leave step landing vague ("update backend") when a narrower file/module target is known.
- Do not leave verification as "run tests" without saying which test/check matters.
- Do not mark a plan complete while acceptance coverage or rollback notes are missing.
- Do not turn the plan into a changelog or implementation transcript; keep it forward-looking.
- Do not let an agent choose between conflicting formal sources; pause and send the conflict back to design/review.
- Do not use parallelism to justify duplicate fixtures, temporary truth, compatibility aliases, or a second state machine.

# Common Anti-Patterns

- **Recreating the retired lightweight planning form.** The plan is just a tiny inline list of next actions, with no durable artifact, no risk coverage, and no handoff to review. That belongs in §4 short planning, not here.
- **Planning through unresolved design.** The agent notices contract choices are still open but keeps drafting execution steps anyway, producing a false sense of readiness.
- **Abstract steps without landing.** The plan says "update the service" or "handle validation" without naming files, modules, or interfaces.
- **No acceptance traceability.** The plan lists steps, but no one can tell which acceptance criterion each step satisfies or whether anything was missed.
- **Risk-free fiction.** The change clearly touches shared surfaces or staged rollout concerns, but the plan contains no rollback or mitigation strategy.
- **Authorization laundering.** The plan is accepted and the agent treats that as approval to install packages, migrate data, call external services, deploy, commit, push, or delete files.
- **Plan-then-code in one turn.** The user asked for a plan or work "before coding", and the agent finishes the plan then immediately edits production files. Plan completion is not an implement request.
- **Truth drift.** The plan lets UI state, generated artifacts, streams, or mocks become business truth because the real owner was not named.
- **Parallelism over ownership.** The plan splits work across agents while two cards still touch the same contract, migration, root config, package/lock file, or app composition surface.

Keep anti-pattern guidance self-contained; installed skills must not depend on maintainer-only documents.

# Composition

Position: after requirements and design are clear enough to implement, before code changes begin.

Standard forward handoffs:

- → `plan-review-loop`: when the plan should be hardened or reviewed before implementation
- → implementation: when the plan is accepted and the user wants to start coding

Standard upstream dependencies:

- `requirement-interview` clarifies what to build
- `scoped-tasking` narrows the boundary
- `design-before-plan` settles design direction when needed
- `impact-analysis` clarifies blast radius when shared callers or contracts are involved

Deactivate this skill once the implementation plan is written and handed off to `plan-review-loop` or implementation.

# Example

For a two-increment notification API, cite the Accepted ADR governing storage in Sources and Alignment and in the persistence step; keep a Proposed delivery ADR out of the frozen constraint set. Sequence model/service before handler/docs and record the additive-schema rollback boundary.

## Contract

### Preconditions

- The requirement or design direction is clear enough to implement.
- The user wants an implementation/execution plan rather than code edits immediately.
- The agent can identify concrete files, modules, or interfaces that the work will likely touch.

### Postconditions

- `status: completed` includes `sequence`, `file_landing`, `verify`, `risks`, and `traceability`.
- A durable plan artifact exists or is proposed with concrete implementation ordering.
- The plan is specific enough for `plan-review-loop` or implementation to consume without reopening basic sequencing questions.
- Every constraining ADR is active and Accepted, and its ID is traceable to affected steps.
- Authorization boundaries, truth owners, shared write owners, and stop conditions are explicit when relevant.

### Invariants

- Planning precedes coding.
- Design decisions remain distinct from execution sequencing.
- Every planned step stays tied to concrete landing surfaces and verification.
- Plan acceptance is not execution authorization for risky, remote, destructive, or persistence-changing actions.

### Downstream Signals

- `sequence` tells implementation and review what order to follow.
- `file_landing` narrows the expected edit surface for downstream work.
- `verify` tells validation and review which checks make each step observable.
- `risks` marks where rollback margin or extra caution is needed.
- `traceability` shows which acceptance criteria are covered and where.

## Failure Handling

### Common Failure Causes

- The requirement doc exists, but the design direction is still ambiguous.
- The blast radius is unclear because shared callers or interfaces were not analyzed yet.
- The user asks for a plan but has not decided increment boundaries, rollout preference, or acceptance expectations.
- The plan needs security, schema, dependency, external-service, deployment, or repository-write authorization that was not granted.

### Retry Policy

- Ask about the same planning-layer gap at most two rounds.
- If the second round still cannot settle a major planning blocker, stop and escalate upstream rather than drafting a speculative plan.

### Fallback

- Hand off to `requirement-interview` if the requirement itself is not mature.
- Hand off to `design-before-plan` if major design decisions are still open.
- Hand off to `impact-analysis` if the blast radius is still speculative.
- If the task is tiny and obvious, deactivate and use `AGENTS.md` §4 short planning instead.
- If authorization or truth ownership is missing, record it as a pre-coding gate rather than drafting executable steps that assume it.

### Low Confidence Handling

- Mark unsettled implementation assumptions explicitly in the plan artifact.
- Require `plan-review-loop` before implementation when risks or sequencing confidence remain medium or low.

## Output Example

```
[output: implementation-planning | completed medium | sequence:"2 PRs, schema/service before handler/docs" file_landing:"models/preferences.py, services/preferences.py, api/preferences.ts, tests/preferences_*" verify:"unit tests for service, integration test for handler, acceptance map coverage check" risks:"shared client compatibility, additive schema rollback, staged rollout order" traceability:"AC1->PR1, AC2->PR2, AC3->PR2" adr_alignment:"ADR-0001->PR1; Proposed ADR-0002 excluded" | next:plan-review-loop]
```

## Deactivation Trigger

- The plan artifact is written and handed to `plan-review-loop` or implementation.
- Upstream clarification becomes necessary again and the skill must hand back to `requirement-interview`, `design-before-plan`, or `impact-analysis`.
- The task is reduced to a small local change that no longer needs durable planning.
