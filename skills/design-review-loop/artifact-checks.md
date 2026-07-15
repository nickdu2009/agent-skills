# Artifact checks and output shape

## Conditional checks

- Architecture: component responsibilities, dependency direction, data ownership, NFR coverage, deployment, and operability.
- Technical proposal: requirement coverage, concrete contracts, failure behavior, migration, and rollout.
- Interface: inputs/outputs, errors, versioning, compatibility, ownership, and deprecation.
- Data model: ownership, invariants, forward/backward migration, data-loss risk, indexes, and rollback.
- ADR/RFC: context, drivers, alternatives, decision, consequences, status, relationships, and revisit conditions.

## Finding shape

```yaml
severity: blocking | warning | low-risk
area: ""
problem: ""
impact: ""
required_fix: ""
```

## Complete output shape

```markdown
## Review Result
review_result: clean | clean_with_assumptions | needs_clarification | issues_found
mode: review-only | review-and-revise
type: architecture | adr-rfc | interface | data-model | technical-proposal

## Issues
blocking:
- <finding or None>

warning:
- <finding or None>

low-risk:
- <finding or None>

## Changes Made
- file: ""
  summary: ""

## Validation
- ""

## Residual Assumptions
- assumption: ""
  validation_method: ""

## Clarification Questions
- question: ""
  why_blocked: ""
```

Do not omit sections. Use `- None` where no entries exist.
