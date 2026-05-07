# AGENTS Integration

Use this snippet when a repository should adopt knowledge-driven development.

```markdown
## Knowledge-Driven Development

Use the `knowledge-driven-development` skill for non-trivial development work where project knowledge should be consulted, captured, or promoted.

Knowledge root: `docs/knowledge-driven-development/`

Before implementation:

- Read the knowledge root README.
- Read relevant shared knowledge under `project/`.
- Read `local/` only when the task depends on local environment, live systems, credentials, or temporary scopes.

During implementation:

- Record reusable shared findings in `project/active-knowledge-log.md`.
- Record current-developer findings in `local/active-knowledge-log.md`.
- Do not write raw secrets, tokens, cookies, DSNs, or private credentials into shared knowledge.

Before final response:

- Promote verified shared findings to the right `project/` category when appropriate.
- Report which knowledge files were read or updated.
```

Also add this ignore rule to the project:

```gitignore
docs/knowledge-driven-development/local/
```
