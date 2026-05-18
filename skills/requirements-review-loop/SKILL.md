---
name: requirements-review-loop
description: "WHAT: Review and revise a requirements document — PRD, user stories, problem statements, or acceptance criteria drafts — against the actual repository context, classify issues, fix real defects, and repeat the review/fix loop until the document is issue-free. WHEN: Use when the user asks to review, validate, harden, or finalize a requirements doc, PRD, user story, problem statement, or acceptance criteria. Do NOT use to review design docs / RFCs / ADRs / interface designs (use design-review-loop), implementation plans (use plan-review-loop), code diffs (use code-review-loop), or test cases (use test-review-loop). Terms like 方案 / 接口 / 思路 / 实现思路 / 实现方案 belong to design-review-loop; 实施方案 / 迁移方案 belong to plan-review-loop."
---
# requirements-review-loop

Use this skill to run a strict review-and-revision loop for requirements documents.

## Goal

Review the target requirements document against the real repository context and project terminology, revise the document to resolve every issue, and repeat the review until the result is clean.

This is not a one-pass review. Continue looping until there are no `blocking`, `warning`, or `low-risk` issues.

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
4. Classify every finding as `blocking`, `warning`, or `low-risk`.
5. Revise the document to resolve all issues.
6. Re-read the revised document.
7. Re-run the review.
8. Continue until `review_result` is `clean`.

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

## Scope protection

- Only edit the requirements document itself.
- Do not write design docs, implementation plans, code, or tests.
- Do not bundle unrelated edits into the same revision pass.

Refer to `minimal-change-strategy` for keeping the edit minimal.

## Validation

The requirements doc is not executed, so validation is review-level, not code-level:

- Cross-check against repository current state, existing schemas, APIs, and conventions
- Use a terminology table to verify word consistency across the document
- For every requirement, try to write a one-line "how I would verify this is met"; if it cannot be written, the requirement is not verifiable — downgrade or rewrite
- For dependencies, verify each prerequisite actually exists or has a known owner

Refer to `targeted-validation` for choosing the minimum useful check.

## Clean result rule

Only return `review_result: clean` when:
- there are no `blocking` issues
- there are no `warning` issues
- there are no `low-risk` issues
- every previous issue has been addressed in the document
- residual assumptions are explicitly documented and have validation methods

If any issue remains, revise the document and review again.

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
- Keep the document concise but verifiable.
- Prefer concrete acceptance criteria over vague guidance.
- Do not use to review design docs, RFCs, ADRs, or interface designs; use `design-review-loop` instead.
- Do not use to review implementation plans, migration plans, or task plans; use `plan-review-loop` instead.
- Do not use to review code diffs, commits, or PRs; use `code-review-loop` instead.
- Do not use to review test cases, test strategy, or coverage; use `test-review-loop` instead.
