#!/usr/bin/env python3
"""Self-tests for fail-closed token and quality regression contracts."""

from __future__ import annotations

import contextlib
import io
import json
import math
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR / "audit"))
sys.path.insert(0, str(SCRIPTS_DIR / "analysis"))

import check_baseline_regression as baseline_checker
import detect_regressions as detector
import run_quarterly_audit as quarterly
import token_efficiency_dashboard as dashboard


IDENTITY = {
    "measurement_contract_version": "1.0",
    "token_counter": "tiktoken",
    "counter_version": "0.13.0",
    "tokenizer": "o200k_base",
}


def assert_identity_validator(
    validator,
    error_type,
) -> None:
    assert validator(dict(IDENTITY), source="test") == IDENTITY
    for field in IDENTITY:
        missing = dict(IDENTITY)
        missing.pop(field)
        try:
            validator(missing, source="test")
        except error_type as exc:
            assert "legacy or unsupported" in str(exc), exc
            assert field in str(exc), exc
        else:
            raise AssertionError(f"missing {field} did not fail closed")

        mismatched = {**IDENTITY, field: "wrong"}
        try:
            validator(mismatched, source="test")
        except error_type as exc:
            assert "measurement identity mismatch" in str(exc), exc
            assert field in str(exc), exc
        else:
            raise AssertionError(f"mismatched {field} did not fail closed")


def invoke_baseline_checker(
    baseline_path: Path,
    current_path: Path,
) -> tuple[int, str]:
    original_argv = sys.argv
    sys.argv = [
        "check_baseline_regression.py",
        "--baseline",
        str(baseline_path),
        "--current",
        str(current_path),
        "--fail-on-regression",
    ]
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr):
            exit_code = baseline_checker.main()
    finally:
        sys.argv = original_argv
    return exit_code, stderr.getvalue()


def invoke_exit_main(main_callable, argv: list[str]) -> tuple[int, str]:
    original_argv = sys.argv
    sys.argv = argv
    stderr = io.StringIO()
    exit_code = 0
    try:
        with contextlib.redirect_stderr(stderr):
            try:
                main_callable()
            except SystemExit as exc:
                exit_code = int(exc.code or 0)
    finally:
        sys.argv = original_argv
    return exit_code, stderr.getvalue()


def detector_current_from_baseline(baseline: dict) -> dict:
    return {
        **baseline,
        "quality_failing_skills": [],
    }


def main() -> int:
    assert baseline_checker.EXPECTED_MEASUREMENT_IDENTITY == IDENTITY
    assert detector.EXPECTED_MEASUREMENT_IDENTITY == IDENTITY
    assert quarterly.EXPECTED_MEASUREMENT_IDENTITY == IDENTITY
    assert dashboard.EXPECTED_MEASUREMENT_IDENTITY == IDENTITY
    assert_identity_validator(
        baseline_checker.validate_measurement_identity,
        baseline_checker.MeasurementIdentityError,
    )
    assert_identity_validator(
        detector.validate_measurement_identity,
        detector.MeasurementIdentityError,
    )
    assert_identity_validator(
        quarterly.validate_measurement_identity,
        quarterly.MeasurementIdentityError,
    )
    assert_identity_validator(
        dashboard.validate_measurement_identity,
        dashboard.MeasurementIdentityError,
    )

    baseline_temp = tempfile.TemporaryDirectory()
    baseline_path = Path(baseline_temp.name) / "identity-baseline.json"
    raw_baseline = json.loads(detector.BASELINE_FILE.read_text(encoding="utf-8"))
    baseline_path.write_text(
        json.dumps({**raw_baseline, **IDENTITY}),
        encoding="utf-8",
    )
    baseline = detector._file_baseline(baseline_path)
    quarterly.BASELINE_TARGETS = quarterly.load_baseline_targets(baseline_path)
    dashboard.TARGETS = dashboard.load_targets(baseline_path)
    assert {field: baseline[field] for field in IDENTITY} == IDENTITY
    assert {
        field: quarterly.BASELINE_TARGETS[field] for field in IDENTITY
    } == IDENTITY
    assert {field: dashboard.TARGETS[field] for field in IDENTITY} == IDENTITY

    supporting_bloat = detector_current_from_baseline(baseline)
    supporting_bloat["supporting_tokens"] *= 10
    supporting_bloat["all_packages_tokens_upper_bound"] = (
        supporting_bloat["total_tokens"] + supporting_bloat["supporting_tokens"]
    )
    supporting_bloat["everything_tokens_upper_bound"] = (
        supporting_bloat["all_packages_tokens_upper_bound"]
        + supporting_bloat["repository_governance_tokens"]
    )
    result = detector.detect_regressions(baseline, supporting_bloat)
    assert any(
        item["type"] == "package_token_inflation"
        for item in result["regressions"]
    ), result

    governance_bloat = detector_current_from_baseline(baseline)
    governance_bloat["repository_governance_tokens"] *= 10
    governance_bloat["everything_tokens_upper_bound"] = (
        governance_bloat["all_packages_tokens_upper_bound"]
        + governance_bloat["repository_governance_tokens"]
    )
    result = detector.detect_regressions(baseline, governance_bloat)
    assert any(
        item["type"] == "governance_token_inflation"
        for item in result["regressions"]
    ), result

    added_failing_skill = detector_current_from_baseline(baseline)
    added_failing_skill.update({
        "quality_passing": 17,
        "quality_total": 18,
        "quality_pass_rate": 17 / 18 * 100,
        "quality_failing_skills": ["new-skill"],
    })
    result = detector.detect_regressions(baseline, added_failing_skill)
    assert any(
        item["type"] == "quality_regression" for item in result["warnings"]
    ), result

    three_failing_skills = detector_current_from_baseline(baseline)
    three_failing_skills.update({
        "quality_passing": 14,
        "quality_total": 17,
        "quality_pass_rate": 14 / 17 * 100,
        "quality_failing_skills": ["one", "two", "three"],
    })
    result = detector.detect_regressions(baseline, three_failing_skills)
    assert any(
        item["type"] == "quality_regression" for item in result["regressions"]
    ), result

    four_broken_refs = detector_current_from_baseline(baseline)
    four_broken_refs["broken_refs"] = 4
    result = detector.detect_regressions(baseline, four_broken_refs)
    assert any(
        item["type"] == "cross_reference_regression"
        for item in result["regressions"]
    ), result

    two_long_skills = detector_current_from_baseline(baseline)
    two_long_skills["over_500"] = 2
    result = detector.detect_regressions(baseline, two_long_skills)
    assert any(
        item["type"] == "skill_length_regression"
        for item in result["regressions"]
    ), result

    quarterly_tokens = {
        "total_skill_tokens": baseline["total_tokens"],
        "avg_tokens_per_skill": baseline["avg_tokens"],
        "max_skill_body_tokens": baseline["max_skill_body_tokens"],
        "all_packages_tokens_upper_bound": baseline["all_packages_tokens_upper_bound"],
        "repository_governance_tokens": baseline["repository_governance_tokens"],
        "skills_over_500_lines": baseline["over_500"],
    }
    quarterly_result = quarterly.calculate_regressions(
        {"pass_rate": 100.0, "failing_skills": 0},
        quarterly_tokens,
        {"broken_references": 1},
    )
    assert quarterly_result["critical_count"] == 0, quarterly_result
    assert quarterly_result["warning_count"] == 1, quarterly_result
    assert quarterly_result["has_warnings"], quarterly_result

    quarterly_quality_warning = quarterly.calculate_regressions(
        {"pass_rate": 16 / 17 * 100, "failing_skills": 1},
        quarterly_tokens,
        {"broken_references": 0},
    )
    assert quarterly_quality_warning["critical_count"] == 0, quarterly_quality_warning
    assert quarterly_quality_warning["warning_count"] == 1, quarterly_quality_warning

    quarterly_quality_failure = quarterly.calculate_regressions(
        {"pass_rate": 14 / 17 * 100, "failing_skills": 3},
        quarterly_tokens,
        {"broken_references": 0},
    )
    assert quarterly_quality_failure["critical_count"] == 1, quarterly_quality_failure

    quarterly_boundary_failure = quarterly.calculate_regressions(
        {"pass_rate": 100.0, "failing_skills": 0},
        {**quarterly_tokens, "skills_over_500_lines": 2},
        {"broken_references": 4},
    )
    assert quarterly_boundary_failure["critical_count"] == 2, quarterly_boundary_failure

    quarterly_max_body_failure = quarterly.calculate_regressions(
        {"pass_rate": 100.0, "failing_skills": 0},
        {**quarterly_tokens, "max_skill_body_tokens": baseline["max_skill_body_tokens"] * 2},
        {"broken_references": 0},
    )
    assert quarterly_max_body_failure["critical_count"] == 1, quarterly_max_body_failure

    assert dashboard.status_for_count(1, critical_at=3) == ("yellow", "WARN")
    assert dashboard.status_for_count(3, critical_at=3) == ("red", "FAIL")
    assert dashboard.status_for_count(4, critical_at=4) == ("red", "FAIL")
    assert dashboard.status_for_count(2, critical_at=2) == ("red", "FAIL")
    assert quarterly.token_surface_status(105, 100) == "✓"
    assert quarterly.token_surface_status(106, 100) == "⚠"
    assert quarterly.token_surface_status(110, 100) == "✗"

    package_limit = math.ceil(
        baseline["all_packages_tokens_upper_bound"] * 1.10
    )
    checker_current = {
        **IDENTITY,
        "token_counting_method": "o200k_base",
        "skill_files": {
            "avg_tokens_per_skill": baseline["avg_tokens"],
            "total_tokens": baseline["total_tokens"],
            "all_packages_tokens_upper_bound": package_limit,
            "over_500_count": baseline["over_500"],
            "skills": [{"body_tokens": 1}],
        },
        "repository_governance": {
            "tokens": baseline["repository_governance_tokens"],
        },
    }
    _exit_code, failures, _warnings = baseline_checker.check_regression(
        {
            **IDENTITY,
            "avg_skill_tokens": baseline["avg_tokens"],
            "max_skill_body_tokens": 999999,
            "total_skill_tokens": baseline["total_tokens"],
            "all_packages_tokens_upper_bound": baseline["all_packages_tokens_upper_bound"],
            "repository_governance_tokens": baseline["repository_governance_tokens"],
        },
        checker_current,
        threshold=0.10,
        warning_threshold=0.05,
    )
    assert any("All package text" in failure for failure in failures), failures

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        baseline_path = temp_root / "baseline.json"
        current_path = temp_root / "current.json"
        legacy_json = temp_root / "legacy-baseline.json"
        legacy_markdown = temp_root / "legacy-baseline.md"
        current_markdown = temp_root / "current-baseline.md"
        baseline_path.write_text(
            json.dumps({
                **IDENTITY,
                "avg_tokens_per_skill": baseline["avg_tokens"],
                "max_skill_body_tokens": baseline["max_skill_body_tokens"],
                "total_skill_tokens": baseline["total_tokens"],
                "all_packages_tokens_upper_bound": baseline["all_packages_tokens_upper_bound"],
                "repository_governance_tokens": baseline["repository_governance_tokens"],
            }),
            encoding="utf-8",
        )
        current_path.write_text(
            json.dumps({
                **checker_current,
            }),
            encoding="utf-8",
        )
        legacy_json.write_text(
            json.dumps({
                key: value
                for key, value in raw_baseline.items()
                if key not in IDENTITY
            }),
            encoding="utf-8",
        )
        legacy_markdown.write_text(
            "**Tokenizer:** `o200k_base`\n",
            encoding="utf-8",
        )
        current_markdown.write_text(
            "\n".join(
                [
                    "# Token Efficiency Baseline",
                    "",
                    "**Measurement contract version:** `1.0`",
                    "**Token counter:** `tiktoken`",
                    "**Counter version:** `0.13.0`",
                    "**Tokenizer:** `o200k_base`",
                    "",
                    "Average `SKILL.md` size is 100 tokens.",
                    "Largest Skill body is 100 tokens.",
                    "| All 12 `SKILL.md` files | 1,200 |",
                    "| All package text | 2,000 |",
                    "| Root `AGENTS.md` | 500 |",
                ]
            ),
            encoding="utf-8",
        )

        assert {
            field: baseline_checker.parse_baseline_from_markdown(current_markdown)[
                field
            ]
            for field in IDENTITY
        } == IDENTITY
        try:
            baseline_checker.parse_baseline_from_markdown(legacy_markdown)
        except baseline_checker.MeasurementIdentityError as exc:
            assert "legacy or unsupported" in str(exc), exc
        else:
            raise AssertionError("legacy Markdown baseline was silently accepted")
        try:
            detector.parse_audit_report(legacy_markdown)
        except detector.MeasurementIdentityError as exc:
            assert "legacy or unsupported" in str(exc), exc
        else:
            raise AssertionError("legacy audit Markdown was silently accepted")

        for module, entrypoint, argv in (
            (detector, detector.main, ["detect_regressions.py", "--json"]),
            (quarterly, quarterly.main, ["run_quarterly_audit.py", "--json"]),
            (dashboard, dashboard.main, ["token_efficiency_dashboard.py", "--json"]),
        ):
            original_baseline_file = module.BASELINE_FILE
            module.BASELINE_FILE = legacy_json
            try:
                exit_code, stderr = invoke_exit_main(entrypoint, argv)
            finally:
                module.BASELINE_FILE = original_baseline_file
            assert exit_code == 2, (module.__name__, exit_code, stderr)
            assert "legacy or unsupported" in stderr, (module.__name__, stderr)
            assert "Traceback" not in stderr, (module.__name__, stderr)

        for field in IDENTITY:
            bad_baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            bad_baseline.pop(field)
            baseline_path.write_text(json.dumps(bad_baseline), encoding="utf-8")
            exit_code, stderr = invoke_baseline_checker(
                baseline_path,
                current_path,
            )
            assert exit_code == 2, (field, exit_code, stderr)
            assert field in stderr, (field, stderr)
            baseline_path.write_text(
                json.dumps(
                    {
                        **IDENTITY,
                        "avg_tokens_per_skill": baseline["avg_tokens"],
                        "max_skill_body_tokens": baseline["max_skill_body_tokens"],
                        "total_skill_tokens": baseline["total_tokens"],
                        "all_packages_tokens_upper_bound": baseline[
                            "all_packages_tokens_upper_bound"
                        ],
                        "repository_governance_tokens": baseline[
                            "repository_governance_tokens"
                        ],
                    }
                ),
                encoding="utf-8",
            )

        bad_current = json.loads(current_path.read_text(encoding="utf-8"))
        bad_current["counter_version"] = "0.12.0"
        current_path.write_text(json.dumps(bad_current), encoding="utf-8")
        exit_code, stderr = invoke_baseline_checker(
            baseline_path,
            current_path,
        )
        assert exit_code == 2, (exit_code, stderr)
        assert "counter_version" in stderr, stderr

    baseline_temp.cleanup()
    print(
        "OK: token identity, legacy rejection, operational exits, "
        "quality, and quarterly regression contracts passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
