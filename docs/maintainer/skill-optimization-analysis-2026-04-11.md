# Skill Optimization Analysis

**Date**: 2026-04-11  
**Scope**: All 18 skills in repository  
**Reference**: docs/maintainer/claude-skill-authoring-best-practices.md  
**Status**: Analysis Complete

## Executive Summary

Found 6 categories of optimization opportunities across 18 skills, with estimated total token savings of **600-900 tokens** (52% reduction in affected sections). One critical issue (phase-plan-review exceeds 500 lines) and multiple consistency improvements needed.

## Findings by Priority

### 🔴 P0 - Critical (Must Fix)

#### 1. Line Count Violation

**Issue**: phase-plan-review exceeds recommended maximum  
**Current**: 530 lines  
**Target**: ≤500 lines  
**Impact**: Performance degradation, slower loading  
**Recommendation**: Split content into reference files

**File**: `skills/phase-plan-review/SKILL.md`

### 🟡 P1 - High Priority (Should Fix)

#### 2. Chain Alias Inconsistency

**Issue**: Skills use detailed composition prose instead of chain aliases  
**Token Impact**: ~60-70 tokens per skill  
**Affected Skills**: 2-4 skills

**Examples Found**:

**minimal-change-strategy** (lines 95-97):
```markdown
Additional composition:
- Combine with `scoped-tasking` to keep the patch boundary honest
- Combine with `plan-before-action` to declare intended edits before changing files
- Combine with `targeted-validation` to verify the patch without paying full-suite cost
```
Token cost: ~80-100 tokens

**Should be**:
```markdown
Additional composition:
- See `bugfix-standard`, `refactor-safe`, `multi-file-planned`, `design-first` chains
- Full definitions: docs/maintainer/skill-chain-aliases.md
```
Token cost: ~25-30 tokens  
**Savings**: 60-70 tokens per skill

**Files to Check**:
- skills/minimal-change-strategy/SKILL.md
- skills/conflict-resolution/SKILL.md (lines ~100+)
- Any other skills with "Combine with" lists

#### 3. Description Field Length Issues

**Issue**: Descriptions don't meet 100-200 word guideline for optimal discovery

**Too Short** (<40 words - may lack trigger clarity):

| Skill | Word Count | Issue |
|-------|-----------|-------|
| bugfix-workflow | 28 | Missing specific trigger scenarios |
| safe-refactor | 29 | Lacks concrete "when to use" examples |
| conflict-resolution | 34 | Could add more discovery keywords |

**Too Long** (>70 words - may be over-specified):

| Skill | Word Count | Issue |
|-------|-----------|-------|
| minimal-change-strategy | 73 | Complex condition list, may confuse discovery |
| read-and-locate | 75 | Could be simplified while keeping triggers |

**Recommendation**:
- Add 10-15 words to short descriptions with concrete trigger scenarios
- Simplify long descriptions by moving edge-case conditions to SKILL.md body

### 🟢 P2 - Medium Priority (Good to Fix)

#### 4. Anti-Pattern Format Standardization

**Issue**: Most anti-patterns follow recommended format, but word count varies

**Current State**: All checked skills use the correct structure:
```markdown
- **[Pattern name].** [Description sentence]. [Consequence sentence].
```

**Examples**:
- ✅ bugfix-workflow: Concise, ~30-40 words per pattern
- ✅ minimal-change-strategy: Good format, ~40-50 words per pattern
- ✅ scoped-tasking: Correct structure, appropriate length

**Action**: Audit all 18 skills to ensure 30-50 word range consistency

#### 5. Protocol Block Format Migration

**Issue**: May have verbose protocol v1 blocks that could use v2 compact format

**Token Impact**: ~75-90 tokens per block

**v1 Example** (~100-120 tokens):
```yaml
[task-input-validation]
task: "Fix auth bug"
checks:
  clarity:
    status: PASS
    reason: "Clear action and target"
  scope:
    status: PASS
```

**v2 Example** (~25-30 tokens):
```
[task-validation: PASS | clarity:✓ scope:✓ safety:✓ | action:proceed]
```

**Action**: Search all SKILL.md files for protocol block examples

#### 6. Contract Section Efficiency

**Issue**: Contract sections may have verbose formatting

**Target Metrics**:
- Preconditions: Start with observable conditions, not full sentences
- Field names: Use backticks (`field_name`)
- One concept per bullet
- Avoid compound sentences

**Example Optimization**:

**Before** (~80 tokens):
```markdown
- The agent has access to the working set that was defined earlier in the planning phase
```

**After** (~20 tokens):
```markdown
- Working set defined by plan-before-action is accessible
```

**Action**: Review contract sections in all skills against skill-contract-template.md

## Detailed Skill Inventory

### Line Count Distribution

```
530 lines - skills/phase-plan-review/SKILL.md     ⚠️ EXCEEDS LIMIT
405 lines - skills/phase-plan/SKILL.md
386 lines - skills/phase-execute/SKILL.md
348 lines - skills/multi-agent-protocol/SKILL.md
332 lines - skills/design-before-plan/SKILL.md
284 lines - skills/context-budget-awareness/SKILL.md
233 lines - skills/phase-contract-tools/SKILL.md
221 lines - skills/incremental-delivery/SKILL.md
206 lines - skills/impact-analysis/SKILL.md
200 lines - skills/self-review/SKILL.md
188 lines - skills/scoped-tasking/SKILL.md
188 lines - skills/plan-before-action/SKILL.md
186 lines - skills/minimal-change-strategy/SKILL.md
186 lines - skills/bugfix-workflow/SKILL.md
185 lines - skills/read-and-locate/SKILL.md
179 lines - skills/targeted-validation/SKILL.md
176 lines - skills/safe-refactor/SKILL.md
175 lines - skills/conflict-resolution/SKILL.md
```

### Description Word Count Distribution

```
28 words - bugfix-workflow               ⚠️ TOO SHORT
29 words - safe-refactor                 ⚠️ TOO SHORT
34 words - conflict-resolution           ⚠️ TOO SHORT
44 words - design-before-plan            ✅ OK
44 words - phase-plan-review             ✅ OK
45 words - targeted-validation           ✅ OK
46 words - phase-plan                    ✅ OK
46 words - plan-before-action            ✅ OK
48 words - incremental-delivery          ✅ OK
48 words - multi-agent-protocol          ✅ OK
49 words - phase-execute                 ✅ OK
51 words - self-review                   ✅ OK
54 words - impact-analysis               ✅ OK
59 words - context-budget-awareness      ✅ OK
65 words - scoped-tasking                ✅ OK
73 words - minimal-change-strategy       ⚠️ TOO LONG
75 words - read-and-locate               ⚠️ TOO LONG
43 words - phase-contract-tools          ✅ OK
```

## Token Savings Estimate

| Optimization Category | Skills Affected | Per-Skill Savings | Total Savings |
|----------------------|-----------------|-------------------|---------------|
| Chain aliases | 4-6 | 60-70 tokens | 300-400 tokens |
| Protocol v2 format | TBD | 75-90 tokens | TBD (needs audit) |
| Contract efficiency | 8-10 | 30-50 tokens | 300-500 tokens |
| **Total Estimate** | | | **600-900 tokens** |

Additional benefits:
- Improved consistency across skills
- Better skill discovery (optimized descriptions)
- Reduced cognitive load for maintainers
- Compliance with official Anthropic best practices

## Reference Documents

- **Best Practices**: docs/maintainer/claude-skill-authoring-best-practices.md
- **Chain Aliases**: docs/maintainer/skill-chain-aliases.md
- **Contract Template**: docs/maintainer/skill-contract-template.md
- **Anti-Pattern Template**: docs/maintainer/skill-anti-pattern-template.md
- **Protocol v2**: docs/maintainer/protocol-v2-compact.md

## Next Steps

See `skill-optimization-plan-2026-04-11.md` for detailed execution plan.
