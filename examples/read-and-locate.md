# Read and Locate

## Scenario

You need to add a `requestedBy` audit field to export jobs, but the codebase is unfamiliar and the edit point is unknown.

## Recommended Skill Composition

- `scoped-tasking`
- `read-and-locate`
- `plan-before-action`

Add `context-budget-awareness` if the discovery path starts branching into too many unrelated export modules.

## Example Discovery Strategy

1. Start from the strongest clue.
   - the export API endpoint
   - the export command
   - a failing export test
2. Identify the first likely entry point.
   - route handler or command handler
3. Trace only the adjacent path.
   - request parsing
   - job creation service
   - job serializer or persistence boundary
4. Mark findings explicitly.
   - confirmed locations
   - tentative leads
5. Stop once the likely edit points are known.

## Example Output

### Confirmed Locations

- export request handler creates the command payload
- export service builds the job object
- job repository persists the serialized job record

### Tentative Leads

- worker-side export executor may read the field later
- audit logger may already support a similar field

### Likely Edit Points

- command payload definition
- job serializer
- narrow tests covering export job creation

## Guardrails

- Do not inspect every export-related worker before the write path is understood.
- Do not confuse a nearby file with a confirmed ownership boundary.
- Once the creation and persistence path are clear, stop exploring and move to planning.

## Skill Protocol v1 Trace

```yaml
[task-input-validation]
task: "Find where to add requestedBy to export jobs in an unfamiliar codebase."
checks:
  clarity:
    status: PASS
    reason: "The desired field addition and unknown ownership are explicit."
  scope:
    status: WARN
    reason: "Edit point is unknown but can be narrowed through discovery."
  safety:
    status: PASS
    reason: "Discovery and bounded planning are safe."
  skill_match:
    status: PASS
    reason: "read-and-locate is a direct fit."
result: WARN
action: ask_clarification
[/task-input-validation]

[trigger-evaluation]
task: "Locate export job ownership path."
evaluated:
  - scoped-tasking: ✓ TRIGGER
  - read-and-locate: ✓ TRIGGER
  - plan-before-action: ⏸ DEFER
activated_now: [scoped-tasking, read-and-locate]
deferred: [plan-before-action]
[/trigger-evaluation]

[precondition-check: read-and-locate]
checks:
  - strongest_clue_available: ✓ PASS
  - exact_symbol_lookup_insufficient: ✓ PASS
result: PASS
[/precondition-check]

[skill-output: read-and-locate]
status: completed
confidence: medium
outputs:
  entry_points: ["export API endpoint", "export command handler"]
  candidate_files: ["export_service", "job_serializer", "job_repository"]
  edit_points: ["job payload definition", "job serializer write path"]
signals:
  validation_surface: ["export job creation tests"]
recommendations:
  downstream_skill: "plan-before-action"
[/skill-output]

[output-validation: read-and-locate]
checks:
  - outputs.entry_points: ✓ PASS
  - outputs.edit_points: ✓ PASS
result: PASS
[/output-validation]

[skill-deactivation: read-and-locate]
reason: "Likely edit points are now known."
outputs_consumed_by: [plan-before-action]
remaining_active: [plan-before-action]
[/skill-deactivation]
```
