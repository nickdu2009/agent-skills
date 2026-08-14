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
artifact_type: design
artifact_subtype: adr-rfc
secondary_types: []
review_context: requested
mode: review-and-revise
authorization_source: explicit-user-request
write_scope: reviewed-artifact

## Issues
blocking:
- None
warning:
- None
low-risk:
- None

## Changes Made
- None

## Validation
- "ADR contract checked"

## Residual Assumptions
- None

## Clarification Questions
- None

[output: artifact-review-loop | completed high | artifact_type:"design" artifact_subtype:"adr-rfc" secondary_types:"none" review_context:"requested" mode:"review-and-revise" authorization_source:"explicit-user-request" write_scope:"reviewed-artifact" review_result:"clean" issues:"0 blocking, 0 warning, 0 low-risk" changes:"none" validation:"ADR contract checked" | next:done]
[validate: artifact-review-loop | PASS | checks:contract]
```

Content review ends there. It does not write the ADR to a repository, change candidate state, or alter formal knowledge lifecycle.
