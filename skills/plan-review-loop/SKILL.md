---
name: plan-review-loop
description: "WHAT: Review (and optionally revise) a project plan file against the actual repository code, docs, configuration, and constraints. Classify findings with a structured schema, distinguish objective plan defects from clarification blockers, and either report findings (review-only) or loop review/fix until the plan is clean, clean_with_assumptions, or blocked by needs_clarification. WHEN: Use when the user asks to review, validate, harden, or finalize an implementation plan, migration plan, refactor plan, task plan, roadmap, or any plan-like document before coding."
metadata:
  version: "0.2.0"
  tags: "review, planning, documentation"
---

# plan-review-loop

Use this skill to run a strict review loop for plan files.

## Goal

Review the target plan against the real repository context, then either report findings or revise the plan until the result is clean.

This is not a one-pass review when running in `review-and-revise` mode. Continue looping until there are no unresolved `blocking`, `warning`, or `low-risk` issues, or until the review is blocked by bounded clarification questions.

## Review mode

Pick the mode before looping:

- `review-only`: classify and report findings; do NOT edit the plan.
  Default when the user says "review / 看一下 / 评审 / 给意见".
- `review-and-revise`: classify, revise, and loop until the plan is ready.
  Default when the user says "harden / finalize / 改到能执行 / 定稿".

If the mode is ambiguous, default to `review-and-revise`, and state the chosen mode in the output.

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
   - **upstream alignment** — consistent with approved design / requirements
   - **sequencing** — step dependencies correct; rollback feasible
   - **scope control** — no unauthorized changes smuggled in
   - **file-level landing** — each step names specific paths or modules
   - **per-step validation** — each step has a verifiable acceptance check
   - **risk mitigation** — critical risks have mitigation
   - **repository reality** — referenced files / interfaces / conventions actually exist
4. For every finding, first decide whether it is:
   - an **objective defect** — directly contradicted by the plan, repository reality, or accepted upstream constraints
   - an **insufficient-basis finding** — cannot be safely resolved without a missing sequencing decision, rollout preference, ownership choice, or acceptance expectation
5. Classify every finding as `blocking`, `warning`, or `low-risk`.
6. Run the clarification gate for every insufficient-basis finding:
   - ask at most 1-3 bounded questions that unblock the exact planning decision
   - do not ask open-ended "what plan do you want" questions
   - if the answer is still unavailable, stop with `review_result: needs_clarification`
7. In `review-and-revise` mode, revise the plan to resolve every objective defect and every clarification-resolved finding. In `review-only` mode, stop here and report the findings and clarification questions.
8. Re-read the revised plan.
9. Re-run the review.
10. Continue until `review_result` is `clean`, `clean_with_assumptions`, or `needs_clarification`.

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

## Clarification gate

Use bounded Socratic questioning only for true insufficient-basis findings.

Examples that usually require clarification instead of unilateral revision:

- the plan assumes a rollout order, split-PR shape, or owner handoff not stated upstream
- two plausible landing sequences exist and the repository does not force one
- success criteria are too vague to decide whether a step should exist at all

Rules:

- Ask 1-3 concrete questions per round.
- Tie each question to one blocked planning decision.
- In `review-and-revise` mode, fix all objective defects you safely can before stopping.
- Do not invent rollout or ownership decisions just to force `clean`.

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

Return `review_result: clean` only when:
- there are no `blocking` issues
- there are no `warning` issues
- there are no `low-risk` issues
- every previous issue has been addressed in the plan

Return `review_result: clean_with_assumptions` when:
- there are no `blocking` issues
- there are no `warning` issues
- the only remaining items are `low-risk` ones that have each been converted into
  an explicit entry in `Residual Assumptions` with a concrete `validation_method`

Return `review_result: needs_clarification` when:
- one or more insufficient-basis findings remain after bounded clarification questions
- the unresolved item is a missing planning decision rather than an objective defect the agent can fix alone

Otherwise return `issues_found`. In `review-and-revise` mode, revise the plan and
review again. In `review-only` mode, report the findings and the recommended next
owner without editing the plan.

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

`[output: plan-review-loop | completed <confidence> | mode:"review-only|review-and-revise" review_result:"clean|clean_with_assumptions|needs_clarification|issues_found" issues:"<count by severity>" changes:"..." validation:"..." | next:<action>]`

The closing compact protocol line is mandatory. Preserve `mode` exactly as shown.

## Contract

### Preconditions

- A plan artifact exists to review.
- The repository provides enough context to validate landing surfaces, sequencing, and verification.
- The artifact is an implementation/refactor/migration/task plan, not requirements, design, code, or tests.

### Postconditions

- `status: completed` includes `review_result`, `issues`, `changes`, and `validation`.
- The plan is either clean or blocked by explicit planning defects or clarification questions.
- Revisions stay inside the target plan artifact.

### Invariants

- The review stays plan-focused, not code-focused.
- Every issue is either resolved, converted into a tracked residual assumption, or surfaced as an explicit clarification blocker before a clean exit.
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
- If the same planning gap recurs after one bounded clarification round, stop and escalate upstream rather than looping blindly.

### Fallback

- Hand off to `design-review-loop` if the artifact is actually a design doc.
- Hand off to `requirements-review-loop` if the artifact is really missing business scope or acceptance criteria.
- Hand off to `code-review-loop` if the artifact is already implemented and the user really wants code review.

### Low Confidence Handling

- Preserve residual assumptions with explicit validation methods.
- Do not mark the plan clean while execution still depends on guessed sequencing or landing.
- Keep `review_result: needs_clarification` when the blocker is a missing planning decision rather than a drafting defect.

## Output Example

```
[output: plan-review-loop | completed high | mode:"review-and-revise" review_result:"clean_with_assumptions" issues:"0 blocking, 0 warning, 0 low-risk" changes:"added missing rollback note and tied AC3 to step 4" validation:"confirmed referenced files and checks exist in repo" | next:implementation]
```

## Deactivation Trigger

- The plan artifact is clean and handed to implementation.
- The plan is reframed into a different artifact type and needs a different review loop.

## Constraints

- Do not stop after only reporting issues, except when running in `review-only` mode or when bounded clarification is required before safe revision.
- Do not treat low-risk issues as optional notes.
- Do not mark the result clean or `clean_with_assumptions` while any blocking or warning issue remains.
- Do not omit required output sections; write `- None` when a section is empty.
- Do not change unrelated files.
- Keep the plan concise but executable.
- Prefer concrete validation and acceptance criteria over vague guidance.
- Keep the artifact type narrow: this skill reviews plans, not requirements, designs, code diffs, or test cases.
