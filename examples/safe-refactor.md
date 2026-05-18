# Safe Refactor

## Scenario

Three webhook handlers each normalize the same incoming payload shape with slightly duplicated logic. The goal is to remove duplication without changing handler signatures, response codes, or normalized output.

## Recommended Skill Composition

- `scoped-tasking`
- `safe-refactor`
- `targeted-validation`

Editing follows `AGENTS.md` Behavioral Guidelines §4 (plan + verify).

## Refactor Invariants

- Handler function signatures stay unchanged.
- The normalized payload shape stays unchanged.
- Existing error messages stay unchanged.
- No new behavior is introduced.

## Example Flow

2. Use `scoped-tasking` to keep the task limited to the three handlers and the new helper location.
3. Per AGENTS.md §4, declare before editing:
   - intended files
   - extraction target
   - invariants
   - per-step verify checks
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

## Skill Protocol v2 Trace

```text
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
[precheck: safe-refactor | result:PASS | checks:invariants_stated structural_goal_bounded]
[output: safe-refactor | status:completed | confidence:high | behavior_invariants:"handler signatures unchanged; normalized payload unchanged" | refactor_boundary:"three webhook handlers, shared normalization helper" | rollback_notes:"revert helper extraction if output shape changes" | validation_boundary:"webhook handler tests only" | next:targeted-validation]
[validate: safe-refactor | result:PASS | checks:behavior_invariants refactor_boundary]
[drop: safe-refactor | reason:"The structural extraction boundary is defined and consumed." | active:targeted-validation]
```
