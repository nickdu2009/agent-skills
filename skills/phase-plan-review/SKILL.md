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

The review evaluates 11 dimensions across three layers (upstream intent alignment, plan quality, and execution readiness).

For detailed dimension definitions and review criteria, see [references/review-dimensions.md](references/review-dimensions.md).

Summary of dimensions:

1. **Requirement / Design / Plan Alignment** - Are we doing the right thing?
2. **Requirement Coverage And Traceability** - Every goal mapped to execution?
3. **Solution Correctness And Architecture Boundaries** - Respects boundaries?
4. **Constraints And Compatibility Alignment** - Contracts declared correctly?
5. **Scope Control And Omission Detection** - Scope honest and complete?
6. **Dependencies, Ordering, And Wave Breakdown** - Dependencies respect ordering?
7. **Parallel Execution And Ownership Clarity** - Safe parallel execution?
8. **Validation And Acceptance Closure** - Validation proves requirements?
9. **Risk, Rollback, And Operational Control** - Safely releasable?
10. **Document Completeness And Authority Consistency** - Four-file set complete?
11. **Execution Readiness** - Ready for phase-execute?

Each dimension specifies which review modes it applies to (full alignment, limited alignment, or artifact-only).

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

# Common Anti-Patterns

- **Rewriting the plan during review.** The agent finds a wave dependency issue and immediately edits `plan.yaml` to fix it instead of reporting the finding and returning to `phase-plan`. This violates the read-only review contract and produces a plan that bypassed the authoring-validation-review cycle.
- **Treating warnings as blocking without evidence.** The agent fails review because the roadmap prose could be clearer, even though the execution schema is complete and validators pass. The review blocks execution for a cosmetic issue that does not affect implementation correctness, wasting iteration cycles.

See skill-anti-pattern-template.md for format guidelines.

## Artifact Contract

### Preconditions

- The strict four-file phase doc set and phase-root `README.md` already exist.
- Review has access to the accepted plan artifacts and any available upstream requirement or design inputs.
- The review remains read-only.

### Review Outputs

- `status: completed` includes `alignment_findings`, `blocking_issues`, and `approval_status`.
- Findings are actionable and use the repository's issue / cause / impact / recommendation / blocking format.
- The overall result states whether execution can proceed or must return to `phase-plan`.

### Invariants

- Review does not rewrite the plan.
- Missing upstream inputs downgrade review scope explicitly instead of implying full approval.
- Validator failures are treated as blocking.

## Gate Contract

- Gate passes only when the overall verdict is `ready-for-execute` or `ready-with-followups`.
- Gate blocks when any blocking finding exists, required artifacts are missing, or validators/preflight fail.
- Wave-scoped review must still respect the same blocking rules for that selected wave.

## Failure Handling

### Common Failure Causes

- The artifact set is incomplete.
- Upstream intent cannot be reviewed fully because inputs are missing.
- Schema or doc-set validation fails before manual review can proceed.

### Retry Policy

- Re-run after `phase-plan` repairs the blocking issues.
- Do not keep reviewing the same broken artifact set without an intervening repair pass.

### Fallback

- Downgrade to limited or artifact-only review only when the missing upstream context is explicit.
- Return to `phase-plan` when the plan must be repaired.
- Hand execution forward to `phase-execute` only after approval is explicit.

## Lifecycle

- Activate after `phase-plan` produces or repairs the plan artifacts.
- Deactivate once an approval or blocking verdict has been delivered.
- Deactivate when the reviewed artifacts are superseded by a newly repaired plan revision.
