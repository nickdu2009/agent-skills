# LLM Following Performance

Use this reference to keep execution stable, resumable, and minimally inferential.

Execution discipline is part of correctness, not style.

## State Over Memory

State is in the environment, not in the prompt.

- recompute progress from `phaseN-plan.yaml`, git state, and repository artifacts
- do not rely on prior chat turns to decide what is complete
- make every wave resumable from objective state

## Immutable Instruction Handoff

Lane instructions are not summaries.

- pass rendered or schema-derived instructions unchanged
- do not compress multiple fields into loose prose
- do not rewrite guardrails, validation, or done checks

## Tool-Native Orchestration

When the platform supports delegation:

- use the delegation tool explicitly
- use background execution for parallel lanes when available
- monitor through observable artifacts such as diffs, logs, or branch state

Do not simulate orchestration with vague prose alone.

## Black-Box Lane Review

The integrator should review:

- the exact input contract
- the resulting diff
- validation evidence

The integrator should not review:

- subagent chain-of-thought
- trial-and-error terminal history
- long debugging narratives

## Retry Budget

Every lane needs a bounded repair loop.

- default to at most 3 validation-fix attempts
- stop when the budget is exhausted
- preserve failing state and report it

## Hard Bans

Never:

- paraphrase a schema-derived lane contract before delegation
- infer progress from chat history when repository state is available
- widen lane scope because a `note` field sounds flexible
- substitute a different validation command when the plan already specifies one
- skip seam validation when the accepted wave requires interacting lanes
- reuse a stale handoff artifact after the plan changed

## Detected Violation To Corrective Action

If you detect one of these failures, repair it this way:

- paraphrased lane handoff: regenerate from the renderer or schema fields and replace the paraphrased version
- uncertain execution state: rebuild the cursor from plan, git state, and artifacts before doing more work
- validation drift: discard the invented command and rerun the declared validation step
- stale handoff digest: re-render the handoff from the current plan and verify it before use

## Isolation

Parallel work must not share a mutable workspace.

- use separate branches or worktrees
- keep overlapping hotspots serialized
- merge only after lane-local validation

## Context Hygiene

Keep the primary agent's working set small.

- retain current wave state, active blockers, and next actions
- discard low-value implementation detail once a lane is reviewed
- prefer short status snapshots over replaying the whole lane history

## Anti-Patterns

Do not:

- paraphrase schema contracts before delegation
- keep retrying until the model "gets lucky"
- assume earlier chat context is trustworthy state
- let multiple lanes drift into the same hotspot family without explicit serialization
