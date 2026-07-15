---
name: design-review-loop
description: "WHAT: Review (and optionally revise) a design document — architecture design, RFC, ADR, interface design, data model, or technical proposal — against the requirements and the actual repository context. Classify the artifact type, run type-appropriate checks, classify findings with a structured schema, distinguish objective defects from clarification blockers, and either report findings (review-only) or loop review/fix until the document is clean, clean_with_assumptions, or blocked by needs_clarification. WHEN: Use when the user asks to review, validate, harden, or finalize a design doc, RFC, ADR, architecture, interface design, data model, or technical proposal. Terms like 方案 / 实现思路 / 实现方案 / 接口 / 思路 belong here. Do NOT use to review requirements (use requirements-review-loop), implementation plans / migration plans (use plan-review-loop), code diffs (use code-review-loop), or test cases (use test-review-loop)."
metadata:
  version: "0.3.0"
  tags: "review, design, documentation"
---

# design-review-loop

Use this skill to run a strict review loop for design documents.

This is not a one-pass review when running in `review-and-revise` mode. Continue looping until there are no unresolved `blocking`, `warning`, or `low-risk` issues, or until the review is blocked by bounded clarification questions.

## Review mode

Pick the mode before looping:

- `review-only`: classify and report findings; do NOT edit the document.
  Default when the user says "review / 看一下 / 评审 / 给意见".
- `review-and-revise`: classify, then revise the document and loop until clean.
  Default when the user says "harden / finalize / 改到能落地 / 定稿".

If the mode is ambiguous, default to `review-and-revise`, and state the chosen mode in the output.

## Artifact type

Classify the document into one primary type, then apply the matching checks below:

- `architecture` — system/subsystem decomposition, NFR, deployment topology
- `adr-rfc` — a decision record or proposal choosing between options
- `interface` — public API / schema / event contract design
- `data-model` — persistence model, schema change, migration
- `technical-proposal` — a mixed "实现方案 / 实现思路" document

A document may carry a secondary type; apply both check sets if so.

## Required loop

1. Read the target design document completely.
2. Identify the relevant repository / project context:
   - upstream requirements doc (if available)
   - existing architecture diagrams
   - existing public APIs, schemas, event contracts
   - non-functional constraints (performance, security, compatibility, deployment)
   - prior architecture decisions and ADRs
3. Review the document. **Universal checks apply to every artifact type:**
   - **Intent alignment** — design fully supports the upstream requirements
   - **Interface contract** — public APIs / schemas / event contracts are defined and evolvable
   - **Failure design** — error paths, degradation, rollback, monitoring approach are explicit
   - **Impact surface** — cross-module / cross-team impact and coordination points are listed
   - **Complexity proportionality** — no over-engineering; YAGNI check
   - **Repository reality** — referenced paths, modules, and contracts actually exist

   **Conditional checks by artifact type** (full checklist: [artifact-checks.md](artifact-checks.md)):
   - `architecture` / `technical-proposal`: NFR coverage (performance / security / compatibility / deployment), operability
   - `adr-rfc`: apply [adr-review.md](adr-review.md), including required sections, decision drivers, realistic alternatives, positive/negative consequences, status, replacement links, and revisit conditions
   - `interface`: backward compatibility, versioning, error semantics
   - `data-model`: forward + backward migration, data-loss risk, ownership

   The "at least 2 alternatives" check is required only for decision-style docs
   (`adr-rfc`, or any doc that selects an approach). For incremental or local
   designs with a single realistic option, require a one-line "why no
   alternative analysis is needed" instead of forcing two options.
4. For every finding, first decide whether it is:
   - an **objective defect** — directly contradicted by the document, repository reality, or accepted project constraints
   - an **insufficient-basis finding** — cannot be safely resolved without a missing product decision, interface choice, owner boundary, or acceptance expectation
5. Classify every finding as `blocking`, `warning`, or `low-risk`.
6. Run the clarification gate for every insufficient-basis finding:
   - ask at most 1-3 bounded questions that unblock the exact design decision
   - do not ask open-ended "what design do you want" questions
   - if the answer is still unavailable, stop with `review_result: needs_clarification`
7. In `review-and-revise` mode, revise the document to resolve every objective defect and every clarification-resolved finding. In `review-only` mode, stop here and report the findings and clarification questions.
8. Re-read the revised document.
9. Re-run the review.
10. Continue until `review_result` is `clean`, `clean_with_assumptions`, or `needs_clarification`.

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

## Clarification gate

Use bounded Socratic questioning only for true insufficient-basis findings.

Examples that usually require clarification instead of unilateral revision:

- the design depends on a product or policy choice not decided in requirements
- two plausible interface or ownership boundaries exist and repository reality does not force one
- an ADR chooses an option, but the acceptance basis for the choice is not actually stated anywhere

Rules:

- Ask 1-3 concrete questions per round.
- Tie each question to one blocked design decision.
- In `review-and-revise` mode, fix all objective defects you safely can before stopping.
- Do not invent architecture or interface decisions just to force `clean`.

## Scope protection

- Only edit the design document itself.
- Do not write implementation code or implementation plans.
- Review ADR content for completeness, consistency, and executability; do not perform persistence or candidate-lifecycle operations.
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
- the unresolved item is a missing design decision rather than an objective defect the agent can fix alone

Otherwise return `issues_found`. In `review-and-revise` mode, revise the document
and review again. In `review-only` mode, report the findings and the recommended
next owner without editing the document.

## Output format

Always emit these sections in order: `Review Result`, `Issues`, `Changes Made`, `Validation`, `Residual Assumptions`, and `Clarification Questions`. Use `- None` for an empty section. Keep these fields unchanged:

```markdown
review_result: clean | clean_with_assumptions | needs_clarification | issues_found
mode: review-only | review-and-revise
type: architecture | adr-rfc | interface | data-model | technical-proposal
```

Each issue records `severity`, `area`, `problem`, `impact`, and `required_fix`. Each residual assumption records `assumption` and `validation_method`; each question records `question` and `why_blocked`. See [artifact-checks.md](artifact-checks.md) for the full rendering shape.

Then finish with the compact protocol line:

`[output: design-review-loop | completed <confidence> | mode:"review-only|review-and-revise" type:"<artifact type>" review_result:"clean|clean_with_assumptions|needs_clarification|issues_found" issues:"<count by severity>" changes:"..." validation:"..." | next:<action>]`

The closing compact protocol line is mandatory. Preserve `mode` and `type` exactly as shown.

## Contract

### Preconditions

- A design document, RFC, ADR, interface design, data model, or technical proposal exists to review.
- The repository contains enough surrounding context to validate executability and alignment.
- The artifact is design-focused, not requirements, implementation plan, code, or tests.

### Postconditions

- `status: completed` includes `review_result`, `issues`, `changes`, and `validation`.
- The reviewed design is either clean or blocked by explicit design issues or clarification questions.
- Design revisions stay inside the target document.

### Invariants

- Review stays design-focused, not implementation-focused.
- Every issue is either resolved, converted into a tracked residual assumption, or surfaced as an explicit clarification blocker before a clean exit.
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
- If requirement ambiguity blocks the review after one bounded clarification round, stop and escalate upstream.

### Fallback

- If the blocking root cause is an unclear business goal / scope / acceptance criteria,
  hand back to `requirement-interview` or `requirements-review-loop`.
- If the document is really an execution plan (steps, file landing, rollback order),
  hand off to `plan-review-loop`.
- If the document is really a requirements artifact, hand off to `requirements-review-loop`.
- Only keep looping here when the unresolved issue is genuinely in the technical design itself.

### Low Confidence Handling

- Keep unresolved assumptions explicit in the document.
- Do not mark the review clean while the design still depends on guessed repository reality.
- Keep `review_result: needs_clarification` when the blocker is a missing design decision rather than a drafting defect.

## Output Example

`[output: design-review-loop | completed high | mode:"review-and-revise" type:"adr-rfc" review_result:"clean" issues:"0 blocking, 0 warning, 0 low-risk" changes:"clarified consequences" validation:"checked requirements and repository contracts" | next:implementation-planning]`

## Deactivation Trigger

- The design document is clean and handed to planning or implementation.
- The design scope changes enough that a fresh review cycle is required.

## Constraints

- Do not stop after only reporting issues, except when running in `review-only` mode or when bounded clarification is required before safe revision.
- Do not treat low-risk issues as optional notes; resolve them or convert them into tracked residual assumptions.
- Do not mark the result `clean` or `clean_with_assumptions` while any blocking or warning issue remains.
- Do not omit required output sections; write `- None` when a section is empty.
- Do not change unrelated files.
- Keep the design concise but executable.
- Prefer concrete acceptance criteria over vague guidance.
- Do not use to review requirements; use `requirements-review-loop` instead.
- Do not use to review implementation plans; use `plan-review-loop` instead.
- Do not use to review code diffs; use `code-review-loop` instead.
- Do not use to review test cases; use `test-review-loop` instead.
