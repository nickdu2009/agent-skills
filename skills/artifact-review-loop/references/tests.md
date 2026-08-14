# Test Artifact Review

Use for test cases, test files as test artifacts, test strategy, coverage
matrices, assertions, fixtures, and flaky-risk analysis. Reviewing the
production code under test routes to `code` instead.

Check scenario and boundary coverage, positive and negative paths, assertion
strength, fixture fidelity, determinism, isolation, ordering/time dependence,
failure diagnostics, contract traceability, and meaningful coverage gaps.

Tests must follow an authorized product contract. Reject tests that invent or
lock in unconfirmed defaults, retries, fallbacks, thresholds, permissions, data
semantics, or failure handling. Green tests do not authorize product behavior.
In review-and-revise mode, edit only test artifacts unless production-code
revision is separately authorized through a fresh code review route.
