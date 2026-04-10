# Impact Analysis

## Scenario

A shared authentication middleware function `validateToken()` needs its
return type changed from `boolean` to `{ valid: boolean, reason: string }`.
The function is called by 4 route handlers across 2 modules, plus 3 test files.

## Recommended Skill Composition

- scoped-tasking
- read-and-locate
- impact-analysis
- plan-before-action
- minimal-change-strategy

## Why This Composition

- read-and-locate finds the function and its call sites.
- impact-analysis traces outward from the edit point to assess blast radius.
- plan-before-action uses the impact summary to make an informed plan.

## Example Execution

1. read-and-locate finds validateToken and its location.
2. impact-analysis traces callers:
   - 4 route handlers (direct consumers)
   - 3 test files (assertion patterns)
   - 1 type definition file (exported interface)
3. impact-analysis outputs structured summary:
   - blast_radius: 8 files, 2 modules
   - risk: high (public interface change)
   - invariants: all callers must handle the new return shape
4. plan-before-action uses impact summary to plan edit sequence.
5. Execution proceeds with informed scope.

## Guardrails

- Do not start planning before impact summary is complete.
- Do not trace beyond 3 call layers.
- Do not read more than 8 files during impact analysis.
- Stop tracing at framework boundaries (HTTP handler, test fixture).
- If blast radius exceeds 8 files, note but do not keep exploring.

## Skill Protocol v1 Trace

```yaml
[task-input-validation]
task: "Assess the blast radius of changing validateToken() return shape."
checks:
  clarity:
    status: PASS
    reason: "The edit point and affected surface are explicit."
  scope:
    status: PASS
    reason: "Impact tracing is bounded by call depth and file count."
  safety:
    status: PASS
    reason: "This pass is read-first analysis."
  skill_match:
    status: PASS
    reason: "impact-analysis is the intended pre-planning skill."
result: PASS
action: proceed
[/task-input-validation]

[trigger-evaluation]
task: "Trace validateToken caller impact."
evaluated:
  - read-and-locate: ✓ TRIGGER
  - impact-analysis: ✓ TRIGGER
  - plan-before-action: ⏸ DEFER
activated_now: [read-and-locate, impact-analysis]
deferred: [plan-before-action]
[/trigger-evaluation]

[precondition-check: impact-analysis]
checks:
  - edit_point_known: ✓ PASS
  - shared_contract_risk_present: ✓ PASS
result: PASS
[/precondition-check]

[skill-output: impact-analysis]
status: completed
confidence: high
outputs:
  affected_callers:
    - "4 route handlers"
    - "3 test files"
  contracts:
    - "validateToken() return type"
  compatibility_risks:
    - "boolean comparisons must be migrated"
signals:
  blast_radius: "8 files across 2 modules"
recommendations:
  downstream_skill: "plan-before-action"
[/skill-output]

[output-validation: impact-analysis]
checks:
  - outputs.affected_callers: ✓ PASS
  - outputs.compatibility_risks: ✓ PASS
result: PASS
[/output-validation]

[skill-deactivation: impact-analysis]
reason: "The impact summary is ready for planning."
outputs_consumed_by: [plan-before-action]
remaining_active: [plan-before-action]
[/skill-deactivation]
```
