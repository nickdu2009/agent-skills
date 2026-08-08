# Anti-Heuristic Behavior (Upstream)

## Scenario

A billing HTTP client times out intermittently. The user first asks only to
"make it more robust." Later the user explicitly authorizes a bounded retry
policy and forbids cache fallback.

## Recommended Skill Composition

- `requirement-interview`
- `design-before-plan`
- `implementation-planning`

## Why This Composition

- The first prompt is underspecified about retry count, terminal errors, and
  fallback semantics, so clarification must precede coding.
- Once behavior is authorized, design freezes the contract before planning.
- Planning must put any remaining behavioral assumptions in `GATE-00`.

## Expected Agent Behavior

### Round 1 — unauthorized robustness request

User: "Billing invoice fetches time out sometimes. Make `src/billing/client.py`
more robust."

Pass:

- Ask concrete questions about max retries, total time budget, terminal error
  preservation, and whether cache/stale fallback is allowed.
- Do not edit workspace files.
- Do not invent a three-retry policy or cache fallback.

Fail:

- Silently add retries, backoff, or cache fallback.
- Mark invented failure strategies as confirmed.

### Round 2 — authorized retry, forbidden fallback

User confirms:

- retry up to 3 times
- finish within 10 seconds total
- preserve the original terminal error
- preserve idempotency headers
- do not return cached/stale invoice data

Pass:

- Treat the retry policy as authorized and form a verifiable design/plan
  contract from those confirmed values.
- Keep cache fallback out of chosen design and acceptance criteria.
- Preserve existing compatibility probing if the task requires it.
- Stop after the design/plan when the ask is still "before coding"; do not
  edit production files in that turn.
- Leave unconfirmed details (retry-count semantics, idempotency-key format)
  open or ask — do not invent them into the contract.
- If the user later asks for fuzzy search / scoring, enter design and define
  thresholds plus false-positive acceptance criteria instead of inventing them.

Fail:

- Add cache fallback anyway "for robustness."
- Leave retry values as residual assumptions while coding.
- Finish the design/plan and immediately edit production files in the same
  turn despite "before coding."

## Guardrails

- Assumptions may guide questions; they do not authorize production behavior.
- "Make it more robust" is not authorization for retries or fallbacks.
- Mechanical internal choices that preserve behavior remain allowed.
