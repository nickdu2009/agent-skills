---
name: plan-review-loop
description: "WHAT: Review and revise project plan files against the actual repository code, docs, configuration, and constraints until the plan is executable and issue-free. WHEN: Use when the user asks to review, validate, harden, or finalize an implementation plan, migration plan, refactor plan, task plan, roadmap, or any plan-like document before coding."
metadata:
  version: "0.1.0"
  tags: "review, planning, documentation"
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

Then finish with the compact protocol line:

`[output: plan-review-loop | completed <confidence> | review_result:"clean|issues_found" issues:"<count by severity>" changes:"..." validation:"..." | next:<action>]`

## Contract

### Preconditions

- A plan artifact exists to review.
- The repository provides enough context to validate landing surfaces, sequencing, and verification.
- The artifact is an implementation/refactor/migration/task plan, not requirements, design, code, or tests.

### Postconditions

- `status: completed` includes `review_result`, `issues`, `changes`, and `validation`.
- The plan is either clean or blocked by explicit planning defects.
- Revisions stay inside the target plan artifact.

### Invariants

- The review stays plan-focused, not code-focused.
- Every issue is resolved before `review_result: clean`.
- File-level landing, validation, and risk coverage remain explicit.

### Downstream Signals

- `review_result` tells implementation whether the plan is ready to execute.
- `issues` records any remaining planning defects or confirms none remain.
- `changes` summarizes how the plan was revised.
- `validation` records the repository checks used to support the review.

## Failure Handling

### Common Failure Causes

- The artifact is not actually a plan.
- The plan references files, modules, or contracts that do not exist.
- Sequencing, rollback, or validation remains too vague to execute safely.

### Retry Policy

- Re-review after each plan revision until no issues remain.
- If the same planning gap recurs twice, stop and escalate upstream rather than looping blindly.

### Fallback

- Hand off to `design-review-loop` if the artifact is actually a design doc.
- Hand off to `code-review-loop` if the artifact is already implemented and the user really wants code review.

### Low Confidence Handling

- Preserve residual assumptions with explicit validation methods.
- Do not mark the plan clean while execution still depends on guessed sequencing or landing.

## Output Example

```
[output: plan-review-loop | completed high | review_result:"clean" issues:"0 blocking, 0 warning, 0 low-risk" changes:"added missing rollback note and tied AC3 to step 4" validation:"confirmed referenced files and checks exist in repo" | next:implementation]
```

## Deactivation Trigger

- The plan artifact is clean and handed to implementation.
- The plan is reframed into a different artifact type and needs a different review loop.

## Constraints

- Do not stop after only reporting issues.
- Do not treat low-risk issues as optional notes.
- Do not mark the result clean while any issue remains.
- Do not change unrelated files.
- Keep the plan concise but executable.
- Prefer concrete validation and acceptance criteria over vague guidance.
- Keep the artifact type narrow: this skill reviews plans, not requirements, designs, code diffs, or test cases.
