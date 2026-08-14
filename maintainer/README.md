# Maintainer Surface

This directory contains repository-internal validation and evaluation assets. It is not part of the published Agent Skills packages.

## Placement Rules

- Keep distributable content only under `skills/<name>/`.
- Put shared fixtures and metadata in `data/`.
- Put reusable checks in `scripts/analysis/` and content evaluation in `scripts/evaluation/`.
- Keep durable baselines in `reports/baselines/`; local run output belongs in `reports/runs/`.
- Do not add runtime discovery paths, installers, governance renderers, sidecars, or runtime-specific acceptance runners.

## Core Checks

```bash
python3 maintainer/scripts/analysis/validate_skill_catalog.py
python3 maintainer/scripts/analysis/validate_agent_skills.py
python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
python3 maintainer/scripts/analysis/validate_repo_layout.py
python3 maintainer/scripts/evaluation/test_review_loop_output_contract.py
python3 maintainer/scripts/evaluation/run_artifact_routing_tests.py --mode report --fail-on-contract-issues
python3 maintainer/scripts/evaluation/test_artifact_routing_contract.py
python3 maintainer/scripts/evaluation/test_adr_contract.py
python3 maintainer/scripts/evaluation/test_skill_catalog_contract.py
python3 maintainer/scripts/evaluation/test_token_activation_contract.py
python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens --validate-activation-contract --fail-on-budget
python3 maintainer/scripts/analysis/generate_skill_index.py --check
python3 maintainer/scripts/evaluation/compare_prompt_sizes.py
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report --fail-on-protocol-issues
```

The package and token validators use the exact versions in `token_tooling_constraints.txt`. CI additionally runs the official `skills-ref==0.1.0` pinned by immutable source commit. Trigger and routing API modes may have additional model-provider requirements; they exercise dedicated evaluation prompts, are not runtime adapter tests, and do not prove raw-model behavior from the actual Skill packages.

## Prompt Optimization

- `python3 maintainer/scripts/analysis/generate_skill_index.py`
- `python3 maintainer/scripts/evaluation/compare_prompt_sizes.py`
- `python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens --validate-activation-contract --fail-on-budget`

Prompt measurements must distinguish discovery metadata, an activated `SKILL.md`, and optional supporting files. Do not report an all-files sum as the normal per-turn cost.
