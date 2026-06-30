---
name: code-review-loop
description: "WHAT: Review (and optionally revise) a code diff, commit, PR, or specified files. Classify findings with a structured schema, distinguish objective defects from clarification blockers, run the minimum necessary validation, and either report findings (review-only) or loop review/fix until the implementation is clean, clean_with_assumptions, or blocked by needs_clarification. WHEN: Use after code has been implemented or staged, when the user asks to review a diff, commit, pull request, or completed implementation; or to validate that finished code matches the requested scope, plan, or contract. Do NOT use to review requirements (use requirements-review-loop), design docs / RFCs / ADRs (use design-review-loop), implementation plans (use plan-review-loop), or test cases themselves (use test-review-loop)."
metadata:
  version: "0.2.0"
  tags: "review, code, validation"
---

# code-review-loop

Use this skill to run a strict review, fix, validation, and re-review loop for implementation changes (diff / commit / PR / specified files).

## Goal

Review the target diff or commit, find real implementation defects first, fix them, validate the fix, and repeat until the review is clean. This is not a style-only review. Focus on requirement alignment, correctness, regressions, security, compatibility, scope control, and test coverage.

This is not a one-pass review when running in `review-and-revise` mode. Continue looping until there are no unresolved `blocking`, `warning`, or `low-risk` issues, or until the review is blocked by bounded clarification questions.

## Review mode

Pick the mode before looping:

- `review-only`: classify and report findings; do NOT edit the implementation.
  Default when the user says "review / 看一下 / 评审 / 给意见".
- `review-and-revise`: classify, fix, validate, and loop until the implementation is ready.
  Default when the user says "harden / fix all review issues / 改到能合 / 定稿".

If the mode is ambiguous, default to `review-only` for already-implemented code and state the chosen mode in the output.

## Required loop

1. Identify the target under review:
   - current working tree diff
   - staged diff
   - specific commit
   - commit range
   - user-specified files
   - pull request diff
2. Inspect repository status before making any changes; distinguish user-existing changes from current task changes.
3. Review the target using findings-first code review.
4. Cover at minimum these core dimensions:
   - requirement alignment: matches the confirmed requirements, acceptance criteria, plan, or contract; no missed behavior, wrong behavior, or over-implementation
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
6. For every finding, first decide whether it is:
   - an **objective defect** — directly contradicted by the code, diff, tests, or accepted requirements/plan/contracts
   - an **insufficient-basis finding** — cannot be safely resolved without a missing requirement decision, scope choice, behavior expectation, or ownership boundary
7. Classify every finding as `blocking`, `warning`, or `low-risk`. Each finding must include: severity, affected file or area, problem, impact, required fix.
8. Run the clarification gate for every insufficient-basis finding:
   - ask at most 1-3 bounded questions that unblock the exact behavior or scope decision
   - infer the narrowest likely intent only to formulate the question, not to justify a fix
   - if the answer is still unavailable, stop with `review_result: needs_clarification`
9. In `review-and-revise` mode, fix only issues related to the reviewed implementation. In `review-only` mode, stop here and report the findings and clarification questions.
10. Run the minimum necessary validation (see Validation).
11. Re-check the diff after changes.
12. Re-run the review.
13. Continue until `review_result` is `clean`, `clean_with_assumptions`, or `needs_clarification`.

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

## Clarification gate

Use bounded Socratic questioning only for true insufficient-basis findings.

Examples that usually require clarification instead of unilateral revision:

- requirement alignment depends on an unstated product choice or acceptance criterion
- two plausible behavior interpretations exist and current tests or docs do not disambiguate
- a scope boundary is unclear enough that a code fix could overwrite user-owned work or over-implement the request

Rules:

- Ask 1-3 concrete questions per round.
- Tie each question to one blocked behavior or scope decision.
- In `review-and-revise` mode, fix all objective defects you safely can before stopping.
- Do not invent product intent just to force `clean`.

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

Return `review_result: clean` only when:
- there are no `blocking` issues
- there are no `warning` issues
- there are no `low-risk` issues
- fixes have been applied for all findings
- minimum necessary validation has been run or explicitly justified
- no unrelated files were changed

Return `review_result: clean_with_assumptions` when:
- there are no `blocking` issues
- there are no `warning` issues
- the only remaining items are `low-risk` ones that have each been converted into
  an explicit entry in `Residual Assumptions` with a concrete `validation_method`
- requirement alignment and scope do not depend on unconfirmed intent

Return `review_result: needs_clarification` when:
- one or more insufficient-basis findings remain after bounded clarification questions
- the unresolved item is a missing behavior or scope decision rather than an objective defect the agent can fix alone

Otherwise return `issues_found`. In `review-and-revise` mode, fix and review
again. In `review-only` mode, report the findings and the recommended next owner
without editing the implementation.

## Output format

Use this exact Markdown structure. Keep the field names unchanged and keep each entry short enough to read without horizontal scrolling.

Always emit every section shown below, in the same order, even when it is empty.
When a section has no entries, write `- None` instead of omitting the section.

```markdown
## Review Result
review_result: clean | clean_with_assumptions | needs_clarification | issues_found
mode: review-only | review-and-revise

## Issues
blocking:
- severity: blocking
  area: ""
  problem: ""
  impact: ""
  required_fix: ""

warning:
- severity: warning
  area: ""
  problem: ""
  impact: ""
  required_fix: ""

low-risk:
- severity: low-risk
  area: ""
  problem: ""
  impact: ""
  required_fix: ""

## Changes Made
- file: ""
  summary: ""

## Validation
- ""

## Residual Assumptions
- assumption: ""
  validation_method: ""

## Clarification Questions
- question: ""
  why_blocked: ""
```

Then finish with the compact protocol line:

`[output: code-review-loop | completed <confidence> | mode:"review-only|review-and-revise" review_result:"clean|clean_with_assumptions|needs_clarification|issues_found" issues:"<count by severity>" fixes:"..." validation:"..." | next:<action>]`

The closing compact protocol line is mandatory. Preserve `mode` exactly as shown.

## Contract

### Preconditions

- A completed implementation diff, commit, PR, or specified file set exists to review.
- The artifact under review is code or implementation behavior, not a requirements/design/plan/test artifact.
- Repository status has been checked so user-existing changes can be distinguished from current-task changes.

### Postconditions

- `status: completed` includes `review_result`, `issues`, `fixes`, and `validation`.
- All findings are tied to correctness, regression, security, compatibility, scope, or test sufficiency.
- The reviewed implementation is either clean or explicitly blocked by unresolved findings or clarification questions.

### Invariants

- Findings come before summaries.
- Fixes stay scoped to review findings only.
- Minimum useful validation is run after fixes when feasible.

### Downstream Signals

- `review_result` tells downstream work whether implementation can proceed or must stop.
- `issues` records the remaining findings and their severity.
- `fixes` summarizes what review-driven changes were applied.
- `validation` records the checks that support the review outcome.

## Failure Handling

### Common Failure Causes

- The artifact under review is the wrong type for code review.
- Requirement alignment depends on unconfirmed user intent.
- User-existing changes are mixed with current-task changes and ownership is ambiguous.

### Retry Policy

- Re-review immediately after scoped fixes and validation.
- If a finding depends on unresolved user intent, stop and ask before continuing.

### Fallback

- Hand off to `requirements-review-loop`, `design-review-loop`, `plan-review-loop`, or `test-review-loop` if the artifact type is wrong.
- Ask the user how to proceed if unrelated user changes prevent a clean scoped review.

### Low Confidence Handling

- Keep `review_result: needs_clarification` if any finding depends on an unconfirmed assumption.
- Prefer reporting a residual risk over overstating confidence.

## Output Example

```
[output: code-review-loop | completed high | mode:"review-and-revise" review_result:"clean_with_assumptions" issues:"0 blocking, 0 warning, 0 low-risk" fixes:"tightened retry guard and removed stale debug log" validation:"pytest tests/auth/test_retry.py -k login_retry" | next:done]
```

## Deactivation Trigger

- The reviewed implementation is clean and handed to the user or the next execution step.
- The artifact under review changes materially and needs a fresh review pass.

## Constraints

- Do not stop after only reporting findings, except when running in `review-only` mode or when bounded clarification is required before safe revision.
- Do not mark the result clean or `clean_with_assumptions` while any blocking or warning issue remains.
- Do not omit required output sections; write `- None` when a section is empty.
- Do not fix unrelated code.
- Do not mix user-existing changes into the task result.
- Do not perform broad refactors unless required to fix a finding.
- Prefer minimal, targeted validation.
- Do not use to review requirements; use `requirements-review-loop` instead.
- Do not use to review design docs / RFCs / ADRs; use `design-review-loop` instead.
- Do not use to review implementation plans; use `plan-review-loop` instead.
- Do not use to review test cases themselves; use `test-review-loop` instead.
