---
name: design-review-loop
description: "WHAT: Review and revise a design document — architecture design, RFC, ADR, interface design, data model, or technical proposal — against the requirements and the actual repository context, classify issues, fix real defects, and repeat the review/fix loop until the document is issue-free. WHEN: Use when the user asks to review, validate, harden, or finalize a design doc, RFC, ADR, architecture, interface design, data model, or technical proposal. Terms like 方案 / 实现思路 / 实现方案 / 接口 / 思路 belong here. Do NOT use to review requirements (use requirements-review-loop), implementation plans / migration plans (use plan-review-loop), code diffs (use code-review-loop), or test cases (use test-review-loop)."
metadata:
  version: "0.1.0"
  tags: "review, design, documentation"
---
# design-review-loop

Use this skill to run a strict review-and-revision loop for design documents.

## Goal

Review the target design document against the upstream requirements and the actual repository context, revise the document to resolve every issue, and repeat the review until the result is clean.

This is not a one-pass review. Continue looping until there are no `blocking`, `warning`, or `low-risk` issues.

## Required loop

1. Read the target design document completely.
2. Identify the relevant repository / project context:
   - upstream requirements doc (if available)
   - existing architecture diagrams
   - existing public APIs, schemas, event contracts
   - non-functional constraints (performance, security, compatibility, deployment)
   - prior architecture decisions and ADRs
3. Review the document along these dimensions — each is a mandatory check, not a suggestion:
   - **Intent alignment** — design fully supports the upstream requirements
   - **Solution soundness** — at least 2 alternatives considered, tradeoffs explained, primary choice justified
   - **Constraint respect** — performance / security / compatibility / deployment constraints identified and addressed
   - **Interface contract** — public APIs / schemas / event contracts defined clearly and are evolvable
   - **Failure design** — error paths, degradation, rollback, monitoring approach are explicit
   - **Complexity proportionality** — no over-engineering; YAGNI check
   - **Impact surface** — cross-module / cross-team impact is explicit; coordination points are listed
4. Classify every finding as `blocking`, `warning`, or `low-risk`.
5. Revise the document to resolve all issues.
6. Re-read the revised document.
7. Re-run the review.
8. Continue until `review_result` is `clean`.

## Issue rules

### blocking
Use for designs that cannot support a stated requirement, contradict approved architecture, omit a critical failure path, or commit to an unevolvable public interface.

### warning
Use for missing alternatives analysis, weak failure handling, unclear cross-module impact, or items that may cause significant rework when implemented.

### low-risk
Use for minor wording ambiguities, soft uncertainty about complexity tradeoffs, undocumented secondary decisions, or weak rollback detail.

Low-risk issues must not be merely reported. Each low-risk issue must be resolved by adding one or more of the following to the document:
- explicit clarification or design constraint
- additional acceptance criterion or validation step
- accepted assumption with a concrete verification method documented in `Residual Assumptions`

## Scope protection

- Only edit the design document itself.
- Do not write implementation code or implementation plans.
- Do not bundle unrelated edits into the same revision pass.

Refer to AGENTS.md Behavioral Guidelines §3 (Surgical Changes) for keeping the edit minimal.

## Validation

The design is not executed, so validation is review-level, not code-level:

- Cross-check the design against the upstream requirements doc for full coverage
- Cross-check against existing architecture diagrams and interface definitions for conflicts
- For each key decision, ask the counterfactual "what if we did NOT do this — what fails"
- For each cross-module impact, verify a coordination owner or migration note exists

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

Then finish with the compact protocol line:

`[output: design-review-loop | completed <confidence> | review_result:"clean|issues_found" issues:"<count by severity>" changes:"..." validation:"..." | next:<action>]`

## Contract

### Preconditions

- A design document, RFC, ADR, interface design, data model, or technical proposal exists to review.
- The repository contains enough surrounding context to validate executability and alignment.
- The artifact is design-focused, not requirements, implementation plan, code, or tests.

### Postconditions

- `status: completed` includes `review_result`, `issues`, `changes`, and `validation`.
- The reviewed design is either clean or blocked by explicit design issues.
- Design revisions stay inside the target document.

### Invariants

- Review stays design-focused, not implementation-focused.
- Every issue is classified and resolved before clean exit.
- Repository reality is checked against the proposed design.

### Downstream Signals

- `review_result` tells downstream planning or implementation whether the design is ready.
- `issues` records unresolved design defects or confirms none remain.
- `changes` summarizes how the document was revised.
- `validation` records the repository checks used to support the review.

## Failure Handling

### Common Failure Causes

- The artifact is not actually a design document.
- The design references repository paths, contracts, or conventions that do not exist.
- Requirements are still too unclear to validate the design.

### Retry Policy

- Re-review after each revision until no issues remain.
- If requirement ambiguity blocks the review twice, stop and escalate upstream.

### Fallback

- Hand off to `requirements-review-loop` if the document is really a requirements artifact.
- Hand off to `plan-review-loop` if the document is really an implementation plan.

### Low Confidence Handling

- Keep unresolved assumptions explicit in the document.
- Do not mark the review clean while the design still depends on guessed repository reality.

## Output Example

```
[output: design-review-loop | completed high | review_result:"clean" issues:"0 blocking, 0 warning, 0 low-risk" changes:"clarified queue ownership, tightened API versioning note" validation:"cross-checked module paths and interface names against repo" | next:implementation-planning]
```

## Deactivation Trigger

- The design document is clean and handed to planning or implementation.
- The design scope changes enough that a fresh review cycle is required.

## Constraints

- Do not stop after only reporting issues.
- Do not treat low-risk issues as optional notes.
- Do not mark the result clean while any issue remains.
- Do not change unrelated files.
- Keep the design concise but executable.
- Prefer concrete acceptance criteria over vague guidance.
- Do not use to review requirements; use `requirements-review-loop` instead.
- Do not use to review implementation plans; use `plan-review-loop` instead.
- Do not use to review code diffs; use `code-review-loop` instead.
- Do not use to review test cases; use `test-review-loop` instead.
