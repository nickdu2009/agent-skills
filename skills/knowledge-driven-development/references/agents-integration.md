# AGENTS Integration

Use this snippet only when a repository still needs the legacy
`docs/knowledge-driven-development/` bridge. Prefer Worktrail for new durable
agent knowledge.

```markdown
## Knowledge-Driven Development

Use Worktrail for durable agent knowledge:

- Run `worktrail context "<task>"` before substantial work.
- If this repository still has `docs/knowledge-driven-development/`, run
  `worktrail import kdd` for a dry-run before migration.
- Run `worktrail import kdd --all` only after the user asks to migrate.
- Review imported candidates with `worktrail review` before any promote or merge.

Use the `knowledge-driven-development` skill only as a legacy bridge when old
KDD docs must be read, migrated, or maintained because Worktrail is unavailable.

Knowledge root: `docs/knowledge-driven-development/`

Before implementation in legacy fallback mode:

- Read the knowledge root README.
- Read relevant shared knowledge under `project/`.
- Read `local/` only when the task depends on local environment, live systems, credentials, or temporary scopes.

During implementation in legacy fallback mode:

- Record reusable shared findings in `project/active-knowledge-log.md`.
- Record current-developer findings in `local/active-knowledge-log.md`.
- Do not write raw secrets, tokens, cookies, DSNs, or private credentials into shared knowledge.

Before final response in legacy fallback mode:

- Promote verified shared findings to the right `project/` category when appropriate.
- Report which knowledge files were read or updated.
```

Also add this ignore rule to the project:

```gitignore
docs/knowledge-driven-development/local/
```
