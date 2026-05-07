---
name: knowledge-driven-development
description: Guide agents to preserve and reuse project knowledge across long-running software work. Use when a repository has or needs docs/knowledge-driven-development, when reusable implementation findings should be captured, when validated discoveries should become project runbooks or decisions, or when AGENTS.md requires knowledge lookup before development.
metadata:
  version: "0.1.0"
  tags: "coding, agents, knowledge, workflow"
---

# Purpose

Make project knowledge durable across conversations. The skill turns repeated development into a loop: read existing project knowledge before work, capture reusable findings while working, promote verified knowledge after validation, and report what changed.

# When to Use

- When project work should consult a repository knowledge base before implementation.
- When creating or maintaining `docs/knowledge-driven-development/`.
- When a finding from code, tests, or a live environment will affect future development decisions.
- When the user asks to preserve development knowledge, runbooks, architecture decisions, validation findings, or local-only context.

# When Not to Use

- For one-off direct answers or single commands.
- For product- or vendor-specific reference material that already belongs in a dedicated domain knowledge base.
- For writing secrets, tokens, cookies, DSNs, or raw credentials into shared documentation.

# Core Rules

- Keep the skill generic; store project facts in the project repository.
- Default the knowledge root to `docs/knowledge-driven-development/`.
- Treat `project/` as shared, versioned knowledge.
- Treat `local/` as current-developer knowledge that must stay out of version control.
- Read relevant project knowledge before non-trivial implementation.
- Record reusable findings as candidates before they fade from context.
- Promote only validated shared knowledge into durable project documents.
- Report knowledge files read and updated in the final response.

# Knowledge Root Discovery

Use this precedence:

1. User-provided knowledge root.
2. Repository configuration such as `knowledge-driven-development.config.json`.
3. `AGENTS.md` or `CLAUDE.md` knowledge-root declaration.
4. Default `docs/knowledge-driven-development/`.

If no knowledge root exists and the task is to set one up, initialize the default structure. If no knowledge root exists and the task is unrelated, continue normally and note that no project knowledge was available.

# Execution Pattern

1. Discover the knowledge root.
2. Read `README.md`, `project/README.md`, and task-relevant project documents.
3. Read `local/` only when local environment, live systems, credentials, temporary scopes, or developer-specific context matter.
4. During work, classify reusable findings as `project` or `local`.
5. Append candidates to the correct active knowledge log.
6. After validation, promote verified shared findings to the appropriate project category.
7. Finish with code changes, validation, knowledge read, and knowledge updates.

# Project Knowledge Layout

Use this default layout:

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

See `references/project-kb-template.md` for document templates and `references/knowledge-taxonomy.md` for category selection.

# Classification

- Use `project` for stable knowledge that all contributors should reuse.
- Use `local` for current-developer environment details, temporary IDs, local paths, personal notes, or sensitive-context pointers.
- Use a dedicated domain knowledge base when one already exists; reference it from project knowledge rather than copying it.

Evidence labels:

- `Source Code Verified`
- `Live Environment Verified`
- `Test Verified`
- `User Confirmed`
- `Pending Verification`

# Scripts

- `scripts/init_project_kb.py --root docs/knowledge-driven-development`
- `scripts/append_knowledge.py --root docs/knowledge-driven-development --scope project --title ...`
- `scripts/list_knowledge.py --root docs/knowledge-driven-development --query ...`

Prefer scripts for mechanical initialization, active-log append, and lightweight search. Use normal file edits when promoting knowledge into durable documents because promotion requires judgment.

# Safety

- Never write raw secrets or credentials into `project/`.
- Record credential mechanisms by variable name or header name only.
- Before writing `local/`, ensure the local directory is ignored by version control.
- Treat live environment IDs as local by default unless they are intentionally documented as sanitized examples.
- If a shared knowledge entry conflicts with current source or live evidence, mark it `contradicted` or update it with the newer evidence.

# Input Contract

Provide:

- the project repository
- the development task or knowledge-maintenance task
- any explicit knowledge root override
- whether edits are allowed now or only after review

Optional but helpful:

- evidence source for a finding
- intended audience for the knowledge
- whether a finding should be shared or local-only

# Output Contract

Return:

- knowledge root discovered or initialized
- project knowledge files read
- local knowledge files read, if any
- candidate knowledge captured
- verified knowledge promoted
- safety notes for anything intentionally left local

# Guardrails

- Do not promote assumptions as verified knowledge.
- Do not duplicate large domain docs into the generic project knowledge base.
- Do not make `local/` tracked.
- Do not let knowledge writing replace tests or validation.
- Keep entries short, executable, and tied to development impact.

# Composition

Use with:

- `read-and-locate` when task-relevant knowledge references code paths that must be confirmed.
- `plan-before-action` when knowledge changes are part of a multi-file implementation plan.
- `self-review` when promoted knowledge should be checked against the final diff.
- `targeted-validation` when evidence must be proven before promotion.

## Contract

### Preconditions

- A long-running project task needs durable knowledge, or the user explicitly asks to create or maintain project knowledge.
- The repository can hold project knowledge under a known root.
- Shared and local knowledge can be separated.

### Postconditions

- `status: completed` includes `knowledge_root`, `knowledge_read`, `candidate_updates`, `promoted_updates`, and `local_only_notes`.
- Shared knowledge is written only under `project/`.
- Local-only knowledge is written only under `local/`.
- The final response reports knowledge activity.

### Invariants

- The skill remains project-agnostic.
- Project facts live in the project repository.
- Secrets and private local context never enter shared knowledge.
- Validated knowledge states its evidence.

### Downstream Signals

- `knowledge_root` tells later agents where to start.
- `knowledge_read` identifies which facts informed the work.
- `candidate_updates` identifies findings that still need verification.
- `promoted_updates` identifies stable knowledge future agents should reuse.
- `local_only_notes` identifies context intentionally excluded from version control.

## Failure Handling

### Common Failure Causes

- No knowledge root exists and initialization is out of scope.
- The candidate finding contains a likely secret.
- A finding is useful but lacks evidence for promotion.
- The project already has a domain-specific knowledge base that should be referenced rather than copied.

### Retry Policy

- If discovery fails, retry once using the default root.
- If secret detection blocks a project entry, rewrite the entry using variable names or sanitized descriptions.
- If evidence is incomplete, leave the finding in the active log as `Pending Verification`.

### Fallback

- Continue implementation without knowledge updates if the user explicitly asks to avoid documentation changes.
- Use `plan-before-action` when knowledge updates must be sequenced with code changes.
- Use `targeted-validation` when promotion depends on a focused check.

### Low Confidence Handling

- Keep low-confidence findings in active logs.
- Mark uncertain findings as `Pending Verification`.
- State residual uncertainty in the final response.

## Output Example

```text
[output: knowledge-driven-development | completed high | knowledge_root:"docs/knowledge-driven-development" knowledge_read:"project/README.md, project/integrations/payments.md" candidate_updates:"project/active-knowledge-log.md" promoted_updates:"project/runbooks/payment-webhook-debugging.md" local_only_notes:"local API token variable name kept in local/" | next:targeted-validation]
```

## Deactivation Trigger

- Deactivate after knowledge has been read, candidates captured, validated findings promoted, and the final response has reported knowledge activity.
- Deactivate when the task becomes a simple one-off action with no durable project knowledge impact.
