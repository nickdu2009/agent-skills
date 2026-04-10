# Template Adoption: Before/After Examples

**Version**: 1.0  
**Date**: 2026-04-11  
**Status**: Reference  
**Scope**: Template application examples for maintainer guidance

## Purpose

Provide concrete before/after examples of contract and anti-pattern template application to guide future skill updates and demonstrate the formatting principles.

## Contract Template Examples

### Example 1: bugfix-workflow

#### Before (182 tokens)

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

#### After (136 tokens, 25.3% reduction)

```markdown
## Contract

### Preconditions

- Bug symptom or unexpected behavior reported; root cause not yet confirmed; evidence gatherable from code/logs/tests/repro steps. See skill-contract-template.md § Preconditions for standard definitions.

### Postconditions

- `status: completed` includes `symptom`, `repro`, `fault_domain`, `fix_hypothesis`.
- Chosen fix backed by direct evidence or reproducible path vs. speculation; validation tied to original symptom.

### Invariants

- Diagnosis precedes editing; confirmed causes distinct from ranked-but-unconfirmed hypotheses; fix scoped to confirmed failure path.

### Downstream Signals

- `symptom`: preserves user-visible failure for later verification
- `repro`: exact failure path for re-check
- `fault_domain`: narrows where edits may happen
- `fix_hypothesis`: confirmed cause and repair direction
```

**Key changes**:
- Preconditions: Semicolon-separated, added template reference
- Postconditions: Removed redundant field repetition, used "vs." for contrast
- Invariants: Semicolon-separated parallel statements
- Downstream Signals: Field:purpose format instead of full sentences

---

### Example 2: plan-before-action

#### Before (208 tokens)

```markdown
## Contract

### Preconditions

- The task needs multi-step execution, multiple files, or explicit sequencing.
- Enough evidence exists to name a working set and a next action.
- Edits are allowed now, or the plan is being produced explicitly for later execution.

### Postconditions

- `status: completed` includes `assumptions`, `working_set`, `sequence`, and `validation_boundary`.
- The plan names the intended files or modules before implementation starts.
- Progress can be reported as done / not done / next without reopening discovery.

### Invariants

- Execution does not begin while the working set is still fuzzy.
- Only one coherent objective is active at a time.
- New dependencies or irreversible operations are surfaced in the plan instead of being introduced silently.

### Downstream Signals

- `assumptions` tell implementers what must still be rechecked.
- `working_set` names the approved edit surface.
- `sequence` gives the execution order for edits and validation.
- `validation_boundary` defines the first targeted check after the patch.
```

#### After (158 tokens, 24.0% reduction)

```markdown
## Contract

### Preconditions

- Task needs multi-step execution, multiple files, or explicit sequencing; enough evidence to name working set and next action; edits allowed now or plan produced for later execution. See skill-contract-template.md § Preconditions for standard definitions.

### Postconditions

- `status: completed` includes `assumptions`, `working_set`, `sequence`, `validation_boundary`.
- Plan names intended files/modules before implementation starts; progress reportable as done/not done/next without reopening discovery.

### Invariants

- Execution doesn't begin while working set is fuzzy; only one coherent objective active at a time; new dependencies/irreversible operations surfaced in plan vs. introduced silently.

### Downstream Signals

- `assumptions`: what must be rechecked
- `working_set`: approved edit surface
- `sequence`: execution order for edits and validation
- `validation_boundary`: first targeted check after patch
```

**Key changes**:
- Removed "The task" / "The agent" / "The plan" framing
- Used contractions ("doesn't" vs. "does not") for natural flow
- Removed "and" repetition in field lists (backticks already provide visual separation)
- Shortened downstream signal explanations to essential purpose

---

## Anti-Pattern Template Examples

### Example 1: minimal-change-strategy

#### Before (84 tokens)

```markdown
# Common Anti-Patterns

- **"While I'm here" cleanup.** The agent fixes the reported bug in one line, then reformats the surrounding function, renames a variable, and reorders imports — tripling the diff for no task-related reason.
- **Rewriting instead of patching.** The agent replaces an entire function or class to fix a single branch condition, making the change harder to review and riskier to revert.
```

#### After (70 tokens, 16.7% reduction)

```markdown
# Common Anti-Patterns

- **"While I'm here" cleanup.** Fixes bug in one line, then reformats surrounding function, renames variable, reorders imports. Triples diff for no task-related reason.
- **Rewriting instead of patching.** Replaces entire function/class to fix single branch condition. Makes change harder to review and riskier to revert.

See skill-anti-pattern-template.md for format guidelines.
```

**Key changes**:
- Removed "The agent" framing (implied subject)
- Split description and consequence into separate sentences for clarity
- Used present tense active verbs for conciseness
- Added template reference footer

---

### Example 2: scoped-tasking

#### Before (92 tokens)

```markdown
# Common Anti-Patterns

- **Grepping the entire repo before reading the error message.** The agent runs broad searches across every directory instead of starting from the user-provided clue. This wastes context and delays the first useful finding.
- **Silent scope creep.** The agent discovers a related issue in a neighboring module and begins investigating it without stating that the original boundary was insufficient. The scope expands without an explicit expansion decision.
```

#### After (79 tokens, 14.1% reduction)

```markdown
# Common Anti-Patterns

- **Grepping the entire repo before reading the error message.** Runs broad searches across every directory instead of starting from user-provided clue. Wastes context and delays first useful finding.
- **Silent scope creep.** Discovers related issue in neighboring module and investigates without stating original boundary was insufficient. Scope expands without explicit expansion decision.

See skill-anti-pattern-template.md for format guidelines.
```

**Key changes**:
- Removed "The agent" and "This" framing
- Simplified compound sentences
- Preserved specific detail (e.g., "user-provided clue", "neighboring module")
- Added template reference

---

## Formatting Principles Demonstrated

### Contract Sections

1. **Semicolon separation**: Use semicolons to separate parallel conditions instead of bullet points for common patterns
2. **Template references**: Add "See skill-contract-template.md § [Section] for standard definitions" to point to canonical guidance
3. **Remove redundant framing**: Avoid "The agent must", "This skill will", "After completion"
4. **Field:purpose format**: For downstream signals, use `field_name`: purpose instead of full sentences
5. **Contractions allowed**: Use natural contractions ("doesn't", "isn't") for readability
6. **Backtick field names**: Always use backticks for field names to improve scannability

### Anti-Pattern Sections

1. **Implicit subject**: Remove "The agent" — action verbs imply the agent
2. **Two-sentence structure**: Description sentence + Consequence sentence
3. **Present tense active voice**: "Fixes bug" not "The agent fixes the bug"
4. **Preserve specific details**: Keep concrete examples (file names, specific actions, measurable impacts)
5. **Template footer**: Add "See skill-anti-pattern-template.md for format guidelines"
6. **Bold pattern name + period**: Maintain `**Pattern name**.**` formatting

## Token Efficiency Patterns

### High-Impact Reductions

1. **"The agent" removal**: Saves 2-3 tokens per occurrence, appears 4-6 times per contract
2. **Semicolon vs. bullet lists**: Saves ~1 token per item when converting 3+ parallel items
3. **Field:purpose vs. full sentences**: Saves 3-5 tokens per downstream signal
4. **Contraction use**: Saves ~0.3 tokens per occurrence ("doesn't" vs. "does not")

### Low-Impact but Additive

1. **Removing "and" in backtick lists**: Saves ~0.5 tokens per list
2. **Removing "The" / "A" at sentence starts**: Saves ~0.3 tokens per sentence
3. **Simplifying "instead of being" to "vs."**: Saves ~1 token per contrast

### Preserved for Clarity

1. **Skill-specific invariants**: Complex invariants kept verbose for precision
2. **Concrete anti-pattern examples**: Specific details preserved over generic descriptions
3. **Technical terms**: No abbreviation of domain terms (e.g., "refactor", "validation")

## Validation Checklist

After applying templates to a skill:

- [ ] Contract section uses semicolon-separated preconditions where applicable
- [ ] Template reference added to Preconditions subsection
- [ ] Downstream Signals use field:purpose format
- [ ] Anti-patterns use two-sentence structure (description + consequence)
- [ ] "The agent" removed from anti-pattern descriptions
- [ ] Template reference footer added to anti-patterns section
- [ ] All backtick field names preserved
- [ ] Skill-specific content remains intact (no semantic changes)
- [ ] Cross-references resolve (template files exist)
- [ ] Quality validation passes (check_skill_quality.py)

## Future Template Evolution

As more skills adopt templates, consider:

1. **Template versioning**: If contract structure changes materially, version templates (v1, v2)
2. **Skill-specific addenda**: For skills with unique contract fields, consider addendum pattern
3. **Compact output examples**: Apply similar compression to Output Example YAML blocks
4. **Guardrails compression**: Explore semicolon format for guardrails sections
5. **Chain composition references**: Already addressed via skill-chain-aliases.md

## Cross-References

- **Contract template**: docs/maintainer/skill-contract-template.md
- **Anti-pattern template**: docs/maintainer/skill-anti-pattern-template.md
- **Adoption tracker**: docs/maintainer/template-adoption-tracker.md
- **Deduplication analysis**: docs/maintainer/deduplication-analysis.md
- **Modified skills**: skills/{minimal-change-strategy,bugfix-workflow,plan-before-action,safe-refactor,scoped-tasking}/SKILL.md
