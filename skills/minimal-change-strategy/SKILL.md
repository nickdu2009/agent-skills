---
name: minimal-change-strategy
description: Constrain a code change to the smallest viable patch when the diff is growing beyond the task, cleanup temptation is high, choosing between competing implementation approaches, or multiple edit strategies compete. Use when user requests minimal change, operation is irreversible, or surrounding code tempts drive-by fixes. Not needed for simple single-file fixes where CLAUDE.md Change Rules suffice.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Keep edits small, local, and reviewable. The skill favors the narrowest patch that solves the stated problem while preserving existing interfaces and behavior unless change is explicitly required.

# When to Use

- When surrounding code looks messy and the agent is tempted to clean up beyond the task.
- When multiple edit strategies exist and the smallest one needs to be deliberately chosen.
- When existing code is imperfect but functional outside the requested change.
- When the diff is growing beyond what the task strictly requires.

# When Not to Use

- When the user explicitly asks for a broader redesign or refactor.
- When the current structure cannot support the required behavior safely.
- When preserving the current interface would itself be the bug.

# Core Rules

- Prefer local patches over broad rewrites.
- Avoid opportunistic cleanup unless it is necessary for the requested change.
- Avoid cosmetic rewrites that change shape without changing value.
- Avoid unrelated renaming.
- Preserve existing interfaces and behavior unless change is required.
- Do not mix bugfixes with refactors unless explicitly requested.
- Stop once the task is solved; do not continue editing because more cleanup looks possible.

# Execution Pattern

1. Define the required behavior change or defect correction.
2. Identify the narrowest edit point that can produce that outcome.
3. Compare options and choose the one that touches the fewest files, changes the fewest interfaces, and affects the fewest downstream consumers.
3.5. Assess reversibility.
   - Code logic only (function bodies, control flow, local variables) → git revert is sufficient, proceed to step 4
   - If change involves DB schema, external APIs, file deletions, or permission changes → state rollback strategy and request confirmation
   - Rollback strategy must answer: Is git revert sufficient? Is data migration rollback needed? How are external side effects handled?
4. Make the patch without broad restructuring.
5. Validate only the affected area first.
6. Record any intentional non-fixes that were observed but deferred.

# Input Contract

Provide:

- the desired outcome
- the current behavior
- compatibility constraints
- any explicit permission for refactoring or cleanup

Optional but helpful:

- examples of acceptable unchanged behavior
- rollback sensitivity

# Output Contract

Return:

- the chosen edit boundary
- the rationale for why it is the smallest viable change
- any preserved interfaces or behaviors
- any deferred cleanup or follow-up work
- the narrow validation plan

# Guardrails

- Do not widen the patch only because related code looks inconsistent.
- Do not normalize style across untouched files.
- Do not rename symbols unless the rename is part of the required fix.
- If the smallest patch is unsafe or too brittle, state why and escalate deliberately to a slightly larger change.
- Keep diffs easy to review and easy to revert.
- For irreversible operations (database schema, external APIs, file deletions, permission changes), state a rollback strategy before editing.
- Do not assume all changes can be undone with git revert — changes with external side effects need an explicit rollback plan.

# Common Anti-Patterns

- **"While I'm here" cleanup.** The agent fixes the reported bug in one line, then reformats the surrounding function, renames a variable, and reorders imports — tripling the diff for no task-related reason.
- **Rewriting instead of patching.** The agent replaces an entire function or class to fix a single branch condition. This makes the change harder to review and riskier to revert.

See skill-anti-pattern-template.md for format guidelines.

# Composition

Part of `bugfix-standard`, `refactor-safe`, `multi-file-planned`, and `design-first` chains. See the project governance file § Skill Chain Triggers.

# Example

Task: "Return `404` instead of `500` when an optional profile is missing."

Prefer:

- adding a guard in the request handler or service method that already owns the lookup

Avoid:

- renaming the entire profile API
- rewriting the exception hierarchy
- reformatting the surrounding file
- bundling unrelated error-handling cleanup into the same change

## Contract

### Preconditions

- Behavior change or defect correction is known.
- Multiple edit options exist or diff is drifting beyond task scope.
- Compatibility boundaries are known or nameable.

### Postconditions

- `status: completed` includes `change_boundary`, `scope_guardrails`, `stop_conditions`.
- States which interfaces or behaviors are intentionally preserved.
- Deferred cleanup is recorded explicitly rather than silently bundled.

### Invariants

- Chosen patch remains smallest safe option.
- Unrelated cleanup, renaming, or style changes stay out of scope.
- Reversibility and rollback sensitivity are considered before irreversible changes.

### Downstream Signals

- `change_boundary` defines where edits may occur.
- `scope_guardrails` constrain follow-on edits and reviews.
- `stop_conditions` specify when to stop editing versus continuing cleanup.

## Failure Handling

### Common Failure Causes

- The smallest local patch is too brittle or unsafe to preserve behavior.
- Hidden compatibility constraints make the minimal edit unclear.
- The user request implicitly requires a larger redesign than the current boundary allows.

### Retry Policy

- Allow one boundary revision when new evidence proves the smallest patch unsafe.
- Do not iterate endlessly on cosmetic reshaping; after one revision, either commit to the slightly larger safe change or escalate.

### Fallback

- Escalate to `design-before-plan` if preserving the current interface may itself be wrong.
- Combine with `impact-analysis` when a supposedly local change affects multiple callers or contracts.
- Ask the user for confirmation when rollback requires more than a simple revert.

### Low Confidence Handling

- State the preserved interfaces as assumptions, not guarantees.
- Require downstream validation to target the riskiest preserved behavior first.

## Output Example

```yaml
[skill-output: minimal-change-strategy]
status: completed
confidence: high
outputs:
  change_boundary:
    - "request handler null-check branch"
  scope_guardrails:
    - "do not rename helpers"
    - "do not reformat unrelated imports"
  stop_conditions:
    - "stop after the 404 behavior and focused validation both pass"
signals:
  preserved_interfaces:
    - "handler signature"
    - "existing exception hierarchy"
recommendations:
  validation_focus: "profile-missing request path"
[/skill-output]
```

## Deactivation Trigger

- Deactivate when the patch has been applied and the guarded boundary is no longer needed.
- Deactivate when the task escalates into a larger design or impact-analysis exercise.
- Deactivate after validation confirms the requested outcome without needing further scope restraint.
