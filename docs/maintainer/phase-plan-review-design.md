# `phase-plan-review` Skill Design

## 1. Goal

`phase-plan-review` should not be limited to checking whether `phase-plan` outputs look complete. It should serve as the acceptance gate between planning and execution by answering three questions:

- Does the implementation plan faithfully carry forward the original requirement and design intent?
- Is the phase plan itself internally complete, coherent, and contract-aligned?
- Is the plan clear enough and safe enough to hand to `phase-execute`?

This is safer than artifact-only review because a plan can be well-formed, validator-clean, and still encode the wrong implementation path.

## 2. Position In The Phase Toolchain

Recommended toolchain:

- `phase-plan`: authors or repairs the phase doc set
- `phase-plan-review`: reviews upstream intent, plan quality, and execution readiness
- `phase-execute`: consumes an accepted phase and executes a selected wave
- `phase-contract-tools`: remains the sole contract authority for schema semantics, validators, renderers, and preflight helpers

`phase-plan-review` is a read-only acceptance skill.

It should not:

- rewrite the phase plan
- author missing phase docs
- redefine schema rules
- execute waves

When review finds defects, the correct next step is to return to `phase-plan`.

## 3. Design Principles

- Review "are we doing the right thing?" before "can we execute it?"
- Treat upstream requirement and design alignment as higher priority than doc completeness
- Keep `docs/phaseN-plan.yaml` as the repository execution authority
- Keep `phase-contract-tools` as the only contract authority
- Do not add a fifth default phase planning document
- If upstream inputs are missing, downgrade the review scope explicitly instead of implying full approval

## 4. Inputs

Potential review inputs include:

- original requirement docs
- accepted design docs, RFCs, migration notes, or architecture notes
- external specs or user-named contract sources
- relevant current-code baseline for ownership and feasibility checks
- `docs/phaseN-execution-index.md`
- `docs/phaseN-plan.yaml`
- `docs/phaseN-wave-guide.md`
- `docs/phaseN-roadmap.md`
- optional wave id
- optional user-specified risk focus or acceptance criteria

## 5. Outputs

The skill should produce:

- findings in this format:
  - `issue`
  - `cause`
  - `impact`
  - `recommendation`
  - `blocking or not`
- three layer verdicts:
  - `intent alignment verdict`
  - `plan quality verdict`
  - `execution readiness verdict`
- one overall verdict:
  - `ready-for-execute`
  - `ready-with-followups`
  - `needs-repair`

## 6. Review Model

`phase-plan-review` should use a three-layer review model.

### Layer 1: Upstream Intent Alignment

Check whether requirement documents, design documents, external contracts, and observable code reality were correctly interpreted and translated into the phase plan.

### Layer 2: Plan Quality

Check whether the strict four-file phase doc set is complete, coherent, scoped correctly, contract-aligned, and structurally executable.

### Layer 3: Execution Readiness

Check whether the accepted phase artifacts are ready to be safely consumed by `phase-execute`.

## 7. Review Dimensions

### 7.1 Requirement / Design / Plan Alignment

Review whether:

- goals drifted between original requirement, accepted design, and implementation plan
- unapproved implementation choices were silently encoded into the phase
- design constraints were weakened into easier-to-execute approximations
- explicitly named inputs or public specs were omitted

### 7.2 Requirement Coverage And Traceability

Review whether:

- key requirements map to roadmap, waves, PR tasks, validation, and done criteria
- key non-goals remain non-goals
- success criteria can be traced to concrete execution work
- intentionally deferred items are explicit instead of silently missing

### 7.3 Solution Correctness And Architecture Boundaries

Review whether:

- the phase plan respects module boundaries and ownership
- responsibilities are split across waves and PRs in a maintainable way
- the encoded implementation path is architecturally sound
- the plan is not forcing a bad split just to create parallelism

### 7.4 Constraints And Compatibility Alignment

Review whether:

- external contracts are declared correctly
- owned subset and excluded subset are explicit
- compatibility, migration, rollback, performance, security, and compliance constraints are encoded where needed
- `fail-closed` behavior is not being mistaken for contract completion

### 7.5 Scope Control And Omission Detection

Review whether:

- the plan expands scope without authorization
- future work is mixed into the current phase
- critical work needed to meet the stated goal is missing
- unnecessary planning artifacts or duplicated planning payloads were introduced

### 7.6 Dependencies, Ordering, And Wave Breakdown

Review whether:

- waves reflect real dependency order
- `control_pr`, `merge_order`, and `start_condition` are coherent
- seemingly parallel lanes are actually safe to run in parallel
- the split will not predictably force execution back into planning

### 7.7 Parallel Execution And Ownership Clarity

Review whether:

- lane ownership is explicit
- hotspot boundaries are clear
- integrator responsibilities are assigned clearly
- parallel execution assumptions are isolated enough for safe execution

### 7.8 Validation And Acceptance Closure

Review whether:

- validation actually proves the requirement is satisfied
- `done_when` covers behavior, contract alignment, and risk boundaries
- validator success is not being misused as proof that the business goal is complete
- seam validation or integration validation is present when cross-lane interaction exists

### 7.9 Risk, Rollback, And Operational Control

Review whether:

- cutover, rollback, backfill, migration, and observation concerns are addressed
- the plan avoids "implementable but not safely releasable" outcomes
- operational hazards are surfaced rather than hidden behind task completion language
- high-risk work includes explicit gates or control points

### 7.10 Document Completeness And Authority Consistency

Review whether:

- the strict four-file set is present when the plan claims execution readiness
- partial-output mode is explicitly declared when applicable
- `phaseN-plan.yaml` remains the execution authority
- Markdown does not redefine YAML-owned fields
- structured task payloads are not duplicated across files

### 7.11 Execution Readiness

Review whether:

- the plan has crossed the minimum bar for `phase-execute`
- schema validation has run
- doc-set validation has run
- wave preflight has run when a specific wave is under review
- any skipped validation is explained with concrete residual risk

This dimension is still a review dimension, but it should also inform the final verdict rather than replace the other dimensions.

## 8. Review Workflow

Recommended workflow:

1. Resolve the phase id, optional wave id, and available upstream source docs.
2. Decide the review mode:
   - `full alignment review`
   - `artifact-only review`
   - `limited alignment review`
3. Confirm all four phase docs exist. If any is missing, FAIL immediately.
4. Run schema validation through `phase-contract-tools`. If errors, FAIL immediately.
5. Run doc-set validation through `phase-contract-tools`. If errors, FAIL immediately.
6. If a wave is in scope, run wave preflight through `phase-contract-tools`.
7. Read the upstream requirement, design, contract, and code-baseline inputs that materially constrain the phase (if available).
8. Read the phase docs in execution order:
   - `execution-index`
   - `plan.yaml`
   - `wave-guide`
   - `roadmap`
9. Evaluate findings across the full review dimensions.
10. Produce layer verdicts plus the overall verdict.
11. If blocking issues exist, return the plan to `phase-plan`.

## 9. Review Mode Downgrade Rules

If original requirement docs, accepted design docs, external specs, or accepted upstream planning inputs are missing, the skill must not imply full approval.

Allowed downgraded review modes:

- `artifact-only review`
- `limited alignment review`

In downgraded mode, the review must state:

- which upstream inputs were unavailable
- which dimensions were only partially reviewed
- what residual risk remains because of the missing context

## 10. Blocking Findings

The following should normally be blocking:

- clear misalignment between requirement, design, and implementation plan
- required external contract declaration is missing
- a key requirement has no traceable execution mapping
- wave breakdown conflicts with real dependency structure
- `done_when` does not prove the stated objective is complete
- the strict four-file set is incomplete while the plan still claims execution readiness
- YAML and Markdown conflict on execution fields
- validators or preflight report hard errors
- the plan creates an obvious rollback or release-control gap

## 11. Non-Blocking Findings

The following are usually non-blocking unless local context raises the risk:

- redundant narrative wording that does not change authority or meaning
- low-risk follow-up work left outside the current phase
- roadmap prose that could be clearer but does not alter execution
- readability improvements to lane summaries when ownership and execution rules are already clear

## 12. Why Artifact-Only Review Is Not Enough

Artifact-only review is insufficient because it can only answer whether the plan artifacts are internally well-formed.

It cannot reliably answer:

- whether the plan still reflects the original requirement
- whether accepted design intent was preserved
- whether the plan encoded an easier but wrong implementation path
- whether the contract obligations were translated correctly from upstream sources

A useful review gate must evaluate upstream intent, plan quality, and execution readiness together.

## 13. Done Criteria

The design of `phase-plan-review` is complete when it can:

- review alignment between original requirement, accepted design, and implementation plan
- review the phase doc set for completeness, coherence, and contract alignment
- determine whether the phase is safe to hand to `phase-execute`
- keep contract authority centralized in `phase-contract-tools`
- avoid introducing a new default planning artifact
- downgrade review scope explicitly when upstream inputs are missing
- produce conclusions that clearly direct the next step:
  - return to `phase-plan`
  - proceed to `phase-execute`
  - or continue with accepted follow-up risk
