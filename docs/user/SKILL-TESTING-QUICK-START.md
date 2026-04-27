# Skill Testing Quick Start

This guide helps you quickly test the agent-skills system using practical scenarios that verify skill activation, protocol compliance, and execution quality.

## Test Scenarios

The repository includes three test scenarios designed to validate different skill chains:

| Scenario | Complexity | Skill Chain | Files Changed |
|----------|------------|-------------|---------------|
| [Skill Definition Validator](../../examples/skill-definition-validator.md) | ⭐ Simple | scoped → plan → minimal → review → validation | +1 |
| [Refactor Installation Script](../../examples/refactor-installation-script.md) | ⭐⭐ Medium | scoped → locate → safe-refactor → minimal → review | ~1 |
| [Fix Skill References](../../examples/fix-skill-references.md) | ⭐⭐⭐ Complex | scoped → locate → bugfix → minimal → review | ~N |

## Quick Start (30 seconds)

### 1. Choose a Test Scenario

Start with the simplest scenario:

```bash
cat examples/skill-definition-validator.md
```

### 2. Run the Test

Copy the scenario description and provide it to your agent:

```
Please implement the following scenario:

[paste scenario content]
```

### 3. Observe Behavior

Check that the agent follows the expected protocol:

**Protocol Compliance:**
- ✅ Outputs `[task-validation: ...]` block
- ✅ Declares `[triggers: ...]` with expected skills
- ✅ Uses Skill Protocol v2 compact format
- ✅ Includes `[precheck]`, `[output]`, `[validate]`, `[drop]` for each skill

**Execution Quality:**
- ✅ Scope defined before exploration
- ✅ Plan provided before editing
- ✅ Changes kept minimal
- ✅ Self-review performed
- ✅ Targeted validation used

## Expected Protocol Output

When running a test scenario, expect output similar to:

```markdown
[task-validation: PASS | clarity:✓ scope:✓ safety:✓ skill_match:✓ | action:proceed]
[triggers: scoped-tasking plan-before-action minimal-change-strategy self-review targeted-validation]

[precheck: scoped-tasking | PASS | checks:boundary inputs]
[output: scoped-tasking | completed high | scope:"validator script" boundary:"scripts/" | next:plan-before-action]
[validate: scoped-tasking | PASS | checks:boundary clarity]
[drop: scoped-tasking | reason:"boundary confirmed" | active:plan-before-action minimal-change-strategy self-review targeted-validation]

[precheck: plan-before-action | PASS | checks:scope edit_points]
[output: plan-before-action | completed high | plan:"..." files:"scripts/validate-skill-definition.py" | next:implementation]
...
```

## Success Indicators

### ✅ Protocol Adherence

1. **Task Validation Present**
   - Agent outputs `[task-validation]` with clarity, scope, safety, skill_match checks
   - Result is PASS, WARN, or REJECT with clear action

2. **Skill Triggers Declared**
   - Agent declares expected skills in `[triggers: ...]`
   - Skills match the recommended composition from the scenario

3. **Skill Lifecycle Tracked**
   - Each skill has precheck, output, validate, drop phases
   - Skills are explicitly dropped when complete
   - Active skill list is maintained

### ✅ Execution Quality

1. **Scope Control**
   - Agent defines clear boundaries before starting
   - Stays within declared scope
   - Doesn't add unrelated features

2. **Planning Before Action**
   - Clear plan provided before file edits
   - Intended files and changes stated
   - Approach explained

3. **Minimal Changes**
   - Changes limited to task requirements
   - No drive-by cleanups or improvements
   - Original behavior preserved (for refactoring)

4. **Validation Appropriateness**
   - Validation matches change scope
   - Doesn't default to full test suite for local changes
   - Provides specific validation commands

## Warning Signals

### 🚨 Protocol Issues

- ❌ No `[task-validation]` or `[triggers]` blocks
- ❌ Skills activated without declaration
- ❌ Skills not explicitly dropped
- ❌ Missing precheck/output/validate phases

### 🚨 Execution Issues

- ❌ Scope expands beyond stated boundary
- ❌ Edits made before plan is provided
- ❌ Unnecessary features added
- ❌ Unrelated code modified
- ❌ Validation too broad or missing

## Troubleshooting

### Protocol Not Appearing

1. **Check governance files are loaded:**
   ```bash
   # Verify CLAUDE.md exists and contains Skill Protocol v2 reference
   grep "Skill Protocol v2" CLAUDE.md
   ```

2. **Check skills are available:**
   ```bash
   # Verify skills directory exists
   ls -la .claude/skills/ || ls -la .cursor/skills/
   ```

3. **Explicitly request protocol:**
   ```
   Please use Skill Protocol v2 format and trigger the recommended skills
   from the scenario: scoped-tasking, plan-before-action, minimal-change-strategy.
   ```

### Skills Not Triggering

1. **Review CLAUDE.md activation rules:**
   - Task-type activation (bugfix → bugfix-workflow)
   - Mid-task escalation rules

2. **Check skill availability:**
   ```bash
   # List installed skills
   ls -1 .claude/skills/ || ls -1 .cursor/skills/
   ```

3. **Verify scenario matches trigger conditions:**
   - Bugfix scenarios should trigger bugfix-workflow
   - Refactor scenarios should trigger safe-refactor
   - Multi-file scenarios should trigger plan-before-action

## Test Scenario Selection Guide

### First Test: Skill Definition Validator

**Why start here:**
- ✅ Lowest risk (creates new file only)
- ✅ Simplest scope (single script)
- ✅ Clear success criteria
- ✅ Immediately useful output

**What it tests:**
- Basic protocol compliance
- Scope definition (scoped-tasking)
- Planning quality (plan-before-action)
- Change minimization (minimal-change-strategy)

**Expected duration:** 5-10 minutes

### Second Test: Refactor Installation Script

**Why next:**
- ✅ Tests code reading (read-and-locate)
- ✅ Tests safe-refactor skill
- ✅ Tests zero-behavior-change constraint
- ✅ More realistic complexity

**What it tests:**
- Code understanding capabilities
- Safe refactoring discipline
- Behavior preservation
- Self-review effectiveness

**Expected duration:** 10-15 minutes

### Third Test: Fix Skill References

**Why last:**
- ✅ Tests systematic searching
- ✅ Tests bugfix-workflow
- ✅ Tests multi-file coordination
- ✅ Tests "no bug found" scenario handling

**What it tests:**
- Systematic investigation
- Bug diagnosis workflow
- Multi-file edits
- False positive avoidance

**Expected duration:** 10-20 minutes

## Observation Checklist

After running a test scenario, score these aspects:

### Protocol Compliance (0-5 points each)

- [ ] `[task-validation]` block present and properly formatted
- [ ] `[triggers]` declaration matches recommended skills
- [ ] Each skill has complete lifecycle (precheck/output/validate/drop)
- [ ] Skills dropped explicitly with reason
- [ ] Active skill list maintained throughout

**Score: ___/25**

### Execution Quality (0-5 points each)

- [ ] Scope clearly defined before exploration
- [ ] Plan provided before editing files
- [ ] Changes kept to minimum viable
- [ ] No unrelated improvements or cleanups
- [ ] Appropriate validation chosen

**Score: ___/25**

### Skill-Specific Behavior (0-10 points each)

- [ ] scoped-tasking: Clear boundary definition
- [ ] plan-before-action: Explicit plan with file list
- [ ] minimal-change-strategy: Controlled scope, no scope creep
- [ ] self-review: Diff review for quality issues
- [ ] targeted-validation: Narrow, appropriate checks

**Score: ___/50**

### Total Score: ___/100

**Rating:**
- 90-100: Excellent - skills working as designed
- 75-89: Good - minor protocol or execution gaps
- 60-74: Fair - significant gaps, needs investigation
- <60: Poor - skills not triggering or behaving incorrectly

## Next Steps

After completing the quick start scenarios:

1. **Review test results:**
   - Document which skills triggered correctly
   - Note any protocol deviations
   - Identify execution quality issues

2. **Run additional scenarios:**
   - Explore `examples/` directory for more scenarios
   - Try scenarios that test specific skills

3. **Report issues:**
   - Document unexpected behavior
   - Compare against skill definitions in `skills/*/SKILL.md`
   - File issues at repository if skills aren't working as designed

## Additional Resources

- **Skill Testing Playbook**: [examples/skill-testing-playbook.md](../../examples/skill-testing-playbook.md)
- **Skill Evaluation Rubric**: [examples/skill-evaluation-rubric.md](../../examples/skill-evaluation-rubric.md)
- **Skill Protocol v2 Spec**: [SKILL-PROTOCOL-V2.md](SKILL-PROTOCOL-V2.md)
- **All Test Scenarios**: [examples/](../../examples/)

## Feedback

If you find issues with these test scenarios or have suggestions for improvement:

1. Check existing issues at the repository
2. Review the skill definitions to understand intended behavior
3. File a detailed bug report with:
   - Scenario used
   - Expected behavior
   - Actual behavior
   - Protocol output (if any)
