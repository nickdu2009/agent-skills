# Skill Protocol v1

Skill Protocol v1 is the repository-wide protocol for how skills are described, activated, validated, and retired.

It applies to all three skill families:

- execution skills
- orchestration skills
- phase skills

## Why It Exists

Protocol v1 makes the skill library easier to validate and safer to evolve:

- one shared activation and output model across all skills
- explicit lifecycle and deactivation instead of silent carry-over
- language-agnostic task validation rules
- shared evaluation entrypoints for static readiness and runtime smoke checks

## Standard Blocks

Use these blocks literally when a skill-driven execution flow is shown or evaluated:

1. `[task-input-validation]`
2. `[trigger-evaluation]`
3. `[precondition-check: <skill-name>]`
4. `[skill-output: <skill-name>]`
5. `[output-validation: <skill-name>]`
6. `[skill-deactivation: <skill-name>]`

Insert `[loop-detected: <skill-name>]` before retrying a skill without materially new evidence.

## Default Order

```text
[task-input-validation]
[trigger-evaluation]
[precondition-check: <skill>]
[skill-output: <skill>]
[output-validation: <skill>]
[skill-deactivation: <skill>]
```

Do not emit `[skill-output: <skill>]` without a matching `[output-validation: <skill>]`.

## Language-Agnostic Input Checks

Task validation must not depend on English-only heuristics such as word counts or verb regexes.

Use these checks instead:

- `clarity`: can you identify an action and a target object?
- `scope`: is the request already bounded, or can it be narrowed safely?
- `safety`: is the request safe and within authority?
- `skill_match`: does at least one skill family apply?

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

## Evaluation Entry Points

Use the existing evaluation entrypoints:

```bash
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report --fail-on-protocol-issues
python3 maintainer/scripts/evaluation/run_claude_trigger_smoke.py --list-cases
```

`run_trigger_tests.py` reports static protocol readiness for skill documents.

`run_claude_trigger_smoke.py` checks runtime outputs for:

- required protocol blocks
- block order
- `skill-output` / `output-validation` pairing
- missing precondition checks
- missing deactivation
- family budget violations

## Examples

All files under `examples/` now include a compact Skill Protocol v1 trace so the repository shows both:

- when a skill should be used
- what compliant protocol output looks like
