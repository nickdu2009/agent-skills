# Schema Consumption Rules

Use this reference when executing a wave directly from `phaseN-plan.yaml`.

## Authority

Consume execution data from YAML first.

- use Markdown to navigate and explain
- use YAML to decide
- if Markdown and YAML disagree on execution fields, YAML wins

## Resolve The Wave

For the selected wave, read at least:

- `id`
- `label`
- `goal`
- `control_pr`
- `prs`
- `merge_order`
- `lane_setup`
- `constraints`
- `integrator_checklist`

Do not infer missing lane metadata from narrative prose when the schema should provide it.

## Lane Resolution

Each lane reference must be typed:

- `ref_kind: pr` with `ref: <pr-id>`
- `ref_kind: role` with `ref: <wave-role-id>`

When `ref_kind: pr`, load the referenced PR entry and consume its execution fields directly.

Do not treat `ref` as a free-form label.

## Read First

`read_first` is an ordered list of mappings:

- `path`
- `section`

Rules:

- preserve list order
- read only the minimum entries needed to start safely
- prefer entries inside the strict phase doc set unless the PR explicitly requires code paths or tests
- do not collapse path and section into one sentence

## Start Condition

`start_condition` is a mapping:

- `gate`
- `refs`
- `note`

Interpret it exactly:

- `gate: immediate` means no dependency gate
- `gate: after_prs` means all referenced PR ids must be complete
- `gate: after_waves` means all referenced wave ids must be complete

`note` may narrow the gate. It does not change the gate type.

## Validation

`validation` is an ordered list of mappings:

- `kind: profile` with `ref`
- `kind: command` with `command`

Rules:

- preserve order
- resolve every profile through `validation_profiles`
- do not merge multiple entries into one prose sentence
- do not invent substitute commands when a profile exists

## Done When

`done_when` is a list of atomic completion checks.

Use it as the lane acceptance contract:

- artifact state is complete
- declared validation passed
- no out-of-scope work was required

Do not replace the checklist with one summary sentence like "feature is complete."

## Derived Lane Instruction Block

When a renderer is unavailable, derive a lane instruction block in this order:

1. lane identity and goal
2. `read_first`
3. `start_condition`
4. allowed scope and denied scope
5. owned files or packages
6. expected changes
7. guardrails
8. non-goals
9. validation
10. `done_when`

Pass that block to the worker unchanged.

## Anti-Patterns

Do not:

- paraphrase schema fields before delegation
- launch a lane with an unresolved typed reference
- treat `note` fields as a license to widen scope
- derive lane readiness from memory instead of objective state

For orchestration-level violations such as stale handoffs, validation substitution, or chat-memory drift, follow the execution skill's instruction-following discipline.
