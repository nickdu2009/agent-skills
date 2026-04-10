# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Upgraded the repository to Skill Protocol v1 across all 18 skills, including explicit protocol blocks, family-specific lifecycle rules, deactivation requirements, and family-level concurrency budgets for execution, orchestration, and phase skills.
- Expanded evaluation tooling to report static Skill Protocol v1 readiness, validate protocol blocks in smoke outputs, and cover the newly added trigger/smoke cases for `design-before-plan`, `impact-analysis`, `incremental-delivery`, `self-review`, and `phase-plan-review`.
- Updated all example scenarios to include compact Skill Protocol v1 traces and updated the release checklist to include protocol-readiness gates.
- Reorganized non-skill repository content into explicit user and maintainer surfaces: install entrypoints now live under `maintainer/scripts/install/`, user release docs under `docs/user/`, and maintainer-only evaluation data, docs, templates, and retained baselines under `maintainer/`, `docs/maintainer/`, and nested `templates/` subdirectories.
- Replaced `subagent-orchestration` with `multi-agent-protocol`, a tiered orchestration skill that distinguishes read-only exploration (Tier 1) from write-capable delegation (Tier 2) with explicit gate declarations, structured subagent contracts, and platform-specific mappings.
- Updated all cross-references in `conflict-resolution`, `context-budget-awareness`, `targeted-validation`, `plan-before-action`, examples, and scoring scripts.
- Unified governance installation and local mirror sync behind a single public script, `maintainer/scripts/install/manage-governance.py`, with profile-based and mirror modes.

### Added

- `docs/user/SKILL-PROTOCOL-V1.md` — a concise user-facing guide to the repository-wide Skill Protocol v1 model, required blocks, family budgets, and evaluation entrypoints.
- `templates/governance/AGENTS-template.md` and `templates/governance/CLAUDE-template.md` — ready-made platform-specific governance templates for project-level rule injection.
- `maintainer/scripts/install/manage-governance.py` — cross-platform entrypoint for governance skills, rule injection, and local mirror management (supports Cursor, Codex, Claude Code).

### Removed

- `subagent-orchestration` skill (superseded by `multi-agent-protocol`).
- Standalone local mirror sync entrypoints in favor of `manage-governance.py --sync-local` and `--check-local`.

## [0.1.0] - 2026-03-27

### Added

- Initial release of 10 agent execution and orchestration skills
- Execution skills: scoped-tasking, minimal-change-strategy, plan-before-action, targeted-validation, context-budget-awareness, read-and-locate, safe-refactor, bugfix-workflow
- Orchestration skills: subagent-orchestration, conflict-resolution
- OpenSkills installation support with `--universal` flag
- Cursor mirror sync script (`maintainer/scripts/install/sync-cursor-skills.py`)
- Skill test report generator (`maintainer/scripts/evaluation/generate-skill-test-report.py`)
- Skill transcript scorer (`maintainer/scripts/evaluation/score-skill-transcript.py`)
- Example scenarios for single-agent bugfix, safe refactor, read-and-locate, context-budgeted debugging, and multi-agent root cause analysis
- OpenSkills release checklist under `docs/user/`
- GitHub Actions CI for format validation and install smoke testing
- LICENSE (MIT)
- SECURITY.md
