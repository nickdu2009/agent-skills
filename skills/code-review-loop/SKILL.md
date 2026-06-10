---
name: code-review-loop
description: "WHAT: Review a code diff, commit, PR, or specified files, classify issues, fix real defects, run the minimum necessary validation, and repeat the review/fix loop until the implementation is issue-free. WHEN: Use after code has been implemented or staged, when the user asks to review a diff, commit, pull request, or completed implementation; or to validate that finished code matches the requested scope, plan, or contract. Do NOT use to review requirements (use requirements-review-loop), design docs / RFCs / ADRs (use design-review-loop), implementation plans (use plan-review-loop), or test cases themselves (use test-review-loop)."
metadata:
  version: "0.1.0"
  tags: "review, code, validation"
---
# code-review-loop

Use this skill to run a strict review, fix, validation, and re-review loop for implementation changes (diff / commit / PR / specified files).

## Goal

Review the target diff or commit, find real implementation defects first, fix them, validate the fix, and repeat until the review is clean. This is not a style-only review. Focus on requirement alignment, correctness, regressions, security, compatibility, scope control, and test coverage.

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
4. Cover at minimum these core dimensions:
   - requirement alignment: matches the confirmed requirements, acceptance criteria, plan, or contract; no missed behavior, wrong behavior, or over-implementation. If explicit requirement evidence is incomplete, infer the narrowest likely user intent from the task wording and visible context, then ask the user to confirm before treating the inferred intent as a review basis. Until confirmed, keep `review_result` as `issues_found` and pause the review at that point.
   - correctness: behavior correctness, boundary handling, error handling, failure paths
   - regression: no unintended behavior regression; key paths and adjacent behavior remain intact
   - security: injection, authz, sensitive data, secrets
   - compatibility: data, API, serialization, migration, and upstream/downstream compatibility
   - scope control: no unrelated changes smuggled in; changes stay within the accepted task boundary
   - test: new logic has sufficient verification; existing tests are not bypassed or weakened
5. Add applicable additional dimensions based on the change type:
   - performance: hot paths, queries, caching, rendering, batch/IO-heavy changes
   - concurrency / idempotency: races, retries, duplicate execution, transaction/locking boundaries
   - operability / observability: logs, metrics, alerts, tracing, diagnosability, recovery
   - rollout / config risk: flags, dependency upgrades, config defaults, rollout/rollback, deployment ordering
   - accessibility / UX states: empty/error/loading states, keyboard access, disabled states, feedback
6. Classify every finding as `blocking`, `warning`, or `low-risk`.
7. Fix only issues related to the reviewed implementation.
8. Run the minimum necessary validation (see Validation).
9. Re-check the diff after changes.
10. Re-run the review.
11. Continue until `review_result` is `clean`.

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

Refer to AGENTS.md Behavioral Guidelines §3 (Surgical Changes) for keeping the edit minimal.

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
- requirement alignment does not depend on unconfirmed inferred user intent

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

Then finish with the compact protocol line:

`[output: code-review-loop | completed <confidence> | review_result:"clean|issues_found" issues:"<count by severity>" fixes:"..." validation:"..." | next:<action>]`

## Constraints

- Do not stop after only reporting findings, except when `requirement alignment` depends on unconfirmed inferred user intent and user confirmation is required before continuing.
- Do not mark the result clean while any issue remains.
- Do not fix unrelated code.
- Do not mix user-existing changes into the task result.
- Do not perform broad refactors unless required to fix a finding.
- Prefer minimal, targeted validation.
- Do not use to review requirements; use `requirements-review-loop` instead.
- Do not use to review design docs / RFCs / ADRs; use `design-review-loop` instead.
- Do not use to review implementation plans; use `plan-review-loop` instead.
- Do not use to review test cases themselves; use `test-review-loop` instead.
