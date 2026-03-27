---
name: context-budget-awareness
version: 0.1.0
description: Compress and refocus the working state when a session grows long, hypotheses accumulate, or the active file set expands beyond what the current step needs. Extends the AGENTS.md Context Budget rules with a structured compression and rehydration pattern.
tags: [coding, agents, orchestration, efficiency]
---

# Purpose

Teach the agent to control context growth. The skill helps avoid bloated sessions, repeated reading, and irrelevant history so that current reasoning stays attached to the live objective instead of accumulated noise.

# When to Use

- In long debugging or refactoring sessions.
- When the working set exceeds 8 files without a recent scope-narrowing step.
- When the same file has been read more than twice without a new question driving the re-read.
- When more than 3 hypotheses are active without evidence to rank them.
- When the agent's last 3 actions did not advance the stated objective.
- When a fresh focused pass may be cheaper than carrying the current context forward.

These thresholds (8 files, 2 re-reads, 3 hypotheses, 3 stalled actions) are starting defaults. Adjust downward for small focused tasks or upward for large multi-module investigations where broader context is expected.

# When Not to Use

- In a short task with a stable, compact working set.
- When a small amount of extra context is essential to avoid repeated discovery.
- When the user explicitly wants a broad historical recap.

# Core Rules

- Avoid long, bloated sessions when a fresh focused session is better.
- Avoid repeatedly re-reading large files without need.
- Avoid injecting excessive policy, logs, or irrelevant history.
- Summarize and compress state whenever a milestone is reached.
- Keep active context aligned to the current objective.
- Distinguish between live context, deferred context, and discarded context.

# Execution Pattern

1. Track the current objective and working set explicitly.
2. Read only the slices of information needed for the next step.
3. After each milestone, compress the state using the standard summary template:
   ```
   - Symptom / Objective: ...
   - Confirmed scope: ...
   - Ruled out: ...
   - Next step: ...
   ```
   A milestone is any of: a file was edited successfully, a hypothesis was confirmed or ruled out, the analysis target shifted to a different module, or a subagent returned results.
4. Drop stale hypotheses, stale logs, and unused files from the active set.
5. If the session becomes noisy, restart from the compressed summary instead of carrying everything forward.
6. Rehydrate only the evidence needed for the next decision.

# Input Contract

Provide:

- the current objective
- the active file or module set
- the current evidence
- any history that is truly required

Optional but helpful:

- the last known good summary
- known dead ends to avoid

# Output Contract

Return:

- the current compressed state (using the standard summary template)
- the active working set, classified as:
  - **Live**: directly needed for the next step.
  - **Deferred**: may matter in a later phase but does not block the current step.
  - **Discarded**: investigated and found irrelevant, or superseded by newer evidence.
- the next focused step

# Guardrails

- Do not keep huge logs or long file excerpts in active memory when a short summary is enough.
- Do not re-read the same large file unless a new question requires it.
- Drop any hypothesis that has no supporting evidence after the most recent investigation pass.
- If starting fresh would improve clarity, say so explicitly.
- The compressed summary must include: the current symptom or objective, the confirmed scope, what has been ruled out, and the next intended step.

# Common Anti-Patterns

- **Carrying the entire session history.** The agent re-reads rejected hypotheses, old terminal output, and abandoned file paths into every subsequent step instead of compressing state after each milestone.
- **Re-reading the same 500-line file for the fourth time.** The agent keeps loading the same large file without a new question driving the re-read, consuming context budget on information that should have been summarized after the first pass.

# Composition

Combine with:

- `read-and-locate` to keep discovery tight in unfamiliar codebases
- `bugfix-workflow` when diagnosis is spreading across too many hypotheses
- `plan-before-action` to keep the next step explicit after compression
- `multi-agent-protocol` when multiple parallel findings need a compact merge state

# Example

Task: "Debug an intermittent worker failure after a long session."

Compressed state (standard summary template):

- Symptom / Objective: worker fails only on retry path.
- Confirmed scope: retry scheduler, payload serializer, retry test fixture.
- Ruled out: queue connection, credential loading.
- Next step: inspect serializer differences between initial and retry enqueue.

Do not carry the full terminal history, every rejected hypothesis, and every unrelated worker module into the next pass.
