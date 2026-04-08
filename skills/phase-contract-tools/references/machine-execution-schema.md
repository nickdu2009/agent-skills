# Machine Execution Schema

Use this reference when you need the schema contract for `$PHASE_DOCS_ROOT/phaseN/plan.yaml`.

## Purpose

`plan.yaml` is the execution authority for a phase.

It should contain the machine-readable facts that agents need in order to execute work with minimal inference:

- who owns each task
- what can start now
- what must wait
- what files or areas are in scope
- what must not change
- how validation expands
- when a task is done

In the strict model, execution accuracy wins over prose flexibility:

- use only the four standard phase files for phase-local doc references
- keep every execution-critical string specific enough that a validator can reject vague language

Markdown docs exist around the schema, not above it.

When a phase depends on a public API, webhook, or user-named spec, `plan.yaml` must also carry the external contract authority metadata needed to keep execution aligned with that spec.

## Authority Model

Use this order:

1. `plan.yaml` owns execution fields
2. `wave-guide.md` owns human wave coordination
3. `roadmap.md` owns milestone narrative and baseline
4. `execution-index.md` owns reading order and authority explanation

If markdown and YAML disagree on task ownership, refs, validation, or wave membership, repair the docs and keep YAML as the source of execution truth.

## Default Doc Set

The standard phase set is:

1. `$PHASE_DOCS_ROOT/phaseN/roadmap.md`
2. `$PHASE_DOCS_ROOT/phaseN/plan.yaml`
3. `$PHASE_DOCS_ROOT/phaseN/wave-guide.md`
4. `$PHASE_DOCS_ROOT/phaseN/execution-index.md`

The phase-doc root also carries:

- `$PHASE_DOCS_ROOT/README.md` as the repository-level phase index

This root README is validator-covered but it is not part of the per-phase strict four-file execution set.

Do not add extra `phaseN-*` planning docs in the strict model.

If more text is needed for humans, derive it from the schema or answer inline instead of adding another phase artifact.

## Required Top-Level Fields

Use this structure:

```yaml
schema_version: "2.0"
last_updated: "2026-03-27"
status: proposed
scope: "Machine-first execution source for Phase N."

hard_rules: []
schema_conventions: {}
placeholder_conventions: {}
validation_profiles: {}
external_contracts: []
accepted_contract_gaps: []
team: []
hotspots: []
prs: []
waves: []
```

`external_contracts` and `accepted_contract_gaps` are optional for phases with no external contract surface. They become required in practice when the phase touches a declared public contract surface.

## External Contract Fields

Use this structure when external contract authority exists:

```yaml
external_contracts:
  - id: "contract_api"
    path: "specs/public-api.yaml"
    kind: "openapi"
    authority: "external_contract"
    owned_scope:
      mode: "subset"
      include:
        - "paths./v1/widgets"
      exclude:
        - "paths owned by another service"

accepted_contract_gaps:
  - id: "gap-webhook-signature"
    contract: "contract_api"
    scope: "POST /v1/webhooks"
    reason: "signature rollout is blocked on the upstream gateway"
    blocking: false
    accepted_by: "product"
```

## PR Card Contract

Each `prs[]` entry should include:

```yaml
- id: "P13-10"
  title: "CodexLite Config Loader and Bootstrap Profiles v1"
  milestone: "M3"
  type: "implementation"
  owner: "agent_c"
  wave: 3
  depends_on: ["P13-09"]
  goal: "Implement explicit config loading."
  read_first:
    - path: "phases/phaseN/roadmap.md"
      section: "M3 section"
  start_condition:
    gate: "after_prs"
    refs: ["P13-09"]
    note: "start only after the foundation gate lands"
  scope:
    allow: []
    deny: []
  files: []
  expected_changes: []
  guardrails: []
  required_contracts: []
  contract_guardrails: []
  non_goals: []
  validation:
    - kind: "profile"
      ref: "bootstrap_smoke"
  done_when:
    - "Config loading is explicit."
    - "Bootstrap profiles are accepted."
  contract_done_when: []
```

Execution accuracy rules for PR cards:

- `read_first` must stay ordered
- phase-local `read_first` references must point only to roadmap, plan.yaml, wave-guide, or execution-index
- `read_first` entries must be structured mappings with `path` and optional `section`
- `validation` entries must be structured mappings with `kind`
- `start_condition` must be a mapping with `gate`, `refs`, and optional `note`
- `done_when` must be a list of concrete completion checks
- when `required_contracts` is non-empty, `contract_guardrails` and `contract_done_when` must also be non-empty lists
- `goal`, `start_condition.note`, `guardrails`, `non_goals`, and `done_when` items must avoid vague phrases such as `as needed` or `when ready`

## Wave Contract

Each `waves[]` entry should include:

```yaml
- id: 3
  label: "Wave 3"
  goal: "CodexLite deployment bootstrap"
  control_pr: "P13-11"
  prs: ["P13-10", "P13-11"]
  merge_order:
    - ["P13-10"]
    - ["P13-11"]
  lane_setup:
    - lane: "A"
      owner: "agent_c"
      ref_kind: "pr"
      ref: "P13-10"
  roles: []           # optional; required only when lane_setup uses ref_kind: role
  constraints: []
  integrator_checklist: []
```

## Typed References

Every lane reference must be typed:

```yaml
lane_setup:
  - lane: "A"
    owner: "agent_a"
    ref_kind: "pr"
    ref: "P13-06"
  - lane: "Integrator"
    owner: "integrator"
    ref_kind: "role"
    ref: "wave3_shared_seam_review"
```

Do not use a free-form field like:

```yaml
lane_setup:
  - lane: "A"
    task: "P13-06"
```

## Validation Model

Use `validation_profiles` for repeated commands and `validation` for task-level checks.

Example:

```yaml
validation_profiles:
  runtime_store_smoke:
    description: "Foundation smoke covering runtime and store seams."
    command: "go test ./pkg/runtime/... ./pkg/store/..."

prs:
  - id: "P13-06"
    validation:
      - kind: "profile"
        ref: "runtime_store_smoke"
      - kind: "command"
        command: "go test ./pkg/runtime/..."
```

If a command contains a placeholder token such as `<suite-dir>` or `<report.json>`, declare that token under `placeholder_conventions`.

## Merge Semantics

- `waves[].prs` declares the full wave membership
- `waves[].merge_order` declares ordered batches
- tasks inside one merge-order batch may proceed in parallel
- later batches wait for earlier batches to finish
- `control_pr` must exist and belong to the same wave

## Anti-Patterns

- Putting PR payloads into `wave-guide.md`
- Using prose to describe dependencies that should be in `depends_on`
- Encoding refs indirectly in titles or notes
- Mixing goal, scope, validation, and stop conditions in one paragraph
- Hand-authoring prompt docs that drift from YAML
- Treating repo-local completion as proof of public contract alignment
