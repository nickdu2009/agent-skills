---
name: phase-execute
description: Execute an accepted phase wave by consuming plan.yaml, resolving wave gates, launching serial or parallel lanes, integrating results, and reporting wave status. Use when phase-plan has produced the execution docs, the accepted wave is ready to execute, and the agent needs to implement a specific wave through schema-driven execution.
---

# Phase Execute

Execute the phase from the schema, not from memory and not from legacy planning prose.

The accepted execution doc set is:

- `$PHASE_DOCS_ROOT/phaseN/execution-index.md`
- `$PHASE_DOCS_ROOT/phaseN/plan.yaml`
- `$PHASE_DOCS_ROOT/phaseN/wave-guide.md`
- `$PHASE_DOCS_ROOT/phaseN/roadmap.md`

Unless the user or environment says otherwise, treat `PHASE_DOCS_ROOT` as the phase-doc root and default it to `docs/phases`.

`$PHASE_DOCS_ROOT/README.md` is a required phase-root summary file. It is for navigation and cross-phase summaries only; execution still consumes the accepted four-file set inside `phaseN/`.

If a phase status change must be written back to repository docs after execution, do that only as an explicit follow-up document maintenance step. Keep `plan.yaml` authoritative and keep `$PHASE_DOCS_ROOT/README.md` aligned with it.

Do not require or recreate:

- `phaseN-pr-delivery-plan.md`
- `phaseN-pr-parallelization-plan.md`
- `phaseN-waveX-kickoff-board.md`
- `phaseN-waveX-agent-launch-prompts.md`
- any extra `phaseN-*` planning doc

If execution depends on any of those legacy artifacts, stop and return to `$phase-plan`.

## Skill Assets

Resolve bundled assets relative to the directory that contains `SKILL.md`.

- `references/...` are read-only operating rules for this skill
- `../phase-contract-tools/references/...` are the shared contract references
- `../phase-contract-tools/scripts/...` are the shared contract helpers
- this skill does **not** ship a local `scripts/` directory; all contract helpers live under `../phase-contract-tools/scripts/` when both skills are installed side by side
- do not assume these files exist in the target repository
- when invoking a helper script, pass target-repository paths explicitly
- repository execution authority always comes from the accepted phase docs, not from the skill bundle

If this SKILL.md and a bundled reference document disagree on a rule, this SKILL.md wins.
References elaborate and provide examples; they do not override top-level skill rules.

Read these references when needed:

- [references/wave-execution-patterns.md](references/wave-execution-patterns.md) for the default execution flow
- [references/integrator-decision-rules.md](references/integrator-decision-rules.md) for integrator authority and merge rules
- [references/llm-following-performance.md](references/llm-following-performance.md) for hard execution-discipline rules
- [references/rollback-and-conflict-procedure.md](references/rollback-and-conflict-procedure.md) for ordered rollback and conflict handling
- [references/escalation-payload.schema.json](references/escalation-payload.schema.json) for machine validation of escalation payloads
- [`../phase-contract-tools/references/contract-authority-and-migration.md`](../phase-contract-tools/references/contract-authority-and-migration.md) for sole contract ownership, cutover rules, and core-only entrypoints
- [`../phase-contract-tools/references/external-contract-authority.md`](../phase-contract-tools/references/external-contract-authority.md) for external contract authority, owned subset, excluded subset, and accepted gap rules
- [`../phase-contract-tools/references/contract-alignment-checklist.md`](../phase-contract-tools/references/contract-alignment-checklist.md) for execution checks that keep contract-bound work aligned
- [`../phase-contract-tools/references/schema-consumption-rules.md`](../phase-contract-tools/references/schema-consumption-rules.md) for consuming structured phase fields
- [`../phase-contract-tools/references/wave-state-model.md`](../phase-contract-tools/references/wave-state-model.md) for allowed wave states and transition rules
- [`../phase-contract-tools/references/wave-status-snapshot.schema.md`](../phase-contract-tools/references/wave-status-snapshot.schema.md) for the canonical wave status output shape
- [`../phase-contract-tools/references/handoff-manifest.schema.md`](../phase-contract-tools/references/handoff-manifest.schema.md) for immutable handoff manifest rules

Use these shared contract scripts:

- `uv run ../phase-contract-tools/scripts/preflight_phase_execution.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --phase-root /path/to/repo/docs/phases --phase phaseN --wave 1`
- `uv run ../phase-contract-tools/scripts/list_wave_lanes.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --wave 1 --json`
- `uv run ../phase-contract-tools/scripts/render_lane_handoff.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --wave 1 --lane backend`
- `uv run ../phase-contract-tools/scripts/verify_lane_handoff.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --handoff /tmp/wave1-backend.md --strict`
- `uv run ../phase-contract-tools/scripts/render_wave_status_snapshot.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --wave 1`
- `uv run ../phase-contract-tools/scripts/validate_handoff_manifest.py --handoff /tmp/wave1-backend.md` (validate a handoff manifest before trusting lane output)
- `uv run ../phase-contract-tools/scripts/validate_wave_status_snapshot.py --snapshot /tmp/wave1-status.yaml` (validate a status snapshot before reporting wave state)

## Core Principles

1. `plan.yaml` is the execution authority.
2. State lives in the environment, not in the conversation.
3. The primary agent is the integrator unless the wave is strictly serial.
4. Lane instructions must be passed to subagents unchanged.
5. Parallel lanes must be isolated by branch or worktree.
6. Validation is bounded; retries are not open-ended.
7. Integration evidence is diff plus validation, not subagent narrative.
8. Do not mutate the phase model while claiming to execute it.

## Required Inputs

Before executing a wave, you must know:

- which phase is being executed
- which wave is being executed; ask the user to confirm the wave id only when the current message does not name it and repository state does not make the active wave unambiguous
- whether the user authorized parallel or subagent execution

If any of these are unclear, ask before launching work.

## Quickstart

Use this first-action sequence before touching implementation:

1. resolve and, if needed, confirm the phase id, wave id, and whether parallel execution is authorized
2. from the directory that contains this `SKILL.md`, run preflight via the sibling contract bundle:
   `uv run ../phase-contract-tools/scripts/preflight_phase_execution.py --plan /path/to/repo/docs/phases/phaseN/plan.yaml --phase-root /path/to/repo/docs/phases --phase phaseN --wave <wave_id>`
3. read `execution-index`, then `plan.yaml`, then `wave-guide`, then `roadmap`
4. resolve any `required_contracts`, owned subset boundaries, and blocking versus accepted contract gaps for the selected wave
5. emit one preflight status line that states the resolved wave, `control_pr`, serial versus parallel decision, and contract readiness
6. only then build the execution cursor and launch or implement work

If the wave can be resolved unambiguously from the current message and repository state, do not ask the user to restate it. State the resolved wave in the preflight status line instead.

If the helper is unavailable or cannot run because of an environment problem, use the manual checklist in `Before Execution`.
When using the manual checklist, do not reinterpret schema semantics or invent substitute rules.
Explicitly state that manual preflight fallback was used and why.

If the phase is a resume, rebuild state from the repository before trusting any earlier status message.

## Read The Execution Docs In Order

Read phase documents in this order:

1. `execution-index.md`
2. `plan.yaml`
3. `wave-guide.md`
4. `roadmap.md`

Authority order for execution fields:

1. `plan.yaml`
2. `execution-index.md`
3. `wave-guide.md`
4. `roadmap.md`

If Markdown disagrees with YAML on execution fields, YAML wins.

## Before Execution

Build an execution cursor from objective state before acting.

Always check:

- current phase doc set exists and matches the accepted four-file model
- `$PHASE_DOCS_ROOT/README.md` exists, but does not override the execution authority
- requested wave id exists in `waves`
- `control_pr`, `prs`, `merge_order`, and `lane_setup` are present for the wave
- required external contracts are declared for any contract-bound PRs in the wave
- blocking contract gaps are not being mistaken for completion state
- current git and file state for any already-completed or in-flight work
- whether wave entry gates are already satisfied

Map each planned PR or lane to observed state:

- `not_started`
- `in_progress`
- `completed`
- `blocked`

Do not infer progress from prior chat messages alone.

## Shared Contract Consumption

Consume structured execution fields through the shared contract references:

- `../phase-contract-tools/references/contract-authority-and-migration.md`
- `../phase-contract-tools/references/external-contract-authority.md`
- `../phase-contract-tools/references/contract-alignment-checklist.md`
- `../phase-contract-tools/references/schema-consumption-rules.md`
- `../phase-contract-tools/references/handoff-manifest.schema.md`

Do not reinterpret those contract rules locally.

Manual preflight fallback is an execution transport fallback, not a contract fallback.
All semantics still come from `plan.yaml` and the shared contract references.

Do not call any non-core contract helper path during execution.

## Reference Loading By Task

When starting a wave (cold start or resume):
- read: wave-execution-patterns.md, external-contract-authority.md, schema-consumption-rules.md, contract-alignment-checklist.md
- run: `uv run ../phase-contract-tools/scripts/preflight_phase_execution.py` with the same `--plan`, `--phase-root`, `--phase`, and `--wave` arguments as in Quickstart (if unavailable, use the manual checklist in Before Execution)

When launching parallel lanes:
- read: integrator-decision-rules.md, llm-following-performance.md, handoff-manifest.schema.md
- run: `uv run ../phase-contract-tools/scripts/list_wave_lanes.py` and `uv run ../phase-contract-tools/scripts/render_lane_handoff.py` with `--plan`, `--wave`, and `--lane` as in **Use these shared contract scripts**

When handling failures:
- read: rollback-and-conflict-procedure.md, wave-state-model.md, escalation-payload.schema.json

When reporting wave status:
- read: wave-status-snapshot.schema.md
- run: `uv run ../phase-contract-tools/scripts/render_wave_status_snapshot.py` with `--plan` and `--wave` as in **Use these shared contract scripts**

Do not load all references at once. Load only the set that matches the current task.

## Serial Vs Parallel Decision

Use serial execution when any of these are true:

- the wave has one active lane
- the requested scope is one PR
- hotspot ownership is not explicit enough for safe parallelism
- the user did not authorize subagents or parallel work

Use parallel execution only when all of these are true:

- the user explicitly authorized multi-agent or parallel execution
- the wave already defines disjoint lanes or PRs with clear ownership
- hotspot serialization rules are explicit
- each lane has a satisfied or independently satisfiable `start_condition`
- each lane can validate independently before seam integration

If the split is unclear, stop and return to `$phase-plan` instead of improvising.

## Launch Rules

When parallel execution is authorized:

- use the platform delegation tool explicitly
- launch each lane with isolated git state
- keep the integrator out of overlapping paths while workers run
- pass the lane instruction block unchanged from the canonical source
- prefer a rendered prompt when one exists; otherwise pass exact schema-derived instructions without paraphrase
- monitor workers through observable outputs, not indefinite waiting

When serial execution is chosen:

- keep work within the single active lane
- respect `scope.allow`, `scope.deny`, `files`, and `non_goals`
- validate the lane before claiming merge readiness

## Immutable Instruction Handoff

Subagent instructions are a contract, not a summary.

- if a renderer exists, pass its output verbatim
- if working directly from YAML, preserve field order and wording from the schema-derived instruction block
- do not rewrite scope, guardrails, validation, or done checks into prose
- do not add hidden assumptions not present in the accepted phase docs

## Integrator Rules

The integrator owns:

- wave selection
- gate resolution
- lane launch decisions
- hotspot ownership enforcement
- merge order enforcement
- seam validation
- final wave state decision

The integrator must review lanes as black-box outputs:

- original lane instruction
- `git diff <base>...<lane>`
- planned validation evidence

Do not treat a subagent's narrative as proof of correctness.

## Validation Rules

Use the narrowest meaningful validation that satisfies the accepted plan.

- run lane validation before merge
- run seam validation after integration when multiple lanes interact
- do not invent a lower validation floor than the docs promised
- do not silently widen scope by running unrelated repository-wide work unless the phase explicitly requires it

If the repository includes phase validators or prompt renderers through `$phase-contract-tools`, use them before launch or during repair rather than inventing new execution artifacts.

## Retry Budget And Circuit Breaker

Each active lane has a hard retry budget.

- default maximum is 3 validation-fix attempts per lane unless the user says otherwise
- on budget exhaustion, stop the lane
- preserve the failing state
- report the exact blocker to the integrator

Trigger the circuit breaker when:

- parallel lanes collide in the same hotspot
- merge conflicts require non-trivial semantic resolution
- validation failures cascade across lanes and the next safe action is unclear

When the circuit breaker trips, follow [references/rollback-and-conflict-procedure.md](references/rollback-and-conflict-procedure.md). Stop, preserve evidence, and report the exact blocker. Do not guess.

## Wave State Model

Use the shared state vocabulary from `../phase-contract-tools/references/wave-state-model.md`:

- `blocked`
- `active`
- `merge_ready`
- `next_wave_ready`

Do not invent additional state labels unless the user explicitly asks for a different model.

## Guardrails

- never reopen planning while pretending to execute
- never create replacement planning docs for convenience
- never launch a lane whose `start_condition` is unsatisfied
- never let two active lanes own the same hotspot family without explicit serialization
- never paraphrase a schema-derived lane contract before delegation
- never rely on memory for resumability
- never call a wave complete without checking `done_when` and planned validation
- never call a wave contract-complete when `contract_done_when` is unmet or a blocking contract gap remains
- never use fail-closed or adapter-unavailable behavior as proof of contract completion
- never deviate from the sole shared contract files in `../phase-contract-tools`
- never rewrite `$PHASE_DOCS_ROOT/README.md` opportunistically during execution; if the user explicitly wants a status write-back, update `plan.yaml` and the root README together in a controlled follow-up step

## Output Contract

Return:

- a wave status snapshot that follows [`../phase-contract-tools/references/wave-status-snapshot.schema.md`](../phase-contract-tools/references/wave-status-snapshot.schema.md)
- the resolved wave id and execution mode
- contract checks completed, blocking contract gaps, accepted contract gaps, and current contract status
- current lane states and blockers
- what was launched or implemented
- validation completed versus still pending
- the resulting wave state
- whether execution may proceed, must wait, or must return to planning

## Composition

Use this skill together with:

- `$phase-contract-tools` for the sole schema, renderer, handoff, snapshot, and validation contract
- `$phase-plan-review` when the user wants a pre-execution quality gate before the first wave launch
- `$phase-plan` when the phase doc set must be repaired, re-rendered, or re-scoped
- `$conflict-resolution` when merge or evidence conflicts exceed the circuit-breaker threshold

# Common Anti-Patterns

- **Executing from memory instead of schema.** The agent remembers lane instructions from an earlier planning conversation and starts implementation without re-reading `plan.yaml`. When the plan was updated after that conversation, the agent implements stale instructions, producing work that violates current scope and validation rules.
- **Mutating the plan during execution.** The agent discovers that the wave split is awkward and rewrites `plan.yaml` fields to fix it mid-execution. This breaks the execution authority contract and leaves the plan out of sync with the accepted review baseline, making rollback and status reporting unreliable.

See skill-anti-pattern-template.md for format guidelines.

## Artifact Contract

### Preconditions

- An accepted phase doc set already exists.
- The phase id, wave id, and parallel authorization state are all resolved.
- Preflight has run, or a manual fallback has been declared explicitly.

### Execution Outputs

- `status: completed` includes `wave_status`, `lane_results`, `gate_outcomes`, and `rollback_state`.
- The execution report names the resolved wave, execution mode, current lane states, validation state, and resulting wave state.
- Status output follows the shared wave-status vocabulary rather than ad hoc labels.

### Invariants

- `plan.yaml` remains the execution authority during the entire wave.
- Lane instructions are passed unchanged from the schema-derived source.
- Execution does not reopen planning while claiming to implement an accepted wave.

## Gate Contract

- Wave execution may start only when the selected wave exists and its `start_condition` gates are satisfied.
- Blocking contract gaps or preflight failures stop execution immediately.
- A wave can advance only after required lane validation and seam validation are satisfied according to the plan.

## Failure Handling

### Common Failure Causes

- A wave gate is unsatisfied.
- Parallel lanes collide in the same hotspot or trigger the circuit breaker.
- Validation retries are exhausted for a lane.

### Retry Policy

- Default maximum is 3 validation-fix attempts per active lane.
- On retry exhaustion, preserve the failing state and report the blocker instead of guessing.

### Fallback

- Return to `phase-plan` when the doc set or wave split is no longer executable as written.
- Use `conflict-resolution` for non-trivial merge or evidence conflicts.
- Use `phase-contract-tools` helpers for preflight, handoff, and status validation instead of inventing substitutes.

## Output Example

### V1 Format (verbose)

```yaml
[skill-output: phase-execute]
status: completed
confidence: high
outputs:
  wave_status: "wave1 completed successfully"
  lane_results:
    - "lane1 (schema): PRs merged, tests passed"
    - "lane2 (migration): data migration complete, validators passed"
  gate_outcomes:
    - "pre-wave gate: satisfied"
    - "post-wave gate: satisfied"
  rollback_state: "clean (no rollback needed)"
signals:
  next_wave_ready: true
recommendations:
  next_step: "proceed to wave2"
[/skill-output]
```

### V2 Format (compact)

```
[output: phase-execute | completed high | wave_status:"wave1 completed successfully" lane_results:"lane1 (schema): PRs merged, tests passed; lane2 (migration): data migration complete, validators passed" gate_outcomes:"pre-wave gate: satisfied, post-wave gate: satisfied" rollback_state:"clean (no rollback needed)" | next:wave2]
```

## Lifecycle

- Activate when a specific accepted wave is ready to execute.
- Deactivate when the wave reaches a terminal reported state or is blocked pending plan repair.
- Deactivate if the task shifts back into review or planning rather than execution.
