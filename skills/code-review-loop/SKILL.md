---
name: code-review-loop
description: "WHAT: Review a code diff, commit, PR, or specified files, classify issues, fix real defects, run the minimum necessary validation, and repeat the review/fix loop until the implementation is issue-free. WHEN: Use after code has been implemented or staged, when the user asks to review a diff, commit, pull request, or completed implementation; or to validate that finished code matches the requested scope, plan, or contract. Do NOT use to review requirements (use requirements-review-loop), design docs / RFCs / ADRs (use design-review-loop), implementation plans (use plan-review-loop), or test cases themselves (use test-review-loop)."
---
# code-review-loop

Use this skill to run a strict review, fix, validation, and re-review loop for implementation changes (diff / commit / PR / specified files).

## Goal

Review the target diff or commit, find real implementation defects first, fix them, validate the fix, and repeat until the review is clean. This is not a style-only review. Focus on correctness, regressions, safety, scope control, data compatibility, and test coverage.

## Required loop

1. Identify the target under review:
   - current working tree diff
   - staged diff
   - specific commit
   - commit range
   - user-specified files
   - pull request diff
2. Inspect repository status before making any changes; distinguish user-existing changes from current task changes.
3. Review the target using findings-first code review. Each finding must include: severity (`blocking` / `warning` / `low-risk`), affected file or area, problem, impact, required fix.
4. Cover at minimum these dimensions:
   - correctness: behavior correctness, boundary handling, error handling
   - regression: no behavior regression; tests cover key paths
   - security: injection, authz, sensitive data, secrets
   - data compatibility: schema, serialization, migration compatibility
   - scope control: no unrelated changes smuggled in
   - test: new logic has tests; existing tests not bypassed
5. Classify every finding as `blocking`, `warning`, or `low-risk`.
6. Fix only issues related to the reviewed implementation.
7. Run the minimum necessary validation (see Validation).
8. Re-check the diff after changes.
9. Re-run the review.
10. Continue until `review_result` is `clean`.

## Optional checks

PR-level checks, when the target is a pull request:

- PR description is clear; links to the related issue or design doc
- Commit messages follow project conventions
- CI checks have passed (or known failures explained)
- Branch is ready to merge (rebased / no conflicts / required reviewers approved)

Skip this section when the target is a local diff or commit only.

## Issue rules

### blocking
Use for correctness bugs, broken builds, failed tests, behavior regressions, security issues, data loss risks, or scope violations that must be fixed before completion.

### warning
Use for incomplete behavior, weak error handling, insufficient tests, ambiguous edge cases, or likely maintainability problems that may cause rework.

### low-risk
Use for minor but real risks, weak validation coverage, unclear assumptions, or small edge cases.

Low-risk issues must still be resolved before the loop can finish. Resolve each by one or more of:
- code fix
- test or validation addition
- explicit accepted assumption with verification method documented in `Residual Assumptions`

## Scope protection

Before modifying files:
- inspect repository status
- distinguish user-existing changes from current task changes
- do not overwrite unrelated user changes
- do not repair unrelated files
- do not reformat unrelated files
- do not include unrelated changes in the final diff

When fixing findings:
- make the smallest safe change
- keep changes tied to review findings
- preserve existing architecture and conventions
- avoid opportunistic refactors

Refer to `minimal-change-strategy` for keeping the edit minimal.

## Validation

Run the smallest validation that gives confidence in the fix, such as: targeted unit tests, targeted integration tests, typecheck, lint for touched files, build step only when necessary.

If validation cannot be run, explain why and provide the closest available alternative.

Refer to `targeted-validation` for choosing the minimum useful check.

Record the command(s) actually run and their results in the `Validation` field of the output.

## Clean result rule

Only return `review_result: clean` when:
- there are no `blocking` issues
- there are no `warning` issues
- there are no `low-risk` issues
- fixes have been applied for all findings
- minimum necessary validation has been run or explicitly justified
- no unrelated files were changed

If any issue remains, fix it and review again.

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

- Do not stop after only reporting findings.
- Do not mark the result clean while any issue remains.
- Do not fix unrelated code.
- Do not mix user-existing changes into the task result.
- Do not perform broad refactors unless required to fix a finding.
- Prefer minimal, targeted validation.
- Do not use to review requirements; use `requirements-review-loop` instead.
- Do not use to review design docs / RFCs / ADRs; use `design-review-loop` instead.
- Do not use to review implementation plans; use `plan-review-loop` instead.
- Do not use to review test cases themselves; use `test-review-loop` instead.
