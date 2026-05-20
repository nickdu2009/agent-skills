# AGENTS.md Initialization Reference

Use this reference only when creating a new project-level `AGENTS.md`, or when an existing file is so thin that it needs a fresh structure.

## Supported Platform Detection

This skill only models user-level governance for currently supported agent platforms: Claude Code, Codex, and Cursor. Treat any other platform as unknown unless the user provides its rule location.

Use this detection order:

1. **Codex**
   - Check `${CODEX_HOME:-~/.codex}/AGENTS.md`.
   - If it exists and contains governance sections such as `Behavioral Guidelines`, `Skill Activation`, or `Validation Rules`, treat generic user-level governance as confirmed.

2. **Claude Code**
   - Check `~/.claude/CLAUDE.md`.
   - If it exists and contains governance sections such as `Behavioral Guidelines`, `Skill Activation`, or `Validation Rules`, treat generic user-level governance as confirmed.

3. **Cursor**
   - Check `~/.cursor/skills/` only to confirm installed skills.
   - Do **not** assume Cursor User Rules are readable or present from the file system. Cursor has no official user-level `AGENTS.md` target.
   - Treat generic Cursor user rules as confirmed only when the user explicitly says they are configured, or when the current system/developer context visibly contains equivalent user-level rules.

If generic user-level rules are confirmed for the active platform, initialize project `AGENTS.md` as a project supplement by default. Do not repeat generic behavioral rules, validation philosophy, communication rules, skill activation, or multi-agent protocol.

If generic user-level rules cannot be confirmed, ask whether the project should carry full team-shared governance or only project-specific instructions. Only include full generic governance when the user explicitly wants the repository to carry rules independent of any one user's setup.

When relying on user-level rules, mention the portability tradeoff in the final response: other users may need the same user-level setup or a project-level governance template.

## Template-Aware Initialization

Before drafting, check whether the project already has a governance template or managed project-level governance sections, such as `templates/governance/AGENTS-template.md`, `CLAUDE.md`, `.cursor/rules/`, or existing sections named:

- `Behavioral Guidelines`
- `Scope & Ownership`
- `Validation Rules`
- `Communication Rules`
- `Skill Activation`
- `Skill Lifecycle`
- `Skill Protocol`
- `Common Flow Patterns`
- `Multi-Agent Rules`

If those sections are already supplied by user-level rules or a project template, do not recreate them in the initialized `AGENTS.md`. Write only project-specific supplements: repository map, concrete commands, local conventions, generated-file rules, migration notes, and validation commands unique to this repository.

Use the governance template as the base when the user wants the standard governance behavior. Use this initialization reference only to fill project-specific gaps.

## Content Checklist

Include these items when they are supported by repository evidence:

- **Project identity**: one or two sentences describing the repository's purpose, main language/framework, and primary entry points.
- **Repository map**: important directories and what agents should or should not edit, such as source, tests, generated files, docs, migrations, or vendored code.
- **Setup commands**: dependency installation and environment setup commands found in package manifests, lockfiles, Makefiles, scripts, or docs.
- **Build, test, lint, and format commands**: the smallest useful commands for common changes, plus any expensive full-suite commands and when to use them.
- **Coding conventions**: project-specific style, naming, architecture, dependency, typing, migration, or API compatibility rules.
- **Change safety rules**: generated-file handling, schema/data migration cautions, public contract rules, secret handling, and rules for preserving user changes.
- **Validation commands**: concrete local commands for documentation-only, single-file, multi-file, shared-interface, and installer/script changes.
- **Agent workflow additions**: only repo-specific skill or subagent routing that is not already covered by a governance template.
- **Repository-derived best practices**: short rules implied by project signals such as version control, CI, package managers, migrations, or generated code.
- **Communication additions**: only repo-specific reporting expectations that are not already covered by a governance template.
- **Nested instruction policy**: how to handle deeper `AGENTS.md` files if the repository uses them.

Do not add a section when the repository has no evidence for it. Prefer a short confirmed file over a complete-looking file with guessed commands.

## Repository Signal Best Practices

Add these rules only when the signal exists in the target project and user-level or template governance does not already cover the same behavior. Keep each rule short and adapt it to the repository's actual tooling.

- **Version control present** (`.git`, `.jj`, or similar): if the template already says to preserve unrelated user changes, do not repeat it. Add only project-specific commit guidance, such as "infer message style from recent history" or "use a concise imperative summary like `fix auth timeout handling`" when the repository has commit history.
- **Commit hooks present** (`.pre-commit-config.yaml`, Husky config, Lefthook, Overcommit): tell agents not to skip hooks unless the user explicitly asks, and to treat hook-modified files as part of the change that must be reviewed.
- **CI present** (`.github/workflows`, `.gitlab-ci.yml`, Buildkite, CircleCI): list the local commands that best approximate required checks, and note when CI-only validation remains as residual risk.
- **Package manager detected** (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, lockfiles): record the canonical install command and prefer existing scripts over ad hoc commands.
- **Monorepo or workspace detected** (`pnpm-workspace.yaml`, Nx, Turborepo, Bazel, Pants, Cargo workspace): tell agents to run package-scoped checks first and avoid touching unrelated packages.
- **Container or dev environment files present** (`Dockerfile`, `compose.yaml`, `.devcontainer`): record when to use the containerized workflow instead of host-machine commands.
- **Environment templates present** (`.env.example`, config samples): tell agents never to commit secrets and to document required variables without inventing values.
- **Database migrations present** (`migrations/`, Prisma, Alembic, Rails db files): add rules to keep schema, migration, and generated client changes together, and to state rollback or compatibility risk.
- **Generated code present** (`generated/`, protobuf/OpenAPI clients, codegen scripts): tell agents not to hand-edit generated outputs unless the repo documents that as acceptable; prefer the generator command.
- **Docs site present** (`docs/`, Docusaurus, MkDocs, VitePress): add the local docs preview/build command when available and require link/path checks for doc-only changes.
- **Test fixtures or snapshots present** (`__snapshots__`, fixtures, golden files): tell agents to update them only when behavior intentionally changes and to mention why.

## Suggested Shape

Use this compact shape when user-level rules or the standard governance template already provide generic agent behavior:

```markdown
# AGENTS.md

## Project Overview

Short, durable description of what this repository is for.

## Repository Map

- `path/`: what lives here and any editing boundaries.

## Working Rules

- Repository-specific rules future agents must follow.
- Boundaries for generated files, vendored code, migrations, or public APIs.

## Build And Test

- `command`: when to use it and what it verifies.

## Project-Specific Rules

- Generated files, migrations, public API, data, or ownership rules specific to this repo.

## Project-Specific Validation

- Local commands and when to run them.
```

If no governance template is being used, it is acceptable to add short generic sections for validation, communication, and agent workflow. Keep them minimal and do not copy large policy blocks.

## Evidence Rules

- A command is confirmed when it appears in package scripts, Makefiles, CI files, task runners, or docs.
- A directory rule is confirmed when the directory exists and its purpose is clear from names, docs, or config.
- A convention is confirmed when it appears repeatedly in source, tests, docs, or repo-level configuration.
- A workflow rule is confirmed when it comes from existing agent instructions, maintainer docs, or explicit user direction.

If evidence is weak, omit the claim or list it as a residual assumption in the final response instead of writing it into `AGENTS.md`.
