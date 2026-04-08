---
name: phase-contract-tools
description: Shared contract library for phase planning and execution. Usually loaded by phase-plan or phase-execute, not triggered independently. Use directly only when the task is to fix, extend, or validate the phase contract scripts, schema definitions, or renderers themselves.
---

# Phase Contract Tools

Use this skill as the shared tools layer for schema-first phase work.

`docs/phaseN-plan.yaml` is the execution authority inside a repository.

`$phase-contract-tools` is the only skill-bundle authority for schema semantics, validators, renderers, handoff contracts, and status snapshot structure.

It owns the stable contract for:

- `docs/phaseN-plan.yaml`
- external contract authority declarations consumed through `phaseN-plan.yaml`
- the strict four-file phase doc set
- prompt derivation from schema
- wave lane handoff artifacts
- wave-state vocabulary
- wave status snapshots

`$phase-plan` should use this skill to design and validate phases.

`$phase-execute` should use this skill to consume, render, verify, and report execution state.

## External Contract Authority

`docs/phaseN-plan.yaml` is the execution authority inside the repository.

It is not the public contract authority.

When a phase depends on OpenAPI, YAML protocol docs, webhook contracts, PDFs, or a user-named spec:

- declare that source under `external_contracts`
- declare the owned subset and excluded subset explicitly
- keep execution aligned with the declared contract instead of legacy repository shapes
- treat `fail-closed` behavior as risk control, not as contract completion

## Skill Assets

Resolve bundled assets relative to the directory that contains `SKILL.md`.

- `references/...` are the contract documents
- `scripts/...` are the executable helpers
- do not assume these files exist in the target repository
- when invoking a helper script, pass target-repository paths explicitly

If this SKILL.md and a bundled reference document disagree on a rule, this SKILL.md wins.
References elaborate and provide examples; they do not override top-level skill rules.

Read these references when needed:

- [references/contract-authority-and-migration.md](references/contract-authority-and-migration.md) for authority boundaries, cutover rules, and core-only entrypoints
- [references/external-contract-authority.md](references/external-contract-authority.md) for external contract authority, owned subset rules, and accepted gap modeling
- [references/contract-alignment-checklist.md](references/contract-alignment-checklist.md) for planner and executor checks that keep execution aligned with declared public contracts
- [references/machine-execution-schema.md](references/machine-execution-schema.md) for the phase schema authority model
- [references/llm-friendly-phase-schema.md](references/llm-friendly-phase-schema.md) for agent-facing field-writing rules
- [references/prompt-derivation-from-schema.md](references/prompt-derivation-from-schema.md) for prompt and kickoff render rules
- [references/schema-consumption-rules.md](references/schema-consumption-rules.md) for consuming structured execution fields
- [references/wave-state-model.md](references/wave-state-model.md) for allowed wave states
- [references/wave-status-snapshot.schema.md](references/wave-status-snapshot.schema.md) for machine-readable execution status output
- [references/wave-status-snapshot.schema.json](references/wave-status-snapshot.schema.json) for machine validation of execution status snapshots
- [references/handoff-manifest.schema.md](references/handoff-manifest.schema.md) for immutable lane handoff payload rules
- [references/handoff-manifest.schema.json](references/handoff-manifest.schema.json) for machine validation of handoff manifests
- [references/phase-execution-schema-template.yaml](references/phase-execution-schema-template.yaml) for a full phase schema skeleton
- [references/phase-agent-task-template.yaml](references/phase-agent-task-template.yaml) for a single PR task template

Use these scripts from the skill bundle:

- `uv run scripts/validate_phase_execution_schema.py --plan /path/to/docs/phaseN-plan.yaml`
- `uv run scripts/validate_phase_doc_set.py --docs-dir /path/to/repo/docs --phase phaseN`
- `uv run scripts/render_agent_prompt.py --plan /path/to/docs/phaseN-plan.yaml --pr P13-10`
- `uv run scripts/render_wave_kickoff.py --plan /path/to/docs/phaseN-plan.yaml --wave 3`
- `uv run scripts/preflight_phase_execution.py --plan /path/to/docs/phaseN-plan.yaml --docs-dir /path/to/repo/docs --phase phaseN --wave 1`
- `uv run scripts/list_wave_lanes.py --plan /path/to/docs/phaseN-plan.yaml --wave 1 --json`
- `uv run scripts/render_lane_handoff.py --plan /path/to/docs/phaseN-plan.yaml --wave 1 --lane backend`
- `uv run scripts/verify_lane_handoff.py --plan /path/to/docs/phaseN-plan.yaml --handoff /tmp/wave1-backend.md --strict`
- `uv run scripts/render_wave_status_snapshot.py --plan /path/to/docs/phaseN-plan.yaml --wave 1`
- `uv run scripts/validate_handoff_manifest.py --handoff /tmp/wave1-backend.md`
- `uv run scripts/validate_wave_status_snapshot.py --snapshot /tmp/wave1-status.yaml`
- `uv run scripts/run_smoke_checks.py` — runs all validators and renderers against bundled fixture data and compares output to golden files; run after modifying any script or reference to verify contract stability

## Core Principles

1. The contract is owned here once, then consumed everywhere else.
2. `phaseN-plan.yaml` is the execution authority.
3. Markdown is narrative and coordination, not the execution source.
4. Prompts and handoffs are derived artifacts, not hand-maintained planning docs.
5. State and status vocabularies must stay stable across planning and execution.
6. Contract helpers must be deterministic and minimally inferential.
7. Do not split the contract across sibling skills or alternate entrypoint paths.

## Scope

This skill owns:

- schema field definitions
- external contract authority field semantics
- validation rules
- render rules
- lane handoff manifest rules
- wave-state definitions
- wave-status snapshot structure

This skill does not own:

- baseline discovery for a new phase
- milestone design trade-offs
- integrator operating policy
- conflict-resolution decision-making

## Reference Loading By Task

When validating a plan:
- read: external-contract-authority.md, machine-execution-schema.md, llm-friendly-phase-schema.md
- run: from the directory that contains this `SKILL.md`, `uv run scripts/validate_phase_execution_schema.py` and `uv run scripts/validate_phase_doc_set.py` with the same arguments as in **Use these scripts from the skill bundle** below

When rendering a prompt or handoff:
- read: external-contract-authority.md, prompt-derivation-from-schema.md, handoff-manifest.schema.md
- run: `uv run scripts/render_agent_prompt.py` or `uv run scripts/render_lane_handoff.py` with arguments as in **Use these scripts from the skill bundle** below

When verifying execution state:
- read: contract-alignment-checklist.md, wave-state-model.md, wave-status-snapshot.schema.md, schema-consumption-rules.md

When resolving authority questions:
- read: contract-authority-and-migration.md

Do not load all references at once. Load only the set that matches the current task.

## Guardrails

- do not add a second contract authority in `phase-plan` or `phase-execute`
- do not duplicate validators or renderers across skills
- do not let prompt wording drift from the schema-derived contract
- do not change field semantics in one skill without updating this one
- do not keep duplicate or fallback contract entrypoints outside core

## Self-Test

After modifying any contract script or reference:

- run `uv run scripts/run_smoke_checks.py`
- passing means all renderers and validators produce stable output against the bundled fixture data
- failing means a contract regression — fix the regression before committing

The smoke fixture set lives in `fixtures/smoke/`. The golden output files live in `fixtures/smoke/golden/`. If a change intentionally alters renderer output, update the golden files.

## Composition

Use this skill together with:

- `$phase-plan` to author the strict four-file phase doc set against this contract
- `$phase-plan-review` to review upstream intent alignment, plan quality, and execution readiness before wave execution begins
- `$phase-execute` to execute accepted waves by consuming this contract and its helpers
