---
name: phase-contract-tools
description: Maintain phase system infrastructure. Use ONLY when (1) task explicitly mentions "fix phase schema validator", "update plan.yaml contract", or "repair phase rendering", (2) working on phase-contract-tools directory itself, or (3) validating phase plan format. Do NOT use for regular phase planning or execution.
---

# Phase Contract Tools

Use this skill as the shared tools layer for schema-first phase work.

`$PHASE_DOCS_ROOT/phaseN/plan.yaml` is the execution authority inside a repository.

Unless the user or environment says otherwise, treat `PHASE_DOCS_ROOT` as the phase-doc root and default it to `docs/phases`.

`$phase-contract-tools` is the only skill-bundle authority for schema semantics, validators, renderers, handoff contracts, and status snapshot structure.

It owns the stable contract for:

- `$PHASE_DOCS_ROOT/phaseN/plan.yaml`
- external contract authority declarations consumed through `plan.yaml`
- the per-phase strict four-file doc set under `$PHASE_DOCS_ROOT/phaseN/`
- the phase-root summary file `$PHASE_DOCS_ROOT/README.md`
- prompt derivation from schema
- wave lane handoff artifacts
- wave-state vocabulary
- wave status snapshots

`$phase-plan` should use this skill to design and validate phases.

`$phase-execute` should use this skill to consume, render, verify, and report execution state.

## External Contract Authority

`$PHASE_DOCS_ROOT/phaseN/plan.yaml` is the execution authority inside the repository.

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

- `uv run scripts/validate_phase_execution_schema.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml`
- `uv run scripts/validate_phase_doc_set.py --phase-root /path/to/repo/docs/phases --phase phaseN`
- `uv run scripts/render_phase_root_readme.py --phase-root /path/to/repo/docs/phases --write /path/to/repo/docs/phases/README.md`
- `uv run scripts/render_agent_prompt.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --pr P13-10`
- `uv run scripts/render_wave_kickoff.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --wave 3`
- `uv run scripts/preflight_phase_execution.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --phase-root /path/to/repo/docs/phases --phase phaseN --wave 1`
- `uv run scripts/list_wave_lanes.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --wave 1 --json`
- `uv run scripts/render_lane_handoff.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --wave 1 --lane backend`
- `uv run scripts/verify_lane_handoff.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --handoff /tmp/wave1-backend.md --strict`
- `uv run scripts/render_wave_status_snapshot.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --wave 1`
- `uv run scripts/validate_handoff_manifest.py --handoff /tmp/wave1-backend.md`
- `uv run scripts/validate_wave_status_snapshot.py --snapshot /tmp/wave1-status.yaml`
- `uv run scripts/migrate_phase_docs.py --source /path/to/repo/docs --target /path/to/repo/docs/phases --dry-run` — moves canonical files to `phaseN/` and extra `phaseN-*` docs to `phaseN/legacy/`
- `uv run scripts/run_smoke_checks.py` — runs all validators and renderers against bundled fixture data and compares output to golden files; run after modifying any script or reference to verify contract stability

## Core Principles

1. The contract is owned here once, then consumed everywhere else.
2. `plan.yaml` is the execution authority.
3. Markdown is narrative and coordination, not the execution source.
4. Prompts and handoffs are derived artifacts, not hand-maintained planning docs.
5. State and status vocabularies must stay stable across planning and execution.
6. Contract helpers must be deterministic and minimally inferential.
7. Do not split the contract across sibling skills or alternate entrypoint paths.

`$PHASE_DOCS_ROOT/README.md` is a phase-root navigation and summary file. It is required by the contract, but it is not part of any per-phase four-file execution set and it never overrides `plan.yaml`.

The default README contract is intentionally lightweight:

- a top-level heading such as `# Phase Index`
- a `## Phase Summaries` section
- one bullet per phase in the form `- `phaseN`: goal: ...; scope: ...; status: ...`
- the summary fields must appear in that order so validators can check them deterministically
- `status` must be one of `proposed`, `active`, `blocked`, or `done`
- the README must cover all actual phase directories under `$PHASE_DOCS_ROOT` in ascending phase order with no duplicates or unknown phase ids
- prefer `render_phase_root_readme.py` to refresh this file instead of hand-maintaining it

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

When rendering or refreshing the phase-root README:
- read: machine-execution-schema.md, contract-authority-and-migration.md
- run: `uv run scripts/render_phase_root_readme.py --phase-root ... --write ...`

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

- `$phase-plan` to author the per-phase strict four-file phase doc set plus the phase-root README against this contract
- `$phase-plan-review` to review upstream intent alignment, plan quality, and execution readiness before wave execution begins
- `$phase-execute` to execute accepted waves by consuming this contract and its helpers

# Common Anti-Patterns

- **Defining parallel contract rules.** The agent authoring a phase adds custom execution field semantics inside `phase-plan/SKILL.md` instead of using the contract definitions in `phase-contract-tools`. When `phase-execute` tries to consume the plan, it encounters undocumented fields that violate the shared contract, breaking validation and rendering.
- **Hand-maintaining derived artifacts.** The agent manually writes lane handoff prompts or wave kickoff summaries as standalone planning files instead of deriving them from `plan.yaml` using the contract scripts. When the schema changes, the hand-written files become stale and conflict with the authoritative execution surface.

See skill-anti-pattern-template.md for format guidelines.

## Artifact Contract

### Preconditions

- The task is about schema semantics, validators, renderers, handoff contracts, or phase contract stability.
- Contract authority remains centralized in this skill and its bundled references/scripts.
- Target repository paths can be passed explicitly to helpers.

### Outputs

- `status: completed` includes `schema_checks`, `rendered_views`, and `contract_issues`.
- Schema checks identify which validator or contract rule passed or failed.
- Rendered outputs stay derivable from schema-owned fields rather than hand-maintained prose.

### Invariants

- This skill is the sole contract authority for phase schema semantics and helper behavior.
- Sibling skills do not redefine field meanings locally.
- Helper outputs stay deterministic enough for smoke testing and golden comparisons.

## Gate Contract

- Contract changes are only acceptable when validators and smoke checks remain coherent.
- A failing validator, renderer, or smoke check is a blocking contract issue until repaired or explicitly accepted.
- Downstream phase skills may consume outputs only after the relevant contract issue is cleared.

## Failure Handling

### Common Failure Causes

- A schema or renderer change breaks bundled smoke fixtures.
- Contract rules drift between this skill and sibling phase skills.
- A direct phase task tries to use this skill as a planning or execution substitute.

### Retry Policy

- Allow one focused repair pass after a failing validator or smoke check.
- If contract stability still fails after that pass, stop and report the exact contract issue rather than broadening unrelated scope.

### Fallback

- Hand phase authoring back to `phase-plan`.
- Hand execution back to `phase-execute`.
- Use repository-local smoke and validator evidence to justify any accepted contract change.

## Output Example

### V1 Format (verbose)

```yaml
[skill-output: phase-contract-tools]
status: completed
confidence: high
outputs:
  schema_checks:
    - "plan.yaml validates against schema v2.1"
    - "wave dependencies are acyclic"
  rendered_views:
    - "execution-index.md rendered from plan.yaml"
    - "wave-guide.md synchronized with wave definitions"
  contract_issues: []
signals:
  validators_passed: true
recommendations:
  next_step: "contract validation complete, return to phase-plan"
[/skill-output]
```

### V2 Format (compact)

```
[output: phase-contract-tools | completed high | schema_checks:"plan.yaml validates against schema v2.1, wave dependencies are acyclic" rendered_views:"execution-index.md rendered from plan.yaml, wave-guide.md synchronized with wave definitions" contract_issues:"none" | next:phase-plan]
```

## Lifecycle

- Activate when maintaining contract scripts, schema references, or renderers directly.
- Activate alongside one primary phase skill only when that phase skill needs contract validation or rendering support.
- Deactivate once contract issues have been consumed by the requesting phase skill or the direct tools-maintenance task is complete.
