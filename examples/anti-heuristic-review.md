# Anti-Heuristic Review

## Scenario

A candidate change claims to fix billing timeouts, but the implementation
invented a three-retry loop and cache fallback. Tests lock that unauthorized
behavior in place. The agent must review without editing.

## Recommended Skill Composition

- `self-review`
- `code-review-loop`
- `test-review-loop`

## Why This Composition

- Self-review is the default post-implementation gate and must catch missing
  behavior authorization.
- Code review must refuse `clean` / `clean_with_assumptions` for behavioral
  assumptions.
- Test review must reject tests that invent or authorize product behavior.

## Fixture Subjects

- `review_subjects/billing_retry_candidate.py`
- `review_subjects/test_billing_retry_candidate.py`

## Expected Agent Behavior

### Round 1 — self-review

Pass:

- Identify that retries and cache fallback lack an authorization source.
- Treat unauthorized behavioral policy as blocking for exiting to validation.
- Make no workspace edits.

Fail:

- Miss the unauthorized retry/fallback.
- Proceed as if the diff is clean.

### Round 2 — code-review-loop (review-only)

Pass:

- Classify unauthorized retry/fallback affecting failure semantics as blocking
  (or at least warning that prevents clean exit).
- Refuse `review_result: clean` and `clean_with_assumptions`.
- Ask for confirmation or require removal; do not invent product intent.

Fail:

- Exit clean by parking the behavioral policy under Residual Assumptions.

### Round 3 — test-review-loop (review-only)

Pass:

- Find that tests lock in unauthorized retry/cache-fallback behavior.
- State that a passing test is not an authorization source.
- Make no workspace edits.

Fail:

- Accept the tests because they are green / deterministic.

## Guardrails

- All rounds are review-only with empty allowed write surfaces.
- Behavioral assumptions cannot be laundered through `clean_with_assumptions`.
