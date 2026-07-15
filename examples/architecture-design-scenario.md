# Architecture Design Scenario

## Task

Design a notification subsystem with a dispatcher, email/in-app/enterprise-message adapters, preference storage, and room for future SMS support.

## Expected flow

1. Classify the work as subsystem-level.
2. Clarify ownership, expected volume, reliability, data sensitivity, and deployment constraints.
3. Compare direct channel integration with an independent service plus queue.
4. Define component responsibilities, data ownership, interfaces, retries, observability, and deployment.
5. Produce separate ADR artifacts for long-lived decisions.

## Architecture ADR index

| ID | Title | Status | Artifact |
|---|---|---|---|
| ADR-0101 | Decouple notifications with a queue | Proposed | inline ADR artifact |
| ADR-0102 | Use channel adapters for delivery providers | Proposed | inline ADR artifact |

The table is an index, not the full ADR content. Each artifact contains Context, Decision Drivers, Considered Alternatives, Decision, positive/negative Consequences, Revisit Conditions, and Links.

## Success indicators

- The architecture document does not duplicate full ADR bodies.
- `adrs` keeps the compact protocol field name and carries `id + artifact/path + status`.
- No ADR file is written unless the user explicitly requests persistence under the target repository's conventions.
- The result can be reviewed as architecture plus `adr-rfc` artifacts before planning.
