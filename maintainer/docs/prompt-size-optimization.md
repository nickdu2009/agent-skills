# Compact Skill Metadata

The trigger evaluator has two metadata loading paths:

- Default mode reads `name` and `description` from each canonical `skills/*/SKILL.md`.
- `--compact-mode` reads the same fields from `maintainer/data/skill_index.json`.

The compact index reduces filesystem parsing work and provides a reviewable metadata snapshot. It does **not** reduce the LLM prompt: both modes must expose byte-identical Skill names and descriptions. Any prompt-size difference indicates a stale index or parsing mismatch.

## Use

```bash
python3 maintainer/scripts/analysis/generate_skill_index.py
python3 maintainer/scripts/evaluation/compare_prompt_sizes.py --detailed
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report --fail-on-protocol-issues
```

Use default mode while editing frontmatter so local changes are read immediately. Use compact mode only after regenerating and reviewing the index.

## Current contract

- Canonical packages: 12 (recommended core 10 plus optional 2).
- Trigger matrix: 101 unique cases.
- Default and compact discovery blocks: exact content parity.
- Prompt comparison output is a lightweight characters/4 estimate, not the canonical repository token metric.
- Canonical token accounting uses `o200k_base` through `measure_prompt_surface.py --actual-tokens`.

The operational token baseline is `maintainer/data/token_efficiency_baseline.json`; do not infer runtime savings from JSON file size or metadata-loading speed.

## Maintenance

Regenerate `skill_index.json` after adding, removing, renaming, or changing the description of a Skill. CI validates the canonical packages and trigger matrix; `compare_prompt_sizes.py` is the direct parity check for the two loading paths.
