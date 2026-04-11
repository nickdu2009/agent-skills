---
name: incremental-delivery
description: Split a plan into 2-4 independently mergeable PRs when the task is medium-sized. ONLY use when (1) explicitly mentions "3 PRs" or "4 PRs", OR (2) spans exactly 1-2 modules without parallel work or external specs. If 5+ PRs, 3+ modules, or needs parallel lanes use phase-plan instead.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Bridge the gap between single-PR plans (plan-before-action) and multi-wave phase execution (phase-plan). The skill splits a plan into 2-4 independently mergeable increments, each keeping the system in a runnable state.

# When to Use

- When plan-before-action produces a plan that spans 2-4 PRs.
- When the task crosses 1-2 module boundaries but does not need parallel lanes.
- When each increment can be merged and validated independently.
- When the delivery order matters and dependencies between increments must be explicit.

# When Not to Use

- When the plan fits in a single PR — stay with plan-before-action.
- When the task spans 5+ PRs, 3+ modules, or needs parallel lanes — escalate to phase-plan.
- When external contract alignment (OpenAPI spec, webhook contract) is required — escalate to phase-plan.
- When the user explicitly asks for a single combined delivery.

# Core Rules

- Each increment must keep the system in a runnable state after merge.
- Each increment must have explicit acceptance criteria.
- Dependencies between increments must be declared (not implicit).
- Increment count must be 2-4. If analysis shows 1 PR suffices, downgrade to plan-before-action. If 5+, escalate to phase-plan.
- Merge order must be explicit.
- Do not force splits that add overhead without value.

# Execution Pattern

1. Receive the plan from plan-before-action.
2. Identify natural split points: data model boundaries, service layer boundaries, API surface boundaries, test boundaries.
3. Draft 2-4 increments with scope, dependencies, and acceptance criteria.
4. Verify each increment keeps the system runnable (no broken imports, no missing types, no dangling references).
5. Output the increment list. If the task can be done in 1 PR, output a downgrade recommendation. If it exceeds 4 increments, output an escalation recommendation.

Upgrade/downgrade thresholds:

| Condition | Stay at incremental-delivery | Escalate to phase-plan |
|-----------|------------------------------|------------------------|
| PR count | 2-4 | 5+ |
| Module span | 1-2 modules | 3+ modules |
| Parallelism | Can deliver serially | Needs parallel lanes |
| Handoff complexity | Merge order only | Formal handoff checklists |
| External contract | None or repo-internal only | External spec alignment needed |

# Input Contract

Provide:

- the plan from plan-before-action
- the estimated PR count
- module boundaries involved

Optional:

- external contract requirements
- team coordination needs

# Output Contract

Return:

```
increments:
  - id: 1
    scope: "Add webhook data model and migration"
    depends_on: []
    acceptance: "Migration runs, model passes unit tests"
    merge_order: 1
  - id: 2
    scope: "Implement delivery service with retry logic"
    depends_on: [1]
    acceptance: "Service passes unit tests, handles retry scenarios"
    merge_order: 2
  - id: 3
    scope: "Add registration API endpoint and integration tests"
    depends_on: [2]
    acceptance: "Endpoint returns correct responses, integration tests pass"
    merge_order: 3
escalation: none
```

If downgrading: `recommendation: "downgrade to plan-before-action — task fits in 1 PR"`

If escalating: `recommendation: "escalate to phase-plan — 6 PRs across 3 modules with external webhook spec"`

# Guardrails

- Do not create increments that leave the system in a broken state.
- Do not skip dependency declarations between increments — implicit dependencies cause merge failures.
- Do not force 3 PRs when 1 PR suffices (check downgrade condition).
- Do not stay at incremental-delivery when the upgrade threshold is clearly exceeded — escalate promptly.
- Do not let increment acceptance criteria be vague ("it works") — each must be testable.
- Keep increment scope descriptions concrete enough that a reviewer can verify the boundary.

# Common Anti-Patterns

- **Splitting for the sake of splitting.** The agent creates 3 increments for a task that cleanly fits in one PR, adding merge overhead and dependency tracking for no benefit.
- **Implicit dependencies.** The agent declares increments as independent when increment 2 actually imports a type defined in increment 1. The second PR will fail CI if merged out of order.

# Composition

Exit point for `large-task` chain (see CLAUDE.md § Skill Chain Triggers).

Role: Split multi-step plan into 2-4 independently mergeable increments. Receives plan from plan-before-action, produces increment list with merge order and dependencies.

Standard forward flow:

- large-task: ... → plan-before-action → incremental-delivery (produces increment list, then exits)

Per-increment validation uses `targeted-validation` to verify each increment independently.

Escalation/downgrade:

- Downgrade to `plan-before-action` when task fits in 1 PR
- Escalate to `phase-plan` when task exceeds 4 increments, 2 modules, or needs parallel lanes

Drop after increment list is finalized.

# Example

Task: "Add webhook support to the notification system."

Plan from plan-before-action identifies: model, service, endpoint, tests.

incremental-delivery splits into 3 increments:

- Increment 1: Webhook model + migration (no dependencies, validates with migration test)
- Increment 2: Delivery service + unit tests (depends on increment 1 for model)
- Increment 3: API endpoint + integration tests (depends on increment 2 for service)

Each increment keeps the system runnable. If the task also requires aligning payloads with an external OpenAPI spec, escalate to phase-plan instead.

## Contract

### Preconditions

- A concrete plan already exists and appears to span 2-4 mergeable units.
- The task can be delivered serially without wave-level parallel coordination.
- Each proposed increment can keep the system runnable after merge.

### Postconditions

- `status: completed` includes `increments`, `merge_order`, and `gates`.
- Dependencies between increments are explicit rather than implied.
- The output recommends downgrade or escalation when the task falls outside the 2-4 increment envelope.

### Invariants

- Increment count stays between 2 and 4 unless the output is an explicit downgrade or escalation.
- Every increment remains independently mergeable and testable.
- Delivery ordering is concrete enough to avoid broken intermediate states.

### Downstream Signals

- `increments` defines the mergeable delivery slices.
- `merge_order` states the required sequence.
- `gates` records what must be true before each increment is considered complete.

## Failure Handling

### Common Failure Causes

- The task actually fits in one PR, so splitting adds overhead without value.
- The task spans too many modules, PRs, or external contracts for increment-only handling.
- Hidden dependencies mean an increment would leave the system broken after merge.

### Retry Policy

- Allow one re-split when a proposed increment is not independently runnable.
- If no valid 2-4 increment split exists after that pass, downgrade or escalate explicitly rather than forcing the split.

### Fallback

- Downgrade to `plan-before-action` when one PR suffices.
- Escalate to `phase-plan` when the task exceeds 4 increments, 2 modules, or needs parallel lanes.
- Use `targeted-validation` to define validation gates per increment once the split is accepted.

### Low Confidence Handling

- Mark uncertain dependencies as gates that must be checked before the next increment starts.
- Prefer a smaller number of defensible increments over a more granular but fragile split.

## Output Example

```yaml
[skill-output: incremental-delivery]
status: completed
confidence: high
outputs:
  increments:
    - "Webhook model and migration"
    - "Delivery service and unit tests"
    - "API endpoint and integration tests"
  merge_order:
    - 1
    - 2
    - 3
  gates:
    - "migration passes before service work starts"
    - "service tests pass before endpoint integration"
signals:
  escalation: "none"
recommendations:
  next_step: "implement increment 1 first"
[/skill-output]
```

## Deactivation Trigger

- Deactivate once the increment list and merge order are accepted.
- Deactivate when the task is downgraded back to a single-PR plan.
- Deactivate when the work escalates into `phase-plan` for larger coordination.
