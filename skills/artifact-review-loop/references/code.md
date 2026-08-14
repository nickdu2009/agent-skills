# Code Review

Use for working-tree or staged diffs, commits, commit ranges, pull requests,
specified implementation files, and mixed implementation-plus-test reviews.

Review findings-first for requirement alignment, behavior authority,
correctness, boundaries, regressions, security, permissions, data/API/serialization
compatibility, concurrency/idempotency, performance, operability, rollout/config,
scope control, and test sufficiency. Tests can prove behavior but cannot
authorize a new retry, fallback, threshold, matching, auto-repair, or failure
policy.

PR metadata and CI state are supporting checks only when available. Never infer
write authority from repository access, file timestamps, a dirty worktree, or a
user's first-person wording. In self-delivery context, revisions are limited to
the trusted current-task diff. In requested review-and-revise mode, edit
production code only when that exact code surface is explicitly authorized.
