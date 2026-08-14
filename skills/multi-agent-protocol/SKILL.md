---
name: multi-agent-protocol
description: "Launch and coordinate parallel subagents. Use when (1) the user explicitly asks for parallel work, (2) a task has 3+ independent investigation areas owned by different teams/modules, or (3) write-capable work can be split into 2-4 non-overlapping scopes with a clear integration owner. Implicit example: understand X system, Y service, and Z pipeline is 3 independent areas."
metadata:
  version: "0.2.0"
  tags: "coding, agents, orchestration"
---

# multi-agent-protocol

Use this skill to decide whether parallel agent work is justified and how to merge results.

## Use When

- There are 3 or more independent investigation areas.
- Different modules, artifacts, or hypotheses can be explored without shared writes.
- Parallel read-only exploration can reduce latency without creating merge confusion.
- Write-capable delegation is explicitly useful and scopes can be isolated.

## Do Not Use When

- A single direct search or file read is enough.
- Work areas overlap heavily.
- The parent agent cannot clearly synthesize the outputs.
- The active environment does not provide delegation or subagent capability.

## Delegation Modes

- Read-only delegation: launch when each subagent has a clear question, bounded scope, and evidence format.
- Write-capable delegation: before launch, emit `[delegate: <count 2-4> | split:<dimension> | risk:<low|medium|high>]`; assign non-overlapping write surfaces and one integration owner.

## Subagent Contract

Each subagent prompt must include:

- objective
- exact scope
- allowed operations
- expected evidence format
- what not to change or inspect

## Parent Duties

- Keep at most 4 subagents active unless a phase plan is warranted.
- Integrate findings; do not paste reports together.
- Preserve uncertainty when evidence is incomplete.
- Own the final decision and validation plan.

## Conflict Step

When subagent conclusions disagree:

1. Normalize each claim with evidence, source, and confidence.
2. Group claims by topic or hypothesis.
3. Compare evidence quality: direct code path, reproducible behavior, logs, then analogy.
4. Adopt only conclusions clearly supported by stronger evidence.
5. If unresolved, choose the smallest follow-up check and mark the remaining uncertainty.

## Output

`[output: multi-agent-protocol | completed <confidence> | lanes:"..." synthesis:"..." uncertainty:"..." | next:<action>]`

## Delegation Contract

### Preconditions

- The task can be split into 2-4 independent lanes.
- Each lane has a clear objective and bounded scope.
- Parallel work will save more time than it creates in merge overhead.

### Postconditions

- Delegated lanes are explicit enough that subagents can run without overlapping responsibilities.
- Write-capable launches include an explicit `[delegate: ...]` gate.
- The parent agent remains accountable for final integration.

### Invariants

- Parallelism stays opt-in, not automatic.
- Overlapping write surfaces are avoided unless explicitly justified.
- Lane prompts remain concrete about scope and expected evidence.

## Synthesis Contract

### Preconditions

- Lane outputs are available or the parent agent has enough evidence to compare them.
- The parent agent can normalize claims into a comparable format.

### Postconditions

- `status: completed` includes `lanes`, `synthesis`, and `uncertainty`.
- Conflicting findings are adjudicated by evidence quality rather than preference.
- Remaining ambiguity is preserved when the evidence does not settle it.

### Invariants

- The parent agent owns the final conclusion.
- Synthesis is more than concatenation; claims are compared and resolved.
- Uncertainty is not erased to force consensus.

## Failure Handling

### Common Failure Causes

- The task was split across overlapping or tightly coupled lanes.
- Subagent prompts were too vague to produce comparable outputs.
- Conflicts remain but the parent agent cannot justify a resolution.

### Retry Policy

- Re-split once if the first lane design is clearly wrong.
- If a second split still overlaps or stalls, stop parallelization and resume serial investigation.

### Fallback

- Collapse back to single-agent execution when the work is too coupled.
- Use a smallest follow-up check when conflicting lane outputs cannot yet be adjudicated.

### Low Confidence Handling

- Keep unresolved claims visible with evidence and confidence notes.
- Prefer narrower synthesis claims over overconfident conclusions.

## Deactivation Trigger

- Lane assignments are complete and handed to subagents, or synthesis is complete and handed back to implementation or reporting.
- The task is re-scoped into a serial path where parallelism no longer helps.
