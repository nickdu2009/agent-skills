# Design Review

Classify `artifact_subtype` as `architecture`, `adr-rfc`, `interface`,
`data-model`, or `technical-proposal`.

Check common design concerns: requirement traceability, alternatives and
trade-offs, component responsibilities, interfaces, data ownership, security,
failure behavior, compatibility, operability, rollout/rollback, and verifiable
acceptance criteria.

For schema/data migration, also check forward and backward compatibility,
mixed-version operation, backfill/validation, cutover ownership, rollback limits,
data-loss risk, and deployment order.

For ADR/RFC content, check title/context, decision drivers, realistic alternatives,
decision, positive and negative consequences, status,
relationships (`supersedes`, `superseded-by`, `amends`, or related records), and
revisit conditions. `Proposed` records are reviewable candidates, not active
constraints. Only active `Accepted` decisions constrain downstream plans.
Reviewing an ADR never authorizes persistence, promotion, or lifecycle mutation.
