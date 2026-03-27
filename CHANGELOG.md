# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Replaced `subagent-orchestration` with `multi-agent-protocol`, a tiered orchestration skill that distinguishes read-only exploration (Tier 1) from write-capable delegation (Tier 2) with explicit gate declarations, structured subagent contracts, and platform-specific mappings.
- Updated all cross-references in `conflict-resolution`, `context-budget-awareness`, `targeted-validation`, `plan-before-action`, examples, and scoring scripts.
- Renamed the governance setup script to `scripts/setup-multi-agent-governance.sh` for clearer multi-agent intent.

### Added

- `templates/AGENTS-multi-agent-rules.md` — a ready-made snippet for injecting Multi-Agent Rules into project-level `AGENTS.md` or `CLAUDE.md`.
- `scripts/setup-multi-agent-governance.sh` — cross-platform installer for governance skills and rules injection (supports Cursor, Codex, Claude Code).

### Removed

- `subagent-orchestration` skill (superseded by `multi-agent-protocol`).

## [0.1.0] - 2026-03-27

### Added

- Initial release of 10 agent execution and orchestration skills
- Execution skills: scoped-tasking, minimal-change-strategy, plan-before-action, targeted-validation, context-budget-awareness, read-and-locate, safe-refactor, bugfix-workflow
- Orchestration skills: subagent-orchestration, conflict-resolution
- OpenSkills installation support with `--universal` flag
- Cursor mirror sync script (`scripts/sync-cursor-skills.py`)
- Skill test report generator (`scripts/generate-skill-test-report.py`)
- Skill transcript scorer (`scripts/score-skill-transcript.py`)
- Example scenarios for single-agent bugfix, safe refactor, read-and-locate, context-budgeted debugging, and multi-agent root cause analysis
- OpenSkills release checklist
- GitHub Actions CI for format validation and install smoke testing
- LICENSE (MIT)
- SECURITY.md
