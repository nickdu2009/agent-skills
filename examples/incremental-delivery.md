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
