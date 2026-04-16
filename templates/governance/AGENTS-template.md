<!-- Governance mirror: keep in sync with CLAUDE-template.md (identical content, different header) -->

# AGENTS.md

## Multi-Agent Rules

Full protocol: `multi-agent-protocol` skill.

**Tier 1 (read-only):** Launch read-only subagents anytime. Subagents return structured results; primary agent synthesizes.

**Tier 2 (write-capable):** Before launching write-capable subagents, emit: `[delegate: <count 2–4> | split: <dimension> | risk: <low|medium|high>]`. If not cleanly splittable: `[delegate: 0 | reason: <why>]`.

**Overflow (>4 subagents):** If the task requires more than 4 parallel subagents, escalate to `phase-plan` to break the work into sequential waves of 2–4 subagents each. Emit: `[delegate: 0 | reason: "overflow — escalating to phase-plan for wave decomposition"]`.

**Exempt:** Single-file edits, direct answers, single commands, git housekeeping.

## Skill Activation

Skills activate via:

- **Task-type**: `bugfix-workflow`, `safe-refactor`, `scoped-tasking`, `read-and-locate`, and `plan-before-action` auto-activate during `[triggers]` evaluation based on SKILL.md triggers.
- **Mid-task escalation**: Load full skill when base governance rules prove insufficient (see below).

## Skill Boundary

`AGENTS.md` is the governance and routing layer, not the skill manual.

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

**Pre-screening decision tree** (evaluate BEFORE task-validation — all checks are surface-level, no code analysis required):

1. Does the request contain a question with no file/code reference? → **Direct answer** → fast-path.
2. Does the request name a single shell/git command to run? → **Single command** → fast-path.
3. Does the request name 1–2 specific file paths to read (no modification)? → **Trivial file read** → fast-path.
4. Is the request a status/existence check (`git status`, `ls`, file exists)? → **Status query** → fast-path.
5. Does the request explicitly name 1 file and describe a typo fix, comment edit, or config value change? → **Single-file low-risk edit** → fast-path.
6. None of the above matched → **not fast-path** → run `[task-validation]` and `[triggers]`.

**Skip `[task-validation]` and `[triggers]`** for fast-path tasks. Proceed directly.

## Skill Escalation

Escalate when base-level governance rules insufficient:

- `design-before-plan`: Multiple implementation approaches, public API/cross-module contract changes, missing acceptance criteria, design decisions remain after scoping, or 3+ modules needing coordination.
- `minimal-change-strategy`: Diff growing beyond task scope, competing edit strategies, or cleanup temptation.
- `context-budget-awareness`: Working set >8 files, same file read >2× without new question, >3 unranked hypotheses, or last 3 actions stalled.
- `targeted-validation`: Multiple validation options, expensive validation for local change, or failure diagnosis needed.
- `impact-analysis`: Change affects 3+ callers, public API/shared type, data model across modules, or 3+ tentative leads.
- `self-review`: Multi-file edits complete, or user requests diff review.
- `incremental-delivery`: Plan spans 2–4 PRs across 1–2 modules, serially deliverable.
- `phase-plan`: Task exceeds 4 PRs or requires wave-level coordination with parallel lanes.
- `phase-execute`: Phase plan accepted and ready for wave implementation.
- `phase-plan-review`: Phase plan produced and needs acceptance gate before execution.
- `phase-contract-tools`: Fixing, extending, or validating phase contract scripts, schemas, or renderers.

## Skill Lifecycle

**Load:** Smallest set fitting task.

**Drop when complete:**
- `scoped-tasking`, `read-and-locate`: working set/edit points confirmed.
- `plan-before-action`: execution underway, no re-plan needed.
- `context-budget-awareness`: session compressed successfully.
- `design-before-plan`: design brief handed to plan-before-action.
- `bugfix-workflow`: root cause confirmed, fix handed off.
- `safe-refactor`: structural goal met, invariants intact.
- `impact-analysis`: plan produced.
- `self-review`: diff passes review.
- `incremental-delivery`: increment list finalized.
- `phase-plan`: plan.yaml and wave docs produced.
- `phase-execute`: wave execution complete and results integrated.
- `phase-plan-review`: acceptance gate passed or blocked.
- `phase-contract-tools`: contract assets updated or validated.

**Keep active:** `minimal-change-strategy`, `targeted-validation` until task complete.

**Re-evaluate:** When task phase changes (diagnosis → implementation).

**Max:** 4 active skills. Exceeding 4 requires explicit justification: the agent must name which skills are active, why each is still needed, and which will be dropped next. Valid justifications: a flow pattern requires overlapping skills during a handoff transition, or a fallback added a skill before the predecessor could be dropped.

## Skill Protocol v2

Compact inline protocol blocks for skill-driven execution.

**Block sequence and semantics:**

1. `[task-validation: ...]` — Assess incoming task for clarity, scope, safety, and skill match. On FAIL (`REJECT`): refuse the task with explanation. On WARN: ask for clarification before proceeding.
2. `[triggers: ...]` — Select which skills to activate based on task characteristics. On FAIL (no skill matches): re-evaluate task validation or ask for clarification.
3. `[precheck: <skill> | ...]` — Verify preconditions before a skill produces output (e.g., required files exist, scope confirmed). On FAIL: address the failed precondition, or fall back to a discovery skill (`read-and-locate`, `scoped-tasking`).
4. `[output: <skill> | ...]` — Record the skill's primary deliverable (e.g., a plan, a patch, a diagnosis). On FAIL: the skill did not produce a usable result; retry with new evidence or escalate to a different skill via Fallback rules.
5. `[validate: <skill> | ...]` — Confirm the output meets acceptance criteria. On FAIL: return to the skill for revision, or escalate per Fallback table.
6. `[drop: <skill> | ...]` — Deactivate a skill and release its concurrency budget slot. On FAIL (skill still needed): keep active with justification.
7. `[loop: <skill> | "reason"]` — Guard against retrying a skill without new evidence. Emit before any repeated activation. On FAIL (no new evidence): stop retrying and escalate or abandon.

**Core rules:**
- Every `[output]` requires matching `[validate]`
- Every triggered skill must eventually `[drop]`
- Use `[loop: <skill> | "reason"]` before retry without new evidence

### Task Validation

Language-agnostic checks (no English-only patterns):
- **clarity**: action + target identifiable → `✓ | ✗ | ⚠`
- **scope**: bounded or scopeable → `✓ | ✗ | ⚠`
- **safety**: no unguarded destruction → `✓ | ✗`
- **skill_match**: at least one skill applies → `✓ | ✗`

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
[loop: bugfix-workflow | "new stack trace from user"]
```

### Block Syntax

- **Separator**: ` | ` (pipe with spaces)
- **Field format**: `name:value` or `name:value1 value2` (space-delimited lists)
- **Quoted values**: Use `"..."` for text with spaces or special chars
- **Status symbols**: `✓` (pass) `✗` (fail) `⚠` (warn) `⏸` (defer)

### Legacy v1 Format

V1 verbose YAML blocks `[block-name]...[/block-name]` remain supported for complex failure scenarios requiring detailed diagnosis. Use v2 compact format for simple cases and execution traces.

## Skill Family Concurrency Budgets

**By family:**
- Execution (max 4): `scoped-tasking`, `read-and-locate`, `bugfix-workflow`, `safe-refactor`, `plan-before-action`, `design-before-plan`, `minimal-change-strategy`, `targeted-validation`, `self-review`, `context-budget-awareness`, `impact-analysis`, `incremental-delivery`
- Orchestration (max 1): `multi-agent-protocol`, `conflict-resolution`
- Primary Phase (max 1): `phase-plan`, `phase-execute`, `phase-plan-review`
- `phase-contract-tools`: coexist with 1 primary phase skill, or run alone

**Deactivation:** Explicit only. No silent retirement.

## Skill Chain Triggers

### Common Flow Patterns

```
Bug fix:       scoped-tasking → read-and-locate → bugfix-workflow → minimal-change-strategy → self-review → targeted-validation
Refactor:      scoped-tasking → safe-refactor + minimal-change-strategy → self-review → targeted-validation
Multi-file:    scoped-tasking → plan-before-action → minimal-change-strategy → self-review → targeted-validation
Design-first:  scoped-tasking → design-before-plan → plan-before-action → minimal-change-strategy → self-review → targeted-validation
Large task:    scoped-tasking → design-before-plan → impact-analysis → plan-before-action → incremental-delivery
Parallel:      multi-agent-protocol → conflict-resolution (if needed)
```

### Forward Handoffs

| From | To | Condition |
|------|----|-----------|
| `scoped-tasking` | `read-and-locate` | Boundary known but edit point still unknown |
| `scoped-tasking` | `plan-before-action` | Boundary confirmed, ready for implementation planning |
| `scoped-tasking` | `safe-refactor` | Task is structural cleanup with known boundary |
| `scoped-tasking` | `design-before-plan` | Boundary confirmed but design choices remain open |
| `read-and-locate` | `plan-before-action` | Edit points identified, ready for sequencing |
| `read-and-locate` | `bugfix-workflow` | Edit point found, root cause investigation begins |
| `bugfix-workflow` | `minimal-change-strategy` | Root cause confirmed, constraining fix scope |
| `safe-refactor` | `minimal-change-strategy` | Structural goal set, constraining change scope |
| `safe-refactor` | `self-review` | Refactor complete, ready for diff review |
| `plan-before-action` | `minimal-change-strategy` | Plan ready, constraining change scope during execution |
| `minimal-change-strategy` | `self-review` | Patch complete, ready for diff review |
| `design-before-plan` | `plan-before-action` | Design brief produced, ready for implementation planning |
| `design-before-plan` | `impact-analysis` | Design complete, assessing caller/module impact |
| `impact-analysis` | `plan-before-action` | Impact summary produced, ready for sequencing |
| `self-review` | `targeted-validation` | Diff clean of blocking issues, ready for behavioral verification |
| `plan-before-action` | `incremental-delivery` | Plan spans 2–4 PRs that can be split into independently mergeable increments |
| `multi-agent-protocol` | `conflict-resolution` | Subagent findings disagree, arbitration needed |

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

### Intentional Exclusions

Phase-internal chains (P1–P7), co-active "combine with" composition edges, and a few low-frequency indirect hops are documented in the relevant SKILL.md files rather than duplicated here.
