# Incremental Delivery

## Scenario

Add webhook support to the notification system. The task requires:
a new webhook model, a delivery service, an API endpoint for
webhook registration, and integration tests. Estimated: 3 PRs.

## Recommended Skill Composition

- scoped-tasking
- plan-before-action
- incremental-delivery
- minimal-change-strategy
- targeted-validation

## Why This Composition

- plan-before-action produces the overall plan.
- incremental-delivery splits it into 3 mergeable increments.
- Each increment must keep the system runnable.

## Example Execution

1. plan-before-action produces the plan (4 logical steps).
2. incremental-delivery splits into 3 increments:
   - Increment 1: webhook data model + migration (depends_on: [])
   - Increment 2: delivery service + unit tests (depends_on: [1])
   - Increment 3: API endpoint + integration tests (depends_on: [2])
3. Each increment has explicit acceptance criteria.
4. Agent executes incrementally, validating each before proceeding.

## Upgrade Check

- If the task also requires aligning webhook payloads with an
  external OpenAPI spec, upgrade to phase-plan.
- If the task grows to 5+ PRs, upgrade to phase-plan.
- If the task can be done in 1 PR, downgrade to plan-before-action.

## Guardrails

- Do not merge increments that break the system.
- Do not skip dependency declarations between increments.
- Do not force 3 PRs if 1 PR suffices (check downgrade condition).
- If upgrade threshold is hit, stop and escalate.

## Skill Protocol v1 Trace

```yaml
[task-input-validation]
task: "Split webhook support into mergeable increments."
checks:
  clarity:
    status: PASS
    reason: "The deliverable is a 3-PR split."
  scope:
    status: PASS
    reason: "The work is bounded to delivery planning, not execution."
  safety:
    status: PASS
    reason: "Increment planning is non-destructive."
  skill_match:
    status: PASS
    reason: "incremental-delivery fits the requested 3-PR split."
result: PASS
action: proceed
[/task-input-validation]

[trigger-evaluation]
task: "Split a webhook feature into 3 increments."
evaluated:
  - plan-before-action: ✓ TRIGGER
  - incremental-delivery: ✓ TRIGGER
  - phase-plan: ⏸ DEFER
activated_now: [plan-before-action, incremental-delivery]
deferred: [phase-plan]
[/trigger-evaluation]

[precondition-check: incremental-delivery]
checks:
  - plan_exists: ✓ PASS
  - pr_count_between_2_and_4: ✓ PASS
result: PASS
[/precondition-check]

[skill-output: incremental-delivery]
status: completed
confidence: high
outputs:
  increments:
    - "Webhook model and migration"
    - "Delivery service and unit tests"
    - "Registration endpoint and integration tests"
  merge_order:
    - 1
    - 2
    - 3
  gates:
    - "increment 1 validated before increment 2"
    - "increment 2 validated before increment 3"
signals:
  escalation: "none"
recommendations:
  next_step: "start increment 1"
[/skill-output]

[output-validation: incremental-delivery]
checks:
  - outputs.increments: ✓ PASS
  - outputs.merge_order: ✓ PASS
result: PASS
[/output-validation]

[skill-deactivation: incremental-delivery]
reason: "The mergeable increment list has been accepted."
outputs_consumed_by: [minimal-change-strategy, targeted-validation]
remaining_active: [minimal-change-strategy]
[/skill-deactivation]
```
