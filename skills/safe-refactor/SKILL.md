---
name: safe-refactor
description: Guide small, controlled refactors that improve code structure while keeping behavior and interfaces stable. Use when the task is structural cleanup, extraction, or simplification — not a behavior change.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Make structural improvements with bounded risk. The skill is for small refactors that reduce duplication or improve local clarity without quietly changing behavior or widening the task.

# When to Use

- When the task is structural cleanup with stable behavior.
- When a small local refactor is needed to support a separate change safely.
- When duplicated or tangled logic can be simplified without interface changes.

# When Not to Use

- When the user asked for a bugfix only and no refactor is needed.
- When the refactor would likely change public behavior or external contracts.
- When the required change is large enough to need a dedicated redesign.

# Core Rules

- Keep interface and behavior stable unless change is explicitly requested.
- Refactor in small reversible steps.
- Separate structural cleanup from behavior changes.
- Define invariants before editing.
- Validate only the affected area unless wider validation is justified.
- Prefer extraction, isolation, and simplification over sweeping reorganization.

# Execution Pattern

1. Define the refactor goal.
2. List invariants that must remain true.
3. Choose the smallest structural step.
4. Edit one structural operation at a time: one extraction, one inline, one rename, or one move. Do not combine multiple structural operations in a single step.
5. Run narrow validation after each meaningful step.
6. Stop once the structural goal is met; do not convert the task into a redesign.

# Input Contract

Provide:

- the refactor goal
- stable interfaces or behaviors that must not change
- the affected files or modules
- allowed scope for structural movement

Optional but helpful:

- duplicated code locations
- available local tests

# Output Contract

Return:

- stated invariants
- the chosen small-step sequence
- touched interfaces and why they remain stable
- the validation boundary
- residual risk or deferred cleanup

# Guardrails

- Do not bundle behavior changes into a structural cleanup.
- Do not rename externally meaningful symbols unless requested.
- Do not reorganize files just because a smaller extraction would work.
- If a refactor step exposes hidden behavior changes, stop and split the work.
- Keep each step easy to review and easy to revert.

# Common Anti-Patterns

- **Combining behavior change with structural cleanup.** The agent extracts a helper function and simultaneously changes its error handling semantics, introducing a behavior change hidden inside what was supposed to be a pure structural refactor.
- **Doing everything in one step.** The agent renames a function, moves it to a new file, and changes its signature in a single commit instead of performing one structural operation at a time with validation between steps.

# Composition

Combine with:

- `minimal-change-strategy` to keep the structural patch bounded
- `plan-before-action` to declare invariants and steps before editing
- `targeted-validation` to validate each step cheaply
- `read-and-locate` when the structural boundaries are not obvious yet

# Example

Task: "Extract duplicate request-normalization logic used by three handlers."

Possible invariants:

- handler signatures stay unchanged
- normalized output shape stays unchanged
- error messages stay unchanged

Apply the refactor by extracting one shared helper, switching one handler at a time if needed, and validating the affected handlers rather than running every API test in the repository.

## Contract

### Preconditions

- The requested work is structural rather than behavioral.
- Stable interfaces or invariants can be named before editing.
- The refactor can be decomposed into small reversible steps.

### Postconditions

- `status: completed` includes `behavior_invariants`, `refactor_boundary`, and `rollback_notes`.
- The structural steps preserve signatures, outputs, and externally visible behavior unless the user requested otherwise.
- Residual risk or deferred cleanup is stated explicitly.

### Invariants

- Behavior and interface contracts stay stable throughout the refactor.
- Structural steps remain reviewable and reversible.
- Validation stays aligned with the touched structural seam.

### Downstream Signals

- `behavior_invariants` define what later validation must preserve.
- `refactor_boundary` limits the structural change surface.
- `rollback_notes` document how to revert if an invariant breaks.

## Failure Handling

### Common Failure Causes

- The proposed extraction or move changes behavior in hidden ways.
- The true refactor scope is larger than the local boundary suggests.
- Stable invariants cannot be stated with confidence.

### Retry Policy

- Allow one smaller-step revision when a planned refactor step proves too large.
- If invariants still cannot be preserved locally, stop and escalate to redesign or bugfix handling.

### Fallback

- Return to `minimal-change-strategy` when only a local cleanup is justified.
- Escalate to `design-before-plan` if the structural change also implies interface redesign.
- Use `read-and-locate` if ownership seams are still unclear.

### Low Confidence Handling

- Treat unstated invariants as blockers, not assumptions.
- Require targeted validation after each meaningful structural step.

## Output Example

```yaml
[skill-output: safe-refactor]
status: completed
confidence: high
outputs:
  behavior_invariants:
    - "handler signatures stay unchanged"
    - "normalized output shape stays unchanged"
  refactor_boundary:
    - "request normalization helper extraction"
  rollback_notes:
    - "revert the helper extraction commit if output shape changes"
signals:
  validation_boundary:
    - "affected handler tests only"
recommendations:
  next_step: "extract one shared helper without changing handler call sites"
[/skill-output]
```

## Deactivation Trigger

- Deactivate when the structural goal is met and invariants remain intact.
- Deactivate when hidden behavior changes force the task into bugfix or redesign territory.
- Deactivate after downstream validation has consumed the invariant list.
