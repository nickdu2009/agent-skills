# Knowledge Taxonomy

Use this reference when deciding where a finding belongs.

## Scopes

- `project`: shared knowledge that should enter version control and help all contributors.
- `local`: current-developer knowledge that should stay in the working copy only.
- `domain`: dedicated external or project-specific knowledge base. Link to it instead of copying large content.

## Evidence Labels

- `Source Code Verified`: confirmed by source code, schemas, tests, or config in the repository.
- `Live Environment Verified`: confirmed by a real runtime, staging system, production read-only probe, or other live service.
- `Test Verified`: confirmed by automated tests, smoke tests, or deterministic fixtures.
- `User Confirmed`: confirmed directly by the user or project owner.
- `Pending Verification`: useful but not yet proven.

## Status Values

- `candidate`: captured for later verification or promotion.
- `verified`: accepted as reusable knowledge with evidence.
- `deprecated`: still historically useful but no longer the current rule.
- `contradicted`: conflicts with newer evidence and should not guide future work.

## Project Categories

- `architecture/`: system boundaries, data flow, contracts, and long-lived design facts.
- `decisions/`: accepted tradeoffs, rejected alternatives, and decision records.
- `runbooks/`: repeatable operational or development procedures.
- `integrations/`: external systems, APIs, authentication shape, payload contracts, and adapter behavior.
- `validation/`: test strategy, acceptance criteria, known validation commands, and evidence summaries.
- `glossary/`: project terms, module names, roles, and abbreviations.

## Promotion Rules

- Promote only knowledge that changes future development decisions.
- Promote shared knowledge only after evidence is available.
- Keep temporary IDs, local paths, personal workflow notes, and sensitive-context pointers in `local/`.
- Do not promote raw logs or artifacts; summarize the conclusion and link to durable evidence when appropriate.
- If a finding belongs to an existing domain knowledge base, add a short pointer in `project/integrations/` instead of copying the domain content.
