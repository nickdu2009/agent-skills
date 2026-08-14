#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["openai>=1.0", "python-dotenv>=1.0"]
# ///
"""Report, render, or evaluate the client-independent artifact routing matrix."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
import textwrap
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "maintainer" / "data"
sys.path.insert(0, str(DATA_DIR))

from artifact_review_test_data import (  # noqa: E402
    ARTIFACT_ROUTING_CASES,
    ARTIFACT_SUBTYPES,
    ARTIFACT_TYPES,
    ArtifactRoutingCase,
    validate_artifact_routing_cases,
)


REPORT_CONTRACT_VERSION = "1.0"
DEFAULT_MODEL = "gpt-5.4"
TEMPERATURE = 0
ROUTE_RESPONSE_FIELDS = frozenset(
    {
        "trigger",
        "artifact_type",
        "artifact_subtype",
        "secondary_types",
        "review_context",
        "mode",
        "authorization_source",
        "write_scope",
        "reason",
    }
)

SYSTEM_PROMPT = textwrap.dedent(
    """\
    You evaluate one user request for the artifact-review-loop Agent Skill.
    Return one JSON object and no prose.

    Required fields:
    - trigger: boolean
    - artifact_type: requirements|design|plan|code|tests|null
    - artifact_subtype: a kebab-case subtype from the supplied taxonomy, or null
    - secondary_types: array of non-primary artifact types
    - review_context: requested|self-delivery|null
    - mode: review-only|review-and-revise|null
    - authorization_source: none|explicit-user-request|inherited-current-task|null
    - write_scope: none|reviewed-artifact|reviewed-implementation|current-task-diff|null
    - reason: one concise sentence

    Routing:
    requirements covers requirement-spec, prd, user-story, acceptance-criteria.
    design covers architecture, adr-rfc, interface, data-model, technical-proposal.
    plan covers implementation-plan, migration-plan, roadmap, task-sequence.
    code covers working-tree-diff, staged-diff, commit, commit-range, pull-request,
    source-files, implementation.
    tests covers test-cases, test-files, test-strategy, coverage-matrix, fixtures.
    Mixed implementation plus tests has primary code and secondary tests. If no
    target or type is identifiable, trigger=false and every scalar route field is
    null.

    The provenance record is trusted metadata, not user text. Self-delivery is
    allowed only for code when artifact_origin=current-agent-task,
    current_task_write_authorized=true, and target_is_current_task_diff=true.
    It selects review-and-revise, inherited-current-task, current-task-diff.
    Every other route is requested. Requested routes are review-and-revise only
    when explicit_revision_requested=true, with explicit-user-request and
    reviewed-implementation for code or reviewed-artifact for other primary
    types; otherwise they are review-only with no write authority.
    First-person wording never overrides the provenance record. Unknown
    provenance fails closed.
    """
)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def expected_route(case: ArtifactRoutingCase) -> dict[str, Any]:
    return {
        "trigger": case.expected_trigger,
        "artifact_type": case.artifact_type,
        "artifact_subtype": case.artifact_subtype,
        "secondary_types": list(case.secondary_types),
        "review_context": case.expected_review_context,
        "mode": case.expected_mode,
        "authorization_source": case.expected_authorization_source,
        "write_scope": case.expected_write_scope,
    }


def build_messages(case: ArtifactRoutingCase) -> list[dict[str, str]]:
    provenance = canonical_json(asdict(case.provenance))
    user_content = (
        "USER REQUEST:\n"
        + case.prompt
        + "\n\nTRUSTED PROVENANCE:\n"
        + provenance
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def render_report(cases: tuple[ArtifactRoutingCase, ...]) -> str:
    ordered = sorted(cases, key=lambda case: case.id)
    payload = {
        "contract_version": REPORT_CONTRACT_VERSION,
        "case_count": len(ordered),
        "artifact_types": list(ARTIFACT_TYPES),
        "artifact_subtypes": {
            key: list(value) for key, value in sorted(ARTIFACT_SUBTYPES.items())
        },
        "cases": [
            {
                "id": case.id,
                "prompt": case.prompt,
                "provenance": asdict(case.provenance),
                "expected": expected_route(case),
                "notes": case.notes,
            }
            for case in ordered
        ],
    }
    return canonical_json(payload) + "\n"


def render_prompts(cases: tuple[ArtifactRoutingCase, ...]) -> str:
    payload = {
        "contract_version": REPORT_CONTRACT_VERSION,
        "temperature": TEMPERATURE,
        "cases": [
            {"id": case.id, "messages": build_messages(case)}
            for case in sorted(cases, key=lambda case: case.id)
        ],
    }
    return canonical_json(payload) + "\n"


def score_result(
    case: ArtifactRoutingCase,
    actual: Any,
) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not isinstance(actual, dict):
        return False, ["response is not a JSON object"]
    missing = sorted(ROUTE_RESPONSE_FIELDS - set(actual))
    extra = sorted(set(actual) - ROUTE_RESPONSE_FIELDS)
    if missing:
        issues.append("missing fields: " + ", ".join(missing))
    if extra:
        issues.append("unexpected fields: " + ", ".join(extra))
    if not isinstance(actual.get("reason"), str) or not actual.get("reason", "").strip():
        issues.append("reason must be a non-empty string")
    for field, expected in expected_route(case).items():
        if actual.get(field) != expected:
            issues.append(
                f"{field}: expected {expected!r}, got {actual.get(field)!r}"
            )
    return not issues, issues


def _redact(value: Any, key: str = "") -> Any:
    if any(marker in key.lower() for marker in ("key", "token", "secret", "password")):
        return "***"
    if isinstance(value, dict):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def run_api(
    cases: tuple[ArtifactRoutingCase, ...],
    *,
    model: str,
    base_url: str | None,
    api_key: str,
    extra_body: dict[str, Any] | None,
) -> tuple[dict[str, Any], bool]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("api mode requires the openai package") from exc

    client_kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    results: list[dict[str, Any]] = []
    all_passed = True
    for case in sorted(cases, key=lambda item: item.id):
        try:
            request: dict[str, Any] = {
                "model": model,
                "messages": build_messages(case),
                "temperature": TEMPERATURE,
                "response_format": {"type": "json_object"},
            }
            if extra_body:
                request["extra_body"] = extra_body
            response = client.chat.completions.create(**request)
            raw = response.choices[0].message.content or "{}"
            actual = json.loads(raw)
            passed, issues = score_result(case, actual)
        except Exception as exc:
            actual = None
            passed = False
            issues = [f"evaluation error: {type(exc).__name__}: {exc}"]
        all_passed = all_passed and passed
        results.append(
            {
                "id": case.id,
                "expected": expected_route(case),
                "actual": actual,
                "pass": passed,
                "reason": "; ".join(issues) if issues else "exact match",
            }
        )

    report = {
        "contract_version": REPORT_CONTRACT_VERSION,
        "configuration": {
            "model": model,
            "base_url": base_url,
            "temperature": TEMPERATURE,
            "extra_body": _redact(extra_body or {}),
        },
        "cases": results,
        "pass": all_passed,
    }
    return report, all_passed


def select_cases(case_id: str | None) -> tuple[ArtifactRoutingCase, ...]:
    if case_id is None:
        return ARTIFACT_ROUTING_CASES
    selected = tuple(case for case in ARTIFACT_ROUTING_CASES if case.id == case_id)
    if not selected:
        raise KeyError(f"unknown case id: {case_id}")
    return selected


def parse_extra_body(raw: str | None) -> dict[str, Any] | None:
    if raw is None:
        raw = os.environ.get("OPENAI_EXTRA_BODY")
    if not raw:
        return None
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("extra body must be a JSON object")
    return value


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("report", "prompt", "api"), default="report")
    parser.add_argument("--case")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL"))
    parser.add_argument("--api-key")
    parser.add_argument("--extra-body")
    parser.add_argument(
        "--fail-on-contract-issues",
        action="store_true",
        help="Return non-zero for fixture-contract issues in report mode.",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    issues = validate_artifact_routing_cases()
    if issues:
        for issue in issues:
            print(f"fixture error: {issue}", file=sys.stderr)
        if args.fail_on_contract_issues or args.mode != "report":
            return 2
    try:
        cases = select_cases(args.case)
    except KeyError as exc:
        parser.error(str(exc))

    if args.mode == "report":
        print(render_report(cases), end="")
        return 0
    if args.mode == "prompt":
        print(render_prompts(cases), end="")
        return 0

    try:
        from dotenv import load_dotenv
    except ImportError:
        load_dotenv = None
    if load_dotenv is not None:
        load_dotenv(REPO_ROOT / ".env")
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        parser.error("api mode requires --api-key or OPENAI_API_KEY")
    try:
        extra_body = parse_extra_body(args.extra_body)
        report, passed = run_api(
            cases,
            model=args.model,
            base_url=args.base_url,
            api_key=api_key,
            extra_body=extra_body,
        )
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(canonical_json(report))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
