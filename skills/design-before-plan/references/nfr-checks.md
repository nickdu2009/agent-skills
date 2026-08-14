# NFR checks

Read when a non-functional dimension can change the design. Treat every item as a question candidate, not a default.

- **Security:** identity, authorization, validation, sensitive data, audit, encryption boundaries.
- **Performance:** observable latency/throughput/resource targets, workload shape, measurement point.
- **Observability:** logs, metrics, traces, ownership, alert condition and response.
- **Resilience:** timeout, retry, idempotency, failure isolation, recovery, degradation.
- **Operability:** configuration, rollout, rollback, feature control, runbooks.
- **Compatibility:** clients, protocols, versions, stored data, mixed-version operation.

For each candidate record `{item, source, status, blocking}`. Only `confirmed`, an active Accepted ADR, or preserved compatibility may constrain `chosen_design`. Retry counts, timeouts, thresholds, fallbacks, alerts, and degradation paths require an explicit authorization source.
