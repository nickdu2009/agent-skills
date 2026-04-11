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

# Execution Pattern

1. **Requirements clarification** (if needed beyond scoped-tasking):
   - Extract functional requirements (what the system must do).
   - Extract non-functional requirements (performance, compatibility, security).
   - **Identify implicit requirements** (hidden but critical): Security (authentication, authorization, input validation, data sanitization, encryption at rest/in transit); Performance (acceptable latency p50/p95/p99, throughput limits, resource constraints memory/CPU, query optimization); Observability (structured logging, metrics/counters, distributed tracing, error tracking, alerting thresholds); Resilience (error handling strategy, retry logic with backoff, circuit breakers, timeout configuration, graceful degradation); Operability (deployment strategy blue-green/canary/rolling, configuration management, feature flags, rollback plan)
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

7. **Output the design brief** (structured contract for plan-before-action).

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

```
requirements:
  functional:
    - "Support async processing of uploads > 100MB"
  non_functional:
    - "Maintain < 500ms p95 latency for small uploads"
  implicit:
    security: ["MIME type validation", "per-user quota"]
    performance: ["stream processing (avoid OOM)", "concurrent limit (max 3/user)"]
    observability: ["log upload events (size, duration)", "metrics (bytes_total, duration_seconds)"]
    resilience: ["timeout after 5min", "retry S3 chunks (3x)"]
  edge_cases:
    - "Handle network interruption mid-upload (resume support)"

design_alternatives:
  - approach: "Streaming upload with chunking"
    pros: ["constant memory usage", "resume support"]
    cons: ["increased complexity", "S3 multipart upload required"]
    blast_radius: 3 files
  - approach: "In-memory buffering with retry"
    pros: ["simple implementation", "reuses existing code"]
    cons: ["memory pressure for large files", "no progress tracking"]
    blast_radius: 1 file

chosen_design:
  approach: "Streaming upload with chunking"
  rationale: "Requirement explicitly mentions >100MB files, in-memory buffering risks OOM"
  deferred: ["compression during upload (performance optimization for future)"]

interface_contracts:
  - module: "upload_service"
    contract: "uploadFile(stream: ReadableStream, metadata: FileMetadata): Promise<UploadResult>"
    error_handling: "throws UploadError with retryable flag"
    backward_compatibility: "existing buffer-based uploadFile() remains supported, marked deprecated"

acceptance_criteria:
  must_have:
    - "100MB file uploads complete without OOM"
    - "Upload resume works after network interruption"
  nice_to_have:
    - "Progress callback support"
  validation_boundary:
    - "Integration test with 200MB fixture"
    - "Memory profiling during upload"

architectural_constraints:
  - "S3 SDK version must be >= 3.0 for multipart upload support"
  - "Node.js streams API (no browser support in this phase)"

data_migration:
  # Only present if data model changes
  schema_changes:
    - "Add uploads.chunk_size INT DEFAULT 5242880"
    - "Add uploads.resumable_token VARCHAR(64) NULLABLE"
  forward_migration: "ALTER TABLE uploads ADD COLUMN chunk_size INT DEFAULT 5242880, ADD COLUMN resumable_token VARCHAR(64)"
  backward_migration: "ALTER TABLE uploads DROP COLUMN chunk_size, DROP COLUMN resumable_token"
  complexity:
    data_volume: "~500K rows (inline migration acceptable)"
    downtime_tolerance: "zero-downtime required (columns are nullable/have defaults)"
  validation:
    - "Check row count before/after (expect no change)"
    - "Verify new columns exist: SELECT chunk_size, resumable_token FROM uploads LIMIT 1"
  risks: "Low — additive change, no data transformation needed"
```

# Guardrails

- Do not enumerate more than 4 design alternatives — too many paralyzes decision-making.
- Do not implement or prototype during this phase — design-before-plan is read-only exploration.
- Do not skip alternative enumeration even when one approach seems obvious — document why other approaches were rejected.
- Do not derive acceptance criteria from implementation details (e.g., "code has 80% coverage" is not a requirement-based criterion).
- If requirements are so unclear that design is impossible, escalate to the user — do not guess.
- If the chosen design requires new dependencies, flag them in the design brief.

**Implicit requirements checks** (triggered by change type):
- If the change involves **user input, external API calls, or file uploads**, explicitly check security requirements: authentication, authorization, input validation, sanitization, rate limiting.
- If the change affects **request handling, data processing, or database queries**, explicitly check performance requirements: acceptable latency (p95/p99), query optimization (avoid N+1), resource limits (connection pooling, memory usage).
- If the change is **user-facing or affects critical paths**, explicitly check observability requirements: structured logging with context (user ID, request ID), error tracking with stack traces, metrics for success/failure rates.
- If the change involves **external dependencies (APIs, databases, queues)**, explicitly check resilience requirements: timeout configuration, retry with exponential backoff, circuit breaker for cascading failures, graceful degradation.

**Data migration checks** (triggered by schema changes):
- Schema/model changes → define migration strategy (forward + backward) before implementation
- Assess data volume (>1M rows = background job) and downtime tolerance (zero-downtime vs. maintenance window)
- Destructive changes (drop columns/types/indexes) → validate no active dependencies before proceeding

**Technical debt assessment** (lightweight, context-dependent):
- Obvious debt (TODOs, deprecated patterns, duplication) → note in design brief but avoid mixing cleanup with delivery unless blocking or safety-critical
- Debt cleanup that simplifies design (reduces blast radius 3+ files, eliminates complex workaround) → consider as separate increment
- Default: defer debt cleanup per minimal-change-strategy unless load-bearing for current design

# Common Anti-Patterns

- **Choosing the first approach without comparison.** The agent picks the minimal-change approach reflexively without considering whether it meets non-functional requirements like performance, maintainability, or extensibility. Design alternatives were never enumerated or compared.
- **Deriving acceptance criteria from implementation.** The agent states "tests pass" or "no linter errors" as acceptance criteria instead of deriving observable success conditions from requirements. The acceptance criteria cannot be verified without looking at the implementation.
- **Skipping interface contract definition for cross-module changes.** The agent plans to modify a shared utility function used by 5 modules without defining the new function signature first. Callers are patched reactively during implementation instead of proactively during design.
- **Ignoring implicit security/performance/observability requirements.** The agent designs a file upload endpoint without considering: input validation (allowing executable uploads), performance limits (no protection against OOM for large files), or observability (no logging/metrics for debugging failures). These omissions surface as production incidents rather than being caught during design.

See skill-anti-pattern-template.md for format guidelines.

# Composition

Entry point for `design-first` and core component of `large-task` chains (see CLAUDE.md § Skill Chain Triggers).

Role: Clarify requirements, compare design alternatives, establish interface contracts before planning. Receives boundary from scoped-tasking, produces design brief, hands to plan-before-action.

Standard forward flow:

- design-first: receives boundary → produces design brief → plan-before-action → minimal-change-strategy → self-review → targeted-validation
- large-task: receives boundary → produces design brief → impact-analysis → plan-before-action → incremental-delivery

Fallbacks:

- To `impact-analysis` when caller/module impact is speculative
- To `scoped-tasking` when task boundary itself is unstable

Drop after plan-before-action consumes the design brief.

# Example

Task: "Add retry logic for flaky payment API calls."

After scoped-tasking establishes the boundary (payment client wrapper + tests), apply design-before-plan:

**Requirements clarification:**
- Functional: retry failed payment-status calls up to 3 times with exponential backoff.
- Non-functional: total retry duration must not exceed 10 seconds.
- Edge case: idempotency — do not double-charge on retry.

**Design alternatives:**
1. Generic retry decorator (wrap any async function).
   - Pros: reusable across all API clients.
   - Cons: 3-file change (decorator, payment client, user client).
2. Inline retry in payment client only.
   - Pros: 1-file change, no abstraction overhead.
   - Cons: not reusable, duplicated if other clients need retry.

**Chosen design:** Inline retry (rationale: only payment API is flaky, generic decorator is premature abstraction).

**Interface contract:**
- Payment client: no signature change, retry is internal.
- Error handling: preserve original error after exhausting retries.

**Acceptance criteria:**
- Must-have: payment-status call retries 3 times on network error, completes within 10s.
- Validation: unit test with mocked flaky API.

**Constraints:**
- Must preserve idempotency token in retry headers.

Hand off design brief to plan-before-action. Do not start editing.

## Contract

### Preconditions

- The task has unresolved design choices, contract changes, or unclear acceptance criteria.
- The scoped boundary is already known, or the user explicitly wants requirements/design clarification first.
- The agent can compare at least two plausible approaches without implementing them.

### Postconditions

- `status: completed` includes `requirements`, `alternatives`, `chosen_design`, and `acceptance_criteria`.
- Cross-module or public-contract work also records interface expectations and compatibility constraints.
- The result is specific enough for `plan-before-action` to produce an implementation sequence without reopening design.

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

```yaml
[skill-output: design-before-plan]
status: completed
confidence: medium
outputs:
  requirements:
    - "Retry flaky payment-status calls up to 3 times."
  alternatives:
    - "Inline retry in payment client"
    - "Reusable retry wrapper"
  chosen_design:
    approach: "Inline retry in payment client"
    rationale: "Smallest viable change for a single flaky upstream path"
  acceptance_criteria:
    - "Retries complete within 10 seconds total"
    - "Idempotency headers are preserved on every retry"
signals:
  planning_ready: true
recommendations:
  downstream_skill: "plan-before-action"
[/skill-output]
```

## Deactivation Trigger

- Deactivate once `plan-before-action` has consumed the design brief.
- Deactivate when the user chooses a different design direction and the brief must be regenerated from scratch.
- Deactivate if the task is reframed into a direct implementation with no remaining design decisions.
