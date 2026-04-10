# AGENTS.md

## Multi-Agent Rules

Multi-agent execution has two tiers. Full operational protocol is in the `multi-agent-protocol` skill.

**Tier 1 — Explore (read-only):** The agent may launch read-only subagents at any time without pre-declaration. Each subagent must return structured results; the primary agent must synthesize them.

**Tier 2 — Delegate (write-capable):** Before launching any subagent that may edit files or run mutating commands, the agent must output: `[delegate: <count 2–4> | split: <dimension> | risk: <low|medium|high>]`. If the task cannot be cleanly split, output `[delegate: 0 | reason: <why>]` and stay serial.

**Exemptions:** No declaration needed for single-file edits, direct answers, single commands, or git housekeeping.

## Skill Escalation

These rules define when base-level AGENTS.md rules are insufficient and the agent should load the full skill.

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
- Drop `impact-analysis` after plan-before-action produces the plan.
- Drop `self-review` after the diff review passes with no blocking issues.
- Drop `incremental-delivery` after the increment list is finalized — it provides structure, not ongoing execution guidance.
- If the task phase changes (e.g., from diagnosis to implementation), re-evaluate which skills are still providing signal.
- Never carry more than 4 active skills simultaneously without explicit justification.

## Skill Protocol v1

Use the following protocol blocks literally when a task requires skill-driven execution:

1. `[task-input-validation]`
2. `[trigger-evaluation]`
3. `[precondition-check: <skill-name>]`
4. `[skill-output: <skill-name>]`
5. `[output-validation: <skill-name>]`
6. `[skill-deactivation: <skill-name>]` when the skill leaves the active set

Insert `[loop-detected: <skill-name>]` before any repeated activation when the same skill is being retried without materially new evidence.

Keep the default block order above. Do not emit `[skill-output: <skill-name>]` without a matching `[output-validation: <skill-name>]`.

### Task Input Validation

The protocol is language-agnostic. Do not rely on English word counts, English verbs, or English regexes.

Evaluate every new task with these checks:

- `clarity`: can identify an action and a target object
- `scope`: clearly bounded, or can be narrowed by `scoped-tasking`
- `safety`: no unguarded destructive or out-of-scope request
- `skill_match`: at least one skill family can take the task

Set:

- `result: PASS` and `action: proceed` when all required checks pass
- `result: WARN` and `action: ask_clarification` when the task can likely be recovered through clarification or scoping
- `result: REJECT` and `action: reject` when the task is unsafe or cannot be matched to the skill library

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

## Skill Family Concurrency Budgets

Track active skills by family, not by one global count:

- Execution: at most 4 active at once
- Orchestration: at most 1 active at once
- Primary Phase: at most 1 active at once
- `phase-contract-tools`: may coexist only with one primary phase skill, or run alone when directly maintaining phase contract assets

All skills must be explicitly deactivated. Do not rely on silent or implicit retirement when outputs have been consumed, the phase changed, the family budget would overflow, or fallback / clarification has taken over.
