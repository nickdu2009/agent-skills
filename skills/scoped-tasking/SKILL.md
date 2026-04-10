---
name: scoped-tasking
description: Narrow a broad or ambiguous task to the smallest useful boundary before exploring or editing. Use when the request is wide but the likely edit surface is small, or when scope is expanding without evidence.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Force the agent to define the minimum useful task boundary before doing work. The goal is to reduce irrelevant reading, avoid repo-wide drift, and keep the working set small enough to reason about clearly.

# When to Use

- When the request is broad or ambiguous but the likely edit surface is small.
- When multiple modules, files, or systems are mentioned but the real change target is unclear.
- When a task is expanding faster than evidence justifies.
- When the agent is about to explore the repository without a clear starting point.
- When the task description is vague or ambiguous and needs clarification before scoping can begin.

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

0. Check requirement clarity before scoping.
   - If the task description includes specific file names, function names, or error messages — skip to step 1.
   - If the task description is under 2 sentences and has 3 or more possible interpretations — trigger clarification.
   - If the task involves multiple stakeholders with potentially different requirements — trigger clarification.
   - If the user explicitly says "help me understand the requirements first" — trigger clarification.
   - Clarification action: list confirmation questions ("My understanding is X — is that correct?"), distinguish must-have from nice-to-have, and establish acceptance criteria before proceeding to step 1.
1. Restate the objective in one sentence.
2. Propose the initial boundary: files, modules, interfaces, and validation surface.
3. Inspect only that boundary.
4. If evidence is missing, expand one layer outward and explain why.
5. Stop expanding when: (a) the next action is clear from current evidence, (b) the last expansion produced no new relevant evidence, or (c) the working set already covers the known call path end-to-end.
6. Before editing, restate the final working set.

If the task is analysis-only, the boundary is the answer surface. If the task is edit-capable, the boundary must also include the validation surface.

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

# Common Anti-Patterns

- **Grepping the entire repo before reading the error message.** The agent runs broad searches across every directory instead of starting from the user-provided clue. This wastes context and delays the first useful finding.
- **Silent scope creep.** The agent discovers a related issue in a neighboring module and begins investigating it without stating that the original boundary was insufficient. The scope expands without an explicit expansion decision.

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
