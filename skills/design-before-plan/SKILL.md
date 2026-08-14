---
name: design-before-plan
description: "Clarify design inputs, compare alternatives, define interface and compatibility contracts, and derive acceptance criteria before implementation planning. Use when multiple approaches are plausible, public or cross-module contracts may change, data migration is involved, or acceptance criteria remain unclear. Do not use when the design is already settled or the task is a simple local fix."
metadata:
  version: "0.2.0"
  tags: "design, contracts, acceptance"
---

# design-before-plan

Produce a reviewable design direction that planning can consume without reopening major choices. This skill creates design artifacts, not production code or an implementation sequence.

## Activation and boundary

Activate after scope is known when the work has competing approaches, public/shared interfaces, cross-module coordination, compatibility choices, schema/data change, or ambiguous acceptance criteria. Defer to `requirement-interview` when the business requirement is immature; use `architecture-design` when component decomposition, technology selection, or deployment topology is the primary task.

## Hard constraint

**Do not plan or implement until one design is selected from authorized inputs, its observable contracts are explicit, and unconfirmed behavioral choices remain open rather than becoming defaults.**

Authorization for observable behavior must come from confirmed requirements, an active Accepted ADR/design, compatibility behavior the task must preserve, or an explicit user decision. This applies to defaults, thresholds, matching, retries, fallbacks, degradation, permissions, data semantics, and failure handling.

## Core workflow

1. **Validate inputs.** Extract functional requirements, confirmed non-functional requirements, constraints, edge cases, stakeholders, and open behavioral decisions. If goal, actors, or main flow is missing, return to requirements clarification.
2. **Enumerate 2–4 alternatives.** Include a minimal-change option where credible. For each record pros, cons, complexity, blast radius, reversibility, and contract impact. Do not add patterns or abstractions merely to create variety.
3. **Check NFR candidates.** Read [nfr-checks.md](references/nfr-checks.md) when security, performance, observability, resilience, or operability may affect the design. Checking a candidate does not authorize it; retain `source`, `status: confirmed|open|assumed`, and `blocking`.
4. **Select and explain.** Choose using confirmed constraints and repository conventions. State gains, sacrifices, rejected alternatives, and revisit conditions. If the choice is still product-driven or unsupported, stop for a decision.
5. **Define interfaces.** For every public/shared boundary specify inputs, outputs, errors, compatibility, ownership, and migration expectations. Do not invent retry or fallback semantics as implementation detail.
6. **Design data change conditionally.** When schemas, stored data, indexes, or ownership change, read [data-migration-checks.md](references/data-migration-checks.md). Require explicit compatibility, rollout, rollback, validation, and loss-tolerance decisions.
7. **Derive acceptance.** Convert requirements into observable must-have conditions and validation boundaries. Keep nice-to-have checks separate. Unconfirmed NFRs or behaviors cannot enter acceptance criteria.
8. **Emit the brief.** Always read [design-brief-format.md](references/design-brief-format.md). If the decision is cross-module/PR, long-lived, or costly to reverse and realistic alternatives existed, also read [adr-format.md](references/adr-format.md) and return a vendor-neutral Proposed ADR candidate. Do not persist it unless explicitly asked.

Read [examples.md](references/examples.md) only when a worked decision helps calibrate detail.

## Decision and authorization gates

Classify every material statement before selection:

- `confirmed_requirement`: user/product-approved observable need
- `accepted_decision`: active Accepted ADR or reviewed design constraint
- `preserved_compatibility`: behavior/interface explicitly in scope to retain
- `mechanical_assumption`: internal choice that preserves all observable contracts
- `open_behavior`: missing owner decision; blocks any affected chosen design or acceptance criterion

Mechanical assumptions may guide exploration when paired with a validation method. They must return to open behavior if they affect users, data, permissions, security, compatibility, or failure handling. “Common practice,” a framework default, or an NFR checklist item is not an authorization source.

Do not force two artificial alternatives when only one requirement-compatible local implementation exists. State why comparison is unnecessary. Conversely, do not collapse materially different compatibility, ownership, data, or failure models into one option. A design is selectable only when its decisive trade-off is supported and no blocking behavior is hidden inside “implementation detail.”

## Design quality gate

Before completion, confirm:

- Alternatives use the same confirmed requirements and evaluation criteria.
- `chosen_design` states rationale, sacrificed qualities, reversibility, and deferred decisions.
- Each interface names producer/consumer ownership, types or semantic shape, error responsibility, versioning, and compatibility. Exact wire schemas are required only when the design boundary needs them.
- Every public-contract change has a migration/coexistence story or an explicit clean-break decision from the owner.
- Schema/data work identifies truth ownership and irreversible operations; it does not smuggle rollout thresholds or loss tolerance into the plan.
- Acceptance checks observe required behavior and contracts without dictating private implementation.
- Existing Accepted ADRs are `linked_adrs`; a new decision stays Proposed in `adr_candidates`. Proposed candidates never constrain the current design as though accepted.

If two viable options remain tied on a product-owned trade-off, return a bounded choice with impacts instead of marking either as `chosen_design`. If the choice changes system decomposition or deployment topology, hand off to `architecture-design` rather than stretching this skill.

## Traceability and stopping

For every chosen element, retain the requirement, Accepted ADR, compatibility contract, or explicit decision that authorized it. Map each acceptance criterion back to a requirement and forward to the contract or design element it validates. If an option can pass only by assuming an unresolved behavior, mark it non-viable until that decision is supplied; do not score the assumption as a benefit.

Stop after the brief on a design-only request. A confirmed design authorizes its semantics but does not authorize planning, code edits, persistence, deployment, or lifecycle actions in the same turn. Regenerate the affected comparison when a requirement or constraining ADR changes rather than patching the selected option in isolation.

## Input contract

Accept one or more of:

- clarified requirements or a PRD
- a scoped boundary
- an impact summary
- active Accepted ADRs or existing compatibility contracts
- explicit constraints and acceptance expectations

If the only input is a path, read it before designing. Stop when source conflicts cannot be resolved without an owner decision.

## Output contract

Return:

- `requirements`: functional, confirmed/non-confirmed NFRs, edge cases
- `alternatives`: 2–4 options and trade-offs
- `chosen_design`: approach, rationale, sacrifices, deferred choices
- `interface_contracts`: inputs, outputs, errors, compatibility, ownership
- `acceptance_criteria`: must-have, nice-to-have, validation boundary
- `architectural_constraints`
- `data_migration`: when applicable
- `linked_adrs`: active Accepted decisions that constrained the result
- `adr_candidates`: qualifying Proposed portable ADRs, otherwise none

## Contract

### Preconditions

- Scope is known and at least two plausible designs or one unresolved contract/acceptance choice exists.
- Requirements are mature enough to compare approaches without inventing product behavior.

### Postconditions

- `status: completed` includes `requirements`, `alternatives`, `chosen_design`, and `acceptance_criteria`.
- Public/shared work includes interface and compatibility contracts.
- `linked_adrs` and `adr_candidates` remain lifecycle-distinct.
- The brief is ready for `implementation-planning` without reopening the chosen direction.

### Invariants

- The skill remains read-only and compares alternatives before selection.
- Acceptance is requirement-driven; assumptions never authorize behavior.
- ADR output remains portable and persistence-neutral.

### Downstream Signals

- `chosen_design` fixes the planning direction.
- `interface_contracts` and `acceptance_criteria` define implementation and validation boundaries.
- Open/assumed candidates remain explicit pre-coding gates.

## Failure Handling

### Common Failure Causes

- Requirements conflict, blast radius is unknown, or every option depends on an unresolved external/product choice.

### Retry Policy

- Run at most one focused clarification pass. If key ambiguity remains after the next response, stop and request the owner decision.

### Fallback

- Use `impact-analysis` for speculative caller/module impact, `scoped-tasking` for unstable boundaries, and `requirement-interview` for immature business scope.

### Low Confidence Handling

- Mark the design provisional, keep behavioral gaps blocking, and require `artifact-review-loop` with `artifact_type: design` before planning.

## Output Example

```text
[output: design-before-plan | completed medium | requirements:"confirmed retry budget and error semantics" alternatives:"inline retry; shared wrapper" chosen_design:"inline retry" acceptance_criteria:"budget and idempotency preserved" linked_adrs:"none" adr_candidates:"none" | next:implementation-planning]
```

## Deactivation Trigger

- The design brief is handed to `implementation-planning`.
- An upstream requirement/scope decision blocks design.
- The task is reframed as architecture work or a simple direct implementation with no remaining design choice.
