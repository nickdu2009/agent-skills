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
python3 maintainer/scripts/install/manage-governance.py --check-local claude
python3 maintainer/scripts/install/manage-governance.py --sync-local cursor
python3 maintainer/scripts/install/manage-governance.py --check-local cursor
```

### Governance Installation (into a target project)

```bash
# Full suite (all skills + AGENTS.md rule injection)
python3 maintainer/scripts/install/manage-governance.py --project /path/to/repo

# Multi-agent profile only (2 orchestration skills)
python3 maintainer/scripts/install/manage-governance.py --profile multi-agent --project /path/to/repo

# Include phase skills for large multi-wave projects
python3 maintainer/scripts/install/manage-governance.py --project /path/to/repo --include-phase
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

**Execution skills** (single-agent): `scoped-tasking`, `minimal-change-strategy`, `plan-before-action`, `targeted-validation`, `context-budget-awareness`, `read-and-locate`, `safe-refactor`, `bugfix-workflow`.

**Orchestration skills** (multi-agent): `multi-agent-protocol`, `conflict-resolution`.

**Phase skills** (large multi-wave projects): `phase-plan`, `phase-execute`, `phase-plan-review`, `phase-contract-tools`. These are heavier and should only be used when the task spans 5+ PRs with wave-level coordination.

The recommended starting composition for most tasks is: `scoped-tasking` + `minimal-change-strategy` + `plan-before-action` + `targeted-validation`.

## Architecture: Installer (`manage-governance.py`)

`maintainer/scripts/install/manage-governance.py` is the single public entrypoint for all installation. It handles:
- Skill copy to platform-specific directories (`~/.cursor/skills/`, `~/.claude/skills/`, `~/.codex/skills/`)
- `AGENTS.md` / `CLAUDE.md` rule injection from governance templates
- Local mirror sync (`--sync-local`) and verification (`--check-local`)
- Profile-based installation (`--profile full` or `--profile multi-agent`)
- Auto-detection of installed platforms

## Key Conventions

- `skills/` is the single source of truth. Generated mirrors (`.cursor/`, `.claude/`, `.agent/`) are gitignored and can be rebuilt anytime.
- SKILL.md frontmatter `name` field must exactly match the enclosing directory name (enforced by CI).
- Testing is behavior-based: run example scenarios in an agent, score against expected guardrails (did the agent scope before exploring? plan before editing? keep changes local?).
- The AGENTS.md at root is gitignored — it is a generated artifact for local development, not a source file. The canonical rules live in `templates/governance/`.

## Skill Escalation

These rules define when base-level CLAUDE.md rules are insufficient and the agent should load the full skill.

- Escalate to `minimal-change-strategy` when: the diff is growing beyond what the task requires, multiple edit strategies compete, or surrounding code tempts drive-by cleanup.
- Escalate to `context-budget-awareness` when: the working set exceeds 8 files, the same file has been read more than twice without a new question, more than 3 hypotheses are active without ranking evidence, or the last 3 actions did not advance the stated objective.
- Escalate to `targeted-validation` when: multiple validation options exist and the cheapest meaningful check needs deliberate selection, validation is expensive and the change is local enough for a narrower check, or a validation failure needs diagnosis before broadening coverage.

## Skill Lifecycle

- Load the smallest set of skills that fits the current task.
- Drop `scoped-tasking` and `read-and-locate` once the working set and edit points are confirmed.
- Drop `plan-before-action` once execution is underway and no re-planning is needed.
- Drop `context-budget-awareness` after a successful compression if the session is now compact.
- Keep `minimal-change-strategy` and `targeted-validation` active until the task is complete.
- If the task phase changes (e.g., from diagnosis to implementation), re-evaluate which skills are still providing signal.
- Never carry more than 4 active skills simultaneously without explicit justification.
