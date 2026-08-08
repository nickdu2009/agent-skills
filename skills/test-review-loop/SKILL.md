---
name: test-review-loop
description: "WHAT: Review (and optionally revise) test cases, test strategy, coverage matrix, or new/modified test files against the code under test and the project's test conventions. Classify findings with a structured schema, distinguish objective defects from clarification blockers, and either report findings (review-only) or loop review/fix until the test set is clean, clean_with_assumptions, or blocked by needs_clarification. WHEN: Use when the user asks to review, validate, harden, or finalize test cases, test strategy, coverage matrix, 测试 / 用例 / 覆盖. Do NOT use to review production code under test, 被测代码, or 实现代码 — use code-review-loop instead. Do NOT use to review requirements (use requirements-review-loop), design docs (use design-review-loop), or implementation plans (use plan-review-loop)."
metadata:
  version: "0.2.0"
  tags: "review, testing, validation"
---

# test-review-loop

Use this skill to run a strict review loop for test cases and test strategy.

## Goal

Review the target test cases / test strategy / coverage matrix against the code under test and the project's test conventions, then either report findings or revise the tests until the result is clean.

This is not a one-pass review when running in `review-and-revise` mode. Continue looping until there are no unresolved `blocking`, `warning`, or `low-risk` issues, or until the review is blocked by bounded clarification questions.

## Review mode

Pick the mode before looping:

- `review-only`: classify and report findings; do NOT edit the tests.
  Default when the user says "review / 看一下 / 评审 / 给意见".
- `review-and-revise`: classify, revise, run tests, and loop until the test artifact is ready.
  Default when the user says "harden / finalize / 改到可信 / 定稿".

If the mode is ambiguous, default to `review-and-revise`, and state the chosen mode in the output.

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
   - **Behavior authority** — tests must not invent or authorize product behavior; a passing test is not a source of authorization for defaults, matching, thresholds, retries, fallbacks, or failure semantics
4. For every finding, first decide whether it is:
   - an **objective defect** — directly contradicted by the tests, code under test, or accepted behavior expectations
   - an **insufficient-basis finding** — cannot be safely resolved without a missing behavior expectation, acceptance criterion, or test scope decision
5. Classify every finding as `blocking`, `warning`, or `low-risk`.
6. Run the clarification gate for every insufficient-basis finding:
   - ask at most 1-3 bounded questions that unblock the exact behavior or coverage decision
   - do not ask open-ended "what tests do you want" questions
   - if the answer is still unavailable, stop with `review_result: needs_clarification`
7. In `review-and-revise` mode, revise the tests to resolve every objective defect and every clarification-resolved finding. In `review-only` mode, stop here and report the findings and clarification questions.
8. Re-run the affected tests.
9. Re-run the review.
10. Continue until `review_result` is `clean`, `clean_with_assumptions`, or `needs_clarification`.

## Issue rules

### blocking
Use for tests that pass for the wrong reason, fail to assert behavior, depend on global state, are flaky, lock in stale behavior that contradicts the current interface, or lock in unauthorized product behavior (defaults, matching, retries, fallbacks, failure semantics) that has no confirmed requirement/design/contract source.

### warning
Use for weak assertions, missing boundary or failure cases, brittle mocking, unclear test intent, or coverage gaps in critical paths.

### low-risk
Use for minor naming or readability issues, mild duplication of scaffolding, missing low-priority edge cases, or soft uncertainty about a fixture's reusability.

Low-risk issues must not be merely reported. Each low-risk issue must be resolved by adding one or more of the following to the tests:
- direct fix (rename / refactor / add assertion / add fixture)
- additional test case
- accepted assumption with a concrete verification method documented in `Residual Assumptions`

## Clarification gate

Use bounded Socratic questioning only for true insufficient-basis findings.

Examples that usually require clarification instead of unilateral revision:

- expected behavior is unclear enough that a boundary or failure test could lock in the wrong contract
- two plausible assertions exist and current requirements/docs do not disambiguate them
- it is unclear whether the target is a test artifact review or a production-code review

Rules:

- Ask 1-3 concrete questions per round.
- Tie each question to one blocked behavior or coverage decision.
- In `review-and-revise` mode, fix all objective defects you safely can before stopping.
- Do not invent product behavior just to force `clean`.
- Do not treat a green test suite as authorization for an unconfirmed behavioral policy.

## Scope protection

- Only edit test-related files (test cases, fixtures, helpers, coverage docs).
- Do not modify the production code under test.
- Do not bundle unrelated edits into the same revision pass.

Refer to AGENTS.md Behavioral Guidelines §3 (Surgical Changes) for keeping the edit minimal.

## Validation

Run the tests as validation:

- Execute the new or modified tests and confirm they pass
- For each key test, mentally simulate mutation: imagine breaking the code under test and confirm the test would catch the regression
- Verify tests pass in isolation (single-file or single-case run)
- Confirm no flaky behavior across at least one repeat run for time- or concurrency-sensitive tests

Refer to `targeted-validation` for choosing the minimum useful check.

## Clean result rule

Return `review_result: clean` only when:
- there are no `blocking` issues
- there are no `warning` issues
- there are no `low-risk` issues
- fixes have been applied for all findings
- targeted test runs have passed or the inability to run them has been explicitly justified
- no unrelated files were changed

Return `review_result: clean_with_assumptions` when:
- there are no `blocking` issues
- there are no `warning` issues
- the only remaining items are `low-risk` ones that have each been converted into
  an explicit entry in `Residual Assumptions` with a concrete `validation_method`
- the remaining assumptions do not change the expected behavior under test
- residual assumptions do not select or invent product behavior (defaults, matching, thresholds, retries, fallbacks, failure semantics)

Return `review_result: needs_clarification` when:
- one or more insufficient-basis findings remain after bounded clarification questions
- the unresolved item is a missing behavior or coverage decision rather than an objective defect the agent can fix alone

Otherwise return `issues_found`. In `review-and-revise` mode, revise the tests
and review again. In `review-only` mode, report the findings and the recommended
next owner without editing the tests.

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

`[output: test-review-loop | completed <confidence> | mode:"review-only|review-and-revise" review_result:"clean|clean_with_assumptions|needs_clarification|issues_found" issues:"<count by severity>" changes:"..." validation:"..." | next:<action>]`

The closing compact protocol line is mandatory. Preserve `mode` exactly as shown.

## Contract

### Preconditions

- A test artifact exists to review (test files, test strategy, test matrix, or test cases).
- The production behavior under test is known well enough to evaluate the test artifact.
- The artifact is test-focused, not production implementation, requirements, design, or planning.

### Postconditions

- `status: completed` includes `review_result`, `issues`, `changes`, and `validation`.
- The reviewed test set is either clean or blocked by explicit test-quality issues or clarification questions.
- Revisions stay limited to the test artifact under review.

### Invariants

- The review evaluates tests, not the production code under test.
- Every issue is either resolved, converted into a tracked residual assumption, or surfaced as an explicit clarification blocker before a clean exit.
- Validation runs the tests that were reviewed whenever feasible.

### Downstream Signals

- `review_result` tells downstream work whether the test artifact is ready.
- `issues` records remaining test-quality defects or confirms none remain.
- `changes` summarizes how the test artifact was revised.
- `validation` records the test runs or closest available checks used to support the review.

## Failure Handling

### Common Failure Causes

- The artifact is actually production code or a planning/design document.
- The tests do not clearly map to expected behavior or acceptance criteria.
- The reviewed tests cannot be run or do not exercise the intended surface.

### Retry Policy

- Re-review after each test revision until no issues remain.
- If the same unclear behavior expectation blocks the review after one bounded clarification round, stop and ask for the expected behavior explicitly.

### Fallback

- Hand off to `code-review-loop` if the user is really asking to review production code.
- Hand off to `requirements-review-loop` if the missing piece is testable acceptance criteria rather than test implementation.

### Low Confidence Handling

- Record residual uncertainty when tests are the best available proxy but cannot fully prove behavior.
- Do not mark the review clean while major coverage or assertion gaps remain.
- Keep `review_result: needs_clarification` when the blocker is a missing behavior decision rather than a drafting defect.

## Output Example

```
[output: test-review-loop | completed high | mode:"review-and-revise" review_result:"clean_with_assumptions" issues:"0 blocking, 0 warning, 0 low-risk" changes:"added partial-failure assertions and removed brittle internal-call expectation" validation:"pytest tests/notifications/test_preferences.py" | next:done]
```

## Deactivation Trigger

- The test artifact is clean and handed back to the user or the next delivery step.
- The artifact changes type or scope enough that a new review cycle is required.

## Constraints

- Do not stop after only reporting issues, except when running in `review-only` mode or when bounded clarification is required before safe revision.
- Do not treat low-risk issues as optional notes.
- Do not mark the result clean or `clean_with_assumptions` while any blocking or warning issue remains.
- Do not omit required output sections; write `- None` when a section is empty.
- Do not modify the production code under test.
- Keep tests minimal but expressive.
- Prefer behavior-level assertions over implementation-detail assertions.
- Do not use to review requirements; use `requirements-review-loop` instead.
- Do not use to review design docs; use `design-review-loop` instead.
- Do not use to review implementation plans; use `plan-review-loop` instead.
- Do not use to review production code under test; use `code-review-loop` instead.
