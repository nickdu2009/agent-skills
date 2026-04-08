# Rollback And Conflict Procedure

Use this reference when merge, hotspot ownership, or validation evidence becomes unsafe.

## Purpose

Execution discipline includes stopping correctly.

When conflict handling becomes guesswork, pause the wave, preserve evidence, and escalate through the defined path instead of improvising a new plan.

## Preconditions Before Merge

Before merging any lane output:

- know the integration target branch or worktree
- know the current wave `control_pr`
- know the expected merge order
- know which hotspots are single-owner in the active pass
- know which validation must pass before and after merge

If any of these are unclear, do not start integration.

## Merge Conflict Procedure

When a merge conflict appears:

1. stop lane promotion immediately
2. preserve the conflicting branches or worktrees
3. record the exact conflicting files
4. record the lane instruction blocks and current validation evidence
5. decide whether the conflict is mechanical or semantic

Use these decisions:

- if the conflict is mechanical and clearly within one lane's approved scope, resolve it carefully and continue
- if the conflict is semantic, crosses hotspot ownership, or changes behavior outside the accepted lane contracts, trigger the circuit breaker

## Hotspot Collision Procedure

When two active lanes touch the same hotspot family without explicit serialization:

1. stop both lanes from further promotion
2. mark the affected lane or wave as `blocked`
3. preserve branch state and current evidence
4. return to the integrator decision point
5. escalate to the user or `$conflict-resolution` if the next safe owner is not already explicit in the plan

Do not silently reassign ownership mid-wave.

## Validation Failure Procedure

When validation fails after implementation or merge:

1. confirm which declared validation step failed
2. keep the repair attempt inside the same lane scope
3. count one retry against the lane budget
4. stop after the budget is exhausted
5. preserve the failing state and report it

Do not widen scope just because the first fix failed.

## Rollback Levels

Use the smallest rollback that preserves correctness:

- discard only uncommitted local work when the lane has not produced useful evidence
- keep committed lane work and stop promotion when the failure is under review
- stop the whole wave only when the failure changes hotspot ownership, merge order, or phase-level execution safety

Do not rewrite `plan.yaml` as a shortcut to make the current state look valid.

## Escalation Rules

Escalate to the user or `$conflict-resolution` when:

- merge resolution requires semantic judgment across lanes
- retry budget is exhausted and the next action is not obvious
- hotspot ownership is no longer trustworthy
- the accepted wave contract must change to proceed safely

Provide a structured escalation payload:

- `phase_id`: the current phase
- `wave_id`: the current wave
- `wave_state`: current wave state from the shared vocabulary
- `trigger`: one of `merge_conflict`, `hotspot_collision`, `validation_cascade`, `budget_exhausted`
- `affected_lanes`: list of lane refs involved
- `conflicting_paths`: list of file paths in conflict, if applicable
- `failing_commands`: list of commands that failed, if applicable
- `validation_evidence`: list of validation results available
- `last_safe_state`: description of the last known good state (branch, commit, or snapshot)
- `recommended_action`: one short sentence on what the agent believes should happen next

Rebuild the execution cursor before constructing this payload. Do not populate it from chat memory.

Machine validation lives in `escalation-payload.schema.json`.

## Resume Rule

After any rollback or conflict pause:

- rebuild the execution cursor from the repository and plan
- do not trust earlier chat summaries as the source of truth
- emit a fresh wave status snapshot before resuming work
