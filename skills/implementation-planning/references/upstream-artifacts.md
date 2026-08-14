# Upstream artifact alignment

Planning may consume requirements, design/architecture, impact summaries, and ADR artifacts. Read supplied paths.

Treat an ADR as frozen only when it is `Accepted`, active/current, unambiguously identified, and not superseded by a newer Accepted ADR. Exclude Proposed, Deprecated, Superseded, historical, retired, and replaced records.

For Markdown-only ADRs:

1. Read IDs and statuses.
2. From Accepted ADRs only, follow `Links > Supersedes`.
3. Exclude replaced Accepted records.
4. Ignore Proposed `Proposes to supersede` when computing the active set.

Stop for design/review when an implementation depends on Proposed decisions, active decisions conflict, replacement targets are missing/ambiguous, lifecycle cannot be resolved, or a new architecture choice is needed.

List every active constraint in `Sources and Alignment`; cite its ID in each affected step and verification.
