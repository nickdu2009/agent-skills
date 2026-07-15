# ADR review

Apply this checklist when `type: adr-rfc`.

## Structure

- Heading contains a stable ADR ID and title.
- `Status` is one of `Proposed`, `Accepted`, `Deprecated`, or `Superseded`.
- `Context`, `Decision`, and `Consequences` are present and non-empty.
- `Decision Drivers`, `Considered Alternatives`, and `Revisit Conditions` are present when the decision warrants them.

## Decision quality

- Drivers are traceable to requirements or constraints.
- All realistic alternatives are included; if only one exists, the ADR explains why comparison is unnecessary.
- The selected option follows from the stated drivers.
- Positive and negative consequences are concrete.
- Revisit conditions are observable rather than vague.

## Relationships

- Accepted ADRs use `Supersedes`.
- Proposed ADRs use only `Proposes to supersede`.
- `Related` does not imply replacement.
- Referenced ADR IDs are unambiguous and do not create contradictory active decisions.

## Status and executability

- Proposed means the choice is not yet a frozen implementation constraint.
- Accepted means implementation may treat the decision as settled.
- Deprecated and Superseded ADRs are not active constraints.
- Content review does not change document status or perform persistence/lifecycle actions.

Classify missing required structure or contradictory decisions as blocking; weak alternatives or consequences as warning; minor wording or revisit detail as low-risk.
