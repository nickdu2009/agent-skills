#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
#   "pytest",
# ]
# ///
"""Unit tests for phase contract validators and shared helpers."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from _shared_phase_tools import Issue, load_plan, infer_phase, find_pr, find_wave, contract_map


# ---------------------------------------------------------------------------
# Issue class
# ---------------------------------------------------------------------------

class TestIssue:
    def test_render_minimal(self):
        issue = Issue("path.field", "something is wrong", None, "file.yaml:10")
        rendered = issue.render("ERROR")
        assert "ERROR path.field: something is wrong" in rendered
        assert "expected:" not in rendered
        assert "repair:" not in rendered
        assert "location: file.yaml:10" in rendered

    def test_render_full(self):
        issue = Issue("path.field", "bad value", "a valid value", "file.yaml:5", "fix it")
        rendered = issue.render("WARN")
        assert "WARN path.field: bad value" in rendered
        assert "expected: a valid value" in rendered
        assert "repair: fix it" in rendered
        assert "location: file.yaml:5" in rendered


# ---------------------------------------------------------------------------
# _shared_phase_tools helpers
# ---------------------------------------------------------------------------

class TestLoadPlan:
    def test_valid_yaml(self, tmp_path: Path):
        plan_file = tmp_path / "phase1-plan.yaml"
        plan_file.write_text(textwrap.dedent("""\
            schema_version: "2.0"
            prs:
              - id: P1-01
        """))
        data = load_plan(plan_file)
        assert data["schema_version"] == "2.0"
        assert data["prs"][0]["id"] == "P1-01"

    def test_non_mapping_raises(self, tmp_path: Path):
        plan_file = tmp_path / "phase1-plan.yaml"
        plan_file.write_text("- item1\n- item2\n")
        with pytest.raises(ValueError, match="mapping"):
            load_plan(plan_file)


class TestInferPhase:
    def test_from_phase_field(self):
        data = {"phase": "phase13"}
        assert infer_phase(Path("anything.yaml"), data) == "phase13"

    def test_from_stem(self):
        data: dict = {}
        assert infer_phase(Path("docs/phase13-plan.yaml"), data) == "phase13"

    def test_from_stem_no_plan_suffix(self):
        data: dict = {}
        assert infer_phase(Path("docs/phase13.yaml"), data) == "phase13"


class TestFindPr:
    def test_found(self):
        data = {"prs": [{"id": "P1-01", "title": "first"}, {"id": "P1-02", "title": "second"}]}
        assert find_pr(data, "P1-02")["title"] == "second"

    def test_not_found(self):
        data = {"prs": [{"id": "P1-01"}]}
        with pytest.raises(KeyError, match="P1-99"):
            find_pr(data, "P1-99")


class TestFindWave:
    def test_found(self):
        data = {"waves": [{"id": 1, "label": "first"}, {"id": 2, "label": "second"}]}
        assert find_wave(data, 2)["label"] == "second"

    def test_not_found(self):
        data = {"waves": [{"id": 1}]}
        with pytest.raises(KeyError, match="99"):
            find_wave(data, 99)


class TestContractMap:
    def test_builds_map(self):
        data = {"external_contracts": [
            {"id": "c1", "kind": "openapi"},
            {"id": "c2", "kind": "proto"},
        ]}
        result = contract_map(data)
        assert set(result.keys()) == {"c1", "c2"}

    def test_empty(self):
        assert contract_map({}) == {}

    def test_skips_non_dict(self):
        data = {"external_contracts": ["bad", {"id": "c1", "kind": "openapi"}]}
        result = contract_map(data)
        assert "c1" in result
        assert len(result) == 1


# ---------------------------------------------------------------------------
# validate_phase_execution_schema — negative cases
# ---------------------------------------------------------------------------

def _run_validator(plan_path: Path) -> tuple[int, str]:
    """Run the schema validator and return (returncode, combined output)."""
    import subprocess
    scripts_dir = Path(__file__).resolve().parent
    proc = subprocess.run(
        ["uv", "run", "scripts/validate_phase_execution_schema.py", "--plan", str(plan_path)],
        cwd=scripts_dir.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestSchemaValidationNegative:
    def test_missing_required_top_level(self, tmp_path: Path):
        plan = tmp_path / "plan.yaml"
        plan.write_text(yaml.dump({"schema_version": "2.0"}))
        rc, out = _run_validator(plan)
        assert rc != 0
        assert "status" in out or "scope" in out

    def test_empty_prs(self, tmp_path: Path):
        plan = tmp_path / "plan.yaml"
        plan.write_text(yaml.dump({
            "schema_version": "2.0", "last_updated": "2026-01-01", "status": "proposed",
            "scope": "test", "hard_rules": [], "schema_conventions": {},
            "placeholder_conventions": {}, "validation_profiles": {},
            "team": [{"id": "t1", "name": "team1"}],
            "hotspots": [], "prs": "not_a_list", "waves": [],
        }))
        rc, out = _run_validator(plan)
        assert rc != 0

    def test_pr_missing_required_field(self, tmp_path: Path):
        plan = tmp_path / "plan.yaml"
        plan.write_text(yaml.dump({
            "schema_version": "2.0", "last_updated": "2026-01-01", "status": "proposed",
            "scope": "test", "hard_rules": [], "schema_conventions": {},
            "placeholder_conventions": {}, "validation_profiles": {},
            "team": [{"id": "t1", "name": "team1"}],
            "hotspots": [],
            "prs": [{"id": "P1-01", "title": "only id and title"}],
            "waves": [],
        }))
        rc, out = _run_validator(plan)
        assert rc != 0
        assert "owner" in out or "wave" in out or "goal" in out

    def test_owner_not_in_team(self, tmp_path: Path):
        plan = tmp_path / "plan.yaml"
        plan.write_text(yaml.dump({
            "schema_version": "2.0", "last_updated": "2026-01-01", "status": "proposed",
            "scope": "test", "hard_rules": [], "schema_conventions": {},
            "placeholder_conventions": {}, "validation_profiles": {},
            "team": [{"id": "t1", "name": "team1"}],
            "hotspots": [],
            "prs": [{"id": "P1-01", "title": "t", "milestone": "m", "type": "implementation",
                      "owner": "unknown_team", "wave": 1, "depends_on": [],
                      "goal": "g", "read_first": [], "start_condition": {"gate": "immediate"},
                      "scope": {"allow": [], "deny": []}, "files": [],
                      "expected_changes": [], "guardrails": [], "non_goals": [],
                      "validation": [], "done_when": []}],
            "waves": [{"id": 1, "label": "w1", "goal": "g", "control_pr": "P1-01",
                        "prs": ["P1-01"], "merge_order": [["P1-01"]], "lane_setup": [],
                        "constraints": [], "integrator_checklist": []}],
        }))
        rc, out = _run_validator(plan)
        assert rc != 0
        assert "unknown_team" in out or "team" in out


# ---------------------------------------------------------------------------
# validate_phase_doc_set — negative cases
# ---------------------------------------------------------------------------

def _run_doc_set_validator(docs_dir: Path, phase: str) -> tuple[int, str]:
    """Run the doc-set validator and return (returncode, combined output)."""
    import subprocess
    scripts_dir = Path(__file__).resolve().parent
    proc = subprocess.run(
        ["uv", "run", "scripts/validate_phase_doc_set.py",
         "--docs-dir", str(docs_dir), "--phase", phase],
        cwd=scripts_dir.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestDocSetValidationNegative:
    def test_missing_required_doc(self, tmp_path: Path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "phase1-plan.yaml").write_text("schema_version: '2.0'")
        rc, out = _run_doc_set_validator(docs, "phase1")
        assert rc != 0
        assert "missing" in out.lower()

    def test_extra_phase_file(self, tmp_path: Path):
        docs = tmp_path / "docs"
        docs.mkdir()
        for name in ("phase1-roadmap.md", "phase1-plan.yaml",
                      "phase1-wave-guide.md", "phase1-execution-index.md",
                      "phase1-pr-delivery-plan.md"):
            (docs / name).write_text("placeholder\n")
        (docs / "phase1-plan.yaml").write_text(yaml.dump({
            "schema_version": "2.0", "prs": [], "waves": [],
        }))
        rc, out = _run_doc_set_validator(docs, "phase1")
        assert rc != 0
        assert "extra" in out.lower() or "pr-delivery-plan" in out


# ---------------------------------------------------------------------------
# Smoke fixture positive validation (unit-level)
# ---------------------------------------------------------------------------

class TestSmokeFixture:
    @pytest.fixture
    def fixture_dir(self) -> Path:
        return Path(__file__).resolve().parents[1] / "fixtures" / "smoke" / "docs"

    def test_schema_validator_passes(self, fixture_dir: Path):
        rc, out = _run_validator(fixture_dir / "smoke-plan.yaml")
        assert rc == 0, f"Schema validation failed:\n{out}"

    def test_doc_set_validator_passes(self, fixture_dir: Path):
        rc, out = _run_doc_set_validator(fixture_dir, "smoke")
        assert rc == 0, f"Doc-set validation failed:\n{out}"
