# Examples

## Local retry decision

Task: add retry logic for one flaky payment API.

- Alternatives: inline retry in the payment client; reusable retry wrapper.
- Choice: inline retry because only one client needs it and a shared abstraction would be premature.
- Contract: preserve the public method signature and original terminal error.
- Acceptance: three retries fit within ten seconds and preserve the idempotency token.
- ADR threshold: no ADR candidate; the choice is local, easy to reverse, and limited to one implementation increment.

## Cross-module queue choice

Task: choose synchronous calls or a queue for a new notification subsystem.

- Alternatives affect multiple components and deployment topology.
- Choice is long-lived and expensive to reverse.
- Output the normal design brief plus one `adr_candidates` entry using the skill's standard ADR contract.
