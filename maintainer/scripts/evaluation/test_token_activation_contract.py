#!/usr/bin/env python3
"""Self-tests for reproducible token identity and activation scenarios."""

from __future__ import annotations

import copy
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent / "analysis"))

import measure_prompt_surface as measurement


REPO_ROOT = Path(__file__).resolve().parents[3]
EXPECTED_IDENTITY = {
    "measurement_contract_version": "1.0",
    "token_counter": "tiktoken",
    "counter_version": "0.13.0",
    "tokenizer": "o200k_base",
}
EXPECTED_REFERENCE_MANIFEST = {
    "path": "references/manifest.yaml",
    "schema_version": "1.0",
    "load_modes": ["always", "conditional", "optional-runtime", "authoring-only"],
}
EXPECTED_BUDGETS = {
    "release": {
        "full_discovery_metadata": 1300,
        "core_discovery_metadata": 1150,
        "artifact_review_metadata": 160,
        "all_skill_main": 29000,
        "typical_activation": 3000,
        "heavy_activation": 5000,
        "worst_runtime_activation": 5000,
        "all_package_text": 35000,
        "repository_governance": 3608,
    },
    "engineering": {
        "full_discovery_metadata": 1275,
        "core_discovery_metadata": 1125,
        "artifact_review_metadata": 160,
        "repository_governance": 3500,
    },
}
EXPECTED_SKILL_FILE_BUDGETS = {
    "requirement-interview": {
        "main_min": 2350,
        "main_max": 2500,
        "references/requirement-types.md": 450,
        "references/examples.md": 450,
        "typical_activation_max": 2950,
        "worst_runtime_max": 3400,
    },
    "design-before-plan": {
        "main_min": 1900,
        "main_max": 2100,
        "references/design-brief-format.md": 400,
        "references/adr-format.md": 250,
        "references/nfr-checks.md": 400,
        "references/data-migration-checks.md": 350,
        "references/examples.md": 300,
        "worst_runtime_max": 3800,
    },
    "architecture-design": {
        "main_min": 2050,
        "main_max": 2200,
        "references/architecture-template.md": 550,
        "references/adr-format.md": 250,
        "references/principles.md": 400,
        "references/examples.md": 200,
        "worst_runtime_max": 3600,
    },
    "implementation-planning": {
        "main_min": 2000,
        "main_max": 2150,
        "references/plan-template.md": 800,
        "references/upstream-artifacts.md": 350,
        "references/gate-00.md": 250,
        "references/delegation-task-card.md": 200,
        "references/examples.md": 300,
        "worst_runtime_max": 4050,
    },
    "artifact-review-loop": {
        "main_min": 1400,
        "main_max": 1800,
        "runtime_references_total_max": 2750,
        "single_object_activation_max": 2350,
        "mixed_activation_max": 4550,
        "worst_runtime_max": 4550,
    },
}
EXPECTED_REFERENCE_CONTRACTS = {
    "requirement-interview": [
        {"path": "references/requirement-types.md", "load_mode": "conditional", "condition_id": "requirement-type-calibration"},
        {"path": "references/examples.md", "load_mode": "optional-runtime", "condition_id": "example-calibration"},
    ],
    "design-before-plan": [
        {"path": "references/design-brief-format.md", "load_mode": "always", "condition_id": "activation"},
        {"path": "references/adr-format.md", "load_mode": "conditional", "condition_id": "adr-candidate"},
        {"path": "references/nfr-checks.md", "load_mode": "conditional", "condition_id": "nfr-design"},
        {"path": "references/data-migration-checks.md", "load_mode": "conditional", "condition_id": "data-migration"},
        {"path": "references/examples.md", "load_mode": "optional-runtime", "condition_id": "example-calibration"},
    ],
    "architecture-design": [
        {"path": "references/architecture-template.md", "load_mode": "always", "condition_id": "activation"},
        {"path": "references/adr-format.md", "load_mode": "conditional", "condition_id": "adr-candidate"},
        {"path": "references/principles.md", "load_mode": "conditional", "condition_id": "architecture-principles"},
        {"path": "references/examples.md", "load_mode": "optional-runtime", "condition_id": "example-calibration"},
    ],
    "implementation-planning": [
        {"path": "references/plan-template.md", "load_mode": "always", "condition_id": "activation"},
        {"path": "references/upstream-artifacts.md", "load_mode": "conditional", "condition_id": "adr-alignment"},
        {"path": "references/gate-00.md", "load_mode": "conditional", "condition_id": "pre-coding-gate"},
        {"path": "references/delegation-task-card.md", "load_mode": "conditional", "condition_id": "delegated-planning"},
        {"path": "references/examples.md", "load_mode": "optional-runtime", "condition_id": "example-calibration"},
    ],
    "artifact-review-loop": [
        {"path": "references/requirements.md", "load_mode": "conditional", "condition_id": "review-requirements"},
        {"path": "references/design.md", "load_mode": "conditional", "condition_id": "review-design"},
        {"path": "references/plan.md", "load_mode": "conditional", "condition_id": "review-plan"},
        {"path": "references/code.md", "load_mode": "conditional", "condition_id": "review-code"},
        {"path": "references/tests.md", "load_mode": "conditional", "condition_id": "review-tests"},
    ],
    "manage-agents-md": [
        {"path": "INITIALIZATION.md", "load_mode": "conditional", "condition_id": "initialization"},
    ],
}
EXPECTED_TOKEN_TOOLING_CONSTRAINTS = ["tiktoken==0.13.0", "PyYAML==6.0.3"]


EXPECTED_SCENARIOS = {
    "token-requirement-interview-type-questions-typical": ("requirement-interview", "typical", ("references/requirement-types.md",)),
    "token-requirement-interview-max-heavy": ("requirement-interview", "heavy", ("references/requirement-types.md", "references/examples.md")),
    "token-design-before-plan-base-typical": ("design-before-plan", "typical", ()),
    "token-design-before-plan-adr-typical": ("design-before-plan", "typical", ("references/adr-format.md",)),
    "token-design-before-plan-nfr-typical": ("design-before-plan", "typical", ("references/nfr-checks.md",)),
    "token-design-before-plan-data-migration-typical": ("design-before-plan", "typical", ("references/data-migration-checks.md",)),
    "token-design-before-plan-example-typical": ("design-before-plan", "typical", ("references/examples.md",)),
    "token-design-before-plan-max-heavy": ("design-before-plan", "heavy", ("references/adr-format.md", "references/nfr-checks.md", "references/data-migration-checks.md", "references/examples.md")),
    "token-architecture-design-base-typical": ("architecture-design", "typical", ()),
    "token-architecture-design-adr-typical": ("architecture-design", "typical", ("references/adr-format.md",)),
    "token-architecture-design-example-typical": ("architecture-design", "typical", ("references/examples.md",)),
    "token-architecture-design-principles-heavy": ("architecture-design", "heavy", ("references/principles.md",)),
    "token-architecture-design-max-heavy": ("architecture-design", "heavy", ("references/adr-format.md", "references/principles.md", "references/examples.md")),
    "token-implementation-planning-base-typical": ("implementation-planning", "typical", ()),
    "token-implementation-planning-accepted-adr-heavy": ("implementation-planning", "heavy", ("references/upstream-artifacts.md",)),
    "token-implementation-planning-gate-heavy": ("implementation-planning", "heavy", ("references/gate-00.md",)),
    "token-implementation-planning-delegation-heavy": ("implementation-planning", "heavy", ("references/delegation-task-card.md",)),
    "token-implementation-planning-example-heavy": ("implementation-planning", "heavy", ("references/examples.md",)),
    "token-implementation-planning-max-heavy": ("implementation-planning", "heavy", ("references/upstream-artifacts.md", "references/gate-00.md", "references/delegation-task-card.md", "references/examples.md")),
    "token-artifact-review-requirements-primary-typical": ("artifact-review-loop", "typical", ("references/requirements.md",)),
    "token-artifact-review-design-primary-typical": ("artifact-review-loop", "typical", ("references/design.md",)),
    "token-artifact-review-plan-primary-typical": ("artifact-review-loop", "typical", ("references/plan.md",)),
    "token-artifact-review-code-primary-typical": ("artifact-review-loop", "typical", ("references/code.md",)),
    "token-artifact-review-tests-primary-typical": ("artifact-review-loop", "typical", ("references/tests.md",)),
    "token-artifact-review-self-delivery-typical": ("artifact-review-loop", "typical", ("references/code.md",)),
    "token-artifact-review-mixed-heavy": ("artifact-review-loop", "heavy", ("references/requirements.md", "references/design.md", "references/plan.md", "references/code.md", "references/tests.md")),
    "token-scoped-tasking-base-typical": ("scoped-tasking", "typical", ()),
    "token-bugfix-workflow-base-typical": ("bugfix-workflow", "typical", ()),
    "token-safe-refactor-base-typical": ("safe-refactor", "typical", ()),
    "token-impact-analysis-base-typical": ("impact-analysis", "typical", ()),
    "token-targeted-validation-base-typical": ("targeted-validation", "typical", ()),
    "token-multi-agent-protocol-base-typical": ("multi-agent-protocol", "typical", ()),
    "token-manage-agents-init-typical": ("manage-agents-md", "typical", ("INITIALIZATION.md",)),
}


def write_fixture(skills_root: Path, contract: dict) -> None:
    core, optional = measurement._catalog_skill_sets()
    for skill_name in [*core, *optional]:
        skill_dir = skills_root / skill_name
        skill_dir.mkdir(parents=True)
        references = contract["reference_contracts"].get(skill_name, [])
        links = "\n".join(f"[{item['condition_id']}]({item['path']})" for item in references)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {skill_name}\ndescription: Fixture.\n---\n# Fixture\n{links}\n",
            encoding="utf-8",
        )
        if references:
            manifest_path = skill_dir / contract["reference_manifest"]["path"]
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                yaml.safe_dump(
                    {
                        "schema_version": "1.0",
                        "references": references,
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            for item in references:
                target = skill_dir / item["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(f"# {item['condition_id']}\nFixture content.\n", encoding="utf-8")


def main() -> int:
    measurement.verify_counter_runtime()
    contract = measurement.load_activation_contract()
    assert measurement.measurement_identity() == EXPECTED_IDENTITY
    assert {key: contract[key] for key in EXPECTED_IDENTITY} == EXPECTED_IDENTITY
    assert contract["reference_manifest"] == EXPECTED_REFERENCE_MANIFEST
    assert contract["budgets"] == EXPECTED_BUDGETS
    assert contract["skill_file_budgets"] == EXPECTED_SKILL_FILE_BUDGETS
    assert contract["reference_contracts"] == EXPECTED_REFERENCE_CONTRACTS
    assert (
        REPO_ROOT / "maintainer/data/token_tooling_constraints.txt"
    ).read_text(encoding="utf-8").splitlines() == EXPECTED_TOKEN_TOOLING_CONSTRAINTS
    actual_scenarios = {
        item["id"]: (item["skill"], item["class"], tuple(item["references"]))
        for item in contract["scenarios"]
    }
    assert actual_scenarios == EXPECTED_SCENARIOS, (
        sorted(EXPECTED_SCENARIOS.keys() - actual_scenarios.keys()),
        sorted(actual_scenarios.keys() - EXPECTED_SCENARIOS.keys()),
    )
    assert {
        item["skill"] for item in contract["scenarios"] if item.get("max_runtime") is True
    } == {
        "requirement-interview",
        "design-before-plan",
        "architecture-design",
        "implementation-planning",
        "artifact-review-loop",
    }

    fixture_contract = copy.deepcopy(contract)
    fixture_contract["budgets"]["release"].update({
        "typical_activation": 100000,
        "heavy_activation": 100000,
        "worst_runtime_activation": 100000,
    })
    fixture_contract["skill_file_budgets"] = {
        name: {"worst_runtime_max": 100000}
        for name in (
            "requirement-interview",
            "design-before-plan",
            "architecture-design",
            "implementation-planning",
            "artifact-review-loop",
        )
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_root = Path(temp_dir) / "skills"
        write_fixture(skills_root, fixture_contract)
        result = measurement.measure_activation_contract(skills_root, fixture_contract)
        assert result["validation_issues"] == [], result
        assert len(result["scenarios"]) == len(EXPECTED_SCENARIOS)

        manifest = skills_root / "design-before-plan/references/manifest.yaml"
        raw = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        raw["references"][0]["load_mode"] = "authoring-only"
        manifest.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
        authoring_result = measurement.measure_activation_contract(skills_root, fixture_contract)
        assert any("authoring-only reference is runtime-reachable" in issue for issue in authoring_result["validation_issues"]), authoring_result

    with tempfile.TemporaryDirectory() as temp_dir:
        bad_contract = Path(temp_dir) / "contract.json"
        value = copy.deepcopy(contract)
        value["counter_version"] = "999.0"
        bad_contract.write_text(json.dumps(value), encoding="utf-8")
        try:
            measurement.load_activation_contract(bad_contract)
        except measurement.ContractError:
            pass
        else:
            raise AssertionError("counter identity mismatch was accepted")

    original_argv = sys.argv
    original_contract_path = measurement.ACTIVATION_CONTRACT_PATH
    with tempfile.TemporaryDirectory() as temp_dir:
        bad_contract = Path(temp_dir) / "contract.json"
        bad_contract.write_text("{}\n", encoding="utf-8")
        sys.argv = [
            "measure_prompt_surface.py",
            "--actual-tokens",
            "--contract",
            str(bad_contract),
        ]
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                assert measurement.main() == 2
        finally:
            sys.argv = original_argv
            measurement.ACTIVATION_CONTRACT_PATH = original_contract_path

    with tempfile.TemporaryDirectory() as temp_dir:
        missing_contract = Path(temp_dir) / "missing-contract.json"
        sys.argv = [
            "measure_prompt_surface.py",
            "--actual-tokens",
            "--contract",
            str(missing_contract),
        ]
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                assert measurement.main() == 2
        finally:
            sys.argv = original_argv

    with tempfile.TemporaryDirectory() as temp_dir:
        budget_contract = Path(temp_dir) / "budget-contract.json"
        value = copy.deepcopy(contract)
        value["budgets"]["release"]["full_discovery_metadata"] = 0
        budget_contract.write_text(json.dumps(value), encoding="utf-8")
        sys.argv = [
            "measure_prompt_surface.py",
            "--actual-tokens",
            "--contract",
            str(budget_contract),
            "--fail-on-budget",
            "--json",
        ]
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                assert measurement.main() == 1
        finally:
            sys.argv = original_argv

    print("OK: token identity, mandatory scenarios, manifests, and runtime reachability passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
