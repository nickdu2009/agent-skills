# Examples

## Notification subsystem

For an independent notification service supporting in-app, email, and enterprise messaging:

- Compare direct integration with an independent service plus queue.
- Select the queue only after confirming reliability and ownership requirements justify added infrastructure.
- Decompose into dispatcher, channel adapters, and preference storage.
- Record long-lived choices as separate ADR artifacts:
  - `ADR-0001`: queue-based decoupling, `Proposed`, artifact held in the response.
  - `ADR-0002`: channel adapter strategy, `Proposed`, artifact held in the response.
- Put only those IDs, titles, statuses, and artifact references in the architecture document ADR index.
- Record assumptions about existing technology and data sensitivity with validation methods.

Recommend design review before implementation planning when assumptions or interface ownership remain non-trivial.
