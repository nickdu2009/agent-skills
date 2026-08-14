# Prompt Metadata Measurement

**Current snapshot:** 2026-08-13

The previous 18-Skill, 82-case, character-estimated snapshot is retired. Current measurements use the 12 canonical Agent Skills packages and 101 unique trigger cases.

## Discovery metadata

`run_trigger_tests.py` sends only each Skill's `name` and `description` in its discovery block. Default and compact modes now produce identical content:

| Mode | Source | Discovery content |
| --- | --- | --- |
| Default | `skills/*/SKILL.md` frontmatter | 12 names and descriptions |
| Compact | `maintainer/data/skill_index.json` | The same 12 names and descriptions |

The comparison utility reports character counts and a simple characters/4 estimate for parity debugging. It is not the canonical token counter and should not be used as an optimization baseline.

```bash
python3 maintainer/scripts/evaluation/compare_prompt_sizes.py --detailed
```

Expected result: `Parity: exact match` and no per-case token difference.

## Canonical token accounting

Canonical repository measurements use `o200k_base`:

| Surface | Tokens |
| --- | ---: |
| Discovery metadata for 12 Skills | 990 |
| Core-10 discovery metadata | 840 |
| All 12 `SKILL.md` files | 18,084 |
| Supporting text files | 6,039 |
| All package text upper bound | 24,123 |
| Repository `AGENTS.md` | 3,480 |
| Everything upper bound | 27,603 |

Reproduce and compare against the machine-readable baseline:

```bash
python3 maintainer/scripts/analysis/measure_prompt_surface.py \
  --actual-tokens --validate-activation-contract --fail-on-budget --json
python3 maintainer/scripts/audit/detect_regressions.py --json
```

The upper bounds are repository analysis ceilings. A normal Agent Skills request pays for discovery metadata, the activated `SKILL.md`, and only the supporting files selected by that Skill.
