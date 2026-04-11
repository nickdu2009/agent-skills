# Review Dimensions

This reference document defines all 11 review dimensions used by the phase-plan-review skill.

## Dimension 1: Requirement / Design / Plan Alignment

Review whether:

- goals drifted between original requirement, accepted design, and implementation plan
- unapproved implementation choices were silently encoded into the phase
- design constraints were weakened into easier-to-execute approximations
- explicitly named inputs or public specs were omitted

Applicable in: full alignment review, limited alignment review.
Skipped in: artifact-only review.

## Dimension 2: Requirement Coverage And Traceability

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

## Dimension 3: Solution Correctness And Architecture Boundaries

Review whether:

- the phase plan respects module boundaries and ownership
- responsibilities are split across waves and PRs in a maintainable way
- the encoded implementation path is architecturally sound
- the plan is not forcing a bad split just to create parallelism

Applicable in: all review modes.

## Dimension 4: Constraints And Compatibility Alignment

Review whether:

- external contracts are declared correctly when applicable
- owned subset and excluded subset are explicit
- compatibility, migration, rollback, performance, security, and compliance constraints are encoded where needed
- `fail-closed` behavior is not being mistaken for contract completion

Applicable in: all review modes.

## Dimension 5: Scope Control And Omission Detection

Review whether:

- the plan expands scope without authorization
- future work is mixed into the current phase
- critical work needed to meet the stated goal is missing
- unnecessary planning artifacts or duplicated planning payloads were introduced

Applicable in: all review modes.

## Dimension 6: Dependencies, Ordering, And Wave Breakdown

Review whether:

- waves reflect real dependency order
- no wave depends on a later wave (no forward dependency cycles)
- PR dependencies (`depends_on`) respect wave ordering: a PR in wave N does not depend on a PR in a later wave
- every `start_condition` with `gate: after_prs` lists PRs that are in earlier or the same wave with earlier merge-order
- every `start_condition` with `gate: after_waves` lists wave ids that are numerically smaller
- `control_pr`, `merge_order`, and `start_condition` are coherent
- the split will not predictably force execution back into planning

Applicable in: all review modes.

## Dimension 7: Parallel Execution And Ownership Clarity

Review whether:

- lane ownership is explicit
- hotspot boundaries are clear
- hotspot ownership across waves does not create ambiguous ownership between concurrent lanes
- integrator responsibilities are assigned clearly
- parallel execution assumptions are isolated enough for safe execution
- seemingly parallel lanes are actually safe to run in parallel

Applicable in: all review modes.

## Dimension 8: Validation And Acceptance Closure

Review whether:

- validation actually proves the requirement is satisfied — not just that the code compiles
- `done_when` covers behavior, contract alignment, and risk boundaries
- validator success is not being misused as proof that the business goal is complete
- seam validation or integration validation is present when cross-lane interaction exists
- every `done_when` entry is testable — no banned phrases like `as needed`, `looks good`, `when ready`, `if needed`, `make sure`
- every `validation` entry is a structured mapping with `kind` and either `ref` or `command`
- every `validation` profile ref resolves to an entry in `validation_profiles`

Applicable in: all review modes.

## Dimension 9: Risk, Rollback, And Operational Control

Review whether:

- cutover, rollback, backfill, migration, and observation concerns are addressed
- the plan avoids "implementable but not safely releasable" outcomes
- operational hazards are surfaced rather than hidden behind task completion language
- high-risk work includes explicit gates or control points

Applicable in: all review modes.

## Dimension 10: Document Completeness And Authority Consistency

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

## Dimension 11: Execution Readiness

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
