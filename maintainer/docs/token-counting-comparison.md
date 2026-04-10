# Token Counting Method Comparison

**Date:** 2026-04-11  
**Purpose:** Compare character-based estimates vs actual tiktoken counts

## Summary

This document compares two token counting methods:

1. **Character-based estimate:** Divide character count by 4 (fast, approximate)
2. **Actual tiktoken:** Use tiktoken cl100k_base encoding (precise, requires library)

## Key Findings

- **Overall accuracy:** Character-based estimate overestimates by ~17%
- **Observed ratio:** 4.69 characters per token (vs assumed 4.0)
- **Recommendation:** Use `--actual-tokens` for precise baselines and CI enforcement

## Detailed Comparison

### Governance Templates

| Metric | Character Estimate | Actual Tokens | Error |
|--------|-------------------|---------------|-------|
| AGENTS-template.md | 2,368 | 2,277 | +4.0% |
| CLAUDE-template.md | 2,368 | 2,279 | +3.9% |
| **Total** | **4,735** | **4,556** | **+3.9%** |

### Generated Governance

| Metric | Character Estimate | Actual Tokens | Error |
|--------|-------------------|---------------|-------|
| AGENTS.md | 3,879 | 3,358 | +15.5% |
| CLAUDE.md | 2,758 | 2,554 | +8.0% |
| **Total** | **6,636** | **5,912** | **+12.2%** |

### Skill Files (Total)

| Metric | Character Estimate | Actual Tokens | Error |
|--------|-------------------|---------------|-------|
| Total (18 skills) | 50,274 | 42,139 | +19.3% |
| Average per skill | 2,793 | 2,341 | +19.3% |

### Skills with Largest Estimation Errors

| Skill | Char Estimate | Actual Tokens | Error % |
|-------|---------------|---------------|---------|
| safe-refactor | 1,513 | 1,173 | +29.0% |
| minimal-change-strategy | 1,856 | 1,449 | +28.1% |
| design-before-plan | 4,482 | 3,547 | +26.4% |
| targeted-validation | 1,625 | 1,290 | +26.0% |
| conflict-resolution | 1,810 | 1,448 | +25.0% |

## Why Character-Based Estimates Overestimate

The character-based estimate assumes 4.0 characters per token, but actual observation shows **4.69 characters per token**. This is because:

1. **Markdown syntax:** Headings, lists, code blocks use fewer tokens than raw character count suggests
2. **Whitespace:** Indentation and spacing are tokenized efficiently
3. **Common words:** Technical terms and repeated patterns compress well in tokenization

## Recommendations

### For Local Development

**Quick checks:** Use character-based estimate for fast iteration
```bash
python3 maintainer/scripts/analysis/measure_prompt_surface.py
```

**Precision needed:** Use actual token counts before committing changes
```bash
python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens
```

### For CI/CD Pipelines

**Always use actual token counts** for baseline enforcement:

```yaml
- name: Measure token efficiency
  run: |
    pip install tiktoken
    python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens --json > metrics.json
    python3 maintainer/scripts/analysis/check_baseline_regression.py \
      --baseline maintainer/data/token_efficiency_baseline.md \
      --current metrics.json \
      --fail-on-regression
```

### For Baseline Updates

When updating token efficiency baselines, always use actual token counts:

```bash
# Generate precise measurements
python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens

# Compare with estimates to validate accuracy
python3 maintainer/scripts/analysis/compare_token_methods.py \
  --estimate metrics_char_estimate.json \
  --actual metrics_actual_tokens.json

# Update baseline document with actual token counts
# Edit maintainer/data/token_efficiency_baseline.md with new values
```

## Observed Character-to-Token Ratios by Component

| Component | Chars/Token | Why |
|-----------|-------------|-----|
| Governance templates | 4.16 | Clean markdown, well-structured |
| Generated governance | 4.49 | Includes tables, more whitespace |
| Skill files (average) | 4.79 | Code blocks, examples, varied structure |
| Skill files (max ratio) | 5.23 | Heavy use of lists and code blocks |

## Fallback Behavior

The measurement script gracefully handles tiktoken unavailability:

```python
# If tiktoken not installed
$ python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens
Warning: --actual-tokens requires tiktoken package
Install with: pip install tiktoken
Falling back to character-based estimates...
```

This ensures the script always produces usable output, even without tiktoken installed.

## See Also

- [Token Efficiency Baseline](../data/token_efficiency_baseline.md) - Current baseline with actual token counts
- [CI Integration Guide](./ci-integration-guide.md) - How to use token counting in CI/CD
- [Prompt Size Optimization](./prompt-size-optimization.md) - Compact mode and optimization strategies
