---
name: design-before-plan
description: Clarify requirements, compare design alternatives, define interface contracts, and establish acceptance criteria before planning implementation. Use when (1) task involves choosing between multiple approaches, (2) mentions "changes the public interface" or "touches contract", (3) cross-module contracts need coordination, or (4) acceptance criteria are unclear.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, design, requirements"
---

# Purpose

Force the agent to complete requirements clarification and design decision-making before creating an implementation plan. The goal is to prevent premature planning when key design questions remain open, ensure alternatives are considered, and establish clear contracts and acceptance criteria that guide implementation.

# When to Use

- When the task involves choosing between multiple architectural or design approaches.
- When the change introduces or modifies a public API, shared interface, or cross-module contract.
- When acceptance criteria are missing or ambiguous.
- When the implementation approach is unclear and design constraints need identification.
- When scoped-tasking identified the boundary but design decisions remain open.
- When impact-analysis revealed 3+ affected modules requiring contract coordination.

# When Not to Use

- When the design is already documented and implementation-ready.
- For simple bug fixes where the design is obvious (wrong constant, typo, etc.).
- For single-file internal changes with no interface impact.
- When the user explicitly requests exploratory implementation ("try X and see").

# Core Rules

- Do not start planning implementation until design decisions are documented.
- Enumerate alternatives before choosing an approach.
- Define interface contracts before planning cross-module changes.
- Derive acceptance criteria from requirements, not from implementation details.
- Identify architectural constraints that limit design choices.
- Make design trade-offs explicit: what is gained and what is sacrificed.
- Produce an ADR candidate when multiple reasonable approaches exist and the chosen decision crosses modules or PRs, is long-lived, or is costly to reverse.
- Keep ADR artifacts vendor-neutral; this skill never depends on a persistence tool or repository-specific knowledge path.

# Execution Pattern

1. **Requirements clarification** (if needed beyond scoped-tasking):
   - Extract functional requirements (what the system must do).
   - Extract non-functional requirements (performance, compatibility, security).
   - **Identify implicit NFR candidates** (must check, must not auto-adopt): Security (authentication, authorization, input validation, data sanitization, encryption at rest/in transit); Performance (acceptable latency p50/p95/p99, throughput limits, resource constraints memory/CPU, query optimization); Observability (structured logging, metrics/counters, distributed tracing, error tracking, alerting thresholds); Resilience (error handling strategy, retry logic with backoff, circuit breakers, timeout configuration, graceful degradation); Operability (deployment strategy blue-green/canary/rolling, configuration management, feature flags, rollback plan). Record each candidate with `source` / `status` (`confirmed` | `open` | `assumed`) / `blocking`. Unconfirmed candidates must not enter `chosen_design` or acceptance criteria.
   - Identify stakeholder concerns (user experience, maintainability, extensibility).
   - Confirm edge cases and error scenarios.

2. **Design alternatives enumeration**:
   - List 2-4 candidate approaches (do not implement yet).
   - For each approach, note: pros, cons, complexity, blast radius.
   - Consider: minimal-change approach, clean-slate approach, incremental migration.
   - When applicable, consider standard design patterns (Strategy, Adapter, Factory, Observer, etc.) but let patterns emerge naturally from requirements — do not impose patterns top-down for the sake of "using a pattern".

3. **Design decision**:
   - Choose an approach based on: task constraints, blast radius, reversibility, alignment with codebase patterns.
   - Document the decision rationale.
   - Flag deferred alternatives for future consideration.

4. **Interface contract definition** (if cross-module or public API):
   - Define input/output contracts (types, schemas, protocols).
   - Specify error handling contracts (exception types, error codes, retry semantics).
   - Identify backward compatibility constraints.
   - Note contract migration strategy if breaking changes are needed.

4.5. **Data migration strategy** (if data model or schema changes):
   - Identify schema changes: new fields, type changes, renames, deletions, index modifications.
   - Design migration path: Forward migration (old to new schema via migration script, data transformation logic); Backward migration (new to old schema for rollback support, restore capability)
   - Assess migration complexity and risks: Data volume (< 1M rows = inline migration during deployment, > 1M rows = background job with progress tracking); Downtime tolerance (zero-downtime = dual-write period + shadow reads, maintenance window = stop-the-world migration); Data loss risk (destructive changes = dropping columns/narrowing types, additive changes = new nullable fields)
   - Define migration validation: Row count verification (before vs. after); checksum or hash comparison for critical data; sample verification (spot-check transformed records)
   - Note performance impact: lock contention, replication lag, storage growth.

5. **Acceptance criteria derivation**:
   - Translate requirements into verifiable conditions.
   - Define observable success indicators (test outcomes, metrics, behaviors).
   - Establish completion gates (when is this task done?).
   - Distinguish must-have from nice-to-have validation.

6. **Architectural constraints capture**:
   - Identify system invariants that must be preserved.
   - Note framework limitations or platform constraints.
   - Document compatibility requirements (API versions, dependency constraints).

7. **Output the design brief** (structured contract for the subsequent `implementation-planning` step).
   - Include `linked_adrs` for existing decisions that constrained the design.
   - Include `adr_candidates` only for decisions that meet the ADR threshold above.
   - Each ADR candidate follows [adr-format.md](adr-format.md) and remains a portable artifact unless the user explicitly asks to write it using the target repository's conventions.

# Input Contract

Provide:

- the task objective (from scoped-tasking)
- the scoped boundary (files, modules, validation surface)
- impact-analysis results if available (affected modules, blast radius)
- known constraints (performance, compatibility, security)

Optional but helpful:

- existing design documentation or ADRs (Architecture Decision Records)
- stakeholder priorities
- preferred validation approach

# Output Contract

Return a **design brief** containing:

- `requirements`
- `design_alternatives`
- `chosen_design`
- `interface_contracts`
- `acceptance_criteria`
- `architectural_constraints`
- optional `data_migration`
- optional `linked_adrs`: existing ADR IDs/artifacts that constrain this design
- optional `adr_candidates`: portable ADR artifacts for newly settled high-impact decisions

Use [design-brief-format.md](design-brief-format.md) for the complete design brief shape and [examples.md](examples.md) for a short worked example.

# Guardrails

- Do not enumerate more than 4 design alternatives — too many paralyzes decision-making.
- Do not implement or prototype during this phase — design-before-plan is read-only exploration; do not edit production files.
- Confirmed behavior values authorize those product semantics in the design brief; they do not authorize coding in the same turn. After the brief, hand off to `implementation-planning` or stop — do not chain into production edits unless the user explicitly asked to implement.
- Do not invent unconfirmed behavioral details (for example retry-count semantics such as "3 retries = 4 total attempts", idempotency-key formats, backoff curves, or fallback shapes). Leave them `open` / ask, or put them outside `chosen_design`.
- Do not skip alternative enumeration even when one approach seems obvious — document why other approaches were rejected.
- Do not derive acceptance criteria from implementation details (e.g., "code has 80% coverage" is not a requirement-based criterion).
- If requirements are so unclear that design is impossible, escalate to the user — do not guess.
- If the chosen design requires new dependencies, flag them in the design brief.
- Unconfirmed behavioral NFR candidates (timeouts, retries, circuit breakers, fallbacks, graceful degradation) stay out of `chosen_design` and acceptance criteria.

**Implicit NFR candidate checks** (triggered by change type; check ≠ adopt):
- If the change involves **user input, external API calls, or file uploads**, explicitly check security candidates: authentication, authorization, input validation, sanitization, rate limiting. Adopt only what is confirmed or already required by an accepted contract.
- If the change affects **request handling, data processing, or database queries**, explicitly check performance candidates: acceptable latency (p95/p99), query optimization (avoid N+1), resource limits (connection pooling, memory usage).
- If the change is **user-facing or affects critical paths**, explicitly check observability candidates: structured logging with context (user ID, request ID), error tracking with stack traces, metrics for success/failure rates.
- If the change involves **external dependencies (APIs, databases, queues)**, explicitly check resilience candidates: timeout configuration, retry with exponential backoff, circuit breaker for cascading failures, graceful degradation. Ask or leave open unless the user/design already authorized specific values and failure semantics.
- Do not treat "good engineering practice" as authorization for timeouts, retries, fallbacks, or degradation paths.

**Data migration checks** (triggered by schema changes):
- Schema/model changes → define migration strategy (forward + backward) before implementation
- Assess data volume (>1M rows = background job) and downtime tolerance (zero-downtime vs. maintenance window)
- Destructive changes (drop columns/types/indexes) → validate no active dependencies before proceeding

**Technical debt assessment** (lightweight, context-dependent):
- Obvious debt (TODOs, deprecated patterns, duplication) → note in design brief but avoid mixing cleanup with delivery unless blocking or safety-critical
- Debt cleanup that simplifies design (reduces blast radius 3+ files, eliminates complex workaround) → consider as separate increment

# Common Anti-Patterns

- **Choosing the first approach without comparison.** The agent picks the minimal-change approach reflexively without considering whether it meets non-functional requirements like performance, maintainability, or extensibility. Design alternatives were never enumerated or compared.
- **Deriving acceptance criteria from implementation.** The agent states "tests pass" or "no linter errors" as acceptance criteria instead of deriving observable success conditions from requirements. The acceptance criteria cannot be verified without looking at the implementation.
- **Skipping interface contract definition for cross-module changes.** The agent plans to modify a shared utility function used by 5 modules without defining the new function signature first. Callers are patched reactively during implementation instead of proactively during design.
- **Ignoring implicit security/performance/observability requirements.** The agent designs a file upload endpoint without considering: input validation (allowing executable uploads), performance limits (no protection against OOM for large files), or observability (no logging/metrics for debugging failures). These omissions surface as production incidents rather than being caught during design.
- **Authorized-then-code.** The user confirmed retry/fallback values or asked to form a design/plan "before coding", and the agent still writes production files in the same turn. Authorization settles semantics; design-before-plan stays read-only until an explicit implement request.

Keep anti-pattern guidance self-contained; installed skills must not depend on maintainer-only documents.

# Composition

Entry point for `design-first` and core component of `large-task` chains (see the project governance file § Skill Chain Triggers).

Role: Clarify requirements, compare design alternatives, establish interface contracts before planning. Receives boundary from scoped-tasking, produces design brief, hands to `implementation-planning`.

Standard forward flow:

Fallbacks:

- To `impact-analysis` when caller/module impact is speculative
- To `scoped-tasking` when task boundary itself is unstable

Drop after `implementation-planning` consumes the design brief.

# Example

See [examples.md](examples.md) for a compact design brief and ADR-threshold example.

## Contract

### Preconditions

- The task has unresolved design choices, contract changes, or unclear acceptance criteria.
- The scoped boundary is already known, or the user explicitly wants requirements/design clarification first.
- The agent can compare at least two plausible approaches without implementing them.

### Postconditions

- `status: completed` includes `requirements`, `alternatives`, `chosen_design`, and `acceptance_criteria`.
- Cross-module or public-contract work also records interface expectations and compatibility constraints.
- Qualifying architecture decisions are returned as vendor-neutral `adr_candidates`; existing constraints are listed in `linked_adrs`.
- The result is specific enough for `implementation-planning` to produce an implementation sequence without reopening design.

### Invariants

- This skill stays read-only and does not prototype implementation.
- Alternatives are compared before one is selected.
- Acceptance criteria are requirement-driven, not implementation-driven.

### Downstream Signals

- `requirements` feeds planning and validation boundaries.
- `alternatives` records rejected options so later phases do not revisit them blindly.
- `chosen_design` gives the authoritative design direction for planning.
- `acceptance_criteria` defines the completion gates for implementation and validation.

## Failure Handling

### Common Failure Causes

- Requirements are too incomplete or contradictory to support a design choice.
- The real blast radius is unknown because impact information is missing.
- Every viable design depends on an unresolved external constraint.

### Retry Policy

- Allow one clarification pass to resolve missing requirements or decision criteria.
- If the second pass still cannot eliminate key ambiguity, stop and escalate to the user.

### Fallback

- Run `impact-analysis` first when caller/module impact is still speculative.
- Return to `scoped-tasking` when the task boundary itself is still unstable.
- Escalate to the user when the design choice is business- or product-driven.

### Low Confidence Handling

- Keep the chosen design marked provisional and require plan consumers to restate the open risk.
- Do not convert a low-confidence design brief into an implementation plan without explicit acknowledgment of the uncertainty.

## Output Example

```
[output: design-before-plan | completed medium | requirements:"Retry flaky payment-status calls up to 3 times." alternatives:"Inline retry in payment client, Reusable retry wrapper" chosen_design:"Inline retry in payment client" acceptance_criteria:"Retries complete within 10 seconds total, Idempotency headers are preserved on every retry" linked_adrs:"none" adr_candidates:"none; local reversible choice" | next:implementation-planning]
```

## Deactivation Trigger

- Deactivate once `implementation-planning` has consumed the design brief.
- Deactivate when the user chooses a different design direction and the brief must be regenerated from scratch.
- Deactivate if the task is reframed into a direct implementation with no remaining design decisions.
