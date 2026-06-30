---
name: requirements-review-loop
description: "WHAT: Review (and optionally revise) a requirements document — PRD, user stories, problem statements, or acceptance criteria drafts — against the actual repository context. Classify findings with a structured schema, distinguish objective defects from clarification blockers, and either report findings (review-only) or loop review/fix until the document is clean, clean_with_assumptions, or blocked by needs_clarification. WHEN: Use when the user asks to review, validate, harden, or finalize a requirements doc, PRD, user story, problem statement, or acceptance criteria. Do NOT use to review design docs / RFCs / ADRs / interface designs (use design-review-loop), implementation plans (use plan-review-loop), code diffs (use code-review-loop), or test cases (use test-review-loop). Terms like 方案 / 接口 / 思路 / 实现思路 / 实现方案 belong to design-review-loop; 实施方案 / 迁移方案 belong to plan-review-loop."
metadata:
  version: "0.2.0"
  tags: "review, requirements, documentation"
---

# requirements-review-loop

Use this skill to run a strict review loop for requirements documents.

## Goal

Review the target requirements document against the real repository context and project terminology, then either report findings or revise the document until the result is clean.

This is not a one-pass review when running in `review-and-revise` mode. Continue looping until there are no unresolved `blocking`, `warning`, or `low-risk` issues, or until the review is blocked by bounded clarification questions.

## Review mode

Pick the mode before looping:

- `review-only`: classify and report findings; do NOT edit the document.
  Default when the user says "review / 看一下 / 评审 / 给意见".
- `review-and-revise`: classify, revise, and loop until the document is ready.
  Default when the user says "harden / finalize / 改到能落地 / 定稿".

If the mode is ambiguous, default to `review-and-revise`, and state the chosen mode in the output.

## Required loop

1. Read the target requirements document completely.
2. Identify the relevant repository / project context:
   - existing requirements docs
   - source code as far as it constrains what is feasible
   - existing schemas, APIs, data models
   - the project terminology table (if any)
   - prior decisions or constraints
3. Review the document along these dimensions — each is a mandatory check, not a suggestion:
   - **Clarity** — every requirement names an action and a target object
   - **Completeness** — inputs / outputs / boundaries / failure scenarios / non-functional constraints are present
   - **Verifiability** — every requirement has an observable acceptance criterion
   - **Consistency** — no internal contradictions; terminology aligned with the project word list
   - **Scope sanity** — neither over-broad nor over-narrow; implicit assumptions made explicit
   - **Feasibility** — no obvious conflict with current code / product state (when repo is available)
   - **Dependencies & priority** — prerequisites are stated; must-have vs nice-to-have is clear
4. For every finding, first decide whether it is:
   - an **objective defect** — directly contradicted by the document, repository reality, or accepted project constraints
   - an **insufficient-basis finding** — cannot be safely resolved without a missing business decision, role boundary, scope choice, or acceptance expectation
5. Classify every finding as `blocking`, `warning`, or `low-risk`.
6. Run the clarification gate for every insufficient-basis finding:
   - ask at most 1-3 bounded questions that unblock the exact requirement decision
   - do not ask open-ended "what do you want" questions
   - if the answer is still unavailable, stop with `review_result: needs_clarification`
7. In `review-and-revise` mode, revise the document to resolve every objective defect and every clarification-resolved finding. In `review-only` mode, stop here and report the findings and clarification questions.
8. Re-read the revised document.
9. Re-run the review.
10. Continue until `review_result` is `clean`, `clean_with_assumptions`, or `needs_clarification`.

## Issue rules

### blocking
Use for missing required behavior, internal contradictions, requirements with no possible acceptance criterion, or items that violate confirmed project constraints.

### warning
Use for uncovered boundary scenarios, inconsistent terminology, undeclared assumptions, weak priority signal, or items likely to cause downstream rework.

### low-risk
Use for minor wording ambiguities, missing priority, soft uncertainty about scope, or weak verifiability hints.

Low-risk issues must not be merely reported. Each low-risk issue must be resolved by adding one or more of the following to the document:
- explicit clarification or constraint
- validation step or acceptance criterion
- accepted assumption with a concrete verification method documented in `Residual Assumptions`

## Clarification gate

Use bounded Socratic questioning only for true insufficient-basis findings.

Examples that usually require clarification instead of unilateral revision:

- the actor / owner of a requirement is missing and the repository does not imply one
- the business rule depends on priority, rollout, or policy preference not stated anywhere
- two plausible acceptance criteria exist and neither is confirmed by current docs or code

Rules:

- Ask 1-3 concrete questions per round.
- Tie each question to one blocked requirement decision.
- In `review-and-revise` mode, fix all objective defects you safely can before stopping.
- Do not invent product decisions just to force `clean`.

## Scope protection

- Only edit the requirements document itself.
- Do not write design docs, implementation plans, code, or tests.
- Do not bundle unrelated edits into the same revision pass.

Refer to AGENTS.md Behavioral Guidelines §3 (Surgical Changes) for keeping the edit minimal.

## Validation

The requirements doc is not executed, so validation is review-level, not code-level:

- Cross-check against repository current state, existing schemas, APIs, and conventions
- Use a terminology table to verify word consistency across the document
- For every requirement, try to write a one-line "how I would verify this is met"; if it cannot be written, the requirement is not verifiable — downgrade or rewrite
- For dependencies, verify each prerequisite actually exists or has a known owner

Refer to `targeted-validation` for choosing the minimum useful check.

## Clean result rule

Return `review_result: clean` only when:
- there are no `blocking` issues
- there are no `warning` issues
- there are no `low-risk` issues
- every previous issue has been addressed in the document

Return `review_result: clean_with_assumptions` when:
- there are no `blocking` issues
- there are no `warning` issues
- the only remaining items are `low-risk` ones that have each been converted into
  an explicit entry in `Residual Assumptions` with a concrete `validation_method`

Return `review_result: needs_clarification` when:
- one or more insufficient-basis findings remain after bounded clarification questions
- the unresolved item is a missing requirement decision rather than an objective defect the agent can fix alone

Otherwise return `issues_found`. In `review-and-revise` mode, revise the document
and review again. In `review-only` mode, report the findings and the recommended
next owner without editing the document.

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

`[output: requirements-review-loop | completed <confidence> | mode:"review-only|review-and-revise" review_result:"clean|clean_with_assumptions|needs_clarification|issues_found" issues:"<count by severity>" changes:"..." validation:"..." | next:<action>]`

The closing compact protocol line is mandatory. Preserve `mode` exactly as shown.

## Contract

### Preconditions

- A requirements artifact exists to review (PRD, user story, problem statement, or acceptance criteria draft).
- The repository provides enough context to validate scope, feasibility, and terminology.
- The artifact is requirements-focused, not design, implementation plan, code, or tests.

### Postconditions

- `status: completed` includes `review_result`, `issues`, `changes`, and `validation`.
- The requirements are either clean or blocked by explicit requirement defects or clarification questions.
- Revisions stay limited to the target requirements artifact.

### Invariants

- The review stays at the requirements level rather than jumping into implementation design.
- Every issue is either resolved, converted into a tracked residual assumption, or surfaced as an explicit clarification blocker before a clean exit.
- Acceptance criteria remain observable and business-facing.

### Downstream Signals

- `review_result` tells downstream design or planning whether the requirements are ready.
- `issues` records any remaining requirement gaps or confirms none remain.
- `changes` summarizes how the requirements artifact was revised.
- `validation` records the repository/context checks used to support the review.

## Failure Handling

### Common Failure Causes

- The artifact is actually design or planning material.
- Business goal, roles, scope, or acceptance criteria are still too ambiguous to validate.
- Repository terminology or constraints contradict the written requirements.

### Retry Policy

- Re-review after each revision until no issues remain.
- If requirement ambiguity remains after one bounded clarification round, stop and ask rather than forcing a rewrite.

### Fallback

- Hand off to `requirement-interview` if the artifact is still too vague and needs interactive clarification.
- Hand off to `design-review-loop` if the artifact is actually a technical design doc.
- Hand off to `plan-review-loop` if the artifact is really an execution plan rather than a requirement.

### Low Confidence Handling

- Keep unresolved requirement assumptions visible.
- Do not mark the review clean while business-critical ambiguity remains.
- Keep `review_result: needs_clarification` when the blocker is a missing business decision rather than a drafting defect.

## Output Example

```
[output: requirements-review-loop | completed high | mode:"review-and-revise" review_result:"clean_with_assumptions" issues:"0 blocking, 0 warning, 0 low-risk" changes:"made acceptance criteria observable and split must-have vs later scope" validation:"checked terminology and referenced modules against repo docs" | next:design-before-plan]
```

## Deactivation Trigger

- The requirements artifact is clean and handed to design or planning.
- The artifact changes scope substantially and needs a fresh review cycle.

## Constraints

- Do not stop after only reporting issues, except when running in `review-only` mode or when bounded clarification is required before safe revision.
- Do not treat low-risk issues as optional notes.
- Do not mark the result clean or `clean_with_assumptions` while any blocking or warning issue remains.
- Do not omit required output sections; write `- None` when a section is empty.
- Do not change unrelated files.
- Keep the document concise but verifiable.
- Prefer concrete acceptance criteria over vague guidance.
- Do not use to review design docs, RFCs, ADRs, or interface designs; use `design-review-loop` instead.
- Do not use to review implementation plans, migration plans, or task plans; use `plan-review-loop` instead.
- Do not use to review code diffs, commits, or PRs; use `code-review-loop` instead.
- Do not use to review test cases, test strategy, or coverage; use `test-review-loop` instead.
