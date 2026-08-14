# Chain Alias Maintenance Guide

**Status**: Current authority

Chain aliases are documentation shorthand for recurring Skill compositions. They do not activate Skills, change runtime behavior, or belong to the Agent Skills standard.

## Sources

- Root `AGENTS.md` records this repository's live common flow patterns.
- [`skill-chain-aliases.md`](skill-chain-aliases.md) explains reusable alias meaning.
- Each participating `SKILL.md` owns its actual composition and handoff contract.

## Add Or Change An Alias

1. Confirm the sequence appears in multiple real task shapes and is not a one-off.
2. Update the repository flow pattern and alias definition.
3. Update only participating Skills whose composition or handoff actually changes.
4. Preserve each Skill's preconditions, outputs, failure handling, and stop condition.
5. Run:

```bash
python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report
```

## Remove Or Rename An Alias

- Search Skill and documentation references first.
- Replace references in one bounded change.
- Do not leave the old alias as a silent compatibility behavior; document a temporary textual redirect only when an active consumer requires it.
- Re-run cross-reference and trigger checks.

## Constraints

- Alias names are lowercase hyphenated documentation identifiers.
- Aliases never replace explicit Skill names in frontmatter.
- A chain does not authorize automatic continuation across an unresolved requirement, public contract, persistence, dependency, destructive, or remote-operation boundary.
- Runtime-specific invocation and discovery behavior stays outside this document.
