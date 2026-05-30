<!-- Governance mirror: keep in sync with CLAUDE-template.md (identical content, different header) -->

# AGENTS.md

## Behavioral Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. These supplement skills with general dispositions. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Change public contracts only when required.
- Never overwrite unrelated user changes.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

Before substantial or multi-step implementation, state a brief plan that starts by deciding whether parallel work is justified. Built-in planning tools and modes count as planning: when Codex or Cursor asks for a plan, include this block at the top of the plan body before numbered steps.

```text
[parallelism:
- independent lanes: <parallel work, or none>
- sequential blockers: <must happen first>
- shared write surfaces: <single-owner files/modules>
- delegation: <delegate count, or 0 with reason>
]

1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Continue without an extra user confirmation when the next step is local, non-destructive, and already implied by the current task or accepted plan (for example: read-only exploration, scoped edits, self-review, or local validation).

Stop and ask when the next step would change requirements, public interfaces, cross-module contracts, persistence schema, dependencies or tooling, bulk file layout, or any remote or destructive operation.

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## Scope & Ownership

Assume the working tree may contain user changes. Preserve unrelated edits, and call out conflicts instead of overwriting them.

## Validation Rules

Start with the smallest sufficient validation. State residual risk for anything unvalidated.

- Default to local, workspace-only checks when they are sufficient to verify the change.
- Stop and ask before validations that touch external services, production-like systems, real user data, or unusually expensive/manual environments.

## Communication Rules

Report what changed, what was validated, and any residual risk. Keep status updates short and focused on new information.

## Skill Activation

Task-type activation: `bugfix-workflow`, `safe-refactor`, `scoped-tasking`, `design-before-plan`, `impact-analysis`, `self-review`, `targeted-validation`, and `manage-agents-md` activate when task shape requires their guidance.

Fast path:

- Stay in the lightest workable path when the task is read-only, single-surface, or a local implementation step whose next action is obvious and non-destructive.

Use the full workflow when:

- ordering across multiple files matters
- acceptance criteria or ownership boundaries are unclear
- public interfaces, shared contracts, persistence schema, or dependencies may change

Mid-task escalation:

- `design-before-plan`: multiple approaches, public API or cross-module contract changes, or unclear acceptance criteria.
- `impact-analysis`: shared interfaces, public APIs, shared data models, or broad caller impact.
- `self-review`: multi-file edits complete or user requests diff review.
- `targeted-validation`: validation choice is non-obvious or expensive.
- `manage-agents-md`: user asks to initialize, create, refresh, or update a project's `AGENTS.md`.

Review-loop activation (pick by artifact type, mutually exclusive):

- `requirements-review-loop`: user asks to review/validate/finalize requirements, PRD, user stories, or acceptance criteria.
- `design-review-loop`: user asks to review design docs / RFC / ADR / interface design / data model / 方案 / 实现思路 / 实现方案 / 接口 / 思路.
- `plan-review-loop`: user asks to review implementation plans / migration plans / 实施方案 / 迁移方案 / refactor plans / roadmaps.
- `code-review-loop`: user asks to review a diff / commit / PR / specified files of already-implemented code.
- `test-review-loop`: user asks to review test cases / test strategy / coverage / 测试用例本身 (not the production code under test).

Workflow routing:

- Start with `scoped-tasking` when a bug fix, refactor, multi-file change, or design/review request still needs boundary definition before execution.
- Stay on the selected implementation workflow when scope is clear and no escalation signal appears; do not trigger `design-before-plan` or `impact-analysis` by default.
- If escalation signals appear mid-task, stop the current implementation path and switch to `design-before-plan` and/or `impact-analysis` before continuing more implementation work.

## Escalation Rules

Ask for clarification when:

- acceptance criteria, ownership boundaries, or destructive actions are unclear
- a step may change public APIs, cross-module contracts, persistence schema, or migration strategy
- a step may add dependencies, change tooling/runtime, or require commit/push/deploy/release actions

Do not proceed by guessing across those boundaries.

## Skill Lifecycle

Load the smallest set that fits the task. Drop a skill when its deliverable is complete. Re-evaluate when the task phase changes. Keep at most 4 active skills unless a handoff transition requires a brief overlap.

## Skill Protocol

Use compact inline blocks when skill-driven execution needs visible traceability:

1. `[task-validation: ...]`
2. `[triggers: ...]`
3. `[precheck: <skill> | ...]`
4. `[output: <skill> | ...]`
5. `[validate: <skill> | ...]`
6. `[drop: <skill> | ...]`

Each triggered skill should produce or be summarized by an `[output]` block. The calling agent is responsible for emitting matching `[validate]` and `[drop]` blocks when validation completes or the skill is no longer active.

## Common Flow Patterns

```text
Bug fix:      scoped-tasking -> bugfix-workflow -> self-review -> targeted-validation
Refactor:     scoped-tasking -> safe-refactor -> self-review -> targeted-validation
Multi-file:   scoped-tasking -> (Behavioral Guidelines §4 plan) -> self-review -> targeted-validation
Design-first: scoped-tasking -> design-before-plan -> impact-analysis
Parallel:     multi-agent-protocol -> synthesis
Review loop:  pick one of requirements-review-loop / design-review-loop / plan-review-loop / code-review-loop / test-review-loop -> revise -> re-review until review_result: clean
```

Normal vs escalation paths:

- `Bug fix`, `Refactor`, `Multi-file`, and `Review loop` are the default execution paths when the task stays within its accepted scope.
- `Design-first` is the escalation path when the work crosses into multiple approaches, unclear acceptance criteria, public-contract changes, shared data models, or broad caller impact.

Automatic continuation:

- Continue from implementation to `self-review` and `targeted-validation` without an extra user checkpoint when the next step is local and non-destructive.
- Continue from a completed plan into implementation, `self-review`, and `targeted-validation` when the next step remains local, non-destructive, and within the accepted task boundary.
- Continue after a review loop returns `review_result: clean` when the next step is explicit, local, and non-destructive.

Stop conditions:

- Pause the current chain and ask before continuing if the work expands into public-contract changes, schema/migration work, dependency/toolchain changes, bulk file moves, or remote/destructive actions.
- Once an escalation path is triggered, stop the current implementation path and move into `design-before-plan` or `impact-analysis` before continuing more implementation work.

## Multi-Agent Rules

Full protocol: `multi-agent-protocol` skill.

**Tier 1 (read-only):** Launch read-only subagents when the user explicitly asks for parallel work or the active plan/workflow has already chosen a parallel investigation path. Subagents return structured results; the primary agent synthesizes.

**Tier 2 (write-capable):** Before launching write-capable subagents, emit: `[delegate: <count 2-4> | split:<dimension> | risk:<low|medium|high>]`. If not cleanly splittable: `[delegate: 0 | reason:<why>]`.

Delegation default:

- Parallelism is opt-in, not automatic. Use `[delegate: 0 | reason:<why>]` when lanes share write surfaces, require strict sequencing, or depend on unresolved contract decisions.

**Overflow:** If the task requires more than 4 parallel subagents, split the work into sequential rounds instead of launching all lanes at once.
