# Wave Execution Patterns

Use this reference when you need the default operating model for running an accepted implementation wave from the strict four-file phase doc set.

## Accepted Doc Set

Wave execution consumes exactly:

- `execution-index.md`
- `plan.yaml`
- `wave-guide.md`
- `roadmap.md`

If execution depends on any additional planning artifact, repair the phase through `$phase-plan` before launching work.

## Source Of Truth Order

Read execution docs in this order:

1. execution index
2. plan yaml
3. wave guide
4. roadmap

Use this precedence when conflicts appear:

1. `plan.yaml`
2. `execution-index.md`
3. `wave-guide.md`
4. `roadmap.md`

Narrative docs help coordination. YAML defines execution.

## Default Execution Flow

1. Confirm the phase and target wave.
2. Verify the four-file doc set exists.
3. Read the execution docs in order.
4. Resolve the wave from `waves[]`.
5. Build the execution cursor from plan plus observed git and file state.
6. Resolve lane eligibility from `lane_setup` plus `start_condition`.
7. Decide serial versus parallel execution.
8. Launch only eligible lanes.
9. Validate each lane, then the integration seam.
10. Decide the resulting wave state.

## Entry Variants

### Cold Start

Use when the user asks to execute a wave and no recent execution state is trusted.

- resolve the wave id from the current message or repository state; confirm with the user only when neither source makes the active wave unambiguous
- run preflight checks first
- read the docs in order
- emit the resolved `control_pr` and execution mode before implementation
- continue only if the wave is executable from current repository state

### Resume From Repository State

Use when work may already be in progress.

- rebuild the execution cursor from git state, branches, files, and the phase docs
- verify any existing handoff artifact before reuse
- continue if the observed state still matches the accepted wave contract

### User Changed Scope

Use when the user's latest request changes lanes, merge order, or validation expectations.

- stop execution
- do not patch around the change locally
- return to `$phase-plan`

## Pre-Launch Checklist

Before opening a wave, confirm:

- the user explicitly authorized parallel or subagent execution if multiple lanes will run
- the requested wave is named or inferable without ambiguity
- `control_pr` is set for the wave
- every lane reference resolves through `ref_kind` plus `ref`
- every active lane has a satisfied `start_condition`
- every hotspot family has at most one active owner unless the plan explicitly serializes access
- the planned validation floor is known

If any of these are missing, stop and repair the execution baseline first.

## Mode 1: Serial Wave

Use when:

- only one lane is eligible
- work is tightly coupled around one hotspot
- the user did not authorize subagents
- the requested scope is a single PR

Primary agent responsibilities:

- implement the active lane locally
- keep work inside the approved scope
- validate against the planned lane checks
- report whether the wave remains active or becomes merge-ready

## Mode 2: Default Parallel Wave

Use when:

- the user explicitly authorized multi-agent execution
- the wave already defines disjoint lanes or PRs
- hotspot ownership is explicit
- each lane can validate independently before integration

Primary agent responsibilities:

- act as integrator
- launch only lanes whose gates are satisfied
- keep hotspot ownership and merge order central
- review lane outputs by diff plus validation
- run seam validation before advancing the wave state

## Mode 3: Partial Wave Execution

Use when:

- the user requested only a subset of the wave
- one or more sidecars are intentionally deferred
- agent availability or timing constrains the current pass

Rules:

- keep the requested subset consistent with dependency order
- do not launch a lane whose `start_condition.refs` include skipped work
- report blocked or deferred lanes explicitly

## Gate Resolution Pattern

Interpret `start_condition` directly:

- `gate: immediate` means the lane may start now
- `gate: after_prs` means every referenced PR must be complete first
- `gate: after_waves` means every referenced wave must be complete first

If the gate is not satisfied, the lane is `blocked`.

## Launch Pattern

For each active lane:

1. collect `read_first` in order
2. collect scope, files, guardrails, validation, and `done_when`
3. produce one lane instruction block
4. pass that block unchanged to the worker or execute it locally

Prefer a rendered handoff artifact when the helper is available.

## Integrator Pattern

The integrator should always know:

- the current wave
- the control PR
- active versus blocked lanes
- hotspot ownership
- merge order
- validation already promised by the plan

Before declaring a wave merge-ready, confirm:

- active lanes stayed inside approved scope
- declared lane validation passed
- seam validation passed for interacting lanes
- no deferred item was silently pulled into scope

## Retry Pattern

For each lane:

- allow up to 3 validation-fix attempts by default
- if the lane still fails, stop it
- preserve the failing state
- report the blocker to the integrator

Do not run open-ended repair loops.

## Stop States

Use one of these outcomes:

- `blocked`
- `active`
- `merge_ready`
- `next_wave_ready`

## Escalate Back To Planning When

Return to `$phase-plan` when:

- the four-file phase doc set is incomplete
- Markdown and YAML disagree materially on execution fields
- lane ownership or hotspot serialization is missing or contradictory
- the requested work needs a new lane, changed merge order, or changed validation floor
- the user is effectively changing scope rather than executing the accepted phase

## Detecting Execution-Index vs Wave-Guide Conflicts

These two Markdown docs serve different purposes:

- execution-index declares reading order, authority boundaries, and doc-set navigation
- wave-guide declares human coordination context: lane visibility, merge windows, constraints

Conflicts most commonly appear when:

- execution-index lists a different wave count, control PR, or lane set than wave-guide
- wave-guide restates execution fields (scope, validation, or ownership) that differ from execution-index or YAML

When a conflict is detected:

1. treat YAML as the source of truth for all execution fields
2. use execution-index as the authoritative doc-set navigation layer
3. update wave-guide to align with YAML and execution-index
4. if the conflict cannot be resolved by alignment alone, return to `$phase-plan`
