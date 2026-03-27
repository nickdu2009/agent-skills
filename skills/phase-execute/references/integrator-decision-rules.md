# Integrator Decision Rules

Use this reference when the primary agent is coordinating a wave.

## Default Role

The primary agent is the integrator unless the wave is strictly serial.

The integrator owns:

- wave selection
- gate checks
- lane launch decisions
- hotspot serialization
- merge order enforcement
- validation decisions
- final wave state reporting

## Control PR Rules

Treat `control_pr` as the anchor for wave safety.

- know which PR is the control PR before launching sidecars
- do not let sidecars redefine the control PR contract
- do not claim wave advancement if the control PR remains incomplete

## Lane Acceptance Rules

Launch a lane only when:

- its typed reference resolves
- its `start_condition` is satisfied
- its hotspot ownership is compatible with every other active lane
- its validation plan is known

Reject or defer a lane when any of those fail.

## Isolation Rules

While workers are running:

- keep each lane in an isolated branch or worktree
- do not edit overlapping paths in the integrator tree
- use merge or diff review as the synchronization point

## Review Rules

Review workers as black-box outputs.

Accepted evidence is:

- the exact lane instruction
- the diff from base to lane
- the planned validation results

Do not use a subagent's intermediate narrative as correctness evidence.

## Merge Rules

Before merging:

- confirm merge order is respected
- confirm lane scope stayed inside plan boundaries
- confirm lane validation passed
- confirm seam validation passed for interacting lanes

If merge reveals unexpected overlap, stop and reassess hotspot ownership.

## Next-Wave Rules

A wave may advance only when:

- required lanes for the current wave are complete
- required validation passed
- the control PR contract is stable
- no unresolved blocker remains that the accepted plan still treats as in-wave work

## Refusal Rules

Stop and return to planning when:

- the accepted four-file phase model is missing
- YAML and Markdown disagree materially on execution fields
- the user requests scope changes that alter lanes, merge order, or validation commitments

## Circuit Breaker Rules

Trip the circuit breaker when:

- merge conflicts require semantic judgment across overlapping lanes
- repeated validation failures make the next safe action unclear
- the same hotspot collision appears across more than one attempted integration

When tripped:

- stop active integration
- follow `rollback-and-conflict-procedure.md`
- report the exact conflict or failing evidence
- escalate to the user or `$conflict-resolution`
