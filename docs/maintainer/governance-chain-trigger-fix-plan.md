# Governance Chain Trigger Fix Plan

Status: Implemented
Date: 2026-04-11

## Summary

The original governance-chain work is already present in the source artifacts:

- `templates/governance/AGENTS-template.md`
- `templates/governance/CLAUDE-template.md`
- `CLAUDE.md`
- `skills/minimal-change-strategy/SKILL.md`
- `skills/targeted-validation/SKILL.md`
- `maintainer/data/trigger_test_data.py`

The remaining gap discovered during review was in the delivery path, not the source content:
`maintainer/scripts/install/manage-governance.py` was still injecting only a hard-coded subset of
governance sections, so fresh project installs could miss sections that already existed in the
templates. The repo-root `AGENTS.md` also lagged behind the current governance model.

## Gap Closed By This Follow-Up

### 1. Template-driven injection was incomplete

Prior behavior:

- Full-profile rule injection only wrote `## Multi-Agent Rules`, `## Skill Escalation`, and
  `## Skill Lifecycle`.
- Fresh installs or `--update` runs could omit:
  - `## Skill Activation`
  - `## Skill Chain Triggers`
  - `## Skill Protocol v1`
  - `## Skill Family Concurrency Budgets`

Fix:

- Load all top-level governance sections from the template in order.
- Render new full-profile docs from that ordered section list.
- Update existing docs section-by-section using the same template order.
- Keep the `multi-agent` profile intentionally limited to `## Multi-Agent Rules`.

### 2. Repo-root `AGENTS.md` had governance drift

Prior behavior:

- Missing `Skill Activation`, `Skill Chain Triggers`, `Skill Protocol v1`, and
  `Skill Family Concurrency Budgets`
- Missing the newer `design-before-plan`, `bugfix-workflow`, and `safe-refactor` lifecycle rules
- Duplicated escalation triggers spread across unrelated sections

Fix:

- Align root `AGENTS.md` with the current governance block used by the templates.
- Centralize escalation rules under `## Skill Escalation`.
- Keep repo-specific sections such as `Role`, `Before Coding`, `Complexity Rules`, and
  `Review Rules` outside the shared governance block.

### 3. Validation guidance now reflects the real risk boundary

Prior behavior:

- `--sync-local ... --check` only verified the local skill mirror.
- That check does not validate generated `AGENTS.md` or `CLAUDE.md` content.

Fix:

- Validate rule injection through a temporary project created with `git init`.
- Use `manage-governance.py --project <temp-dir>` to generate governance files.
- Inspect the generated governance docs directly for the expected sections.

## Implementation Details

### Script changes

- Add top-level governance section discovery in `manage-governance.py`
- Use template section order as the source of truth for full-profile injection
- Insert missing sections before the next known governance heading, or after the previous one, so
  updates preserve ordering inside existing files

### Repo governance changes

- Update root `AGENTS.md` to include:
  - `Skill Activation`
  - unified `Skill Escalation`
  - expanded `Skill Lifecycle`
  - `Skill Chain Triggers`
  - `Skill Protocol v1`
  - `Skill Family Concurrency Budgets`
- Remove now-redundant escalation bullets from unrelated sections

## File Change Summary

| File | Changes |
|------|---------|
| `maintainer/scripts/install/manage-governance.py` | Make rule injection follow the full template section list instead of a hard-coded subset |
| `AGENTS.md` | Align repo-root governance content with the templates and centralize escalation rules |
| `docs/maintainer/governance-chain-trigger-fix-plan.md` | Update the plan to reflect implemented state and correct validation guidance |

## Validation

1. Create a temporary directory and initialize it with `git init`.
2. Run `python3 maintainer/scripts/install/manage-governance.py --project <temp-dir> --rules-only --update --platform cursor`.
3. Verify generated `AGENTS.md` contains:
   - `## Skill Activation`
   - `## Skill Chain Triggers`
   - `## Skill Protocol v1`
   - `## Skill Family Concurrency Budgets`
4. Run `python3 maintainer/scripts/install/manage-governance.py --project <temp-dir> --rules-only --update --platform claude-code`.
5. Verify generated `CLAUDE.md` contains the same sections.
6. Optionally run `--sync-local cursor --check` and `--sync-local claude --check` for skill mirror
   validation only.

## Notes

- No additional template edits were required in this follow-up because the template sources were
  already updated before this patch.
- No additional trigger-test edits were required because the chain-trigger cases were already
  present in `maintainer/data/trigger_test_data.py`.
- The key invariant after this patch is: the templates are the source of truth, and full-profile
  rule injection follows the template section list rather than a manually maintained subset.
