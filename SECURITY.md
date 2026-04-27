# Security Policy

## Scope

This repository contains agent behavior skills (SKILL.md files) and supporting Python scripts. Skills are plain Markdown with YAML frontmatter and contain no executable code. The `maintainer/scripts/install/` directory contains install and mirror entrypoints, while `maintainer/` contains internal evaluation utilities, data, and retained reports.

## Reporting a Vulnerability

If you discover a security issue in this repository, please report it by opening a GitHub issue or contacting the maintainer directly.

## Installation Safety

When installing skills from any source:

- Review both the `maintainer/scripts/install/` entrypoints and any `maintainer/` utilities before running repository tooling
- Prefer the supported installer entrypoints in `maintainer/scripts/install/` over ad hoc copying
- Prefer the canonical `skills/` directory as the source of truth when auditing published skill content
- Verify generated installs or mirrors against the canonical source before use

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
