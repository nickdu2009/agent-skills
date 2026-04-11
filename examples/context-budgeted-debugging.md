# Context-Budgeted Debugging

## Scenario

A background worker fails intermittently on retry. The investigation has already grown across logs, queue code, payload serialization, worker startup, and several dead-end hypotheses.

## Recommended Skill Composition

- `context-budget-awareness`
- `bugfix-workflow`
- `scoped-tasking`
- `targeted-validation`

Add `read-and-locate` only if the retry path is still not mapped.

## Problem Pattern

The session is no longer failing because of lack of effort. It is failing because the active context is too noisy to support crisp next steps.

## Recovery Pattern

1. Compress the current state.
2. Drop stale hypotheses.
3. Re-scope the task to the smallest still-plausible fault domain.
4. Resume bugfix work from the compressed summary.
5. Validate only the retry path that matters.

## Example Compressed State

- Symptom: worker fails only on retry enqueue.
- Confirmed scope: retry scheduler, payload serializer, retry fixture.
- Ruled out: queue connection, worker boot sequence, credential loading.
- Open question: is retry payload missing the idempotency marker?
- Next step: inspect retry serialization and compare it with initial enqueue.

## When to Start Fresh

Start a fresh focused pass when:

- the same large files are being re-read without new questions
- logs dominate the session more than code evidence
- more than one rejected hypothesis is still driving actions
- a one-paragraph summary is enough to continue productively

## Guardrails

- Do not drag full logs and every prior command into the next pass.
- Do not preserve stale theories because they were expensive to investigate.
- Do not widen validation just because the session feels uncertain; target the uncertainty directly.

## Skill Protocol v2 Trace

```
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
[triggers: context-budget-awareness:trigger bugfix-workflow:defer targeted-validation:defer]
[precheck: context-budget-awareness | result:PASS | checks:noisy_session_detected objective_restated]
[output: context-budget-awareness | status:completed | confidence:medium | objective:"find root cause of retry enqueue failure" | live_scope:"retry scheduler, payload serializer, retry fixture" | dropped_hypotheses:"queue connection failure, credential loading problem" | open_questions:"is idempotency marker missing on retry serialization?" | next:bugfix-workflow]
[validate: context-budget-awareness | result:PASS | checks:objective live_scope open_questions]
[drop: context-budget-awareness | reason:"compressed state handed to diagnosis" | active:bugfix-workflow]
```
