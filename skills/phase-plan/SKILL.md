---
name: phase-plan
description: Design or update a structured implementation plan that breaks a large task into sequenced waves of parallel work. Use when the agent needs to create plan.yaml and supporting docs for multi-wave execution, or convert a roadmap into an executable plan with PR sequencing and wave ownership.
---

# Phase Plan

Design the phase as an execution system, not as a pile of planning prose.

The primary output is a structured execution schema:

- `$PHASE_DOCS_ROOT/phaseN/plan.yaml`

Markdown exists to help humans coordinate around that schema:

- `$PHASE_DOCS_ROOT/phaseN/roadmap.md`
- `$PHASE_DOCS_ROOT/phaseN/wave-guide.md`
- `$PHASE_DOCS_ROOT/phaseN/execution-index.md`

Unless the user or environment says otherwise, treat `PHASE_DOCS_ROOT` as the phase-doc root and default it to `docs/phases`.

The phase-doc root also owns a root summary file:

- `$PHASE_DOCS_ROOT/README.md`

Use this root README to summarize each phase at a glance. It is a coordination and navigation file, not a per-phase execution artifact and not part of any `phaseN/` strict four-file set.

Use this minimal shape by default:

```markdown
# Phase Index

## Phase Summaries

- `phaseN`: goal: one-line goal; scope: current scope boundary; status: proposed | active | blocked | done
```

## Skill Assets

Resolve bundled assets relative to the directory that contains `SKILL.md`.

- `../phase-contract-tools/references/...` are the shared contract references
- `../phase-contract-tools/scripts/...` are the shared contract helpers
- this skill does **not** ship a local `scripts/` directory; all contract helpers live under `../phase-contract-tools/scripts/` when both skills are installed side by side
- do not assume these files exist in the target repository
- when invoking a helper script, pass target-repository paths explicitly

If this SKILL.md and a bundled reference document disagree on a rule, this SKILL.md wins.
References elaborate and provide examples; they do not override top-level skill rules.

Read these shared contract references when needed:

- [`../phase-contract-tools/references/contract-authority-and-migration.md`](../phase-contract-tools/references/contract-authority-and-migration.md) for authority boundaries, cutover rules, and core-only entrypoints
- [`../phase-contract-tools/references/external-contract-authority.md`](../phase-contract-tools/references/external-contract-authority.md) for external contract authority, owned subset, excluded subset, and accepted gap rules
- [`../phase-contract-tools/references/contract-alignment-checklist.md`](../phase-contract-tools/references/contract-alignment-checklist.md) for planning checks that keep contract-bound phases aligned
- [`../phase-contract-tools/references/machine-execution-schema.md`](../phase-contract-tools/references/machine-execution-schema.md) for the execution authority model and required schema fields
- [`../phase-contract-tools/references/llm-friendly-phase-schema.md`](../phase-contract-tools/references/llm-friendly-phase-schema.md) for agent-facing instruction encoding rules
- [`../phase-contract-tools/references/phase-execution-schema-template.yaml`](../phase-contract-tools/references/phase-execution-schema-template.yaml) for a full phase schema skeleton
- [`../phase-contract-tools/references/phase-agent-task-template.yaml`](../phase-contract-tools/references/phase-agent-task-template.yaml) for a single PR task template
- [`../phase-contract-tools/references/prompt-derivation-from-schema.md`](../phase-contract-tools/references/prompt-derivation-from-schema.md) for prompt and kickoff rendering rules

Use these shared contract scripts:

- `uv run ../phase-contract-tools/scripts/validate_phase_execution_schema.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml`
- `uv run ../phase-contract-tools/scripts/validate_phase_doc_set.py --phase-root /path/to/repo/docs/phases --phase phaseN`
- `uv run ../phase-contract-tools/scripts/render_phase_root_readme.py --phase-root /path/to/repo/docs/phases --write /path/to/repo/docs/phases/README.md`
- `uv run ../phase-contract-tools/scripts/render_agent_prompt.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --pr P13-10`
- `uv run ../phase-contract-tools/scripts/render_wave_kickoff.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --wave 3`

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

1. `$PHASE_DOCS_ROOT/phaseN/roadmap.md`
2. `$PHASE_DOCS_ROOT/phaseN/plan.yaml`
3. `$PHASE_DOCS_ROOT/phaseN/wave-guide.md`
4. `$PHASE_DOCS_ROOT/phaseN/execution-index.md`
5. `$PHASE_DOCS_ROOT/README.md`

Do not create these by default:

- `phaseN-first-wave-pr-breakdown.md`
- `phaseN-parallel-matrix.md`
- `phaseN-pr-delivery-plan.md`
- `phaseN-pr-parallelization-plan.md`
- `phaseN-waveX-agent-launch-prompts.md`

Do not add extra `phaseN-*` planning docs inside `$PHASE_DOCS_ROOT/phaseN/`.

If the user wants additional handoff material, derive it from the schema at response time or through a renderer instead of creating another planning file.

If the user explicitly asks for a narrower subset, enter partial-output mode.

In partial-output mode:
- produce only the explicitly requested artifacts
- do not claim the per-phase strict four-file phase doc set is complete
- run only the validators that apply to the artifacts that were created or changed
- explicitly state which artifacts and validations were omitted

## File Responsibilities

### `$PHASE_DOCS_ROOT/phaseN/roadmap.md`

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

### `$PHASE_DOCS_ROOT/phaseN/plan.yaml`

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

### `$PHASE_DOCS_ROOT/phaseN/wave-guide.md`

Use it for:

- wave summary
- lane visibility
- merge windows
- wave constraints
- integrator checklists
- how to resolve work from `plan.yaml`

Do not restate full PR payloads here.

### `$PHASE_DOCS_ROOT/phaseN/execution-index.md`

Use it for:

- reading order
- authority order
- role-to-doc navigation
- current doc-set boundaries

### `$PHASE_DOCS_ROOT/README.md`

Use it for:

- a short summary for each phase under `$PHASE_DOCS_ROOT`
- phase-to-phase reading order at the repository level
- quick navigation into each `phaseN/` directory
- one bullet entry per phase under a shared `## Phase Summaries` section
- fixed summary fields in this order: `goal`, `scope`, `status`
- one entry per actual phase directory under `$PHASE_DOCS_ROOT`, in ascending phase order, with no duplicates

Do not use it for:

- execution authority
- wave-by-wave task payloads
- duplicated `plan.yaml` structure
- replacing any file inside the per-phase four-file set

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
- external contract authority field semantics
- agent-facing field-writing rules
- prompt derivation rules
- schema and doc-set validation helpers
- cutover rules for canonical script entrypoints

When authoring or repairing `plan.yaml`, treat these as the contract authorities:

- `../phase-contract-tools/references/contract-authority-and-migration.md`
- `../phase-contract-tools/references/external-contract-authority.md`
- `../phase-contract-tools/references/machine-execution-schema.md`
- `../phase-contract-tools/references/llm-friendly-phase-schema.md`
- `../phase-contract-tools/references/prompt-derivation-from-schema.md`

Do not define a parallel contract inside `phase-plan`.

## Reference Loading By Task

When authoring a new phase:
- read: external-contract-authority.md, machine-execution-schema.md, llm-friendly-phase-schema.md, phase-execution-schema-template.yaml, phase-agent-task-template.yaml
- run: from the directory that contains this `SKILL.md`, `uv run ../phase-contract-tools/scripts/render_phase_root_readme.py`, `uv run ../phase-contract-tools/scripts/validate_phase_execution_schema.py`, and `uv run ../phase-contract-tools/scripts/validate_phase_doc_set.py` with the same arguments as in **Use these shared contract scripts** (after authoring)

When repairing an existing plan:
- read: external-contract-authority.md, machine-execution-schema.md, llm-friendly-phase-schema.md
- run: `uv run ../phase-contract-tools/scripts/validate_phase_execution_schema.py --plan ...` to see current errors, then refresh `$PHASE_DOCS_ROOT/README.md` if goal, scope, or status changed

When deriving prompts:
- read: prompt-derivation-from-schema.md
- run: `uv run ../phase-contract-tools/scripts/render_agent_prompt.py` or `uv run ../phase-contract-tools/scripts/render_wave_kickoff.py` with arguments as in **Use these shared contract scripts**

Do not load all references at once. Load only the set that matches the current task.

## Workflow

Before following the default workflow, determine whether the task is:
- full-doc-set authoring
- partial-output mode

If partial-output mode is requested, execute only the steps relevant to the requested artifacts and explicitly skip the others.

Follow this order:

1. Read the current code baseline and accepted planning inputs.
2. Identify any external contract authority named by the user, repo inputs, or accepted design docs.
3. Freeze the authority matrix: execution authority, external contract authority, owned subset, and excluded subset.
4. Freeze scope, non-goals, and milestones in `$PHASE_DOCS_ROOT/phaseN/roadmap.md`.
5. Encode execution structure and any contract-bound fields in `$PHASE_DOCS_ROOT/phaseN/plan.yaml`.
6. Build the human coordination view in `$PHASE_DOCS_ROOT/phaseN/wave-guide.md`.
7. Build the reading order and authority view in `$PHASE_DOCS_ROOT/phaseN/execution-index.md`.
8. Add or refresh `$PHASE_DOCS_ROOT/README.md`: append a new phase entry when a new phase is created, and refresh the existing entry when the phase goal, scope, or status changes. Prefer `uv run ../phase-contract-tools/scripts/render_phase_root_readme.py --phase-root ... --write ...` over hand-editing.
9. Validate the schema: `uv run ../phase-contract-tools/scripts/validate_phase_execution_schema.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml`.
10. Validate the doc set: `uv run ../phase-contract-tools/scripts/validate_phase_doc_set.py --phase-root /path/to/repo/docs/phases --phase phaseN`.
11. Derive prompts or kickoff text from the schema only through `uv run ../phase-contract-tools/scripts/render_agent_prompt.py` or `uv run ../phase-contract-tools/scripts/render_wave_kickoff.py` when needed (see **Use these shared contract scripts** for placeholders).

Do not start by drafting prompt text.

## Validation Requirements

Run both validators for a non-trivial full-doc-set phase.

For partial-output mode:
- run schema validation if `$PHASE_DOCS_ROOT/phaseN/plan.yaml` was created or changed
- run doc-set validation only when the root README plus the full per-phase strict four-file set are being delivered
- if a validator is skipped, state why

Schema validation:

- `uv run ../phase-contract-tools/scripts/validate_phase_execution_schema.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml`

Doc-set validation:

- `uv run ../phase-contract-tools/scripts/validate_phase_doc_set.py --phase-root /path/to/repo/docs/phases --phase phaseN`

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
- Do not add any extra phase planning docs inside `$PHASE_DOCS_ROOT/phaseN/` beyond the strict four-file set.
- Do not use legacy route shapes or DTOs as temporary substitutes when they conflict with the declared external contract.
- Do not leave a contract-bound PR with only repo-local `done_when`; add `required_contracts`, `contract_guardrails`, and `contract_done_when`.
- Do not leave validation as "run tests" when you can name the package, suite, or profile.
- Do not use vague execution language such as `as needed`, `if needed`, or `make sure`.
- Do not let `read_first` drift into undeclared phase-local files outside the strict four-file set inside `$PHASE_DOCS_ROOT/phaseN/`.
- Do not store document path and section hint in one `read_first` string.
- Do not store profile refs and shell commands as raw validation strings.

## Done Criteria

The following done criteria apply to a full-doc-set planning pass.

The planning pass is done only when:

- the baseline matches observable code reality
- any external contract authority is identified or explicitly marked not applicable
- the roadmap freezes scope and non-goals clearly
- the YAML schema is complete and internally consistent
- contract-bound PRs declare `required_contracts`, `contract_guardrails`, and `contract_done_when`
- the wave guide is sufficient for human coordination without duplicating YAML
- the execution index states reading order and authority clearly
- the root README gives a concise summary for each phase under `$PHASE_DOCS_ROOT`
- prompts can be derived from the schema without hand-maintained prompt docs
- validators pass or any accepted warning is explicitly explained

For partial-output mode, the task is done only when:
- the requested artifacts are internally consistent
- any applicable validators pass
- omitted artifacts and skipped validators are explicitly called out
- if the per-phase strict four-file set is incomplete after this pass, state that execution via `$phase-execute` requires completing the remaining artifacts

## Composition

Use this skill together with:

- `$phase-contract-tools` for the sole schema, validator, renderer, handoff, and cutover contract
- `$phase-plan-review` when the accepted doc set should be independently reviewed before execution begins
- `$phase-execute` after the accepted doc set exists and execution can consume the contract-defined artifacts

# Common Anti-Patterns

- **Markdown owns execution authority.** The agent encodes all PR tasks, lane ownership, and validation rules in prose-heavy `wave-guide.md` paragraphs instead of structured YAML fields. When `phase-execute` tries to consume the plan, it cannot derive lane instructions because the execution authority is scattered across unstructured text.
- **Duplicating task payloads across files.** The agent copies full PR descriptions into both `plan.yaml` and `wave-guide.md`, inflating the doc set and creating maintenance drift. When a scope change happens, only one file gets updated, leaving conflicting instructions.

See skill-anti-pattern-template.md for format guidelines.

## Artifact Contract

### Preconditions

- The task is large enough to require sequenced waves or multi-PR coordination.
- The baseline, scope, and current constraints can be grounded in repository reality.
- `phase-contract-tools` remains the sole contract authority for schema and validator semantics.

### Produced Artifacts

- `status: completed` includes `plan_artifacts`, `waves`, `gates`, and `ownership`.
- The default artifact set is the strict four-file phase doc set plus the phase-root `README.md`.
- `waves` describe wave ids, lane or PR grouping, dependency order, and merge structure.

### Invariants

- `plan.yaml` remains the execution authority.
- Extra phase-local planning files are not introduced.
- Ownership, PR order, and validation profiles are encoded in schema-owned fields, not hidden in prose.

## Gate Contract

- The planning pass is only ready for review when the required artifact set exists or partial-output mode is explicitly declared.
- Schema validation and doc-set validation are required for the full-doc-set path.
- Any skipped validator must be explained together with the residual risk.

## Failure Handling

### Common Failure Causes

- The baseline is stale or inconsistent with current code reality.
- External contract authority is unresolved, making the plan structurally incomplete.
- Validators fail because schema or doc-set fields are missing or contradictory.

### Retry Policy

- Allow one focused repair pass after validator or baseline issues are identified.
- If the plan still cannot satisfy the contract after the second pass, stop and report the blocking gap instead of emitting partial authority claims.

### Fallback

- Use partial-output mode only when the user explicitly asks for a subset.
- Hand contract questions to `phase-contract-tools`.
- Hand acceptance review to `phase-plan-review` before execution starts.

## Output Example

### V1 Format (verbose)

```yaml
[skill-output: phase-plan]
status: completed
confidence: high
outputs:
  plan_artifacts:
    - "docs/phases/phase1/plan.yaml"
    - "docs/phases/phase1/roadmap.md"
    - "docs/phases/phase1/wave-guide.md"
    - "docs/phases/phase1/execution-index.md"
  waves:
    - "wave1: schema migration (3 PRs, serial)"
    - "wave2: service layer (4 PRs, parallel lanes)"
  gates:
    - "wave1 complete before wave2 starts"
    - "schema validators pass before service implementation"
  ownership:
    - "wave1: backend-team"
    - "wave2: service-team"
signals:
  validation_passed: true
recommendations:
  next_step: "hand off to phase-plan-review"
[/skill-output]
```

### V2 Format (compact)

```
[output: phase-plan | completed high | plan_artifacts:"docs/phases/phase1/plan.yaml, roadmap.md, wave-guide.md, execution-index.md" waves:"wave1: schema migration (3 PRs, serial) → wave2: service layer (4 PRs, parallel lanes)" gates:"wave1 complete before wave2 starts, schema validators pass before service implementation" ownership:"wave1: backend-team, wave2: service-team" | next:phase-plan-review]
```

## Lifecycle

- Activate while authoring or repairing the accepted phase artifact set.
- Deactivate once the artifact set has been handed to `phase-plan-review` or the user accepts the plan.
- Deactivate immediately if the work escalates into direct maintenance of contract tools rather than phase authoring.
