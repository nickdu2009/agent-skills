#!/usr/bin/env python3
"""Validate the canonical skills tree against the Agent Skills specification."""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import yaml


ALLOWED_FRONTMATTER_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
FRONTMATTER_PATTERN = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)


def validate_skill(skill_dir: Path) -> list[str]:
    issues: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return [f"{skill_dir}: missing SKILL.md"]

    content = skill_file.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(content)
    if match is None:
        return [f"{skill_file}: missing or malformed YAML frontmatter"]

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"{skill_file}: invalid YAML frontmatter: {exc}"]
    if not isinstance(frontmatter, dict):
        return [f"{skill_file}: frontmatter must be a mapping"]

    unexpected = sorted(set(frontmatter) - ALLOWED_FRONTMATTER_FIELDS)
    if unexpected:
        issues.append(f"{skill_file}: unsupported frontmatter fields: {', '.join(unexpected)}")

    name = frontmatter.get("name")
    if not isinstance(name, str):
        issues.append(f"{skill_file}: name must be a non-empty string")
    else:
        normalized_name = unicodedata.normalize("NFKC", name.strip())
        if not normalized_name:
            issues.append(f"{skill_file}: name must be a non-empty string")
        else:
            if len(normalized_name) > 64:
                issues.append(f"{skill_file}: name exceeds 64 characters")
            if (
                normalized_name != normalized_name.lower()
                or any(character != "-" and not character.isalnum() for character in normalized_name)
                or normalized_name.startswith("-")
                or normalized_name.endswith("-")
                or "--" in normalized_name
            ):
                issues.append(
                    f"{skill_file}: name must use lowercase Unicode alphanumeric characters and single hyphens"
                )
            normalized_parent = unicodedata.normalize("NFKC", skill_dir.name)
            if normalized_name != normalized_parent:
                issues.append(f"{skill_file}: name {name!r} does not match parent directory {skill_dir.name!r}")

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        issues.append(f"{skill_file}: description must be a non-empty string")
    elif len(description) > 1024:
        issues.append(f"{skill_file}: description exceeds 1024 characters")

    license_value = frontmatter.get("license")
    if license_value is not None and (not isinstance(license_value, str) or not license_value):
        issues.append(f"{skill_file}: license must be a non-empty string when provided")

    compatibility = frontmatter.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str) or not compatibility:
            issues.append(f"{skill_file}: compatibility must be a non-empty string when provided")
        elif len(compatibility) > 500:
            issues.append(f"{skill_file}: compatibility exceeds 500 characters")

    metadata = frontmatter.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            issues.append(f"{skill_file}: metadata must be a mapping")
        elif any(not isinstance(key, str) or not isinstance(value, str) for key, value in metadata.items()):
            issues.append(f"{skill_file}: metadata keys and values must be strings")

    allowed_tools = frontmatter.get("allowed-tools")
    if allowed_tools is not None and (not isinstance(allowed_tools, str) or not allowed_tools):
        issues.append(f"{skill_file}: allowed-tools must be a non-empty space-separated string")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("skills"))
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"skills root does not exist: {root}")

    skill_dirs = sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and (path / "SKILL.md").is_file()
    )
    issues = [issue for skill_dir in skill_dirs for issue in validate_skill(skill_dir)]
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")
        return 1

    print(f"OK: {len(skill_dirs)} Agent Skills packages are specification-compliant")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
