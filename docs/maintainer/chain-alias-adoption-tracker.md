# Chain Alias Adoption Tracker

**Version**: 1.0  
**Date**: 2026-04-11  
**Status**: Active

## Purpose

Track the adoption status of chain aliases across all skills, measure token savings, and guide systematic optimization.

## Audit Results

### Skills With Composition Sections (10/18)

| Skill | Current Format | Chain References | Status | Tokens (Est.) |
|-------|---------------|------------------|--------|---------------|
| bugfix-workflow | Verbose | Implied bugfix-standard | Needs alias | ~80 |
| design-before-plan | Verbose | Implied design-first | Needs alias | ~70 |
| impact-analysis | Verbose | Implied multiple | Needs alias | ~75 |
| plan-before-action | Alias | `multi-file-planned`, `design-first`, `large-task` | Optimized | ~40 |
| safe-refactor | Alias | `refactor-safe` | Optimized | ~30 |
| scoped-tasking | Alias | Multiple chains | Optimized | ~35 |
| self-review | Alias | Multiple chains | Optimized | ~30 |
| targeted-validation | Alias | Multiple chains | Optimized | ~25 |

### Skills Without Composition Sections (5/18)

Phase-related skills use domain-specific composition patterns that don't map to standard execution chains:

| Skill | Reason for Exclusion | Notes |
|-------|---------------------|-------|
| multi-agent-protocol | Has composition but uses `parallel` chain | Already optimized |
| phase-contract-tools | Phase-specific composition | Uses phase workflow references |
| phase-execute | Phase-specific composition | Uses phase workflow references |
| phase-plan | Phase-specific composition | Uses phase workflow references |

## Adoption Status Summary

- **Total skills**: 18
- **Skills with composition sections**: 10 execution skills + 4 phase skills + 1 orchestration = 15
- **Skills without composition sections**: 3 (phase skills are properly structured)
- **Phase/orchestration skills**: 5 (use domain-specific patterns, not execution chains)

**Adoption rate for execution chains**: 7/12 skills = 58.3%

## Token Analysis

### Before Optimization (Verbose Skills)

| Skill | Verbose Tokens | Notes |
|-------|---------------|-------|
| bugfix-workflow | ~80 | Lists 4 skills explicitly |
| design-before-plan | ~70 | Lists dependencies and outputs |
| impact-analysis | ~75 | Lists dependencies and outputs |
| **Total** | **~395 tokens** | |

### After Optimization (Alias Format)

Estimated format:
```markdown
## Composition

Part of [chain-name] chain (see CLAUDE.md § Skill Chain Triggers).

[Role description: 1-2 sentences]

Additional compositions:
- [Unique skill-specific relationships]
```

Estimated tokens per skill: ~20-30 tokens

| Skill | Alias Tokens | Savings |
|-------|-------------|---------|
| bugfix-workflow | ~25 | ~55 |
| design-before-plan | ~25 | ~45 |
| impact-analysis | ~25 | ~50 |
| **Total** | **~135 tokens** | **~260 tokens** |

### Current Token Usage (Already Optimized)

| Skill | Alias Tokens | Original (Est.) | Savings Achieved |
|-------|-------------|-----------------|------------------|
| plan-before-action | ~40 | ~100 | ~60 |
| safe-refactor | ~30 | ~85 | ~55 |
| scoped-tasking | ~35 | ~90 | ~55 |
| self-review | ~30 | ~85 | ~55 |
| targeted-validation | ~25 | ~80 | ~55 |
| **Total** | **~240 tokens** | **~690 tokens** | **~450 tokens** |

## Total Impact Projection

| Metric | Value |
|--------|-------|
| Already saved (7 skills) | ~450 tokens |
| Additional savings potential (5 skills) | ~260 tokens |
| **Total savings (all 12 execution skills)** | **~710 tokens** |
| Pre-optimization total | ~1,085 tokens |
| Post-optimization total | ~375 tokens |
| **Reduction** | **65.4%** |

## Skills Requiring Optimization

### High Priority (Core Execution Chains)

1. **bugfix-workflow**
   - Current: Verbose "Combine with" listing
   - Target: `bugfix-standard` chain alias
   - Role: Core diagnostic component
   - Estimated savings: ~55 tokens

2. **design-before-plan**
   - Current: Verbose dependencies/outputs listing
   - Target: `design-first` and `large-task` chain aliases
   - Role: Entry point for design-first chain
   - Estimated savings: ~45 tokens

3. **impact-analysis**
   - Current: Verbose dependencies/outputs listing
   - Target: `large-task` chain alias
   - Role: Core component in large-task chain
   - Estimated savings: ~50 tokens

### Medium Priority (Supporting Skills)

   - Current: Verbose "Combine with" listing
   - Target: Cross-chain fallback references
   - Role: Fallback skill for multiple chains
   - Estimated savings: ~60 tokens

   - Current: Verbose dependencies listing
   - Target: `large-task` chain alias
   - Role: Exit point for large-task chain
   - Estimated savings: ~50 tokens

## Chain Mapping

### Canonical Chains from CLAUDE.md

| Chain Alias | Full Chain | Skills Involved |
|-------------|-----------|-----------------|

### Skills by Chain Participation

| Skill | Chains | Role |
|-------|--------|------|
| scoped-tasking | All execution chains | Entry point |
| targeted-validation | bugfix-standard, refactor-safe, multi-file-planned, design-first | Exit point |
| self-review | bugfix-standard, refactor-safe, multi-file-planned, design-first | Pre-validation gate |
| plan-before-action | multi-file-planned, design-first, large-task | Planning component |
| bugfix-workflow | bugfix-standard | Core diagnostic |
| safe-refactor | refactor-safe | Core refactor component |
| design-before-plan | design-first, large-task | Design component |
| impact-analysis | large-task | Impact assessment |

## Optimization Checklist

For each skill requiring optimization:

- [ ] bugfix-workflow
  - [ ] Identify applicable chains: bugfix-standard
  - [ ] Define role: core diagnostic component
  - [ ] Replace verbose listing with alias reference
  - [ ] Preserve unique skill-specific compositions
  - [ ] Measure before/after tokens
  - [ ] Verify CLAUDE.md alignment

  - [ ] Identify applicable chains: fallback for multiple chains
  - [ ] Define role: cross-chain context management
  - [ ] Replace verbose listing with fallback references
  - [ ] Preserve unique skill-specific compositions
  - [ ] Measure before/after tokens
  - [ ] Verify CLAUDE.md alignment

- [ ] design-before-plan
  - [ ] Identify applicable chains: design-first, large-task
  - [ ] Define role: entry point for design-first, design component for large-task
  - [ ] Replace verbose listing with alias references
  - [ ] Preserve unique skill-specific compositions
  - [ ] Measure before/after tokens
  - [ ] Verify CLAUDE.md alignment

- [ ] impact-analysis
  - [ ] Identify applicable chains: large-task
  - [ ] Define role: core impact assessment component
  - [ ] Replace verbose listing with alias reference
  - [ ] Preserve unique skill-specific compositions
  - [ ] Measure before/after tokens
  - [ ] Verify CLAUDE.md alignment

  - [ ] Identify applicable chains: large-task
  - [ ] Define role: exit point (delivery orchestration)
  - [ ] Replace verbose listing with alias reference
  - [ ] Preserve unique skill-specific compositions
  - [ ] Measure before/after tokens
  - [ ] Verify CLAUDE.md alignment

## Quality Validation

After optimization:

- [ ] All chain alias references resolve to CLAUDE.md § Skill Chain Triggers
- [ ] No broken links between skills
- [ ] Role descriptions accurately reflect skill position in chain
- [ ] Unique skill-specific compositions are preserved
- [ ] Token savings match estimates (±20%)
- [ ] No regressions in skill functionality

## Next Steps

1. **Phase 2**: Apply chain aliases to 5 remaining verbose skills
2. **Phase 3**: Optimize existing alias references (7 skills) for clarity and consistency
3. **Phase 4**: Measure actual token savings vs. estimates
4. **Phase 5**: Update skill-chain-aliases.md with adoption metrics
5. **Phase 6**: Create chain-alias-maintenance.md guide

## Notes

- multi-agent-protocol is correctly using the `parallel` chain alias.
- Context-budget-awareness is a cross-chain fallback skill and may need special treatment in chain alias references.
