# Wave Status Snapshot Schema

Use this reference for a stable, machine-readable execution status snapshot.

Machine validation lives in `wave-status-snapshot.schema.json`.

## Required Keys

Every execution update should provide:

- `phase_id`
- `wave_id`
- `execution_mode`
- `wave_state`
- `control_pr`
- `contract_status`
- `lanes`
- `validation`
- `next_action`
- `planning_escalation`

## Field Rules

### `phase_id`

- string
- example: `phase13`

### `wave_id`

- integer
- example: `1`

### `execution_mode`

- one of `serial` or `parallel`

### `wave_state`

- one of `blocked`, `active`, `merge_ready`, `next_wave_ready`

### `control_pr`

- string PR id from `phaseN-plan.yaml`

### `contract_status`

- mapping with at least:
  - `state`
  - `checked_contracts`
  - `blocking_gaps`
  - `accepted_gaps`

`state` should be:

- `not_applicable`
- `pending`
- `aligned`
- `blocked`

`checked_contracts` should list contract ids checked for the wave.

`blocking_gaps` and `accepted_gaps` should list gap ids or short explicit gap labels.

### `lanes`

- list of lane objects
- each lane object should include:
  - `lane_ref`
  - `ref_kind`
  - `ref`
  - `lane_state`
  - `owner`
  - `blockers`
  - `validation_status`
  - `evidence_refs`

`evidence_refs` entries should be either a non-empty string or an object with one of these keys: `branch`, `commit`, `validation`, `diff`, `artifact`, `command`. Each key maps to a string value.

`lane_state` should use:

- `not_started`
- `in_progress`
- `completed`
- `blocked`

### `validation`

- mapping with at least:
  - `lane_checks`
  - `seam_checks`
  - `status`

`status` should be:

- `not_run`
- `in_progress`
- `passed`
- `failed`

### `next_action`

- one short explicit action sentence
- example: `Wait for backend lane validation, then run seam checks.`

### `planning_escalation`

- mapping with:
  - `needed`
  - `reason`

If `needed` is `false`, set `reason` to an empty string.

## Minimal Example

```yaml
phase_id: phase13
wave_id: 2
execution_mode: parallel
wave_state: active
control_pr: P13-22
contract_status:
  state: aligned
  checked_contracts:
    - contract_api
  blocking_gaps: []
  accepted_gaps: []
lanes:
  - lane_ref: backend
    ref_kind: pr
    ref: P13-22
    lane_state: completed
    owner: runtime
    blockers: []
    validation_status: passed
    evidence_refs:
      - branch: feature/P13-22-runtime
      - validation: go test ./internal/runtime/...
  - lane_ref: docs
    ref_kind: role
    ref: closeout
    lane_state: blocked
    owner: integrator
    blockers:
      - waiting on P13-22 merge
    validation_status: not_run
    evidence_refs: []
validation:
  lane_checks:
    - P13-22 targeted tests passed
  seam_checks: []
  status: in_progress
next_action: Merge P13-22, then unblock the closeout lane.
planning_escalation:
  needed: false
  reason: ""
```

## Empty Template

```yaml
phase_id: phaseN
wave_id: 1
execution_mode: serial
wave_state: blocked
control_pr: P0-00
contract_status:
  state: not_applicable
  checked_contracts: []
  blocking_gaps: []
  accepted_gaps: []
lanes: []
validation:
  lane_checks: []
  seam_checks: []
  status: not_run
next_action: ""
planning_escalation:
  needed: false
  reason: ""
```

## Anti-Patterns

Do not:

- omit lane blockers when a lane is blocked
- use free-form state labels outside the defined enums
- report `merge_ready` or `next_wave_ready` without corresponding validation status
- report repo-local completion without stating contract alignment status
