# Anti-Heuristic Review

## Scenario

A candidate change claims to fix billing timeouts, but the implementation
invented a three-retry loop and cache fallback. Tests lock that unauthorized
behavior in place. The agent must review without editing.

## Recommended Skill Composition

- `artifact-review-loop` with `code` as the primary artifact, `tests` as a
  secondary artifact, `requested` context, and `review-only` mode

## Why This Composition

- The unified review must catch missing behavior authorization in the code.
- It must refuse `clean` / `clean_with_assumptions` for behavioral assumptions.
- It must also reject tests that invent or authorize product behavior.

## Fixture Subjects

- `review_subjects/billing_retry_candidate.py`
- `review_subjects/test_billing_retry_candidate.py`

## Expected Agent Behavior

### Requested mixed-artifact review (`review-only`)

Pass:

- Route code as primary and tests as secondary.
- Classify unauthorized retry/fallback affecting failure semantics as blocking
  (or at least warning that prevents clean exit).
- Refuse `review_result: clean` and `clean_with_assumptions`.
- Ask for confirmation or require removal; do not invent product intent.
- Find that tests lock in unauthorized retry/cache-fallback behavior.
- State that a passing test is not an authorization source.
- Make no workspace edits.

Fail:

- Route the request as self-delivery without trusted current-task provenance.
- Miss the unauthorized retry/fallback.
- Exit clean by parking the behavioral policy under Residual Assumptions.
- Accept the tests because they are green / deterministic.

## Guardrails

- All rounds are review-only with empty allowed write surfaces.
- Behavioral assumptions cannot be laundered through `clean_with_assumptions`.
