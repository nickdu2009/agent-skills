# ADR format

Create a separate artifact for each key architecture decision that is long-lived, cross-component, or costly to reverse.

```markdown
# <ADR-ID>: <title>

- Status: Proposed | Accepted | Deprecated | Superseded
- Date: YYYY-MM-DD

## Context

## Decision Drivers

## Considered Alternatives

## Decision

## Consequences

### Positive

### Negative

## Revisit Conditions

## Links
- Supersedes: <ADR-ID>
- Proposes to supersede: <ADR-ID>
- Related: <ADR-ID>
```

Rules:

- `Context`, `Decision`, `Consequences`, and `Status` are required.
- Record alternatives when more than one realistic option exists; otherwise state why comparison is unnecessary.
- Use `ADR-NNNN` or a target-repository-compatible `ADR-YYYYMMDD-<slug>` identifier.
- Accepted ADRs use `Supersedes`; Proposed ADRs use only `Proposes to supersede`.
- Keep the artifact vendor-neutral. The architecture document links to it but does not duplicate its full content.
