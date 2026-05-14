---
name: knowledge-driven-development
description: Legacy bridge for repositories that still use docs/knowledge-driven-development. Prefer Worktrail for durable project knowledge; use this skill to read existing KDD roots, migrate them with worktrail import kdd, or fall back to the legacy docs workflow when Worktrail is unavailable.
metadata:
  version: "0.2.0"
  tags: "coding, agents, knowledge, workflow, worktrail, migration"
---

# Purpose

Bridge legacy `docs/knowledge-driven-development/` repositories into Worktrail.

The long-term source of truth for reusable agent knowledge should be Worktrail
formal knowledge under `.worktrail/`. Legacy KDD roots remain useful as migration
sources and as a fallback when Worktrail is not installed or the user explicitly
asks to maintain the old docs format.

# When to Use

- A repository already has `docs/knowledge-driven-development/`.
- `AGENTS.md`, `CLAUDE.md`, or the user explicitly mentions KDD.
- The user asks to migrate old KDD knowledge into Worktrail.
- Worktrail is unavailable, but reusable project findings still need a legacy
  shared/local knowledge split.

# When Not to Use

- The repository already uses Worktrail and has no legacy KDD root to read or
  migrate.
- The task is a one-off direct answer or single command.
- The information belongs in a dedicated product, vendor, or domain knowledge
  base instead of project-agent knowledge.
- The finding contains raw secrets, tokens, cookies, DSNs, or credentials.

# Primary Worktrail Path

Use Worktrail first when it is available:

1. Run `worktrail context "<task>"` before non-trivial development.
2. If `docs/knowledge-driven-development/` exists, run `worktrail import kdd`
   and report matched, skipped, local-skipped, and blocked counts.
3. Run `worktrail import kdd --all` only when the user asked to migrate or
   proceed with import.
4. Use `/worktrail-review` or `worktrail review` before any promote, merge,
   discard, restore, or retire action.
5. Never promote, merge, discard, restore, or retire imported candidates without
   explicit user confirmation.
6. After migration, treat `.worktrail/` as the source of truth and do not keep
   reading the old KDD root as a parallel live knowledge base.

KDD import behavior to preserve:

- `docs/knowledge-driven-development/local/**` is skipped by default.
- Category README files such as `project/architecture/README.md` are skipped by
  default.
- `project/active-knowledge-log.md` is imported only as a pending split source
  marked `Pending Verification`; do not promote it directly.
- Imported candidate `target_path` values are relative to `.worktrail/`, with no
  `.worktrail/` prefix.

# Legacy Fallback Path

Use the legacy docs workflow only when Worktrail cannot be used or when the user
explicitly asks for old-format KDD maintenance.

## Knowledge Root Discovery

Use this precedence:

1. User-provided knowledge root.
2. Repository configuration such as `knowledge-driven-development.config.json`.
3. `AGENTS.md` or `CLAUDE.md` knowledge-root declaration.
4. Default `docs/knowledge-driven-development/`.

If no root exists and setup is in scope, initialize the default structure. If no
root exists and setup is not in scope, continue normally and report that no KDD
knowledge root was available.

## Legacy Layout

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

## Legacy Execution Pattern

1. Discover the knowledge root.
2. Read `README.md`, `project/README.md`, and task-relevant project documents.
3. Read `local/` only when local environment, live systems, credentials,
   temporary scopes, or developer-specific context matter.
4. During work, classify reusable findings as `project` or `local`.
5. Append candidates to the correct active knowledge log.
6. Promote only validated shared findings into the appropriate project category.
7. Finish with code changes, validation, knowledge read, and knowledge updates.

Use `project` for stable shared knowledge. Use `local` for current-developer
environment details, temporary IDs, local paths, personal notes, or
sensitive-context pointers.

Evidence labels:

- `Source Code Verified`
- `Live Environment Verified`
- `Test Verified`
- `User Confirmed`
- `Pending Verification`

# Scripts

These scripts support the legacy fallback path:

- `scripts/init_project_kb.py --root docs/knowledge-driven-development`
- `scripts/append_knowledge.py --root docs/knowledge-driven-development --scope project --title ...`
- `scripts/list_knowledge.py --root docs/knowledge-driven-development --query ...`

Prefer Worktrail commands for new migration and review flows. Use these scripts
only for old-format initialization, active-log append, and lightweight search.

# Safety

- Never write raw secrets or credentials into shared project knowledge.
- Record credential mechanisms by variable name or header name only.
- Before writing `local/`, ensure the local directory is ignored by version
  control.
- Treat live environment IDs as local by default unless they are intentionally
  documented as sanitized examples.
- If shared knowledge conflicts with current source or live evidence, mark it
  contradicted or update it with the newer evidence.

# Input Contract

Provide:

- the project repository
- the development task or knowledge-maintenance task
- whether Worktrail should be used, migrated to, or bypassed
- any explicit legacy KDD root override
- whether edits are allowed now or only after review

# Output Contract

Return:

- Worktrail context status, or reason Worktrail was unavailable
- legacy KDD root discovered, migrated, initialized, or skipped
- project knowledge files read
- local knowledge files read, if any
- pending candidates imported or captured
- verified knowledge promoted, only with explicit approval
- safety notes for anything intentionally left local

# Guardrails

- Do not maintain Worktrail and legacy KDD as competing live sources of truth.
- Do not promote imported KDD assumptions as verified Worktrail knowledge.
- Do not duplicate large domain docs into generic project-agent knowledge.
- Do not make `local/` tracked.
- Do not let knowledge writing replace tests or validation.
- Keep entries short, executable, and tied to development impact.

# Composition

Use with:

- Worktrail context commands when Worktrail is available and the task is
  substantial.
- Worktrail import commands when migrating old KDD or transcript evidence.
- Worktrail review commands before any Worktrail lifecycle action.
- `read-and-locate` when task-relevant knowledge references code paths that must
  be confirmed.
- `plan-before-action` when knowledge changes are part of a multi-file plan.
- `self-review` when promoted knowledge should be checked against the final diff.
- `targeted-validation` when evidence must be proven before promotion.

## Contract

### Preconditions

- A repository has legacy KDD docs, needs migration to Worktrail, or explicitly
  requires old-format project knowledge.
- Shared and local knowledge can be separated.

### Postconditions

- `status: completed` includes `worktrail_status`, `legacy_kdd_root`,
  `knowledge_read`, `candidate_updates`, `promoted_updates`, and
  `local_only_notes`.
- Worktrail is the preferred source of truth after migration.
- Shared legacy knowledge is written only under `project/`.
- Local-only legacy knowledge is written only under `local/`.

### Invariants

- The skill remains project-agnostic.
- Project facts live in the project repository or Worktrail formal knowledge.
- Secrets and private local context never enter shared knowledge.
- Validated knowledge states its evidence.

### Downstream Signals

- `worktrail_status` tells later agents whether Worktrail was used.
- `legacy_kdd_root` identifies any old root that was read or migrated.
- `knowledge_read` identifies which facts informed the work.
- `candidate_updates` identifies findings that still need verification.
- `promoted_updates` identifies stable knowledge future agents should reuse.
- `local_only_notes` identifies context intentionally excluded from version
  control.

## Failure Handling

### Common Failure Causes

- Worktrail is not installed or not initialized.
- No KDD root exists and initialization is out of scope.
- The candidate finding contains a likely secret.
- A finding is useful but lacks evidence for promotion.
- A project already has a domain-specific knowledge base that should be
  referenced rather than copied.

### Retry Policy

- If Worktrail context fails because the project is not initialized, retry once
  after `worktrail init` only when initialization is in scope.
- If KDD discovery fails, retry once using the default root.
- If secret detection blocks an entry, rewrite it using variable names or
  sanitized descriptions.
- If evidence is incomplete, keep the finding pending.

### Fallback

- Continue implementation without knowledge updates if the user explicitly asks
  to avoid documentation changes.
- Use the legacy docs workflow only when Worktrail cannot be used or old-format
  KDD maintenance is explicitly requested.

### Low Confidence Handling

- Keep low-confidence findings pending.
- Mark uncertain findings as `Pending Verification`.
- State residual uncertainty in the final response.

## Output Example

```text
[output: knowledge-driven-development | completed high | worktrail_status:"context loaded; KDD dry-run matched 12 skipped 3 local_skipped 2 blocked 0" legacy_kdd_root:"docs/knowledge-driven-development" knowledge_read:"project/README.md, project/integrations/payments.md" candidate_updates:"12 pending Worktrail candidates imported" promoted_updates:"none; awaiting review" local_only_notes:"local API token variable name kept local" | next:worktrail-review]
```

## Deactivation Trigger

- Deactivate after Worktrail context or legacy KDD lookup has been completed,
  candidates have been imported or captured as needed, and the final response
  reports knowledge activity.
- Deactivate when the task becomes a simple one-off action with no durable
  project knowledge impact.
