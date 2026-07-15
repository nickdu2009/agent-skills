# ADR Design Review Scenario

## Task

Review `ADR-0042: Use a dedicated REST batch endpoint` in `review-and-revise` mode.

## Review checks

- ID and Status use the standard contract.
- Context explains the batch-operation problem and constraints.
- Decision Drivers trace to latency, compatibility, and partial-failure requirements.
- Alternatives include a dedicated endpoint, polymorphic existing endpoint, and GraphQL mutation.
- Decision rationale follows from the drivers.
- Consequences include both client adoption cost and clearer server contracts.
- Revisit Conditions are observable.
- Proposed ADR uses `Proposes to supersede`; Accepted ADR uses `Supersedes`.

## Expected result

If the artifact is complete and repository contracts match:

```markdown
## Review Result
review_result: clean
mode: review-and-revise
type: adr-rfc
```

Content review ends there. It does not write the ADR to a repository, change candidate state, or alter formal knowledge lifecycle.
