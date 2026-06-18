# Single-Agent Bugfix

## Scenario

An API returns `500` when an optional marketing profile is missing. The intended behavior is `404` with the rest of the account update flow unchanged.

## Recommended Skill Composition

- `scoped-tasking`
- `bugfix-workflow`
- `targeted-validation`

Editing follows `AGENTS.md` Behavioral Guidelines §4 short planning (plan + verify); this bugfix is intentionally small enough that `implementation-planning` is not needed.

## Why This Composition

- `scoped-tasking` keeps the investigation inside the handler, service, and profile lookup path.
- `bugfix-workflow` prevents editing before the symptom and fault domain are clear.
- AGENTS.md §4 forces the agent to declare the intended edit surface and per-step verification before touching files.
- `targeted-validation` keeps verification limited to the affected endpoint or test path.

## Example Execution

1. State the symptom clearly.
   - "Updating an account with no marketing profile returns `500`."
2. Define the smallest plausible fault domain.
   - request handler
   - account service
   - marketing profile lookup
3. Gather evidence.
   - inspect the failing test or route handler
   - confirm whether a nullable lookup result is dereferenced
4. Plan before editing.
   - intended files: request handler or service method, targeted test
   - intended action: convert missing optional profile into a handled `404`
5. Apply the smallest viable fix.
   - add a local guard where the missing profile is first handled
6. Validate narrowly.
   - run the endpoint-focused test or reproduction command
   - avoid unrelated account-management tests

## Example Progress Format

- Done: confirmed the `nil` access occurs after the optional profile lookup.
- Not done: patch the handler/service and prove the `404` behavior.
- Next: add the guard and run the profile-missing test path.

## Guardrails

- Do not widen into a global error-handling refactor.
- Do not rename profile-related interfaces.
- Do not run the full API suite by default.
- If the symptom cannot be reproduced directly, state the remaining uncertainty.

## Skill Protocol v2 Trace

```text
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
[precheck: bugfix-workflow | result:PASS | checks:symptom_known repro_available]
[validate: bugfix-workflow | result:PASS | checks:symptom fault_domain]
```
