# Maintainer Surface

This directory contains repository-internal tooling and evaluation assets and should stay clearly separated from the published `skills/` source tree.

## Placement Rules

- Keep the unified install and local mirror entrypoint in `scripts/install/`.
- Run `python3 maintainer/scripts/install/validate_repo_layout.py` after `git add` so the index matches your intended tree; CI enforces the same rules on the pushed commit.
- Put shared rubric data, scenario matrices, and trigger fixtures in `data/`.
- Put maintainer-only evaluation scripts in `scripts/evaluation/`.
- Put durable, reference-worthy outputs in `reports/baselines/`.
- Put scratch runs and local report output in `reports/runs/`, then promote only the small subset that becomes a stable baseline.

## Useful Evaluation Entrypoints

- `python3 maintainer/scripts/install/run_manage_governance_smoke.py`
- `python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report`
- `python3 maintainer/scripts/evaluation/run_claude_trigger_smoke.py`
- `python3 maintainer/scripts/evaluation/run_claude_interactive_mainline.py`

The Claude smoke runner uses clean temporary workspaces with `.claude/skills/`
mirrored from the canonical `skills/` tree, so trigger validation is less
likely to be distorted by repository-local examples and maintainer fixtures.

For multi-turn Claude acceptance work, use the fixture-backed interactive plan in
[`docs/maintainer/claude-interactive-test-implementation-plan.md`](../docs/maintainer/claude-interactive-test-implementation-plan.md)
together with the checklist in
[`docs/maintainer/claude-interactive-test-checklist.md`](../docs/maintainer/claude-interactive-test-checklist.md).

For retained upstream authoring guidance, see
[`docs/maintainer/claude-skill-authoring-best-practices.md`](../docs/maintainer/claude-skill-authoring-best-practices.md).
