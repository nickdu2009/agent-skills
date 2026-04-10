# Token Efficiency Baseline Report

**Date:** 2026-04-11  
**Purpose:** Establish baseline measurements for token efficiency optimization

## Executive Summary

This baseline captures the prompt surface area across governance templates, skill documentation, and evaluation infrastructure. Total prompt surface measured: **~233KB** text across templates, governance, and skills.

**Key Findings:**
- 18 skills with average 254 lines/skill
- 1 skill over 500-line target (phase-plan-review: 521 lines)
- 9/18 skills (50%) pass all quality checks
- Governance templates inject 264 lines (11.5KB) into every project

## Measurement Details

### 1. Governance Templates

Templates injected into every new project:

| File | Lines | Characters | Bytes |
|------|-------|------------|-------|
| AGENTS-template.md | 135 | 6,128 | 6,154 |
| CLAUDE-template.md | 129 | 5,354 | 5,374 |
| **Total** | **264** | **11,482** | **11,528** |

### 2. Generated Governance

Actual governance files in root (includes skill chain triggers and protocol details):

| File | Lines | Characters | Bytes |
|------|-------|------------|-------|
| AGENTS.md | 141 | 7,613 | 7,625 |
| CLAUDE.md | 197 | 11,030 | 11,116 |
| **Total** | **338** | **18,643** | **18,741** |

**Expansion ratio:** Generated governance is 28% larger than templates (338 vs 264 lines).

### 3. Skill Documentation

18 skills total, measuring body content (excluding frontmatter):

| Metric | Value |
|--------|-------|
| Total files | 18 |
| Total lines | 4,576 |
| Total characters | 202,931 |
| Total bytes | 203,185 |
| Average lines/skill | 254.2 |
| Max body lines | 521 (phase-plan-review) |
| Skills over 500 lines | 1 |

#### Top 10 Skills by Size (Body Lines)

| Skill | Body Lines | Over 500? |
|-------|------------|-----------|
| phase-plan-review | 521 | ✗ OVER |
| phase-plan | 396 | ✓ |
| phase-execute | 377 | ✓ |
| multi-agent-protocol | 341 | ✓ |
| design-before-plan | 336 | ✓ |
| context-budget-awareness | 278 | ✓ |
| phase-contract-tools | 224 | ✓ |
| incremental-delivery | 203 | ✓ |
| self-review | 191 | ✓ |
| minimal-change-strategy | 186 | ✓ |

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

## Token Efficiency Implications

### Current State

1. **Governance overhead:** Every project gets 338 lines (18.7KB) of governance injected
2. **Skill activation cost:** Loading a skill adds 170-521 lines depending on which skill
3. **Average skill cost:** 254 lines per skill loaded
4. **Quality variance:** 50% of skills meet quality guidelines, 50% need improvement

### Optimization Opportunities

Based on this baseline, the following optimization vectors are identified:

1. **Governance compression** - 28% expansion from template to generated (264→338 lines) suggests redundancy
2. **Skill length reduction** - 1 skill over target, 4 skills near target (336-396 lines)
3. **Description quality** - 9 skills need description improvements
4. **Structure simplification** - 4 skills have deep nesting that could be flattened

### Measurement Assumptions

- **Token approximation:** Using line count and character count as proxy for tokens (actual token count ~1.3× character count ÷ 4)
- **Generated governance:** Measured from root AGENTS.md/CLAUDE.md, not actual project generation
- **Prompt surface:** Does not include Claude Code system prompts, only project-specific governance
- **Quality checks:** Heuristic-based, not semantic analysis

## Usage for Other Agents

### For Documentation Agent

Use this baseline to prioritize which skills need description and structure improvements:
- **High priority:** phase-plan-review (over 500 lines + quality issues)
- **Medium priority:** context-budget-awareness, design-before-plan, minimal-change-strategy (deep structure)
- **Low priority:** Skills passing all checks

### For Governance Agent

Use template measurements to optimize governance injection:
- Current: 264 template lines → 338 generated lines (28% expansion)
- Target: Reduce expansion ratio by eliminating redundancy
- Focus: Skill chain triggers section (likely candidate for compression)

### For Evaluation Agent

Use these baselines as targets:
- **Governance:** Should not exceed 350 lines after optimization
- **Average skill:** Target 200 lines (current: 254)
- **Max skill:** Target 450 lines (current: 521)
- **Quality passing rate:** Target 80% (current: 50%)

## Validation Commands

Reproduce these measurements:

```bash
# Generate baseline measurements
python3 maintainer/scripts/analysis/measure_prompt_surface.py

# Check quality metrics
python3 maintainer/scripts/analysis/check_skill_quality.py

# Get JSON output for programmatic analysis
python3 maintainer/scripts/analysis/measure_prompt_surface.py --json
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
