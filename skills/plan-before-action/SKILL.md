---
name: plan-before-action
description: Require a clear plan before multi-step or uncertain edits. Use when (1) user says "not sure", "don't know", or "uncertain" about file locations or structure, (2) 3+ files involved with unclear sequencing, (3) task mentions multiple areas that need coordination. Always trigger when uncertainty keywords present.
metadata:
  version: "0.2.0"
  tags: "coding, agents, planning"
---

# plan-before-action

Use this skill to pause long enough to make the next edit sequence explicit.

## Use When

- The task touches 3 or more files.
- The edit order matters.
- The user or agent is uncertain about file locations, ownership, or acceptance criteria.
- A proposed change affects tests, docs, and implementation together.

## Skip When

- The request is a direct answer, status check, or one-command task.
- The exact single-file edit is already known and low risk.

## Required Plan

Before editing, state:

- scope: the smallest boundary that satisfies the request
- assumptions: facts being relied on before execution
- files: intended files or directories to inspect or edit
- sequence: the next 2-5 actions in order
- validation: the narrowest useful check after the change

## Rules

- Keep the plan shorter than the implementation unless the work is inherently large.
- Ask a focused question when scope or acceptance criteria are not actionable.
- Update the plan only when new evidence changes the path.
- Start implementation once the plan is specific enough to execute.

## Output

`[output: plan-before-action | completed <confidence> | scope:"..." files:"..." sequence:"..." validation:"..." | next:<skill-or-action>]`
