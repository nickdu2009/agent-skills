# Contract Authority And Migration

Use this reference when you need to understand where the phase contract lives and how sibling skills consume it.

## Two Authority Layers

There are two different authorities:

- repository execution authority: `$PHASE_DOCS_ROOT/phaseN/plan.yaml` inside the target repository
- skill-bundle contract authority: `$phase-contract-tools` inside the skill bundle

`plan.yaml` decides the work for one repository.

`$phase-contract-tools` decides how that schema, its validators, its renderers, and its execution artifacts are defined.

Do not confuse these layers.

## Sole Contract Owner

`$phase-contract-tools` is the only skill that may define:

- execution schema field semantics
- doc-set validation rules
- prompt derivation rules
- handoff manifest rules
- wave-state vocabulary
- wave status snapshot structure

Do not fork or restate those rules in sibling skills.

## How Planning Consumes The Contract

`$phase-plan` uses `$phase-contract-tools` to:

- read the schema and field-writing rules
- validate `plan.yaml`
- validate the strict four-file doc set
- derive prompts or kickoff text from accepted schema

`$phase-plan` owns authoring and sequencing.

It does not own the contract definitions.

## How Execution Consumes The Contract

`$phase-execute` uses `$phase-contract-tools` to:

- consume structured phase fields safely
- preflight a wave before launch
- render immutable lane handoffs
- verify handoff integrity
- emit machine-readable wave status snapshots

`$phase-execute` owns orchestration and integration.

It does not own the contract definitions.

## Canonical Script Entry Points

All automation and all documentation should call:

- `phase-contract-tools/scripts/validate_phase_execution_schema.py`
- `phase-contract-tools/scripts/validate_phase_doc_set.py`
- `phase-contract-tools/scripts/render_agent_prompt.py`
- `phase-contract-tools/scripts/render_wave_kickoff.py`
- `phase-contract-tools/scripts/preflight_phase_execution.py`
- `phase-contract-tools/scripts/render_lane_handoff.py`
- `phase-contract-tools/scripts/verify_lane_handoff.py`
- `phase-contract-tools/scripts/render_wave_status_snapshot.py`

## Cutover Rule

When you see planning or execution text that points to a non-core contract asset:

1. move the canonical rule or helper into `$phase-contract-tools`
2. repoint sibling skills to the core path
3. delete the non-core entrypoint instead of preserving a fallback

## Anti-Patterns

Do not:

- define schema semantics in both planning and execution
- keep duplicate contract entrypoints under sibling skills
- add a second copy of a validator or renderer under another skill
- treat sibling skill docs as stronger than the core contract
