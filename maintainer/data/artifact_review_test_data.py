#!/usr/bin/env python3
"""Deterministic routing and authorization fixtures for artifact review."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product


ARTIFACT_TYPES: tuple[str, ...] = (
    "requirements",
    "design",
    "plan",
    "code",
    "tests",
)

ARTIFACT_SUBTYPES: dict[str, tuple[str, ...]] = {
    "requirements": (
        "requirement-spec",
        "prd",
        "user-story",
        "acceptance-criteria",
    ),
    "design": (
        "architecture",
        "adr-rfc",
        "interface",
        "data-model",
        "technical-proposal",
    ),
    "plan": (
        "implementation-plan",
        "migration-plan",
        "roadmap",
        "task-sequence",
    ),
    "code": (
        "working-tree-diff",
        "staged-diff",
        "commit",
        "commit-range",
        "pull-request",
        "source-files",
        "implementation",
    ),
    "tests": (
        "test-cases",
        "test-files",
        "test-strategy",
        "coverage-matrix",
        "fixtures",
    ),
}

ARTIFACT_ORIGINS: tuple[str, ...] = (
    "current-agent-task",
    "user-or-external",
    "unknown",
)


@dataclass(frozen=True)
class ReviewProvenance:
    artifact_origin: str
    current_task_write_authorized: bool
    target_is_current_task_diff: bool
    explicit_revision_requested: bool


@dataclass(frozen=True)
class ReviewAuthorization:
    review_context: str
    mode: str
    authorization_source: str
    write_scope: str


@dataclass(frozen=True)
class ArtifactRoutingCase:
    id: str
    prompt: str
    expected_trigger: bool
    artifact_type: str | None
    artifact_subtype: str | None
    secondary_types: tuple[str, ...]
    provenance: ReviewProvenance
    expected_review_context: str | None
    expected_mode: str | None
    expected_authorization_source: str | None
    expected_write_scope: str | None
    notes: str


REQUESTED = ReviewProvenance(
    artifact_origin="user-or-external",
    current_task_write_authorized=False,
    target_is_current_task_diff=False,
    explicit_revision_requested=False,
)

EXPLICIT_REVISION = ReviewProvenance(
    artifact_origin="user-or-external",
    current_task_write_authorized=False,
    target_is_current_task_diff=False,
    explicit_revision_requested=True,
)

SELF_DELIVERY = ReviewProvenance(
    artifact_origin="current-agent-task",
    current_task_write_authorized=True,
    target_is_current_task_diff=True,
    explicit_revision_requested=False,
)


def resolve_review_authorization(
    artifact_type: str,
    provenance: ReviewProvenance,
) -> ReviewAuthorization:
    """Resolve context and write authority from trusted provenance inputs."""

    if artifact_type not in ARTIFACT_TYPES:
        raise ValueError(f"unknown artifact_type: {artifact_type!r}")
    if provenance.artifact_origin not in ARTIFACT_ORIGINS:
        raise ValueError(f"unknown artifact_origin: {provenance.artifact_origin!r}")
    for field_name in (
        "current_task_write_authorized",
        "target_is_current_task_diff",
        "explicit_revision_requested",
    ):
        if type(getattr(provenance, field_name)) is not bool:
            raise TypeError(f"{field_name} must be bool")

    is_self_delivery = (
        artifact_type == "code"
        and provenance.artifact_origin == "current-agent-task"
        and provenance.current_task_write_authorized
        and provenance.target_is_current_task_diff
    )
    if is_self_delivery:
        return ReviewAuthorization(
            review_context="self-delivery",
            mode="review-and-revise",
            authorization_source="inherited-current-task",
            write_scope="current-task-diff",
        )
    if provenance.explicit_revision_requested:
        return ReviewAuthorization(
            review_context="requested",
            mode="review-and-revise",
            authorization_source="explicit-user-request",
            write_scope=(
                "reviewed-implementation"
                if artifact_type == "code"
                else "reviewed-artifact"
            ),
        )
    return ReviewAuthorization(
        review_context="requested",
        mode="review-only",
        authorization_source="none",
        write_scope="none",
    )


def _case(
    case_id: str,
    prompt: str,
    artifact_type: str | None,
    artifact_subtype: str | None,
    *,
    secondary_types: tuple[str, ...] = (),
    provenance: ReviewProvenance = REQUESTED,
    notes: str,
) -> ArtifactRoutingCase:
    if artifact_type is None:
        return ArtifactRoutingCase(
            id=case_id,
            prompt=prompt,
            expected_trigger=False,
            artifact_type=None,
            artifact_subtype=None,
            secondary_types=(),
            provenance=provenance,
            expected_review_context=None,
            expected_mode=None,
            expected_authorization_source=None,
            expected_write_scope=None,
            notes=notes,
        )
    authorization = resolve_review_authorization(artifact_type, provenance)
    return ArtifactRoutingCase(
        id=case_id,
        prompt=prompt,
        expected_trigger=True,
        artifact_type=artifact_type,
        artifact_subtype=artifact_subtype,
        secondary_types=secondary_types,
        provenance=provenance,
        expected_review_context=authorization.review_context,
        expected_mode=authorization.mode,
        expected_authorization_source=authorization.authorization_source,
        expected_write_scope=authorization.write_scope,
        notes=notes,
    )


ARTIFACT_ROUTING_CASES: tuple[ArtifactRoutingCase, ...] = (
    _case(
        "route-requirement-spec",
        "评审一下这份需求文档，看看完整性和可验证性如何",
        "requirements",
        "requirement-spec",
        notes="Generic requirements document.",
    ),
    _case(
        "route-prd",
        "Review this PRD to check if all acceptance criteria are clear and verifiable.",
        "requirements",
        "prd",
        notes="PRD routing.",
    ),
    _case(
        "route-user-story",
        "帮我审核用户故事的边界条件和失败场景是否齐全",
        "requirements",
        "user-story",
        notes="User story routing.",
    ),
    _case(
        "route-acceptance-criteria",
        "Audit these acceptance criteria for observability and independent verification.",
        "requirements",
        "acceptance-criteria",
        notes="Acceptance-criteria routing.",
    ),
    _case(
        "route-architecture",
        "Review this architecture RFC for soundness and rollback design.",
        "design",
        "architecture",
        notes="Architecture design routing.",
    ),
    _case(
        "route-proposed-adr",
        "ADR-0043 is Proposed. Review its decision drivers, alternatives, consequences, relationships, and revisit conditions.",
        "design",
        "adr-rfc",
        notes="A Proposed ADR is reviewed as design, not used as a plan constraint.",
    ),
    _case(
        "route-interface",
        "帮我评审这个接口设计，看看契约定义是否清晰",
        "design",
        "interface",
        notes="Interface design routing.",
    ),
    _case(
        "route-schema-migration",
        "Review this database schema migration design for mixed-version safety, backfill, cutover, and rollback.",
        "design",
        "data-model",
        notes="Schema migration design coverage.",
    ),
    _case(
        "route-technical-proposal",
        "评审一下我的技术方案，看看有没有遗漏失败处理",
        "design",
        "technical-proposal",
        notes="Bare technical proposal routes to design.",
    ),
    _case(
        "route-migration-plan",
        "Review this migration plan for executability and rollback safety.",
        "plan",
        "migration-plan",
        notes="Migration plan routing.",
    ),
    _case(
        "route-implementation-plan",
        "评审一下实施方案，确认顺序和验证步骤都清楚",
        "plan",
        "implementation-plan",
        notes="Implementation plan routing.",
    ),
    _case(
        "route-task-sequence",
        "帮我评审实施计划是否每一步都有具体文件落点",
        "plan",
        "task-sequence",
        notes="Task sequence routing.",
    ),
    _case(
        "route-roadmap",
        "Review this delivery roadmap for prerequisites, ownership, gates, and stop conditions.",
        "plan",
        "roadmap",
        notes="Roadmap routing.",
    ),
    _case(
        "route-accepted-adr-plan",
        "Review this implementation plan against active Accepted ADR-0042 and exclude Proposed or superseded decisions.",
        "plan",
        "implementation-plan",
        notes="Accepted ADR alignment belongs to plan review.",
    ),
    _case(
        "route-working-tree",
        "Review the working tree diff for correctness, regressions, and scope control.",
        "code",
        "working-tree-diff",
        notes="Working-tree code routing.",
    ),
    _case(
        "route-staged-diff",
        "Review the staged diff before it is committed.",
        "code",
        "staged-diff",
        notes="Staged code routing.",
    ),
    _case(
        "route-commit",
        "帮我 review 一下这次 commit，看看有没有 bug 或安全问题",
        "code",
        "commit",
        notes="Commit code routing.",
    ),
    _case(
        "route-commit-range",
        "Audit the last three commits as one implementation change.",
        "code",
        "commit-range",
        notes="Commit-range code routing.",
    ),
    _case(
        "route-pull-request",
        "Review this pull request: check description quality, CI status, and the diff itself.",
        "code",
        "pull-request",
        notes="Pull-request code routing.",
    ),
    _case(
        "route-source-files",
        "评审一下被测代码",
        "code",
        "source-files",
        notes="Code under test is code, not a test artifact.",
    ),
    _case(
        "route-implementation",
        "Review the completed payment implementation for contract alignment.",
        "code",
        "implementation",
        notes="Completed implementation routing.",
    ),
    _case(
        "route-test-cases",
        "评审测试用例的覆盖度和断言质量，看看是否有 flaky 风险",
        "tests",
        "test-cases",
        notes="Test case routing.",
    ),
    _case(
        "route-test-strategy",
        "Review the test strategy for scenario completeness.",
        "tests",
        "test-strategy",
        notes="Test strategy routing.",
    ),
    _case(
        "route-test-files",
        "帮我看看新加的单元测试，断言够不够强",
        "tests",
        "test-files",
        notes="Test file as an artifact.",
    ),
    _case(
        "route-coverage-matrix",
        "Review the coverage matrix for missing negative and boundary scenarios.",
        "tests",
        "coverage-matrix",
        notes="Coverage matrix routing.",
    ),
    _case(
        "route-fixtures",
        "Audit these test fixtures for fidelity, isolation, and determinism.",
        "tests",
        "fixtures",
        notes="Fixture routing.",
    ),
    _case(
        "route-bare-review",
        "帮我评审一下",
        None,
        None,
        notes="No identifiable target; clarification precedes activation.",
    ),
    _case(
        "route-mixed-code-tests",
        "Review this implementation diff and its new unit tests for correctness and assertion quality.",
        "code",
        "working-tree-diff",
        secondary_types=("tests",),
        notes="Mixed code and tests selects code as the single primary route.",
    ),
    _case(
        "route-first-person-diff",
        "I just finished implementing the feature. Can you review the diff before I run tests?",
        "code",
        "working-tree-diff",
        notes="First-person wording is user-or-external and remains requested review-only.",
    ),
    _case(
        "route-first-person-multifile",
        "I've made changes across 5 files. Before testing, let me check if the diff looks clean.",
        "code",
        "working-tree-diff",
        notes="First-person multi-file wording does not establish current-agent provenance.",
    ),
    _case(
        "route-self-delivery",
        "Review the current task diff before targeted validation.",
        "code",
        "working-tree-diff",
        provenance=SELF_DELIVERY,
        notes="All trusted self-delivery gates are present.",
    ),
    _case(
        "route-provenance-origin-gate",
        "Review the current diff before validation.",
        "code",
        "working-tree-diff",
        provenance=ReviewProvenance(
            artifact_origin="user-or-external",
            current_task_write_authorized=True,
            target_is_current_task_diff=True,
            explicit_revision_requested=False,
        ),
        notes="Missing current-agent origin fails closed.",
    ),
    _case(
        "route-provenance-write-gate",
        "Review the current diff before validation.",
        "code",
        "working-tree-diff",
        provenance=ReviewProvenance(
            artifact_origin="current-agent-task",
            current_task_write_authorized=False,
            target_is_current_task_diff=True,
            explicit_revision_requested=False,
        ),
        notes="Missing current-task write authority fails closed.",
    ),
    _case(
        "route-provenance-target-gate",
        "Review the current diff before validation.",
        "code",
        "working-tree-diff",
        provenance=ReviewProvenance(
            artifact_origin="current-agent-task",
            current_task_write_authorized=True,
            target_is_current_task_diff=False,
            explicit_revision_requested=False,
        ),
        notes="A non-current-task target fails closed.",
    ),
    _case(
        "route-provenance-unknown",
        "Review this diff before validation.",
        "code",
        "working-tree-diff",
        provenance=ReviewProvenance(
            artifact_origin="unknown",
            current_task_write_authorized=True,
            target_is_current_task_diff=True,
            explicit_revision_requested=False,
        ),
        notes="Unknown origin fails closed.",
    ),
    _case(
        "route-explicit-revision",
        "Review this requirements draft, fix every supported issue, and re-review it.",
        "requirements",
        "requirement-spec",
        provenance=EXPLICIT_REVISION,
        notes="Explicit revision authorizes only the primary artifact.",
    ),
    _case(
        "route-explicit-code-revision",
        "Review this implementation diff, fix every supported issue, and re-review it.",
        "code",
        "working-tree-diff",
        provenance=EXPLICIT_REVISION,
        notes="Explicit requested code revision is limited to reviewed implementation.",
    ),
    _case(
        "route-retry-fallback-authorization",
        "Review the billing diff that added three retries and a cache fallback without a confirmed behavior decision.",
        "code",
        "working-tree-diff",
        notes="Unauthorized retry and fallback behavior must block a clean result.",
    ),
)


def validate_artifact_routing_cases(
    cases: tuple[ArtifactRoutingCase, ...] = ARTIFACT_ROUTING_CASES,
) -> list[str]:
    """Return fixture contract issues in deterministic order."""

    issues: list[str] = []
    counts: dict[str, int] = {}
    for case in cases:
        counts[case.id] = counts.get(case.id, 0) + 1
        if case.expected_trigger:
            if case.artifact_type not in ARTIFACT_TYPES:
                issues.append(f"{case.id}: invalid artifact_type")
                continue
            if case.artifact_subtype not in ARTIFACT_SUBTYPES[case.artifact_type]:
                issues.append(f"{case.id}: invalid artifact_subtype")
            if len(set(case.secondary_types)) != len(case.secondary_types):
                issues.append(f"{case.id}: duplicate secondary_types")
            if case.artifact_type in case.secondary_types:
                issues.append(f"{case.id}: primary type repeated in secondary_types")
            unknown_secondary = sorted(set(case.secondary_types) - set(ARTIFACT_TYPES))
            if unknown_secondary:
                issues.append(f"{case.id}: invalid secondary_types {unknown_secondary}")
            route = resolve_review_authorization(case.artifact_type, case.provenance)
            expected = (
                case.expected_review_context,
                case.expected_mode,
                case.expected_authorization_source,
                case.expected_write_scope,
            )
            actual = (
                route.review_context,
                route.mode,
                route.authorization_source,
                route.write_scope,
            )
            if actual != expected:
                issues.append(f"{case.id}: authorization expectation drift")
        elif any(
            value is not None
            for value in (
                case.artifact_type,
                case.artifact_subtype,
                case.expected_review_context,
                case.expected_mode,
                case.expected_authorization_source,
                case.expected_write_scope,
            )
        ) or case.secondary_types:
            issues.append(f"{case.id}: non-trigger case carries a route")

    for duplicate in sorted(case_id for case_id, count in counts.items() if count > 1):
        issues.append(f"duplicate case id: {duplicate}")
    return issues


def self_delivery_truth_table() -> tuple[tuple[str, bool, bool, bool, bool], ...]:
    """Expose the complete trusted-input truth table for contract tests."""

    rows: list[tuple[str, bool, bool, bool, bool]] = []
    for origin, write_authorized, current_target, explicit_revision in product(
        ARTIFACT_ORIGINS,
        (False, True),
        (False, True),
        (False, True),
    ):
        provenance = ReviewProvenance(
            artifact_origin=origin,
            current_task_write_authorized=write_authorized,
            target_is_current_task_diff=current_target,
            explicit_revision_requested=explicit_revision,
        )
        route = resolve_review_authorization("code", provenance)
        rows.append(
            (
                origin,
                write_authorized,
                current_target,
                explicit_revision,
                route.review_context == "self-delivery",
            )
        )
    return tuple(rows)
