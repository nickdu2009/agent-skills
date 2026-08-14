# Design calibration

## Local retry choice

Assume the requirement already confirms maximum retries, total budget, terminal-error behavior, and idempotency. Compare inline retry with a shared wrapper. Choose inline logic when only one client needs it and the choice is local/reversible; preserve the public contract and derive acceptance from the confirmed budget and idempotency. No ADR candidate is needed.

If retry count, budget, error result, or fallback is open, keep it blocking and ask. Never invent resilience defaults because the NFR checklist was read.

## Cross-module queue choice

For synchronous calls versus a queue across a notification subsystem, compare component, data, failure, and deployment impacts. Because the choice is cross-component and costly to reverse, return the design brief plus a Proposed ADR candidate.
