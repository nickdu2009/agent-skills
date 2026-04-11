# Multi-Agent Root Cause Analysis

## Scenario

Checkout latency spikes intermittently. Evidence may live in the API path, database access path, and client request behavior. The task is analysis-first, not immediate editing.

## Recommended Skill Composition

- `scoped-tasking`
- `plan-before-action`
- `multi-agent-protocol`
- `conflict-resolution`
- `targeted-validation`

## Orchestration Flow

```mermaid
flowchart TD
    P[Primary Agent] --> A[Subagent A: API Path]
    P --> B[Subagent B: Database Path]
    P --> C[Subagent C: Client Path]
    A --> M[Merge Findings]
    B --> M
    C --> M
    M --> R[Conflict Resolution]
    R --> V[Targeted Adjudication]
    V --> O[Primary Recommendation]
```

## Why Parallelism Is Justified

- The suspected fault domains are low-coupling.
- Each line of investigation can be described independently.
- The primary agent can merge findings without overlapping code edits.

Parallelism is not justified if all paths collapse into the same reducer file or the same narrow edit surface.

## Example Subagent Assignments

### Subagent A: API Path

- Scope: checkout handler, service layer, request fan-out
- Goal: identify whether latency is introduced before database access
- Output format:
  - Findings
  - Evidence
  - Uncertainty
  - Recommendation

### Subagent B: Database Path

- Scope: checkout queries, indexes, transaction boundaries
- Goal: identify whether query shape or locking explains the spike
- Output format:
  - Findings
  - Evidence
  - Uncertainty
  - Recommendation

### Subagent C: Client Path

- Scope: batching, retry, duplicate request behavior
- Goal: identify whether client behavior amplifies latency
- Output format:
  - Findings
  - Evidence
  - Uncertainty
  - Recommendation

## Primary Agent Responsibilities

1. Define the split and stop conditions.
2. Ensure the subagents do not edit overlapping areas unless explicitly allowed.
3. Normalize outputs into comparable claims.
4. Use `conflict-resolution` to separate consensus from disagreement.
5. Choose the smallest adjudication step if findings conflict.

## Example Merge Outcome

- Consensus: spikes correlate with a slow query branch under one checkout option.
- Disagreement: API-path analysis blames request fan-out, while database-path analysis blames one missing index.
- Evidence weighting: query timing and execution-plan evidence is stronger than timing-only handler observations.
- Adjudication: run one targeted request with the fan-out path disabled and compare query latency directly.

## Guardrails

- Keep the subagent count between 2 and 4 unless there is a strong reason to exceed it.
- Do not allow recursive subagent spawning by default.
- Keep final synthesis with the primary agent.
- Use targeted adjudication rather than forcing certainty from weak evidence.

## Skill Protocol v2 Trace

```
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
[triggers: multi-agent-protocol:trigger conflict-resolution:defer targeted-validation:defer]
[precheck: multi-agent-protocol | result:PASS | checks:split_is_low_coupling lane_contracts_defined]
[output: multi-agent-protocol | status:completed | confidence:high | split_dimension:"by suspected fault domain" | lanes:"api path, database path, client path" | integration_plan:"merge findings, compare evidence, adjudicate only if needed" | synthesis:"database timing evidence is strongest but one API-path disagreement remains" | adjudication_needed:true | next:conflict-resolution]
[validate: multi-agent-protocol | result:PASS | checks:split_dimension synthesis]
[drop: multi-agent-protocol | reason:"lane findings collected, handed to synthesis" | active:conflict-resolution]
```
