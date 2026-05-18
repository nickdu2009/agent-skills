# AGENTS.md Initialization Reference

Use this reference only when creating a new project-level `AGENTS.md`, or when an existing file is so thin that it needs a fresh structure.

## Content Checklist

Include these items when they are supported by repository evidence:

- **Project identity**: one or two sentences describing the repository's purpose, main language/framework, and primary entry points.
- **Repository map**: important directories and what agents should or should not edit, such as source, tests, generated files, docs, migrations, or vendored code.
- **Setup commands**: dependency installation and environment setup commands found in package manifests, lockfiles, Makefiles, scripts, or docs.
- **Build, test, lint, and format commands**: the smallest useful commands for common changes, plus any expensive full-suite commands and when to use them.
- **Coding conventions**: project-specific style, naming, architecture, dependency, typing, migration, or API compatibility rules.
- **Change safety rules**: generated-file handling, schema/data migration cautions, public contract rules, secret handling, and rules for preserving user changes.
- **Validation expectations**: what to run for documentation-only, single-file, multi-file, shared-interface, and installer/script changes.
- **Agent workflow guidance**: when to plan first, when to ask for clarification, when to use subagents, and any repo-specific skill routing.
- **Repository-derived best practices**: short rules implied by project signals such as version control, CI, package managers, migrations, or generated code.
- **Communication expectations**: how to report changed files, validation results, residual risk, and unverified assumptions.
- **Nested instruction policy**: how to handle deeper `AGENTS.md` files if the repository uses them.

Do not add a section when the repository has no evidence for it. Prefer a short confirmed file over a complete-looking file with guessed commands.

## Repository Signal Best Practices

Add these rules only when the signal exists in the target project. Keep each rule short and adapt it to the repository's actual tooling.

- **Version control present** (`.git`, `.jj`, or similar): tell agents to preserve unrelated user changes, inspect status before commit-related work, and avoid history rewriting unless explicitly requested. If the user asks for a commit, infer the message style from recent history and use a concise imperative summary, for example `fix auth timeout handling`.
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

Use only the sections that fit the project:

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

## Validation

- Smallest meaningful checks for common changes.
- Any expensive checks and when they are justified.

## Agent Guidance

- Skill, subagent, MCP, or tool-routing rules that are specific to this repo.

## Reporting

- How agents should summarize changes, validation, and residual risk.
```

## Evidence Rules

- A command is confirmed when it appears in package scripts, Makefiles, CI files, task runners, or docs.
- A directory rule is confirmed when the directory exists and its purpose is clear from names, docs, or config.
- A convention is confirmed when it appears repeatedly in source, tests, docs, or repo-level configuration.
- A workflow rule is confirmed when it comes from existing agent instructions, maintainer docs, or explicit user direction.

If evidence is weak, omit the claim or list it as a residual assumption in the final response instead of writing it into `AGENTS.md`.
