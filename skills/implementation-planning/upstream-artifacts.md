# Upstream artifacts

## Accepted inputs

Planning may consume requirements, design briefs, architecture documents, impact summaries, and ADR artifacts or paths. Read supplied files before planning.

## ADR activity resolution

Treat an ADR as a frozen decision only when:

1. Its document status is `Accepted`.
2. Its lifecycle, when supplied by the upstream source, is active/current rather than historical/retired.
3. No newer Accepted ADR supersedes it.
4. Its ID and relationship references are unambiguous.

Never freeze:

- `Proposed`
- `Deprecated`
- `Superseded`
- historical or retired records
- an Accepted ADR replaced by another Accepted ADR

When only portable Markdown is available:

1. Read every ADR heading and Status.
2. From Accepted ADRs only, read fixed `Links` entries named `Supersedes`.
3. Build the reverse replacement graph.
4. Exclude replaced Accepted ADRs from the active set.
5. Ignore Proposed `Proposes to supersede` links when computing activity.

When generic upstream lifecycle or relationship metadata is also available, use it to refine the active set without depending on any vendor-specific field name.

## Blocking conditions

Return upstream to design/review when:

- an ADR is Proposed but implementation depends on it
- two active Accepted ADRs conflict
- a replacement target is missing or ambiguous
- lifecycle/activity cannot be determined safely
- the plan would need a new architecture decision

## Traceability

List each active Accepted ADR in `Sources and Alignment`. Cite its ID in every implementation step whose landing, sequence, interface, or validation it constrains.
