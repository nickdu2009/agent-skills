# Self-Delivery Review

## Scenario

After implementing a new caching layer for the user profile endpoint,
the agent should review its own diff before running tests. The diff
includes the intended cache logic, but also accidentally contains a
leftover console.log, a modified config file not in the plan, and
an `as any` type assertion.

## Recommended Skill Composition

- artifact-review-loop (`artifact_type=code`, `review_context=self-delivery`)
- targeted-validation

Implementation precedes review through a lightweight inline plan with explicit verification.

## Why This Composition

- artifact-review-loop catches diff quality issues before testing without expanding the current task's write scope.
- targeted-validation verifies behavior after diff is clean.
- The two are sequential: review first, then test.

## Example Execution

1. Agent completes all edits for the caching layer.
2. artifact-review-loop verifies current-task provenance, then examines the authorized diff.
3. artifact-review-loop finds 3 issues:
   - blocking: console.log in production code
   - blocking: config.ts modified but not in planned working set
   - warning: `as any` type assertion in cache adapter
4. Agent fixes blocking issues before proceeding.
5. targeted-validation runs the endpoint-specific tests.

## Guardrails

- Do not run tests before the self-delivery review is clean on blocking issues.
- Do not treat warnings as blocking.
- Do not skip review because "tests will catch it."
- Check the planned working set against actual changed files.

## Skill Protocol v2 Trace

```
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
[triggers: artifact-review-loop:trigger targeted-validation:defer]
[precheck: artifact-review-loop | result:PASS | checks:current_agent_origin write_authorized current_task_diff]
[output: artifact-review-loop | completed high | artifact_type:"code" artifact_subtype:"working-tree-diff" secondary_types:"none" review_context:"self-delivery" mode:"review-and-revise" authorization_source:"inherited-current-task" write_scope:"current-task-diff" review_result:"issues_found" issues:"2 blocking, 1 warning, 0 low-risk" changes:"none" validation:"inspected current-task diff" | next:fix-and-re-review]
[validate: artifact-review-loop | PASS | checks:contract]
```

The full Markdown result contains the three severity buckets and all five
required fields for every finding. Keep the review loop active while blocking
issues remain; trigger `targeted-validation` only after revision and re-review
reach `clean` or an explicitly accepted non-blocking result.
