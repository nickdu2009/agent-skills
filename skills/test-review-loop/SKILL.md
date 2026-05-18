---
name: test-review-loop
description: "WHAT: Review and revise test cases, test strategy, coverage matrix, or new/modified test files — classify issues, fix real defects, run the tests as validation, and repeat the review/fix loop until the test set is issue-free. WHEN: Use when the user asks to review, validate, harden, or finalize test cases, test strategy, coverage matrix, 测试 / 用例 / 覆盖. Do NOT use to review production code under test, 被测代码, or 实现代码 — use code-review-loop instead. Do NOT use to review requirements (use requirements-review-loop), design docs (use design-review-loop), or implementation plans (use plan-review-loop)."
---
# test-review-loop

Use this skill to run a strict review-and-revision loop for test cases and test strategy.

## Goal

Review the target test cases / test strategy / coverage matrix against the code under test and the project's test conventions, revise the tests to resolve every issue, and repeat the review until the result is clean.

This is not a one-pass review. Continue looping until there are no `blocking`, `warning`, or `low-risk` issues.

## Required loop

1. Identify the target under review:
   - new or modified test files
   - test strategy document
   - coverage matrix
   - specific test cases under discussion
2. Identify the code under test and the existing test conventions in the repository.
3. Review the target along these dimensions — each is a mandatory check, not a suggestion:
   - **Scenario coverage** — happy path, boundary, failure, and exceptional behaviors are exercised, not only line coverage
   - **Assertion quality** — every test has explicit behavior-level assertions; a test does not pass merely because nothing was thrown
   - **Isolation** — tests have no implicit dependency on each other and can be run individually
   - **Determinism** — no flaky sources such as wall-clock time, concurrency, network, filesystem races, or unseeded randomness
   - **Readability** — test names express intent; arrange / act / assert structure is clear
   - **Maintenance cost** — no over-mocking; no duplicated scaffolding that belongs in a fixture or helper
   - **Alignment with code under test** — assertions reflect the current interface contract and do not lock in stale behavior
4. Classify every finding as `blocking`, `warning`, or `low-risk`.
5. Revise the tests to resolve all issues.
6. Re-run the affected tests.
7. Re-run the review.
8. Continue until `review_result` is `clean`.

## Issue rules

### blocking
Use for tests that pass for the wrong reason, fail to assert behavior, depend on global state, are flaky, or lock in stale behavior that contradicts the current interface.

### warning
Use for weak assertions, missing boundary or failure cases, brittle mocking, unclear test intent, or coverage gaps in critical paths.

### low-risk
Use for minor naming or readability issues, mild duplication of scaffolding, missing low-priority edge cases, or soft uncertainty about a fixture's reusability.

Low-risk issues must not be merely reported. Each low-risk issue must be resolved by adding one or more of the following to the tests:
- direct fix (rename / refactor / add assertion / add fixture)
- additional test case
- accepted assumption with a concrete verification method documented in `Residual Assumptions`

## Scope protection

- Only edit test-related files (test cases, fixtures, helpers, coverage docs).
- Do not modify the production code under test.
- Do not bundle unrelated edits into the same revision pass.

Refer to the `Change Rules` section in AGENTS.md for keeping the edit minimal.

## Validation

Run the tests as validation:

- Execute the new or modified tests and confirm they pass
- For each key test, mentally simulate mutation: imagine breaking the code under test and confirm the test would catch the regression
- Verify tests pass in isolation (single-file or single-case run)
- Confirm no flaky behavior across at least one repeat run for time- or concurrency-sensitive tests

Refer to `targeted-validation` for choosing the minimum useful check.

## Clean result rule

Only return `review_result: clean` when:
- there are no `blocking` issues
- there are no `warning` issues
- there are no `low-risk` issues
- fixes have been applied for all findings
- targeted test runs have passed or the inability to run them has been explicitly justified
- no unrelated files were changed

If any issue remains, revise the tests and review again.

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
- Do not modify the production code under test.
- Keep tests minimal but expressive.
- Prefer behavior-level assertions over implementation-detail assertions.
- Do not use to review requirements; use `requirements-review-loop` instead.
- Do not use to review design docs; use `design-review-loop` instead.
- Do not use to review implementation plans; use `plan-review-loop` instead.
- Do not use to review production code under test; use `code-review-loop` instead.
