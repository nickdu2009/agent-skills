# CLAUDE.md

## Multi-Agent Rules

Full protocol: `multi-agent-protocol` skill.

**Tier 1 (read-only):** Launch read-only subagents anytime. Subagents return structured results; primary agent synthesizes.

**Tier 2 (write-capable):** Before launching write-capable subagents, emit: `[delegate: <count 2–4> | split: <dimension> | risk: <low|medium|high>]`. If not cleanly splittable: `[delegate: 0 | reason: <why>]`.

**Exempt:** Single-file edits, direct answers, single commands, git housekeeping.

## Skill Activation

Skills activate via:

- **Task-type**: Skills auto-activate during `[trigger-evaluation]` based on SKILL.md triggers.
- **Mid-task escalation**: Load full skill when base governance rules prove insufficient (see below).

## Governance Fast-Path

**No skill needed** for tasks fully handleable at the governance layer:

- **Direct answers**: Questions requiring no code exploration (concepts, prior context, definitions).
- **Single commands**: One-off shell/git commands with clear output.
- **Trivial file reads**: Read 1–2 specific files when path is known.
- **Status queries**: Git status, file existence, directory listing.
- **Single-file low-risk edits**: Typo fix, comment update, config tweak in 1 file with no caller impact.

**Skip `[task-input-validation]` and `[trigger-evaluation]`** for fast-path tasks. Proceed directly.

## Skill Escalation

Escalate when base-level CLAUDE.md rules insufficient:

- `design-before-plan`: Multiple implementation approaches, public API/cross-module contract changes, missing acceptance criteria, design decisions remain after scoping, or 3+ modules needing coordination.
- `minimal-change-strategy`: Diff growing beyond task scope, competing edit strategies, or cleanup temptation.
- `context-budget-awareness`: Working set >8 files, same file read >2× without new question, >3 unranked hypotheses, or last 3 actions stalled.
- `targeted-validation`: Multiple validation options, expensive validation for local change, or failure diagnosis needed.
- `impact-analysis`: Change affects 3+ callers, public API/shared type, data model across modules, or 3+ tentative leads.
- `self-review`: Multi-file edits complete, or user requests diff review.
- `incremental-delivery`: Plan spans 2–4 PRs across 1–2 modules, serially deliverable.

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

**Keep active:** `minimal-change-strategy`, `targeted-validation` until task complete.

**Re-evaluate:** When task phase changes (diagnosis → implementation).

**Max:** 4 active skills without justification.

## Skill Chain Triggers

### Common Flow Patterns

```
Bug fix:       scoped-tasking -> read-and-locate -> bugfix-workflow -> minimal-change-strategy -> self-review -> targeted-validation
Refactor:      scoped-tasking -> safe-refactor + minimal-change-strategy -> self-review -> targeted-validation
Multi-file:    scoped-tasking -> plan-before-action -> minimal-change-strategy -> self-review -> targeted-validation
Design-first:  scoped-tasking -> design-before-plan -> plan-before-action -> minimal-change-strategy -> self-review -> targeted-validation
Large task:    scoped-tasking -> design-before-plan -> impact-analysis -> plan-before-action -> incremental-delivery
Parallel:      multi-agent-protocol -> [subagents] -> conflict-resolution (if needed) -> synthesis
```

### Forward Handoffs

| From | To | Condition |
|------|----|-----------|
| `scoped-tasking` | `read-and-locate` | Boundary known but edit point still unknown |
| `scoped-tasking` | `plan-before-action` | Boundary confirmed, ready for implementation planning |
| `read-and-locate` | `plan-before-action` | Edit points identified, ready for sequencing |
| `design-before-plan` | `plan-before-action` | Design brief produced, ready for implementation planning |
| `impact-analysis` | `plan-before-action` | Impact summary produced, ready for sequencing |
| `self-review` | `targeted-validation` | Diff clean of blocking issues, ready for behavioral verification |
| `plan-before-action` | `incremental-delivery` | Plan spans 2-4 PRs that can be split into independently mergeable increments |

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
| `incremental-delivery` | `plan-before-action` | Downgrade -- task fits in a single PR |
| `multi-agent-protocol` | `conflict-resolution` | Subagent findings disagree materially |
| `conflict-resolution` | `targeted-validation` | Adjudication requires an empirical check |

## Skill Protocol v1

**Block sequence** for skill-driven tasks:

1. `[task-input-validation]`
2. `[trigger-evaluation]`
3. `[precondition-check: <skill-name>]`
4. `[skill-output: <skill-name>]`
5. `[output-validation: <skill-name>]`
6. `[skill-deactivation: <skill-name>]`

**Loop guard:** `[loop-detected: <skill-name>]` before retry without new evidence.

**Pairing rule:** Every `[skill-output]` requires matching `[output-validation]`.

### Task Input Validation

**Language-agnostic.** Do not rely on English-specific patterns.

**Checks:**
- `clarity`: action + target identifiable
- `scope`: bounded or scopeable
- `safety`: no unguarded destruction
- `skill_match`: at least one skill family applies

**Results:**
- `PASS` / `proceed`: all checks pass
- `WARN` / `ask_clarification`: recoverable via clarification
- `REJECT` / `reject`: unsafe or unmatchable

### Minimum Block Shape

```yaml
[task-input-validation]
task: "<user request verbatim>"
checks:
  clarity:
    status: PASS | FAIL
    reason: "<why>"
  scope:
    status: PASS | WARN | FAIL
    reason: "<why>"
  safety:
    status: PASS | FAIL
    reason: "<why>"
  skill_match:
    status: PASS | WARN | FAIL
    reason: "<why>"
result: PASS | WARN | REJECT
action: proceed | ask_clarification | reject
[/task-input-validation]

[trigger-evaluation]
task: "<one-line task summary>"
evaluated:
  - scoped-tasking: ✓ TRIGGER | ✗ SKIP | ⏸ DEFER
activated_now: [...]
deferred: [...]
[/trigger-evaluation]

[precondition-check: <skill-name>]
checks:
  - <field>: ✓ PASS | ✗ FAIL
result: PASS | FAIL
[/precondition-check]

[skill-output: <skill-name>]
status: completed | failed | partial
confidence: high | medium | low
outputs: {...}
signals: {...}
recommendations: {...}
[/skill-output]

[output-validation: <skill-name>]
checks:
  - outputs.<field>: ✓ PASS | ✗ FAIL
result: PASS | FAIL
[/output-validation]

[skill-deactivation: <skill-name>]
reason: "<why>"
outputs_consumed_by: [...]
remaining_active: [...]
[/skill-deactivation]
```

### Protocol v2 (Compact)

For simple cases, use compact inline format:

- `[task-validation: PASS | clarity:✓ scope:✓ safety:✓ skill_match:✓ | action:proceed]`
- `[triggers: scoped-tasking plan-before-action]`
- `[precheck: skill-name | PASS]`
- `[output: skill-name | completed high | <key outputs> | next:next-skill]`
- `[validate: skill-name | PASS]`
- `[drop: skill-name | "reason" | active: remaining skills]`

Both v1 (verbose YAML) and v2 (compact inline) are supported. Use v2 for simple pass cases and execution traces; keep v1 for failures requiring detailed diagnosis.

## Skill Family Concurrency Budgets

**By family:**
- Execution: max 4
- Orchestration: max 1
- Primary Phase: max 1
- `phase-contract-tools`: coexist with 1 primary phase skill, or run alone

**Deactivation:** Explicit only. No silent retirement.
