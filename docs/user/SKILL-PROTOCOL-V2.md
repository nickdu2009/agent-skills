# Skill Protocol v2

Skill Protocol v2 defines the canonical compact protocol for how skills are activated, validated, and retired.

It applies to all three skill families:

- execution skills
- orchestration skills
- phase skills

## Protocol Position

v2 is a protocol reset, not a formatting shortcut.

- compact inline blocks are the only canonical representation
- verbose multi-line YAML-style protocol blocks are not part of v2
- protocol evidence must be observable in execution traces, not implied by prose alone

## Scope And Intent

v2 is a governance-layer execution protocol, not a universal response format.

Use it when a task has entered skill-driven execution and the agent must make skill activation,
handoff, validation, or deactivation observable.

Do not use it to wrap ordinary conversation, simple direct answers, or routine low-risk actions
that do not materially rely on skill governance.

This boundary keeps the protocol useful without making the agent sound procedural in every turn.
The goal is controlled skill execution, not protocol-shaped conversation.

## Where It Applies

v2 applies anywhere the repository needs skill-driven work to be observable and checkable:

- governance files such as `AGENTS.md` or `CLAUDE.md`
- skill execution traces where activation, handoff, validation, and retirement must be explicit
- evaluation and release checks that inspect whether skill usage followed the required lifecycle

It is not just a formatting convention for examples. It is the shared execution trace contract
across governance, runtime behavior, and evaluation.

## Why It Exists

Protocol v2 keeps the skill library easier to execute, validate, and evolve:

- one shared compact activation and output model across all skills
- lower token overhead in governance templates and execution traces
- explicit lifecycle and deactivation instead of silent carry-over
- language-agnostic task validation rules
- one consistent machine-readable surface for evaluation

## What It Does

v2 gives the repository a consistent way to make skill usage visible:

- shows why a skill was activated instead of leaving activation implicit
- records whether preconditions were checked before execution
- pairs each skill output with a validation step
- makes handoff and deactivation explicit when the active skill set changes
- gives evaluators one compact surface for checking protocol compliance

In practice, v2 turns skill use from hidden agent state into a structured, reviewable trace.

## Standard Blocks

Use these blocks literally when a skill-driven execution flow is shown or evaluated:

1. `[task-validation: ...]`
2. `[triggers: ...]`
3. `[precheck: <skill-name> | ...]`
4. `[output: <skill-name> | ...]`
5. `[validate: <skill-name> | ...]`
6. `[drop: <skill-name> | ...]`

Optional:

- `[loop: <skill-name> | "..."]`

## Default Order

```text
[task-validation: ...]
[triggers: ...]
[precheck: <skill> | ...]
[output: <skill> | ...]
[validate: <skill> | ...]
[drop: <skill> | ...]
```

Rules:

- `task-validation` must appear before `triggers`
- `precheck` must appear before the matching `output`
- do not emit `output` without a matching `validate`
- every activated skill must eventually emit `drop`
- use `loop` only when retrying without materially new evidence

## Canonical Block Forms

### Task Validation

```text
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
```

Required semantics:

- result: `PASS | WARN | REJECT`
- `clarity`
- `scope`
- `safety`
- `skill_match`
- action: `proceed | ask_clarification | reject`

### Trigger Evaluation

```text
[triggers: scoped-tasking:trigger plan-before-action:trigger read-and-locate:defer safe-refactor:skip]
```

Required semantics:

- every evaluated skill must appear exactly once
- each evaluated skill must carry one decision: `trigger | defer | skip`
- at least one skill must be marked `trigger`

### Precondition Check

```text
[precheck: plan-before-action | result:PASS | checks:boundary-known working-set-sized validation-path-chosen]
```

Required semantics:

- skill name
- `result:PASS | FAIL`
- `checks`, naming the preconditions actually evaluated

Optional:

- `failed`
- quoted notes when a failure or warning needs explanation

### Skill Output

```text
[output: plan-before-action | status:completed | confidence:high | assumptions:"single timeout path" | working_set:"a.py b.py" | sequence:"edit -> validate" | validation_boundary:"focused timeout test" | next:minimal-change-strategy]
```

Required semantics:

- skill name
- `status:completed | partial | failed`
- `confidence:high | medium | low`
- canonical output fields from the skill's contract

Optional:

- `next:<skill>`
- residual uncertainty

Rules:

- field names inside `output` must match the canonical names defined by the skill contract
- `completed` output must include the required contract fields for that skill
- `partial` and `failed` output may include only the fields established so far

### Output Validation

```text
[validate: plan-before-action | result:PASS | checks:assumptions working_set sequence validation_boundary]
```

Required semantics:

- skill name
- `result:PASS | FAIL`
- `checks`, naming the output fields actually validated

Optional:

- `failed`
- `missing`

### Skill Deactivation

```text
[drop: plan-before-action | reason:"execution started" | active:minimal-change-strategy targeted-validation]
```

Required semantics:

- skill name
- reason
- remaining active skills, or `active:none`

### Loop Detection

```text
[loop: read-and-locate | reason:"re-activated without new evidence"]
```

Use only when the same skill is retried without materially new evidence.

## Canonical Syntax Rules

Use one canonical surface so compact traces remain parseable and comparable:

- block shape: `[<block>: <header> | <field> | <field> ...]`
- canonical field separator: ` | `
- every segment after the header is a named field using `name:value`
- field names may appear at most once per block
- identifier lists use space-delimited bare tokens
- values containing spaces or reserved characters must be double-quoted
- double quotes inside quoted values must be escaped as `\"`
- unknown field names are not canonical

Header semantics:

- `task-validation`: overall result token
- `triggers`: one or more `<skill>:<decision>` pairs
- `precheck`, `output`, `validate`, `drop`, `loop`: skill name

Canonical order:

- `task-validation`: result -> check statuses -> action
- `triggers`: evaluated skill decisions only
- `precheck`: skill -> result -> checks -> failed or notes
- `output`: skill -> status -> confidence -> contract-bound output fields -> next or residual
- `validate`: skill -> result -> checks -> failed or missing
- `drop`: skill -> reason -> active
- `loop`: skill -> reason

Status vocabularies:

- task validation: `PASS | WARN | REJECT`
- trigger decision: `trigger | defer | skip`
- precheck / validate result: `PASS | FAIL`
- output status: `completed | partial | failed`
- output confidence: `high | medium | low`

## Output Field Binding

Every skill owns a canonical output field set through its contract.

- `output` fields must use those canonical names directly
- `validate` checks must reference the same canonical names
- aliases are not canonical protocol

Examples:

- use `analysis_boundary`, not `boundary`
- use `validation_boundary`, not `validation`
- use `affected_callers`, not `callers`

## Language-Agnostic Input Checks

Task validation must not depend on English-only heuristics such as word counts or verb regexes.

Use these checks instead:

- `clarity`: can you identify an action and a target object?
- `scope`: is the request already bounded, or can it be narrowed safely?
- `safety`: is the request safe and within authority?
- `skill_match`: does at least one skill family apply?

## Governance Fast-Path

These tasks may skip protocol blocks entirely:

- direct answers
- single commands
- trivial file reads
- status queries
- single-file low-risk edits

## Family Budgets

Track active skills by family:

- Execution: at most 4 active at once
- Orchestration: at most 1 active at once
- Primary Phase: at most 1 active at once
- `phase-contract-tools`: may coexist only with one primary phase skill, or run alone for direct contract maintenance

All active skills must be explicitly deactivated.

## Skill Document Requirements

Execution skills must include:

- `## Contract`
- `## Failure Handling`
- `## Output Example`
- `## Deactivation Trigger`

`multi-agent-protocol` must include:

- `## Delegation Contract`
- `## Synthesis Contract`
- `## Failure Handling`
- `## Deactivation Trigger`

`conflict-resolution` must include:

- `## Contract`
- `## Failure Handling`
- `## Deactivation Trigger`

Phase skills must include:

- `## Artifact Contract`
- `## Gate Contract`
- `## Failure Handling`
- `## Lifecycle`

## Canonical Example

```text
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
[triggers: scoped-tasking:trigger plan-before-action:trigger read-and-locate:defer]
[precheck: scoped-tasking | result:PASS | checks:objective-clear boundary-unknown]
[output: scoped-tasking | status:completed | confidence:high | objective:"fix timeout regression" | analysis_boundary:"export controller export service failing test" | excluded_areas:"payment flow ui" | next:plan-before-action]
[validate: scoped-tasking | result:PASS | checks:objective analysis_boundary excluded_areas]
[drop: scoped-tasking | reason:"boundary consumed by planning" | active:plan-before-action]
[precheck: plan-before-action | result:PASS | checks:boundary-known working-set-sized validation-path-chosen]
[output: plan-before-action | status:completed | confidence:high | assumptions:"single timeout path in export flow" | working_set:"export_service.py export_test.py" | sequence:"patch -> focused test" | validation_boundary:"export timeout test" | next:minimal-change-strategy]
[validate: plan-before-action | result:PASS | checks:assumptions working_set sequence validation_boundary]
[drop: plan-before-action | reason:"execution begins" | active:minimal-change-strategy targeted-validation]
```

## Differences From v1

v2 differs from v1 in these ways:

1. v2 is compact-first and inline-only.
   v1 used verbose multi-line YAML-style protocol blocks as the standard format.

2. v2 treats compact blocks as the canonical protocol surface.
   v1 tied the protocol definition more closely to verbose teaching examples.

3. v2 removes verbose block-shape as part of the protocol definition.
   Under v2, block semantics remain, but the canonical representation is always compact.

4. v2 reduces runtime token cost.
   Governance templates, examples, and execution traces can express the same protocol semantics with fewer tokens.

5. v2 keeps the core lifecycle semantics.
   Task validation, trigger evaluation, precondition checks, output/validation pairing, explicit deactivation, and family budgets all remain part of the protocol.

6. v2 is better suited for machine parsing in live traces.
   Inline blocks with fixed field order, explicit trigger decisions, and contract-bound output fields produce a smaller and more regular surface for protocol-aware evaluation.
