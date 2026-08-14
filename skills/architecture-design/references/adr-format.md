# ADR format

Create a separate artifact for each long-lived, cross-component, or costly-to-reverse architecture decision.

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

Require Context, Decision, Consequences, and Status. Accepted ADRs may use `Supersedes`; Proposed ADRs use only `Proposes to supersede`. Keep the artifact vendor-neutral and do not persist it without explicit intent.
