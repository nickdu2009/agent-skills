# Test Example: Simple Bugfix (v2 Format)

This is a test file to validate v2 protocol parsing.

## Protocol Trace

[task-validation: PASS | clarity:✓ scope:✓ safety:✓ skill_match:✓ | action:proceed]

[triggers: scoped-tasking bugfix-workflow]

[precheck: scoped-tasking | PASS | checks:objective boundary]
[output: scoped-tasking | completed high | objective:"fix timeout" analysis_boundary:"auth module" | next:bugfix-workflow]
[validate: scoped-tasking | PASS | checks:objective analysis_boundary]
[drop: scoped-tasking | reason:"boundary confirmed" | active: bugfix-workflow]

[precheck: bugfix-workflow | PASS | checks:symptom repro]
[validate: bugfix-workflow | PASS | checks:root_cause fix_location]
