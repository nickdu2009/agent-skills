# Design brief format

Use this shape when the main skill needs a durable handoff to planning:

```yaml
requirements:
  functional: []
  non_functional: []
  implicit:
    # Candidates to check — not auto-adopted defaults.
    # Each item: { item, source, status: confirmed|open|assumed, blocking: true|false }
    security: []
    performance: []
    observability: []
    resilience: []
  edge_cases: []

design_alternatives:
  - approach: ""
    pros: []
    cons: []
    complexity: ""
    blast_radius: ""

chosen_design:
  approach: ""
  rationale: ""
  deferred: []
  # Only confirmed / explicitly authorized behaviors may appear here.
  # Unconfirmed implicit NFR candidates must stay in requirements.implicit with status open|assumed.

interface_contracts:
  - module: ""
    contract: ""
    error_handling: ""
    backward_compatibility: ""

acceptance_criteria:
  must_have: []
  nice_to_have: []
  validation_boundary: []
  # Do not promote unconfirmed timeouts, retries, fallbacks, or degradation paths into AC.

architectural_constraints: []

data_migration:
  schema_changes: []
  forward_migration: ""
  backward_migration: ""
  complexity:
    data_volume: ""
    downtime_tolerance: ""
  validation: []
  risks: ""

linked_adrs:
  - id: ""
    artifact: ""
    status: Accepted

adr_candidates:
  - id: ""
    artifact: "<inline artifact or target-repository path when explicitly written>"
    status: Proposed
```

Omit optional blocks that do not apply. Keep acceptance criteria requirement-driven and ensure every chosen trade-off is visible. Checking an implicit NFR candidate does not authorize it; only `status: confirmed` (or an active Accepted ADR / preserved compatibility contract) may enter `chosen_design` or acceptance criteria.
