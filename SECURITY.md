# Security Policy

## Scope

This repository contains agent behavior skills (SKILL.md files) and supporting Python scripts. Skills are plain Markdown with YAML frontmatter and contain no executable code. The `scripts/` directory contains Python utilities for local development and testing.

## Reporting a Vulnerability

If you discover a security issue in this repository, please report it by opening a GitHub issue or contacting the maintainer directly.

For issues related to the OpenSkills CLI or installation toolchain, report to the [OpenSkills repository](https://github.com/numman-ali/openskills/issues).

## Installation Safety

When installing skills from any source:

- Review `scripts/` directory contents before running any Python scripts
- Use `npx openskills read <skill-name>` to inspect skill content before use
- Prefer installing from the canonical `skills/` directory rather than the repository root
- Verify that installed skills match the expected count and names using `npx openskills list`

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
