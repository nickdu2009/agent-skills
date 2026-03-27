---
name: phase-plan
description: Design or update a structured implementation plan that breaks a large task into sequenced waves of parallel work. Use when the agent needs to create phaseN-plan.yaml and supporting docs for multi-wave execution, or convert a roadmap into an executable plan with PR sequencing and wave ownership.
---

# Phase Plan

Design the phase as an execution system, not as a pile of planning prose.

The primary output is a structured execution schema:

- `docs/phaseN-plan.yaml`

Markdown exists to help humans coordinate around that schema:

- `docs/phaseN-roadmap.md`
- `docs/phaseN-wave-guide.md`
- `docs/phaseN-execution-index.md`

## Skill Assets

Resolve bundled assets relative to the directory that contains `SKILL.md`.

- `../phase-contract-tools/references/...` are the shared contract references
- `../phase-contract-tools/scripts/...` are the shared contract helpers
- do not assume these files exist in the target repository
- when invoking a helper script, pass target-repository paths explicitly

If this SKILL.md and a bundled reference document disagree on a rule, this SKILL.md wins.
References elaborate and provide examples; they do not override top-level skill rules.

Read these shared contract references when needed:

- [`../phase-contract-tools/references/contract-authority-and-migration.md`](../phase-contract-tools/references/contract-authority-and-migration.md) for authority boundaries, cutover rules, and core-only entrypoints
- [`../phase-contract-tools/references/machine-execution-schema.md`](../phase-contract-tools/references/machine-execution-schema.md) for the execution authority model and required schema fields
- [`../phase-contract-tools/references/llm-friendly-phase-schema.md`](../phase-contract-tools/references/llm-friendly-phase-schema.md) for agent-facing instruction encoding rules
- [`../phase-contract-tools/references/phase-execution-schema-template.yaml`](../phase-contract-tools/references/phase-execution-schema-template.yaml) for a full phase schema skeleton
- [`../phase-contract-tools/references/phase-agent-task-template.yaml`](../phase-contract-tools/references/phase-agent-task-template.yaml) for a single PR task template
- [`../phase-contract-tools/references/prompt-derivation-from-schema.md`](../phase-contract-tools/references/prompt-derivation-from-schema.md) for prompt and kickoff rendering rules

Use these shared contract scripts:

- `uv run ../phase-contract-tools/scripts/validate_phase_execution_schema.py --plan /path/to/docs/phaseN-plan.yaml`
- `uv run ../phase-contract-tools/scripts/validate_phase_doc_set.py --docs-dir /path/to/repo/docs --phase phaseN`
- `uv run ../phase-contract-tools/scripts/render_agent_prompt.py --plan /path/to/docs/phaseN-plan.yaml --pr P13-10`
- `uv run ../phase-contract-tools/scripts/render_wave_kickoff.py --plan /path/to/docs/phaseN-plan.yaml --wave 3`

## Core Principles

1. Execution schema is the authority.
2. Markdown is narrative and coordination, not the execution source.
3. Agent-facing instructions must be explicit, list-shaped, and minimally inferential.
4. Every execution reference must be typed and resolvable.
5. Prompts are derived artifacts, not hand-maintained planning assets.
6. Do not duplicate structured task payloads across files.
7. Do not add fallback planning modes. Use one uniform phase model. Partial-output mode is not a fallback — it is the same model applied to a user-requested artifact subset.

## Default Output Contract

Unless the user explicitly asks for a narrower subset, produce exactly this default phase set:

1. `docs/phaseN-roadmap.md`
2. `docs/phaseN-plan.yaml`
3. `docs/phaseN-wave-guide.md`
4. `docs/phaseN-execution-index.md`

Do not create these by default:

- `phaseN-first-wave-pr-breakdown.md`
- `phaseN-parallel-matrix.md`
- `phaseN-pr-delivery-plan.md`
- `phaseN-pr-parallelization-plan.md`
- `phaseN-waveX-agent-launch-prompts.md`

Do not add extra `phaseN-*` planning docs.

If the user wants additional handoff material, derive it from the schema at response time or through a renderer instead of creating another planning file.

If the user explicitly asks for a narrower subset, enter partial-output mode.

In partial-output mode:
- produce only the explicitly requested artifacts
- do not claim the strict four-file phase doc set is complete
- run only the validators that apply to the artifacts that were created or changed
- explicitly state which artifacts and validations were omitted

## File Responsibilities

### `phaseN-roadmap.md`

Use it for:

- baseline
- goals
- non-goals
- milestones
- success metrics
- validation posture
- recommended order
- deferred items
- phase done-when

Do not use it for:

- full PR task cards
- wave lane payloads
- prompt text
- duplicate validation command blocks that already live in YAML

### `phaseN-plan.yaml`

This is the only execution authority.

It owns:

- authority
- hard rules
- team
- hotspots
- validation profiles
- placeholder conventions
- PR task definitions
- wave definitions
- typed lane references

If Markdown disagrees with YAML on execution fields, YAML wins.

### `phaseN-wave-guide.md`

Use it for:

- wave summary
- lane visibility
- merge windows
- wave constraints
- integrator checklists
- how to resolve work from `phaseN-plan.yaml`

Do not restate full PR payloads here.

### `phaseN-execution-index.md`

Use it for:

- reading order
- authority order
- role-to-doc navigation
- current doc-set boundaries

## Build The Baseline

Establish the real baseline from current code and accepted planning state, not from stale prose.

Read only the inputs that materially constrain the next phase:

- latest accepted phase roadmap or closeout
- backlog or architecture-improvement docs
- RFCs or design notes that still constrain behavior
- current code layout when hotspot ownership depends on real files

If code and older planning docs disagree, plan from current code and record the stale docs as context rather than re-planning already-complete work.

## Shared Contract Authority

`phase-plan` owns phase design and document authoring.

`phase-contract-tools` is the sole contract authority and owns:

- execution schema field semantics
- agent-facing field-writing rules
- prompt derivation rules
- schema and doc-set validation helpers
- cutover rules for canonical script entrypoints

When authoring or repairing `phaseN-plan.yaml`, treat these as the contract authorities:

- `../phase-contract-tools/references/contract-authority-and-migration.md`
- `../phase-contract-tools/references/machine-execution-schema.md`
- `../phase-contract-tools/references/llm-friendly-phase-schema.md`
- `../phase-contract-tools/references/prompt-derivation-from-schema.md`

Do not define a parallel contract inside `phase-plan`.

## Reference Loading By Task

When authoring a new phase:
- read: machine-execution-schema.md, llm-friendly-phase-schema.md, phase-execution-schema-template.yaml, phase-agent-task-template.yaml
- run: validate_phase_execution_schema.py, validate_phase_doc_set.py after authoring

When repairing an existing plan:
- read: machine-execution-schema.md, llm-friendly-phase-schema.md
- run: validate_phase_execution_schema.py to see current errors

When deriving prompts:
- read: prompt-derivation-from-schema.md
- run: render_agent_prompt.py or render_wave_kickoff.py

Do not load all references at once. Load only the set that matches the current task.

## Workflow

Before following the default workflow, determine whether the task is:
- full-doc-set authoring
- partial-output mode

If partial-output mode is requested, execute only the steps relevant to the requested artifacts and explicitly skip the others.

Follow this order:

1. Read the current code baseline and accepted planning inputs.
2. Freeze scope, non-goals, and milestones in `phaseN-roadmap.md`.
3. Encode execution structure in `phaseN-plan.yaml`.
4. Build the human coordination view in `phaseN-wave-guide.md`.
5. Build the reading order and authority view in `phaseN-execution-index.md`.
6. Validate the schema through `../phase-contract-tools/scripts/validate_phase_execution_schema.py`.
7. Validate the doc set through `../phase-contract-tools/scripts/validate_phase_doc_set.py`.
8. Derive prompts or kickoff text from the schema only through `../phase-contract-tools/scripts/*` renderers when needed.

Do not start by drafting prompt text.

## Validation Requirements

Run both validators for a non-trivial full-doc-set phase.

For partial-output mode:
- run schema validation if `docs/phaseN-plan.yaml` was created or changed
- run doc-set validation only when the full strict four-file set is being delivered
- if a validator is skipped, state why

Schema validation:

- `uv run ../phase-contract-tools/scripts/validate_phase_execution_schema.py --plan /path/to/docs/phaseN-plan.yaml`

Doc-set validation:

- `uv run ../phase-contract-tools/scripts/validate_phase_doc_set.py --docs-dir /path/to/repo/docs --phase phaseN`

Validator output must be LLM-actionable:

- include the failing field path when available
- include the invalid value when available
- include the expected value or allowed set
- include the file path and, if practical, a line number or section location

Fix hard errors before finishing. If a warning is intentionally accepted, state why.

## Script Rules

- Run shared contract Python helpers with `uv run`, not plain `python`.
- Keep dependencies declared inline with PEP 723 metadata.
- Prefer deterministic stdout over chatty logs.
- Do not make renderers depend on hand-written prompt docs.

- Only call `../phase-contract-tools/scripts/*`.
- Do not add or preserve alternate script entrypoints under `phase-plan`.
- Do not document any non-core path as a valid contract helper.

## Guardrails

- Do not add fallback planning modes for simpler phases.
- Do not let Markdown redefine YAML-owned execution fields.
- Do not duplicate full task payloads across docs.
- Do not hide constraints inside prose-heavy paragraphs.
- Do not invent owner splits or PR ids inside prompts.
- Do not add any extra phase planning docs beyond the strict four-file set.
- Do not leave validation as "run tests" when you can name the package, suite, or profile.
- Do not use vague execution language such as `as needed`, `if needed`, or `make sure`.
- Do not let `read_first` drift into undeclared phase-local files outside the strict four-file set.
- Do not store document path and section hint in one `read_first` string.
- Do not store profile refs and shell commands as raw validation strings.

## Done Criteria

The following done criteria apply to a full-doc-set planning pass.

The planning pass is done only when:

- the baseline matches observable code reality
- the roadmap freezes scope and non-goals clearly
- the YAML schema is complete and internally consistent
- the wave guide is sufficient for human coordination without duplicating YAML
- the execution index states reading order and authority clearly
- prompts can be derived from the schema without hand-maintained prompt docs
- validators pass or any accepted warning is explicitly explained

For partial-output mode, the task is done only when:
- the requested artifacts are internally consistent
- any applicable validators pass
- omitted artifacts and skipped validators are explicitly called out
- if the strict four-file set is incomplete after this pass, state that execution via `$phase-execute` requires completing the remaining artifacts

## Composition

Use this skill together with:

- `$phase-contract-tools` for the sole schema, validator, renderer, handoff, and cutover contract
- `$phase-execute` after the accepted doc set exists and execution can consume the contract-defined artifacts
