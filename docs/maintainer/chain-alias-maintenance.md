# Chain Alias Maintenance Guide

**Version**: 1.0  
**Date**: 2026-04-11  
**Status**: Active

## Purpose

Define procedures for maintaining chain aliases across the skill library, ensuring CLAUDE.md remains the single source of truth for chain definitions.

## Principles

1. **Single Source of Truth**: CLAUDE.md § Skill Chain Triggers is the authoritative definition for all chain patterns.
2. **Propagation Discipline**: Changes to chain definitions must propagate to affected SKILL.md files systematically.
3. **Version Control**: Chain definition changes must be documented in maintainer changelogs.
4. **Validation**: Chain references must be validated before merge.

## Chain Definition Lifecycle

### Adding a New Chain Pattern

**Preconditions for adding a new alias:**

1. The chain appears in at least 3 distinct usage contexts across the codebase
2. The pattern is stable enough to document as canonical
3. The chain is not a one-off variation better expressed inline

**Process:**

1. **Define in CLAUDE.md first**
   - Add to CLAUDE.md § Skill Chain Triggers → Common Flow Patterns
   - Use the canonical format:
     ```markdown
     - [Chain name]: `skill-a` → `skill-b` → `skill-c` → `skill-d`
     ```
   - Add forward handoff conditions if needed (§ Forward Handoffs table)
   - Add fallback conditions if needed (§ Fallbacks table)

2. **Document in skill-chain-aliases.md**
   - Add full chain definition with:
     - Full chain (explicit skill sequence)
     - Use-when criteria
     - Entry point
     - Exit point
     - Variations (if applicable)
     - Fallbacks (if applicable)
     - Example trigger
   - Follow the existing template structure

3. **Update affected SKILL.md files**
   - For each skill in the chain, update Composition section to reference the new alias
   - Use the standard format:
     ```markdown
     ## Composition
     
     Part of [chain-name] chain (see CLAUDE.md § Skill Chain Triggers).
     
     Role: [entry point | core component | exit point] — [1-2 sentence description]
     
     Additional compositions:
     - [Unique skill-specific relationships not covered by the chain]
     ```

4. **Validate references**
   - Run cross-reference check: `grep -r "chain-name" skills/*/SKILL.md`
   - Verify all skills in the chain have updated Composition sections
   - Check for broken links

5. **Document the change**
   - Add entry to maintainer changelog
   - Update chain-alias-adoption-tracker.md adoption status

### Updating an Existing Chain

**Triggers for chain updates:**

- Skill added to or removed from chain
- Handoff condition clarified or changed
- Fallback path added or removed
- Chain name renamed for clarity

**Process:**

1. **Update CLAUDE.md first**
   - Modify the chain definition in § Common Flow Patterns
   - Update Forward Handoffs or Fallbacks tables if conditions changed
   - Consider backward compatibility: can old references still work?

2. **Update skill-chain-aliases.md**
   - Revise the affected chain definition
   - Update use-when criteria if changed
   - Update example trigger if needed
   - Add note about what changed and why

3. **Propagate to SKILL.md files**
   - For skills added to the chain: add Composition reference
   - For skills removed from the chain: remove or update Composition reference
   - For skills with changed roles: update role description
   - For changed handoff conditions: update forward flow or fallback sections

4. **Validate propagation**
   - Check that all affected skills reference the updated chain correctly
   - Verify no orphaned references to old chain structure
   - Run grep to find any stale references: `grep -r "old-pattern" skills/`

5. **Regression check**
   - Ensure skill preconditions still align with new chain structure
   - Verify handoff contracts are still satisfied
   - Check that examples still make sense

6. **Document the change**
   - Add to maintainer changelog with:
     - What changed (chain structure, handoff, fallback)
     - Why it changed
     - Which skills were affected
     - Migration notes if the change is breaking

### Deprecating a Chain

**Triggers for deprecation:**

- Chain pattern no longer used in practice
- Chain merged into another more general pattern
- Chain split into more specific patterns

**Process:**

1. **Mark deprecated in CLAUDE.md**
   - Add deprecation notice: `(Deprecated: use [new-chain] instead)`
   - Keep the definition visible for one release cycle
   - Document migration path

2. **Update skill-chain-aliases.md**
   - Add deprecation status and migration guidance
   - Do not remove the definition immediately

3. **Migrate skill references**
   - Update all SKILL.md files to reference the new pattern
   - Remove references to deprecated chain

4. **Remove after grace period**
   - After one release cycle, remove from CLAUDE.md
   - Archive in skill-chain-aliases.md with deprecation date
   - Remove from adoption tracker

## Composition Section Template

### For Skills in Standard Chains

```markdown
## Composition

[Entry point for | Core component of | Exit point for] [chain-alias] chain (see CLAUDE.md § Skill Chain Triggers).

Role: [1-2 sentence description of role]. Receives [inputs] from [predecessor], produces [outputs], hands to [successor].

Standard forward flow:

- [chain-name]: [abbreviated chain showing this skill's position]

Additional compositions:

- [Unique skill-specific relationships]

Fallbacks:

- To `skill-x` when [condition]
- To `skill-y` when [condition]

Drop after [deactivation condition].
```

### For Cross-Chain Fallback Skills

```markdown
## Composition

Cross-chain fallback skill. Activates when [threshold conditions] during any execution chain (see CLAUDE.md § Skill Escalation).

Role: [1-2 sentence description]. Produces [outputs] that downstream skills can consume.

Typical activations:

- During `skill-a` when [condition]
- During `skill-b` when [condition]
- After [action], typically hands back to `skill-c` to resume

Drop after [deactivation condition].
```

### For Phase/Orchestration Skills

Phase and orchestration skills use domain-specific composition patterns that don't map to standard execution chains. They should use their own templates focused on phase workflow or parallel orchestration patterns.

```markdown
## Composition

Use this skill together with:

- `$skill-a` for [specific phase/orchestration purpose]
- `$skill-b` when [specific condition]

See also [skill-name] usage in [domain] workflow chain definitions in docs/maintainer/skill-chain-aliases.md.
```

## Validation Procedures

### Pre-Commit Validation

Before committing chain definition changes:

1. **Reference integrity check**
   ```bash
   # Check all chain references resolve to CLAUDE.md
   grep -r "Part of.*chain" skills/*/SKILL.md | \
     while read ref; do
       chain=$(echo "$ref" | grep -o "\`[^']*\`" | head -1 | tr -d '`')
       if ! grep -q "$chain" CLAUDE.md; then
         echo "Broken chain reference: $chain in $ref"
       fi
     done
   ```

2. **Skill coverage check**
   ```bash
   # Verify all skills in a chain have Composition sections
   # Extract chain definition from CLAUDE.md
   # For each skill in chain, check if its SKILL.md references the chain
   ```

3. **Consistency check**
   - All chain references use the same naming (case, hyphenation)
   - All skills in a chain agree on the chain structure
   - Entry/exit point designations are consistent

### Post-Merge Validation

After merging chain changes:

1. **Adoption tracker sync**
   - Update chain-alias-adoption-tracker.md with new adoption stats
   - Recalculate token savings if chain structure changed

2. **Documentation consistency**
   - Verify CLAUDE.md, skill-chain-aliases.md, and SKILL.md files all agree
   - Check that examples still use correct chain references

3. **Regression testing**
   - If chain handoff conditions changed, verify skill contracts still align
   - Check that trigger examples still match the new chain structure

## Migration Procedures

### When Chain Definition Changes

1. **Identify affected skills**
   ```bash
   # Find all skills referencing the changed chain
   grep -l "chain-name" skills/*/SKILL.md
   ```

2. **Update each skill's Composition section**
   - Follow the template above
   - Preserve skill-specific compositions
   - Update role descriptions if position in chain changed

3. **Update examples**
   - Review Example sections in affected SKILL.md files
   - Ensure examples still reflect the updated chain

4. **Validate handoff contracts**
   - Check that predecessor outputs match successor inputs
   - Verify fallback conditions are still valid

### When Adding Skills to a Chain

1. **Update CLAUDE.md first** (add skill to chain definition)
2. **Add Composition section to new skill's SKILL.md**
3. **Update adjacent skills** (update their "hands to" descriptions)
4. **Update skill-chain-aliases.md** (revise chain description)
5. **Update examples** (show new skill in context)

### When Removing Skills from a Chain

1. **Update CLAUDE.md first** (remove skill from chain definition)
2. **Update removed skill's SKILL.md** (change or remove Composition section)
3. **Update adjacent skills** (update handoff paths to skip the removed skill)
4. **Update skill-chain-aliases.md** (revise chain description)
5. **Document the removal** (why was it removed, what replaced it)

## Token Budget Management

### Monitoring Token Usage

Track composition section size across all skills:

```bash
# Estimate tokens in Composition sections
for skill in skills/*/SKILL.md; do
  echo -n "$(basename $(dirname $skill)): "
  sed -n '/^## Composition$/,/^## /p' "$skill" | wc -w | awk '{print int($1 * 1.3)}'
done
```

### Optimization Targets

- Individual composition section: < 100 tokens
- Total across all execution skills: < 500 tokens
- Phase/orchestration skills: use domain-appropriate patterns, don't force into execution chain model

### When to Optimize

Optimize when:

- Composition section exceeds 100 tokens
- Verbose skill listing duplicates chain definition
- Skills reference chains that are now canonical aliases

Do not optimize when:

- Skill-specific compositions add semantic value not in the chain definition
- Unique handoff conditions need explicit documentation
- The skill doesn't fit cleanly into any standard chain pattern

## Quality Standards

### Chain Alias Quality Criteria

A well-defined chain alias:

1. **Is concise**: name clearly indicates the purpose (bugfix-standard, refactor-safe, design-first)
2. **Is stable**: chain structure is unlikely to change frequently
3. **Is well-documented**: CLAUDE.md and skill-chain-aliases.md provide complete information
4. **Is consistently used**: all skills in the chain reference it correctly
5. **Adds value**: saves tokens and improves clarity vs. spelling out the chain each time

### Composition Section Quality Criteria

A well-written Composition section:

1. **References canonical chains**: uses aliases from CLAUDE.md, not verbose listings
2. **Describes role clearly**: entry/core/exit designation is obvious
3. **Shows data flow**: makes clear what inputs are received and outputs produced
4. **Preserves unique relationships**: documents skill-specific compositions not covered by standard chains
5. **Is concise**: < 100 tokens, no redundant information

## Troubleshooting

### Common Issues

**Issue**: Chain reference in SKILL.md doesn't match CLAUDE.md

**Solution**:
1. Check CLAUDE.md § Skill Chain Triggers for the authoritative definition
2. Update SKILL.md to match
3. If CLAUDE.md is wrong, update it first, then propagate to skills

---

**Issue**: Skill appears in multiple chains, Composition section is confusing

**Solution**:
1. Identify the primary chain (most common usage)
2. List primary chain first
3. Use "Also appears in" or "Additional compositions" for secondary chains
4. Keep role description focused on primary chain position

---

**Issue**: Chain alias saves no tokens because unique compositions dominate

**Solution**:
1. Evaluate if the skill really fits the standard chain pattern
2. Consider whether the skill needs a domain-specific composition template
3. Don't force chain aliases where they don't add clarity

---

**Issue**: After chain update, skill handoff contracts are broken

**Solution**:
1. Review predecessor and successor skill contracts
2. Update output/input contracts to align
3. Add migration notes in contract sections if breaking change
4. Update examples to show the new handoff

## Governance

### Change Authority

- **CLAUDE.md changes**: Require maintainer review
- **skill-chain-aliases.md changes**: Require maintainer review
- **SKILL.md Composition changes**: Can be made by contributors with PR review
- **Chain deprecation**: Requires maintainer consensus

### Review Checklist

For chain definition changes:

- [ ] CLAUDE.md updated first
- [ ] skill-chain-aliases.md updated
- [ ] All affected SKILL.md files updated
- [ ] Cross-reference validation passed
- [ ] Examples updated
- [ ] Adoption tracker updated
- [ ] Maintainer changelog entry added
- [ ] Token savings measured (if applicable)

## Metrics

Track these metrics over time:

1. **Adoption rate**: X/Y execution skills using chain aliases
2. **Token savings**: Total tokens saved vs. verbose listings
3. **Chain stability**: How often chain definitions change
4. **Coverage**: % of skills with Composition sections
5. **Quality**: Average composition section size

Target metrics:

- 100% adoption for skills in standard chains
- > 60% token reduction vs. verbose listings
- < 2 chain definition changes per release
- 100% of execution skills have Composition sections
- < 100 tokens per Composition section

## References

- CLAUDE.md § Skill Chain Triggers: authoritative chain definitions
- docs/maintainer/skill-chain-aliases.md: detailed chain documentation
- docs/maintainer/chain-alias-adoption-tracker.md: adoption status and metrics
