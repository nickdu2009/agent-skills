# Maintainer Surface

This directory contains repository-internal tooling and evaluation assets and should stay clearly separated from the published `skills/` source tree.

## Placement Rules

- Put install and local mirror entrypoints in `scripts/install/`.
- Run `python3 maintainer/scripts/install/validate_repo_layout.py` after `git add` so the index matches your intended tree; CI enforces the same rules on the pushed commit.
- Put shared rubric data, scenario matrices, and trigger fixtures in `data/`.
- Put maintainer-only evaluation scripts in `scripts/evaluation/`.
- Put durable, reference-worthy outputs in `reports/baselines/`.
- Put scratch runs and local report output in `reports/runs/`, then promote only the small subset that becomes a stable baseline.
