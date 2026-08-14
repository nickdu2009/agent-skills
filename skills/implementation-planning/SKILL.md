---
name: implementation-planning
description: "Define a durable, file-grounded implementation plan from a settled requirement/design, with sequencing, acceptance traceability, per-step verification, authorization boundaries, ownership, risks, and rollback. Use for multi-file, multi-module, staged, or PR-sized work whose direction is settled but execution ordering still needs a reviewable artifact. Do not use for a tiny obvious edit or while major design choices remain open."
metadata:
  version: "0.3.0"
  tags: "planning, sequencing, traceability"
---

# implementation-planning

Produce an executable plan artifact, not production code. Another agent should be able to follow it without reopening design, ownership, or sequencing decisions.

## Activation and boundary

Activate when scope/design is settled and work spans multiple files, modules, increments, shared write surfaces, risky sequencing, or non-trivial validation/rollback. Use a lightweight inline plan for a small local edit. Return to `requirement-interview`, `design-before-plan`, or `architecture-design` when the product or architecture direction is not settled.

## Hard constraint

**A plan records authorized execution; it never invents behavior or itself authorize code edits, schema/dependency changes, external access, deployment, commit/push, destructive cleanup, or production-like validation.**

A plan-only or “before coding” request stops after the artifact. Observable defaults, thresholds, matching, retries, fallbacks, permissions, data semantics, and failure strategies need a confirmed source before becoming executable steps.

## Core workflow

1. **Check the ceremony level.** If ordering, landing, and validation fit a short inline plan, deactivate. Otherwise create a durable artifact.
2. **Resolve planning inputs.** Read supplied requirements, design/architecture, scoped boundary, impact summary, and ADR artifacts. When ADR lifecycle is present, read [upstream-artifacts.md](references/upstream-artifacts.md); only active Accepted decisions constrain implementation. Proposed, conflicting, replaced, or ambiguous decisions go back to design/review.
3. **Lock authority and truth.** Record formal sources, selected compatibility strategy, business/source-of-truth owner, non-truth surfaces, shared write-surface owners, and every action needing separate approval. Do not let UI state, streams, caches, logs, generated artifacts, or mocks silently become truth.
4. **Run a planning clarification gate.** Ask only about increment boundaries, sequencing, validation, rollback, risk tolerance, ownership, and artifact location. After two unproductive rounds, stop. Send requirement/design gaps upstream.
5. **Build traceability.** Assign `AC1`, `AC2`, … to source acceptance conditions. Every criterion must map to at least one step and verification.
6. **Choose increments and ownership.** Decide one pass or 2–4 mergeable increments. Fill `[parallelism: ...]` with independent lanes, sequential blockers, shared write surfaces, and delegation. A shared contract, migration, package/lock file, root config, composition surface, or test config has one writer.
7. **Close pre-coding gates.** When contracts, schema, security, dependencies, external services, runtime conditions, authorization, or behavioral assumptions remain open, read [gate-00.md](references/gate-00.md). Mechanical assumptions may continue only with validation; behavioral assumptions block coding.
8. **Draft steps.** Each step names landing files/modules/interfaces, dependency, action, constraining ADR IDs, verification, and covered ACs. Keep decisions out of steps. For delegated execution, read [delegation-task-card.md](references/delegation-task-card.md) and emit complete task cards with disjoint ownership.
9. **Add failure margins.** Record sequencing hazards, compatibility risk, rollback boundary, mitigation, and residual risk. Verification must name the narrow check that makes the step observable.
10. **Write and hand off.** Always read [plan-template.md](references/plan-template.md). Use the user’s path; otherwise propose `.plans/<topic>-plan.md`. Recommend `artifact-review-loop` with `artifact_type: plan` for non-trivial/high-impact work. Stop after planning unless the user explicitly requested implementation.

Read [examples.md](references/examples.md) only when calibration is useful.

## Planning decision gates

Before sequencing, classify every unresolved item:

- A `mechanical_assumption` concerns a path, command, internal landing, or other behavior-preserving detail. It may remain only with a concrete validation method and rollback margin.
- A `behavioral_assumption` changes observable results, data, permissions, security, compatibility, matching, retries, fallback, or failure semantics. It enters GATE-00 and blocks affected coding.
- A `design_gap` changes architecture, interfaces, data ownership, compatibility strategy, or technology choice. It returns upstream; the planner does not decide it.
- An `authorization_gap` names an otherwise-designed action the user has not authorized. Keep the action out of execution until its exact scope and owner approval are recorded.

Accepted plan text settles sequencing only to the extent stated. It does not turn Proposed ADRs into constraints or turn approval of product behavior into permission to edit code during a plan-only turn.

## Step and rollback quality gate

A step is executable only when it records:

- a narrow landing surface and single owner for any shared write
- prerequisites and sequence dependency
- the behavior-preserving implementation intent, without reopening design
- relevant Accepted ADR IDs
- the smallest sufficient verification with an observable pass condition
- covered acceptance IDs
- stop/escalate conditions when a prerequisite or contract differs from the plan

Order steps so contracts and truth models stabilize before dependent adapters/UI, additive compatibility precedes destructive cleanup, and validation exists before irreversible boundaries. Do not parallelize tasks that share contracts, migrations, locks/packages, root configuration, app composition, fixtures, or a state machine.

For each material risk, state trigger, impact, affected step, mitigation, rollback action, and the last safe rollback point. “Revert the change” is insufficient for schema/data migration, mixed-version compatibility, external side effects, or one-way cleanup. If rollback is impossible, record the forward-recovery strategy and require explicit owner acceptance before implementation.

The final coverage check must prove every AC maps to a step and verification, every step maps to an authorized source, every shared surface has one writer, and every blocking gate names the steps it prevents. A plan with “run tests,” “update backend,” or unowned rollout choices is not complete.

Do not create the default plan path when the user requested an in-thread plan only; propose the path and preserve the requested artifact destination.

## Input contract

Accept a settled design brief/architecture, clear requirement artifact, scoped boundary, impact summary, active Accepted ADRs, or a combination. Optional inputs include preferred plan path, validation style, rollout/rollback constraints, and increment expectations. Read any supplied path before planning.

## Output contract

Return:

- `sequence`: ordered steps/increments and dependencies
- `file_landing`: concrete files, modules, interfaces, and shared owners
- `verify`: per-step and overall checks
- `risks`: mitigation, rollback, and residual risk
- `traceability`: acceptance criteria → steps/checks
- `authorization`: allowed work, non-authorized actions, approval gates
- `truth_ownership`: business truth owner and non-truth surfaces
- `parallelism`: lanes, blockers, shared writes, delegation stance
- `task_cards`: complete cards when delegation is planned
- `adr_alignment`: active constraining ADRs and affected steps

## Contract

### Preconditions

- Requirement/design direction is settled and concrete landing surfaces can be identified.
- The work needs more than a lightweight inline plan.

### Postconditions

- `status: completed` includes `sequence`, `file_landing`, `verify`, `risks`, and `traceability`.
- Authorization, truth ownership, shared writers, gates, and ADR alignment are explicit when applicable.
- The artifact is ready for plan review or authorized implementation without basic sequencing decisions.

### Invariants

- Planning precedes coding and remains distinct from design selection.
- Every step has landing, verification, and acceptance traceability.
- Plan acceptance never expands implementation or lifecycle authorization.

### Downstream Signals

- `sequence` and `file_landing` define execution order and write scope.
- `verify`, `risks`, and `traceability` define observable completion and rollback margin.
- Gates and task cards define stop conditions and ownership handoffs.

## Failure Handling

### Common Failure Causes

- Design is unresolved, blast radius/ownership is unknown, or required authorization and behavioral decisions are missing.

### Retry Policy

- Ask about a planning-layer gap for at most two productive rounds; then stop or escalate upstream.

### Fallback

- Use requirements/design/architecture clarification for upstream gaps, `impact-analysis` for speculative blast radius, or a lightweight inline plan for tiny work. Put missing execution authorization in a pre-coding gate.

### Low Confidence Handling

- Preserve mechanical assumptions with validation, keep behavioral assumptions blocking, and require `artifact-review-loop` with `artifact_type: plan` before implementation.

## Output Example

```text
[output: implementation-planning | completed medium | sequence:"contract then service then adapter" file_landing:"contract, service, adapter, tests" verify:"targeted contract/unit/integration checks" risks:"compatibility and rollback order" traceability:"AC1->S1/S2; AC2->S3" adr_alignment:"ADR-0001->S1" | next:artifact-review-loop(type=plan)]
```

## Deactivation Trigger

- The plan is handed to plan review or authorized implementation.
- An upstream decision becomes necessary.
- The task shrinks to a local change that needs only inline planning.
