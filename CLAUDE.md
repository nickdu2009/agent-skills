# CLAUDE.md

## Multi-Agent Rules

Multi-agent execution has two tiers. Full operational protocol is in the `multi-agent-protocol` skill.

**Tier 1 — Explore (read-only):** The agent may launch read-only subagents at any time without pre-declaration. Each subagent must return structured results; the primary agent must synthesize them.

**Tier 2 — Delegate (write-capable):** Before launching any subagent that may edit files or run mutating commands, the agent must output: `[delegate: <count 2–4> | split: <dimension> | risk: <low|medium|high>]`. If the task cannot be cleanly split, output `[delegate: 0 | reason: <why>]` and stay serial.

**Exemptions:** No declaration needed for single-file edits, direct answers, single commands, or git housekeeping.

## Skill Activation

Skills activate through two mechanisms:

- **Task-type activation**: `bugfix-workflow`, `safe-refactor`, `scoped-tasking`, `read-and-locate`, and `plan-before-action` activate based on task characteristics recognized during `[triggers]` evaluation. Their SKILL.md descriptions define when they match.
- **Mid-task escalation**: The rules below define when base-level governance rules prove insufficient and the agent should load the full skill during execution.

## Skill Boundary

`CLAUDE.md` is the governance and routing layer, not the skill manual.

**Keep here only:**

- Skill trigger/load/defer/drop rules.
- Skill chain handoffs, concurrency budgets, and protocol syntax.
- Short routing descriptions needed to decide when a skill applies.

**Do not put here:**

- A skill's internal step-by-step workflow.
- Skill-specific checklists, examples, edge-case catalogs, or output schemas that belong in `SKILL.md`.
- Long skill descriptions that duplicate or paraphrase the skill file.

**Source of truth:** Each skill's behavior, procedure, and detailed guidance live in that skill's `SKILL.md`.

## Governance Fast-Path

**No skill needed** for tasks fully handleable at the governance layer:

- **Direct answers**: Questions requiring no code exploration (concepts, prior context, definitions).
- **Single commands**: One-off shell/git commands with clear output.
- **Trivial file reads**: Read 1–2 specific files when path is known.
- **Status queries**: Git status, file existence, directory listing.
- **Single-file low-risk edits**: Typo fix, comment update, config tweak in 1 file with no caller impact.

**Skip `[task-validation]` and `[triggers]`** for fast-path tasks. Proceed directly.

## Skill Escalation

These rules define when base-level CLAUDE.md rules are insufficient and the agent should load the full skill.

- Escalate to `design-before-plan` when: the task involves choosing between multiple implementation approaches, the change introduces or modifies a public API or cross-module contract, acceptance criteria are missing or unclear, scoped-tasking identified the boundary but design decisions remain open, or impact-analysis revealed 3+ affected modules requiring contract coordination.
- Escalate to `minimal-change-strategy` when: the diff is growing beyond what the task requires, multiple edit strategies compete, or surrounding code tempts drive-by cleanup.
- Escalate to `context-budget-awareness` when: the working set exceeds 8 files, the same file has been read more than twice without a new question, more than 3 hypotheses are active without ranking evidence, or the last 3 actions did not advance the stated objective.
- Escalate to `targeted-validation` when: multiple validation options exist and the cheapest meaningful check needs deliberate selection, validation is expensive and the change is local enough for a narrower check, or a validation failure needs diagnosis before broadening coverage.
- Escalate to `impact-analysis` when: the change touches a function or interface with 3+ callers, involves a public API or shared type, modifies a data model used across multiple modules, or read-and-locate produced 3+ tentative leads.
- Escalate to `self-review` when: edits span multiple files and are complete, or the user requests a diff review before testing.
- Escalate to `incremental-delivery` when: the plan from plan-before-action spans 2–4 PRs across 1–2 modules and can be delivered serially.

## Skill Lifecycle

- Load the smallest set of skills that fits the current task.
- Drop `scoped-tasking` and `read-and-locate` once the working set and edit points are confirmed.
- Drop `plan-before-action` once execution is underway and no re-planning is needed.
- Drop `context-budget-awareness` after a successful compression if the session is now compact.
- Keep `minimal-change-strategy` and `targeted-validation` active until the task is complete.
- Drop `design-before-plan` after the design brief is produced and handed to plan-before-action — it does not stay active during implementation.
- Drop `bugfix-workflow` once the root cause is confirmed and the fix is handed off to implementation.
- Drop `safe-refactor` once the structural goal is met and invariants are intact.
- Drop `impact-analysis` after plan-before-action produces the plan.
- Drop `self-review` after the diff review passes with no blocking issues.
- Drop `incremental-delivery` after the increment list is finalized — it provides structure, not ongoing execution guidance.
- If the task phase changes (e.g., from diagnosis to implementation), re-evaluate which skills are still providing signal.
- Never carry more than 4 active skills simultaneously without explicit justification.

## Skill Protocol v2

Use the following protocol blocks literally when a task requires skill-driven execution:

1. `[task-validation: ...]`
2. `[triggers: ...]`
3. `[precheck: <skill> | ...]`
4. `[output: <skill> | ...]`
5. `[validate: <skill> | ...]`
6. `[drop: <skill> | ...]`

Insert `[loop: <skill> | "reason"]` before any repeated activation when the same skill is being retried without materially new evidence.

Keep the default block order above. Do not emit `[output: <skill>]` without a matching `[validate: <skill>]`.

### Task Validation

Language-agnostic (no English word counts, verbs, or regexes):

- `clarity`: can identify an action and a target object → `✓ | ✗ | ⚠`
- `scope`: clearly bounded, or can be narrowed by `scoped-tasking` → `✓ | ✗ | ⚠`
- `safety`: no unguarded destructive or out-of-scope request → `✓ | ✗`
- `skill_match`: at least one skill family can take the task → `✓ | ✗`

Results: `PASS` (proceed), `WARN` (ask_clarification), `REJECT` (reject)

### Standard Block Format

```
[task-validation: PASS | clarity:✓ scope:✓ safety:✓ skill_match:✓ | action:proceed]
[triggers: scoped-tasking plan-before-action]
[precheck: skill-name | PASS | checks:field1 field2]
[output: skill-name | completed high | key:"value" | next:next-skill]
[validate: skill-name | PASS | checks:field1 field2]
[drop: skill-name | reason:"completed" | active: remaining skills]
```

**With failures:**
```
[task-validation: WARN | scope:⚠ "spans 3 modules" | action:ask_clarification]
[validate: skill | FAIL | checks:field1 | failed:field2 "missing detail"]
```

**Block syntax:**
- Separator: ` | ` (pipe with spaces)
- Fields: `name:value` or `name:value1 value2` (space-delimited lists)
- Quoted values: `"..."` for text with spaces
- Symbols: `✓` (pass) `✗` (fail) `⚠` (warn) `⏸` (defer)

### Legacy v1 Format

V1 verbose YAML blocks `[block-name]...[/block-name]` remain supported for complex failures. Use v2 compact format for simple cases.

## Skill Family Concurrency Budgets

Track active skills by family, not by one global count:

- Execution: at most 4 active at once
- Orchestration: at most 1 active at once
- Primary Phase: at most 1 active at once
- `phase-contract-tools`: may coexist only with one primary phase skill, or run alone when directly maintaining phase contract assets

All skills must be explicitly deactivated. Do not rely on silent or implicit retirement when outputs have been consumed, the phase changed, the family budget would overflow, or fallback / clarification has taken over.

## Skill Chain Triggers

### Common Flow Patterns

- **bugfix-standard** (Bug fix): `scoped-tasking` → `read-and-locate` → `bugfix-workflow` → `minimal-change-strategy` → `self-review` → `targeted-validation`
- **refactor-safe** (Refactor): `scoped-tasking` → `safe-refactor` + `minimal-change-strategy` → `self-review` → `targeted-validation`
- **multi-file-planned** (Multi-file): `scoped-tasking` → `plan-before-action` → `minimal-change-strategy` → `self-review` → `targeted-validation`
- **design-first** (Design-first): `scoped-tasking` → `design-before-plan` → `plan-before-action` → `minimal-change-strategy` → `self-review` → `targeted-validation`
- **large-task** (Large task): `scoped-tasking` → `design-before-plan` → `impact-analysis` → `plan-before-action` → `incremental-delivery`
- **parallel** (Parallel): `multi-agent-protocol` → [subagents] → `conflict-resolution` (if needed) → synthesis

### Forward Handoffs

| From | To | Condition |
|------|----|-----------|
| `scoped-tasking` | `read-and-locate` | Boundary known but edit point still unknown |
| `scoped-tasking` | `plan-before-action` | Boundary confirmed, ready for implementation planning |
| `read-and-locate` | `plan-before-action` | Edit points identified, ready for sequencing |
| `design-before-plan` | `plan-before-action` | Design brief produced, ready for implementation planning |
| `impact-analysis` | `plan-before-action` | Impact summary produced, ready for sequencing |
| `self-review` | `targeted-validation` | Diff clean of blocking issues, ready for behavioral verification |
| `plan-before-action` | `incremental-delivery` | Plan spans 2–4 PRs that can be split into independently mergeable increments |

### Fallbacks

| From | To | Condition |
|------|----|-----------|
| `bugfix-workflow` | `read-and-locate` | Failure path is still unknown |
| `bugfix-workflow` | `context-budget-awareness` | Diagnosis is spinning across too many files or hypotheses |
| `minimal-change-strategy` | `design-before-plan` | Preserving the current interface may itself be the bug |
| `minimal-change-strategy` | `impact-analysis` | Supposedly local change affects multiple callers or contracts |
| `safe-refactor` | `design-before-plan` | Structural change implies interface redesign |
| `safe-refactor` | `minimal-change-strategy` | Only local cleanup is justified, not structural refactoring |
| `safe-refactor` | `read-and-locate` | Ownership seams still unclear |
| `self-review` | `minimal-change-strategy` | Review reveals the patch grew beyond task scope |
| `context-budget-awareness` | `scoped-tasking` | Compressed state shows the objective itself is too broad |
| `plan-before-action` | `design-before-plan` | Design choices, not execution order, are the real blocker |
| `plan-before-action` | `scoped-tasking` / `read-and-locate` | Edit surface still uncertain, return to discovery |
| `design-before-plan` | `impact-analysis` | Caller or module impact is still speculative |
| `design-before-plan` | `scoped-tasking` | Task boundary itself is unstable |
| `impact-analysis` | `read-and-locate` | True edit point is not stable |
| `impact-analysis` | `phase-plan` | Contract migration becomes multi-stage or externally constrained |
| `incremental-delivery` | `phase-plan` | Task exceeds 4 increments, 2 modules, or needs parallel lanes |
| `incremental-delivery` | `plan-before-action` | Downgrade — task fits in a single PR |
| `multi-agent-protocol` | `conflict-resolution` | Subagent findings disagree materially |
| `conflict-resolution` | `targeted-validation` | Adjudication requires an empirical check |

### Intentional exclusions

Phase-internal chains (P1–P7), co-active “combine with” composition edges, and a few low-frequency indirect hops are documented in the relevant SKILL.md files rather than duplicated here.
