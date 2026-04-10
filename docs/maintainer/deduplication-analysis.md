# Documentation Deduplication Analysis

**Version**: 1.0  
**Date**: 2026-04-11  
**Status**: Draft  
**Scope**: Skill SKILL.md files and maintainer documentation

## Executive Summary

This analysis identifies the top repeated prose patterns across skill documentation and governance templates. The goal is to quantify duplication, locate canonical homes for shared explanations, and enable token-efficient normalization through cross-references.

### Key Findings

1. **Structural patterns are highly consistent**: 13 of 18 skills use identical section headers (`Purpose`, `When to Use`, `Core Rules`, `Contract`, `Failure Handling`, etc.)
2. **Contract boilerplate repeats extensively**: Input/Output contract formatting appears in 13+ skills with nearly identical phrasing
3. **Chain composition prose duplicates across 10+ skills**: Each skill lists its common compositions individually
4. **Anti-pattern examples share similar structure**: 14 skills include anti-pattern sections with redundant explanatory framing
5. **Precondition/Postcondition/Invariant prose is formulaic**: Contract subsections use repeated template language

### Estimated Token Impact

- **Chain composition duplication**: ~800–1,200 tokens (addressable via chain aliases)
- **Contract section boilerplate**: ~600–900 tokens (addressable via canonical template reference)
- **Anti-pattern framing**: ~400–600 tokens (addressable via shared example structure)
- **Section header overhead**: ~200–300 tokens (not actionable without semantic loss)
- **Total estimated addressable duplication**: ~2,000–3,000 tokens across 18 skills

This analysis focuses on safe, low-risk deduplication that preserves readability and does not change skill semantics.

---

## Top 10 Duplicated Prose Patterns

### 1. Chain Composition Prose

**Frequency**: 10 skills  
**Location**: "Combine with:" or "Composition" sections  
**Pattern**:

```markdown
Combine with:

- `scoped-tasking` to keep the patch boundary honest
- `plan-before-action` to declare intended edits before changing files
- `targeted-validation` to verify the patch without paying full-suite cost
- `bugfix-workflow` when the minimal fix depends on evidence from diagnosis
```

**Duplication type**: Each skill lists 3–5 companion skills with 1-sentence explanations, resulting in repeated chains like:

- `scoped-tasking → plan-before-action → minimal-change-strategy → self-review → targeted-validation`
- `scoped-tasking → read-and-locate → bugfix-workflow → minimal-change-strategy → self-review`

**Token cost per instance**: ~80–120 tokens  
**Total estimated cost**: ~800–1,200 tokens (10 instances)

**Normalization strategy**:

- Define canonical chains in `docs/maintainer/skill-chain-aliases.md` (completed)
- Replace repeated chain prose with alias references: "See bugfix-standard chain in skill-chain-aliases.md"
- Keep full explanations only in the canonical chain reference

**Example before/after**:

Before (in `minimal-change-strategy/SKILL.md`):

```markdown
Combine with:

- `scoped-tasking` to keep the patch boundary honest
- `plan-before-action` to declare intended edits before changing files
- `targeted-validation` to verify the patch without paying full-suite cost
- `bugfix-workflow` when the minimal fix depends on evidence from diagnosis
```

After:

```markdown
Combine with:

- Part of `bugfix-standard`, `refactor-safe`, and `multi-file-planned` chains
- See full chain definitions in docs/maintainer/skill-chain-aliases.md
```

---

### 2. Input Contract Boilerplate

**Frequency**: 13 skills  
**Location**: "Input Contract" section  
**Pattern**:

```markdown
# Input Contract

Provide:

- [required field 1]
- [required field 2]
- [required field 3]

Optional but helpful:

- [optional field 1]
- [optional field 2]
```

**Duplication type**: Section header, "Provide:" label, and "Optional but helpful:" framing repeat verbatim

**Token cost per instance**: ~40–60 tokens (structure only, not field content)  
**Total estimated cost**: ~520–780 tokens (13 instances)

**Normalization strategy**:

- Extract the contract section template to a canonical location (e.g., `docs/maintainer/skill-contract-template.md`)
- Keep individual skill contract content in place but reference the template structure in maintainer docs
- Do NOT normalize the actual contract fields — those are skill-specific and semantically meaningful

**Recommendation**: Low-priority — structure is lightweight and aids readability. Normalization would save tokens but harm scanability.

---

### 3. Output Contract Boilerplate

**Frequency**: 13–16 skills  
**Location**: "Output Contract" section  
**Pattern**:

```markdown
# Output Contract

Return:

- [output field 1]
- [output field 2]
- [output field 3]
```

**Duplication type**: Section header, "Return:" label repeat verbatim

**Token cost per instance**: ~30–50 tokens (structure only)  
**Total estimated cost**: ~390–800 tokens (13–16 instances)

**Normalization strategy**: Same as Input Contract — low-priority, structure aids readability.

---

### 4. Anti-Pattern Section Framing

**Frequency**: 14 skills  
**Location**: "Common Anti-Patterns" section  
**Pattern**:

```markdown
# Common Anti-Patterns

- **[Pattern name].** [Description of the anti-pattern]. [Consequence or example].
- **[Pattern name].** [Description]. [Consequence].
```

**Duplication type**: Section header and bold-labeled list structure repeat across skills

**Token cost per instance**: ~30–50 tokens (structure + header)  
**Total estimated cost**: ~420–700 tokens (14 instances)

**Normalization strategy**:

- Extract anti-pattern template structure to `docs/maintainer/skill-authoring-best-practices.md`
- Reference the template in maintainer guidance: "Use the anti-pattern format defined in skill-authoring-best-practices.md"
- Keep individual anti-pattern content in place — the examples are skill-specific

**Recommendation**: Medium-priority — template reference would reduce boilerplate while preserving examples.

---

### 5. Contract Subsection: Preconditions

**Frequency**: 14+ skills  
**Location**: "Contract" → "Preconditions" subsection  
**Pattern**:

```markdown
### Preconditions

- [Condition 1]
- [Condition 2]
- [Condition 3]
```

**Duplication type**: Subsection header and bullet list structure

**Token cost per instance**: ~20–40 tokens (structure only)  
**Total estimated cost**: ~280–560 tokens (14 instances)

**Normalization strategy**: Same as Input/Output Contract — structure is lightweight and aids scanability. Not a high-priority target.

---

### 6. Contract Subsection: Postconditions

**Frequency**: 14+ skills  
**Location**: "Contract" → "Postconditions" subsection  
**Pattern**:

```markdown
### Postconditions

- `status: completed` includes [required outputs].
- [Additional postcondition 1]
- [Additional postcondition 2]
```

**Duplication type**: Subsection header and "`status: completed` includes..." opening phrase

**Token cost per instance**: ~25–45 tokens  
**Total estimated cost**: ~350–630 tokens (14 instances)

**Normalization strategy**: Low-priority — opening phrase provides useful consistency signal.

---

### 7. Contract Subsection: Invariants

**Frequency**: 13+ skills  
**Location**: "Contract" → "Invariants" subsection  
**Pattern**:

```markdown
### Invariants

- [Invariant statement 1]
- [Invariant statement 2]
```

**Duplication type**: Subsection header and bullet structure

**Token cost per instance**: ~15–30 tokens  
**Total estimated cost**: ~195–390 tokens (13 instances)

**Normalization strategy**: Not actionable — structure is minimal and semantically important.

---

### 8. Contract Subsection: Downstream Signals

**Frequency**: 13 skills  
**Location**: "Contract" → "Downstream Signals" subsection  
**Pattern**:

```markdown
### Downstream Signals

- `[field_name]` [explanation of what downstream skills consume]
- `[field_name]` [explanation]
```

**Duplication type**: Subsection header and backtick-labeled list structure

**Token cost per instance**: ~20–35 tokens  
**Total estimated cost**: ~260–455 tokens (13 instances)

**Normalization strategy**: Not actionable — signals are skill-specific and semantically distinct.

---

### 9. Failure Handling Section Structure

**Frequency**: 18 skills  
**Location**: "Failure Handling" section  
**Pattern**:

```markdown
## Failure Handling

### Common Failure Causes

- [Cause 1]
- [Cause 2]

### Retry Policy

- [Retry condition]
- [Stop condition]

### Fallback

- [Fallback skill or action]
```

**Duplication type**: Section and subsection headers, list structure

**Token cost per instance**: ~45–70 tokens (structure only)  
**Total estimated cost**: ~810–1,260 tokens (18 instances)

**Normalization strategy**:

- Extract the Failure Handling template to `docs/maintainer/skill-contract-template.md`
- Reference the structure in maintainer docs but keep individual failure causes, retry policies, and fallbacks in place
- This is primarily a maintainer-facing normalization, not a runtime token saver

**Recommendation**: Low-priority — structure provides consistent navigation across skills.

---

### 10. Guardrails Section Framing

**Frequency**: 13+ skills  
**Location**: "Guardrails" section  
**Pattern**:

```markdown
# Guardrails

- Do not [anti-pattern 1].
- Do not [anti-pattern 2].
- Avoid [anti-pattern 3].
- [Positive guideline].
```

**Duplication type**: Section header and "Do not..." / "Avoid..." imperative phrasing

**Token cost per instance**: ~25–40 tokens (structure + header)  
**Total estimated cost**: ~325–520 tokens (13 instances)

**Normalization strategy**: Not actionable — imperative phrasing is intentional and aids clarity. Changing to a shared template would harm readability.

---

## Additional Repeated Patterns (Lower Frequency)

### 11. "Example" Section Introductions

Many skills introduce examples with:

```markdown
# Example

Task: "[task description]"

[Implementation walkthrough or pattern]
```

This pattern is consistent but not duplicative — each example is skill-specific.

### 12. "When to Use" / "When Not to Use" Structure

13 skills use paired sections:

```markdown
# When to Use

- [Condition 1]
- [Condition 2]

# When Not to Use

- [Condition 1]
- [Condition 2]
```

Structure is consistent but content is entirely skill-specific. Not a deduplication target.

### 13. "Execution Pattern" Numbered Lists

Many skills use:

```markdown
# Execution Pattern

1. [Step 1]
2. [Step 2]
3. [Step 3]
```

Format is intentional for clarity. Not a normalization target.

---

## Normalization Recommendations

### High-Priority (Phase 3)

1. **Chain composition prose → chain aliases**
   - Status: Chain alias reference created (`docs/maintainer/skill-chain-aliases.md`)
   - Next: Update skill SKILL.md files to reference canonical chains instead of repeating prose
   - Token savings: ~800–1,200 tokens

2. **Anti-pattern section framing → template reference**
   - Extract anti-pattern structure to `docs/maintainer/skill-authoring-best-practices.md`
   - Add guidance: "Use the anti-pattern format defined in the authoring guide"
   - Token savings: ~200–400 tokens (structure only, keep examples in place)

### Medium-Priority

3. **Contract section templates → maintainer reference**
   - Document the canonical Input/Output/Preconditions/Postconditions/Invariants/Downstream Signals structure in `docs/maintainer/skill-contract-template.md`
   - Use this as a maintainer authoring guide, not a runtime normalization
   - Token savings: Minimal at runtime, but improves authoring consistency

### Low-Priority / Not Recommended

4. **Section headers and list structure**
   - Consistent headers (`Purpose`, `When to Use`, `Core Rules`, etc.) aid navigation
   - Normalizing these would harm readability and save minimal tokens
   - Recommendation: Keep as-is

5. **Guardrails imperative phrasing**
   - "Do not..." / "Avoid..." phrasing is intentional for clarity
   - Recommendation: Keep as-is

---

## Cross-Reference Extraction Targets

The following explanatory prose blocks appear in multiple locations and could be extracted to canonical references:

### 1. Skill Protocol Block Explanations

**Current state**: Protocol block examples (`[task-input-validation]`, `[trigger-evaluation]`, etc.) appear in:

- Root `CLAUDE.md`
- `docs/user/SKILL-PROTOCOL-V1.md`
- Several skill SKILL.md files (as examples)

**Normalization**: Point all references to `docs/user/SKILL-PROTOCOL-V1.md` as the canonical source. Remove duplicated protocol block shape documentation from individual skills.

**Token savings**: ~300–500 tokens

### 2. Skill Family Definitions

**Current state**: Skill family explanations (Execution, Orchestration, Primary Phase, etc.) appear in:

- Root `CLAUDE.md`
- Some maintainer docs

**Normalization**: Already reasonably centralized. No further action needed.

### 3. Trigger vs. Escalation Distinction

**Current state**: Explanation of task-type activation vs. mid-task escalation appears in:

- Root `CLAUDE.md` § Skill Activation
- Some individual skill SKILL.md files

**Normalization**: Keep primary definition in `CLAUDE.md`, remove from skill files.

**Token savings**: ~100–200 tokens

---

## Safe Deduplication Principles

When normalizing documentation:

1. **Preserve skill-specific content**: Do not extract examples, guardrails, or contract fields that are unique to a skill.
2. **Maintain scanability**: Structural headers and list formats aid navigation — only normalize if token savings are substantial.
3. **Use cross-references for explanatory prose**: Extract repeated explanations (e.g., protocol blocks, chain patterns) to canonical locations and link to them.
4. **Avoid over-normalization**: If a section appears in only 2–3 skills, it may not be worth normalizing.
5. **Test after normalization**: Verify that cross-references resolve correctly and that the documentation remains usable.

---

## Before/After Comparison

### Example 1: Chain Composition (minimal-change-strategy/SKILL.md)

**Before** (~115 tokens):

```markdown
# Composition

Combine with:

- `scoped-tasking` to keep the patch boundary honest
- `plan-before-action` to declare intended edits before changing files
- `targeted-validation` to verify the patch without paying full-suite cost
- `bugfix-workflow` when the minimal fix depends on evidence from diagnosis
```

**After** (~22 tokens):

```markdown
# Composition

Part of `bugfix-standard`, `refactor-safe`, and `multi-file-planned` chains. See full definitions in docs/maintainer/skill-chain-aliases.md.
```

**Net savings**: ~93 tokens per skill × 10 skills = **~930 tokens**

---

### Example 2: Anti-Pattern Structure (bugfix-workflow/SKILL.md)

**Before** (~95 tokens):

```markdown
# Common Anti-Patterns

- **Patching before diagnosing.** The agent sees something that looks wrong and immediately edits it without confirming the code path is related to the reported symptom. The "fix" turns out to be for a different issue entirely.
- **Treating correlation as causation.** A recent commit touched the same file where the bug manifests, so the agent assumes it is the cause and reverts part of it — without tracing the actual failure path or checking whether the symptom existed before that commit.
```

**After** (~90 tokens):

```markdown
# Common Anti-Patterns

- **Patching before diagnosing.** The agent sees something that looks wrong and immediately edits it without confirming the code path is related to the reported symptom. The "fix" turns out to be for a different issue entirely.
- **Treating correlation as causation.** A recent commit touched the same file where the bug manifests, so the agent assumes it is the cause and reverts part of it — without tracing the actual failure path or checking whether the symptom existed before that commit.

(Format: docs/maintainer/skill-authoring-best-practices.md § Anti-Pattern Template)
```

**Net savings**: Minimal at runtime, but improves maintainer consistency.

---

## Validation Checklist

After normalization:

- [ ] All cross-references resolve to existing files
- [ ] Chain aliases match the definitions in `CLAUDE.md` § Skill Chain Triggers
- [ ] Skill-specific content remains in place (examples, guardrails, contract fields)
- [ ] Section structure remains scanable and navigable
- [ ] Maintainer docs accurately reflect the normalized structure
- [ ] No semantic changes to skill contracts or preconditions

---

## Rollout Strategy

### Phase 3A: Chain Alias Adoption (Current Phase)

1. Create `docs/maintainer/skill-chain-aliases.md` (✓ Complete)
2. Create this analysis document (✓ Complete)
3. Update 5–10 high-duplication skills to use chain aliases
4. Verify cross-references resolve correctly
5. Measure token savings

### Phase 3B: Anti-Pattern Template (Optional)

1. Extract anti-pattern structure to `docs/maintainer/skill-authoring-best-practices.md`
2. Add maintainer guidance for using the template
3. Update skills to reference the template (footer note only, keep examples in place)

### Phase 3C: Contract Template (Low Priority)

1. Create `docs/maintainer/skill-contract-template.md` as an authoring guide
2. Use for new skill development, not as a runtime normalization

---

## Appendix: Duplication Measurement Methodology

### Data Collection

1. Used `grep -r "Pattern"` to identify repeated section headers across `/skills/*/SKILL.md`
2. Manually reviewed 18 skill files to identify prose patterns vs. structural patterns
3. Estimated token counts using rough word-to-token ratio (1 word ≈ 1.3 tokens)
4. Counted instances of each pattern across the skill corpus

### Limitations

- Token estimates are approximate (not measured with actual tokenizer)
- Analysis focused on SKILL.md files; did not comprehensively audit maintainer docs or governance templates
- Did not measure duplication in skill reference files (`/skills/*/references/*.md`)
- Some patterns may be intentional repetition for consistency (e.g., contract structure)

### Future Work

- Extend analysis to maintainer documentation (`docs/maintainer/*.md`)
- Analyze governance templates (`templates/governance/AGENTS-template.md`, `CLAUDE-template.md`)
- Use actual tokenizer (e.g., `tiktoken`) for precise measurements
- Identify duplication in skill reference files
