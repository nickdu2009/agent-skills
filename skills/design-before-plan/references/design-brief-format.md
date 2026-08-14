# Design brief format

```yaml
requirements:
  functional: []
  non_functional: []
  implicit: # each: {item, source, status: confirmed|open|assumed, blocking: bool}
    security: []
    performance: []
    observability: []
    resilience: []
    operability: []
  edge_cases: []
alternatives: # each: {approach, pros, cons, complexity, blast_radius, reversibility}
  - {}
chosen_design:
  approach: ""
  rationale: ""
  sacrifices: []
  deferred: []
interface_contracts: # each: {boundary, input, output, errors, compatibility, owner}
  - {}
acceptance_criteria:
  must_have: []
  nice_to_have: []
  validation_boundary: []
architectural_constraints: []
data_migration:
  schema_changes: []
  compatibility: ""
  forward: ""
  rollback: ""
  validation: []
  risks: []
linked_adrs: # each: {id, artifact, status: Accepted}
  - {}
adr_candidates: # each: {id, artifact, status: Proposed}
  - {}
```

Omit optional blocks that do not apply. Only authorized behavior may enter `chosen_design` or acceptance criteria; keep every other candidate open/assumed with its source and blocking status.
