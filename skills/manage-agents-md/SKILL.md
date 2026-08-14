---
name: manage-agents-md
description: Initialize and update project-level AGENTS.md guidance for coding agents. Use when the user asks to create, bootstrap, refresh, audit, or update a repository's AGENTS.md, agent instructions, AI coding rules, or project governance content.
metadata:
  version: "0.1.0"
  tags: "coding, agents, documentation, governance"
---
# manage-agents-md

Use this skill to create or maintain a project's `AGENTS.md` without overwriting useful local guidance.

## Goal

Produce concise, durable, repository-specific agent instructions that help future agents work safely in the project.

The result should be useful on the next task, not just accurate for the current chat.

## When to Use

- The user asks to initialize, create, generate, or bootstrap `AGENTS.md` for a project.
- The user asks to update, refresh, clean up, or reconcile existing agent instructions.
- The user mentions project AI rules, coding agent guidance, governance content, or repository instructions.
- A project has stale or conflicting agent instruction files and the user asks to fix them.

## When Not to Use

- The user asks to change a runtime's settings, discovery paths, or user-level rules; use that runtime's documented workflow instead.
- The user asks to create a new reusable skill; use the skill authoring workflow instead.
- The user asks to implement product code and `AGENTS.md` is only background context.
- The target is a requirements, design, implementation plan, code, or test review artifact; use the matching review-loop skill.

## Core Rules

- Preserve project-specific guidance unless there is clear evidence it is wrong or obsolete.
- Do not overwrite an existing `AGENTS.md` wholesale when a smaller merge is enough.
- Keep instructions durable: avoid task-specific notes, temporary plans, chat summaries, and time-sensitive claims.
- Base commands, paths, and conventions on repository evidence, not guesses.
- Prefer the nearest applicable `AGENTS.md` when nested instruction files exist.
- Do not include secrets, private tokens, machine-local paths, or credentials.
- Keep this skill scoped to the requested project-level `AGENTS.md`; do not create runtime-specific companion files.

## Workflow

1. Confirm the target.
   - Identify the repository root and whether the user wants root-level `AGENTS.md` only.
   - If the target path or nested scope is ambiguous, ask before editing.

2. Read current instruction sources.
   - Existing `AGENTS.md` files from the target directory upward.
   - Related repository files such as README, contributor docs, package manifests, build files, CI, and test configuration.
   - Any user-provided exact wording; preserve exact wording when requested.

3. Classify the operation.
   - **Initialize**: no suitable `AGENTS.md` exists at the target level.
   - **Update**: an existing `AGENTS.md` exists and needs changes.
   - **Reconcile**: multiple instruction sources conflict or duplicate each other.

4. Draft from evidence.
   - Include project purpose only if it is clear from existing docs.
   - Include setup, build, test, lint, and formatting commands only when found in the repo or docs.
   - Include repository-specific safety rules, generated-file rules, naming conventions, or validation requirements.
   - Add repository-signal best practices only when the signal is present and relevant.
   - Include skill/tool routing only when the project actually depends on those workflows.

5. Merge carefully.
   - Keep stable local rules.
   - Do not duplicate an applicable parent or existing project section; add only the missing project-specific guidance.
   - Remove duplicate or obsolete rules only when the replacement is clearly better supported.
   - Resolve contradictions by favoring current repository files over stale prose, and call out any unresolved conflict.
   - Keep sections short enough that future agents will read them.

6. Validate the result.
   - Check that referenced files, directories, and commands exist or are explicitly marked as assumptions.
   - Check that Markdown headings and code fences are valid.
   - Confirm no secrets or user-private machine details were added.
   - For documentation-only changes, validation can be a focused file review instead of running project tests.

## Initialization Reference

For a new root `AGENTS.md`, read [INITIALIZATION.md](INITIALIZATION.md) and use its checklist, repository-signal guidance, and template. Do not read it for ordinary update or reconcile work unless the current file lacks a usable structure or the user asks to enrich project best practices.

## Output Contract

Report:

- operation: `initialized`, `updated`, or `reconciled`
- path: changed `AGENTS.md` path
- preserved: important existing rules kept
- changed: concise summary of updates
- validation: checks performed
- residual_assumptions: any unverified commands, paths, or conventions

Finish with:

`[output: manage-agents-md | completed <confidence> | operation:"initialized|updated|reconciled" path:"..." validation:"..." assumptions:"..." | next:<action>]`

## Contract

### Preconditions

- The user wants to create or update project-level agent instructions.
- The target repository or target `AGENTS.md` path is known, or can be clarified before editing.
- Repository evidence is available for at least the commands, paths, or rules being added.

### Postconditions

- `status: completed` includes `operation`, `path`, `validation`, and `residual_assumptions`.
- The resulting `AGENTS.md` is concise, durable, and project-specific.
- Existing local guidance is preserved unless a documented replacement was applied.

### Invariants

- Project facts come from repository evidence or explicit user instructions.
- Documentation-only edits do not trigger expensive validation by default.
- Unverified commands or paths are reported as assumptions instead of stated as fact.

### Downstream Signals

- `operation` tells downstream work whether instructions were initialized, updated, or reconciled.
- `residual_assumptions` identifies any project facts future agents should verify before relying on them.

## Failure Handling

### Common Failure Causes

- The target project or desired instruction scope is unclear.
- Existing instruction files contradict each other without enough evidence to resolve the conflict.
- The repository does not expose reliable build, test, or formatting commands.

### Retry Policy

- Ask one focused clarification question when target path, nested scope, or conflict resolution is unclear.
- If repository evidence is missing after a focused search, leave the item out or mark it as an assumption.

### Fallback

- Produce a minimal `AGENTS.md` with only confirmed project facts.
- Report unresolved conflicts instead of guessing.

### Low Confidence Handling

- Prefer a smaller file with fewer claims.
- Mark the update as provisional and list exactly what needs confirmation.

## Output Example

```
[output: manage-agents-md | completed high | operation:"updated" path:"AGENTS.md" validation:"reviewed referenced commands and paths" assumptions:"none" | next:done]
```

## Deactivation Trigger

- Deactivate when the requested `AGENTS.md` initialization or update is complete.
- Deactivate if the task changes from agent-instruction maintenance to product implementation.
- Deactivate if the user chooses a different artifact type that belongs to a review-loop skill.

## Constraints

- Do not create broad governance systems unless the user asked for them.
- Do not copy large generic policy blocks into a small project.
- Do not silently delete local rules because they look unusual.
- Do not make the file a changelog for agent behavior.
- Do not run expensive project validation for a documentation-only edit unless the repository requires it.
