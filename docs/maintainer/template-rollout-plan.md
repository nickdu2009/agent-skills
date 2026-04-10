# Template Rollout Plan

**Version**: 1.0  
**Date**: 2026-04-11  
**Status**: Active  
**Scope**: Remaining 13 skills template application strategy

## Executive Summary

Phase 1 successfully applied contract and anti-pattern templates to 5 high-duplication skills, achieving 297 tokens saved (21.2% reduction) with no quality regressions. This document outlines the rollout strategy for the remaining 13 skills.

## Phase 1 Results (Complete)

**Skills Modified**: minimal-change-strategy, bugfix-workflow, plan-before-action, safe-refactor, scoped-tasking

**Token Savings**:
- Contract sections: 212 tokens (22.8% reduction)
- Anti-pattern sections: 85 tokens (18.0% reduction)
- Total: 297 tokens saved

**Quality Validation**: All skills pass check_skill_quality.py ✓

**Key Learnings**:
1. Conservative compression maintains readability
2. Semicolon-separated preconditions work well for 3+ parallel items
3. Field:purpose format improves downstream signal clarity
4. Template references add negligible tokens but improve maintainability

## Remaining Skills: Prioritization

### Group A: High-Priority Execution Skills (5 skills)

**Rationale**: Similar contract structure to Phase 1 skills; likely to have comparable savings.

1. **context-budget-awareness**
   - Contract sections: Preconditions/Postconditions/Invariants/Signals
   - Anti-patterns: 2-3 patterns expected
   - Estimated savings: ~55-65 tokens

2. **design-before-plan**
   - Contract sections: Full standard structure
   - Anti-patterns: 2-3 patterns expected
   - Estimated savings: ~55-65 tokens

3. **impact-analysis**
   - Contract sections: Full standard structure
   - Anti-patterns: 2-3 patterns expected
   - Estimated savings: ~55-65 tokens

4. **read-and-locate**
   - Contract sections: Full standard structure
   - Anti-patterns: 2-3 patterns expected
   - Estimated savings: ~55-65 tokens

5. **targeted-validation**
   - Contract sections: Full standard structure
   - Anti-patterns: 2-3 patterns expected
   - Estimated savings: ~55-65 tokens

**Group A Total Estimated Savings**: ~275-325 tokens

**Timeline**: Apply in parallel with other agents in current session

---

### Group B: Medium-Priority Execution Skills (2 skills)

**Rationale**: Newer or more specialized skills; may have unique contract structures.

1. **incremental-delivery**
   - Contract sections: Standard structure likely
   - Anti-patterns: 2 patterns expected
   - Estimated savings: ~40-50 tokens

2. **self-review**
   - Contract sections: Standard structure likely
   - Anti-patterns: 2 patterns expected
   - Estimated savings: ~40-50 tokens

**Group B Total Estimated Savings**: ~80-100 tokens

**Timeline**: Next maintenance cycle after Group A

---

### Group C: Orchestration Skill (1 skill)

**Rationale**: Complex orchestration logic; may require custom template adaptation.

1. **multi-agent-protocol**
   - Contract sections: Likely has extended preconditions/postconditions
   - Anti-patterns: 3-4 patterns expected (coordination failures)
   - Estimated savings: ~60-80 tokens
   - **Note**: May need orchestration-specific contract addendum

**Group C Total Estimated Savings**: ~60-80 tokens

**Timeline**: After Group A; careful review for orchestration-specific needs

---

### Group D: Phase System Skills (4 skills)

**Rationale**: Tightly coupled phase system; should be updated together for consistency.

1. **phase-plan**
   - Contract sections: Phase-specific structure
   - Anti-patterns: 2-3 patterns expected
   - Estimated savings: ~40-50 tokens

2. **phase-execute**
   - Contract sections: Phase-specific structure
   - Anti-patterns: 2-3 patterns expected
   - Estimated savings: ~40-50 tokens

3. **conflict-resolution**
   - Contract sections: Standard structure likely
   - Anti-patterns: 2 patterns expected
   - Estimated savings: ~35-45 tokens

4. **phase-contract-tools**
   - Contract sections: May be minimal (shared library skill)
   - Anti-patterns: 1-2 patterns expected
   - Estimated savings: ~25-35 tokens
   - **Note**: This is a contract tool library; template application may differ

**Group D Total Estimated Savings**: ~140-180 tokens

**Timeline**: Dedicated phase system maintenance cycle

---

### Group E: Governance/Infrastructure Skills (1 skill)

**Rationale**: Governance skill; lower priority for token optimization.

1. **phase-plan-review**
   - Contract sections: Governance-focused structure
   - Anti-patterns: 2 patterns expected
   - Estimated savings: ~35-45 tokens

**Group E Total Estimated Savings**: ~35-45 tokens

**Timeline**: Low priority; apply during governance documentation updates

---

## Recommended Rollout Sequence

### Session 1: Group A (Current)
- Apply templates to 5 high-priority execution skills
- Run validation suite
- Measure token savings
- Update template-adoption-tracker.md

**Expected outcome**: ~275-325 tokens saved, cumulative 572-622 tokens

### Session 2: Group C + Group B
- Apply templates to multi-agent-protocol (careful review)
- Apply templates to incremental-delivery and self-review
- Run validation suite
- Measure token savings

**Expected outcome**: ~140-180 tokens saved, cumulative 712-802 tokens

### Session 3: Group D
- Coordinate with phase system owners
- Apply templates to all 4 phase skills together
- Run phase system integration tests
- Measure token savings

**Expected outcome**: ~140-180 tokens saved, cumulative 852-982 tokens

### Session 4: Group E
- Apply templates to phase-plan-review
- Run governance validation
- Measure token savings

**Expected outcome**: ~35-45 tokens saved, cumulative 887-1,027 tokens

---

## Total Estimated Impact

**Current (Phase 1)**: 297 tokens saved  
**After all phases**: ~887-1,027 tokens saved across 18 skills

**Percentage of original contract/anti-pattern content**: ~20-25% reduction  
**Time investment**: ~1-2 hours per group (validation included)

---

## Validation Protocol (All Groups)

For each skill in a group:

1. **Pre-validation**:
   - Read current SKILL.md
   - Measure before token counts (contract + anti-patterns sections)
   - Note any unique contract structures

2. **Template application**:
   - Apply contract template (semicolon preconditions, field:purpose signals)
   - Apply anti-pattern template (remove "The agent", two-sentence structure)
   - Add template reference footers
   - Preserve skill-specific content

3. **Post-validation**:
   - Run `check_skill_quality.py --skill <skill-name>`
   - Measure after token counts
   - Verify cross-references resolve
   - Update template-adoption-tracker.md

4. **Batch validation**:
   - After completing a group, run full suite validation
   - Check for cross-skill consistency
   - Verify no regressions in related skills

---

## Risk Mitigation

### Low-Risk Changes (Groups A, B, E)
- Standard contract structures
- Straightforward template application
- Minimal cross-skill dependencies

**Mitigation**: Follow standard validation protocol

### Medium-Risk Changes (Group C)
- Orchestration logic is complex
- May have non-standard contract fields

**Mitigation**:
1. Review multi-agent-protocol contract structure before applying template
2. Consider creating orchestration-specific contract addendum if needed
3. Validate against existing multi-agent examples
4. Test with a sample multi-agent workflow

### Higher-Risk Changes (Group D)
- Phase skills are tightly coupled
- Changes to one may affect others
- Phase system has integration tests

**Mitigation**:
1. Update all 4 phase skills in a single batch
2. Run phase system integration tests after changes
3. Validate phase plan → phase execute → conflict resolution workflow
4. Consider phase-specific template guidance document

---

## Exception Handling

### When NOT to Apply Templates

1. **Unique contract structures**: If a skill has a non-standard contract that doesn't fit the template, document the exception
2. **Minimal content**: If a skill has 1-2 preconditions, template application may not save tokens
3. **Governance skills**: If template application reduces clarity for governance purposes, prioritize clarity
4. **Beta/experimental skills**: Wait until skill structure stabilizes

### Documentation for Exceptions

When skipping template application:
1. Add entry to template-adoption-tracker.md under "Exceptions"
2. Document reason for exception
3. Note whether exception is temporary or permanent

---

## Success Metrics

### Quantitative
- [ ] 18/18 skills have template application evaluated
- [ ] ~850-1,000 tokens saved across full library
- [ ] All modified skills pass quality validation
- [ ] No regressions in skill cross-references

### Qualitative
- [ ] Contract sections are more scannable
- [ ] Anti-pattern examples remain concrete and actionable
- [ ] Template references improve maintainability
- [ ] New skill authors can follow template examples

---

## Next Actions

1. **Immediate**: Apply templates to Group A skills (context-budget-awareness, design-before-plan, impact-analysis, read-and-locate, targeted-validation)
2. **This week**: Update skill-authoring-best-practices.md to reference templates
3. **Next sprint**: Apply templates to Groups B and C
4. **Following sprint**: Apply templates to Group D (phase system)
5. **Ongoing**: Track adoption in template-adoption-tracker.md

---

## Cross-References

- **Current tracker**: docs/maintainer/template-adoption-tracker.md
- **Before/after examples**: docs/maintainer/template-adoption-examples.md
- **Contract template**: docs/maintainer/skill-contract-template.md
- **Anti-pattern template**: docs/maintainer/skill-anti-pattern-template.md
- **Deduplication analysis**: docs/maintainer/deduplication-analysis.md
- **Quality script**: maintainer/scripts/analysis/check_skill_quality.py

---

## Maintenance Notes

### Template Updates

If skill-contract-template.md or skill-anti-pattern-template.md is updated:
1. Test new format against 2-3 sample skills
2. Document changes in template changelog
3. Plan batch update for all previously adopted skills
4. Prioritize high-traffic skills for re-application

### Skill Additions

When adding new skills:
1. Use templates from the start (see template-adoption-examples.md)
2. Mark as "template-native" in template-adoption-tracker.md
3. Include template references in initial SKILL.md

### Regression Handling

If template application causes issues:
1. Revert the specific skill to pre-template state
2. Document the issue in template-adoption-tracker.md
3. Analyze root cause (template limitation vs. skill uniqueness)
4. Update rollout plan to exclude similar skills if needed
