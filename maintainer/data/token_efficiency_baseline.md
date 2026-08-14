# Token Efficiency Baseline

**Date:** 2026-08-13

**Scope:** canonical `skills/` packages plus repository-only `AGENTS.md`

**Measurement contract version:** `1.0`

**Token counter:** `tiktoken`

**Counter version:** `0.13.0`

**Tokenizer:** `o200k_base`

Machine-readable source of truth: `maintainer/data/token_efficiency_baseline.json`. This document explains how to interpret that snapshot.

## Current Snapshot

| Surface | Tokens | Interpretation |
| --- | ---: | --- |
| Discovery metadata for all 12 Skills | 990 | Repository representation of `name` + `description`; runtime wrappers may differ |
| Discovery metadata for core 10 | 840 | Recommended default set; optional Skills remain standard packages |
| All 12 `SKILL.md` files | 18,084 | Sum for authoring and comparison, not a normal per-turn load |
| 28 supporting text files | 6,039 | Read only when the activated Skill and scenario require them |
| All package text | 24,123 | Theoretical full-load upper bound |
| Root `AGENTS.md` | 3,480 | Internal repository governance; not distributed with Skills |
| Everything above | 27,603 | Repository analysis ceiling, not an expected request cost |

Average `SKILL.md` size is 1,507 tokens. The largest Skill body is 2,261 tokens (`requirement-interview`), whose complete main file is 2,364 tokens including frontmatter. The largest complete package is `implementation-planning` at 3,161 tokens when every supporting file is counted. Mandatory activation scenarios top out at 2,974 tokens for a typical path and 3,028 tokens for a heavy path.

## Correct Runtime Interpretation

Agent Skills progressive loading means the normal cost has three stages:

1. Discovery: the runtime exposes Skill metadata.
2. Activation: it reads the selected `SKILL.md`.
3. Task-specific expansion: it reads only referenced supporting files needed for that scenario.

Therefore, 24,123 tokens is a safety ceiling for an artificial “load every package file” case. A typical single-Skill task should be estimated as discovery metadata plus one activated `SKILL.md` plus the supporting files selected by that Skill's reference manifest.

## Regression Targets

- 12/12 Skills pass repository quality checks.
- No broken cross-references.
- No Skill body exceeds 500 lines.
- Total `SKILL.md` tokens should not grow by more than 5% without an explicit content reason.
- New supporting material must have a conditional read path; moving always-required content out of `SKILL.md` is not counted as a saving.
- Release budgets are enforced by `maintainer/data/token_activation_contract.json`: discovery ≤1,300, all main files ≤29,000, typical activation ≤3,000, heavy/worst activation ≤5,000, and all package text ≤35,000.

## Reproduce

```bash
python3 maintainer/scripts/analysis/measure_prompt_surface.py \
  --actual-tokens --validate-activation-contract --fail-on-budget --json
python3 maintainer/scripts/analysis/check_skill_quality.py --json
python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
```
