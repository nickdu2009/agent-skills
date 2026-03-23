---
name: subagent-orchestration
description: Decide when parallel subagents are justified, assign bounded subproblems, and merge results without losing ownership of the final answer.
tags: [coding, agents, orchestration, efficiency]
---

# Purpose

Teach a primary agent how to use parallel subagents deliberately rather than by default. The goal is to gain speed or breadth only when the task can be split cleanly and merged safely.

# When to Use

- When the task has low-coupling subproblems that can be described independently.
- When multiple hypotheses can be tested in parallel.
- When modules, responsibilities, or artifact types can be separated cleanly.
- When synthesis cost is lower than serial investigation cost.

# When Not to Use

- For tiny tasks.
- For same-file fine-grained edits.
- For shared-state changes that require tight coordination.
- For tasks with strong sequential dependency.
- When the primary agent cannot clearly define subproblem boundaries.

# Core Rules

- Parallelism is not the default.
- Only parallelize when subtasks are low-coupling and independently describable.
- Good split dimensions include module, responsibility, artifact type, or hypothesis.
- Bad cases include shared-state edits, same-file fine-grained edits, strong sequential dependency, or tiny tasks.
- Define a clear subagent input and output contract.
- Primary agent owns final synthesis.
- Default cap: 2 to 4 subagents.
- Subagents should not recursively spawn more subagents unless explicitly allowed.
- When parallelism is not justified, fall back to serial execution.

# Execution Pattern

1. Decide whether serial execution is good enough.
2. If not, identify a clean split dimension.
3. Define bounded subproblems with clear stop conditions.
4. Give each subagent explicit scope, evidence expectations, and non-goals.
5. Collect outputs in a normalized format.
6. Merge, compare, and synthesize centrally.
7. Assign any final edits or adjudication to the primary agent unless explicitly delegated.

# Input Contract

Provide to each subagent:

- the precise objective
- the allowed scope
- excluded areas
- the type of evidence to gather
- the required output format
- whether edits are allowed
- the stop condition

Standard subagent output format:

- Findings
- Evidence
- Uncertainty
- Recommendation

# Output Contract

Return from the primary agent:

- whether parallelism was justified
- the chosen split dimension
- each subagent assignment
- merged findings
- unresolved uncertainty
- the final recommendation or next action

# Guardrails

- Do not use subagents to hide unclear thinking.
- Do not assign overlapping edit scopes unless collision is explicitly managed.
- Do not parallelize tasks that mostly require one coherent reasoning chain.
- Do not exceed the default cap without a clear reason.
- Keep synthesis centralized; subagents inform, the primary agent decides.

# Composition

Combine with:

- `plan-before-action` to define the overall decomposition plan
- `scoped-tasking` to keep each subagent bounded
- `conflict-resolution` when outputs overlap or disagree
- `targeted-validation` after synthesis to test the chosen conclusion cheaply

# Example

Task: "Find the cause of intermittent checkout latency."

A justified split could be:

- subagent 1: API handler and service path
- subagent 2: database query and index path
- subagent 3: client request batching and retry behavior

This is a good parallel case because each line of investigation has low coupling and produces analyzable evidence. It is a bad case for overlapping edits to one checkout reducer file.
