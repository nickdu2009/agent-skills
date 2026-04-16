# Governance Template Evaluation

Validate governance templates (CLAUDE-template.md / AGENTS-template.md) for content self-consistency and behavioral correctness.

## Problem

Governance templates are consumed by AI agents (Claude Code, Cursor Agent), not by humans or parsers. Existing evaluation infrastructure validates SKILL.md structure (`skill_protocol_v1.py`) and protocol block syntax (`skill_protocol_v2.py`), but nothing validates the governance template itself — the document that ties skills together into a coherent system.

Content issues in the template (orphaned skills, undefined semantics, circular logic) silently degrade agent behavior without surfacing as errors.

## Execution Environment

Both checks run directly in the agent CLIs that consume the governance templates:

| Capability | Claude Code CLI | Cursor Agent CLI |
|------------|----------------|-----------------|
| Non-interactive | `claude -p "prompt"` | `cursor agent -p "prompt"` |
| JSON output | `--output-format json` | `--output-format json` |
| Read-only mode | `--permission-mode plan` | `--mode plan` |
| Workspace | defaults to cwd | `--workspace <path>` |
| Trust | implied in `-p` | `--trust` |
| Model override | `--model sonnet` | `--model sonnet-4` |

No Python validation script. The evaluation tests whether agents can **interpret and act on** the governance rules, not whether the markdown parses correctly.

## Test Isolation

### Problem

Both CLIs auto-load governance files from the workspace at startup:

- Claude Code reads `CLAUDE.md` from cwd and parent directories
- Cursor Agent reads `.cursorrules`, `AGENTS.md`, `.cursor/rules/` from workspace

Running evaluations inside the project workspace means the agent sees **both** the project's real `CLAUDE.md` **and** the template being tested. Two sets of governance rules stack, contaminating the result. Additionally, the agent may read `skills/` directory contents, gaining knowledge that a real template consumer would not have.

### Isolation Dimensions

| Dimension | Risk | Mitigation |
|-----------|------|------------|
| **Governance file stacking** | Project CLAUDE.md + tested template both active | Isolated workspace contains only the tested template |
| **Skill file leakage** | Agent reads skills/ for extra knowledge | Isolated workspace has no skills/ directory |
| **Session bleed** | Prior test case context leaks into next | `-p` mode is stateless per invocation — already isolated |
| **Cross-CLI interference** | Claude and Cursor share state | Sequential execution, no shared files — already isolated |
| **Git context** | Agent reads git log/blame for extra context | Isolated workspace has a fresh empty git repo |

### Isolated Workspace Setup

Before each evaluation run, create a temporary workspace containing **only** the governance file under test, with no other project files:

```bash
setup_isolated_workspace() {
  local template="$1"        # e.g. templates/governance/CLAUDE-template.md
  local target_name="$2"     # CLAUDE.md or AGENTS.md
  local ws
  ws=$(mktemp -d)

  # Deploy only the tested template as the governance file
  cp "$template" "$ws/$target_name"

  # Minimal git repo (some CLI behaviors depend on git context)
  git -C "$ws" init -q
  git -C "$ws" add .
  git -C "$ws" commit -q -m "init" --allow-empty

  echo "$ws"
}

teardown_isolated_workspace() {
  local ws="$1"
  [ -d "$ws" ] && rm -rf "$ws"
}
```

Usage per CLI:

```bash
# For Claude Code evaluation
WS=$(setup_isolated_workspace "templates/governance/CLAUDE-template.md" "CLAUDE.md")
(cd "$WS" && claude -p "$prompt" --output-format json --permission-mode plan)
teardown_isolated_workspace "$WS"

# For Cursor Agent evaluation
WS=$(setup_isolated_workspace "templates/governance/AGENTS-template.md" "AGENTS.md")
cursor agent -p "$prompt" --trust --workspace "$WS" --output-format json --mode plan
teardown_isolated_workspace "$WS"
```

### What the Agent Sees

Inside the isolated workspace:

```
$TMPDIR/governance_eval_XXXXX/
├── .git/                  # empty repo
└── CLAUDE.md              # (or AGENTS.md) — the only file
```

No `skills/`, no `templates/`, no `maintainer/`. The agent can only answer based on the governance template's own content — exactly what the test cases require.

### Prompt Implications

Because the template is deployed as the workspace's governance file (not at its original path), test case prompts must **not** reference the original template path (e.g. `templates/governance/AGENTS-template.md`). Instead, prompts use a `{{GOVERNANCE_FILE}}` placeholder:

```yaml
prompt: |
  Read {{GOVERNANCE_FILE}}.
  In the "Skill Family Concurrency Budgets" section, ...
```

The driver script replaces `{{GOVERNANCE_FILE}}` with the deployed filename before execution:

| CLI | Template Source | Deployed As | `{{GOVERNANCE_FILE}}` → |
|-----|----------------|-------------|------------------------|
| Claude Code | `CLAUDE-template.md` | `$WS/CLAUDE.md` | `CLAUDE.md` |
| Cursor Agent | `AGENTS-template.md` | `$WS/AGENTS.md` | `AGENTS.md` |

The agent then reads its own governance file — exactly the same path it would use in a real project.

## File Layout

```
governance_eval/
├── cases.yaml           # 8 test cases (prompt + judge expression)
├── run_eval.sh           # Driver: iterate cases × CLIs × runs
└── judge.jq              # Shared jq judge expressions (optional)
```

## Test Cases

### Overview

8 checks, mapped to 8 known content issues:

| # | ID | Category | What It Validates | Current Expected |
|---|-----|----------|-------------------|-----------------|
| 1 | `family_mapping` | static | Concurrency budget families have skill membership lists | FAIL |
| 2 | `activation_coverage` | static | Every referenced skill has at least one entry path | FAIL |
| 3 | `chain_consistency` | static | Flow Pattern transitions appear in Handoff/Fallback tables | FAIL |
| 4 | `protocol_semantics` | behavioral | Every Protocol v2 block type has description, example, fail-handling | FAIL |
| 5 | `lifecycle_coverage` | static | Activated skills have matching lifecycle drop rules | PASS |
| 6 | `delegation_bounds` | behavioral | Delegation rules cover >4 subagent edge case | FAIL |
| 7 | `fastpath_testability` | behavioral | Fast-path criteria are decidable without task-validation | FAIL |
| 8 | `max_skills_operability` | behavioral | "Max 4" constraint links to lifecycle drop timing and defines "justification" | FAIL |

**`expect_current`**: Each case records its expected result against the current (unfixed) template. This calibrates the evaluation itself — if a known FAIL isn't caught, the test case prompt needs revision, not the template.

### Case Definitions

#### 1. `family_mapping` — Concurrency Budget Enforceability

**Rule:** Every skill family in "Skill Family Concurrency Budgets" must have a visible mapping of which skills belong to it.

```yaml
id: family_mapping
category: static
prompt: |
  Read the file {{GOVERNANCE_FILE}}.
  In the "Skill Family Concurrency Budgets" section, three families
  are referenced: Execution, Orchestration, Primary Phase.
  Based ONLY on this file's content, list which specific skills
  are mapped to each family.
  Respond in JSON only:
  {"families": {"Execution": [...], "Orchestration": [...], "Primary Phase": [...]}}
  If a family has no skills listed, use an empty array.
judge: '.families | to_entries | all(.value | length > 0)'
expect_current: fail
```

**Why it matters:** An agent that sees "Execution: max 4" but doesn't know which skills are Execution cannot enforce the budget.

#### 2. `activation_coverage` — Entry Path Completeness

**Rule:** Every skill referenced anywhere in the template must have at least one activation path: task-type activation, escalation trigger, or chain target (Forward Handoff/Fallback "To" column).

```yaml
id: activation_coverage
category: static
prompt: |
  Read {{GOVERNANCE_FILE}}.
  1. Collect every skill name (in backticks) referenced anywhere in the file.
  2. Collect every skill that has an explicit activation path:
     task-type activation, escalation trigger, Forward Handoff "To" column,
     or Fallback "To" column.
  3. Return skills that appear in (1) but not in (2).
  Respond in JSON only:
  {"all_skills": [...], "activated": [...], "orphaned": [...]}
judge: '.orphaned | length == 0'
expect_current: fail
```

**Why it matters:** Orphaned skills (like `multi-agent-protocol`) exist in the governance system but have no defined way to enter it.

#### 3. `chain_consistency` — Flow vs. Table Alignment

**Rule:** Every A→B transition in "Common Flow Patterns" must appear in the Forward Handoffs or Fallbacks tables, or be explicitly marked as self-evident.

```yaml
id: chain_consistency
category: static
prompt: |
  Read {{GOVERNANCE_FILE}}.
  1. Parse "Common Flow Patterns" — extract every A→B transition pair.
  2. Parse "Forward Handoffs" and "Fallbacks" tables — extract every From→To pair.
  3. Return transitions in (1) that do not appear in (2).
  Respond in JSON only:
  {"pattern_transitions": [...], "table_transitions": [...], "undocumented": [...]}
judge: '.undocumented | length == 0'
expect_current: fail
```

**Why it matters:** An agent following a Flow Pattern hits a transition not documented in the Handoff table and has no condition to evaluate — should it proceed or stop?

#### 4. `protocol_semantics` — Block Type Completeness

**Rule:** Every block type listed in Protocol v2's block sequence must have: (a) a semantic description, (b) at least one example, (c) defined behavior on FAIL.

```yaml
id: protocol_semantics
category: behavioral
prompt: |
  Read {{GOVERNANCE_FILE}}, "Skill Protocol v2" section.
  For each block type (task-validation, triggers, precheck, output,
  validate, drop, loop), answer based ONLY on what the file says:
  1. Does it have a semantic description? (true/false)
  2. Does it have at least one example? (true/false)
  3. Does it define what to do on FAIL? (true/false)
  Respond in JSON only:
  {"blocks": {"task-validation": {"description": true/false, "example": true/false, "fail_handling": true/false}, ...}}
judge: '[.blocks | to_entries[] | .value | to_entries[] | .value] | all'
expect_current: fail
```

**Why it matters:** An agent that encounters `[validate: skill | FAIL | ...]` has no guidance on what to do next — retry, escalate, or continue.

#### 5. `lifecycle_coverage` — Drop Rule Completeness

**Rule:** Every skill with an activation rule (task-type or escalation) must have a corresponding entry in Skill Lifecycle (drop condition or keep-active designation).

```yaml
id: lifecycle_coverage
category: static
prompt: |
  Read {{GOVERNANCE_FILE}}.
  1. Collect skills from "Skill Activation" (task-type list)
     and "Skill Escalation".
  2. Collect skills from "Skill Lifecycle" (drop rules + keep-active rules).
  3. Return skills in (1) not covered by (2).
  Respond in JSON only:
  {"activation_skills": [...], "lifecycle_skills": [...], "uncovered": [...]}
judge: '.uncovered | length == 0'
expect_current: pass
```

**Why it matters:** A skill without a drop rule stays active indefinitely, consuming concurrency budget.

#### 6. `delegation_bounds` — Edge Case Coverage

**Rule:** Tier 2 delegation rules must cover three scenarios: normal split (2–4), unsplittable (0), and overflow (>4).

```yaml
id: delegation_bounds
category: behavioral
prompt: |
  Read {{GOVERNANCE_FILE}}, "Multi-Agent Rules" section.
  A task requires splitting into 7 parallel subagents.
  Based ONLY on this file's rules, what should the agent do?
  Respond in JSON only:
  {"action": "description of what to do",
   "has_escalation_path": true/false,
   "rule_cited": "exact quote from the file, or null if no rule covers this"}
judge: '.has_escalation_path == true'
expect_current: fail
```

**Why it matters:** Without an overflow path, an agent facing a >4 split either violates the 2–4 rule or silently truncates parallelism.

#### 7. `fastpath_testability` — Bootstrap Independence

**Rule:** Fast-path criteria must be decidable without performing task-validation first.

```yaml
id: fastpath_testability
category: behavioral
prompt: |
  Read {{GOVERNANCE_FILE}}.
  The "Governance Fast-Path" section says to skip [task-validation]
  and [triggers] for certain tasks.
  Question: Can the agent determine whether a task qualifies for
  fast-path WITHOUT first performing the task-validation checks
  (clarity, scope, safety, skill_match)?
  Is there an explicit pre-screening mechanism defined in the file,
  or must the agent use its own judgment?
  Respond in JSON only:
  {"explicit_prescreening": true/false,
   "mechanism": "description or null",
   "bootstrap_problem": true/false}
judge: '.explicit_prescreening == true and .bootstrap_problem == false'
expect_current: fail
```

**Why it matters:** "Skip task-validation for simple tasks" requires assessing task complexity — which is what task-validation does. Circular dependency.

#### 8. `max_skills_operability` — Constraint Enforceability

**Rule:** "Max N active skills" must link to lifecycle drop timing and define "justification" criteria for exceptions.

```yaml
id: max_skills_operability
category: behavioral
prompt: |
  Read {{GOVERNANCE_FILE}}.
  The "Bug fix" flow pattern lists 6 skills in sequence.
  The "Skill Lifecycle" section says max 4 active skills
  without justification.
  Based ONLY on what the file says:
  1. Does it define WHEN to drop earlier skills in the bug fix chain
     so the active count stays ≤4?
  2. Does it define what constitutes valid "justification"
     for exceeding 4?
  Respond in JSON only:
  {"drop_timing_defined": true/false,
   "justification_criteria_defined": true/false,
   "max_concurrent_in_bugfix_chain": number or null}
judge: '.drop_timing_defined == true and .justification_criteria_defined == true'
expect_current: fail
```

**Why it matters:** Without explicit drop timing, the "max 4" constraint is either violated by normal flow patterns or becomes a dead rule that agents ignore.

## Driver Script Design

```bash
#!/bin/bash
# run_eval.sh — Run governance template evaluation on both CLIs

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CASES_FILE="$(dirname "$0")/cases.yaml"
RUNS=3

# --- Isolation ---

setup_isolated_workspace() {
  local template="$1"       # source template path
  local target_name="$2"    # CLAUDE.md or AGENTS.md
  local ws
  ws=$(mktemp -d)
  cp "$template" "$ws/$target_name"
  git -C "$ws" init -q
  git -C "$ws" add . && git -C "$ws" commit -q -m "init"
  echo "$ws"
}

teardown_isolated_workspace() {
  [ -d "$1" ] && rm -rf "$1"
}

# --- CLI definitions ---
# Each CLI entry: template_source | target_filename | run_command_template
#   {{WS}} is replaced with the isolated workspace path
#   {{PROMPT}} is replaced with the test prompt

declare -A CLI_TEMPLATE
CLI_TEMPLATE[claude]="templates/governance/CLAUDE-template.md|CLAUDE.md|cd {{WS}} && claude -p {{PROMPT}} --output-format json --permission-mode plan"
CLI_TEMPLATE[cursor]="templates/governance/AGENTS-template.md|AGENTS.md|cursor agent -p {{PROMPT}} --trust --workspace {{WS}} --output-format json --mode plan"

# --- Main loop ---

for cli_name in claude cursor; do
  echo "=== $cli_name ==="

  IFS='|' read -r tpl_source tpl_target cmd_template <<< "${CLI_TEMPLATE[$cli_name]}"

  # Create isolated workspace (one per CLI, reused across cases)
  WS=$(setup_isolated_workspace "$PROJECT_ROOT/$tpl_source" "$tpl_target")
  trap "teardown_isolated_workspace '$WS'" EXIT

  for case_id in $(yq -r '.[] | .id' "$CASES_FILE"); do
    raw_prompt=$(yq -r ".[] | select(.id == \"$case_id\") | .prompt" "$CASES_FILE")
    judge=$(yq -r ".[] | select(.id == \"$case_id\") | .judge" "$CASES_FILE")
    expected=$(yq -r ".[] | select(.id == \"$case_id\") | .expect_current" "$CASES_FILE")

    # Replace governance file placeholder
    prompt="${raw_prompt//\{\{GOVERNANCE_FILE\}\}/$tpl_target}"

    # Build CLI command
    run_cmd="${cmd_template//\{\{WS\}\}/$WS}"

    pass_count=0
    for run in $(seq 1 $RUNS); do
      final_cmd="${run_cmd//\{\{PROMPT\}\}/\"$prompt\"}"
      output=$(eval "$final_cmd" 2>/dev/null || true)

      # Extract text content from CLI JSON envelope, then judge
      content=$(echo "$output" | jq -r '.result // .content // .text // .' 2>/dev/null)
      echo "$content" | jq -e "$judge" >/dev/null 2>&1 && ((pass_count++))
    done

    # Majority vote
    [ $pass_count -ge 2 ] && verdict="PASS" || verdict="FAIL"

    # Calibration
    if [ "$verdict" = "$expected" ]; then
      cal="(calibrated)"
    else
      cal="(MISCALIBRATED: expected $expected)"
    fi

    printf "  %-25s %-4s %s\n" "$case_id" "$verdict" "$cal"
  done

  teardown_isolated_workspace "$WS"
  trap - EXIT
done
```

## Output Format

```
=== claude ===
  family_mapping            FAIL (calibrated)
  activation_coverage       FAIL (calibrated)
  chain_consistency         FAIL (calibrated)
  protocol_semantics        FAIL (calibrated)
  lifecycle_coverage        PASS (calibrated)
  delegation_bounds         FAIL (calibrated)
  fastpath_testability      FAIL (calibrated)
  max_skills_operability    FAIL (calibrated)

=== cursor ===
  family_mapping            FAIL (calibrated)
  ...

Result: 2 CLI × 8 cases = 16 verdicts
  claude:  1 pass, 7 fail (7 calibrated, 0 miscalibrated)
  cursor:  1 pass, 7 fail (7 calibrated, 0 miscalibrated)
```

**Calibration** means the actual result matches `expect_current`. A miscalibrated result means either:
- The test case prompt is poorly written (agent misunderstood the question), or
- The template was modified and `expect_current` is stale.

## Workflow

1. **Before fixing**: Run `run_eval.sh` → confirm 7 FAIL, 1 PASS, all calibrated.
2. **Fix template content**: Address the 7 failing issues.
3. **After fixing**: Run `run_eval.sh` → confirm 8 PASS. Update `expect_current` to `pass` for all.
4. **Ongoing**: Run on template changes to catch regressions.

## Dependencies

- `yq` (YAML parser) — `brew install yq`
- `jq` (JSON processor) — `brew install jq`
- `claude` CLI — installed and authenticated
- `cursor agent` CLI — installed and authenticated
