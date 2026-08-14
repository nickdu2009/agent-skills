#!/usr/bin/env python3
"""Self-tests for standards-compliant Skill frontmatter and index parity."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR / "analysis"))
sys.path.insert(0, str(SCRIPT_DIR))

import generate_skill_index as generator
import run_trigger_tests as trigger_runner
import validate_agent_skills as validator


REPO_ROOT = Path(__file__).resolve().parents[3]
OFFICIAL_SKILLS_REF_SHA = "69ef37e9424c0a7ea9dd2293b559e43ec8176379"
EXPECTED_SKILLS_REF_CONSTRAINTS = [
    "hatchling==1.27.0",
    "packaging==25.0",
    "pathspec==0.12.1",
    "pluggy==1.6.0",
    "trove-classifiers==2025.5.9.12",
    "click==8.3.1",
    "strictyaml==1.7.3",
    "python-dateutil==2.9.0.post0",
    "six==1.17.0",
]


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_root = Path(temp_dir) / "skills"
        skill_dir = skills_root / "block-scalar-demo"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            """---
name: block-scalar-demo
description: >-
  Do the thing.
  Use when asked.
metadata:
  version: "1"
---
# Block scalar demo
""",
            encoding="utf-8",
        )

        assert validator.validate_skill(skill_dir) == []
        frontmatter = generator.extract_frontmatter(skill_file)
        expected = "Do the thing. Use when asked."
        assert frontmatter["description"] == expected, frontmatter

        original_skills_dir = trigger_runner.SKILLS_DIR
        original_data_dir = trigger_runner.DATA_DIR
        catalog_dir = Path(temp_dir) / "data"
        catalog_dir.mkdir()
        (catalog_dir / "skill_catalog.json").write_text(
            json.dumps({
                "core_skill_names": ["block-scalar-demo"],
                "optional_skill_names": [],
            }),
            encoding="utf-8",
        )
        trigger_runner.SKILLS_DIR = skills_root
        trigger_runner.DATA_DIR = catalog_dir
        try:
            descriptions = trigger_runner.extract_descriptions()
        finally:
            trigger_runner.SKILLS_DIR = original_skills_dir
            trigger_runner.DATA_DIR = original_data_dir
        assert descriptions == {"block-scalar-demo": expected}, descriptions
        generator.SKILL_FAMILY["block-scalar-demo"] = "execution"
        try:
            fixture_index = generator.generate_skill_index(
                skills_root,
                catalog_path=catalog_dir / "skill_catalog.json",
            )
        finally:
            del generator.SKILL_FAMILY["block-scalar-demo"]
        assert fixture_index["skills"][0]["description"] == expected, fixture_index

    with tempfile.TemporaryDirectory() as temp_dir:
        skills_root = Path(temp_dir) / "skills"

        unicode_skill_dir = skills_root / "ffi-分析"
        unicode_skill_dir.mkdir(parents=True)
        (unicode_skill_dir / "SKILL.md").write_text(
            """---
name: ﬃ-分析
description: Valid Unicode skill name.
---
""",
            encoding="utf-8",
        )
        assert validator.validate_skill(unicode_skill_dir) == []

        blank_name_dir = skills_root / "blank-name"
        blank_name_dir.mkdir()
        (blank_name_dir / "SKILL.md").write_text(
            """---
name: "   "
description: Valid description.
---
""",
            encoding="utf-8",
        )
        blank_name_issues = validator.validate_skill(blank_name_dir)
        assert any("name must be a non-empty string" in issue for issue in blank_name_issues), blank_name_issues

        blank_description_dir = skills_root / "blank-description"
        blank_description_dir.mkdir()
        (blank_description_dir / "SKILL.md").write_text(
            """---
name: blank-description
description: "   "
---
""",
            encoding="utf-8",
        )
        blank_description_issues = validator.validate_skill(blank_description_dir)
        assert any(
            "description must be a non-empty string" in issue for issue in blank_description_issues
        ), blank_description_issues

    generated = generator.generate_skill_index(generator.SKILLS_DIR)
    assert generated["schema_version"] == "0.2.0", generated
    assert "generated_at" not in generated, generated
    assert len(generated["source_digest"]) == 64, generated
    assert generated == generator.generate_skill_index(generator.SKILLS_DIR), generated
    checked_in = json.loads(generator.DEFAULT_OUTPUT.read_text(encoding="utf-8"))
    assert checked_in == generated, "checked-in compact index is stale"
    assert {
        item["name"]: item["description"] for item in generated["skills"]
    } == trigger_runner.load_skill_index(), "canonical metadata differs from compact index"
    metadata_schema = yaml.safe_load(
        (REPO_ROOT / "maintainer/data/skill_metadata_schema.yaml").read_text(encoding="utf-8")
    )
    assert metadata_schema["version"] == "0.2.0", metadata_schema
    index_fields = metadata_schema["schema"]["skill_index"]
    assert index_fields["schema_version"]["required"] is True
    assert index_fields["source_digest"]["required"] is True
    assert index_fields["source_digest"]["pattern"] == "^[0-9a-f]{64}$"
    assert "generated_at" not in index_fields

    with tempfile.TemporaryDirectory() as temp_dir:
        bad_catalog = Path(temp_dir) / "catalog.json"
        bad_catalog.write_text(
            json.dumps({
                "core_skill_names": ["architecture-design"],
                "optional_skill_names": [],
            }),
            encoding="utf-8",
        )
        unknown_mapping = copy.deepcopy(generator.SKILL_FAMILY)
        generator.SKILL_FAMILY.clear()
        try:
            try:
                generator.generate_skill_index(generator.SKILLS_DIR, catalog_path=bad_catalog)
            except ValueError as exc:
                assert "unknown Skill family" in str(exc), exc
            else:
                raise AssertionError("index generator accepted an unknown Skill family")
        finally:
            generator.SKILL_FAMILY.update(unknown_mapping)

    original_data_dir = trigger_runner.DATA_DIR
    with tempfile.TemporaryDirectory() as temp_dir:
        trigger_runner.DATA_DIR = Path(temp_dir)
        try:
            try:
                trigger_runner.load_skill_index(strict=True)
            except RuntimeError:
                pass
            else:
                raise AssertionError("strict index loading accepted a missing index")
        finally:
            trigger_runner.DATA_DIR = original_data_dir

    constraints = (
        REPO_ROOT / "maintainer/data/skills_ref_constraints.txt"
    ).read_text(encoding="utf-8").splitlines()
    assert constraints == EXPECTED_SKILLS_REF_CONSTRAINTS, constraints
    ci_text = (REPO_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    token_ci_text = (
        REPO_ROOT / ".github/workflows/token-efficiency-check.yml"
    ).read_text(encoding="utf-8")
    yaml.safe_load(ci_text)
    yaml.safe_load(token_ci_text)
    workflows = ci_text + "\n" + token_ci_text
    assert "pip install --upgrade" not in workflows
    assert "pip install -U" not in workflows
    assert ci_text.count("-c maintainer/data/token_tooling_constraints.txt") == 2
    assert token_ci_text.count("-c maintainer/data/token_tooling_constraints.txt") == 1
    assert "-c maintainer/data/skills_ref_constraints.txt" in ci_text
    assert "--no-build-isolation --no-deps" in ci_text
    assert (
        "skills-ref @ git+https://github.com/agentskills/agentskills.git@"
        f"{OFFICIAL_SKILLS_REF_SHA}#subdirectory=skills-ref"
    ) in ci_text
    assert (
        "test \"$(skills-ref --version)\" = 'skills-ref, version 0.1.0'"
        in ci_text
    )
    assert "validate_skill_catalog.py" in ci_text
    assert "--print-all-skills > /tmp/agent-skills-catalog.txt" in ci_text
    assert "LC_ALL=C sort -c /tmp/agent-skills-catalog.txt" in ci_text
    assert "skill_count=$(wc -l < /tmp/agent-skills-catalog.txt)" in ci_text
    assert '"$skill_count" -ne 12' in ci_text
    assert 'skills-ref validate "skills/$skill"' in ci_text
    assert "done < /tmp/agent-skills-catalog.txt" in ci_text
    assert "run_artifact_routing_tests.py" in ci_text
    assert "--mode report --fail-on-contract-issues" in ci_text
    print("OK: Agent Skills YAML parsing and compact-index parity passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
