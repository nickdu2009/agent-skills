# Contract Alignment Checklist

Use this checklist when planning or executing work that depends on an external contract.

## Planner Checks

Before freezing a phase:

- identify the external contract authority
- declare the owned subset and any excluded subset
- encode contract-facing PRs with `required_contracts`
- add `contract_guardrails` that forbid legacy substitutions
- add `contract_done_when` that proves alignment with the owned subset
- record any accepted gap explicitly under `accepted_contract_gaps`

## Executor Checks

Before launching a wave:

- list the wave's `required_contracts`
- confirm each required contract exists in `external_contracts`
- confirm owned subset boundaries are present
- confirm no blocking accepted gap blocks this wave
- confirm lane prompts include contract guardrails and contract done checks

## Completion Checks

Before reporting a wave complete:

- repo-local done checks passed
- contract-level done checks passed
- no blocking contract gap remains for the wave
- any accepted gap is reported explicitly
- wave status distinguishes execution progress from contract alignment status

## Escalate Back To Planning When

- external contract authority is unclear
- owned subset is unclear
- the implementation would require a legacy public shape that conflicts with the declared contract
- the phase encodes repo-safe behavior but not contract-complete behavior
