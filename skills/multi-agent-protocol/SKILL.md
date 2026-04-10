---
name: multi-agent-protocol
description: Skill that provides complete operational protocol for launching, coordinating, and synthesizing parallel subagents. Defines what parallelism is appropriate (Tier 1 read-only vs. Tier 2 write-capable), when to parallelize (decision framework), and how to execute (templates, merge checklist, failure handling).
metadata:
  version: "0.1.0"
  tags: "coding, agents, orchestration, efficiency"
---

# Multi-Agent Protocol

## 1. Decision Framework

Before spawning any subagent, answer the parallelism scorecard.
If 4+ answers are **yes**, parallelism is likely worthwhile.
If 2 or fewer are **yes**, stay serial.

| Question | yes / no |
|----------|----------|
| Can the task be split into independent units with clear contracts? | |
| Is there meaningful local work the primary agent can do while subagents run? | |
| Are the planned write scopes disjoint or read-only? | |
| Is merge cost lower than the likely time saved? | |
| Can the work fit within 2–4 agents? | |
| Can each agent finish without waiting on another agent's intermediate output? | |

### Choose the execution mode

- **Stay serial** for: tiny tasks, same-file fine-grained edits, tasks requiring one coherent reasoning chain, or strong sequential dependency.
- **Use tool-level parallelism** (parallel reads, searches, metadata fetches) when work is shallow and local — no subagent needed.
- **Use Tier 1 (Explore)** when multiple areas of the codebase need to be investigated in parallel, and no files will be edited.
- **Use Tier 2 (Delegate)** when 2+ substantive work items have independent deliverables, meaningful reasoning, and disjoint write scopes.

---

## 2. Tier 1 — Explore Protocol

### When it applies

Subagents only read code, search, or verify hypotheses. No files are created, edited, or deleted.

### Rules

- No pre-declaration required.
- Subagent count is unrestricted but must stay proportional to the question scope.
- Each subagent must receive a clear question or objective.
- The primary agent must synthesize all results into a single response.
- Conflicting findings must be explicitly called out, not silently dropped.

### Subagent prompt template

```text
Question: <clear question or objective>
Scope: <files, directories, or packages to focus on>
Exclude: <areas to skip>
Return format:
  - Findings: <what you discovered>
  - Evidence: <file paths, line ranges, symbol names>
  - Confidence: <high | medium | low> — <one-sentence reason>
```

### Synthesis rules

1. Deduplicate overlapping findings across subagents.
2. If two subagents report conflicting evidence, present both with their supporting evidence and label the disagreement.
3. If confidence is low across all subagents, state the uncertainty explicitly rather than guessing.
4. Use the `conflict-resolution` skill when disagreements are non-trivial. When doing so, map subagent output to its input format: `Findings` → `Claim`, infer `Source` from the subagent identity, carry `Evidence` and `Confidence` directly.

---

## 3. Tier 2 — Delegate Protocol

### When it applies

Any subagent may create, edit, or delete files, run mutating commands, or make decisions that affect module boundaries.

### Gate

Before launching, the agent must output a one-line declaration:

```
[delegate: <count> | split: <dimension> | risk: <low|medium|high>]
```

- **count**: 2–4. If the task needs more, decompose into sequential rounds of 2–4.
- **split**: the axis of decomposition (see Split Design below).
- **risk**: `low` = additive-only changes; `medium` = modifies existing code within one module; `high` = cross-module or public API changes.

If the task cannot be cleanly split, output:

```
[delegate: 0 | reason: <why>]
```

and remain serial.

### Split design

Good decomposition axes:

| Axis | Example |
|------|---------|
| Module | `pkg/tool` vs `pkg/runtime` vs `internal/eval` |
| Layer | API handler vs database vs client |
| Responsibility | implementation vs tests vs docs |
| Artifact type | backend vs frontend vs infrastructure |
| Hypothesis | competing root-cause candidates |

Bad splits:

- Multiple agents editing the same small file or function.
- A chain where one agent cannot start until another produces an exact intermediate result.
- Vague prompts such as "look around and help."
- More agents than independent work items.

### Subagent prompt template

```text
Objective: <one-sentence deliverable>

You are not alone in the codebase. Do not revert others' changes.

Scope: <files/directories you may read and edit>
Excluded: <files/directories you must NOT touch>
Edit permission: <read-only | additive | full>
Validation: <command or check to run before reporting done>

Return format:
  - Findings: <what you did or discovered>
  - Evidence: <files changed, diffs, or paths examined>
  - Uncertainty: <what you are not sure about>
  - Recommendation: <what the primary agent should do next>

If you need to touch excluded scope, STOP and report the conflict.
If validation fails after 3 attempts, commit WIP state and report the failure.
```

### Subagent behavior rules

- Stay within assigned scope and edit permission.
- Do not spawn additional subagents unless the prompt explicitly allows it.
- If validation fails after 3 retries, commit the current state (`git commit -m "WIP: <description>"`) and report the failure to the primary agent.
- If you discover a need to touch excluded scope, stop immediately and report the scope conflict.

### Primary agent behavior

- Do not duplicate work assigned to subagents.
- Continue meaningful local work while subagents run; do not idle.
- When results return: review evidence before conclusions, compare by evidence quality not confidence tone.
- Resolve conflicts using the `conflict-resolution` skill when needed.
- If a subagent reports a scope conflict or failure, resolve it before proceeding.
- The primary agent retains final decision authority and delivers the single final answer.

### Merge checklist

After all subagents complete:

1. Collect outputs in normalized format.
2. Confirm no write scopes overlapped unexpectedly.
3. Review evidence before accepting conclusions.
4. Integrate changes or findings centrally.
5. Run targeted validation at the integration seam.
6. Summarize residual risk.

---

## 4. Operational Rules

### State and resumability

State is in the environment, not in the prompt.

- Derive the execution cursor from the file system, `git log`, or structured schema files — never from conversation history alone.
- A new agent session must be able to resume from objective state if the previous session was interrupted.

### Isolation

- Tier 2 subagents must work in isolated Git branches or worktrees.
- The primary agent must not make overlapping edits while subagents are active.
- Merge (`git merge` or diff review) is the synchronization point.

### Context budget

- The primary agent treats subagent work as a black box: input prompt → final diff → validation result.
- Do not read subagent intermediate debugging steps or trial-and-error output.
- After a successful merge, compress state into a summary and discard implementation details.

### Failure boundaries

- Maximum 3 validation retries per subagent.
- On retry exhaustion: subagent commits WIP, reports failure, escalates to primary.
- On complex merge conflicts: primary pauses, outputs exact conflict files/errors, and escalates to the user or to the `conflict-resolution` skill.
- Do not attempt to blindly guess merge conflict resolutions.

---

## 5. Platform Mapping

These rules are platform-agnostic. The table below maps concepts to platform-specific mechanisms.

| Concept | Cursor | Codex | Claude Code |
|---------|--------|-------|-------------|
| Tier 1 launch | `Task(subagent_type="explore", readonly=true)` | delegation with read-only scope | parallel `tool_use` with read-only tools |
| Tier 2 launch | `Task(subagent_type="generalPurpose")` or `Task(subagent_type="best-of-n-runner")` | delegation with branch isolation | subprocess with edit tools |
| Branch isolation | `best-of-n-runner` provides worktree; otherwise manual `git checkout -b` | one branch per delegated agent | manual `git checkout -b` |
| Background execution | `run_in_background: true` | async delegation / `wait_agent` | background subprocess |
| Monitor progress | read terminal output file | poll branch status / `wait_agent` | poll subprocess output |
| Redirect running agent | resume Task with new prompt | `send_input` to existing agent | send follow-up to subprocess |

---

## 6. Guardrails

- Do not parallelize by default. Serial is the safe default.
- Do not delegate the single urgent blocking step if the primary agent will immediately need the result.
- Do not create overlapping edit scopes without an explicit collision-management plan.
- Do not recurse into more subagents unless explicitly allowed in the subagent's prompt.
- Do not let synthesis cost exceed the work that was parallelized.
- Do not use subagents to hide unclear thinking — if you cannot describe the subproblem cleanly, you are not ready to delegate it.
- Close or terminate subagents when they are no longer needed.

---

## 7. Exemptions

These tasks require no multi-agent declaration and no activation of this skill:

- Single-file edits or modifications scoped to one function.
- Direct answers to questions that require no codebase investigation.
- Running a single command (test, build, lint) and reporting the result.
- Commits, branch operations, or other git housekeeping.

---

## 8. Common Anti-Patterns

- **Parallelizing by default.** The agent launches 3 subagents for a task that requires one coherent reasoning chain across a single module. The merge cost exceeds the time saved, and the split introduces coordination confusion.
- **Overlapping write scopes.** Two subagents are assigned to edit the same file or the same function. Neither knows about the other's changes, and the merge produces silent logic errors or conflicts that the primary agent has to untangle.

## 9. Examples

### Explore example

**Task:** "How does user authentication work in this codebase?"

→ **Tier 1.** No declaration needed.

Launch 3 explore subagents:
- Subagent 1: "Where is the auth middleware defined and what does it check?" Scope: `pkg/auth/`, `internal/middleware/`
- Subagent 2: "How are sessions stored and invalidated?" Scope: `pkg/session/`, `pkg/store/`
- Subagent 3: "Where are user roles checked in the request path?" Scope: `pkg/policy/`, `internal/app/`

Each returns Findings / Evidence / Confidence. Primary synthesizes into one answer.

### Delegate example

**Task:** "Add tool registry to pkg/tool and update all consumers."

→ **Tier 2.**

```
[delegate: 3 | split: by module | risk: medium]
```

- Subagent 1: `pkg/tool/registry.go` + `registry_test.go`. Edit permission: additive. Validation: `go test ./pkg/tool/...`
- Subagent 2: `internal/tools/` refactor. Edit permission: full. Validation: `go test ./internal/tools/...`
- Subagent 3: `internal/eval/` refactor. Edit permission: full. Validation: `go test ./internal/eval/...`

Each returns Findings / Evidence / Uncertainty / Recommendation. Primary merges, runs integration test, delivers final answer.

### Serial example

**Task:** "Fix the off-by-one error in pkg/runtime/replay.go"

→ No declaration needed (single-file edit, exemption applies).

Or if asked explicitly:

```
[delegate: 0 | reason: single-file fix with sequential debugging]
```

---

## Composition

Part of parallel chain. See CLAUDE.md Skill Chain Triggers section.

Additional composition:
- Combine with `conflict-resolution` when subagent findings disagree or merge conflicts arise
- Combine with `plan-before-action` to design the overall decomposition plan before delegating
- Combine with `targeted-validation` to choose the cheapest meaningful validation after synthesis
- Combine with `context-budget-awareness` to compress multi-branch reasoning into a usable merged state

## Delegation Contract

### Preconditions

- The task can be split into 2-4 independent lanes with clear scope boundaries.
- Merge cost is lower than the expected time saved.
- Write scopes are disjoint, or the work is strictly read-only.

### Required Outputs

- `status: completed` includes `split_dimension`, `lanes`, and `integration_plan`.
- Each lane declares its objective, scope, exclusions, edit permission, and validation boundary.
- Tier 2 launches emit the required `[delegate: <count> | split: <dimension> | risk: <level>]` gate first.

### Invariants

- No overlapping write scopes without an explicit collision-management plan.
- The primary agent does not duplicate subagent work.
- Lane instructions are passed unchanged from the canonical source.

## Synthesis Contract

- Synthesis must collect each lane's findings and evidence before drawing conclusions.
- The final synthesis output includes `split_dimension`, `lanes`, `integration_plan`, and `synthesis`.
- Conflicting findings remain explicit until resolved; use `conflict-resolution` when disagreement is non-trivial.
- Integration validation runs at the seam after lane results are merged.

## Failure Handling

### Common Failure Causes

- The split axis is unclear, so lanes would overlap materially.
- A subagent needs excluded scope or exhausts its retry budget.
- Merge conflicts or shared hotspots break lane isolation.

### Retry Policy

- Allow up to 3 validation/fix retries per delegated lane.
- If a lane exhausts retries or hits a scope conflict, stop the lane and return control to the primary agent.

### Fallback

- Stay serial when the task cannot be split cleanly.
- Use `conflict-resolution` when returned findings disagree materially.
- Escalate to the user when merge conflicts require policy or product judgment.

### Low Confidence Handling

- Preserve uncertainty in the final synthesis instead of flattening it into a forced conclusion.
- Prefer a targeted adjudication step over a weak merge decision.

## Deactivation Trigger

- Deactivate once all lane outputs have been synthesized into a single conclusion.
- Deactivate when the task is reclassified as serial work.
- Deactivate after conflicts are handed off to `conflict-resolution` or the user for resolution.
