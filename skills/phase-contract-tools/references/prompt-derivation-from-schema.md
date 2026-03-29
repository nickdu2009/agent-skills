# Prompt Derivation From Schema

Use this reference when the user wants prompts or kickoff text derived from `phaseN-plan.yaml`.

Prompts are not primary planning docs. They are renderings of accepted schema fields.

## Inputs

Read from `phaseN-plan.yaml` only:

- `hard_rules`
- `external_contracts`
- `accepted_contract_gaps`
- `validation_profiles`
- `placeholder_conventions`
- `team`
- `prs`
- `waves`

Use Markdown only for human-facing context or cross-checking.

## Supported Render Shapes

### PR prompt

Render from `prs[]`:

- id
- title
- goal
- read_first
- start_condition
- scope.allow
- scope.deny
- files
- expected_changes
- guardrails
- required_contracts
- contract_guardrails
- non_goals
- validation
- done_when
- contract_done_when

### Lane prompt

Resolve through:

1. `waves[]`
2. `lane_setup[]`
3. `ref_kind`
4. `ref`

If `ref_kind: pr`, render the PR prompt.

If `ref_kind: role`, render from the matching `waves[].roles[]` entry.

### Wave kickoff text

Render from:

- `waves[].label`
- `waves[].goal`
- `waves[].contract_status` when present
- `waves[].lane_setup`
- `waves[].merge_order`
- `waves[].constraints`
- `waves[].integrator_checklist`

## Expansion Rules

### Validation profiles

If a validation entry starts with `profile:`, expand it through:

- `validation_profiles.<id>.description`
- `validation_profiles.<id>.command`

### Placeholder tokens

If a command contains `<token>`, include the token and its meaning from `placeholder_conventions`.

Do not silently guess a replacement value.

### External contract constraints

When a PR declares `required_contracts`:

- expand each contract id through `external_contracts[].id`
- include the contract source path and kind
- include owned subset include and exclude lists
- include matching entries from `accepted_contract_gaps`
- include `contract_guardrails`
- include `contract_done_when`

## Prompt Shape

Keep the rendered prompt bounded and executable.

Preferred order:

1. task identity
2. read first
3. start condition
4. scope
5. expected changes
6. guardrails
7. external contract constraints
8. validation
9. done condition

## Anti-Patterns

- inventing files or constraints that are not in schema
- summarizing away `scope.deny`
- hiding guardrails in prose
- omitting `done_when`
- omitting required contract constraints from a contract-bound prompt
- creating a wave prompt pack file by default
- introducing a new `phaseN-*` planning doc just to hold rendered text

## Example Invocation

```bash
uv run scripts/render_agent_prompt.py --plan docs/phase13-plan.yaml --pr P13-10
uv run scripts/render_agent_prompt.py --plan docs/phase13-plan.yaml --wave 3 --lane A
uv run scripts/render_wave_kickoff.py --plan docs/phase13-plan.yaml --wave 3
```
