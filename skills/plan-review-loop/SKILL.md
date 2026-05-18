---
name: plan-review-loop
description: "WHAT: Review and revise project plan files against the actual repository code, docs, configuration, and constraints until the plan is executable and issue-free. WHEN: Use when the user asks to review, validate, harden, or finalize an implementation plan, migration plan, refactor plan, task plan, roadmap, or any plan-like document before coding."
---
# plan-review-loop

Use this skill to run a strict review-and-revision loop for plan files.

## Goal

Review the target plan against the real repository context, revise the plan to resolve every issue, and repeat the review until the result is clean.

This is not a one-pass plan review. Continue looping until there are no `blocking`, `warning`, or `low-risk` issues.

## Required loop

1. Read the target plan file completely.
2. Identify the relevant repository context:
   - source code
   - tests
   - docs
   - configuration
   - existing conventions
   - related architecture decisions
3. Review the plan for executability and correctness along these dimensions:
   - upstream alignment: consistent with approved design / requirements
   - sequencing: step dependencies correct; rollback feasible
   - scope control: no unauthorized changes smuggled in
   - file-level landing: each step names specific paths or modules
   - per-step validation: each step has a verifiable acceptance check
   - risk mitigation: critical risks have mitigation
   - repository reality: referenced files / interfaces / conventions actually exist
4. Classify every issue as `blocking`, `warning`, or `low-risk`.
5. Revise the plan to resolve all issues.
6. Re-read the revised plan.
7. Re-run the review.
8. Continue until `review_result` is `clean`.

## Issue rules

### blocking
Use for issues that would make the plan fail, misimplement the requested behavior, violate repository architecture, omit required dependencies, or create major ambiguity.

### warning
Use for issues that may cause rework, incomplete implementation, weak verification, unclear sequencing, or behavior drift.

### low-risk
Use for minor but real uncertainties, assumptions, missing edge cases, or weak validation details.

Low-risk issues must not be merely reported. Each low-risk issue must be resolved by adding one or more of the following to the plan:
- explicit implementation constraint
- validation step
- acceptance criterion
- accepted assumption with a concrete verification method documented in `Residual Assumptions`

## Scope protection

- Only edit the plan file itself.
- Do not modify code, design docs, requirements, or test files.
- Do not bundle unrelated edits into the same revision pass.

Keep revisions limited to the target plan and avoid unrelated cleanup.

## Validation

The plan is not executed, so validation is documentation-level rather than code-level:

- Cross-check the plan against actual repository structure / configuration / tests / docs
- For each step, ask "what would actually block execution here"
- Confirm every referenced file path, interface, and convention exists
- For each acceptance criterion, confirm it is observable and falsifiable

Refer to `targeted-validation` for choosing the minimum useful check.

## Clean result rule

Only return `review_result: clean` when:
- there are no `blocking` issues
- there are no `warning` issues
- there are no `low-risk` issues
- every previous issue has been addressed in the plan
- residual assumptions are explicitly documented and have validation methods

If any issue remains, revise the plan and review again.

## Output format

Use this exact Markdown structure. Keep the field names unchanged and keep each entry short enough to read without horizontal scrolling.

```markdown
## Review Result
review_result: clean | issues_found

## Issues
blocking:
- None

warning:
- None

low-risk:
- None

## Changes Made
- file: ""
  summary: ""

## Validation
- ""

## Residual Assumptions
- assumption: ""
  validation_method: ""
```

## Constraints

- Do not stop after only reporting issues.
- Do not treat low-risk issues as optional notes.
- Do not mark the result clean while any issue remains.
- Do not change unrelated files.
- Keep the plan concise but executable.
- Prefer concrete validation and acceptance criteria over vague guidance.
- Keep the artifact type narrow: this skill reviews plans, not requirements, designs, code diffs, or test cases.
