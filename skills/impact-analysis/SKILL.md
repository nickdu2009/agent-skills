---
name: impact-analysis
description: Assess blast radius of code changes. Use when (1) function/API has 3+ callers across modules, (2) modifies public API or shared interface, (3) changes data model used by 3+ modules, (4) mentions "might/may/could affect multiple modules/areas", or (5) read-and-locate found 3+ tentative leads. Do NOT use for 2 or fewer callers in single module.
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Purpose

Trace outward from a planned edit point to identify affected callers, dependents, modules, and contracts. The goal is to produce a structured impact summary so that plan-before-action can make informed scope and sequencing decisions.

# When to Use

- When the change involves a function/interface called by 3+ other modules.
- When the change touches a public API, shared type, or configuration schema.
- When the change involves a data model (ORM model, database schema, protobuf).
- When read-and-locate produced 3+ tentative leads.

# When Not to Use

- Single-file internal refactor with no exported symbol change.
- Pure documentation or comment changes.
- Test file modifications only.

# Core Rules

- Trace outward from the edit point: callers, dependents, type consumers, test references.
- Mark each affected module with impact type and risk level.
- Estimate the blast radius (file count, module count).
- Extract invariants that must be preserved during the change.
- Stop tracing at framework boundaries (HTTP handlers, CLI entry points, test fixtures).

# Execution Pattern

1. Receive the edit point from scoped-tasking or read-and-locate.
2. Trace direct callers of the changed symbol (layer 1).
3. Trace callers of callers (layer 2), then one more layer if needed (layer 3 max).
4. For each affected file, classify: direct consumer, transitive consumer, test reference, type dependency.
5. Check for public API surface, shared type exports, configuration schema references.
6. Output the structured impact summary.

Stop conditions (critical guardrails preventing full-repo scan):

- Tracing depth must not exceed 3 call layers.
- Total files traced must not exceed 8 (aligned with context-budget-awareness threshold).
- Stop at framework boundaries: HTTP handler, CLI entry, test fixture, plugin boundary.

# Input Contract

Provide:

- the edit point (file, function, symbol)
- the nature of the planned change
- results from read-and-locate if available

Optional:

- known callers
- suspected affected areas

# Output Contract

Return a structured impact summary:

```
affected_modules:
  - module: "auth/middleware"
    impact: "direct consumer of changed interface"
    risk: high
  - module: "tests/auth/"
    impact: "test fixtures reference old signature"
    risk: medium
blast_radius: 4 files, 2 modules
invariants_to_preserve:
  - "AuthMiddleware.validate() return type must not change without updating all callers"
stop_reason: "reached framework boundary at HTTP handler layer"
```

# Guardrails

- Do not start planning before the impact summary is complete.
- Do not trace beyond 3 call layers.
- Do not read more than 8 files during impact tracing.
- Stop tracing at framework boundaries — do not chase into HTTP handlers, CLI entry points, or test harness infrastructure.
- If blast radius exceeds the 8-file threshold, record the estimate but stop tracing. Note the overflow for plan-before-action.
- Do not confuse "reachable" with "affected" — only files that consume the changed interface count.

# Common Anti-Patterns

- **Full-repo grep instead of call tracing.** The agent greps for the function name across all files instead of tracing the actual call graph. This finds mentions in comments, strings, and unrelated code, inflating the blast radius.
- **Tracing beyond framework boundaries.** The agent follows callers past the HTTP handler into the test infrastructure and client code, treating the entire stack as "affected" when the real impact stops at the API surface.

See skill-anti-pattern-template.md for format guidelines.

# Composition

Core component of `large-task` chain (see CLAUDE.md § Skill Chain Triggers).

Role: Assess blast radius by tracing outward from edit point to affected callers, dependents, and contracts. Receives edit point from read-and-locate or design-before-plan, produces impact summary, hands to plan-before-action.

Standard forward flow:

- large-task: design-before-plan → impact-analysis → plan-before-action → incremental-delivery

Additional compositions:

- Receives input from `read-and-locate` when edit point is discovered
- Provides invariants to `safe-refactor` as preservation contract

Fallbacks:

- To `read-and-locate` when true edit point is not stable
- To `phase-plan` when contract migration becomes multi-stage or externally constrained

Drop after plan-before-action consumes the impact summary.

# Example

Task: "Change the return type of validateToken() from boolean to { valid: boolean, reason: string }."

Apply impact-analysis:

- Layer 1: 4 route handlers call validateToken directly.
- Layer 2: 1 middleware wrapper composes validateToken into an auth check.
- Layer 3: reached HTTP handler boundary — stop.
- Test references: 3 test files assert on the boolean return.
- Blast radius: 8 files, 2 modules.
- Invariants: all callers must destructure the new return shape; no caller should compare the result to true/false directly.

Hand off the summary to plan-before-action. Do not start editing.

## Contract

### Preconditions

- A planned edit point, symbol, or contract surface is already known.
- The change may affect shared callers, types, schemas, or public interfaces.
- Tracing outward can still stay within the bounded depth and file-count guardrails.

### Postconditions

- `status: completed` includes `affected_callers`, `contracts`, and `compatibility_risks`.
- The blast radius is described concretely enough for planning and sequencing.
- The analysis stops at declared framework boundaries instead of drifting into full-repo tracing.

### Invariants

- Outward tracing stays limited to affected consumers, not every textual mention.
- Depth and file-count limits remain explicit.
- Compatibility-sensitive contracts are recorded before planning begins.

### Downstream Signals

- `affected_callers` tells planning which modules or layers must be coordinated.
- `contracts` records the public or shared surfaces that may need migration.
- `compatibility_risks` identifies where rollback, phased rollout, or caller updates matter.

## Failure Handling

### Common Failure Causes

- The supposed edit point is still ambiguous or moves during tracing.
- Reachability is mistaken for actual impact, inflating the blast radius.
- The blast radius exceeds bounded tracing limits before a reliable summary is formed.

### Retry Policy

- Allow one narrowed tracing pass when the first pass overestimates affected callers.
- If the impact still exceeds bounded analysis after the second pass, stop and report the overflow instead of continuing to scan.

### Fallback

- Return to `read-and-locate` when the true edit point is not stable.
- Escalate to `phase-plan` or `design-before-plan` when contract migration becomes multi-stage or externally constrained.
- Ask the user for confirmation when compatibility trade-offs exceed the original task scope.

### Low Confidence Handling

- Mark uncertain callers as tentative rather than affected.
- Require planning to preserve extra rollback margin when compatibility risk remains medium or high.

## Output Example

```yaml
[skill-output: impact-analysis]
status: completed
confidence: high
outputs:
  affected_callers:
    - "auth/middleware"
    - "admin dashboard route handlers"
  contracts:
    - "validateToken() return shape"
  compatibility_risks:
    - "boolean comparisons must be migrated before rollout"
signals:
  blast_radius: "8 files across 2 modules"
recommendations:
  downstream_skill: "plan-before-action"
[/skill-output]
```

## Deactivation Trigger

- Deactivate once `plan-before-action` has absorbed the impact summary.
- Deactivate when the change is downgraded to a local internal edit with no shared-contract impact.
- Deactivate if broader contract work escalates into a phase-planning exercise.
