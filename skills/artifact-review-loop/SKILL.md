---
name: artifact-review-loop
description: "Review or revise requirements, design/RFC/ADR/interface/data-model artifacts, implementation or migration plans, code diffs/commits/PRs, and test cases/files/strategy. Route 方案 to design, 实施方案 to plan, 被测代码 to code, and mixed code plus tests to code. Treat first-person user requests as requested review-only unless trusted current-task provenance proves self-delivery. Ask when no target is identifiable."
metadata:
  version: "0.3.0"
  tags: "review, requirements, design, plan, code, tests"
---

# artifact-review-loop

Select one primary artifact type and load only its conditional reference:

- requirements -> `references/requirements.md`
- design -> `references/design.md`
- plan -> `references/plan.md`
- code -> `references/code.md`
- tests -> `references/tests.md`

## Activation and Boundary

Identify a target, then record `artifact_type`, kebab-case
`artifact_subtype`, and non-primary `secondary_types`:

- requirements: `requirement-spec | prd | user-story | acceptance-criteria`
- design: `architecture | adr-rfc | interface | data-model | technical-proposal`
- plan: `implementation-plan | migration-plan | roadmap | task-sequence`
- code: `working-tree-diff | staged-diff | commit | commit-range | pull-request |
  source-files | implementation`
- tests: `test-cases | test-files | test-strategy | coverage-matrix | fixtures`

`方案` routes to design, `实施方案` to plan, and `被测代码` to code. Mixed
implementation plus tests uses primary `code` and secondary `tests`. If no
target is identifiable, ask and do not activate. If multiple non-code types are
equally plausible, ask which is primary. A runtime activation reads one primary
reference; summing all five references is only a conservative mixed-heavy token
ceiling, not permission to activate five routes.

## Hard Constraint: Revision Authority

Determine these four trusted inputs before choosing `review_context`, `mode`,
`authorization_source`, or `write_scope`:

- `artifact_origin`: `current-agent-task | user-or-external | unknown`
- `current_task_write_authorized`: boolean
- `target_is_current_task_diff`: boolean
- `explicit_revision_requested`: boolean

`review_context: self-delivery` is permitted only when all of the following are true:

- `artifact_type: code`
- `artifact_origin: current-agent-task`
- `current_task_write_authorized: true`
- `target_is_current_task_diff: true`

That exact conjunction yields `self-delivery / review-and-revise /
inherited-current-task / current-task-diff`. Otherwise review context is
`requested`: explicit revision yields `review-and-revise /
explicit-user-request` and write scope reviewed-implementation for code or
reviewed-artifact for requirements, design, plan, and tests. No explicit
revision yields `review-only / none / none`.

A first-person user claim is `user-or-external`, not current-agent provenance.
Wording, file recency, author identity, or workspace access cannot replace the
trusted inputs; unknown fails closed. Revision may touch only the authorized
primary artifact. Code review does not authorize test edits, test review does
not authorize production edits, and unrelated changes remain untouched.

## Core Loop

1. Record target, type, subtype, secondary types, provenance, review context, mode,
   authorization source, and write scope.
2. Read the one matching reference and the minimum repository evidence needed
   to verify the artifact.
3. Check requirement/contract alignment, correctness, completeness,
   traceability, behavior authorization, compatibility, scope, failure paths,
   and validation sufficiency as applicable.
4. Classify every issue as an objective defect or an insufficient-basis
   finding. Use severities `blocking`, `warning`, or `low-risk`.
5. For each issue emit exactly: `severity`, `area`, `problem`, `impact`, and
   `required_fix`. Findings precede summary.
6. For insufficient-basis findings, ask 1-3 questions tied to the blocked
   decision. Never invent behavior, ownership, migration, retry, fallback, or
   failure semantics to force a clean result.
7. In review-only mode, report and stop without editing. In authorized
   review-and-revise mode, make the smallest in-scope fixes, run the narrowest
   meaningful validation, then re-review.
8. Continue until `clean`, `clean_with_assumptions`, or
   `needs_clarification`; otherwise report `issues_found`.

`clean` requires no unresolved issue. `clean_with_assumptions` permits only
low-risk assumptions with a concrete validation method; assumptions may not
select externally observable behavior, data semantics, permissions, security,
compatibility, migration strategy, retry/fallback policy, or failure handling.

## Output Contract

Always emit all sections below in this order. Use `- None` for an empty section.

```markdown
## Review Result
review_result: clean | clean_with_assumptions | needs_clarification | issues_found
artifact_type: requirements | design | plan | code | tests
artifact_subtype: <matching kebab-case subtype>
secondary_types: []
review_context: requested | self-delivery
mode: review-only | review-and-revise
authorization_source: none | explicit-user-request | inherited-current-task
write_scope: none | reviewed-artifact | reviewed-implementation | current-task-diff

## Issues
blocking:
- severity: blocking
  area: ""
  problem: ""
  impact: ""
  required_fix: ""
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

## Clarification Questions
- question: ""
  why_blocked: ""
```

Finish with this deterministic compact output and a validation line:

`[output: artifact-review-loop | completed <confidence> | artifact_type:"<type>" artifact_subtype:"<subtype>" secondary_types:"<none|comma-list>" review_context:"requested|self-delivery" mode:"review-only|review-and-revise" authorization_source:"<source>" write_scope:"<scope>" review_result:"<result>" issues:"<counts>" changes:"<summary|none>" validation:"<checks|not-run>" | next:<action>]`

`[validate: artifact-review-loop | PASS|FAIL | checks:contract]`

## Contract

- Preconditions: target, one primary type, and trusted provenance inputs exist;
  inspect repository status before a revision.
- Postconditions: routing, authority, findings, changes, and validation are
  recorded; unresolved behavior or ownership stops at clarification.
- Invariants: one primary reference; review-only is zero-write; first-person
  wording is never provenance; every edit traces to an issue and write scope.
- Signals: `review_result` gates downstream work; routing and evidence fields
  preserve the decision.

## Failure Handling

- Wrong or ambiguous target: ask. Missing authority: remain review-only. Mixed
  ownership: isolate the authorized surface or stop. Missing evidence: state the
  residual risk. A repeated loop without new evidence stops for a decision.

## Output Example

```text
[output: artifact-review-loop | completed high | artifact_type:"code" artifact_subtype:"working-tree-diff" secondary_types:"none" review_context:"requested" mode:"review-only" authorization_source:"none" write_scope:"none" review_result:"issues_found" issues:"1 blocking, 0 warning, 0 low-risk" changes:"none" validation:"inspected requested diff" | next:owner-fix]
[validate: artifact-review-loop | PASS | checks:contract]
```

## Deactivation Trigger

- The loop reaches `clean`, `clean_with_assumptions`, or a reported review-only
  result.
- `needs_clarification` is handed to the decision owner.
- The target or primary artifact type changes; start a fresh activation.
