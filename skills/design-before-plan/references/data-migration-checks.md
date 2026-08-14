# Data migration checks

Read only when schema, stored data, indexes, or data ownership changes.

Record:

- current and target schema/ownership
- compatibility strategy during mixed versions
- forward transformation and idempotency
- rollback or restore boundary, including irreversible operations
- rollout constraints: volume, downtime tolerance, locks, replication, storage
- validation: counts, invariants, checksums/samples, application-level behavior
- failure ownership and stop conditions

Do not infer volume thresholds, dual-write periods, maintenance windows, backfill rate, destructive cleanup timing, or acceptable loss. Present alternatives and obtain an owner decision. If rollback is impossible, state that explicitly and require acceptance before planning.
