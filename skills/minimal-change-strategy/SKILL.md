---
name: minimal-change-strategy
description: Constrain a code change to the smallest viable patch when the diff is growing beyond the task, cleanup temptation is high, or multiple edit strategies compete. Not needed for simple single-file fixes where AGENTS.md Change Rules suffice.
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
   - If the change only involves code logic (function bodies, control flow, local variables) — git revert is sufficient, proceed to step 4.
   - If the change involves any of the following, state a rollback strategy and request confirmation before proceeding:
     - database schema or persistent storage format changes
     - external API calls or webhook registrations
     - file or directory deletions or renames
     - permission, authentication, or encryption configuration changes
   - The rollback strategy must answer: Is git revert sufficient? Is a data migration rollback needed? How are already-triggered external side effects handled?
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
- **Rewriting instead of patching.** The agent replaces an entire function or class to fix a single branch condition, making the change harder to review and riskier to revert.

# Composition

Combine with:

- `scoped-tasking` to keep the patch boundary honest
- `plan-before-action` to declare intended edits before changing files
- `targeted-validation` to verify the patch without paying full-suite cost
- `bugfix-workflow` when the minimal fix depends on evidence from diagnosis

# Example

Task: "Return `404` instead of `500` when an optional profile is missing."

Prefer:

- adding a guard in the request handler or service method that already owns the lookup

Avoid:

- renaming the entire profile API
- rewriting the exception hierarchy
- reformatting the surrounding file
- bundling unrelated error-handling cleanup into the same change
