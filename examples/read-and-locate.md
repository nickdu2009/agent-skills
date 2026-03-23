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
