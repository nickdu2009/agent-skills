# Safe Refactor

## Scenario

Three webhook handlers each normalize the same incoming payload shape with slightly duplicated logic. The goal is to remove duplication without changing handler signatures, response codes, or normalized output.

## Recommended Skill Composition

- `scoped-tasking`
- `read-and-locate`
- `plan-before-action`
- `safe-refactor`
- `targeted-validation`

## Refactor Invariants

- Handler function signatures stay unchanged.
- The normalized payload shape stays unchanged.
- Existing error messages stay unchanged.
- No new behavior is introduced.

## Example Flow

1. Use `read-and-locate` to confirm all normalization entry points and the shared boundary.
2. Use `scoped-tasking` to keep the task limited to the three handlers and the new helper location.
3. Use `plan-before-action` to declare:
   - intended files
   - extraction target
   - invariants
4. Use `safe-refactor` to perform small steps:
   - extract the shared normalization helper
   - switch one handler to the helper
   - validate
   - switch the remaining handlers
5. Use `targeted-validation` to run only the handler and normalization tests.

## Suggested Plan

- Goal: extract duplicate normalization logic into one shared helper.
- Scope: the three handlers plus one helper module.
- Assumptions: duplication is structural only; behavior should not change.
- Intended files: handler files, shared helper, related tests.

## Guardrails

- Do not mix the refactor with webhook retry or error-handling changes.
- Do not reorganize the entire webhook package.
- If extraction reveals behavior differences between handlers, split that into a follow-up behavior task instead of silently standardizing them.
- Validate the affected handlers after each meaningful structural step.

## Skill Protocol v1 Trace

```yaml
[task-input-validation]
task: "Extract duplicated webhook payload normalization without changing behavior."
checks:
  clarity:
    status: PASS
    reason: "Refactor goal and invariants are explicit."
  scope:
    status: PASS
    reason: "The task is limited to three handlers and one helper."
  safety:
    status: PASS
    reason: "Behavior-preserving structural cleanup is bounded."
  skill_match:
    status: PASS
    reason: "safe-refactor and targeted-validation apply directly."
result: PASS
action: proceed
[/task-input-validation]

[trigger-evaluation]
task: "Perform a behavior-preserving webhook refactor."
evaluated:
  - read-and-locate: ✓ TRIGGER
  - safe-refactor: ✓ TRIGGER
  - targeted-validation: ⏸ DEFER
activated_now: [read-and-locate, safe-refactor]
deferred: [targeted-validation]
[/trigger-evaluation]

[precondition-check: safe-refactor]
checks:
  - invariants_stated: ✓ PASS
  - structural_goal_bounded: ✓ PASS
result: PASS
[/precondition-check]

[skill-output: safe-refactor]
status: completed
confidence: high
outputs:
  behavior_invariants:
    - "handler signatures unchanged"
    - "normalized payload unchanged"
  refactor_boundary: ["three webhook handlers", "shared normalization helper"]
  rollback_notes: ["revert helper extraction if output shape changes"]
signals:
  next_skill: "targeted-validation"
recommendations:
  validation_boundary: "webhook handler tests only"
[/skill-output]

[output-validation: safe-refactor]
checks:
  - outputs.behavior_invariants: ✓ PASS
  - outputs.refactor_boundary: ✓ PASS
result: PASS
[/output-validation]

[skill-deactivation: safe-refactor]
reason: "The structural extraction boundary is defined and consumed."
outputs_consumed_by: [targeted-validation]
remaining_active: [targeted-validation]
[/skill-deactivation]
```
