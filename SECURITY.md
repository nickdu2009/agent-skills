# Security Policy

## Scope

This repository contains portable Agent Skills packages under `skills/` plus repository-internal validation and evaluation tooling under `maintainer/`. Skill instructions and references are reviewable text; Python files under `maintainer/` are executable repository tooling. The repository intentionally contains no client installer, runtime mirror, discovery-path adapter, governance renderer, or Skill sidecar.

## Reporting a Vulnerability

If you discover a security issue in this repository, please report it by opening a GitHub issue or contacting the maintainer directly.

## Installation Safety

When importing Skills from any source:

- Review the complete package, including `SKILL.md` and every supporting file.
- Treat canonical `skills/<name>/` as this repository's only distributable source.
- Follow the target runtime's current Agent Skills import and discovery documentation; those behaviors are outside this repository.
- Do not execute repository-internal `maintainer/` tooling merely to use a Skill package.
- Preserve locally modified installed copies unless their replacement or removal is separately authorized.

## Supported Versions

| Version | Supported |
|---------|-----------|
| Current default branch / latest release | Yes |
| Historical snapshots | No |
