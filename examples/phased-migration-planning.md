# Phased Migration Planning

## Scenario

A monorepo contains three services — `billing`, `notifications`, and `analytics` — that share a PostgreSQL database. A schema migration must rename a column used by all three services (`user_id` → `account_id`) without downtime. The migration must be sequenced so that each service can be updated and deployed independently.

The agent's task is to produce a phased execution plan using the phase system, not to implement the migration itself.

## Recommended Skill Composition

- `phase-plan`
- `phase-contract-tools`
- `scoped-tasking`
- `plan-before-action`

## Inputs

- Three service directories: `services/billing/`, `services/notifications/`, `services/analytics/`
- A shared schema file: `db/migrations/`
- Known hotspot: the `users` table is read by all three services

## Task

Break the migration into a phased plan:

1. Identify which services read or write `user_id` and in which files.
2. Design wave sequencing: which service can be migrated first with the least coupling risk?
3. Produce the per-phase strict four-file phase doc set plus the phase-root summary: `docs/phases/phase1/roadmap.md`, `docs/phases/phase1/plan.yaml`, `docs/phases/phase1/wave-guide.md`, `docs/phases/phase1/execution-index.md`, and `docs/phases/README.md`.
4. Run the schema validator against `docs/phases/phase1/plan.yaml`.
5. Run the doc-set validator.

## What To Observe

- The agent produces `docs/phases/phase1/plan.yaml` as the execution authority, not a Markdown-first plan.
- The per-phase strict four-file output contract is respected inside `docs/phases/phase1/` — no extra phase-local planning docs.
- `docs/phases/README.md` follows the lightweight root template: a title, a `## Phase Summaries` section, and a bullet summary for `phase1` with `goal`, `scope`, and `status`.
- Validators are run immediately after YAML is produced, not deferred.
- Hotspot ownership is explicit in the plan (the `users` table must appear in `hotspots`).
- Wave ordering reflects real coupling: the service with the fewest cross-references migrates first.
- The agent does not hand-write prompts — prompt derivation is deferred to renderers.
- Scope is narrowed before the agent reads all three services exhaustively.

## Example Root README

```markdown
# Phase Index

## Phase Summaries

- `phase1`: goal: rename `user_id` to `account_id` without downtime; scope: plan the multi-service migration and hotspot ownership only; status: proposed
- `phase2`: goal: update downstream services after compatibility cutover; scope: reserved follow-up phase after phase1 completes; status: blocked
```

## What NOT To Observe

- The agent should not implement the actual migration SQL or code changes.
- The agent should not create `phase1-pr-delivery-plan.md` or other non-standard planning docs.
- The agent should not skip validation because "it looks correct."
