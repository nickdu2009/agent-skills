---
name: phase-plan-review
description: Review phase plan outputs for upstream intent alignment, plan quality, and execution readiness before wave execution begins. Use after phase-plan has produced its outputs and before phase-execute launches any wave. Acts as a three-layer acceptance gate that can block or approve progression to execution.
---

# Phase Plan Review

Review upstream intent, plan quality, and execution readiness as an acceptance gate — not as a second planning pass.

A plan can be well-formed, validator-clean, and still encode the wrong implementation path. This skill answers three questions:

1. Does the implementation plan faithfully carry forward the original requirement and design intent?
2. Is the phase plan itself internally complete, coherent, and contract-aligned?
3. Is the plan clear enough and safe enough to hand to `$phase-execute`?

This skill is read-only. When review finds defects, the correct next step is to return to `$phase-plan`.

## Skill Assets

Resolve bundled assets relative to the directory that contains `SKILL.md`.

- `../phase-contract-tools/references/...` are the shared contract references
- `../phase-contract-tools/scripts/...` are the shared contract helpers
- this skill does **not** ship a local `scripts/` or `references/` directory; all contract helpers and references live under `../phase-contract-tools/` when both skills are installed side by side
- do not assume these files exist in the target repository
- when invoking a helper script, pass target-repository paths explicitly

If this SKILL.md and a bundled reference document disagree on a rule, this SKILL.md wins.
References elaborate and provide examples; they do not override top-level skill rules.

Read these shared contract references when needed:

- [`../phase-contract-tools/references/contract-authority-and-migration.md`](../phase-contract-tools/references/contract-authority-and-migration.md) for authority boundaries and cutover rules
- [`../phase-contract-tools/references/external-contract-authority.md`](../phase-contract-tools/references/external-contract-authority.md) for external contract authority, owned subset, excluded subset, and accepted gap rules
- [`../phase-contract-tools/references/contract-alignment-checklist.md`](../phase-contract-tools/references/contract-alignment-checklist.md) for planner and executor checks that keep contract-bound phases aligned
- [`../phase-contract-tools/references/machine-execution-schema.md`](../phase-contract-tools/references/machine-execution-schema.md) for the execution authority model and required schema fields
- [`../phase-contract-tools/references/llm-friendly-phase-schema.md`](../phase-contract-tools/references/llm-friendly-phase-schema.md) for agent-facing instruction encoding rules and banned phrases
- [`../phase-contract-tools/references/schema-consumption-rules.md`](../phase-contract-tools/references/schema-consumption-rules.md) for consuming structured phase fields
- [`../phase-contract-tools/references/prompt-derivation-from-schema.md`](../phase-contract-tools/references/prompt-derivation-from-schema.md) for prompt and kickoff rendering rules

Use these shared contract scripts:

- `uv run ../phase-contract-tools/scripts/validate_phase_execution_schema.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml`
- `uv run ../phase-contract-tools/scripts/validate_phase_doc_set.py --phase-root /path/to/repo/docs/phases --phase phaseN`
- `uv run ../phase-contract-tools/scripts/preflight_phase_execution.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --phase-root /path/to/repo/docs/phases --phase phaseN --wave <wave-id>` (when a specific wave is under review)
- `uv run ../phase-contract-tools/scripts/render_agent_prompt.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --pr <pr-id>` (optional, for prompt readiness testing)

Unless the user or environment says otherwise, treat `PHASE_DOCS_ROOT` as the phase-doc root and default it to `docs/phases`.

`$PHASE_DOCS_ROOT/README.md` may also exist at the phase-doc root. It is a required repository-level summary file, but it is not part of any `phaseN/` four-file execution set and does not affect execution authority.

## Core Principles

1. Review "are we doing the right thing?" before "can we execute it?"
2. Treat upstream requirement and design alignment as higher priority than doc completeness.
3. The review reads phase docs and upstream inputs but writes nothing.
4. Every finding must be actionable: include issue, cause, impact, and recommendation.
5. Do not second-guess milestone or scope decisions that are internally consistent.
6. Do not reopen planning debates. Surface gaps, then return to `$phase-plan` if needed.
7. Keep `phase-contract-tools` as the only contract authority.
8. If upstream inputs are missing, downgrade review scope explicitly instead of implying full approval.

## Inputs

### Required

- the phase id (e.g., `phase13`)
- the phase docs root path (e.g., `/path/to/repo/docs/phases`)
- the four-file phase doc set must exist:
  - `$PHASE_DOCS_ROOT/phaseN/roadmap.md`
  - `$PHASE_DOCS_ROOT/phaseN/plan.yaml`
  - `$PHASE_DOCS_ROOT/phaseN/wave-guide.md`
  - `$PHASE_DOCS_ROOT/phaseN/execution-index.md`
- the phase-doc root README must exist:
  - `$PHASE_DOCS_ROOT/README.md`

If any of the four files is missing, the review FAILS immediately without proceeding to deeper checks.

### Optional

- optional wave id to scope the review to a specific wave
- optional paths to upstream requirement or design documents (RFCs, architecture docs, backlog items, design specs, external specs)
- optional user-specified risk focus or acceptance criteria

## Review Mode

Before executing the review, determine which mode applies:

- **full alignment review**: all upstream inputs are available — review intent alignment, plan quality, and execution readiness
- **limited alignment review**: some but not all upstream inputs are available — review what can be traced and explicitly state what is partially reviewed
- **artifact-only review**: no upstream inputs are available — review plan quality and execution readiness only, skip intent alignment dimensions

When operating in downgraded mode, the review must state:

- which upstream inputs were unavailable
- which dimensions were only partially reviewed or skipped
- what residual risk remains because of the missing context

## Three-Layer Review Model

The review operates across three layers, each producing its own verdict:

### Layer 1: Upstream Intent Alignment

Check whether requirement documents, design documents, external contracts, and observable code reality were correctly interpreted and translated into the phase plan.

This layer covers Dimensions 1 through 5.

### Layer 2: Plan Quality

Check whether the per-phase strict four-file phase doc set is complete, coherent, scoped correctly, contract-aligned, and structurally executable, and whether the phase-doc root README is present as the repository-level summary.

This layer covers Dimensions 6 through 10.

### Layer 3: Execution Readiness

Check whether the accepted phase artifacts are ready to be safely consumed by `$phase-execute`.

This layer covers Dimension 11.

## Review Dimensions

### Dimension 1: Requirement / Design / Plan Alignment

Review whether:

- goals drifted between original requirement, accepted design, and implementation plan
- unapproved implementation choices were silently encoded into the phase
- design constraints were weakened into easier-to-execute approximations
- explicitly named inputs or public specs were omitted

Applicable in: full alignment review, limited alignment review.
Skipped in: artifact-only review.

### Dimension 2: Requirement Coverage And Traceability

Review whether:

- every goal in `roadmap.md` is covered by at least one PR's `goal` or `expected_changes` in `plan.yaml`
- every PR traces back to at least one stated goal, milestone, or explicit requirement — no orphan PRs
- key requirements map to roadmap, waves, PR tasks, validation, and done criteria
- success criteria can be traced to concrete execution work
- intentionally deferred items are explicit instead of silently missing
- key non-goals remain non-goals
- the roadmap done-when section covers all stated goals — no goal lacks a completion criterion
- the roadmap baseline accurately reflects current code state — no planned-against-stale-baseline risk

If upstream docs are provided, additionally check:

- every key requirement or design decision from the upstream docs appears in the roadmap goals or in at least one PR
- no PR introduces work that is not traceable to a requirement, design decision, or stated non-goal refinement
- any requirement that is deferred or descoped has an explicit entry in the roadmap deferred items section

Applicable in: full alignment review, limited alignment review.
Derives requirements from roadmap goals only in: artifact-only review.

### Dimension 3: Solution Correctness And Architecture Boundaries

Review whether:

- the phase plan respects module boundaries and ownership
- responsibilities are split across waves and PRs in a maintainable way
- the encoded implementation path is architecturally sound
- the plan is not forcing a bad split just to create parallelism

Applicable in: all review modes.

### Dimension 4: Constraints And Compatibility Alignment

Review whether:

- external contracts are declared correctly when applicable
- owned subset and excluded subset are explicit
- compatibility, migration, rollback, performance, security, and compliance constraints are encoded where needed
- `fail-closed` behavior is not being mistaken for contract completion

Applicable in: all review modes.

### Dimension 5: Scope Control And Omission Detection

Review whether:

- the plan expands scope without authorization
- future work is mixed into the current phase
- critical work needed to meet the stated goal is missing
- unnecessary planning artifacts or duplicated planning payloads were introduced

Applicable in: all review modes.

### Dimension 6: Dependencies, Ordering, And Wave Breakdown

Review whether:

- waves reflect real dependency order
- no wave depends on a later wave (no forward dependency cycles)
- PR dependencies (`depends_on`) respect wave ordering: a PR in wave N does not depend on a PR in a later wave
- every `start_condition` with `gate: after_prs` lists PRs that are in earlier or the same wave with earlier merge-order
- every `start_condition` with `gate: after_waves` lists wave ids that are numerically smaller
- `control_pr`, `merge_order`, and `start_condition` are coherent
- the split will not predictably force execution back into planning

Applicable in: all review modes.

### Dimension 7: Parallel Execution And Ownership Clarity

Review whether:

- lane ownership is explicit
- hotspot boundaries are clear
- hotspot ownership across waves does not create ambiguous ownership between concurrent lanes
- integrator responsibilities are assigned clearly
- parallel execution assumptions are isolated enough for safe execution
- seemingly parallel lanes are actually safe to run in parallel

Applicable in: all review modes.

### Dimension 8: Validation And Acceptance Closure

Review whether:

- validation actually proves the requirement is satisfied — not just that the code compiles
- `done_when` covers behavior, contract alignment, and risk boundaries
- validator success is not being misused as proof that the business goal is complete
- seam validation or integration validation is present when cross-lane interaction exists
- every `done_when` entry is testable — no banned phrases like `as needed`, `looks good`, `when ready`, `if needed`, `make sure`
- every `validation` entry is a structured mapping with `kind` and either `ref` or `command`
- every `validation` profile ref resolves to an entry in `validation_profiles`

Applicable in: all review modes.

### Dimension 9: Risk, Rollback, And Operational Control

Review whether:

- cutover, rollback, backfill, migration, and observation concerns are addressed
- the plan avoids "implementable but not safely releasable" outcomes
- operational hazards are surfaced rather than hidden behind task completion language
- high-risk work includes explicit gates or control points

Applicable in: all review modes.

### Dimension 10: Document Completeness And Authority Consistency

Review whether:

- the per-phase strict four-file set is present when the plan claims execution readiness
- `$PHASE_DOCS_ROOT/README.md` exists and does not claim execution authority
- the README summary for the reviewed phase does not materially contradict `roadmap.md` or `plan.yaml` on goal, scope, or status
- partial-output mode is explicitly declared when applicable
- `plan.yaml` remains the execution authority
- Markdown does not redefine YAML-owned fields
- structured task payloads are not duplicated across files
- every PR id in `plan.yaml` has a corresponding mention in `wave-guide.md` and `execution-index.md`
- every wave in `plan.yaml` has a matching heading section in `wave-guide.md`
- the reading order in `execution-index.md` lists all four files
- the authority order in `execution-index.md` places `plan.yaml` first

Validator-covered checks (already handled by `validate_phase_doc_set.py` — do not re-check manually):

- no deprecated doc names (e.g., `phaseN-pr-delivery-plan.md`) are referenced in any file
- no extra phase-local files exist in `$PHASE_DOCS_ROOT/phaseN/` beyond the strict four-file set

Applicable in: all review modes.

### Dimension 11: Execution Readiness

Review whether the plan has crossed the minimum bar for `$phase-execute`.

Run the validators first. Their output covers structural checks; this dimension then reviews what validators cannot judge.

Validator-covered checks (do not re-check manually — trust the validator output):

- schema validation has run via `uv run ../phase-contract-tools/scripts/validate_phase_execution_schema.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml` — this covers: `owner` resolves to `team[].id`, `depends_on` resolves to declared PR, `ref_kind: pr` points to same-wave PR, `ref_kind: role` points to same-wave role, `control_pr` belongs to its wave, `merge_order` covers same PR set as `waves[].prs`, every lane has `start_condition`
- doc-set validation has run via `uv run ../phase-contract-tools/scripts/validate_phase_doc_set.py --phase-root /path/to/repo/docs/phases --phase phaseN` — this covers: presence of `$PHASE_DOCS_ROOT/README.md`, deprecated doc name references, extra phase-local files, `control_pr` consistency across index and plan
- wave preflight has run when a specific wave is under review
- any skipped validation is explained with concrete residual risk

Manual review checks (validators cannot judge these — review by reading the docs):

- every `scope.allow` and `scope.deny` entry names a concrete file pattern or module, not a vague description
- every `files` entry names an actual file path or glob that is plausibly reachable
- every `start_condition` resolves to a concrete gate (`immediate`, `after_prs`, `after_waves`) with valid refs

If either validator or preflight reports hard errors, the review FAILS immediately.
This dimension also informs the final verdict rather than replacing the other dimensions.

Applicable in: all review modes.

## Contract Completeness (Cross-Cutting)

When `external_contracts` is non-empty, the following contract checks apply across Dimensions 4, 8, and 10:

- every entry in `external_contracts` has `id`, `path`, `kind`, `authority`, and `owned_scope`
- every `owned_scope` has `mode`, `include`, and `exclude`
- every PR that touches contract-sensitive surface declares `required_contracts`, `contract_guardrails`, and `contract_done_when`
- every `required_contracts` entry resolves to a declared `external_contracts[].id`
- every `accepted_contract_gaps` entry references a declared contract and has `blocking` as a boolean
- no blocking gap is present without an explicit escalation path or accepted-by attribution
- no `contract_done_when` entry uses banned phrases like `adapter unavailable` or `fail-closed`
- the roadmap has an External Contract Authority section that names the contract source
- the roadmap goals and done-when sections mention contract alignment

Layer attribution: findings from these checks affect **Layer 2 (Plan Quality)** when they concern structural completeness (missing declarations, unresolved refs). They affect **Layer 3 (Execution Readiness)** when they concern whether the plan can be safely consumed by `$phase-execute` (blocking gaps, renderer failures).

Skip these checks and mark them N/A when `external_contracts` is empty.

## Prompt Derivation Readiness (Cross-Cutting)

Verify that a prompt renderer can produce complete lane instructions from the schema alone:

- every PR has all fields needed by `render_agent_prompt.py`: `goal`, `read_first`, `start_condition`, `scope`, `files`, `expected_changes`, `guardrails`, `non_goals`, `validation`, `done_when`
- contract-bound PRs also have `required_contracts`, `contract_guardrails`, `contract_done_when`
- every `read_first` entry is a structured mapping with `path` and optional `section`
- no `read_first` entry references a file outside the strict four-file set unless it is a code path or test file
- no prompt-critical information is locked inside narrative prose that is not represented in schema fields

Optionally, test prompt rendering for a sample PR:

- `uv run ../phase-contract-tools/scripts/render_agent_prompt.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --pr <first-pr-id>`

If the renderer fails, that is a blocking finding.

Layer attribution: findings from this section affect **Layer 3 (Execution Readiness)** — if the renderer cannot produce a prompt, the plan is not ready for `$phase-execute`.

## Workflow

Follow this order:

1. Resolve the phase id, optional wave id, and available upstream source docs.
2. Decide the review mode: `full alignment review`, `limited alignment review`, or `artifact-only review`.
3. Confirm all four phase docs exist. If any is missing, FAIL immediately.
4. Run schema validation. If errors, FAIL immediately.
5. Run doc-set validation. If errors, FAIL immediately. Collect warnings.
6. If a wave is in scope, run wave preflight.
7. Read upstream requirement, design, contract, and code-baseline inputs that materially constrain the phase (if available).
8. Read the four phase docs in order: execution-index, plan.yaml, wave-guide, roadmap.
9. Evaluate findings across all applicable review dimensions.
10. Produce layer verdicts plus the overall verdict.
11. If blocking issues exist, return the plan to `$phase-plan`.

## Findings Format

Every finding must include:

- **issue**: what is wrong
- **cause**: why it happened
- **impact**: what happens if left unfixed
- **recommendation**: concrete repair action
- **blocking**: yes or no

Normally blocking:

- clear misalignment between requirement, design, and implementation plan
- required external contract declaration is missing
- a key requirement has no traceable execution mapping
- wave breakdown conflicts with real dependency structure
- `done_when` does not prove the stated objective is complete
- the per-phase strict four-file set is incomplete while the plan still claims execution readiness
- YAML and Markdown conflict on execution fields
- validators or preflight report hard errors
- the plan creates an obvious rollback or release-control gap

Normally non-blocking:

- redundant narrative wording that does not change authority or meaning
- low-risk follow-up work left outside the current phase
- roadmap prose that could be clearer but does not alter execution
- readability improvements to lane summaries when ownership and execution rules are already clear

## Verdicts

### Layer Verdicts

Each layer produces its own verdict:

- **intent alignment verdict**: Layer 1 — are we doing the right thing?
- **plan quality verdict**: Layer 2 — is the plan well-formed?
- **execution readiness verdict**: Layer 3 — can we safely hand this to `$phase-execute`?

Skipped layers in downgraded mode are marked as `not_assessed` with an explanation of what was not reviewed.

### Overall Verdict

One overall verdict:

- **ready-for-execute**: all layers pass, no blocking findings
- **ready-with-followups**: passes but carries accepted non-blocking risks that should be tracked
- **needs-repair**: has blocking findings and must return to `$phase-plan`

## Review Report Format

Output the review report to stdout. Do not write any files.

```markdown
## Phase Plan Review: phaseN

### Review Mode: full alignment review | limited alignment review | artifact-only review

### Overall Verdict: ready-for-execute | ready-with-followups | needs-repair

### Layer Verdicts
- Intent alignment: PASS | FAIL | NOT_ASSESSED (reason)
- Plan quality: PASS | FAIL
- Execution readiness: PASS | FAIL

### Validators
- Schema validation: PASSED | FAILED (N errors, M warnings)
- Doc-set validation: PASSED | FAILED (N errors, M warnings)
- Wave preflight (wave N): PASSED | FAILED | SKIPPED

### Findings

#### Blocking
| # | Dimension | Issue | Cause | Impact | Recommendation |
|---|-----------|-------|-------|--------|----------------|
| 1 | ... | ... | ... | ... | ... |

#### Non-Blocking
| # | Dimension | Issue | Cause | Impact | Recommendation |
|---|-----------|-------|-------|--------|----------------|
| 1 | ... | ... | ... | ... | ... |

### Summary
- Review mode: full alignment | limited alignment | artifact-only
- Upstream inputs: N provided, N missing
- Total PRs reviewed: N
- Total waves reviewed: N
- Requirements traceability: N/N goals covered, N orphan PRs, N explicitly deferred, N silently missing
- Contract-bound: yes/no
- External contracts: N declared, N gaps (M blocking)
- Prompt derivation: ready | blocked
- Next step: proceed to `$phase-execute` | return to `$phase-plan`
```

When the overall verdict is `ready-for-execute` or `ready-with-followups`, the next step is to proceed to `$phase-execute`.
When the overall verdict is `needs-repair`, the next step is to return to `$phase-plan` with the blocking findings.

## Reference Loading By Task

When running a full alignment review:
- read: contract-authority-and-migration.md, external-contract-authority.md, machine-execution-schema.md, llm-friendly-phase-schema.md, contract-alignment-checklist.md, schema-consumption-rules.md, prompt-derivation-from-schema.md
- run: schema validation, doc-set validation, and optionally wave preflight

When running an artifact-only or limited alignment review:
- read: machine-execution-schema.md, llm-friendly-phase-schema.md, schema-consumption-rules.md
- run: schema validation, doc-set validation, and optionally wave preflight
- explicitly state which dimensions were skipped or partially reviewed

When testing prompt readiness:
- read: prompt-derivation-from-schema.md
- run: `uv run ../phase-contract-tools/scripts/render_agent_prompt.py` with arguments as in **Use these shared contract scripts**

Do not load all references at once. Load only the set that matches the current task.

## Guardrails

- do not modify any phase doc or code file
- do not rewrite the phase plan, author missing docs, or execute waves
- do not reopen planning debates about scope, milestone design, or team assignments that are internally consistent
- do not invent new schema rules beyond what `phase-contract-tools` defines
- do not add a second contract authority
- do not treat non-blocking findings as blocking
- do not treat a pass verdict as a substitute for per-wave preflight in `$phase-execute`
- do not produce additional planning artifacts
- do not run full test suites or builds; this is a document review, not an execution check
- do not add a fifth default planning document inside any `phaseN/` directory; `$PHASE_DOCS_ROOT/README.md` is the only allowed root-level summary file in this model

## Composition

Use this skill together with:

- `$phase-contract-tools` for the sole schema, validator, renderer, and handoff contract
- `$phase-plan` when the review finds blocking issues that require plan repair
- `$phase-execute` after the review passes and execution can consume the accepted artifacts
