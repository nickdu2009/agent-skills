# Skill Contract Template

**Version**: 1.0  
**Date**: 2026-04-11  
**Status**: Active  
**Scope**: Skill authoring and maintenance

## Purpose

This template defines the canonical structure for skill contracts. Use it when authoring new skills or refactoring existing ones to ensure consistent contract formatting across the skill library.

## When to Use This Template

- When creating a new skill SKILL.md
- When refactoring contract sections in existing skills
- When reviewing skill PRs for contract completeness
- As reference documentation for maintainer onboarding

## When to Inline vs. Reference

### Inline the Contract (Recommended)

Keep the contract inline in SKILL.md when:

- The skill is under 400 lines total
- Contract fields are skill-specific and unique
- Readability benefits from seeing the contract in context

### Reference This Template

Reference this template in maintainer documentation, not in skill SKILL.md files. Skills should always contain their full contracts inline for optimal discoverability.

## Template Structure

```markdown
## Contract

### Preconditions

- [Condition that must be true before the skill activates]
- [Another precondition]
- [Observable state or available evidence]

### Postconditions

- `status: completed` includes [required output fields].
- [What must be true after successful execution]
- [What downstream skills can rely on]

### Invariants

- [Property that remains true throughout execution]
- [Constraint that is never violated]
- [Relationship that must be preserved]

### Downstream Signals

- `field_name` [explains what downstream skills consume from this field]
- `another_field` [explains the signal's purpose]
```

## Field Definitions

### Preconditions

**Purpose**: Define when the skill can activate successfully.

**Content**:
- Observable conditions (e.g., "A bug symptom has been reported")
- Available inputs or evidence (e.g., "Reproduction steps are available")
- State requirements (e.g., "The root cause is not yet confirmed")

**Anti-patterns**:
- Listing skill names as preconditions (use composition section instead)
- Describing what the skill does (use purpose section instead)
- Vague conditions that cannot be checked ("the task is complex enough")

### Postconditions

**Purpose**: Define what the skill guarantees upon successful completion.

**Content**:
- Required output fields for `status: completed`
- Observable outcomes (e.g., "The fault domain is narrowed")
- Guarantees for downstream consumers (e.g., "Validation is tied to the symptom")

**Anti-patterns**:
- Describing the execution process (use execution pattern instead)
- Listing possible but optional outputs (keep only guarantees)
- Duplicating output contract content (reference it instead)

### Invariants

**Purpose**: Define properties that must remain true throughout skill execution.

**Content**:
- Ordering constraints (e.g., "Diagnosis precedes editing")
- Scope constraints (e.g., "The fix stays scoped to the confirmed path")
- Separation of concerns (e.g., "Confirmed causes remain distinct from hypotheses")

**Anti-patterns**:
- Restating guardrails (keep them in the guardrails section)
- Describing desirable but not mandatory properties
- Mixing runtime state with conceptual constraints

### Downstream Signals

**Purpose**: Explain what downstream skills consume from this skill's outputs.

**Content**:
- Signal name in backticks: `signal_name`
- Clear explanation of consumption purpose
- How the signal enables downstream work

**Anti-patterns**:
- Duplicating the output contract (signals explain usage, not structure)
- Listing signals that are not actually consumed downstream
- Vague explanations like "provides context" (be specific)

## Input/Output Contract Structure

Skills should include separate Input Contract and Output Contract sections before the main Contract section:

```markdown
# Input Contract

Provide:

- [required input 1]
- [required input 2]
- [required input 3]

Optional but helpful:

- [optional input 1]
- [optional input 2]
```

```markdown
# Output Contract

Return:

- [output field 1]: [brief description]
- [output field 2]: [brief description]
- [output field 3]: [brief description]
```

**Note**: Input/Output contracts are distinct from the main Contract section. Input/Output describe the data interface; Contract describes execution guarantees.

## Before/After Examples

### Before: Verbose Contract with Redundancy

```markdown
## Contract

### Preconditions

Before activating this skill, the following conditions must be met:
- The agent must have identified a bug symptom that has been clearly described and documented
- There must be evidence that the root cause has not yet been determined or confirmed through code analysis
- The codebase or system state must allow the agent to gather further evidence through code inspection, log analysis, or test execution

### Postconditions

After this skill completes successfully with status set to completed:
- The skill will have produced a symptom field containing the original reported symptom
- There will be a fault_domain field that identifies the narrowed area where the bug exists
- A fix_hypothesis field will contain the confirmed cause and the direction for repair
- All outputs will be validated and ready for consumption by downstream skills

### Invariants

Throughout the execution of this skill:
- The agent will always perform diagnosis before making any code edits
- Confirmed causes will be kept separate and distinct from hypotheses that have been ranked but remain unconfirmed
- Any fix that is applied will remain scoped strictly to the confirmed failure path
```

Token count: ~180 words × 1.3 ≈ **234 tokens**

### After: Concise Contract Following Template

```markdown
## Contract

### Preconditions

- A bug symptom or unexpected behavior has been reported.
- The root cause is not yet confirmed.
- The agent can gather evidence from code, logs, tests, or reproduction steps before editing.

### Postconditions

- `status: completed` includes `symptom`, `repro`, `fault_domain`, and `fix_hypothesis`.
- The chosen fix is backed by direct evidence or a reproducible path rather than speculation alone.
- Validation is tied back to the original symptom.

### Invariants

- Diagnosis precedes editing.
- Confirmed causes remain distinct from ranked but unconfirmed hypotheses.
- The fix stays scoped to the confirmed failure path.

### Downstream Signals

- `symptom` preserves the user-visible failure to verify later.
- `repro` gives downstream validation the exact failure path to re-check.
- `fault_domain` narrows where edits may happen.
- `fix_hypothesis` documents the confirmed cause and chosen repair direction.
```

Token count: ~125 words × 1.3 ≈ **163 tokens**

**Savings**: ~71 tokens per skill (30% reduction)

## Token Efficiency Guidelines

When authoring contracts:

1. **Use parallel structure**: Start bullets with observable conditions, not full sentences
2. **Avoid redundant framing**: Don't repeat "this skill will" or "the agent must"
3. **Use backticks for field names**: `field_name` is clearer than "the field_name field"
4. **Keep explanations specific**: "Narrows where edits may happen" vs. "provides context"
5. **One concept per bullet**: Don't pack multiple requirements into compound sentences

## Integration with Other Templates

This contract template works alongside:

- **skill-anti-pattern-template.md**: For common failure modes
- **protocol-v2-compact.md**: For execution protocol blocks
- **skill-chain-aliases.md**: For composition patterns

## Validation Checklist

When reviewing a skill contract:

- [ ] Preconditions are observable and checkable
- [ ] Postconditions specify required output fields for `status: completed`
- [ ] Invariants describe properties that hold throughout execution
- [ ] Downstream signals explain consumption purpose, not just field structure
- [ ] No duplication between Input/Output contract and main Contract sections
- [ ] Contract follows the template structure (order: Pre/Post/Invariants/Signals)
- [ ] Field names use backticks for clarity
- [ ] Bullets are concise and parallel in structure

## Maintenance Protocol

When updating this template:

1. Validate changes against 3+ existing skill contracts
2. Update the before/after examples to reflect new guidance
3. Announce changes in maintainer changelog
4. Update skill authoring best practices if guidelines change

## Cross-References

- **Full skill structure**: `docs/maintainer/claude-skill-authoring-best-practices.md`
- **Contract examples**: See `skills/bugfix-workflow/SKILL.md`, `skills/minimal-change-strategy/SKILL.md`
- **Composition patterns**: `docs/maintainer/skill-chain-aliases.md`
