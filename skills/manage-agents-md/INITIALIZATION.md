# AGENTS.md Initialization Reference

Use this reference only when creating a new project-level `AGENTS.md`, or when an existing file is so thin that it needs a fresh structure.

## Project Scope Detection

Use only repository-visible evidence and explicit user instructions:

1. Identify the repository root.
2. Search from the target directory upward for an applicable `AGENTS.md`.
3. Check for nested `AGENTS.md` files below the target when their scope could overlap the requested change.
4. Decide whether the requested file is the root policy or a narrower nested supplement.

Do not inspect runtime-specific skill directories, settings, or user-level rule files. They are outside this skill's contract. If the project needs to remain portable, make the repository's `AGENTS.md` self-contained enough for its intended collaborators.

## Existing-Guidance-Aware Initialization

Before drafting, inspect applicable parent and target-level `AGENTS.md` sections. Do not recreate guidance already supplied by an applicable parent file. Write the smallest missing project supplement: repository map, concrete commands, local conventions, generated-file rules, migration notes, and validation commands unique to this repository.

## Content Checklist

Include these items when they are supported by repository evidence:

- **Project identity**: one or two sentences describing the repository's purpose, main language/framework, and primary entry points.
- **Repository map**: important directories and what agents should or should not edit, such as source, tests, generated files, docs, migrations, or vendored code.
- **Setup commands**: dependency installation and environment setup commands found in package manifests, lockfiles, Makefiles, scripts, or docs.
- **Build, test, lint, and format commands**: the smallest useful commands for common changes, plus any expensive full-suite commands and when to use them.
- **Coding conventions**: project-specific style, naming, architecture, dependency, typing, migration, or API compatibility rules.
- **Change safety rules**: generated-file handling, schema/data migration cautions, public contract rules, secret handling, and rules for preserving user changes.
- **Validation commands**: concrete local commands for documentation-only, single-file, multi-file, shared-interface, and installer/script changes.
- **Agent workflow additions**: only repository-specific skill or subagent routing that is not already covered by an applicable `AGENTS.md`.
- **Repository-derived best practices**: short rules implied by project signals such as version control, CI, package managers, migrations, or generated code.
- **Communication additions**: only repository-specific reporting expectations not already covered by applicable parent instructions.
- **Nested instruction policy**: how to handle deeper `AGENTS.md` files if the repository uses them.

Do not add a section when the repository has no evidence for it. Prefer a short confirmed file over a complete-looking file with guessed commands.

## Repository Signal Best Practices

Add these rules only when the signal exists in the target project and an applicable `AGENTS.md` does not already cover the same behavior. Keep each rule short and adapt it to the repository's actual tooling.

- **Version control present** (`.git`, `.jj`, or similar): if an applicable instruction already says to preserve unrelated user changes, do not repeat it. Add only project-specific commit guidance when repository history supports it.
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

Use this compact shape when an applicable parent `AGENTS.md` already provides generic agent behavior:

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

When there is no applicable parent guidance, it is acceptable to add short generic sections for validation, communication, and agent workflow. Keep them minimal and do not copy large policy blocks.

## Evidence Rules

- A command is confirmed when it appears in package scripts, Makefiles, CI files, task runners, or docs.
- A directory rule is confirmed when the directory exists and its purpose is clear from names, docs, or config.
- A convention is confirmed when it appears repeatedly in source, tests, docs, or repo-level configuration.
- A workflow rule is confirmed when it comes from existing agent instructions, maintainer docs, or explicit user direction.

If evidence is weak, omit the claim or list it as a residual assumption in the final response instead of writing it into `AGENTS.md`.
