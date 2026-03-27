# Agent Execution Skills

This repository is a reusable skill library for coding agents. It focuses on execution discipline and orchestration patterns: how an agent scopes work, plans edits, reads code efficiently, validates narrowly, controls context growth, and coordinates parallel analysis when justified.

It is not a language tutorial, framework guide, product-specific prompt pack, or optimization bundle. The goal is stable working behavior that transfers across agent platforms.

## Repository Map

```mermaid
flowchart TD
    T[Task] --> S[scoped-tasking]
    S --> P[plan-before-action]
    P --> M[minimal-change-strategy]
    M --> V[targeted-validation]
    P --> C[context-budget-awareness]
    S --> R[read-and-locate]
    M --> F[safe-refactor]
    S --> B[bugfix-workflow]
    P --> O[multi-agent-protocol]
    O --> X[conflict-resolution]
```

## What This Repository Is

- A behavior library for coding agents working on real repositories.
- A set of composable skills for narrowing scope, making smaller changes, and reducing avoidable risk.
- A practical reference for single-agent and multi-agent execution patterns.

## What This Repository Is Not

- Not a language or framework knowledge base.
- Not a collection of vendor-specific prompts or UI instructions.
- Not a substitute for project-specific architecture, domain rules, or coding standards.

## Skill Types

### Execution Skills

Execution skills shape how one agent works inside a bounded task. They reduce unnecessary edits, unnecessary reading, and unnecessary validation.

Included execution skills:

- `scoped-tasking`
- `minimal-change-strategy`
- `plan-before-action`
- `targeted-validation`
- `context-budget-awareness`
- `read-and-locate`
- `safe-refactor`
- `bugfix-workflow`

### Orchestration Skills

Orchestration skills shape how a primary agent coordinates multiple lines of work, especially when analysis can be decomposed without creating coupling or merge confusion.

Included orchestration skills:

- `multi-agent-protocol`
- `conflict-resolution`

## Recommended Starting Composition

For most single-agent coding tasks, start with:

- `scoped-tasking`
- `minimal-change-strategy`
- `plan-before-action`
- `targeted-validation`

This baseline composition creates a disciplined default:

- define the smallest useful boundary
- decide the intended edit before touching files
- prefer the smallest viable patch
- verify only the affected surface first

## When to Add More Skills

Add `context-budget-awareness` when:

- the session is getting long or noisy
- large files or logs are pulling too much attention
- the active objective keeps drifting
- a fresh focused pass would be cheaper than carrying accumulated context

Add `read-and-locate` when:

- the codebase is unfamiliar
- the edit point is not known yet
- you need to identify call paths, boundaries, or ownership quickly

Add `safe-refactor` when:

- the task is structural rather than behavioral
- duplicated logic or local complexity needs cleanup
- you must keep interfaces and behavior stable while improving internals

Add `bugfix-workflow` when:

- the main task is diagnosing or fixing a bug
- symptoms are known but the fault domain is not
- evidence must be gathered before any edit is justified

Add `multi-agent-protocol` when:

- the task can be split into low-coupling subproblems
- multiple hypotheses can be tested independently
- different modules or artifact types can be analyzed in parallel
- read-only exploration benefits from parallel subagents

Add `conflict-resolution` when:

- multiple subagents report overlapping or conflicting conclusions
- evidence must be compared and merged before acting
- uncertainty should be preserved instead of collapsed too early

## Design Philosophy

- Scope first.
- Plan first.
- Make the smallest viable change.
- Validate narrowly.
- Control context growth.
- Parallelize only when justified.

## Repository Layout

```text
README.md
OPENSKILLS-RELEASE-CHECKLIST.md
skills/
  scoped-tasking/
  minimal-change-strategy/
  plan-before-action/
  targeted-validation/
  context-budget-awareness/
  read-and-locate/
  safe-refactor/
  bugfix-workflow/
  multi-agent-protocol/
  conflict-resolution/
templates/
  AGENTS-multi-agent-rules.md
examples/
  single-agent-bugfix.md
  safe-refactor.md
  read-and-locate.md
  context-budgeted-debugging.md
  multi-agent-root-cause-analysis.md
scripts/
  sync-cursor-skills.py
  setup-multi-agent-governance.sh
```

## Publishing Shape

This repository is published with one canonical skill tree: `skills/`.

That source-of-truth rule matters for installers that recursively scan repositories for `SKILL.md`. Each published skill should exist once in the source tree.

Local tool-specific mirrors and generated install outputs must stay out of the published source tree.

Generated local artifacts in this repository include:

- `.cursor/`
- `.agent/`
- `.claude/`
- `AGENTS.md`

These are local-only files or directories and are ignored by Git.

## OpenSkills

Use `skills/` as the installation source.

Install all skills from a published repository:

```bash
npx openskills install your-org/agent-skills --universal
npx openskills sync
```

Install one skill directly:

```bash
npx openskills install your-org/agent-skills/skills/scoped-tasking --universal
npx openskills sync
```

For local development against this repository:

```bash
npx openskills install ./skills --universal
npx openskills sync
```

Always install from `./skills`, not from the repository root. Installing from the root causes the OpenSkills scanner to find duplicate skills in generated local directories such as `.agent/skills/`.

`--universal` installs to `.agent/skills/`, which is the safer default for multi-agent setups. If you prefer the default OpenSkills layout, omit `--universal`.

For release readiness and acceptance checks, use [`OPENSKILLS-RELEASE-CHECKLIST.md`](OPENSKILLS-RELEASE-CHECKLIST.md).

## Governance Setup

The `multi-agent-protocol` skill works best when paired with a short Multi-Agent Rules section in your project-level `AGENTS.md` (or `CLAUDE.md` for Claude Code). A ready-made template lives in `templates/AGENTS-multi-agent-rules.md`.

Install both the governance skills and inject the rules into a project:

```bash
./scripts/setup-multi-agent-governance.sh --project /path/to/my-repo
```

Install only the skills (no project file changes):

```bash
./scripts/setup-multi-agent-governance.sh --skills-only
```

Inject only the rules into an existing `AGENTS.md`:

```bash
./scripts/setup-multi-agent-governance.sh --rules-only /path/to/my-repo
```

Force a specific platform:

```bash
./scripts/setup-multi-agent-governance.sh --skills-only --platform codex --force
```

The script auto-detects installed platforms (Cursor, Codex, Claude Code) and places skills in the appropriate directory.

## Cursor Mirror

If you want local Cursor discovery while working in this repository, generate `.cursor/skills/` from `skills/`:

```bash
python3 scripts/sync-cursor-skills.py
```

The generated `.cursor/` tree is local-only, ignored by Git, and can be deleted and rebuilt at any time.

To verify that the local mirror is still current:

```bash
python3 scripts/sync-cursor-skills.py --check
```

## How to Test Skills

Skill testing in this repository is intentionally lightweight. These skills shape agent behavior, so the most useful checks combine one static verification step with one scenario-based behavior review.

```mermaid
flowchart TD
    A[Edit skills/] --> B[Check Cursor mirror sync]
    B --> C[Pick one example scenario]
    C --> D[Run the scenario in Cursor or another agent]
    D --> E[Score behavior against the checklist]
    E --> F[Capture pass/fail and residual risk]
```

Use this three-part loop:

1. Verify the local Cursor mirror is current.
2. Run one or more example scenarios as acceptance tests.
3. Record whether the agent behavior matched the intended skill guardrails.

Before release, also run an OpenSkills install smoke test using the checklist in [`OPENSKILLS-RELEASE-CHECKLIST.md`](OPENSKILLS-RELEASE-CHECKLIST.md).

### 1. Static Verification

Use the existing sync checker after every change to `skills/`:

```bash
python3 scripts/sync-cursor-skills.py --check
```

If the mirror is out of date, rebuild it:

```bash
python3 scripts/sync-cursor-skills.py
```

### 2. Scenario-Based Acceptance Testing

The `examples/` directory is the primary behavior test suite. Each example defines:

- a task shape
- a recommended skill composition
- expected execution patterns
- guardrails that should appear in the agent behavior

Recommended examples:

- `examples/single-agent-bugfix.md`
- `examples/read-and-locate.md`
- `examples/safe-refactor.md`
- `examples/context-budgeted-debugging.md`
- `examples/multi-agent-root-cause-analysis.md`

When testing, evaluate behavior rather than only the final answer. For example:

- Did the agent declare scope before exploring?
- Did it plan before editing?
- Did it keep the change local?
- Did it choose targeted validation instead of defaulting to a full suite?
- Did it preserve uncertainty when the evidence was incomplete?

### 3. Generate a Report Skeleton

Use the helper script to print the example-to-skill matrix:

```bash
python3 scripts/generate-skill-test-report.py
```

Generate a Markdown report template for a manual test pass:

```bash
python3 scripts/generate-skill-test-report.py --write-report skill-test-report.md
```

Optionally include the local mirror sync check in the same command:

```bash
python3 scripts/generate-skill-test-report.py --check-sync --write-report skill-test-report.md
```

The generated report is designed for lightweight regression checks across skill revisions. It does not replace human review of agent behavior.

## How to Use

Use these skills as composable working constraints, not as rigid scripts.

1. Start with the smallest set of skills that fits the task.
2. Add skills only when the task shape justifies them.
3. Keep the active composition aligned with the current objective.
4. Remove or ignore skills that no longer provide signal for the current step.

## Design Bias

This repository intentionally favors smaller moves over broader automation. That bias trades some speed for lower error rate, lower review cost, and easier recovery when a line of work turns out to be wrong.
