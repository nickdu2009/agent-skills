---
name: read-and-locate
version: 0.1.0
description: Find the relevant files, code paths, and edit points in an unfamiliar area of the codebase without broad exploration. Use when the agent does not yet know where the change should happen.
tags: [coding, agents, orchestration, efficiency]
---

# Purpose

Teach the agent to understand only the amount of code needed to move the task forward. The skill emphasizes narrow discovery, explicit evidence, and early stopping once the likely edit surface is known.

# When to Use

- When the codebase is unfamiliar.
- When the relevant file or module is not known yet.
- When the agent needs to trace a call path, data path, or ownership boundary.
- Before a bugfix or small feature change in an unfamiliar area.

# When Not to Use

- When the exact edit file is already known.
- When the user asks for a broad architectural survey.
- When the task is analysis of one already-open file with no discovery needed.

# Core Rules

- Start from the most relevant entry points.
- Prefer narrow discovery over broad repository exploration.
- Identify likely files, modules, call paths, and boundaries first.
- Stop exploring once enough evidence is gathered for the next step.
- Distinguish confirmed locations from tentative leads.
- Do not treat every interesting file as part of the required working set.

# Execution Pattern

1. Start from the strongest clue: endpoint, command, stack trace, test, symbol, or file path.
2. Identify the first likely entry point.
   - Runtime path: follow function calls and control flow.
   - Data path: follow data transformations and storage boundaries.
   - Ownership path: follow module boundaries and responsibility seams.
   - Configuration path: follow config loading, overrides, and environment resolution.
3. Trace only the adjacent call path or ownership path.
4. Mark each discovered file as confirmed location or tentative lead.
5. Stop once the likely edit points and validation surface are clear.
6. Hand off to planning or editing without continuing to browse for curiosity.

# Input Contract

Provide:

- the objective
- the strongest available clue
- the kind of path to trace: runtime, data, ownership, or configuration

Optional but helpful:

- suspected modules
- recent failing commands

# Output Contract

Return:

- confirmed locations
- tentative leads
- likely edit points
- relevant boundaries or ownership seams
- what remains unknown but does not block the next step

# Guardrails

- Do not start with repo-wide reading.
- Do not read entire directories when one or two files can establish the path.
- Do not keep exploring after the next action is already clear.
- Do not present tentative leads as confirmed facts.
- If the first clue is weak, say so and choose the narrowest next-best clue.

# Composition

Combine with:

- `scoped-tasking` to define the discovery boundary
- `plan-before-action` once likely edit points are identified
- `context-budget-awareness` to avoid carrying every discovered branch forward
- `bugfix-workflow` when the discovery goal is to isolate the fault domain

# Example

Task: "Add an audit field to generated invoices."

A good discovery sequence is:

- start from the invoice generation command or endpoint
- locate the service that builds invoice payloads
- identify the serializer or template boundary
- confirm where persistence happens

Stop once the generation path and serialization boundary are clear. Do not survey every billing file just because they look related.
