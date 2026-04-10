# Skill Anti-Pattern Template

**Version**: 1.0  
**Date**: 2026-04-11  
**Status**: Active  
**Scope**: Skill authoring and maintenance

## Purpose

This template defines the canonical structure for documenting anti-patterns in skill SKILL.md files. Use it to ensure anti-pattern examples are clear, actionable, and consistently formatted across the skill library.

## When to Use This Template

- When adding anti-pattern sections to new skills
- When refactoring existing anti-pattern documentation
- When reviewing skill PRs for anti-pattern clarity
- As reference for maintainer onboarding

## Template Structure

```markdown
# Common Anti-Patterns

- **[Pattern name].** [One-sentence description of the anti-pattern behavior]. [One-sentence consequence or concrete example showing why it fails].
```

## Formatting Rules

### Pattern Name

- Use bold formatting: `**Pattern name**`
- Follow with a period: `**Pattern name**.**`
- Keep to 3-5 words maximum
- Use present participle or noun phrase: "Patching before diagnosing", "While I'm here cleanup"
- Avoid generic names: "Bad approach", "Wrong method"

### Description Sentence

- Describe what the agent does wrong in concrete, observable terms
- Use third person: "The agent..." not "You..."
- Focus on behavior, not motivation
- Keep to 15-25 words

### Consequence/Example Sentence

- Show the failure mode or unintended outcome
- Use concrete details when possible: file names, specific changes, measurable impact
- Avoid vague warnings like "this might cause problems"
- Keep to 15-25 words

## Anti-Pattern Categories

Anti-patterns typically fall into these categories. Use this taxonomy to organize multiple anti-patterns within a skill:

### Sequencing Violations

**Pattern**: Doing step B before step A when A is a prerequisite.

**Example**: "Patching before diagnosing" (bugfix-workflow)

### Scope Creep

**Pattern**: Expanding beyond the task boundary without explicit permission.

**Example**: "While I'm here cleanup" (minimal-change-strategy)

### Evidence Failures

**Pattern**: Acting on correlation, assumption, or speculation without confirmation.

**Example**: "Treating correlation as causation" (bugfix-workflow)

### Premature Optimization

**Pattern**: Choosing a more complex solution when a simpler one suffices.

**Example**: "Rewriting instead of patching" (minimal-change-strategy)

### Signal Loss

**Pattern**: Discarding information that downstream skills or users need.

**Example**: "Vague progress reporting" (plan-before-action)

## Good Examples

### Example 1: Sequencing Violation

```markdown
- **Patching before diagnosing.** The agent sees something that looks wrong and immediately edits it without confirming the code path is related to the reported symptom. The "fix" turns out to be for a different issue entirely.
```

**Why this works**:
- Clear pattern name (3 words)
- Observable behavior (agent edits without confirmation)
- Concrete consequence (fixes wrong issue)
- Total: ~30 words

### Example 2: Evidence Failure

```markdown
- **Treating correlation as causation.** A recent commit touched the same file where the bug manifests, so the agent assumes it is the cause and reverts part of it — without tracing the actual failure path or checking whether the symptom existed before that commit.
```

**Why this works**:
- Specific scenario (recent commit, same file)
- Clear failure mode (assumes without checking)
- Concrete action (reverts without evidence)
- Total: ~45 words

### Example 3: Scope Creep

```markdown
- **"While I'm here" cleanup.** The agent fixes the reported bug in one line, then reformats the surrounding function, renames a variable, and reorders imports — tripling the diff for no task-related reason.
```

**Why this works**:
- Memorable pattern name (common phrase)
- Specific scope violation (list of unrelated changes)
- Measurable consequence (triples the diff)
- Total: ~30 words

### Example 4: Signal Loss

```markdown
- **Vague progress reporting.** The agent says "making progress" or "almost done" instead of reporting concrete done / not done / next items. This hides whether the plan is still on track.
```

**Why this works**:
- Observable behavior (specific vague phrases)
- Clear alternative (done/not done/next)
- User-facing consequence (can't track plan)
- Total: ~30 words

## Bad Examples (Avoid These)

### Too Vague

```markdown
- **Bad approach.** The agent does something wrong. This causes problems.
```

**Problems**:
- Pattern name is generic ("bad approach")
- No specific behavior described ("something wrong")
- No concrete consequence ("causes problems")

### Too Verbose

```markdown
- **Attempting to perform edits before completing the diagnostic phase.** When the agent has not yet fully completed the process of gathering evidence and analyzing the root cause of the reported bug symptom, and instead begins making code changes based on preliminary observations or superficial indicators, this frequently results in the unintended consequence that the modifications being applied are actually targeting a completely different defect or area of concern than the one that was originally reported by the user or identified through initial investigation.
```

**Problems**:
- Pattern name is a full sentence (12 words)
- Description is overly formal and wordy
- Runs multiple sentences together
- Total: ~85 words (should be 30-50)

### Missing Consequence

```markdown
- **Editing too early.** The agent makes changes before diagnosis is complete.
```

**Problems**:
- No concrete example
- No stated consequence or failure mode
- Doesn't show why this is problematic

### First Person Voice

```markdown
- **Cleaning up while I'm in the area.** I see some messy code and decide to refactor it even though it's not part of my task. You might end up with a bigger diff than needed.
```

**Problems**:
- Uses first person ("I see", "my task")
- Uses second person ("You might")
- Should use third person throughout

## Section Placement

Place the "Common Anti-Patterns" section:

- **After** the "Guardrails" section
- **Before** the "Composition" section
- Or at the end of the SKILL.md if composition and examples follow

This placement groups related constraint content (Guardrails → Anti-Patterns) while keeping positive guidance (Composition, Examples) later.

## How Many Anti-Patterns?

- **Minimum**: 1 anti-pattern (if only one clear failure mode exists)
- **Optimal**: 2-3 anti-patterns per skill
- **Maximum**: 5 anti-patterns (beyond this, consider whether the skill scope is too broad)

If a skill has 0 anti-patterns, consider whether:
- The skill is too simple to need dedicated documentation
- Anti-patterns exist but haven't been observed yet (add them after real usage)
- The guardrails section already covers failure modes adequately

## Shared vs. Skill-Specific Anti-Patterns

### Shared Anti-Patterns (Cross-Skill)

Some anti-patterns appear across multiple skills. Document these in each affected skill, but keep the wording consistent:

**Example**: "Editing while still discovering" appears in both `plan-before-action` and `scoped-tasking`.

**Guideline**: Use the same pattern name and similar phrasing, but adapt the example to the skill context.

### Skill-Specific Anti-Patterns

Most anti-patterns are unique to a skill's domain. These should be documented only in that skill's SKILL.md.

**Example**: "Treating correlation as causation" is specific to `bugfix-workflow` because it relates to diagnostic reasoning.

## Token Efficiency Guidelines

Target 30-50 words per anti-pattern:

- Pattern name: 3-5 words
- Description: 15-25 words
- Consequence: 15-25 words

At 1.3 tokens/word:
- Each anti-pattern: ~40-65 tokens
- Section with 2 anti-patterns: ~100-150 tokens (including header)

## Integration with Guardrails Section

Anti-patterns and guardrails are related but distinct:

**Guardrails**: Imperative rules ("Do not...", "Avoid...")  
**Anti-patterns**: Narrative examples showing how violations occur in practice

**Good separation**:

```markdown
# Guardrails

- Do not edit before the fault domain is narrowed.
- Do not combine unrelated cleanup into the fix.

# Common Anti-Patterns

- **Patching before diagnosing.** The agent sees something that looks wrong and immediately edits it without confirming the code path is related to the symptom. The "fix" targets a different issue entirely.
```

**Avoid redundancy**: Don't restate every guardrail as an anti-pattern. Choose 2-3 most common or impactful failure modes.

## Before/After Examples

### Before: Weak Anti-Pattern Documentation

```markdown
# Things to Avoid

Don't do things in the wrong order. Make sure you check everything first. Also don't make the change too big. You should be careful about changing things that aren't related to the task.
```

**Problems**:
- Section title is vague ("Things to Avoid")
- No specific pattern names
- No concrete examples
- Vague advice ("check everything")
- Second person ("You should")

Token count: ~35 words × 1.3 ≈ **46 tokens** (but low signal)

### After: Strong Anti-Pattern Documentation

```markdown
# Common Anti-Patterns

- **Patching before diagnosing.** The agent sees something that looks wrong and immediately edits it without confirming the code path is related to the reported symptom. The "fix" turns out to be for a different issue entirely.
- **"While I'm here" cleanup.** The agent fixes the reported bug in one line, then reformats the surrounding function, renames a variable, and reorders imports — tripling the diff for no task-related reason.
```

**Strengths**:
- Clear section title
- Specific, memorable pattern names
- Concrete behaviors and consequences
- Third person throughout

Token count: ~75 words × 1.3 ≈ **98 tokens** (high signal)

**Net change**: +52 tokens, but dramatically improved signal-to-noise ratio.

## Validation Checklist

When reviewing anti-pattern documentation:

- [ ] Section titled "Common Anti-Patterns"
- [ ] Each pattern has bold name followed by period
- [ ] Pattern names are 3-5 words
- [ ] Descriptions use third person ("the agent...")
- [ ] Each pattern includes concrete consequence or example
- [ ] Each pattern is 30-50 words total
- [ ] 2-3 anti-patterns per skill (rarely more than 5)
- [ ] No redundancy with guardrails section
- [ ] Examples are skill-specific, not generic
- [ ] Formatting is consistent across all patterns

## Maintenance Protocol

When updating this template:

1. Validate changes against 3+ existing skill anti-pattern sections
2. Update before/after examples if guidelines change
3. Announce changes in maintainer changelog
4. Update skill authoring best practices to reference new guidance

## Cross-References

- **Guardrails formatting**: `docs/maintainer/skill-contract-template.md`
- **Full skill structure**: `docs/maintainer/claude-skill-authoring-best-practices.md`
- **Example anti-patterns**: See `skills/bugfix-workflow/SKILL.md`, `skills/minimal-change-strategy/SKILL.md`, `skills/plan-before-action/SKILL.md`
