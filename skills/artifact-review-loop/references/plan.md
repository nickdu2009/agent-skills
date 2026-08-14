# Plan Review

Use for implementation plans, migration plans, task sequences, roadmaps, and
`实施方案`.

Check:

- prerequisites and GATE decisions precede dependent work
- steps are ordered, bounded, file- or component-grounded, and independently
  verifiable
- ownership, shared write surfaces, rollback, stop conditions, and integration
  sequencing are explicit
- each step traces to confirmed requirements and design
- active `Accepted` ADRs are cited where they constrain a step
- `Proposed`, superseded, inactive, or ambiguous ADRs are excluded as constraints
- schema migration steps cover expand/migrate/verify/contract ordering and
  mixed-version safety
- unconfirmed retry, fallback, threshold, matching, or failure semantics remain
  blocking decisions rather than ordinary assumptions

Do not introduce new architecture decisions while reviewing a plan.
