# Test Example: Validation Failure (v2 Format)

This tests v2 protocol parsing with failure scenarios.

## Protocol Trace

[task-validation: WARN | clarity:✓ scope:⚠ "spans 3 modules" safety:✓ skill_match:✓ | action:ask_clarification]

[triggers: scoped-tasking | defer: design-before-plan]

[precheck: scoped-tasking | PASS]
[output: scoped-tasking | partial medium | narrowed_scope:"auth and user modules" excluded:"payment module" | next:design-before-plan]
[validate: scoped-tasking | FAIL | checks:narrowed_scope | failed:excluded "missing justification"]
[drop: scoped-tasking | reason:"partial scoping needs confirmation" | active: none]
