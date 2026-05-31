#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Evaluate curated governance session observability decision points."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POINTS = REPO_ROOT / "maintainer" / "governance_observability" / "decision_points.yaml"
KNOWN_SKILLS = [
    "bugfix-workflow",
    "safe-refactor",
    "scoped-tasking",
    "design-before-plan",
    "impact-analysis",
    "self-review",
    "targeted-validation",
    "code-review-loop",
    "test-review-loop",
    "plan-review-loop",
    "requirements-review-loop",
    "design-review-loop",
]
ASK_PATTERNS = [
    r"\?",
    r"是否要我",
    r"你要我",
    r"你希望我",
    r"请确认",
    r"等你确认",
    r"给你确认",
    r"批准之前",
    r"要不要我",
    r"would you like",
    r"should i",
    r"confirm",
]
REVIEW_RESULT_PATTERN = re.compile(r"review_result:\s*([a-z_]+)", flags=re.IGNORECASE)
DROP_PATTERN = re.compile(r"\[drop:\s*([a-z0-9_-]+)", flags=re.IGNORECASE)
REVISION_PATTERN = re.compile(r"修订|revise|revision|revised", flags=re.IGNORECASE)


def load_points(path: Path) -> list[dict[str, Any]]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"decision point file not found: {path}") from exc

    if not isinstance(payload, list):
        raise ValueError("decision point file must contain a top-level YAML list")
    return payload


def detect_asked_user(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in ASK_PATTERNS)


def detect_skills(text: str) -> list[str]:
    lowered = text.lower()
    detected = [skill for skill in KNOWN_SKILLS if skill in lowered]
    return detected


def detect_review_result(text: str) -> str | None:
    matches = REVIEW_RESULT_PATTERN.findall(text)
    if not matches:
        return None
    return matches[-1].lower()


def detect_drop_after_issues(text: str) -> bool:
    event_pattern = re.compile(
        r"review_result:\s*([a-z_]+)|\[drop:\s*([a-z0-9_-]+)",
        flags=re.IGNORECASE,
    )
    unresolved_issues = False
    for match in event_pattern.finditer(text):
        review_result = match.group(1)
        drop_skill = match.group(2)
        if review_result is not None:
            unresolved_issues = review_result.lower() == "issues_found"
            continue
        if drop_skill is None:
            continue
        if "review-loop" in drop_skill.lower() and unresolved_issues:
            return True
    return False


def detect_rereview_after_revision(text: str) -> bool:
    revision_matches = list(REVISION_PATTERN.finditer(text))
    if not revision_matches:
        return False
    last_revision_start = revision_matches[-1].start()
    return any(
        review_match.start() > last_revision_start
        for review_match in REVIEW_RESULT_PATTERN.finditer(text)
    )


def evaluate_point(point: dict[str, Any]) -> dict[str, Any]:
    point_id = point.get("id")
    metric = point.get("metric")
    text = point.get("transcript_excerpt", "")
    if not isinstance(point_id, str) or not isinstance(metric, str) or not isinstance(text, str):
        raise ValueError(f"invalid decision point schema: {point!r}")

    observed_asked_user = detect_asked_user(text)
    observed_skills = detect_skills(text)
    observed_review_result = detect_review_result(text)
    observed_drop_after_issues = detect_drop_after_issues(text)
    observed_rereview_after_revision = detect_rereview_after_revision(text)

    result: dict[str, Any] = {
        "id": point_id,
        "metric": metric,
        "observed_asked_user": observed_asked_user,
        "observed_skills": observed_skills,
        "observed_review_result": observed_review_result,
        "observed_drop_after_issues": observed_drop_after_issues,
        "observed_rereview_after_revision": observed_rereview_after_revision,
    }

    if metric == "extra_confirmation":
        should_ask_user = bool(point.get("should_ask_user"))
        extra_confirmation_event = (not should_ask_user) and observed_asked_user
        missed_required_confirmation = should_ask_user and (not observed_asked_user)
        result.update(
            {
                "should_ask_user": should_ask_user,
                "extra_confirmation_event": extra_confirmation_event,
                "missed_required_confirmation": missed_required_confirmation,
                "calibrated": not extra_confirmation_event and not missed_required_confirmation,
            }
        )
        return result

    if metric == "routing":
        expected_skills = point.get("expected_skills", [])
        forbidden_skills = point.get("forbidden_skills", [])
        if not isinstance(expected_skills, list) or not isinstance(forbidden_skills, list):
            raise ValueError(f"routing point must use list fields: {point_id}")
        expected_review_result = point.get("expected_review_result")
        forbid_drop_after_issues = point.get("forbid_drop_after_issues", False)
        require_rereview_after_revision = point.get("require_rereview_after_revision", False)
        if expected_review_result is not None and not isinstance(expected_review_result, str):
            raise ValueError(f"expected_review_result must be a string when present: {point_id}")
        if not isinstance(forbid_drop_after_issues, bool):
            raise ValueError(f"forbid_drop_after_issues must be a bool: {point_id}")
        if not isinstance(require_rereview_after_revision, bool):
            raise ValueError(f"require_rereview_after_revision must be a bool: {point_id}")

        missing_expected = [skill for skill in expected_skills if skill not in observed_skills]
        present_forbidden = [skill for skill in forbidden_skills if skill in observed_skills]
        loop_breakage_signals: list[str] = []
        if expected_review_result is not None and observed_review_result != expected_review_result:
            loop_breakage_signals.append("review_result_mismatch")
        if forbid_drop_after_issues and observed_drop_after_issues:
            loop_breakage_signals.append("drop_after_issues_found")
        if require_rereview_after_revision and not observed_rereview_after_revision:
            loop_breakage_signals.append("missing_rereview_after_revision")
        result.update(
            {
                "expected_skills": expected_skills,
                "forbidden_skills": forbidden_skills,
                "expected_review_result": expected_review_result,
                "forbid_drop_after_issues": forbid_drop_after_issues,
                "require_rereview_after_revision": require_rereview_after_revision,
                "missing_expected_skills": missing_expected,
                "present_forbidden_skills": present_forbidden,
                "loop_breakage_signals": loop_breakage_signals,
                "routing_misjudgment": bool(
                    missing_expected or present_forbidden or loop_breakage_signals
                ),
                "calibrated": not missing_expected and not present_forbidden and not loop_breakage_signals,
            }
        )
        return result

    raise ValueError(f"unsupported metric type for {point_id}: {metric}")


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    extra_points = [result for result in results if result["metric"] == "extra_confirmation"]
    routing_points = [result for result in results if result["metric"] == "routing"]

    eligible_extra = [result for result in extra_points if not result["should_ask_user"]]
    extra_confirmation_event_count = sum(
        1 for result in eligible_extra if result["extra_confirmation_event"]
    )
    required_confirmation_points = [result for result in extra_points if result["should_ask_user"]]
    missed_required_confirmation_count = sum(
        1 for result in required_confirmation_points if result["missed_required_confirmation"]
    )
    routing_misjudgment_count = sum(
        1 for result in routing_points if result["routing_misjudgment"]
    )

    return {
        "decision_point_count": len(results),
        "extra_confirmation_denominator": len(eligible_extra),
        "extra_confirmation_event_count": extra_confirmation_event_count,
        "extra_confirmation_rate": (
            extra_confirmation_event_count / len(eligible_extra) if eligible_extra else None
        ),
        "required_confirmation_point_count": len(required_confirmation_points),
        "missed_required_confirmation_count": missed_required_confirmation_count,
        "routing_point_count": len(routing_points),
        "routing_misjudgment_count": routing_misjudgment_count,
        "routing_misjudgment_rate": (
            routing_misjudgment_count / len(routing_points) if routing_points else None
        ),
    }


def print_text_report(summary: dict[str, Any], results: list[dict[str, Any]]) -> None:
    print("=" * 80)
    print("Governance Session Observability")
    print("=" * 80)
    print()
    print(f"Decision points: {summary['decision_point_count']}")
    print(
        f"Extra confirmation rate: {summary['extra_confirmation_event_count']}"
        f" / {summary['extra_confirmation_denominator']}"
        f" = {format_rate(summary['extra_confirmation_rate'])}"
    )
    print(
        f"Missed required confirmations: {summary['missed_required_confirmation_count']}"
        f" / {summary['required_confirmation_point_count']}"
    )
    print(
        f"Routing misjudgment rate: {summary['routing_misjudgment_count']}"
        f" / {summary['routing_point_count']}"
        f" = {format_rate(summary['routing_misjudgment_rate'])}"
    )
    print()
    print("Mismatches:")
    mismatches = [
        result for result in results
        if not result["calibrated"]
    ]
    if not mismatches:
        print("  - none")
        return
    for result in mismatches:
        print(f"  - {result['id']}")


def format_rate(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run governance observability evaluation")
    parser.add_argument(
        "--decision-points",
        type=Path,
        default=DEFAULT_POINTS,
        help="Path to curated decision point YAML",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        points = load_points(args.decision_points)
        results = [evaluate_point(point) for point in points]
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    payload = {
        "decision_points": str(args.decision_points),
        "summary": build_summary(results),
        "results": results,
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print_text_report(payload["summary"], results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
