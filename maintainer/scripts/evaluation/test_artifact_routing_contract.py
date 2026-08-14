#!/usr/bin/env python3
"""Self-tests for unified artifact routing and revision authority."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

from run_artifact_routing_tests import (
    ROUTE_RESPONSE_FIELDS,
    build_argument_parser,
    build_messages,
    expected_route,
    render_prompts,
    render_report,
    score_result,
)
from artifact_review_test_data import (
    ARTIFACT_ROUTING_CASES,
    ARTIFACT_SUBTYPES,
    ARTIFACT_TYPES,
    ReviewProvenance,
    resolve_review_authorization,
    self_delivery_truth_table,
    validate_artifact_routing_cases,
)
from trigger_test_data import ALL_TRIGGER_CASES


REPO_ROOT = Path(__file__).resolve().parents[3]
FINAL_SKILLS = frozenset(
    {
        "artifact-review-loop",
        "architecture-design",
        "bugfix-workflow",
        "design-before-plan",
        "impact-analysis",
        "implementation-planning",
        "manage-agents-md",
        "multi-agent-protocol",
        "requirement-interview",
        "safe-refactor",
        "scoped-tasking",
        "targeted-validation",
    }
)


def assert_fixture_contract() -> None:
    assert not validate_artifact_routing_cases()
    assert {case.artifact_type for case in ARTIFACT_ROUTING_CASES if case.expected_trigger} == set(
        ARTIFACT_TYPES
    )
    covered_subtypes = {
        artifact_type: {
            case.artifact_subtype
            for case in ARTIFACT_ROUTING_CASES
            if case.artifact_type == artifact_type
        }
        for artifact_type in ARTIFACT_TYPES
    }
    for artifact_type, subtypes in ARTIFACT_SUBTYPES.items():
        assert set(subtypes) <= covered_subtypes[artifact_type], (
            artifact_type,
            sorted(set(subtypes) - covered_subtypes[artifact_type]),
        )
    mixed = next(case for case in ARTIFACT_ROUTING_CASES if case.id == "route-mixed-code-tests")
    assert mixed.artifact_type == "code"
    assert mixed.secondary_types == ("tests",)


def assert_provenance_contract() -> None:
    rows = self_delivery_truth_table()
    for origin, write_authorized, current_target, _explicit, is_self in rows:
        assert is_self == (
            origin == "current-agent-task" and write_authorized and current_target
        )

    for case_id in ("route-first-person-diff", "route-first-person-multifile"):
        case = next(case for case in ARTIFACT_ROUTING_CASES if case.id == case_id)
        assert case.provenance.artifact_origin == "user-or-external"
        assert case.expected_review_context == "requested"
        assert case.expected_mode == "review-only"
        assert case.expected_authorization_source == "none"
        assert case.expected_write_scope == "none"

    for artifact_type in ARTIFACT_TYPES:
        route = resolve_review_authorization(
            artifact_type,
            ReviewProvenance(
                artifact_origin="user-or-external",
                current_task_write_authorized=False,
                target_is_current_task_diff=False,
                explicit_revision_requested=True,
            ),
        )
        assert route.review_context == "requested"
        assert route.mode == "review-and-revise"
        assert route.authorization_source == "explicit-user-request"
        expected_scope = (
            "reviewed-implementation"
            if artifact_type == "code"
            else "reviewed-artifact"
        )
        assert route.write_scope == expected_scope


def assert_trigger_fixture_contract() -> None:
    ids = [case.id for case in ALL_TRIGGER_CASES]
    assert len(ids) == len(set(ids))
    positive = {
        skill
        for case in ALL_TRIGGER_CASES
        for skill in case.expected_triggers
    }
    referenced = {
        skill
        for case in ALL_TRIGGER_CASES
        for skill in (*case.expected_triggers, *case.expected_non_triggers)
    }
    assert referenced <= FINAL_SKILLS, sorted(referenced - FINAL_SKILLS)
    assert FINAL_SKILLS <= positive, sorted(FINAL_SKILLS - positive)

    matrix = json.loads(
        (REPO_ROOT / "maintainer" / "data" / "review_skill_migration_matrix.json").read_text(
            encoding="utf-8"
        )
    )
    retired = tuple(matrix["retired_skill_names"])
    for case in ALL_TRIGGER_CASES:
        assert not any(name in case.notes for name in retired), case.id


def assert_runner_contract() -> None:
    args = build_argument_parser().parse_args(["--fail-on-contract-issues"])
    assert args.fail_on_contract_issues is True
    args = build_argument_parser().parse_args([])
    assert args.fail_on_contract_issues is False
    report_one = render_report(ARTIFACT_ROUTING_CASES)
    report_two = render_report(ARTIFACT_ROUTING_CASES)
    assert report_one == report_two
    parsed_report = json.loads(report_one)
    assert parsed_report["contract_version"] == "1.0"
    assert parsed_report["case_count"] == len(ARTIFACT_ROUTING_CASES)
    assert [case["id"] for case in parsed_report["cases"]] == sorted(
        case.id for case in ARTIFACT_ROUTING_CASES
    )

    prompts = render_prompts(ARTIFACT_ROUTING_CASES)
    assert prompts == render_prompts(ARTIFACT_ROUTING_CASES)
    parsed_prompts = json.loads(prompts)
    assert parsed_prompts["temperature"] == 0
    assert "expected" not in prompts
    first = ARTIFACT_ROUTING_CASES[0]
    messages = build_messages(first)
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    for field in (
        "artifact_origin",
        "current_task_write_authorized",
        "target_is_current_task_diff",
        "explicit_revision_requested",
    ):
        assert field in messages[1]["content"]

    actual = {**expected_route(first), "reason": "The request identifies a requirement artifact."}
    passed, issues = score_result(first, actual)
    assert passed, issues
    missing = dict(actual)
    missing.pop("write_scope")
    assert not score_result(first, missing)[0]
    extra = {**actual, "client_hint": "ignored"}
    assert not score_result(first, extra)[0]
    assert set(actual) == ROUTE_RESPONSE_FIELDS


def main() -> int:
    assert_fixture_contract()
    assert_provenance_contract()
    assert_trigger_fixture_contract()
    assert_runner_contract()
    print("OK: artifact routing, trigger coverage, and raw runner contracts passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
