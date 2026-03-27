---
name: scoped-tasking
version: 0.1.0
description: Narrow the task to the smallest useful analysis and edit boundary before exploring, editing, or validating.
tags: [coding, agents, orchestration, efficiency]
---

# Purpose

Force the agent to define the minimum useful task boundary before doing work. The goal is to reduce irrelevant reading, avoid repo-wide drift, and keep the working set small enough to reason about clearly.

# When to Use

- At the start of almost any coding task.
- When the request is broad but the likely edit surface is small.
- Before repository exploration, editing, or validation.
- When a task is expanding faster than evidence justifies.

# When Not to Use

- When the user explicitly asks for a repo-wide audit or broad survey.
- When the task is truly global by nature, such as a deliberate API rename across many packages.
- When the scope is already tightly specified and no ambiguity remains.

# Core Rules

- Do not scan the whole repository by default.
- Define the minimum useful analysis boundary first: likely files, modules, call path, and validation surface.
- Start from the most direct clues available: user-provided file paths, stack traces, failing tests, logs, commands, or symbols.
- Focus only on directly relevant files and modules.
- Expand scope only when the current boundary cannot explain the problem or support the next step.
- Each scope expansion must state why the old boundary was insufficient.
- Keep a clear distinction between in-scope items and merely possible leads.

# Execution Pattern

1. Restate the objective in one sentence.
2. Propose the initial boundary: files, modules, interfaces, and validation surface.
3. Inspect only that boundary.
4. If evidence is missing, expand one layer outward and explain why.
5. Stop expanding once there is enough evidence to answer, edit, or validate.
6. Before editing, restate the final working set.

# Input Contract

Provide:

- the task objective
- any starting clues
- known constraints or non-goals
- whether the task is analysis-only or edit-capable

Optional but helpful:

- likely entry points
- recent failures
- affected commands or endpoints

# Output Contract

Return:

- the objective
- the current analysis boundary
- explicitly excluded areas
- any scope expansion and its justification
- the next action inside the chosen boundary

# Guardrails

- Avoid broad repository exploration as a reflex.
- Avoid reading large files end-to-end when a smaller entry point is available.
- Avoid mixing search, diagnosis, design, refactor, and validation across unrelated areas.
- If several leads exist, rank them and inspect one at a time.
- If the task turns out to be global, make that conclusion explicit rather than drifting into it silently.

# Composition 

Combine with:

- `plan-before-action` to convert the scoped boundary into a concrete work plan
- `read-and-locate` when the edit point is not known yet
- `minimal-change-strategy` once an edit path is clear
- `targeted-validation` to keep verification aligned to the same boundary

# Example

Task: "Fix the timeout regression in invoice export."

Apply this skill by starting with the smallest plausible boundary:

- `invoice_export_controller`
- export service
- the failing export test or command

Do not scan every reporting module. If the service delegates to a shared query builder and the evidence shows the delay comes from there, expand scope to the query builder and explain that the original boundary could not account for query generation time.
