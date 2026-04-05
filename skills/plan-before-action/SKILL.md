---
name: plan-before-action
description: Require a clear plan with scope, assumptions, and intended file list before multi-step or uncertain edits. Use when multiple files are involved, sequencing matters, or the task shape is not yet clear.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Prevent impulsive editing. The skill requires the agent to converge on a short, explicit plan before making changes so that execution stays aligned with the stated goal and current evidence.

# When to Use

- When the edit involves three or more files or multiple coordinated steps.
- When the task includes uncertainty, assumptions, or sequencing risk.
- When the agent is unsure which files need to change or in what order.
- When progress reporting matters because the task is long or multi-phase.

# When Not to Use

- For purely informational questions with no code changes.
- For a tiny one-line edit where the scope and action are already fully obvious.
- When the user explicitly requests exploratory analysis before any plan is possible.

# Core Rules

- Summarize the goal before acting.
- Define the scope and assumptions explicitly.
- List intended files and actions before editing.
- Complete one clear objective at a time.
- Report progress in terms of done, not done, and next.
- If assumptions become invalid, stop and revise the plan before continuing.

# Execution Pattern

1. Restate the goal.
2. Declare the current scope.
3. List assumptions and open questions.
4. List intended files and planned actions.
5. Execute one objective.
6. Report: done, not done, next.
7. Re-plan if new evidence changes the task shape.

# Input Contract

Provide:

- the goal
- known constraints
- current evidence
- whether edits are allowed now or only after confirmation

Optional but helpful:

- acceptance criteria
- preferred validation boundary

# Output Contract

Return:

- a concise task summary
- stated assumptions
- the planned working set
- the intended sequence of actions
- progress updates using done / not done / next

# Guardrails

- Do not begin editing while the intended file list is still fuzzy.
- Do not keep multiple unrelated objectives active at once.
- Do not hide uncertainty; surface it as an assumption or open question.
- Do not let progress updates collapse into vague status language.
- Keep the plan short enough to execute, not so broad that it becomes a project document.

# Common Anti-Patterns

- **Editing while still discovering.** The agent starts modifying a file before confirming the full set of files that need to change, then backtracks when a dependency surfaces. The plan was never stated.
- **Vague progress reporting.** The agent says "making progress" or "almost done" instead of reporting concrete done / not done / next items. This hides whether the plan is still on track.

# Composition

Combine with:

- `scoped-tasking` to establish the initial boundary
- `minimal-change-strategy` to constrain the edit size
- `targeted-validation` to pre-decide how confidence will be earned
- `multi-agent-protocol` when the plan includes parallel analysis

# Example

Task: "Add a retry around one flaky upstream call."

Plan:

- Goal: add bounded retry logic for the upstream payment-status call.
- Scope: the client wrapper and the unit tests covering that call path.
- Assumptions: other upstream calls are unaffected.
- Intended files: client wrapper, retry helper if already present, related tests.
- Progress:
  - Done: mapped current call path.
  - Not done: implement retry and verify no duplicate side effects.
  - Next: patch the wrapper and run the targeted tests.
