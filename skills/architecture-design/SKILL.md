---
name: architecture-design
description: "Design a system, subsystem, or significant module by defining components, data ownership and flow, interface contracts, non-functional architecture, deployment topology, and ADR candidates. Use for new subsystems, 3+ interacting components, technology selection, major evolution, or architecture-level scalability, availability, security, and operability concerns. Do not use for vague requirements or a small internal design choice."
metadata:
  version: "0.2.0"
  tags: "architecture, system-design, adr"
---

# architecture-design

Produce a concrete, reviewable architecture document, not production code. The result must let planning proceed without reopening component boundaries, technology choices, or public interfaces.

## Activation and scale boundary

Activate for a new system/subsystem, significant module, 3+ interacting components, cross-service evolution, technology selection, deployment topology, or architecture-level NFR work. Use `design-before-plan` for a smaller approach/contract choice and `requirement-interview` when goal, actors, main flow, or scope is unclear.

| Scale | Typical signal | Required depth |
|---|---|---|
| System | New/major system, 5+ components, cross-service topology | Full document including deployment |
| Subsystem | 3–4 components, technology/NFR decisions | Full document; deployment when relevant |
| Module | 2–3 internal layers, no cross-service topology | Components, data, interfaces, key decisions |

Choose the lightest scale supported by evidence and expand only when the design requires it.

## Hard constraint

**Run at least one architecture clarification round before drafting, and keep every unconfirmed behavioral strategy blocking instead of embedding it in components, interfaces, NFRs, or ADRs.**

Behavioral strategies include timeouts, retry counts, fallbacks, degradation, matching thresholds, permission outcomes, and failure semantics. They require confirmed requirements, an active Accepted ADR/baseline, preserved compatibility, or an explicit owner decision.

## Core workflow

1. **Validate readiness and scale.** Collect requirements, design brief, scoped boundary, impact summary, existing architecture, and ADRs. Classify component boundaries, technology constraints, deployment, NFR priorities, data characteristics, integrations, ownership, scale, security/compliance, and migration as `known|unknown|assumed`.
2. **Clarify architecture.** Ask 3–5 highest-impact architecture questions. Do not repeat requirement-level interviewing. Run another round only when a key dimension remains unsupported; expose assumption basis and `blocking` status.
3. **Compare approaches when unsettled.** Evaluate 2–4 options by complexity, blast radius, reversibility, ownership, and requirement fit. Principles validate a requirement-led design; they do not select one. Use [principles.md](references/principles.md) only for a relevant decision or final calibration.
4. **Decompose components.** Define responsibility, owner, public interface, dependencies, dependency direction, and technology rationale. Prefer cohesive boundaries, explicit contracts, least necessary complexity, and visible trade-offs.
5. **Design data.** Define business source of truth, models, ownership, flows, storage rationale, consistency, lifecycle, and migration/coexistence. UI state, caches, logs, generated artifacts, and mocks are not truth without an authorized architecture decision.
6. **Define interfaces.** Record caller/provider, inputs, outputs, errors, versioning, compatibility, and ownership. Keep unresolved observable behavior out of executable contracts.
7. **Address NFRs and deployment.** Evaluate failure modes, scale, security, observability, operability, topology, and environment constraints. State authorized mechanisms and keep unsupported strategies as blocking assumptions.
8. **Record decisions.** For each long-lived, cross-component, or costly-to-reverse choice, read [adr-format.md](references/adr-format.md) and create a separate vendor-neutral Proposed ADR artifact. The architecture document holds only `id`, `title`, `status`, and `artifact/path`.
9. **Draft and verify.** Always read [architecture-template.md](references/architecture-template.md). Check component/data/interface consistency, technology rationale, assumption gates, risks, and architecture-level acceptance. Read [examples.md](references/examples.md) only for calibration.

## Clarification and decision rules

The mandatory first round must cover the dimensions most likely to change boundaries or technology. Ask about ownership and constraints before naming products. Do not ask all ten dimensions mechanically: select 3–5 unknowns with the highest decision impact. A dimension may be `assumed` only when the assumption is mechanical, its basis is visible, and a validation method exists.

Approach comparison is optional only when direction is already fixed by confirmed inputs or an active Accepted ADR. Otherwise compare credible architectures on the same requirements. Never add a queue, service, cache, database, layer, or abstraction only to appear scalable. When a technology is selected, state the required capability, why the option fits it, what alternatives were rejected, operational/ownership cost, and revisit condition.

New ADRs are Proposed artifacts even when the architecture document recommends them. An existing Accepted ADR may constrain the design only while active and not superseded. Do not let a Proposed ADR silently authorize a behavioral strategy or implementation plan.

## Architecture consistency gate

Before completion, verify:

- Each component has one coherent responsibility, an owner, and a bounded public contract; dependencies do not bypass the contract through shared internals.
- Every data object has one named business truth owner. Copies, projections, caches, indexes, and generated views state synchronization and failure implications without becoming competing truth.
- Each data flow connects declared components and interfaces; consistency claims match storage and communication choices.
- Interfaces align on semantic input/output, error ownership, versioning, and compatibility. Callers do not depend on provider implementation order or private schema.
- Failure modes are evaluated at every external boundary. Concrete timeout/retry/fallback/degradation choices appear only when authorized; otherwise they remain blocking assumptions.
- Security identifies trust boundaries, identity/authorization ownership, sensitive-data handling, and audit needs appropriate to scale.
- Observability names where correlation, logs, metrics, and traces must be possible, without inventing alert thresholds.
- Deployment topology matches component ownership, state, availability, and environment constraints; omit it only for a truly module-level design.
- Architecture acceptance checks validate boundaries, data ownership/flow, interfaces, and key NFR outcomes rather than private code structure.

When two components each claim the same truth, an interface has no error owner, or a key behavioral assumption remains open, the document is not ready for planning. Return the exact conflict to its owner or require design review.

Diagrams and prose must describe the same components, direction, and ownership. Every edge in a component/data/deployment diagram needs a corresponding interface or flow description; every declared public interface must have identifiable endpoints in the architecture. Treat a diagram mismatch as a design defect, not presentation cleanup. Architecture acceptance must also state how later validation can observe the claimed boundary or quality without requiring a specific private implementation.

Name excluded architecture work explicitly so deferred topology, migration, or quality concerns do not enter planning as implied scope.

## Output contract

Return:

- `scale`: system, subsystem, or module
- `components`: responsibilities, owners, interfaces, dependencies, technology rationale
- `data_architecture`: truth owner, models, flow, storage, consistency, lifecycle
- `interface_contracts`: inputs, outputs, errors, versioning, compatibility, ownership
- `non_functional_architecture`: authorized scale, resilience, security, observability, operability choices
- `deployment_topology`: when applicable
- `adrs`: `{id, title, status, artifact/path}`; new candidates remain Proposed
- `risks_and_constraints`
- `assumptions`: basis, impact, blocking, validation/owner decision
- `acceptance_criteria`: architecture-level observable conditions

Use Mermaid only when it materially clarifies components, data flow, or deployment.

## Contract

### Preconditions

- Goal, main flow, and scope are clear enough for architecture decisions.
- The task genuinely needs at least two explicit component/layer boundaries.

### Postconditions

- `status: completed` includes `components`, `data_architecture`, `interface_contracts`, `adrs`, and `acceptance_criteria`.
- Technology and boundary choices have rationale and alternatives where material.
- The document is ready for `implementation-planning` without reopening core architecture.

### Invariants

- The skill remains read-only and right-sizes complexity.
- Technology choices have rationale; principles validate rather than drive.
- Unconfirmed behavioral assumptions remain blocking and cannot feed planning.

### Downstream Signals

- Components and interfaces define implementation ownership and landing boundaries.
- Data architecture fixes source-of-truth and consistency expectations.
- ADR references preserve decision lifecycle and traceability.

## Failure Handling

### Common Failure Causes

- Requirements are immature, scale is misjudged, ownership is unknown, or technology evidence is insufficient.

### Retry Policy

- Clarify while each round can add evidence. After two consecutive rounds add none, stop with the blocking dimensions.

### Fallback

- Use `requirement-interview` for immature requirements, `design-before-plan` for a smaller choice, or `impact-analysis` for speculative blast radius.

### Low Confidence Handling

- Mark uncertain decisions Proposed/provisional and require `artifact-review-loop` with `artifact_type: design` before planning.

## Output Example

```text
[output: architecture-design | completed medium | scale:"subsystem" components:"dispatcher, channel adapters, preference store" data_architecture:"preferences owned by service database" interface_contracts:"dispatch and preference APIs" adrs:"ADR-0001:inline:Proposed" | next:artifact-review-loop(type=design)]
```

## Deactivation Trigger

- The architecture is handed to design review or `implementation-planning`.
- The task downscales to a local design choice or returns to upstream clarification.
- The user explicitly skips architecture after receiving a bounded risk note.
