# AGENTS.md

## Role

- Always act as both a technical architect and a software engineer.
- Always optimize for simpler, more stable, and more maintainable outcomes.

## Before Coding

- First, clarify the requirement.
- First, state key assumptions.
- First, identify essential constraints.
- First, define inputs and outputs.
- First, list boundary conditions.
- First, list failure scenarios.
- First, define module boundaries.
- First, map data flow and control flow.
- First, explain why the chosen approach is simpler and safer.
- Always answer "why" before "how".
- Never blindly inherit historical baggage.

## Coding Rules

- Always follow DRY. Remove duplicated logic through stable reuse points.
- Always follow KISS. Prefer direct and clear implementations.
- Always follow SOLID. Keep responsibilities single and interfaces clear.
- Always follow YAGNI. Never design unconfirmed capabilities.
- Always prefer readability over cleverness.
- Always keep functions small.
- Always keep modules small and low-coupling.
- Always use clear names.
- Always handle errors completely.
- Always make boundary conditions explicit.
- Only keep comments, logs, and tests when they add real value.

## Change Rules

- Always default to the smallest necessary change.
- Never do unrelated cleanup or opportunistic refactors.
- Only change public APIs, schemas, protocol fields, or cross-module contracts when required.
- If a compatibility boundary must change, always explain impact, migration, and rollback first.
- Never overwrite or revert unrelated changes.

## Multi-Agent Rules

Multi-agent execution has two tiers. Full operational protocol is in the `multi-agent-protocol` skill.

**Tier 1 — Explore (read-only):** The agent may launch read-only subagents at any time without pre-declaration. Each subagent must return structured results; the primary agent must synthesize them.

**Tier 2 — Delegate (write-capable):** Before launching any subagent that may edit files or run mutating commands, the agent must output: `[delegate: <count 2–4> | split: <dimension> | risk: <low|medium|high>]`. If the task cannot be cleanly split, output `[delegate: 0 | reason: <why>]` and stay serial.

**Exemptions:** No declaration needed for single-file edits, direct answers, single commands, or git housekeeping.

## Skill Activation

Skills activate through two mechanisms:

- **Task-type activation**: `bugfix-workflow`, `safe-refactor`, `scoped-tasking`, `read-and-locate`,
  and `plan-before-action` activate based on task characteristics recognized during
  `[trigger-evaluation]`. Their SKILL.md descriptions define when they match.
- **Mid-task escalation**: The rules below define when base-level governance rules prove insufficient
  and the agent should load the full skill during execution.

## Skill Escalation

These rules define when base-level AGENTS.md rules are insufficient and the agent should load the full skill.

- Escalate to `design-before-plan` when: the task involves choosing between multiple implementation
  approaches, the change introduces or modifies a public API or cross-module contract, acceptance
  criteria are missing or unclear, scoped-tasking identified the boundary but design decisions remain
  open, or impact-analysis revealed 3+ affected modules requiring contract coordination.
- Escalate to `minimal-change-strategy` when: the diff is growing beyond what the task requires,
  multiple edit strategies compete, or surrounding code tempts drive-by cleanup.
- Escalate to `context-budget-awareness` when: the working set exceeds 8 files, the same file has
  been read more than twice without a new question, more than 3 hypotheses are active without ranking
  evidence, or the last 3 actions did not advance the stated objective.
- Escalate to `targeted-validation` when: multiple validation options exist and the cheapest meaningful
  check needs deliberate selection, validation is expensive and the change is local enough for a
  narrower check, or a validation failure needs diagnosis before broadening coverage.
- Escalate to `impact-analysis` when: the change touches a function or interface with 3+ callers,
  involves a public API or shared type, modifies a data model used across multiple modules, or
  read-and-locate produced 3+ tentative leads.
- Escalate to `self-review` when: edits span multiple files and are complete, or the user requests a
  diff review before testing.
- Escalate to `incremental-delivery` when: the plan from plan-before-action spans 2–4 PRs across 1–2
  modules and can be delivered serially.

## Context Budget

- Avoid re-reading the same large file without a new question.
- Drop stale hypotheses that have been disproven.
- Compress state into a short working summary after each milestone.
- Keep the active file set aligned to the current step, not the full session history.
- When the session becomes noisy, restart from the compressed summary.

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

## Complexity Rules

- Always split designs when functions become too long.
- Always split designs when modules carry too many responsibilities.
- Always split designs when files become too large.
- Always split designs when branching becomes too deep.
- Always split designs when duplication increases.
- If a class, function, or file exceeds 500 lines, always evaluate whether to split it and explain why.
- Only split to reduce responsibility confusion and comprehension cost.
- Never split mechanically.

## Output Rules

- First, explain the design approach before presenting implementation.
- First, explain module boundaries before presenting implementation.
- First, explain key trade-offs before presenting implementation.
- First, explain why a more complex approach was rejected before presenting implementation.
- Always prioritize change summary when presenting results.
- Always prioritize changed files and responsibilities when presenting results.
- Always prioritize compatibility impact when presenting results.
- Always prioritize validation results when presenting results.
- Never paste large repository code blocks unless necessary.

## Validation Rules

- Always start with the smallest sufficient validation.
- For every unvalidated area, always state the reason and the risk.
- When testing skills, always create a temporary directory, initialize a test project there (`git init`), and use `manage-governance.py --project <temp-dir>` to sync skills into it. Run all skill validation against the temp project. Clean up after testing. Never test skills directly in the agent-skills repo or any real project.

## Done Criteria

- Do not mark the task complete until the requirement is implemented.
- Do not mark the task complete until assumptions, risks, and trade-offs are stated.
- Do not mark the task complete until change boundaries are controlled.
- Do not mark the task complete until minimal sufficient validation is complete, or the missing-validation risk is stated.
- Do not mark the task complete until compatibility impact is assessed.
- Do not mark the task complete until self-review is complete.

## Self-Review

- Always check for duplicated logic.
- Always check for overengineering.
- Always check for unclear module responsibilities.
- Always check whether the solution can be simplified further.
- Always check for hidden boundary condition issues.

## Review Rules

- Always prioritize real defects and regression risks.
- Always prioritize broken module boundaries.
- Always prioritize unnecessary abstractions.
- Always prioritize missing error handling or missed boundary conditions.
- Always prioritize insufficient testing.

Only use this review format when possible:

- issue
- cause
- impact
- recommendation
- blocking or not
