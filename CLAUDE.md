# CLAUDE.md

## Multi-Agent Rules

Multi-agent execution has two tiers. Full operational protocol is in the `multi-agent-protocol` skill.

**Tier 1 — Explore (read-only):** The agent may launch read-only subagents at any time without pre-declaration. Each subagent must return structured results; the primary agent must synthesize them.

**Tier 2 — Delegate (write-capable):** Before launching any subagent that may edit files or run mutating commands, the agent must output: `[delegate: <count 2–4> | split: <dimension> | risk: <low|medium|high>]`. If the task cannot be cleanly split, output `[delegate: 0 | reason: <why>]` and stay serial.

**Exemptions:** No declaration needed for single-file edits, direct answers, single commands, or git housekeeping.


This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Response Language

Always respond in Chinese (中文). All explanations, summaries, questions, and status updates should be in Chinese. Code, commands, file paths, and technical identifiers remain in English.

## What This Repository Is

A reusable behavior skill library for coding agents. Skills are composable execution constraints (not scripts or language tutorials) that shape how an agent scopes work, plans edits, validates changes, controls context growth, and coordinates parallel analysis. The goal is stable working behavior that transfers across agent platforms (Cursor, Codex, Claude Code).

## Repository Structure

- `skills/` — the **only** canonical published skill source. Each skill is a directory with a `SKILL.md` file containing YAML frontmatter (`name`, `description`, optional `version`). The frontmatter `name` must match the directory name.
- `templates/governance/` — platform-specific governance templates (`AGENTS-template.md`, `CLAUDE-template.md`) used by the installer for rule injection.
- `examples/` — scenario-based acceptance test inputs that define task shape, recommended skill composition, and expected agent behavior.
- `maintainer/` — internal tooling: install scripts, evaluation scripts, data fixtures, and reports. Not part of the published skill tree.
- `docs/user/` — user-facing release documentation. `docs/maintainer/` — internal evaluation docs.

## Key Commands

### Local Mirror Sync (for development)

After editing anything in `skills/`, rebuild and verify local mirrors:

```bash
python3 maintainer/scripts/install/manage-governance.py --sync-local claude
python3 maintainer/scripts/install/manage-governance.py --sync-local claude --check
python3 maintainer/scripts/install/manage-governance.py --sync-local cursor
python3 maintainer/scripts/install/manage-governance.py --sync-local cursor --check
```

### Governance Installation (into a target project)

```bash
# Full suite (skills + rules into project directory)
python3 maintainer/scripts/install/manage-governance.py --project /path/to/repo

# Multi-agent profile only (2 orchestration skills)
python3 maintainer/scripts/install/manage-governance.py --profile multi-agent --project /path/to/repo

# Include phase skills for large multi-wave projects
python3 maintainer/scripts/install/manage-governance.py --project /path/to/repo --include-phase

# Rules only (no skills)
python3 maintainer/scripts/install/manage-governance.py --project /path/to/repo --rules-only

# Verify project-local skills
python3 maintainer/scripts/install/manage-governance.py --project /path/to/repo --check

# Install skills globally (not into a project)
python3 maintainer/scripts/install/manage-governance.py --global

# Verify global skills
python3 maintainer/scripts/install/manage-governance.py --global --check
```

### Validation and Testing

```bash
# Repository layout validation (also runs in CI)
python3 maintainer/scripts/install/validate_repo_layout.py

# Installer smoke tests
python3 maintainer/scripts/install/run_manage_governance_smoke.py

# Skill test report (example-to-skill matrix)
python3 maintainer/scripts/evaluation/generate-skill-test-report.py

# Trigger tests
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report

# Claude trigger smoke
python3 maintainer/scripts/evaluation/run_claude_trigger_smoke.py
```

### CI

GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR to main:
1. **validate-skills** — ensures all `SKILL.md` files are under `skills/`, validates frontmatter (name matches directory, description and version present).
2. **validate-scripts** — runs `validate_repo_layout.py`, checks Python syntax on all scripts, runs installer smoke tests.
3. **install-smoke-test** — does a full `npx openskills install` from `skills/` and verifies at least 10 skills install correctly.

## Architecture: Skill Types

**Execution skills** (single-agent): `scoped-tasking`, `design-before-plan`, `minimal-change-strategy`, `plan-before-action`, `targeted-validation`, `context-budget-awareness`, `read-and-locate`, `safe-refactor`, `bugfix-workflow`, `impact-analysis`, `self-review`, `incremental-delivery`.

**Orchestration skills** (multi-agent): `multi-agent-protocol`, `conflict-resolution`.

**Phase skills** (large multi-wave projects): `phase-plan`, `phase-execute`, `phase-plan-review`, `phase-contract-tools`. These are heavier and should only be used when the task spans 5+ PRs with wave-level coordination.

The recommended starting composition for most tasks is: `scoped-tasking` + `minimal-change-strategy` + `plan-before-action` + `targeted-validation`.

For tasks involving design decisions, use: `scoped-tasking` + `design-before-plan` + `plan-before-action` + `minimal-change-strategy` + `targeted-validation`.

## Architecture: Installer (`manage-governance.py`)

`maintainer/scripts/install/manage-governance.py` is the single public entrypoint for all installation. Three mutually exclusive targets:
- `--project DIR` — install skills + rules into project directory (`DIR/.claude/skills/` etc.)
- `--global` — install skills to global platform directories (`~/.claude/skills/` etc.)
- `--sync-local TARGET` — sync repo-local development mirrors

Modifiers: `--check` (verify instead of install), `--rules-only` / `--skills-only` (with `--project`), `--profile`, `--platform`, `--force`, `--include-phase`

## Key Conventions

- `skills/` is the single source of truth. Generated mirrors (`.cursor/`, `.claude/`, `.agent/`) are gitignored and can be rebuilt anytime.
- SKILL.md frontmatter `name` field must exactly match the enclosing directory name (enforced by CI).
- Testing is behavior-based: run example scenarios in an agent, score against expected guardrails (did the agent scope before exploring? plan before editing? keep changes local?).
- When testing or validating skills, create a temporary directory (`mktemp -d`), initialize a test project there (`git init`), and sync skills with `manage-governance.py --project <temp-dir>`. Run all validation in that isolated environment. Never test skills directly in the agent-skills repo or any real project.
- The AGENTS.md at root is gitignored — it is a generated artifact for local development, not a source file. The canonical rules live in `templates/governance/`.

## Skill Escalation

These rules define when base-level CLAUDE.md rules are insufficient and the agent should load the full skill.

- Escalate to `design-before-plan` when: the task involves choosing between multiple implementation approaches, the change introduces or modifies a public API or cross-module contract, acceptance criteria are missing or unclear, or scoped-tasking identified the boundary but design decisions remain open.
- Escalate to `minimal-change-strategy` when: the diff is growing beyond what the task requires, multiple edit strategies compete, or surrounding code tempts drive-by cleanup.
- Escalate to `context-budget-awareness` when: the working set exceeds 8 files, the same file has been read more than twice without a new question, more than 3 hypotheses are active without ranking evidence, or the last 3 actions did not advance the stated objective.
- Escalate to `targeted-validation` when: multiple validation options exist and the cheapest meaningful check needs deliberate selection, validation is expensive and the change is local enough for a narrower check, or a validation failure needs diagnosis before broadening coverage.
- Escalate to `impact-analysis` when: the change touches a function or interface with 3+ callers, involves a public API or shared type, modifies a data model used across multiple modules, or read-and-locate produced 3+ tentative leads.
- Escalate to `self-review` when: edits span multiple files and are complete, or the user requests a diff review before testing.
- Escalate to `incremental-delivery` when: the plan from plan-before-action spans 2–4 PRs across 1–2 modules and can be delivered serially.

## Skill Lifecycle

- Load the smallest set of skills that fits the current task.
- Drop `scoped-tasking` and `read-and-locate` once the working set and edit points are confirmed.
- Drop `design-before-plan` after the design brief is produced and handed to plan-before-action — it does not stay active during implementation.
- Drop `plan-before-action` once execution is underway and no re-planning is needed.
- Drop `context-budget-awareness` after a successful compression if the session is now compact.
- Keep `minimal-change-strategy` and `targeted-validation` active until the task is complete.
- Drop `impact-analysis` after plan-before-action produces the plan.
- Drop `self-review` after the diff review passes with no blocking issues.
- Drop `incremental-delivery` after the increment list is finalized — it provides structure, not ongoing execution guidance.
- If the task phase changes (e.g., from diagnosis to implementation), re-evaluate which skills are still providing signal.
- Never carry more than 4 active skills simultaneously without explicit justification.
