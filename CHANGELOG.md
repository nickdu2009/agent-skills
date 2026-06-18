# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - 2026-06-19: `requirement-interview`, `architecture-design`, and `implementation-planning` Skills

- Added the `requirement-interview` skill to clarify vague feature requests through a multi-round business interview before any scoping, design, or coding begins.
- Added the `architecture-design` skill to produce structured architecture design documents (component decomposition, data architecture, interface contracts, non-functional design, deployment topology, ADRs) for system/subsystem/module-level work.
- Added the `implementation-planning` skill to create durable implementation plan artifacts between `design-before-plan` and coding.
- Restored dedicated planning as a live execution skill for multi-file, multi-step, or reviewable implementation work, while keeping `AGENTS.md` / `CLAUDE.md` §4 short planning for small local tasks.
- Updated governance (`AGENTS.md`, `CLAUDE.md`, `templates/governance/{AGENTS,CLAUDE}-template.md`) to route requirement clarification, architecture design, and durable planning through the three new skills.
- Added the Cursor user-level rule template (`templates/governance/cursor-agent-skills.mdc`) and taught `manage-governance.py` to install/verify `~/.cursor/rules/agent-skills.mdc`.
- Updated skill metadata (`skill_index.json`), protocol evaluator output fields, trigger test data, manual docs, README, skill-chain aliases, downstream handoffs, and examples to reference the three new skills.

### Removed - 2026-05-18: `plan-before-action` Skill Retirement

- Removed the `plan-before-action` skill (live + `.cursor/` and `.claude/` mirrors). Its discipline is now absorbed by the new `Behavioral Guidelines §4 Goal-Driven Execution` section in governance files.
- Added a `Behavioral Guidelines` section (Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution) to `templates/governance/{AGENTS,CLAUDE}-template.md` and live `AGENTS.md` / `CLAUDE.md`. The new §3 Surgical Changes supersedes the old `Change Rules` section.
- Updated `Skill Activation` lists, `Common Flow Patterns`, and the project-specific "delete-skill-directory" cleanup rule (re-homed under §3) across all four governance files.
- Rewrote downstream handoffs in `skills/scoped-tasking/SKILL.md`, `skills/design-before-plan/SKILL.md`, and `skills/impact-analysis/SKILL.md` to point at `implementation` per AGENTS.md §4 instead of the removed skill.
- Removed `plan-before-action` entries from `maintainer/data/{skill_index.json,skill_test_data.py,trigger_test_data.py,token_efficiency_baseline.md}` and from `maintainer/scripts/evaluation/{skill_protocol_v1.py,score-skill-transcript.py,run_claude_trigger_smoke.py}`.
- Updated user-facing docs: `docs/manual/{SKILL-INDEX,SKILL-SELECTION,COMMON-WORKFLOWS,FAQ,DECISION-RATIONALE}.md` and `docs/user/{SKILL-PROTOCOL-V2,SKILL-TESTING-QUICK-START}.md`.
- Updated examples: `single-agent-bugfix`, `safe-refactor`, `multi-agent-root-cause-analysis`, `self-review`, `impact-analysis`, `skill-evaluation-rubric`, `skill-definition-validator`, `skill-testing-playbook`, `design-before-plan-scenario`, `fix-skill-references`.
- Updated `README.md` (Mermaid graph, Skill Types, Repository Layout, Recommended Starting Composition).
- Historical analysis reports under `docs/maintainer/`, `maintainer/reports/`, and `CHANGELOG-trigger-optimization.md` are intentionally untouched as point-in-time snapshots.

### Removed - 2026-05-18: Phase Skill Family Retirement

- Removed the entire phase skill family: `phase-plan`, `phase-execute`, and `phase-contract-tools` (live skills + `.cursor/` and `.claude/` mirrors).
- Pruned phase references from governance (`AGENTS.md`, `CLAUDE.md`, `templates/governance/{AGENTS,CLAUDE}-template.md`) including Tier-2 Overflow guidance, Mid-task escalation entries, and the Common Flow Patterns table.
- Updated `README.md` (Mermaid graph, Skill Types section, Repository Layout, Recommended Starting Composition) and `docs/manual/SKILL-INDEX.md` / `SKILL-SELECTION.md` to drop the Phase System Skills group.
- Removed `phase-plan` fallback from `skills/impact-analysis/SKILL.md` (Composition fallbacks, Failure Handling fallback, Deactivation triggers).
- Cleaned `docs/user/SKILL-PROTOCOL-V1.md` / `SKILL-PROTOCOL-V2.md` family-budget rules and removed the phase escalation from `docs/maintainer/skill-chain-aliases.md`.
- Deleted phase-only assets: `examples/phased-migration-planning.md` and root `phase-toolchain-optimization-zh.md`; trimmed phase rows from `examples/skill-testing-playbook.md` and `examples/skill-evaluation-rubric.md`.
- Removed phase entries from `maintainer/data/{skill_index.json,skill_test_data.py,trigger_test_data.py}` (deleted `PHASE_CASES`, the `incremental-upgrade-to-phase` and `phase-5pr-boundary` boundary cases, and the duplicate copies under `ALL_TRIGGER_CASES`).
- Removed phase scenarios/cases from `maintainer/scripts/evaluation/{run_claude_trigger_smoke.py,run_claude_interactive_mainline.py,skill_protocol_v1.py}` and the phase fixture assertion in `maintainer/scripts/install/run_manage_governance_smoke.py`; pruned phase-only allowlist entries from `maintainer/scripts/analysis/check_cross_references.py`.
- Historical analysis reports under `docs/maintainer/` and `maintainer/data/token_efficiency_baseline.md` are intentionally untouched as point-in-time snapshots.

### Changed - 2026-05-18: Skill Library Modernization

- Removed 7 live skills: read-and-locate, context-budget-awareness, incremental-delivery, minimal-change-strategy, knowledge-driven-development, conflict-resolution, and phase-plan-review.
- Merged conflict arbitration into multi-agent-protocol and phase acceptance checks into phase-plan.
- Slimmed plan-before-action, self-review, multi-agent-protocol, targeted-validation, safe-refactor, and bugfix-workflow to compact trigger-and-contract guidance.
- Removed compatibility shims and updated governance, docs, examples, data, and maintenance scripts for the 14-skill live set.

### Added - 2026-04-11: Skill Protocol v2 Migration

**Skill Protocol v2**: Compact inline protocol format for improved token efficiency and readability.

- **New Protocol Format**: `[task-validation: PASS | clarity:✓ scope:✓ safety:✓ skill_match:✓ | action:proceed]`
  - Replaces verbose YAML multi-line blocks with single-line compact format
  - Achieves 53-70% token savings depending on content type and complexity
  - Backward compatible: v1 verbose format still supported for complex diagnostic scenarios

- **Protocol Parser Infrastructure**:
  - `maintainer/scripts/evaluation/skill_protocol_v2.py`: Complete v2 block parser (7 block types)
  - `maintainer/scripts/evaluation/skill_protocol_unified.py`: Auto-detection and format delegation
  - `maintainer/scripts/analysis/measure_protocol_blocks.py`: Token measurement for protocol blocks
  - Lifecycle validation: validates output/validate and trigger/drop pairing

- **Documentation**:
  - `docs/user/SKILL-PROTOCOL-V2.md`: Complete v2 specification (354 lines)
  - `docs/maintainer/protocol-v2-compact.md`: V1→V2 migration guide with side-by-side examples
  - `docs/maintainer/protocol-v2-migration-tracker.md`: Migration progress tracking and token metrics

### Changed - 2026-04-11: Skill Protocol v2 Migration

**Governance Files** (4 files migrated to v2 as primary format):
- CLAUDE.md, AGENTS.md, CLAUDE-template.md, AGENTS-template.md
  - "Skill Protocol v1" renamed to "Skill Protocol v2"
  - Protocol block examples converted to v2 compact format
  - V1 format moved to "Legacy v1 Format" section for reference

**Example Files** (10/12 migrated to v2, 83.3%):
- Migrated: single-agent-bugfix, safe-refactor, read-and-locate, context-budgeted-debugging, self-review, impact-analysis, incremental-delivery, multi-agent-root-cause-analysis, phased-migration-planning, design-before-plan-scenario
- Kept in v1: skill-evaluation-rubric, skill-testing-playbook (pedagogical, shows both formats)
- Code impact: -682 lines removed, +423 added, net -259 lines

**Skill Documentation** (12/18 updated with v2 output examples, 66.7%):
- Tier 1 (5/5): bugfix-workflow, minimal-change-strategy, plan-before-action, scoped-tasking, targeted-validation
- Tier 2 (7/7): conflict-resolution, context-budget-awareness, design-before-plan, impact-analysis, incremental-delivery, read-and-locate, safe-refactor, self-review
- Format: Added "### V2 Format (compact)" sections alongside existing v1 examples

### Performance - 2026-04-11

**Token Savings** (measured with tiktoken cl100k_base):
- Protocol block skeletons (Phase 2): **69.6% reduction** (303 → 92 tokens)
- Content-rich examples (Phase 3): **53.4% average reduction** (4,422 → 2,061 tokens)
  - Simple examples (Wave 1): 54.3% reduction (873 → 399 tokens)
  - Complex examples (Wave 2+3): 53.2% reduction (3,549 → 1,662 tokens)
- **Total tokens saved**: 2,572 tokens across migrated files

**Readability Improvements**:
- Protocol blocks: 1 line vs 10-20 lines (v1)
- Net code reduction: 259 lines across 28 files
- Improved scanability: protocol blocks visible at a glance
- Better density: more information per screen

### Migration Methodology - 2026-04-11

Executed via **multi-agent-protocol** with 3 parallel agents:
- Agent 1 (Wave 1): Migrated 2 simple examples in 2.1 hours
- Agent 2 (Wave 2+3): Migrated 8 complex examples in 5.4 hours
- Agent 3 (Skills): Updated 12 skill files (ongoing)
- **Efficiency gain**: ~95% time reduction vs serial execution (1 day vs 3-4 days)

### Validation - 2026-04-11

All automated checks passed:
- ✅ Parser validation: 100% pass rate (10/10 v2 files parse correctly)
- ✅ Lifecycle validation: Output/validate pairing, trigger/drop pairing verified
- ✅ Semantic preservation: Zero information loss detected
- ✅ Protocol compliance: Zero violations

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
- Initial third-party CLI installation path
- Cursor mirror sync script (`maintainer/scripts/install/sync-cursor-skills.py`)
- Skill test report generator (`maintainer/scripts/evaluation/generate-skill-test-report.py`)
- Skill transcript scorer (`maintainer/scripts/evaluation/score-skill-transcript.py`)
- Example scenarios for single-agent bugfix, safe refactor, read-and-locate, context-budgeted debugging, and multi-agent root cause analysis
- Initial release-readiness checklist under `docs/user/`
- GitHub Actions CI for format validation and install smoke testing
- LICENSE (MIT)
- SECURITY.md
