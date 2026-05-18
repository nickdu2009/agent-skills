# Impact Analysis

## Scenario

A shared authentication middleware function `validateToken()` needs its
return type changed from `boolean` to `{ valid: boolean, reason: string }`.
The function is called by 4 route handlers across 2 modules, plus 3 test files.

## Recommended Skill Composition

- scoped-tasking
- impact-analysis

Planning follows `AGENTS.md` Behavioral Guidelines §4 (plan + verify).

## Why This Composition

- impact-analysis traces outward from the edit point to assess blast radius.
- AGENTS.md §4 uses the impact summary to declare a per-step implementation plan.

## Example Execution

2. impact-analysis traces callers:
   - 4 route handlers (direct consumers)
   - 3 test files (assertion patterns)
   - 1 type definition file (exported interface)
3. impact-analysis outputs structured summary:
   - blast_radius: 8 files, 2 modules
   - risk: high (public interface change)
   - invariants: all callers must handle the new return shape
4. AGENTS.md §4 plan uses impact summary to sequence edits with per-step verify checks.
5. Execution proceeds with informed scope.

## Guardrails

- Do not start planning before impact summary is complete.
- Do not trace beyond 3 call layers.
- Do not read more than 8 files during impact analysis.
- Stop tracing at framework boundaries (HTTP handler, test fixture).
- If blast radius exceeds 8 files, note but do not keep exploring.

## Skill Protocol v2 Trace

```
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
[precheck: impact-analysis | result:PASS | checks:edit_point_known shared_contract_risk_present]
[output: impact-analysis | status:completed | confidence:high | affected_callers:"4 route handlers, 3 test files" | contracts:"validateToken() return type" | compatibility_risks:"boolean comparisons must be migrated" | blast_radius:"8 files across 2 modules" | next:implementation]
[validate: impact-analysis | result:PASS | checks:affected_callers compatibility_risks]
[drop: impact-analysis | reason:"impact summary ready for AGENTS.md §4 plan" | active:none]
```
