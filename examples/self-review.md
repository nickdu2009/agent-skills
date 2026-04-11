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

## Skill Protocol v2 Trace

```
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
[triggers: self-review:trigger targeted-validation:defer]
[precheck: self-review | result:PASS | checks:diff_is_stable working_set_available]
[output: self-review | status:completed | confidence:high | findings:"blocking: console.log in profile handler; blocking: config.ts changed outside planned working set" | residual_risks:"warning: as any remains in cache adapter" | scope_violations:"src/config.ts" | blocking_count:2 | next:targeted-validation]
[validate: self-review | result:PASS | checks:findings scope_violations]
[drop: self-review | reason:"diff review complete, blocking issues identified" | active:targeted-validation]
```
