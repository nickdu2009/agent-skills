---
name: architecture-design
description: "Guide architecture design for a system, subsystem, or module by producing a structured design document covering component decomposition, data architecture, interface contracts, non-functional design, deployment topology, and ADRs. Includes approach comparison when design direction is not yet settled. WHEN: Use when the user asks for architecture design / system design / technical proposal / 架构设计 / 系统设计 / 出个架构 / 写个技术方案, when a task involves 3+ components or a new subsystem, when technology selection decisions are needed, or when non-functional requirements (scalability, availability, security) require architectural treatment. Do NOT use for single-module internal design choices where design-before-plan suffices, for requirements clarification (use requirement-interview), or for reviewing an existing design doc (use design-review-loop)."
metadata:
  version: "0.1.0"
  tags: "coding, agents, architecture, design, system-design"
---

# architecture-design

Produce a structured architecture design for a system, subsystem, or module. The skill outputs a reviewable architecture design document — not code — covering component decomposition, data architecture, interface contracts, non-functional design, and key architecture decisions with rationale.

# Purpose

Turn a clear requirement or design direction into a concrete, reviewable architecture. Core goals:

- Decompose the system into components with clear responsibilities and dependency directions.
- Design data architecture: models, flow, storage, consistency.
- Define cross-component interface contracts.
- Address non-functional requirements at the architecture level (not as afterthoughts).
- Record architecture decisions with rationale (ADRs) so they are traceable.
- Produce a document that `design-review-loop` can review and `implementation-planning` can consume.

Success criterion: on exit, the architecture document is specific enough for implementation planning without reopening component boundaries, technology choices, or interface contracts.

# When to Use

- The user asks for architecture design / system design / technical proposal / 架构设计 / 系统设计 / 技术方案.
- A task involves building a new system, subsystem, or significant new module.
- The change requires decomposing responsibilities across 3+ components.
- Technology selection decisions are needed (database, messaging, caching, framework, etc.).
- Non-functional requirements (scalability, availability, security, observability) need architectural solutions.
- `design-before-plan` produced a design brief whose `blast_radius` is large and component decomposition is needed.
- Major architecture evolution or migration of an existing system.

# When Not to Use

- Single-module internal design choice with limited blast radius → `design-before-plan`.
- The requirement is still vague → `requirement-interview`.
- An existing architecture document needs review → `design-review-loop`.
- Simple bug fix or small refactor → `bugfix-workflow` / `safe-refactor`.
- The user explicitly says "不用出架构，直接做" → respect the user, give a one-line risk note.

# Scale Judgment

Before starting, judge the task scale to calibrate output depth:

| Scale | Signal | Output depth |
|---|---|---|
| **System-level** | New system / major evolution / 5+ components / cross-service / deployment topology matters | Full architecture document with all sections |
| **Subsystem-level** | New subsystem / 3-4 components / technology selection needed / clear non-functional requirements | Full document, deployment section optional |
| **Module-level** | Single module internal architecture / 2-3 internal layers / no cross-service impact | Lighter document: component decomposition + data architecture + key ADRs; skip deployment and some non-functional sections |

When in doubt, start with the lighter version and expand if the design reveals more complexity.

# Core Rules

- Do not write production code; output is an architecture design document only.
- Decompose before detailing: establish component boundaries first, then dive into each component.
- Every technology choice must have a rationale; do not list names without justification.
- Architecture principles are a validation tool, not a design driver. Design from requirements, then validate against principles. See [reference.md](reference.md) for the principle checklist.
- When principles conflict, record the trade-off explicitly (which principle was prioritized, which was relaxed, and why).
- Do not over-architect: component count and layer depth must match the problem scale.
- Use Mermaid diagrams for architecture visualization when helpful.
- Always run at least one architecture clarification round before starting the design.

# Architecture Information Dimensions

Use the readiness checklist in [architecture-template.md](architecture-template.md). At minimum, assess component boundaries, technology constraints, non-functional priorities, and data characteristics. If all four are unknown, ask before designing. Mark every reasonable assumption explicitly. "Reasonably assumed" covers mechanical architecture context only — not behavioral strategies such as retry counts, fallbacks, degradation paths, matching rules, or failure semantics.

# Execution Pattern

0. **Check inputs and judge scale**:
   - Collect available requirement doc, design brief, scoped boundary, impact summary.
   - Judge scale (system / subsystem / module) per the Scale Judgment table.
   - If the requirement is unclear, hand off to `requirement-interview`.

1. **Architecture clarification round** (mandatory, at least one round):
   - Scan architecture information dimensions; mark each as known / unknown / assumed.
   - Generate 3-5 questions for the most important unknown dimensions, ordered by impact on architecture decisions.
   - Do not ask requirement-level questions (that belongs to `requirement-interview`).
   - After receiving answers, update dimension status. If key dimensions remain unknown and cannot be reasonably assumed, run another round.
   - No hard cap on rounds; stop when enough dimensions are known or reasonably assumed to support architecture decisions. In practice, 1-2 rounds usually suffice.
   - Tag assumptions explicitly with their basis; assumptions enter the final document's "待确认假设" section, not treated as confirmed facts.
   - Behavioral assumptions (timeouts, retries, circuit breakers, fallbacks, graceful degradation, matching thresholds) stay in "待确认假设" with `blocking: true` until confirmed; they must not become executable planning inputs.

2. **Approach comparison** (if design direction is not settled):
   - List 2-4 candidate architecture approaches.
   - For each: pros, cons, complexity, blast radius, principle alignment.
   - Choose one with explicit rationale; record rejected alternatives in ADR.
   - If direction was already settled upstream, skip this step and note the source.

3. **Component decomposition**:
   - Identify core components and their responsibilities.
   - Define dependency directions (which component depends on which).
   - Validate against structural principles: cohesion, coupling, separation of concerns, single responsibility.
   - Produce a Mermaid component diagram.

4. **Data architecture**:
   - Design core data models and their ownership (which component owns which data).
   - Define data flow between components.
   - Choose storage technology with rationale.
   - Address data consistency strategy (transactions, eventual consistency, saga, etc.).

5. **Interface contract definition**:
   - Define cross-component interfaces: input/output types, error handling, versioning.
   - Validate against interface principles: interface segregation, dependency inversion, encapsulation.

6. **Non-functional architecture** (depth per scale judgment):
   - Scalability: horizontal/vertical scaling strategy, bottleneck analysis.
   - Availability & resilience: enumerate failure modes and required evaluation of timeout/retry/circuit-breaker/degradation options; adopt specific strategies only from confirmed requirements, architecture baseline, or an active Accepted ADR.
   - Security: authentication, authorization, data protection, defense in depth.
   - Observability: logging, metrics, tracing injection points.
   - Validate against runtime quality principles.

7. **Deployment architecture** (system-level only):
   - Deployment topology, environment requirements, infrastructure dependencies.

8. **Record ADRs**:
   - Produce a separate, portable ADR artifact for each key long-lived or costly-to-reverse decision.
   - Use [adr-format.md](adr-format.md); creating an ADR artifact does not imply writing a file.
   - Keep the architecture document's ADR table as an index only: `id`, title, document status, and artifact/path reference.
   - Preserve the compact protocol field name `adrs`; its value is `id + artifact/path + status`.

9. **Write or output the architecture design document** (see Output Format).

10. **Recommend next step**:
    - `design-review-loop` when the architecture should be reviewed before planning.
    - `implementation-planning` when the architecture is accepted.

# Input Contract

Provide one or more of:

- a requirement document or requirement-clarification result
- a design brief from `design-before-plan`
- a scoped boundary from `scoped-tasking`
- user's direct architecture task description

Optional but helpful:

- existing system architecture or context
- technology constraints or preferences
- team structure (for Conway's Law alignment)
- non-functional priority ranking

# Output Format

Return a reviewable architecture document with:

- background, goals, constraints, and scale
- approach comparison when direction was open
- component decomposition and dependency direction
- data architecture and ownership
- interface contracts
- relevant non-functional and deployment design
- ADR index (`id`, title, status, artifact/path)
- risks, assumptions, and architecture-level acceptance criteria

Use [architecture-template.md](architecture-template.md) for the full document shape. For module-level work, omit deployment and irrelevant non-functional sections. ADR artifacts follow [adr-format.md](adr-format.md).

# Guardrails

- Do not skip the architecture clarification round. Always scan the information dimensions and ask at least one round before designing.
- Do not code while designing; this skill is read-only exploration and document production.
- Do not over-decompose: if the problem needs 3 components, do not create 8 for "future flexibility".
- Do not pick technologies without rationale ("用 Redis" is not architecture; "用 Redis 因为读多写少、需要亚毫秒延迟且数据可丢失" is).
- Do not skip approach comparison when direction is genuinely open, even if one approach seems obvious.
- Do not mechanically apply every architecture principle. Use principles as validation checks, not design drivers. See [reference.md](reference.md).
- If requirement gaps block architecture decisions, stop and hand off to `requirement-interview` rather than guessing.
- Ask at most 5 questions per clarification round; do not dump all architecture concerns at once.
- Do not treat an assumption as a confirmed fact — tag it and record it in the "待确认假设" section.
- Do not invent behavioral failure strategies under Design for Failure; evaluate failure modes, then require authorization before specifying retries, fallbacks, or degradation.
- Do not write ADR files unless the user explicitly requests document persistence and the target repository's existing convention is known.

# Composition

Enter directly for explicit architecture work or after `design-before-plan` reveals system-level complexity. Upstream options are `requirement-interview`, `scoped-tasking`, `design-before-plan`, and `impact-analysis`. Hand off to `design-review-loop` when review is needed or to `implementation-planning` when accepted, then deactivate.

# Example

See [examples.md](examples.md) for a subsystem example with separate ADR artifacts and an ADR index.

## Contract

### Preconditions

- The requirement is clear enough to make architecture decisions (business goal, main flow, scope boundary are known).
- The task genuinely needs architecture work (not a simple single-file edit).
- The agent can identify 2+ components or layers that need explicit boundary definition.

### Postconditions

- `status: completed` includes `components`, `data_architecture`, `interface_contracts`, `adrs`, and `acceptance_criteria`.
- The document is specific enough for `implementation-planning` to produce an execution plan without reopening component boundaries or technology choices.
- Key architecture decisions are recorded with alternatives and rationale.
- `adrs` keeps its existing field name and points to independent ADR artifacts using `id + artifact/path + status`.

### Invariants

- This skill stays read-only; no production code is written.
- Technology choices always have rationale.
- Architecture complexity matches the problem scale.
- Principles are used as validation, not as design drivers.

### Downstream Signals

- `components` defines the decomposition for implementation to follow.
- `data_architecture` grounds data modeling and storage decisions.
- `interface_contracts` gives implementation precise API boundaries.
- `adrs` prevent later phases from unknowingly revisiting settled decisions.

## Failure Handling

### Common Failure Causes

- The requirement is too incomplete to make architecture decisions.
- The technology landscape is unfamiliar and the agent cannot make informed choices.
- Architecture scale is misjudged (treating a module-level task as system-level, or vice versa).

### Retry Policy

- No hard cap on clarification rounds; stop when enough architecture dimensions are known or reasonably assumed.
- If two consecutive rounds produce no new confirmed information (user cannot or will not answer), stop and escalate to the user with the specific blocking dimensions listed.

### Fallback

- Hand off to `requirement-interview` if the requirement is not mature.
- Hand off to `design-before-plan` if only approach selection (not full architecture) is needed.
- Hand off to `impact-analysis` if blast radius is speculative.
- If the user insists on implementing directly, give a risk note and deactivate.

### Low Confidence Handling

- Mark uncertain architecture decisions as provisional in the ADR table.
- Recommend `design-review-loop` before proceeding when confidence is medium or low.

## Output Example

```
[output: architecture-design | completed medium | scale:"subsystem" components:"notification-service, channel-adapters(3), preference-store" tech_choices:"RabbitMQ(async decoupling), PostgreSQL(preference storage)" adrs:"ADR-0001:inline-artifact:Proposed, ADR-0002:inline-artifact:Proposed" | next:design-review-loop]
```

## Deactivation Trigger

- The architecture document is produced and handed off to `design-review-loop` or `implementation-planning`.
- The task is downscaled to a simple design choice that `design-before-plan` can handle.
- The user explicitly asks to skip architecture and implement directly.
