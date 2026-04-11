---
name: plan-before-action
description: Require a clear plan before multi-step or uncertain edits. Use when (1) user says "not sure", "don't know", or "uncertain" about file locations or structure, (2) 3+ files involved with unclear sequencing, (3) task mentions multiple areas that need coordination. Always trigger when uncertainty keywords present.
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
- If the plan involves adding or upgrading dependencies, note the dependency change in the plan and recommend running the project's dependency audit tool (npm audit / pip-audit / cargo audit or equivalent).
- If a lock file shows large-scale changes, flag it in the plan and assess the impact before proceeding.
- Do not silently introduce new dependencies during implementation — all new dependencies must be declared in the plan.

# Common Anti-Patterns

- **Editing while still discovering.** Starts modifying file before confirming full set of files that need change, backtracks when dependency surfaces. Plan was never stated.
- **Vague progress reporting.** Says "making progress" or "almost done" instead of reporting concrete done/not done/next items. Hides whether plan is still on track.

See skill-anti-pattern-template.md for format guidelines.

# Composition

Core component of multiple chains: `multi-file-planned`, `design-first`, and `large-task` (see CLAUDE.md § Skill Chain Triggers).

Standard forward flow: receives scoped boundary from `scoped-tasking` or edit points from `read-and-locate`, produces plan, hands to `minimal-change-strategy` → `self-review` → `targeted-validation`.

Additional compositions:

- `multi-agent-protocol` when the plan includes parallel analysis
- `incremental-delivery` when the plan spans 2-4 independently mergeable PRs

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

## Contract

### Preconditions

- Task needs multi-step execution, multiple files, or explicit sequencing; enough evidence to name working set and next action; edits allowed now or plan produced for later execution. See skill-contract-template.md § Preconditions for standard definitions.

### Postconditions

- `status: completed` includes `assumptions`, `working_set`, `sequence`, `validation_boundary`.
- Plan names intended files/modules before implementation starts; progress reportable as done/not done/next without reopening discovery.

### Invariants

- Execution doesn't begin while working set is fuzzy; only one coherent objective active at a time; new dependencies/irreversible operations surfaced in plan vs. introduced silently.

### Downstream Signals

- `assumptions`: what must be rechecked
- `working_set`: approved edit surface
- `sequence`: execution order for edits and validation
- `validation_boundary`: first targeted check after patch

## Failure Handling

### Common Failure Causes

- Discovery is incomplete, so the intended file list is still unstable.
- Hidden assumptions change the task shape mid-plan.
- The task combines unrelated objectives that should be split first.

### Retry Policy

- Allow one re-plan when new evidence invalidates a stated assumption.
- If the working set remains unstable after the second pass, stop and return to discovery or scoping.

### Fallback

- Return to `scoped-tasking` or `read-and-locate` when the edit surface is still uncertain.
- Hand off to `design-before-plan` when design choices, not execution order, are the real blocker.
- Escalate to the user when plan alternatives require product or policy decisions.

### Low Confidence Handling

- Mark uncertain steps as assumptions and keep the first edit narrow.
- Require downstream execution to restate any unresolved assumption before editing.

## Output Example

```yaml
[skill-output: plan-before-action]
status: completed
confidence: high
outputs:
  assumptions:
    - "Only the payment client wrapper is affected."
  working_set:
    - "payment_client.py"
    - "payment_client_test.py"
  sequence:
    - "add bounded retry logic"
    - "update focused tests"
    - "run targeted validation"
  validation_boundary:
    - "payment client unit tests"
signals:
  execution_ready: true
recommendations:
  next_step: "patch the client wrapper before touching broader payment flows"
[/skill-output]
```

## Deactivation Trigger

- Deactivate once execution starts and no re-planning is required.
- Deactivate when a new assumption failure forces the task back into scoping or design.
- Deactivate after the plan has been consumed by downstream implementation and validation work.
