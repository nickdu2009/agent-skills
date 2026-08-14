# GATE-00 contract

Use a pre-coding gate for unresolved contracts, schema, security, dependencies, external services, runtime conditions, authorization, or behavioral assumptions.

Required fields:

- `goal`
- `prerequisites`
- `owner`
- `owns`
- `must_not_touch`
- `actions`
- `expected_outputs`
- `verify`
- `done_conditions`
- `stop_escalate_conditions`
- `handoff`

For each behavioral assumption include `item`, `source`, `owner_decision`, and `done_condition`. Name exactly which implementation steps remain blocked. The gate may inspect and decide; it must not modify production code, migrations, dependencies, or external state unless separately authorized.
