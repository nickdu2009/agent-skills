# Cross-Platform Skills Compatibility

Status: Draft  
Date: 2026-04-11  
Scope: Cursor, Claude Code, Codex, ZCode, Kimi Code

## Summary

`Cursor`, `Claude Code`, `Codex`, `ZCode`, and `Kimi Code` do not expose identical full `skills`
 specifications, but they do share a meaningful common base:

- all five support directory-based skills
- all five use `SKILL.md` as the entrypoint
- all five support automatic relevance-based invocation
- all five support explicit invocation
- all five support optional supporting files such as scripts or reference docs

The correct compatibility model for this repository is therefore:

1. a shared portable core
2. platform-specific extensions
3. platform-specific installation and governance wrappers

This document focuses on `skills` only. It does not cover `AGENTS.md`,
`CLAUDE.md`, or rules systems except where they affect skill compatibility.

## Source Notes

This comparison is based on official documentation:

- Codex: [Agent Skills](https://developers.openai.com/codex/skills)
- Claude Code: [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- Cursor: [Agent Skills](https://cursor.com/cn/docs/skills)
- ZCode: [Skill](https://zcode.z.ai/cn/docs/skill) and [ZCode Agent](https://zcode.z.ai/cn/docs/agents)
- Kimi Code: [Agent Skills](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html)

For Cursor, the official web page did not expose full HTML content through the
available fetch path during review, so the comparison used the official Cursor
docs PDF export of the same page content.

## Confirmed Common Ground

The following points are explicitly supported across all five platforms:

### 1. Skill package shape

- A skill is stored as a directory.
- `SKILL.md` is the entrypoint file.
- Skills can include supporting files.

### 2. Invocation model

- Skills can be triggered automatically when relevant.
- Skills can also be invoked explicitly by the user.
- `description` is central to relevance matching.

### 3. Resource packaging

- Skills may include scripts.
- Skills may include reference or asset files.
- Platforms encourage keeping the main skill concise and placing larger
  supporting material outside the main `SKILL.md`.

### 4. Progressive loading intent

All four platforms describe or imply a progressive-loading model:

- load lightweight identifying metadata first
- load detailed instructions only when the skill is actually used

This is important for token-efficiency planning because it means skill
 compatibility is not just about syntax; it is also about how much content is
 always loaded versus loaded on demand.

## Compatibility Matrix

| Dimension | Cursor | Codex | Claude Code | ZCode | Kimi Code |
|-----------|--------|-------|-------------|-------|-----------|
| Open standard alignment | Yes | Yes | Yes | Yes | Yes |
| `SKILL.md` required | Yes | Yes | Yes | Yes | Yes |
| `name` required | Yes | Yes | No, may fall back to directory name | Yes | Yes for directory form; flat `.md` falls back to filename |
| `description` required | Yes | Yes | Recommended, not strictly required | Yes | Yes for directory form; flat `.md` falls back to first body line |
| `name` must equal directory name | Yes | Not stated as required | Not required | Yes in public examples and UI flow | Not stated as required |
| Automatic invocation | Yes | Yes | Yes | Yes | Yes |
| Explicit invocation | Yes | Yes | Yes | Yes | Yes (`/skill:<name>`) |
| Optional supporting files | Yes | Yes | Yes | Yes | Yes |
| Scripts supported | Yes | Yes | Yes | Yes | Yes |
| References/assets supported | Yes | Yes | Yes | Yes | Yes |
| Platform-specific metadata/extensions | Yes | Yes | Yes, most extensive | Yes | Yes (`whenToUse`, `type`, `arguments`, `disableModelInvocation`) |

## Platform Notes

## Cursor

Officially confirmed behavior:

- Skills are part of an open Agent Skills standard.
- Skills load from:
  - `.agents/skills/`
  - `.cursor/skills/`
  - `~/.cursor/skills/`
- Cursor also loads compatible skills from:
  - `.claude/skills/`
  - `.codex/skills/`
  - `~/.claude/skills/`
  - `~/.codex/skills/`
- Frontmatter fields include:
  - `name` (required)
  - `description` (required)
  - `license`
  - `compatibility`
  - `metadata`
  - `disable-model-invocation`

Important compatibility implications:

- Cursor is the strictest of the three on the portable basics.
- `name` must be present.
- `description` must be present.
- `name` must match the parent folder name.

This makes Cursor a good baseline for the repository's cross-platform minimum
 contract.

## Codex

Officially confirmed behavior:

- Codex skills build on the open agent skills standard.
- A skill is a directory with `SKILL.md` plus optional scripts and references.
- `SKILL.md` must include:
  - `name`
  - `description`
- Codex uses progressive disclosure:
  - metadata first
  - full instructions only when the skill is selected
- Codex supports platform-specific metadata via `agents/openai.yaml`.

Important compatibility implications:

- Codex keeps the core contract fairly small.
- Its main extension point is not frontmatter bloat inside `SKILL.md`, but
  adjacent metadata and plugin packaging.

## Claude Code

Officially confirmed behavior:

- Claude Code skills follow the open Agent Skills standard.
- Claude Code extends that standard with additional runtime controls.
- `SKILL.md` fields include or support:
  - `name`
  - `description`
  - `argument-hint`
  - `disable-model-invocation`
  - `user-invocable`
  - `allowed-tools`
  - `model`
  - `effort`
  - `context`
  - `agent`
  - `hooks`
  - `paths`
  - `shell`

Important compatibility implications:

- Claude Code is the most feature-rich skill runtime among the currently
  compared platforms.
- It is the least suitable platform to use as the portable baseline because its
  extra fields encode runtime behavior that other platforms may not honor.

## ZCode

Officially confirmed behavior:

- ZCode skills are directory-based and use `SKILL.md` as the entrypoint.
- ZCode public examples require `name` and `description` frontmatter.
- ZCode user-level skills live at `~/.zcode/skills/<skill-name>/SKILL.md`.
- ZCode supports explicit `$skill-name` invocation and relevance-based use.
- ZCode can import skills maintained in other agent tools instead of requiring
  a separate rewrite.

Important compatibility implications:

- ZCode fits the same portable `SKILL.md` core already used by this repository.
- ZCode publicly documents the user-level skill path, but current public docs do
  not publish a stable project-level skill filesystem path.
- Governance should therefore prefer `AGENTS.md` for workspace rules and treat
  project-local skill installation as a platform-adaptation concern, not a
  portable-core assumption.

## Kimi Code

Officially confirmed behavior:

- Kimi Code skills are directory-based and use `SKILL.md` with YAML frontmatter
  as the entrypoint; a flat single `.md` file is also supported.
- In directory form, both `name` and `description` must be explicitly provided;
  omitting either causes parsing to fail.
- Skill loading locations:
  - project level: `.kimi-code/skills/`, `.agents/skills/`
  - user level: `$KIMI_CODE_HOME/skills/` (default `~/.kimi-code/skills/`),
    `~/.agents/skills/`
  - extra directories via `extra_skill_dirs` in `config.toml`
- Frontmatter fields include `name`, `description`, `type`, `whenToUse`,
  `disableModelInvocation`, and `arguments`; unknown fields are ignored.
- Skills are triggered automatically based on `description` / `whenToUse`, or
  explicitly via `/skill:<name>`.
- Kimi Code natively reads project-root `AGENTS.md` as workspace instructions;
  user-level global instructions live at `$KIMI_CODE_HOME/AGENTS.md`.

Important compatibility implications:

- Kimi Code fits the same portable `SKILL.md` core already used by this
  repository with zero skill-source changes.
- Unlike ZCode, Kimi Code publicly documents a stable project-level skill
  filesystem path (`.kimi-code/skills/`), so project installation can be fully
  automated.
- Governance reuse is direct: the existing `AGENTS.md` template works as-is,
  with no third governance template needed.
- Skill bodies should avoid unescaped `$ARGUMENTS` / `$0`-style placeholders,
  which Kimi Code expands at invocation time.

## Practical Repository Contract

For this repository, the most portable baseline should be the strictest shared
subset that still works naturally on all five platforms.

### Recommended portable minimum

Every shared skill should satisfy:

```yaml
---
name: my-skill
description: Explain what this skill does and when it should trigger.
---
```

And the following repository rules should hold:

- directory name matches `name`
- `name` uses lowercase letters, digits, and hyphens only
- `description` is mandatory in practice, even if one platform treats it as
  optional
- the main `SKILL.md` stays focused and concise
- large reference material lives outside `SKILL.md`

### Recommended portable directory shape

```text
my-skill/
├── SKILL.md
├── scripts/        # optional
├── references/     # optional
└── assets/         # optional
```

This structure is safe because it fits the documented expectations of all five
 platforms.

## What Should Stay Out of the Portable Core

The following should be treated as platform-enhancement features, not as part of
 the shared contract:

### Claude Code-specific runtime controls

- `allowed-tools`
- `user-invocable`
- `model`
- `effort`
- `context`
- `agent`
- `hooks`
- `paths`
- `shell`

### Codex-specific extension surface

- `agents/openai.yaml`
- Codex plugin packaging and UI metadata

### Cursor-specific assumptions

- direct reliance on Cursor-only loading locations
- migration workflows such as `/migrate-to-skills`
- fields that are accepted by Cursor but not guaranteed elsewhere unless they
  are already part of the common subset

## Compatibility Strategy

This repository should follow a three-layer strategy.

### Layer 1: Portable core

Keep the shared skill source tree compatible with:

- Cursor's required `name` + `description`
- Codex's required `name` + `description`
- Claude Code's standard-compatible baseline
- ZCode's documented `SKILL.md` + frontmatter format
- Kimi Code's required `name` + `description` for directory-form skills

### Layer 2: Platform adaptation

Use installation layout and platform-specific governance files to adapt how the
 same skill tree is surfaced to each tool.

Examples:

- `AGENTS.md` for Cursor, Codex, ZCode, and Kimi Code
- `CLAUDE.md` for Claude Code

### Layer 3: Platform enhancement

If the repository later wants to use platform-only features, treat them as
 optional overlays rather than changing the shared core contract.

## Implications For Token Efficiency Work

This compatibility model changes what token-efficiency work is realistic inside
 the repository.

Safe optimization targets:

- keep `SKILL.md` concise
- move bulky instructions into `references/`
- tighten `description` wording
- avoid duplicating long process explanations across multiple skills
- preserve a small shared frontmatter contract

Unsafe optimization targets unless platform-specific:

- relying on Claude-only runtime fields in shared skills
- relying on Codex-only metadata behavior in shared skills
- assuming all platforms interpret invocation control the same way

## Recommendations

1. Treat Cursor's stricter frontmatter requirements as the baseline.
2. Require `name` and `description` in every shared skill.
3. Require `name == directory name` for every shared skill.
4. Keep shared skills free of platform-only behavior fields unless they are
   isolated behind a deliberate enhancement path.
5. Keep the repository's public guidance explicit that it offers:
   - one shared skill source tree
   - multiple platform-specific governance wrappers
   - optional platform-specific enhancement opportunities
6. Treat ZCode project-level skill placement as an explicit platform-adaptation
   question until official docs publish a stable filesystem path.

## Final Assessment

The most accurate statement for maintainers is:

> Cursor, Codex, Claude Code, ZCode, and Kimi Code do not expose identical full skill runtimes,
> but they do share a real Agent Skills standard core. This repository should
> target that shared core and treat platform-specific behavior as an optional
> extension layer.
