# Token Efficiency Baseline Report

**Date:** 2026-04-11  
**Purpose:** Establish baseline measurements for token efficiency optimization  
**Token Counting:** tiktoken cl100k_base (actual token counts)

## Executive Summary

This baseline captures the prompt surface area across governance templates, skill documentation, and evaluation infrastructure. Total prompt surface measured: **~52,600 tokens** (**~247KB** text) across templates, governance, and skills.

**Key Findings:**
- 18 skills with average 2,341 tokens/skill (~251 lines)
- 0 skills over 500-line target (max: phase-plan-review at 464 lines)
- 9/18 skills (50%) pass all quality checks
- Governance templates inject 4,556 tokens (444 lines, ~18.9KB) into every project
- Character-based estimate overestimates by ~17% (use `--actual-tokens` for precision)

## Measurement Details

### 1. Governance Templates

Templates injected into every new project:

| File | Lines | Characters | Tokens | Bytes |
|------|-------|------------|--------|-------|
| AGENTS-template.md | 222 | 9,471 | 2,277 | 9,509 |
| CLAUDE-template.md | 222 | 9,471 | 2,279 | 9,509 |
| **Total** | **444** | **18,942** | **4,556** | **19,018** |

### 2. Generated Governance

Actual governance files in root (includes skill chain triggers and protocol details):

| File | Lines | Characters | Tokens | Bytes |
|------|-------|------------|--------|-------|
| AGENTS.md | 321 | 15,515 | 3,358 | 15,559 |
| CLAUDE.md | 197 | 11,030 | 2,554 | 11,116 |
| **Total** | **518** | **26,545** | **5,912** | **26,675** |

**Expansion ratio:** Generated governance is 17% larger than templates (518 vs 444 lines, 5,912 vs 4,556 tokens).

### 3. Skill Documentation

18 skills total, measuring body content (excluding frontmatter):

| Metric | Value |
|--------|-------|
| Total files | 18 |
| Total lines | 4,525 |
| Total characters | 201,773 |
| Total tokens | 42,139 |
| Total bytes | 202,009 |
| Average lines/skill | 251.4 |
| Average tokens/skill | 2,341 |
| Max body lines | 464 (phase-plan-review) |
| Max body tokens | 5,177 (phase-plan-review) |
| Skills over 500 lines | 0 |

#### Top 10 Skills by Size (Body Tokens)

| Skill | Body Lines | Body Tokens | Over 500 Lines? |
|-------|------------|-------------|-----------------|
| phase-plan-review | 464 | 5,177 | ✓ |
| phase-plan | 396 | 4,012 | ✓ |
| phase-execute | 379 | 3,965 | ✓ |
| design-before-plan | 336 | 3,547 | ✓ |
| multi-agent-protocol | 341 | 2,997 | ✓ |
| context-budget-awareness | 278 | 2,719 | ✓ |
| phase-contract-tools | 226 | 2,659 | ✓ |
| incremental-delivery | 203 | 1,701 | ✓ |
| self-review | 193 | 1,675 | ✓ |
| impact-analysis | 184 | 1,542 | ✓ |

### 4. Evaluation Prompts

Trigger test infrastructure:

| File | Lines | Characters | Bytes |
|------|-------|------------|-------|
| run_trigger_tests.py | 499 | 17,071 | 17,079 |

**Note:** Full prompt size depends on runtime test data. The script constructs prompts dynamically from skill descriptions and test cases.

## Quality Check Results

**Overall:** 9/18 skills (50%) pass all quality checks.

### Quality Criteria

1. **Description has "what" + "when" triggers** - Helps LLM understand both purpose and activation conditions
2. **Third-person phrasing** - Avoids first-person ("I", "we") and uses action verbs
3. **Body length under 500 lines** - Target guideline for maintainability
4. **Shallow reference structure** - Avoids deep nesting (heading level ≤3, bullet indent ≤4)

### Skills with Quality Issues (9)

| Skill | Issues |
|-------|--------|
| bugfix-workflow | ✗ Third-person phrasing |
| context-budget-awareness | ✗ "what" missing, ✗ Third-person, ✗ Deep structure (indent=6) |
| design-before-plan | ✗ Deep structure (indent=6) |
| minimal-change-strategy | ✗ Deep structure (indent=5) |
| multi-agent-protocol | ✗ "what" missing, ✗ Third-person |
| phase-contract-tools | ✗ Third-person phrasing |
| phase-execute | ✗ "when" missing |
| phase-plan-review | ✗ "when" missing, ✗ Over 500 lines (+21), ✗ Deep structure (heading=4) |
| self-review | ✗ "when" missing |

### Skills Passing All Checks (9)

✓ conflict-resolution (168 lines)  
✓ impact-analysis (184 lines)  
✓ incremental-delivery (203 lines)  
✓ phase-plan (396 lines)  
✓ plan-before-action (182 lines)  
✓ read-and-locate (177 lines)  
✓ safe-refactor (170 lines)  
✓ scoped-tasking (181 lines)  
✓ targeted-validation (170 lines)

## Token Counting Methodology

This baseline uses **tiktoken** with the `cl100k_base` encoding (used by GPT-4 and Claude 3+) for precise token counts.

### Character vs Token Estimation

**Character-based estimate:** Divide character count by 4 (rough heuristic)  
**Actual observation:** ~4.69 characters per token (actual ratio)  
**Accuracy:** Character-based estimate overestimates by ~17%

| Component | Char Estimate | Actual Tokens | Error |
|-----------|---------------|---------------|-------|
| Governance templates | 4,735 | 4,556 | +3.9% |
| Generated governance | 6,636 | 5,912 | +12.2% |
| Skill files | 50,274 | 42,139 | +19.3% |

**Recommendation:** Use `--actual-tokens` flag for precise measurements and CI baselines. Character-based estimates provide a conservative upper bound for quick checks.

### Baseline Enforcement Thresholds

| Metric | Baseline | Warning (+10%) | Fail (+20%) |
|--------|----------|----------------|-------------|
| Governance templates tokens | 4,556 | 5,012 | 5,467 |
| Average skill tokens | 2,341 | 2,575 | 2,809 |
| Max skill body tokens | 5,177 | 5,695 | 6,212 |
| Skills over 500 lines | 0 | 1 | 2 |

## Token Efficiency Implications

### Current State

1. **Governance overhead:** Every project gets 5,912 tokens (518 lines, ~26.5KB) of governance injected
2. **Skill activation cost:** Loading a skill adds 1,173-5,177 tokens depending on which skill
3. **Average skill cost:** 2,341 tokens per skill loaded
4. **Quality variance:** 50% of skills meet quality guidelines, 50% need improvement

### Optimization Opportunities

Based on this baseline, the following optimization vectors are identified:

1. **Governance compression** - 17% expansion from template to generated (4,556→5,912 tokens) suggests some redundancy
2. **Skill length reduction** - 0 skills over 500-line target, but 4 skills near 400 lines (phase-plan-review, phase-plan, phase-execute, design-before-plan)
3. **Description quality** - 9 skills need description improvements
4. **Structure simplification** - 4 skills have deep nesting that could be flattened

### Measurement Methodology

- **Token counting:** tiktoken cl100k_base encoding (precise, not estimated)
- **Generated governance:** Measured from root AGENTS.md/CLAUDE.md, not actual project generation
- **Prompt surface:** Does not include Claude Code system prompts, only project-specific governance
- **Quality checks:** Heuristic-based, not semantic analysis

## Usage for Other Agents

### For Documentation Agent

Use this baseline to prioritize which skills need description and structure improvements:
- **High priority:** phase-plan-review (5,177 tokens, quality issues)
- **Medium priority:** context-budget-awareness, design-before-plan, minimal-change-strategy (deep structure)
- **Low priority:** Skills passing all checks

### For Governance Agent

Use template measurements to optimize governance injection:
- Current: 4,556 template tokens → 5,912 generated tokens (17% expansion)
- Target: Reduce expansion ratio by eliminating redundancy
- Focus: Skill chain triggers section (likely candidate for compression)

### For Evaluation Agent

Use these baselines as targets:
- **Governance:** Should not exceed 6,500 tokens after optimization
- **Average skill:** Target 2,200 tokens (current: 2,341)
- **Max skill:** Target 5,000 tokens (current: 5,177)
- **Quality passing rate:** Target 80% (current: 50%)

## Validation Commands

Reproduce these measurements:

```bash
# Generate baseline measurements with actual token counts (RECOMMENDED)
python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens

# Quick character-based estimate (faster but less accurate)
python3 maintainer/scripts/analysis/measure_prompt_surface.py

# Check quality metrics
python3 maintainer/scripts/analysis/check_skill_quality.py

# Compare token counting methods
python3 maintainer/scripts/analysis/compare_token_methods.py \
  --estimate metrics_char_estimate.json \
  --actual metrics_actual_tokens.json

# Get JSON output for programmatic analysis
python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens --json
python3 maintainer/scripts/analysis/check_skill_quality.py --json
```

## Next Steps

1. **Governance agent:** Compress templates and reduce expansion ratio
2. **Documentation agent:** Fix 9 skills failing quality checks
3. **Evaluation agent:** Update scripts to validate against these baselines
4. **All agents:** Re-measure after Phase 1 optimizations to track progress

---

**Baseline established:** 2026-04-11  
**Measurement scripts:** `maintainer/scripts/analysis/measure_prompt_surface.py`, `check_skill_quality.py`  
**Re-measurement cadence:** After each optimization phase
