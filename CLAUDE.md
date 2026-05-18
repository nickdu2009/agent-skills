# AGENTS.md

## Multi-Agent Rules

Full protocol: `multi-agent-protocol` skill.

**Tier 1 (read-only):** Launch read-only subagents anytime. Subagents return structured results; the primary agent synthesizes.

**Tier 2 (write-capable):** Before launching write-capable subagents, emit: `[delegate: <count 2-4> | split:<dimension> | risk:<low|medium|high>]`. If not cleanly splittable: `[delegate: 0 | reason:<why>]`.

**Overflow:** If the task requires more than 4 parallel subagents, split the work into sequential rounds instead of launching all lanes at once.

## Skill Activation

Task-type activation: `bugfix-workflow`, `safe-refactor`, `scoped-tasking`, `plan-before-action`, `design-before-plan`, `impact-analysis`, `self-review`, and `targeted-validation` activate when task shape requires their guidance.

Mid-task escalation:

- `design-before-plan`: multiple approaches, public API or cross-module contract changes, or unclear acceptance criteria.
- `impact-analysis`: shared interfaces, public APIs, shared data models, or broad caller impact.
- `self-review`: multi-file edits complete or user requests diff review.
- `targeted-validation`: validation choice is non-obvious or expensive.

Review-loop activation (pick by artifact type, mutually exclusive):

- `requirements-review-loop`: user asks to review/validate/finalize requirements, PRD, user stories, or acceptance criteria.
- `design-review-loop`: user asks to review design docs / RFC / ADR / interface design / data model / 方案 / 实现思路 / 实现方案 / 接口 / 思路.
- `plan-review-loop`: user asks to review implementation plans / migration plans / 实施方案 / 迁移方案 / refactor plans / roadmaps.
- `code-review-loop`: user asks to review a diff / commit / PR / specified files of already-implemented code.
- `test-review-loop`: user asks to review test cases / test strategy / coverage / 测试用例本身 (not the production code under test).

## Skill Lifecycle

Load the smallest set that fits the task. Drop a skill when its deliverable is complete. Re-evaluate when the task phase changes. Keep at most 4 active skills unless a handoff transition requires a brief overlap.

## Common Flow Patterns

```text
Bug fix:      scoped-tasking -> bugfix-workflow -> self-review -> targeted-validation
Refactor:     scoped-tasking -> safe-refactor -> self-review -> targeted-validation
Multi-file:   scoped-tasking -> plan-before-action -> self-review -> targeted-validation
Design-first: scoped-tasking -> design-before-plan -> impact-analysis -> plan-before-action
Parallel:     multi-agent-protocol -> synthesis
Review loop:  pick one of requirements-review-loop / design-review-loop / plan-review-loop / code-review-loop / test-review-loop -> revise -> re-review until review_result: clean
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

## Validation Rules

Start with the smallest sufficient validation. State residual risk for anything unvalidated. When testing skills, use a temporary project and `manage-governance.py --project <temp-dir>`.
