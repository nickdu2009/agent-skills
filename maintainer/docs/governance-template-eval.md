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
| Model override | `--model opus` | `--model claude-opus-4-6` |

No Python validation of markdown structure. The evaluation tests whether agents can **interpret and act on** the governance rules, not whether the markdown parses correctly. The driver script (`run_eval.py`) is written in Python for safety and robustness (subprocess isolation, proper JSON/YAML handling, cross-platform timeout), but all evaluation logic runs inside the agent CLIs.

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

```python
import shutil, subprocess, tempfile
from pathlib import Path

def setup_isolated_workspace(template: Path, target_name: str) -> Path:
    """Create a temp workspace with only the governance file under test."""
    ws = Path(tempfile.mkdtemp(prefix="governance_eval_"))
    shutil.copy2(template, ws / target_name)
    # Minimal git repo (some CLI behaviors depend on git context)
    subprocess.run(["git", "init", "-q"], cwd=ws, check=True)
    subprocess.run(["git", "add", "."], cwd=ws, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=ws, check=True)
    return ws

def teardown_isolated_workspace(ws: Path) -> None:
    if ws.is_dir():
        shutil.rmtree(ws, ignore_errors=True)
```

Usage per CLI:

```python
# For Claude Code evaluation
ws = setup_isolated_workspace(Path("templates/governance/CLAUDE-template.md"), "CLAUDE.md")
try:
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json",
         "--permission-mode", "plan", "--model", "opus"],
        cwd=ws, capture_output=True, text=True, timeout=120,
    )
finally:
    teardown_isolated_workspace(ws)

# For Cursor Agent evaluation
ws = setup_isolated_workspace(Path("templates/governance/AGENTS-template.md"), "AGENTS.md")
try:
    result = subprocess.run(
        ["cursor", "agent", "-p", prompt, "--trust", "--workspace", str(ws),
         "--output-format", "json", "--mode", "plan", "--model", "claude-opus-4-6"],
        capture_output=True, text=True, timeout=120,
    )
finally:
    teardown_isolated_workspace(ws)
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
maintainer/
└── governance_eval/
    ├── cases.yaml       # 8 test cases (prompt + judge expression)
    └── run_eval.py      # Driver: uv single-file script (deps inline)
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
     Fallback "To" column, or starting skill (first position) in a
     Common Flow Pattern.
  3. Return skills that appear in (1) but not in (2).
  Respond in JSON only:
  {"all_skills": [...], "activated": [...], "orphaned": [...]}
judge: '.orphaned | length == 0'
expect_current: fail
```

**Why it matters:** Orphaned skills (like `phase-contract-tools`, which only appears in concurrency budgets) exist in the governance system but have no defined way to enter it.

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
     Also include this synthetic test skill: `phantom-test-skill`.
  2. Collect skills from "Skill Lifecycle" (drop rules + keep-active rules).
  3. Return skills in (1) not covered by (2).
  Respond in JSON only:
  {"activation_skills": [...], "lifecycle_skills": [...], "uncovered": [...]}
judge: '.uncovered == ["phantom-test-skill"]'
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
  Question: Does the file define a formal, enumerated pre-screening
  mechanism (e.g. a checklist, decision tree, or classifier) that
  determines whether a task qualifies for fast-path BEFORE running
  the task-validation checks (clarity, scope, safety, skill_match)?
  "Use your own judgment" or "common sense" does NOT count as a
  formal mechanism.
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

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""run_eval.py — Run governance template evaluation on both CLIs.

Usage:
  uv run maintainer/governance_eval/run_eval.py
  uv run maintainer/governance_eval/run_eval.py --model sonnet   # cheaper, less accurate
  uv run maintainer/governance_eval/run_eval.py --runs 1         # fast smoke test
"""

import argparse, json, re, subprocess, shutil, tempfile, sys
from dataclasses import dataclass
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # maintainer/governance_eval/ → project root
CASES_FILE = Path(__file__).with_name("cases.yaml")
TIMEOUT = 120  # seconds per CLI invocation

assert (PROJECT_ROOT / "templates" / "governance").is_dir(), (
    f"PROJECT_ROOT miscalculated: {PROJECT_ROOT} — "
    "expected to find templates/governance/ at project root"
)

# --- Defaults ---
# Opus is used for highest accuracy; override with --model for cost savings.
# Cost note: full run = 2 CLIs × (4 static×3 + 4 behavioral×5) = 64 opus calls.
#   Use --model sonnet (or --runs 1) for cheaper iteration during development.
DEFAULT_MODELS = {"claude": "opus", "cursor": "claude-opus-4-6"}
DEFAULT_RUNS = {"static": 3, "behavioral": 5}

# Model name mapping: short name → per-CLI model identifier
MODEL_MAP = {
    "opus":   {"claude": "opus",   "cursor": "claude-opus-4-6"},
    "sonnet": {"claude": "sonnet", "cursor": "claude-sonnet-4-6"},
}


# --- CLI definitions ---

@dataclass
class CLIDef:
    name: str
    template_source: str   # relative to PROJECT_ROOT
    target_name: str       # deployed as (CLAUDE.md or AGENTS.md)
    model: str

    def build_cmd(self, prompt: str, workspace: Path) -> list[str]:
        raise NotImplementedError

class ClaudeCode(CLIDef):
    def build_cmd(self, prompt: str, workspace: Path) -> list[str]:
        return [
            "claude", "-p", prompt,
            "--output-format", "json",
            "--permission-mode", "plan",
            "--model", self.model,
        ]

class CursorAgent(CLIDef):
    def build_cmd(self, prompt: str, workspace: Path) -> list[str]:
        return [
            "cursor", "agent", "-p", prompt,
            "--trust", "--workspace", str(workspace),
            "--output-format", "json",
            "--mode", "plan",
            "--model", self.model,
        ]


def build_clis(model_override: str | None = None) -> list[CLIDef]:
    if model_override and model_override in MODEL_MAP:
        models = MODEL_MAP[model_override]
    else:
        models = DEFAULT_MODELS
    return [
        ClaudeCode("claude", "templates/governance/CLAUDE-template.md",
                   "CLAUDE.md", models["claude"]),
        CursorAgent("cursor", "templates/governance/AGENTS-template.md",
                    "AGENTS.md", models["cursor"]),
    ]


# --- Isolation ---

def setup_isolated_workspace(template: Path, target_name: str) -> Path:
    ws = Path(tempfile.mkdtemp(prefix="governance_eval_"))
    shutil.copy2(template, ws / target_name)
    subprocess.run(["git", "init", "-q"], cwd=ws, check=True)
    subprocess.run(["git", "add", "."], cwd=ws, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=ws, check=True)
    return ws


# --- Response extraction ---

def extract_response(raw: str) -> str:
    """Extract agent response text from CLI JSON envelope."""
    try:
        envelope = json.loads(raw)
        text = raw
        for key in ("result", "content", "text"):
            if key in envelope and envelope[key]:
                text = envelope[key]
                break
    except json.JSONDecodeError:
        text = raw
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text.strip())
    return text


def evaluate_judge(content: str, judge_expr: str) -> bool:
    """Run jq judge expression against agent response."""
    result = subprocess.run(
        ["jq", "-e", judge_expr],
        input=content, capture_output=True, text=True,
    )
    return result.returncode == 0


# --- Main ---

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Governance template evaluation")
    p.add_argument("--model", choices=list(MODEL_MAP), default=None,
                   help="Override model for both CLIs (default: opus)")
    p.add_argument("--runs", type=int, default=None,
                   help="Override run count for all cases (default: 3 static, 5 behavioral)")
    return p.parse_args()


def main():
    args = parse_args()
    cases = yaml.safe_load(CASES_FILE.read_text())
    clis = build_clis(args.model)

    results: dict[str, list[dict]] = {}

    for cli in clis:
        print(f"=== {cli.name} (model: {cli.model}) ===")
        cli_results = []

        template_path = PROJECT_ROOT / cli.template_source
        ws = setup_isolated_workspace(template_path, cli.target_name)

        try:
            for case in cases:
                case_id = case["id"]
                category = case.get("category", "static")
                runs = args.runs or DEFAULT_RUNS.get(category, 3)
                majority = (runs // 2) + 1
                judge_expr = case["judge"]
                expected = case["expect_current"]

                prompt = case["prompt"].replace(
                    "{{GOVERNANCE_FILE}}", cli.target_name
                )
                cmd = cli.build_cmd(prompt, ws)

                pass_count = 0
                for _ in range(runs):
                    try:
                        proc = subprocess.run(
                            cmd, cwd=ws,
                            capture_output=True, text=True,
                            timeout=TIMEOUT,
                        )
                        content = extract_response(proc.stdout)
                        if evaluate_judge(content, judge_expr):
                            pass_count += 1
                    except subprocess.TimeoutExpired:
                        pass  # counts as fail

                verdict = "PASS" if pass_count >= majority else "FAIL"
                calibrated = verdict.lower() == expected.lower()
                cal = ("(calibrated)" if calibrated
                       else f"(MISCALIBRATED: expected {expected})")

                print(f"  {case_id:<25} {verdict:<4} {cal}")
                cli_results.append({
                    "id": case_id, "verdict": verdict,
                    "calibrated": calibrated, "runs": runs,
                    "pass_count": pass_count,
                })
        finally:
            shutil.rmtree(ws, ignore_errors=True)

        results[cli.name] = cli_results

    # --- Summary ---
    print()
    for name, cli_results in results.items():
        p = sum(1 for r in cli_results if r["verdict"] == "PASS")
        f = sum(1 for r in cli_results if r["verdict"] == "FAIL")
        cal = sum(1 for r in cli_results if r["calibrated"])
        mis = len(cli_results) - cal
        print(f"  {name}: {p} pass, {f} fail "
              f"({cal} calibrated, {mis} miscalibrated)")

    sys.exit(0 if all(
        r["calibrated"] for v in results.values() for r in v
    ) else 1)

if __name__ == "__main__":
    main()
```

## Output Format

```
=== claude (model: opus) ===
  family_mapping            FAIL (calibrated)
  activation_coverage       FAIL (calibrated)
  chain_consistency         FAIL (calibrated)
  protocol_semantics        FAIL (calibrated)
  lifecycle_coverage        PASS (calibrated)
  delegation_bounds         FAIL (calibrated)
  fastpath_testability      FAIL (calibrated)
  max_skills_operability    FAIL (calibrated)

=== cursor (model: claude-opus-4-6) ===
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

1. **Before fixing**: Run `uv run maintainer/governance_eval/run_eval.py` → confirm 7 FAIL, 1 PASS, all calibrated.
2. **Fix template content**: Address the 7 failing issues.
3. **After fixing**: Run `uv run maintainer/governance_eval/run_eval.py` → confirm 8 PASS. Update `expect_current` to `pass` for all.
4. **Ongoing**: Run on template changes to catch regressions.

**Cost-saving options:**
- `--model sonnet` — use sonnet instead of opus (~5-10x cheaper, slightly less accurate on behavioral cases)
- `--runs 1` — single run per case, no majority vote (fast smoke test during development)

## Dependencies

- `uv` — `brew install uv` (manages Python and PyYAML automatically via inline script metadata)
- `jq` (JSON processor) — `brew install jq`
- `claude` CLI — installed and authenticated
- `cursor agent` CLI — installed and authenticated
