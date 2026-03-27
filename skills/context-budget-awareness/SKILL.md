---
name: context-budget-awareness
version: 0.1.0
description: Keep the active context small, current, and aligned to the objective by trimming noise and compressing state.
tags: [coding, agents, orchestration, efficiency]
---

# Purpose

Teach the agent to control context growth. The skill helps avoid bloated sessions, repeated reading, and irrelevant history so that current reasoning stays attached to the live objective instead of accumulated noise.

# When to Use

- In long debugging or refactoring sessions.
- When the active file set keeps growing.
- When logs, policies, or previous attempts are dominating the session.
- When a fresh focused pass may be cheaper than carrying the current context forward.

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
3. After each milestone, compress the state into a short working summary.
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

- the current compressed state
- the active working set
- deferred context that may matter later
- stale context that should no longer drive decisions
- the next focused step

# Guardrails

- Do not keep huge logs or long file excerpts in active memory when a short summary is enough.
- Do not re-read the same large file unless a new question requires it.
- Do not let earlier hypotheses survive without evidence.
- If starting fresh would improve clarity, say so explicitly.
- Compression must preserve decision-relevant facts, not just shorten text.

# Composition

Combine with:

- `read-and-locate` to keep discovery tight in unfamiliar codebases
- `bugfix-workflow` when diagnosis is spreading across too many hypotheses
- `plan-before-action` to keep the next step explicit after compression
- `multi-agent-protocol` when multiple parallel findings need a compact merge state

# Example

Task: "Debug an intermittent worker failure after a long session."

Compressed state:

- Symptom: worker fails only on retry path.
- Confirmed scope: retry scheduler, payload serializer, retry test fixture.
- Ruled out: queue connection, credential loading.
- Next step: inspect serializer differences between initial and retry enqueue.

Do not carry the full terminal history, every rejected hypothesis, and every unrelated worker module into the next pass.
