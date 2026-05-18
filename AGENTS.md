# AGENTS.md

## Multi-Agent Rules

Full protocol: `multi-agent-protocol` skill.

**Tier 1 (read-only):** Launch read-only subagents anytime. Subagents return structured results; the primary agent synthesizes.

**Tier 2 (write-capable):** Before launching write-capable subagents, emit: `[delegate: <count 2-4> | split:<dimension> | risk:<low|medium|high>]`. If not cleanly splittable: `[delegate: 0 | reason:<why>]`.

**Overflow:** If the task requires more than 4 parallel subagents, use `phase-plan` to break work into sequential waves.

## Skill Activation

Task-type activation: `bugfix-workflow`, `safe-refactor`, `scoped-tasking`, `plan-before-action`, `design-before-plan`, `impact-analysis`, `self-review`, and `targeted-validation` activate when task shape requires their guidance.

Mid-task escalation:

- `design-before-plan`: multiple approaches, public API or cross-module contract changes, or unclear acceptance criteria.
- `impact-analysis`: shared interfaces, public APIs, shared data models, or broad caller impact.
- `self-review`: multi-file edits complete or user requests diff review.
- `targeted-validation`: validation choice is non-obvious or expensive.
- `phase-plan`: work exceeds a single reviewable implementation or needs wave-level coordination.
- `phase-execute`: accepted phase plan is ready for wave implementation.
- `phase-contract-tools`: maintaining phase contract scripts, schemas, or renderers.

## Skill Lifecycle

Load the smallest set that fits the task. Drop a skill when its deliverable is complete. Re-evaluate when the task phase changes. Keep at most 4 active skills unless a handoff transition requires a brief overlap.

## Common Flow Patterns

```text
Bug fix:      scoped-tasking -> bugfix-workflow -> self-review -> targeted-validation
Refactor:     scoped-tasking -> safe-refactor -> self-review -> targeted-validation
Multi-file:   scoped-tasking -> plan-before-action -> self-review -> targeted-validation
Design-first: scoped-tasking -> design-before-plan -> impact-analysis -> plan-before-action
Parallel:     multi-agent-protocol -> synthesis
Phase work:   phase-plan -> phase-execute -> phase-contract-tools
```

## Skill Protocol v2

Use compact inline blocks when skill-driven execution needs visible traceability:

1. `[task-validation: ...]`
2. `[triggers: ...]`
3. `[precheck: <skill> | ...]`
4. `[output: <skill> | ...]`
5. `[validate: <skill> | ...]`
6. `[drop: <skill> | ...]`

Every `[output]` needs matching `[validate]`; every triggered skill must eventually be dropped.

## Change Rules

- Default to the smallest necessary change.
- Do not do unrelated cleanup or opportunistic refactors.
- Change public contracts only when required.
- Never overwrite unrelated user changes.
- When renaming or deleting a skill directory, also remove its stale copy under `.cursor/skills/<old-name>/` and `.claude/skills/<old-name>/`, then `git add -f` the new paths and verify with `ls .cursor/skills/ .claude/skills/`. IDE caches otherwise reverse-sync the old directory and silently roll back the change.

## Validation Rules

Start with the smallest sufficient validation. State residual risk for anything unvalidated. When testing skills, use a temporary project and `manage-governance.py --project <temp-dir>`.
