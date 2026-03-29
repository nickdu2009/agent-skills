# LLM-Friendly Phase Schema

Use this reference when writing agent-facing schema fields.

The goal is not to sound polished. The goal is to make execution reliable.

## Writing Rules

- Prefer one instruction per bullet.
- Keep one obligation per bullet.
- Prefer short, direct sentences.
- Prefer explicit nouns over pronouns.
- Prefer exact files, packages, commands, and IDs over general phrasing.
- Put hard limits in `guardrails`, not in narrative text.
- Put external contract authority in `external_contracts`, not in roadmap prose alone.
- Put excluded work in `non_goals` or `scope.deny`.
- Put runnable checks in `validation`.
- Put completion checks in `done_when`.
- Put contract completion checks in `contract_done_when`.
- Keep `read_first` ordered.
- Keep phase-local `read_first` references inside the four-file phase set.
- Make `start_condition` resolve to a concrete gate, not a mood.
- Make `done_when` name both the changed state and the validation state.

## Banned Phrases

Do not use these in execution-critical fields:

These bans apply to `goal`, `guardrails`, `non_goals`, `done_when`, `expected_changes`, `start_condition.note`, `scope.allow`, and `scope.deny`.

- `as needed`
- `if needed`
- `where appropriate`
- `related`
- `relevant`
- `etc`
- `and so on`
- `be careful`
- `make sure`
- `improve things`
- `clean up`
- `looks good`
- `when ready`

## Field-by-Field Guidance

### `goal`

Use one sentence that describes the outcome.

Good:

```yaml
goal: "Implement explicit config loading with file, env, and flag precedence."
```

Bad:

```yaml
goal: "Improve the bootstrap situation and make config better."
```

### `start_condition`

Make the gate concrete.

Good:

```yaml
start_condition:
  gate: "after_prs"
  refs: ["P13-09"]
  note: "start only after the foundation gate lands"
```

Bad:

```yaml
start_condition: "start when the foundation is ready"
```

Bad:

```yaml
start_condition: "start when ready"
```

### `scope.allow`

List what the agent may touch.

Good:

```yaml
scope:
  allow:
    - "cmd/codexlite/*"
    - "internal/codexlite/config/*"
```

### `scope.deny`

List what the agent must not touch.

Good:

```yaml
scope:
  deny:
    - "pkg/runtime/* semantics"
    - "pkg/store/*"
```

### `guardrails`

Use these for invariants, compatibility rules, or ownership limits.

Good:

```yaml
guardrails:
  - "Do not change public runtime interfaces."
  - "Do not change replay or persistence semantics."
```

Bad:

```yaml
notes: "Be careful and preserve behavior."
```

### `required_contracts`

Use contract ids only.

Good:

```yaml
required_contracts:
  - "contract_api"
```

Bad:

```yaml
required_contracts:
  - "the external webhook spec"
```

### `contract_guardrails`

Use these for forbidden substitutions against the public contract.

Good:

```yaml
contract_guardrails:
  - "Do not substitute legacy webhook field names."
  - "Do not reuse the legacy DTO unless it matches the owned spec fields."
```

### `contract_done_when`

Use these for contract-level completion checks.

Good:

```yaml
contract_done_when:
  - "The owned webhook payload matches the declared spec fields."
  - "No blocking contract gap remains for this PR."
```

### `validation`

Write structured validation entries only.

Good:

```yaml
validation:
  - kind: "profile"
    ref: "runtime_store_smoke"
  - kind: "command"
    command: "go test ./pkg/runtime/..."
```

Bad:

```yaml
validation:
  - "run tests if needed"
```

### `done_when`

Make the stop condition testable.

Good:

```yaml
done_when:
  - "Config precedence is explicit."
  - "Bootstrap tests pass."
  - "Provider scope is unchanged."
```

Bad:

```yaml
done_when: "Looks good."
```

Good:

```yaml
done_when:
  - "Config precedence is explicit."
  - "Bootstrap tests pass."
```

## `read_first`

Keep this list short, ordered, and phase-safe.

Good:

```yaml
read_first:
  - path: "docs/phaseN-roadmap.md"
    section: "M3 section"
  - path: "docs/phaseN-wave-guide.md"
    section: "Wave 3 section"
```

Bad:

```yaml
read_first:
  - path: "docs/phaseN-random-note.md"
  - "anything relevant"
```

## Good vs Bad Task Card

Bad:

```yaml
- id: "P13-06"
  notes: "Refactor runtime and update related tests as needed while preserving behavior."
```

Good:

```yaml
- id: "P13-06"
  goal: "Extract remaining concentrated responsibilities from runtime.go."
  start_condition:
    gate: "after_waves"
    refs: [1]
  read_first:
    - path: "docs/phaseN-roadmap.md"
      section: "M1 section"
  scope:
    allow:
      - "pkg/runtime/*"
    deny:
      - "pkg/store/*"
  guardrails:
    - "Structural hardening only."
    - "Do not change replay or interrupt semantics."
  validation:
    - kind: "command"
      command: "go test ./pkg/runtime/..."
  done_when:
    - "Runtime responsibilities are narrower."
    - "Runtime tests pass."
```

## Common Failure Modes

- Hiding critical rules in long prose paragraphs
- Using "related", "necessary", or "appropriate" without naming the thing
- Using phase-local doc references outside the strict four-file set
- Using free-form `read_first` strings instead of structured doc refs
- Using free-form validation strings instead of structured entries
- Mixing future work and current work in one field
- Using titles to carry data that should have its own field
- Leaving lane ownership implicit

## Prompt Derivation Rule

Anything needed by a renderer should live in a named field.

If a prompt renderer has to guess:

- what files are owned
- what start gate applies
- what must be avoided
- what counts as done

then the schema is under-specified.
