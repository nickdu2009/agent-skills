# Wave State Model

Use this reference to decide and report the current wave state.

## Allowed States

Only use these states:

- `blocked`
- `active`
- `merge_ready`
- `next_wave_ready`

## State Definitions

### `blocked`

Use when the wave cannot safely start or continue.

Examples:

- the required phase docs are incomplete
- a lane `start_condition` is unsatisfied
- hotspot ownership is ambiguous
- a circuit-breaker event requires replanning or human input

### `active`

Use when at least one lane is currently running or being integrated.

Examples:

- serial execution is in progress
- parallel workers are active
- one lane is complete but another required lane is still running

### `merge_ready`

Use when all lanes scheduled for this execution pass are complete and the planned validation floor passed, but wave closeout or merge has not yet advanced the next wave.

Examples:

- active lanes passed validation
- seam validation passed
- the integrator is ready to merge or report completion for the current pass

### `next_wave_ready`

Use when the current wave's required work is complete and the accepted plan's exit conditions for advancing are satisfied.

Examples:

- control PR and dependent sidecars are complete
- planned merge order is satisfied
- no required lane remains blocked or deferred for this wave

## Decision Order

Choose the state in this order:

1. if a required gate or safety condition is unresolved, use `blocked`
2. else if required work is still executing or integrating, use `active`
3. else if the current pass is validated and ready to land, use `merge_ready`
4. else if the wave exit conditions are satisfied, use `next_wave_ready`

## Reporting Rule

Always pair the state with evidence:

- what gates were checked
- which lanes are complete, active, or blocked
- what validation passed
- what still prevents the next transition

Use `wave-status-snapshot.schema.md` when you need a stable field-level output shape instead of a prose summary.

## Anti-Patterns

Do not:

- invent extra labels like `ready-for-merge` or `wave-in-progress`
- mark a wave `next_wave_ready` while any required lane is still deferred
- mark a wave `merge_ready` without checking the planned validation floor
