# Skill Protocol v2: Compact Representation

**Version**: 2.0  
**Date**: 2026-04-11  
**Status**: Draft  
**Scope**: Repository governance templates and skill execution

## Overview

Protocol v2 introduces a compact, inline representation of skill execution protocol blocks. It coexists with the existing v1 verbose YAML-style blocks and is designed to reduce token footprint in governance templates, skill examples, and agent execution traces.

## Design Principles

1. **Backward compatible**: v1 remains the canonical reference form.
2. **Opt-in**: Use v2 where readability and maintainability remain acceptable.
3. **No runtime dependency**: This is a text representation choice, not a runtime feature.
4. **Evaluation safe**: Test harnesses must support both forms.

## Protocol Block Mapping

### Task Input Validation

**v1 (verbose):**

```yaml
[task-input-validation]
task: "Fix the login bug in auth.py"
checks:
  clarity:
    status: PASS
    reason: "Action (fix) and target (login bug in auth.py) clear"
  scope:
    status: PASS
    reason: "Bounded to single file and function"
  safety:
    status: PASS
    reason: "No destructive operations"
  skill_match:
    status: PASS
    reason: "bugfix-workflow applies"
result: PASS
action: proceed
[/task-input-validation]
```

**v2 (compact):**

```
[task-validation: PASS | clarity:✓ scope:✓ safety:✓ skill_match:✓ | action:proceed]
```

**v2 with reasons (when failure/warning needs explanation):**

```
[task-validation: WARN | clarity:✓ scope:⚠ "spans 3 modules" safety:✓ skill_match:✓ | action:ask_clarification]
```

**v2 rejection:**

```
[task-validation: REJECT | safety:✗ "requests force-push to main" | action:reject]
```

### Trigger Evaluation

**v1 (verbose):**

```yaml
[trigger-evaluation]
task: "Fix authentication timeout in user service"
evaluated:
  - scoped-tasking: ✓ TRIGGER
  - read-and-locate: ⏸ DEFER
  - bugfix-workflow: ✓ TRIGGER
  - plan-before-action: ✗ SKIP
activated_now: [scoped-tasking, bugfix-workflow]
deferred: [read-and-locate]
[/trigger-evaluation]
```

**v2 (compact):**

```
[triggers: scoped-tasking bugfix-workflow | defer: read-and-locate]
```

**v2 with skip detail (optional):**

```
[triggers: scoped-tasking bugfix-workflow | skip: plan-before-action "single file" | defer: read-and-locate]
```

### Precondition Check

**v1 (verbose):**

```yaml
[precondition-check: bugfix-workflow]
checks:
  - symptom_described: ✓ PASS
  - root_cause_unknown: ✓ PASS
  - edit_point_unknown: ✗ FAIL
result: FAIL
[/precondition-check]
```

**v2 (compact):**

```
[precheck: bugfix-workflow | FAIL | symptom:✓ root_cause:✓ edit_point:✗]
```

**v2 pass:**

```
[precheck: bugfix-workflow | PASS]
```

### Skill Output

**v1 (verbose):**

```yaml
[skill-output: bugfix-workflow]
status: completed
confidence: high
outputs:
  root_cause: "Auth token expires too quickly in session.py:42"
  fix_location: "session.py:42, config.yaml:15"
  test_strategy: "Unit test session timeout logic"
signals:
  working_set_size: 2
  hypotheses_tested: 3
recommendations:
  next_skill: minimal-change-strategy
[/skill-output]
```

**v2 (compact):**

```
[output: bugfix-workflow | completed high | root_cause:"Auth token expires too quickly in session.py:42" | next:minimal-change-strategy]
```

**v2 partial/failed:**

```
[output: bugfix-workflow | partial medium | root_cause:"narrowed to auth module" | next:read-and-locate]
```

### Output Validation

**v1 (verbose):**

```yaml
[output-validation: bugfix-workflow]
checks:
  - outputs.root_cause: ✓ PASS
  - outputs.fix_location: ✓ PASS
  - outputs.test_strategy: ✓ PASS
result: PASS
[/output-validation]
```

**v2 (compact):**

```
[validate: bugfix-workflow | PASS]
```

**v2 with failures:**

```
[validate: bugfix-workflow | FAIL | root_cause:✓ fix_location:✗ "missing line number"]
```

### Skill Deactivation

**v1 (verbose):**

```yaml
[skill-deactivation: bugfix-workflow]
reason: "Root cause confirmed, fix handed to minimal-change-strategy"
outputs_consumed_by: [minimal-change-strategy]
remaining_active: [minimal-change-strategy, targeted-validation]
[/skill-deactivation]
```

**v2 (compact):**

```
[drop: bugfix-workflow | reason:"root cause confirmed" | active: minimal-change-strategy targeted-validation]
```

### Loop Detection

**v1 (verbose):**

```yaml
[loop-detected: read-and-locate]
reason: "Re-activating without new evidence after 2 previous attempts"
last_activation: "3 actions ago"
[/loop-detected]
```

**v2 (compact):**

```
[loop: read-and-locate | "re-activating without new evidence"]
```

## When to Use v2

### Recommended for v2

- **Governance template examples**: Shorter blocks improve template readability.
- **Skill SKILL.md examples**: Compact examples reduce doc size.
- **Simple pass cases**: When all checks pass, compact form is clearer.
- **Execution traces**: Agent logs with many blocks benefit from compression.

### Keep v1 for

- **Failure diagnosis**: When multiple checks fail and detailed reasons matter.
- **Complex validations**: When outputs have rich nested structures.
- **Tutorial/onboarding material**: Learners benefit from explicit structure.
- **Debugging**: Verbose form makes troubleshooting easier.

## Syntax Rules

### General

- Block format: `[<command>: <target> | <fields>]`
- Field separator: `|` (pipe with surrounding spaces)
- Multi-value separator: space (e.g., `active: skill1 skill2`)
- Quoted strings: Use `"..."` for values with spaces or special chars
- Status symbols: `✓` (pass), `✗` (fail), `⚠` (warn), `⏸` (defer)

### Symbol Shortcuts

- `PASS` / `✓` interchangeable in status fields
- `FAIL` / `✗` interchangeable in status fields
- `WARN` / `⚠` interchangeable in status fields

### Omitting Fields

Fields can be omitted when they follow standard defaults:

- **Precondition pass**: `[precheck: skill-name | PASS]` (no need to list individual checks)
- **Output validation pass**: `[validate: skill-name | PASS]`
- **Deactivation without handoff**: `[drop: skill-name | "completed"]`

## Migration Strategy

### Phase 1: Documentation (Current)

- Add v2 examples to `CLAUDE-template.md` and `AGENTS-template.md`
- Document v2 in skill authoring best practices
- Update maintainer guides to reference both forms

### Phase 2: Test Support

- Ensure `maintainer/scripts/eval/run_skill_trigger_collaboration_test.py` accepts v2 blocks
- Add v2 parsing to any governance validation scripts

### Phase 3: Adoption

- Migrate skill SKILL.md examples to v2 where appropriate
- Prefer v2 in generated governance examples
- Keep v1 as reference in protocol definition sections

## Examples

### Full Task Sequence (v2)

```
[task-validation: PASS | clarity:✓ scope:✓ safety:✓ skill_match:✓ | action:proceed]

[triggers: scoped-tasking bugfix-workflow]

[precheck: scoped-tasking | PASS]
[output: scoped-tasking | completed high | boundary:"auth module" files:3 | next:bugfix-workflow]
[validate: scoped-tasking | PASS]
[drop: scoped-tasking | "boundary confirmed" | active: bugfix-workflow]

[precheck: bugfix-workflow | PASS]
[output: bugfix-workflow | completed high | root_cause:"session timeout" fix:"session.py:42" | next:minimal-change-strategy]
[validate: bugfix-workflow | PASS]
[drop: bugfix-workflow | "root cause found" | active: minimal-change-strategy]

[precheck: minimal-change-strategy | PASS]
[output: minimal-change-strategy | completed high | changed:1 lines:3 | next:self-review]
[validate: minimal-change-strategy | PASS]
[drop: minimal-change-strategy | "patch minimal" | active: self-review]
```

### Mixed v1/v2 (Allowed)

Agents can mix v1 and v2 in the same session:

```
[task-input-validation]
task: "Complex multi-module refactor with unclear scope"
checks:
  clarity:
    status: WARN
    reason: "Refactor target identified but scope spans 3 modules without clear boundaries"
  scope:
    status: WARN
    reason: "Initial request mentions 'improve error handling' but doesn't specify which modules"
  safety:
    status: PASS
    reason: "No destructive operations requested"
  skill_match:
    status: PASS
    reason: "scoped-tasking can narrow this"
result: WARN
action: ask_clarification
[/task-input-validation]

[triggers: scoped-tasking | defer: safe-refactor design-before-plan]

[precheck: scoped-tasking | PASS]

[skill-output: scoped-tasking]
status: partial
confidence: medium
outputs:
  narrowed_scope: "Error handling in auth and user modules only"
  excluded: "Payment module uses different error framework"
  files: ["auth/errors.py", "user/validation.py", "tests/test_auth_errors.py"]
signals:
  boundary_confidence: medium
  user_confirmation_needed: true
recommendations:
  next_skill: design-before-plan
  clarify: "Should payment module error handling be included?"
[/skill-output]

[validate: scoped-tasking | PASS]
[drop: scoped-tasking | "boundary narrowed pending confirmation" | active: design-before-plan]
```

## Governance Template Integration

### Current v1 Reference (Keep)

The "Skill Protocol v1" section in governance templates should remain as the canonical reference with full YAML examples.

### Add v2 Note

Add a subsection after "Minimum Block Shape":

```markdown
### Protocol v2 (Compact)

For simple cases, use compact inline format:

- `[task-validation: PASS | clarity:✓ scope:✓ safety:✓ skill_match:✓ | action:proceed]`
- `[triggers: scoped-tasking plan-before-action]`
- `[precheck: skill-name | PASS]`
- `[output: skill-name | completed high | <key outputs> | next:next-skill]`
- `[validate: skill-name | PASS]`
- `[drop: skill-name | "reason" | active: remaining skills]`

See `docs/maintainer/protocol-v2-compact.md` for complete specification.
```

## Validation

### Smoke Test

After updating templates:

```bash
python3 maintainer/scripts/install/run_manage_governance_smoke.py
```

### Test Governance Generation

```bash
python3 maintainer/scripts/install/manage-governance.py \
  --project /tmp/test-gov-v2 \
  --mode both
```

Verify:
- Generated `CLAUDE.md` includes v2 note
- Generated `AGENTS.md` includes v2 note
- File structure intact
- No syntax errors

## Readability Trade-offs

### Gains

- **30-50% shorter** protocol blocks in simple cases
- **Faster scanning** when reviewing execution traces
- **Lower token cost** in governance templates and examples

### Costs

- **Learning curve**: New syntax to learn
- **Reduced explicitness**: Harder to understand for newcomers
- **Tooling dependency**: Parsing logic must support both forms

### Mitigation

- Keep v1 as reference documentation standard
- Use v2 primarily in examples and execution traces
- Provide side-by-side v1/v2 examples in docs
- Keep migration gradual and reversible

## Future Extensions

### Potential v3 (Beyond Current Scope)

- Symbol-only ultra-compact form: `[✓task | ✓triggers:st bf]`
- JSON-line format for machine parsing: `{"block":"task-validation","result":"PASS"}`
- Diff-style incremental updates: `[output:+ confidence:high | root_cause:"..."]`

These are noted for awareness but are **not** part of the current v2 specification.
