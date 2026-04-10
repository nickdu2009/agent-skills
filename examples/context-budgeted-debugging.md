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

## Skill Protocol v1 Trace

```yaml
[task-input-validation]
task: "Compress a noisy retry-debugging session and resume from the smallest live fault domain."
checks:
  clarity:
    status: PASS
    reason: "The objective is to compress and refocus, not keep exploring."
  scope:
    status: PASS
    reason: "The current live scope can be reduced."
  safety:
    status: PASS
    reason: "State compression is non-destructive."
  skill_match:
    status: PASS
    reason: "context-budget-awareness is the right first move."
result: PASS
action: proceed
[/task-input-validation]

[trigger-evaluation]
task: "Refocus a stalled retry investigation."
evaluated:
  - context-budget-awareness: ✓ TRIGGER
  - bugfix-workflow: ⏸ DEFER
  - targeted-validation: ⏸ DEFER
activated_now: [context-budget-awareness]
deferred: [bugfix-workflow, targeted-validation]
[/trigger-evaluation]

[precondition-check: context-budget-awareness]
checks:
  - noisy_session_detected: ✓ PASS
  - objective_restated: ✓ PASS
result: PASS
[/precondition-check]

[skill-output: context-budget-awareness]
status: completed
confidence: medium
outputs:
  current_state:
    objective: "find root cause of retry enqueue failure"
    live: ["retry scheduler", "payload serializer", "retry fixture"]
  dropped_hypotheses:
    - "queue connection failure"
    - "credential loading problem"
  open_questions:
    - "is the idempotency marker missing on retry serialization?"
signals:
  action: "compress"
recommendations:
  downstream_skill: "bugfix-workflow"
[/skill-output]

[output-validation: context-budget-awareness]
checks:
  - outputs.current_state: ✓ PASS
  - outputs.open_questions: ✓ PASS
result: PASS
[/output-validation]

[skill-deactivation: context-budget-awareness]
reason: "Compressed state has been handed off to the next diagnosis step."
outputs_consumed_by: [bugfix-workflow]
remaining_active: [bugfix-workflow]
[/skill-deactivation]
```
