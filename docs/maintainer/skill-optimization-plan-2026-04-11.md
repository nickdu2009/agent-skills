# Skill Optimization Execution Plan

**Date**: 2026-04-11  
**Analysis**: skill-optimization-analysis-2026-04-11.md  
**Execution Mode**: Multi-agent parallel (Tier 2)  
**Status**: Ready for execution

## Execution Strategy

### Multi-Agent Declaration

```
[delegate: 4 | split: by optimization category | risk: low]
```

**Rationale**:
- 4 independent optimization categories with disjoint scopes
- Each category has clear acceptance criteria
- Risk is low: no API changes, no logic changes, only documentation optimization
- Write scopes are disjoint (different sections of different files)
- Can validate independently before merge

### Split Design

| Agent | Responsibility | Edit Scope | Validation |
|-------|---------------|------------|------------|
| **Agent 1** | P0: Line count + Chain aliases | phase-plan-review + composition sections | Line count check + grep verify |
| **Agent 2** | P1: Description optimization | All SKILL.md frontmatter | Word count check + trigger validation |
| **Agent 3** | P2: Anti-patterns + Protocol blocks | Anti-pattern sections + protocol examples | Format check + word count |
| **Agent 4** | P2: Contract efficiency | Contract sections in all skills | Template compliance check |

**Primary Agent**: Coordinates execution, performs final validation, commits results

## Detailed Work Breakdown

### Agent 1: Critical Fixes (P0)

**Objective**: Fix phase-plan-review line count violation and standardize chain alias usage

**Scope**:
- `skills/phase-plan-review/SKILL.md` (reduce to ≤500 lines)
- Composition sections in:
  - `skills/minimal-change-strategy/SKILL.md`
  - `skills/conflict-resolution/SKILL.md`
  - Any other skills with detailed "Combine with" lists

**Edit Permission**: Full (may need to create reference files for phase-plan-review)

**Tasks**:

1. **phase-plan-review optimization**:
   - Identify content suitable for extraction (≥30 lines)
   - Create reference file(s) in `skills/phase-plan-review/references/` if needed
   - Update SKILL.md with references
   - Verify line count ≤500

2. **Chain alias standardization**:
   - Search all skills for "Combine with" patterns
   - Replace detailed composition lists with chain alias references
   - Format: "Part of `chain-name` chain. See docs/maintainer/skill-chain-aliases.md"
   - Preserve any unique composition notes not in chain aliases

**Validation**:
```bash
# Line count check
wc -l skills/phase-plan-review/SKILL.md | awk '{if ($1 > 500) exit 1}'

# Chain alias verification
grep -r "Combine with" skills/*/SKILL.md && exit 1 || exit 0

# Should use chain references instead
grep -r "Part of.*chain" skills/*/SKILL.md
```

**Expected Output**:
- phase-plan-review: 450-490 lines
- 3-5 skills updated with chain alias references
- Token savings: ~250-350 tokens

### Agent 2: Description Optimization (P1)

**Objective**: Optimize all skill descriptions to 100-200 word guideline with clear triggers

**Scope**:
- Frontmatter `description:` field in all 18 SKILL.md files

**Edit Permission**: Full (frontmatter only)

**Tasks**:

1. **Expand short descriptions** (<40 words):
   - `bugfix-workflow`: Add specific trigger scenarios (e.g., "intermittent failures", "test passes but production fails")
   - `safe-refactor`: Add concrete examples (e.g., "extract duplicate code", "consolidate similar functions")
   - `conflict-resolution`: Add discovery keywords

2. **Simplify long descriptions** (>70 words):
   - `minimal-change-strategy`: Move edge cases to "When Not to Use" section in body
   - `read-and-locate`: Simplify while preserving key triggers

3. **Verify all descriptions**:
   - Written in third person
   - Include both "what" and "when"
   - No XML tags, reserved words
   - ≤1024 characters

**Validation**:
```bash
# Word count check
for skill in skills/*/SKILL.md; do
  words=$(sed -n '/^description:/,/^[a-z_]*:/p' "$skill" | head -1 | wc -w)
  name=$(basename $(dirname "$skill"))
  echo "$name: $words words"
done

# All should be in range 40-100 words
# Third person check (manual review)
```

**Expected Output**:
- 5 descriptions expanded
- 2 descriptions simplified
- All descriptions in 40-100 word range
- Improved skill discovery clarity

### Agent 3: Format Standardization (P2)

**Objective**: Standardize anti-pattern format and migrate protocol blocks to v2

**Scope**:
- "Common Anti-Patterns" sections in all skills
- Protocol block examples (if present)

**Edit Permission**: Full (specific sections only)

**Tasks**:

1. **Anti-pattern audit**:
   - Verify all anti-patterns use: `**[Name].** [Description]. [Consequence].`
   - Ensure each pattern is 30-50 words
   - Check all skills include "See skill-anti-pattern-template.md" reference
   - Adjust wording if needed to meet word count

2. **Protocol block migration**:
   - Search for verbose protocol v1 blocks (multi-line YAML format)
   - Convert to v2 compact format where appropriate
   - Keep v1 for complex examples that benefit from verbosity
   - Document which examples were converted

3. **Consistency check**:
   - All anti-patterns follow same punctuation style
   - Protocol references use consistent terminology

**Validation**:
```bash
# Anti-pattern format check
grep -A 2 "^# Common Anti-Patterns" skills/*/SKILL.md | grep "^\*\*.*\.\*\*"

# Protocol v2 usage
grep -r "\[task-validation:" skills/*/SKILL.md

# Reference presence
grep -r "skill-anti-pattern-template.md" skills/*/SKILL.md
```

**Expected Output**:
- All anti-patterns in standard format
- 0-5 protocol blocks migrated to v2 (if found)
- Token savings: ~150-250 tokens (from protocol migration)

### Agent 4: Contract Efficiency (P2)

**Objective**: Optimize contract sections for clarity and token efficiency

**Scope**:
- "## Contract" sections in all skills
- Subsections: Preconditions, Postconditions, Invariants, Downstream Signals

**Edit Permission**: Full (contract sections only)

**Tasks**:

1. **Apply template structure**:
   - Reference: docs/maintainer/skill-contract-template.md
   - Ensure all 4 subsections present (if applicable)
   - Start bullets with observable conditions

2. **Efficiency improvements**:
   - Use backticks for field names: `field_name`
   - Remove redundant words ("the", "that", etc.)
   - One concept per bullet
   - Avoid compound sentences
   - Specific over generic: "Narrows where edits may happen" not "provides context"

3. **Verify contract completeness**:
   - Postconditions list required output fields
   - Downstream Signals explain consumption purpose
   - No duplicate information across subsections

**Validation**:
```bash
# Structure check - all should have Contract section
grep "^## Contract" skills/*/SKILL.md

# Backtick usage for fields
grep -A 20 "^## Contract" skills/*/SKILL.md | grep '`[a-z_]*`'

# Template compliance (manual review)
```

**Expected Output**:
- 15-18 contract sections optimized
- Consistent structure across all skills
- Token savings: ~300-500 tokens

## Primary Agent Responsibilities

**During Execution**:
1. Monitor subagent progress
2. Create comprehensive test script for final validation
3. Prepare git branch structure
4. Document any scope conflicts that arise

**After Subagents Complete**:
1. Review all changes for consistency
2. Run comprehensive validation suite
3. Check for write scope overlaps
4. Verify token savings achieved
5. Create summary commit
6. Update this plan with actual results

## Validation Suite

**Primary agent will create and run**:

```bash
#!/bin/bash
# validate-skill-optimizations.sh

echo "=== Skill Optimization Validation ==="

# P0 Checks
echo "1. Line count compliance..."
for skill in skills/*/SKILL.md; do
  lines=$(wc -l < "$skill")
  if [ $lines -gt 500 ]; then
    echo "  ❌ FAIL: $skill has $lines lines (>500)"
    exit 1
  fi
done
echo "  ✅ All skills ≤500 lines"

# Chain alias check
echo "2. Chain alias usage..."
if grep -r "Combine with \`.*\` to" skills/*/SKILL.md > /dev/null; then
  echo "  ❌ FAIL: Found detailed composition prose"
  grep -r "Combine with \`.*\` to" skills/*/SKILL.md
  exit 1
fi
echo "  ✅ Using chain aliases"

# Description length check
echo "3. Description word counts..."
for skill in skills/*/SKILL.md; do
  name=$(basename $(dirname "$skill"))
  words=$(sed -n '/^description:/,/^[a-z_]*:/p' "$skill" | head -1 | sed 's/^description: *//' | wc -w)
  if [ $words -lt 30 ]; then
    echo "  ⚠️  WARN: $name has only $words words"
  elif [ $words -gt 100 ]; then
    echo "  ⚠️  WARN: $name has $words words (consider simplifying)"
  fi
done
echo "  ✅ Description check complete"

# Anti-pattern format
echo "4. Anti-pattern format..."
for skill in skills/*/SKILL.md; do
  name=$(basename $(dirname "$skill"))
  if grep "^# Common Anti-Patterns" "$skill" > /dev/null; then
    if ! grep -A 3 "^# Common Anti-Patterns" "$skill" | grep "^\*\*.*\.\*\*" > /dev/null; then
      echo "  ❌ FAIL: $name anti-patterns not in standard format"
      exit 1
    fi
  fi
done
echo "  ✅ Anti-pattern format compliant"

# Contract section presence
echo "5. Contract sections..."
for skill in skills/*/SKILL.md; do
  name=$(basename $(dirname "$skill"))
  if ! grep "^## Contract" "$skill" > /dev/null; then
    echo "  ⚠️  INFO: $name has no Contract section (may be intentional)"
  fi
done
echo "  ✅ Contract check complete"

echo ""
echo "=== All Validations Passed ==="
```

## Risk Assessment

**Risk Level**: Low

**Rationale**:
- No logic changes, only documentation optimization
- No API or interface changes
- Each category independently testable
- Easy rollback (git revert)
- No production impact

**Mitigation**:
- Comprehensive validation suite
- Agent scope isolation (disjoint sections)
- Primary agent final review
- Git branch for safe review before merge

## Success Criteria

- [ ] phase-plan-review ≤500 lines
- [ ] All composition sections use chain aliases
- [ ] All descriptions 40-100 words with clear triggers
- [ ] All anti-patterns in standard 30-50 word format
- [ ] All contract sections follow template structure
- [ ] Validation suite passes 100%
- [ ] Token savings: 600-900 tokens achieved
- [ ] No regression in skill functionality
- [ ] Commit message documents changes clearly

## Rollback Plan

If issues discovered post-merge:

1. Identify problematic skill(s)
2. `git revert <commit-hash>`
3. Create issue documenting the problem
4. Fix individually and re-validate
5. Re-apply with updated approach

## Timeline Estimate

- Agent 1 (Critical): 15-20 minutes
- Agent 2 (Descriptions): 20-25 minutes
- Agent 3 (Format): 15-20 minutes
- Agent 4 (Contracts): 20-25 minutes
- Primary review + validation: 10-15 minutes
- **Total**: 80-105 minutes (vs. 3-4 hours serial)

## Post-Execution

After successful completion:

1. Update skill-optimization-analysis-2026-04-11.md with actual results
2. Archive this plan as executed
3. Create PR or commit with summary
4. Update maintainer documentation if new patterns discovered
5. Consider adding optimization checks to CI/CD

---

**Ready for execution**: Yes  
**Blocking issues**: None  
**Next action**: Primary agent launches 4 subagents per Tier 2 protocol
