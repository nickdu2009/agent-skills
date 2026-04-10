---
name: impact-analysis
description: Assess the blast radius of a planned code change by tracing outward from the edit point to affected callers, dependents, and contracts before planning. Use when the change touches shared interfaces, public APIs, data models, or has 3+ tentative leads from discovery.
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

# Composition

- Depends on `read-and-locate` (edit point and discovery results are input).
- Outputs to `plan-before-action` (impact summary informs the plan).
- Outputs to `safe-refactor` (invariants list serves as the preservation contract).
- Drop after `plan-before-action` produces the plan — impact-analysis does not stay active during editing.

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
