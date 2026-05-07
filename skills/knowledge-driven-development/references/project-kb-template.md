# Project Knowledge Base Template

Use this reference when initializing or repairing a project knowledge root.

## Default Layout

```text
docs/knowledge-driven-development/
|-- README.md
|-- project/
|   |-- README.md
|   |-- active-knowledge-log.md
|   |-- architecture/
|   |-- decisions/
|   |-- runbooks/
|   |-- integrations/
|   |-- validation/
|   `-- glossary/
`-- local/
    |-- README.md
    |-- active-knowledge-log.md
    `-- notes/
```

## Root README

```markdown
# Knowledge-Driven Development

This directory is the project knowledge root for agent-assisted development.

Start here before non-trivial work:

- Read `project/README.md` for shared knowledge categories.
- Read relevant documents under `project/`.
- Read `local/` only for current-developer environment, live systems, temporary scopes, or private notes.

`project/` is versioned shared knowledge. `local/` is developer-local and must stay ignored by version control.
```

## Project README

```markdown
# Project Knowledge

Shared knowledge in this directory should be reusable by all contributors.

Categories:

- `architecture/`: system boundaries, contracts, and data flow.
- `decisions/`: accepted tradeoffs and decision records.
- `runbooks/`: repeatable procedures.
- `integrations/`: external systems and API behavior.
- `validation/`: test and acceptance strategy.
- `glossary/`: terms and abbreviations.

Use `active-knowledge-log.md` for candidate knowledge before promotion.
```

## Local README

```markdown
# Local Knowledge

This directory is for current-developer notes only. It must not enter version control.

Use it for:

- local environment details
- temporary live-system IDs
- personal debugging notes
- sensitive-context pointers without raw secrets

Do not store raw credentials.
```

## Active Log Template

```markdown
# Active Knowledge Log

Use this file for candidate knowledge before it is verified and promoted.

## <short-title>

- Scope: project | local
- Status: candidate | verified | deprecated | contradicted
- Evidence: Source Code Verified | Live Environment Verified | Test Verified | User Confirmed | Pending Verification
- Last verified: YYYY-MM-DD
- Source:
  - <file path / command / live run / discussion reference>
- Conclusion:
  - <one executable conclusion>
- Development impact:
  - <how this should change future implementation decisions>
```
