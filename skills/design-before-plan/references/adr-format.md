# ADR format

Create a candidate only when realistic alternatives existed and the decision is cross-module/PR, long-lived, or costly to reverse.

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
