---
name: design-before-plan
description: Clarify requirements, compare design alternatives, define interface contracts, and establish acceptance criteria before planning implementation. Use when the task involves design choices, cross-module contracts, or unclear acceptance criteria.
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
   - Extract functional requirements (what the system must do)
   - Extract non-functional requirements (performance, compatibility, security)
   - Identify implicit requirements (see Guardrails section for security, performance, observability, resilience checks)
   - Identify stakeholder concerns (user experience, maintainability, extensibility)
   - Confirm edge cases and error scenarios

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
   - Identify schema changes: new fields, type changes, renames, deletions, index modifications
   - Design forward migration (old → new schema) and backward migration (rollback support)
   - Assess complexity: data volume (< 1M rows inline, > 1M background job), downtime tolerance, data loss risk
   - Define validation: row count, checksums for critical data, sample verification
   - Note performance impact: lock contention, replication lag, storage growth

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
    security:
      - "Validate file MIME type against whitelist (prevent executable upload)"
      - "Enforce per-user upload quota to prevent abuse"
    performance:
      - "Stream processing to avoid OOM for large files"
      - "Limit concurrent uploads per user (max 3)"
    observability:
      - "Log upload start/complete with file size and duration"
      - "Emit metrics: upload_bytes_total, upload_duration_seconds"
    resilience:
      - "Timeout upload after 5 minutes of inactivity"
      - "Retry S3 upload chunks up to 3 times on transient errors"
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
- User input / external APIs / file uploads → check security (auth, validation, sanitization, rate limiting)
- Request handling / data processing / DB queries → check performance (latency p95/p99, query optimization, resource limits)
- User-facing / critical paths → check observability (structured logging, error tracking, metrics)
- External dependencies (APIs, DBs, queues) → check resilience (timeouts, retry with backoff, circuit breaker, graceful degradation)

**Data migration checks** (triggered by schema changes):
- DB schema or data model changes → define migration strategy (forward + backward) before planning
- Assess data volume (> 1M rows requires background job) and downtime tolerance
- Destructive changes (drop columns, narrow types, delete indexes) → validate no active dependencies first

**Technical debt assessment** (lightweight, context-dependent):
- Note obvious debt (TODOs, deprecated patterns) but do not mix cleanup with feature delivery
- If debt cleanup significantly simplifies design (reduces blast radius 3+ files), consider as separate increment
- When in doubt, defer cleanup — follow `minimal-change-strategy` unless load-bearing

# Common Anti-Patterns

- **Choosing the first approach without comparison.** The agent picks the minimal-change approach reflexively without considering whether it meets non-functional requirements (performance, maintainability, extensibility). Design alternatives were never enumerated.
- **Deriving acceptance criteria from implementation.** The agent states "tests pass" or "no linter errors" as acceptance criteria instead of deriving observable success conditions from requirements. The acceptance criteria cannot be verified without looking at the implementation.
- **Skipping interface contract definition for cross-module changes.** The agent plans to modify a shared utility function used by 5 modules without defining the new function signature first. Callers are patched reactively during implementation instead of proactively during design.
- **Ignoring implicit security/performance/observability requirements.** The agent designs a file upload endpoint without considering: input validation (allowing executable uploads), performance limits (no protection against OOM for large files), or observability (no logging/metrics for debugging failures). These omissions surface as production incidents rather than being caught during design.

# Composition

Part of design-first chain. See CLAUDE.md Skill Chain Triggers section.

Additional composition:
- Depends on `scoped-tasking` (task boundary is input)
- Depends on `impact-analysis` when blast radius is unclear
- Outputs to `plan-before-action` (design brief becomes planning input)
- Combine with `incremental-delivery` when design spans multiple PRs
- Drop after `plan-before-action` produces the implementation plan

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
