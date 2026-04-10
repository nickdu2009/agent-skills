# Skill Chain Aliases

**Version**: 1.0  
**Date**: 2026-04-11  
**Status**: Active

## Purpose

This document defines canonical chain patterns that can be referenced by alias in documentation, examples, and governance. Chain aliases reduce repeated prose across skill docs while preserving the full chain definition in a single authoritative location.

## Scope

Chain aliases are documentation shortcuts, not runtime primitives. They:

- Simplify examples and maintainer docs
- Enable consistent chain naming across the repository
- Reduce token cost from repeated chain narration
- Centralize chain definitions for easier maintenance

They do not:

- Replace the detailed chain trigger tables in CLAUDE.md
- Introduce new runtime batch activation behavior
- Change how skills are activated or deactivated
- Modify skill preconditions or contracts

## Canonical Chain Definitions

### bugfix-standard

**Full chain:**  
`scoped-tasking` → `read-and-locate` → `bugfix-workflow` → `minimal-change-strategy` → `self-review` → `targeted-validation`

**Use when:**

- A bug symptom is reported but root cause is unknown
- The failure path needs to be traced through unfamiliar code
- The fix should be minimal and verified against the original symptom

**Entry point:** `scoped-tasking` narrows the fault domain  
**Exit:** `targeted-validation` confirms the symptom no longer reproduces  

**Variations:**

- Skip `read-and-locate` if the fault domain is already known
- Skip `self-review` for trivial one-line patches
- Add `context-budget-awareness` if diagnosis spans too many files or hypotheses

**Example trigger:** "Background retries sometimes send duplicate emails"

---

### refactor-safe

**Full chain:**  
`scoped-tasking` → `safe-refactor` + `minimal-change-strategy` → `self-review` → `targeted-validation`

**Use when:**

- The task is structural cleanup, extraction, or simplification
- Behavior and interfaces must remain stable
- The change should be small and behavior-preserving

**Entry point:** `scoped-tasking` defines the cleanup boundary  
**Exit:** `targeted-validation` confirms no behavior regression  

**Co-activation:** `safe-refactor` and `minimal-change-strategy` run together to balance structural improvement with patch size control.

**Fallbacks:**

- → `design-before-plan` if structural change requires interface redesign
- → `minimal-change-strategy` if only local cleanup is justified, not structural refactoring
- → `read-and-locate` if ownership seams are unclear

**Example trigger:** "Extract repeated validation logic into a shared helper"

---

### multi-file-planned

**Full chain:**  
`scoped-tasking` → `plan-before-action` → `minimal-change-strategy` → `self-review` → `targeted-validation`

**Use when:**

- The change spans 3+ files or requires sequencing
- The task involves uncertainty or assumptions
- Progress reporting matters because the work is multi-phase

**Entry point:** `scoped-tasking` defines the working set  
**Exit:** `targeted-validation` verifies the narrowest meaningful check  

**Variations:**

- Prepend `read-and-locate` if edit points are not yet known after scoping
- Append or escalate to `incremental-delivery` if the plan spans 2–4 PRs

**Example trigger:** "Add retry logic around the payment gateway with exponential backoff"

---

### design-first

**Full chain:**  
`scoped-tasking` → `design-before-plan` → `plan-before-action` → `minimal-change-strategy` → `self-review` → `targeted-validation`

**Use when:**

- Multiple implementation approaches exist and need comparison
- The change introduces or modifies a public API or cross-module contract
- Acceptance criteria are unclear or missing
- Design decisions block planning

**Entry point:** `scoped-tasking` confirms the boundary  
**Handoff:** `design-before-plan` → `plan-before-action` once the design brief is complete  
**Exit:** `targeted-validation` verifies the contract  

**Deactivation note:** Drop `design-before-plan` after the design brief is handed to `plan-before-action` — it does not stay active during implementation.

**Example trigger:** "Add pagination to the search API"

---

### large-task

**Full chain:**  
`scoped-tasking` → `design-before-plan` → `impact-analysis` → `plan-before-action` → `incremental-delivery`

**Use when:**

- The task spans 2–4 PRs across 1–2 modules
- The change affects multiple callers or shared contracts
- Impact radius is uncertain and needs assessment before planning
- Delivery can be split into independently mergeable increments

**Entry point:** `scoped-tasking` confirms the task boundary  
**Handoffs:**

1. `design-before-plan` → `impact-analysis` when caller/module impact is still speculative
2. `impact-analysis` → `plan-before-action` after the impact summary is produced
3. `plan-before-action` → `incremental-delivery` when the plan identifies 2–4 independently mergeable PRs

**Exit:** `incremental-delivery` produces the increment list; execution then follows per-increment chains

**Escalation:**

- → `phase-plan` if the task exceeds 4 increments, 2 modules, or needs parallel lanes

**Example trigger:** "Migrate authentication from session tokens to JWT across the API layer"

---

### parallel

**Full chain:**  
`multi-agent-protocol` → [subagents] → `conflict-resolution` (if needed) → synthesis

**Use when:**

- The task can be cleanly split across 2–4 independent dimensions
- Each subagent can work in parallel without shared state
- Results need synthesis after parallel execution

**Entry point:** Primary agent declares `[delegate: <count> | split: <dimension> | risk: <level>]`  
**Exit:** Primary agent synthesizes subagent findings  

**Conditional:** `conflict-resolution` activates only if subagent findings materially disagree.

**Example trigger:** "Analyze test coverage across backend, frontend, and mobile repos"

---

## Usage Guidance

### When to use aliases

Use chain aliases in:

- Skill SKILL.md examples and composition sections (if referencing well-known flows)
- Maintainer documentation when explaining workflow patterns
- Governance docs when summarizing common task flows
- Training materials and onboarding guides

### When to spell out full chains

Spell out the full chain when:

- The chain definition itself is the topic (e.g., in CLAUDE.md Skill Chain Triggers)
- A variation or fallback deviates meaningfully from the canonical alias
- Precision matters more than brevity (e.g., in contract or precondition sections)
- The alias does not yet exist or is under debate

### Cross-references

- Full chain trigger rules: `/CLAUDE.md` § Skill Chain Triggers
- Forward handoff conditions: `/CLAUDE.md` § Forward Handoffs
- Fallback conditions: `/CLAUDE.md` § Fallbacks
- Skill lifecycle rules: `/CLAUDE.md` § Skill Lifecycle

## Alias Naming Convention

Chain aliases follow this pattern:

- **Descriptive stem** (e.g., `bugfix`, `refactor`, `multi-file`, `design`, `large-task`, `parallel`)
- **Qualifier suffix** (e.g., `-standard`, `-safe`, `-planned`, `-first`) to distinguish variants

Avoid:

- Generic names (`workflow-1`, `chain-a`)
- Tool-specific jargon (`cursor-chain`, `claude-flow`)
- Overly cute or whimsical names (`mega-chain`, `turbo-mode`)

## Maintenance Protocol

When a canonical chain changes:

1. Update this document first
2. Review references in maintainer docs
3. Update examples in affected SKILL.md files (if they use the alias directly)
4. Regenerate governance templates if chain triggers are affected
5. Update trigger test data if new entry/exit conditions apply

When proposing a new alias:

1. Verify the chain appears in at least 3 distinct usage contexts
2. Confirm it is stable enough to document as canonical
3. Add it to this file with full definition, use-when criteria, and example trigger
4. Announce in maintainer changelog or design notes

## Before/After Example

### Before (repeated chain prose)

In `bugfix-workflow/SKILL.md`:

```markdown
Combine with:
- scoped-tasking to keep diagnosis inside the smallest plausible domain
- read-and-locate to trace the relevant path quickly
- minimal-change-strategy to keep the fix small
- targeted-validation to verify the symptom without paying unnecessary suite cost
```

In `scoped-tasking/SKILL.md`:

```markdown
Combine with:
- read-and-locate when the edit point is not known yet
- plan-before-action to convert the scoped boundary into a concrete work plan
- minimal-change-strategy once an edit path is clear
- targeted-validation to keep verification aligned to the same boundary
```

### After (using aliases)

In `bugfix-workflow/SKILL.md`:

```markdown
Combine with:
- scoped-tasking, read-and-locate, minimal-change-strategy, and targeted-validation
  (see canonical bugfix-standard chain in docs/maintainer/skill-chain-aliases.md)
```

In `scoped-tasking/SKILL.md`:

```markdown
Common flows:
- bugfix-standard: scoped-tasking → read-and-locate → bugfix-workflow → ...
- multi-file-planned: scoped-tasking → plan-before-action → ...
- refactor-safe: scoped-tasking → safe-refactor + minimal-change-strategy → ...

(Full definitions: docs/maintainer/skill-chain-aliases.md)
```

## Token Savings Estimate

Rough calculation for repeated chain narration:

- Full chain prose: ~80–120 tokens per instance
- Chain alias reference: ~15–25 tokens per instance
- Net savings: ~60–95 tokens per replaced instance

If chain patterns appear in:

- 10 skill composition sections
- 5 maintainer doc examples
- 3 governance flow summaries

Total estimated savings: ~1,000–1,700 tokens across the repository.

This estimate does not include secondary benefits from easier maintenance and reduced cognitive load when scanning documentation.
