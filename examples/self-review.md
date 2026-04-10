# Self Review

## Scenario

After implementing a new caching layer for the user profile endpoint,
the agent should review its own diff before running tests. The diff
includes the intended cache logic, but also accidentally contains a
leftover console.log, a modified config file not in the plan, and
an `as any` type assertion.

## Recommended Skill Composition

- plan-before-action
- minimal-change-strategy
- self-review
- targeted-validation

## Why This Composition

- self-review catches diff quality issues before testing.
- targeted-validation verifies behavior after diff is clean.
- The two are sequential: review first, then test.

## Example Execution

1. Agent completes all edits for the caching layer.
2. self-review runs git diff and examines each changed file.
3. self-review finds 3 issues:
   - blocking: console.log in production code
   - blocking: config.ts modified but not in planned working set
   - warning: `as any` type assertion in cache adapter
4. Agent fixes blocking issues before proceeding.
5. targeted-validation runs the endpoint-specific tests.

## Guardrails

- Do not run tests before self-review is clean on blocking issues.
- Do not treat warnings as blocking.
- Do not skip self-review because "tests will catch it."
- Check the planned working set against actual changed files.

## Skill Protocol v1 Trace

```yaml
[task-input-validation]
task: "Review the caching-layer diff before running tests."
checks:
  clarity:
    status: PASS
    reason: "The review target and timing are explicit."
  scope:
    status: PASS
    reason: "The work is bounded to the current diff."
  safety:
    status: PASS
    reason: "Diff review is non-destructive."
  skill_match:
    status: PASS
    reason: "self-review is the direct fit."
result: PASS
action: proceed
[/task-input-validation]

[trigger-evaluation]
task: "Review a multi-file diff before validation."
evaluated:
  - self-review: ✓ TRIGGER
  - targeted-validation: ⏸ DEFER
activated_now: [self-review]
deferred: [targeted-validation]
[/trigger-evaluation]

[precondition-check: self-review]
checks:
  - diff_is_stable: ✓ PASS
  - working_set_available: ✓ PASS
result: PASS
[/precondition-check]

[skill-output: self-review]
status: completed
confidence: high
outputs:
  findings:
    - "blocking: console.log in profile handler"
    - "blocking: config.ts changed outside the planned working set"
  residual_risks:
    - "warning: as any remains in cache adapter"
  scope_violations:
    - "src/config.ts"
signals:
  blocking_count: 2
recommendations:
  next_step: "fix blocking issues before targeted validation"
[/skill-output]

[output-validation: self-review]
checks:
  - outputs.findings: ✓ PASS
  - outputs.scope_violations: ✓ PASS
result: PASS
[/output-validation]

[skill-deactivation: self-review]
reason: "Diff review findings have been handed back to execution."
outputs_consumed_by: [targeted-validation]
remaining_active: [targeted-validation]
[/skill-deactivation]
```
