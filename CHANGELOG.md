# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Reorganized non-skill repository content into explicit user and maintainer surfaces: install entrypoints now live under `maintainer/scripts/install/`, user release docs under `docs/user/`, and maintainer-only evaluation data, docs, templates, and retained baselines under `maintainer/`, `docs/maintainer/`, and nested `templates/` subdirectories.
- Replaced `subagent-orchestration` with `multi-agent-protocol`, a tiered orchestration skill that distinguishes read-only exploration (Tier 1) from write-capable delegation (Tier 2) with explicit gate declarations, structured subagent contracts, and platform-specific mappings.
- Updated all cross-references in `conflict-resolution`, `context-budget-awareness`, `targeted-validation`, `plan-before-action`, examples, and scoring scripts.
- Renamed the governance setup script to `maintainer/scripts/install/setup-multi-agent-governance.sh` for clearer multi-agent intent.

### Added

- `templates/governance/AGENTS-multi-agent-rules.md` — a ready-made snippet for injecting Multi-Agent Rules into project-level `AGENTS.md` or `CLAUDE.md`.
- `maintainer/scripts/install/setup-multi-agent-governance.sh` — cross-platform installer for governance skills and rules injection (supports Cursor, Codex, Claude Code).

### Removed

- `subagent-orchestration` skill (superseded by `multi-agent-protocol`).

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
