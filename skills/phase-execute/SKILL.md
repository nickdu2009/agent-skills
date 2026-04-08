---
name: phase-execute
description: Execute an accepted phase wave by consuming phaseN-plan.yaml, resolving wave gates, launching serial or parallel lanes, integrating results, and reporting wave status. Use after phase-plan has produced the execution docs and the agent is ready to implement a specific wave.
---

# Phase Execute

Execute the phase from the schema, not from memory and not from legacy planning prose.

The accepted execution doc set is:

- `docs/phaseN-execution-index.md`
- `docs/phaseN-plan.yaml`
- `docs/phaseN-wave-guide.md`
- `docs/phaseN-roadmap.md`

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

- `uv run ../phase-contract-tools/scripts/preflight_phase_execution.py --plan /path/to/docs/phaseN-plan.yaml --docs-dir /path/to/repo/docs --phase phaseN --wave 1`
- `uv run ../phase-contract-tools/scripts/list_wave_lanes.py --plan /path/to/docs/phaseN-plan.yaml --wave 1 --json`
- `uv run ../phase-contract-tools/scripts/render_lane_handoff.py --plan /path/to/docs/phaseN-plan.yaml --wave 1 --lane backend`
- `uv run ../phase-contract-tools/scripts/verify_lane_handoff.py --plan /path/to/docs/phaseN-plan.yaml --handoff /tmp/wave1-backend.md --strict`
- `uv run ../phase-contract-tools/scripts/render_wave_status_snapshot.py --plan /path/to/docs/phaseN-plan.yaml --wave 1`
- `uv run ../phase-contract-tools/scripts/validate_handoff_manifest.py --handoff /tmp/wave1-backend.md` (validate a handoff manifest before trusting lane output)
- `uv run ../phase-contract-tools/scripts/validate_wave_status_snapshot.py --snapshot /tmp/wave1-status.yaml` (validate a status snapshot before reporting wave state)

## Core Principles

1. `phaseN-plan.yaml` is the execution authority.
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
   `uv run ../phase-contract-tools/scripts/preflight_phase_execution.py --plan /path/to/docs/phaseN-plan.yaml --docs-dir /path/to/repo/docs --phase phaseN --wave <wave_id>`
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

1. `phaseN-execution-index.md`
2. `phaseN-plan.yaml`
3. `phaseN-wave-guide.md`
4. `phaseN-roadmap.md`

Authority order for execution fields:

1. `phaseN-plan.yaml`
2. `phaseN-execution-index.md`
3. `phaseN-wave-guide.md`
4. `phaseN-roadmap.md`

If Markdown disagrees with YAML on execution fields, YAML wins.

## Before Execution

Build an execution cursor from objective state before acting.

Always check:

- current phase doc set exists and matches the accepted four-file model
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
All semantics still come from `phaseN-plan.yaml` and the shared contract references.

Do not call any non-core contract helper path during execution.

## Reference Loading By Task

When starting a wave (cold start or resume):
- read: wave-execution-patterns.md, external-contract-authority.md, schema-consumption-rules.md, contract-alignment-checklist.md
- run: `uv run ../phase-contract-tools/scripts/preflight_phase_execution.py` with the same `--plan`, `--docs-dir`, `--phase`, and `--wave` arguments as in Quickstart (if unavailable, use the manual checklist in Before Execution)

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
