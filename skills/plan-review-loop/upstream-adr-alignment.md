# Upstream ADR alignment

Use this dimension when a plan cites ADRs or makes architecture-sensitive changes.

## Active-set check

- Only `Status: Accepted` ADRs may constrain implementation.
- Exclude Proposed, Deprecated, and Superseded ADRs.
- Exclude historical or retired records when lifecycle information is available.
- Exclude an Accepted ADR replaced by a newer Accepted ADR.
- With Markdown-only inputs, derive replacement from Accepted `Links > Supersedes`; ignore Proposed `Proposes to supersede`.
- Stop on conflicting active decisions or ambiguous IDs.

## Plan traceability check

- `Sources and Alignment` lists every constraining ADR ID and artifact/path.
- Every affected step cites the relevant ADR ID.
- Landing files, interfaces, sequence, and validation do not contradict the decision.
- Rollback does not require violating an ADR without explicitly returning upstream.
- The plan does not add a new architecture choice under an implementation detail.

## Finding severity

- Blocking: plan depends on Proposed/inactive/conflicting ADRs, contradicts an active Accepted ADR, or invents a major architecture decision.
- Warning: ADR is valid but affected steps fail to cite it, or validation does not prove alignment.
- Low-risk: artifact/path or rationale traceability is incomplete but the active decision is otherwise unambiguous.

In review-and-revise mode, fix objective traceability gaps in the plan. Return to design/review when the decision itself is unresolved.
