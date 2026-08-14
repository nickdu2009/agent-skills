# Skill Chain Aliases

**Version**: 1.0  
**Date**: 2026-04-11  
**Status**: Current authority
**Current implementation note**: Updated for the 12-skill model. Review routing is consolidated in `artifact-review-loop`; lightweight repository planning lives in `AGENTS.md`, while durable implementation planning routes through `implementation-planning`.

## Purpose

This document defines canonical chain patterns that can be referenced by alias in documentation, examples, and governance. Chain aliases reduce repeated prose across skill docs while preserving the full chain definition in a single authoritative location.

## Scope

Chain aliases are documentation shortcuts, not runtime primitives. They:

- Simplify examples and maintainer docs
- Enable consistent chain naming across the repository
- Reduce token cost from repeated chain narration
- Centralize chain definitions for easier maintenance

They do not:

- Replace the repository maintenance flow patterns in `AGENTS.md`
- Introduce new runtime batch activation behavior
- Change how skills are activated or deactivated
- Modify skill preconditions or contracts

## Canonical Chain Definitions

### bugfix-standard

**Full chain:**  
`scoped-tasking` → `bugfix-workflow` → `artifact-review-loop` (`self-delivery`) → `targeted-validation`

**Use when:**

- A bug symptom is reported but root cause is unknown
- The failure path needs to be traced through unfamiliar code
- The fix should be minimal and verified against the original symptom

**Entry point:** `scoped-tasking` narrows the fault domain  
**Exit:** `targeted-validation` confirms the symptom no longer reproduces  

**Variations:**

- Skip self-delivery review for trivial one-line patches

**Example trigger:** "Background retries sometimes send duplicate emails"

---

### refactor-safe

**Full chain:**  
`scoped-tasking` → `safe-refactor` → `artifact-review-loop` (`self-delivery`) → `targeted-validation`

**Use when:**

- The task is structural cleanup, extraction, or simplification
- Behavior and interfaces must remain stable
- The change should be small and behavior-preserving

**Entry point:** `scoped-tasking` defines the cleanup boundary  
**Exit:** `targeted-validation` confirms no behavior regression  

**Fallbacks:**

- → `design-before-plan` if structural change requires interface redesign

**Example trigger:** "Extract repeated validation logic into a shared helper"

---

### multi-file-planned

**Full chain:**  
`scoped-tasking` → `implementation-planning` → `artifact-review-loop` (`self-delivery`) → `targeted-validation`

**Use when:**

- The change spans 3+ files or requires sequencing
- The task involves uncertainty or assumptions
- Progress reporting matters because the work is multi-phase

**Entry point:** `scoped-tasking` defines the working set  
**Exit:** `targeted-validation` verifies the narrowest meaningful check  

**Variations:**

**Example trigger:** "Add retry logic around the payment gateway with exponential backoff"

---

### design-first

**Full chain:**  
`scoped-tasking` → `design-before-plan` → `impact-analysis` → `implementation-planning`

**Use when:**

- Multiple implementation approaches exist and need comparison
- The change introduces or modifies a public API or cross-module contract
- Acceptance criteria are unclear or missing
- Design decisions block planning

**Entry point:** `scoped-tasking` confirms the boundary  
**Handoff:** `design-before-plan` → `impact-analysis` when shared callers, data models, or public contracts need blast-radius review; `impact-analysis` → `implementation-planning` when sequencing is ready
**Exit:** an implementation plan under `implementation-planning`, followed by `targeted-validation` after code changes

**Deactivation note:** Drop `design-before-plan` after the design brief is accepted or handed to implementation planning — it does not stay active during implementation.

**Example trigger:** "Add pagination to the search API"

---

### large-task

**Status:** Historical alias retained for older maintainer reports. Current governance handles this with `scoped-tasking`, `design-before-plan`, `impact-analysis`, `implementation-planning`, and optional `multi-agent-protocol`; there is no dedicated phase or incremental-delivery skill in the live 12-skill set.

**Full chain:**  
No active canonical chain. Use the current common flow patterns instead.

**Use when:**

- The task spans 2–4 PRs across 1–2 modules
- The change affects multiple callers or shared contracts
- Impact radius is uncertain and needs assessment before planning
- Delivery can be split into independently mergeable increments

**Entry point:** `scoped-tasking` confirms the task boundary  
**Handoffs:**

1. `design-before-plan` → `impact-analysis` when caller/module impact is still speculative
2. `impact-analysis` → `implementation-planning` after the impact summary is produced

**Escalation:**

- Split the work across separate sessions or ask the user to re-scope if it grows beyond 4 increments, 2 modules, or needs parallel lanes

**Example trigger:** "Migrate authentication from session tokens to JWT across the API layer"

---

### parallel

**Full chain:**  
`multi-agent-protocol` → synthesis

**Use when:**

- The task can be cleanly split across 2–4 independent dimensions
- Each subagent can work in parallel without shared state
- Results need synthesis after parallel execution

**Entry point:** Primary agent declares `[delegate: <count> | split: <dimension> | risk: <level>]`  
**Exit:** Primary agent synthesizes subagent findings  

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

- The chain definition itself is the topic
- A variation or fallback deviates meaningfully from the canonical alias
- Precision matters more than brevity (e.g., in contract or precondition sections)
- The alias does not yet exist or is under debate

### Cross-references

- Common flow patterns: `/AGENTS.md` § Common Flow Patterns
- Skill activation and escalation: `/AGENTS.md` § Skill Activation and § Escalation Rules
- Skill lifecycle rules: `/AGENTS.md` § Skill Lifecycle

## Alias Naming Convention

Chain aliases follow this pattern:

- **Descriptive stem** (e.g., `bugfix`, `refactor`, `multi-file`, `design`, `large-task`, `parallel`)
- **Qualifier suffix** (e.g., `-standard`, `-safe`, `-planned`, `-first`) to distinguish variants

Avoid:

- Generic names (`workflow-1`, `chain-a`)
- Runtime-specific jargon (`editor-chain`, `vendor-flow`)
- Overly cute or whimsical names (`mega-chain`, `turbo-mode`)

## Maintenance Protocol

When a canonical chain changes:

1. Update this document first
2. Review references in maintainer docs
3. Update examples in affected SKILL.md files (if they use the alias directly)
4. Update affected Skill descriptions or examples when chain triggers change
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
- targeted-validation to verify the symptom without paying unnecessary suite cost
```

In `scoped-tasking/SKILL.md`:

```markdown
Combine with:
- implementation-planning to convert the scoped boundary into a durable work plan when sequencing and rollback matter
- targeted-validation to keep verification aligned to the same boundary
```

### After (using aliases)

In `bugfix-workflow/SKILL.md`:

```markdown
Combine with:
  (see canonical bugfix-standard chain in docs/maintainer/skill-chain-aliases.md)
```

In `scoped-tasking/SKILL.md`:

```markdown
Common flows:
- multi-file-planned: scoped-tasking → implementation-planning → ...

(Full definitions: docs/maintainer/skill-chain-aliases.md)
```

## Adoption Status

**Last updated**: 2026-08-13

This section records current live-chain status. Older optimization reports may mention the pre-2026-05 18-skill set; treat those as historical snapshots.

### Live Governance Chains

| Alias | Current status | Live chain |
|---|---|---|
| `bugfix-standard` | Current | `scoped-tasking` → `bugfix-workflow` → `artifact-review-loop` (`self-delivery`) → `targeted-validation` |
| `refactor-safe` | Current | `scoped-tasking` → `safe-refactor` → `artifact-review-loop` (`self-delivery`) → `targeted-validation` |
| `multi-file-planned` | Current | `scoped-tasking` → `implementation-planning` → `artifact-review-loop` (`self-delivery`) → `targeted-validation` |
| `design-first` | Current | `scoped-tasking` → `design-before-plan` → `impact-analysis` → `implementation-planning` |
| `parallel` | Current | `multi-agent-protocol` → synthesis |
| `large-task` | Historical | Retained for older reports; use current common flow patterns instead |

### Historical Optimization Snapshot (2026-04-11)

The token-savings figures below describe the old 18-skill optimization pass and are kept for historical comparison only.

- **bugfix-workflow**: Adopted `bugfix-standard` chain alias (~55 tokens saved)
- **design-before-plan**: Adopted `design-first` and `large-task` chain aliases (~45 tokens saved)
- **impact-analysis**: Adopted `large-task` chain alias (~50 tokens saved)

Total savings from Phase 2: ~260 tokens

### Orchestration Skills

These skills use domain-specific composition patterns that don't map to standard execution chains:

- multi-agent-protocol: Uses `parallel` chain (correctly optimized)

## Token Savings Achieved

### Before Optimization (All Execution Skills)

- Total verbose composition sections: ~1,085 tokens
- Average per skill: ~90 tokens

### After Optimization (All Execution Skills)

- Total optimized composition sections: ~375 tokens
- Average per skill: ~31 tokens

### Total Impact

- **Tokens saved**: ~710 tokens (65.4% reduction)
- **Historical scope**: old 12 execution skill subset
- **Current status**: historical measurement only; do not use as the current 12-skill inventory

### Breakdown by Optimization Phase

| Phase | Skills | Tokens Before | Tokens After | Savings |
|-------|--------|--------------|--------------|---------|
| Phase 1 (Pre-existing) | 7 | ~690 | ~240 | ~450 |
| Phase 2 (2026-04-11) | 5 | ~395 | ~135 | ~260 |
| **Total** | **12** | **~1,085** | **~375** | **~710** |

## Maintenance

See docs/maintainer/chain-alias-maintenance.md for:

- Adding new chain patterns
- Updating existing chains
- Propagating chain changes to skills
- Validation procedures
