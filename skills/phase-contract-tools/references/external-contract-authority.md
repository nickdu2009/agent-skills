# External Contract Authority

Use this reference when a phase touches a public API, webhook, protocol, schema file, or any user-named external spec.

## Core Model

`plan.yaml` remains the execution authority inside the repository.

External contract authority is separate:

- it defines the public contract that implementation must align to
- it may come from OpenAPI, YAML, JSON Schema, protocol docs, PDFs, or a user-named spec
- it cannot be replaced by legacy repository shapes just because those shapes are easier to ship

Execution can narrow work to an owned subset. Execution cannot redefine the target public contract.

## Required Concepts

### `external_contracts`

Declare each contract explicitly:

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
```

Rules:

- `id` must be stable and unique
- `path` must point to the contract source
- `kind` should describe the contract source type
- `authority` stays `external_contract`
- `owned_scope.mode` should be `subset` or `full`
- `owned_scope.include` lists the owned contract surface
- `owned_scope.exclude` lists known out-of-scope surface

### `accepted_contract_gaps`

Use accepted gaps only when misalignment is intentional and explicit:

```yaml
accepted_contract_gaps:
  - id: "gap-webhook-signature"
    contract: "contract_api"
    scope: "POST /v1/webhooks"
    reason: "signature rollout is blocked on the upstream gateway"
    blocking: false
    accepted_by: "product"
```

Rules:

- gaps must name the contract they belong to
- gaps must describe the affected scope
- `blocking: true` means execution is not contract-complete
- accepted gaps are not a license to omit contract checks from prompts or status

## PR-Level Contract Fields

Use these when a PR must stay aligned with an external contract:

```yaml
required_contracts:
  - "contract_api"
contract_guardrails:
  - "Do not substitute legacy route shapes."
contract_done_when:
  - "Generated routes align with the owned spec paths."
```

Rules:

- `required_contracts` names the contract ids this PR depends on
- `contract_guardrails` describes forbidden substitutions and invariants
- `contract_done_when` describes contract-level completion checks, not just repo-local readiness

If a PR declares `required_contracts`, it must also declare `contract_guardrails` and `contract_done_when`.

## Completion Semantics

These states do not imply contract completion by themselves:

- compile passes
- adapter registers
- direct-call scans are clean
- fail-closed behavior hides an unavailable dependency

Contract completion means the owned subset remains aligned with the declared external contract, or any remaining gap is explicitly accepted.

## Anti-Patterns

Do not:

- treat `plan.yaml` as the source of truth for public contract semantics
- reuse legacy DTOs or route shapes when they do not match the declared contract
- mark `adapter unavailable` as a completion state
- hide contract gaps inside prose instead of `accepted_contract_gaps`
