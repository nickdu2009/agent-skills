# Examples

## Local retry decision

Task: add retry logic for one flaky payment API.

Confirmed inputs already available before design (not invented by the designer):

- maximum 3 retries
- total budget within 10 seconds
- preserve the original terminal error
- preserve the idempotency token on every retry

Design steps:

- Alternatives: inline retry in the payment client; reusable retry wrapper.
- Choice: inline retry because only one client needs it and a shared abstraction would be premature.
- Contract: preserve the public method signature and original terminal error.
- Acceptance: three retries fit within ten seconds and preserve the idempotency token.
- ADR threshold: no ADR candidate; the choice is local, easy to reverse, and limited to one implementation increment.

If retry count, budget, terminal-error behavior, or fallback were still open, leave them as open/blocking candidates and ask — do not invent defaults just because resilience was checked.

## Cross-module queue choice

Task: choose synchronous calls or a queue for a new notification subsystem.

- Alternatives affect multiple components and deployment topology.
- Choice is long-lived and expensive to reverse.
- Output the normal design brief plus one `adr_candidates` entry using the skill's standard ADR contract.
