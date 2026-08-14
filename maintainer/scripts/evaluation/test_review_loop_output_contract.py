#!/usr/bin/env python3
"""Self-tests for unified artifact review output validation."""

from __future__ import annotations

from protocol_output_validation import validate_protocol_output


def assert_protocol_fails(text: str, expected_issue: str) -> None:
    status, _blocks, issues = validate_protocol_output(text)
    assert status == "fail", issues
    assert any(expected_issue in issue for issue in issues), issues


def assert_protocol_passes(text: str) -> None:
    status, _blocks, issues = validate_protocol_output(text)
    assert status == "pass", issues


COMPLETE_REQUESTED_OUTPUT = """
## Review Result
review_result: issues_found
artifact_type: requirements
artifact_subtype: prd
secondary_types: []
review_context: requested
mode: review-only
authorization_source: none
write_scope: none

## Issues
blocking:
- severity: blocking
  area: "acceptance criteria"
  problem: "The failure behavior is unspecified."
  impact: "The implementation cannot be verified deterministically."
  required_fix: "Define the observable failure response."
warning:
- None
low-risk:
- None

## Changes Made
- None

## Validation
- "checked target document"

## Residual Assumptions
- None

## Clarification Questions
- None

[output: artifact-review-loop | completed high | artifact_type:"requirements" artifact_subtype:"prd" secondary_types:"none" review_context:"requested" mode:"review-only" authorization_source:"none" write_scope:"none" review_result:"issues_found" issues:"1 blocking, 0 warning, 0 low-risk" changes:"none" validation:"checked target document" | next:done]
[validate: artifact-review-loop | PASS | checks:contract]
"""


COMPLETE_SELF_DELIVERY_OUTPUT = """
## Review Result
review_result: clean
artifact_type: code
artifact_subtype: working-tree-diff
secondary_types: [tests]
review_context: self-delivery
mode: review-and-revise
authorization_source: inherited-current-task
write_scope: current-task-diff

## Issues
blocking:
- None
warning:
- None
low-risk:
- None

## Changes Made
- file: "src/current-task.py"
  summary: "Fixed the reviewed defect."

## Validation
- "targeted test passed"

## Residual Assumptions
- None

## Clarification Questions
- None

[output: artifact-review-loop | completed high | artifact_type:"code" artifact_subtype:"working-tree-diff" secondary_types:"tests" review_context:"self-delivery" mode:"review-and-revise" authorization_source:"inherited-current-task" write_scope:"current-task-diff" review_result:"clean" issues:"none" changes:"fixed current task diff" validation:"targeted test passed" | next:done]
[validate: artifact-review-loop | PASS | checks:contract]
"""


COMPLETE_EXPLICIT_REVISION_OUTPUT = """
## Review Result
review_result: clean
artifact_type: design
artifact_subtype: adr-rfc
secondary_types: []
review_context: requested
mode: review-and-revise
authorization_source: explicit-user-request
write_scope: reviewed-artifact

## Issues
blocking:
- None
warning:
- None
low-risk:
- None

## Changes Made
- file: "docs/adr.md"
  summary: "Added the missing consequence."

## Validation
- "document contract passed"

## Residual Assumptions
- None

## Clarification Questions
- None

[output: artifact-review-loop | completed high | artifact_type:"design" artifact_subtype:"adr-rfc" secondary_types:"none" review_context:"requested" mode:"review-and-revise" authorization_source:"explicit-user-request" write_scope:"reviewed-artifact" review_result:"clean" issues:"none" changes:"updated primary artifact" validation:"document contract passed" | next:done]
[validate: artifact-review-loop | PASS | checks:contract]
"""


CANONICAL_NAMED_OUTPUT = """
[task-validation: PASS | clarity:✓ | scope:✓ | safety:✓ | skill_match:✓ | action:proceed]
[triggers: targeted-validation:trigger | scoped-tasking:defer]
[precheck: targeted-validation | result:PASS | checks:changed-surface-known]
[output: targeted-validation | status:completed | confidence:high | command:"run focused test" reason:"covers changed path" residual_risk:"full suite not run" | next:done]
[validate: targeted-validation | result:PASS | checks:command reason residual_risk]
[drop: targeted-validation | reason:"validation completed" | active:none]
"""


CLEAN_WITH_ASSUMPTIONS_OUTPUT = COMPLETE_EXPLICIT_REVISION_OUTPUT.replace(
    "review_result: clean",
    "review_result: clean_with_assumptions",
).replace(
    'review_result:"clean"',
    'review_result:"clean_with_assumptions"',
).replace(
    "## Residual Assumptions\n- None",
    """## Residual Assumptions
- assumption: \"The owner list is current.\"
  validation_method: \"Confirm it with the repository owners file.\"""",
)


CLEAN_WITH_LOW_RISK_OUTPUT = CLEAN_WITH_ASSUMPTIONS_OUTPUT.replace(
    "low-risk:\n- None",
    """low-risk:
- severity: low-risk
  area: \"documentation freshness\"
  problem: \"The owner list may be one day stale.\"
  impact: \"A follow-up reviewer may contact an outdated owner.\"
  required_fix: \"Validate the owner list before release.\"""",
).replace(
    'issues:"none"',
    'issues:"0 blocking, 0 warning, 1 low-risk"',
)


NEEDS_CLARIFICATION_OUTPUT = COMPLETE_REQUESTED_OUTPUT.replace(
    "review_result: issues_found",
    "review_result: needs_clarification",
).replace(
    'review_result:"issues_found"',
    'review_result:"needs_clarification"',
).replace(
    "## Clarification Questions\n- None",
    """## Clarification Questions
- question: \"What is the required failure response?\"
  why_blocked: \"Without it the acceptance criterion is not testable.\"""",
)


LEGACY_V1_PASS = """
[task-input-validation]
clarity: sufficient
scope: bounded
safety: safe
skill_match: matched
result: PASS
action: proceed
[/task-input-validation]
[trigger-evaluation]
evaluated: none
activated_now: none
deferred: none
[/trigger-evaluation]
"""


def main() -> int:
    explicit_code_revision = (
        COMPLETE_EXPLICIT_REVISION_OUTPUT.replace(
            "artifact_type: design", "artifact_type: code"
        )
        .replace("artifact_subtype: adr-rfc", "artifact_subtype: working-tree-diff")
        .replace('artifact_type:"design"', 'artifact_type:"code"')
        .replace('artifact_subtype:"adr-rfc"', 'artifact_subtype:"working-tree-diff"')
        .replace("write_scope: reviewed-artifact", "write_scope: reviewed-implementation")
        .replace('write_scope:"reviewed-artifact"', 'write_scope:"reviewed-implementation"')
    )
    assert_protocol_passes(COMPLETE_REQUESTED_OUTPUT)
    assert_protocol_passes(COMPLETE_SELF_DELIVERY_OUTPUT)
    assert_protocol_passes(COMPLETE_EXPLICIT_REVISION_OUTPUT)
    assert_protocol_passes(explicit_code_revision)
    assert_protocol_passes(CLEAN_WITH_ASSUMPTIONS_OUTPUT)
    assert_protocol_passes(NEEDS_CLARIFICATION_OUTPUT)
    assert_protocol_passes(CANONICAL_NAMED_OUTPUT)
    assert_protocol_fails(
        COMPLETE_REQUESTED_OUTPUT.replace(' mode:"review-only"', ""),
        "required `mode` field",
    )
    assert_protocol_fails(
        COMPLETE_REQUESTED_OUTPUT.replace("## Clarification Questions", "## Questions"),
        "Clarification Questions",
    )
    assert_protocol_fails(
        COMPLETE_REQUESTED_OUTPUT.replace("artifact_subtype: prd", "artifact_subtype: adr-rfc").replace(
            'artifact_subtype:"prd"', 'artifact_subtype:"adr-rfc"'
        ),
        "invalid for",
    )
    assert_protocol_fails(
        COMPLETE_REQUESTED_OUTPUT.replace("- None\n\n## Validation", '- file: "prd.md"\n  summary: "edited"\n\n## Validation').replace(
            'changes:"none"', 'changes:"edited"'
        ),
        "must report no changes",
    )
    assert_protocol_fails(
        COMPLETE_SELF_DELIVERY_OUTPUT.replace(
            "authorization_source: inherited-current-task",
            "authorization_source: explicit-user-request",
        ).replace(
            'authorization_source:"inherited-current-task"',
            'authorization_source:"explicit-user-request"',
        ),
        "strict revision authority",
    )
    assert_protocol_fails(
        COMPLETE_EXPLICIT_REVISION_OUTPUT.replace(
            "write_scope: reviewed-artifact", "write_scope: none"
        ).replace('write_scope:"reviewed-artifact"', 'write_scope:"none"'),
        "exact explicit write scope",
    )
    assert_protocol_fails(
        explicit_code_revision.replace(
            "write_scope: reviewed-implementation", "write_scope: reviewed-artifact"
        ).replace(
            'write_scope:"reviewed-implementation"', 'write_scope:"reviewed-artifact"'
        ),
        "exact explicit write scope",
    )
    assert_protocol_fails(
        COMPLETE_REQUESTED_OUTPUT.replace(
            'issues:"1 blocking, 0 warning, 0 low-risk"',
            'issues:"0 blocking, 0 warning, 0 low-risk"',
        ),
        "counts do not match",
    )
    assert_protocol_fails(
        COMPLETE_REQUESTED_OUTPUT.replace(
            "review_result: issues_found", "review_result: clean"
        ).replace(
            'review_result:"issues_found"', 'review_result:"clean"'
        ),
        "clean review_result requires zero",
    )
    assert_protocol_fails(
        COMPLETE_REQUESTED_OUTPUT.replace(
            "required_fix: \"Define the observable failure response.\"",
            'required_fix: ""',
        ),
        "required_fix:` value must be nonempty",
    )
    assert_protocol_fails(
        COMPLETE_REQUESTED_OUTPUT.replace(
            "- severity: blocking", "- severity: warning"
        ),
        "finding severity must be 'blocking'",
    )
    assert_protocol_fails(
        COMPLETE_SELF_DELIVERY_OUTPUT.replace(
            "blocking:\n- None\nwarning:\n- None\nlow-risk:\n- None",
            "- None",
        ),
        "exactly three buckets",
    )
    assert_protocol_fails(
        COMPLETE_SELF_DELIVERY_OUTPUT.replace(
            "## Issues\nblocking:", "## Issues - None\nblocking:"
        ),
        "missing `## Issues` section",
    )
    assert_protocol_fails(
        CLEAN_WITH_LOW_RISK_OUTPUT,
        "clean_with_assumptions review_result requires zero",
    )
    assert_protocol_fails(
        CLEAN_WITH_LOW_RISK_OUTPUT.replace(
            "low-risk:\n- severity: low-risk",
            "low-risk:\n- None\nwarning-extra:\n- severity: warning",
        ),
        "exactly three buckets",
    )
    assert_protocol_fails(
        CLEAN_WITH_ASSUMPTIONS_OUTPUT.replace(
            "validation_method: \"Confirm it with the repository owners file.\"",
            'validation_method: ""',
        ),
        "validation_method:` value must be nonempty",
    )
    assert_protocol_fails(
        NEEDS_CLARIFICATION_OUTPUT.replace(
            "## Clarification Questions\n- question: \"What is the required failure response?\"\n  why_blocked: \"Without it the acceptance criterion is not testable.\"",
            "## Clarification Questions\n- None",
        ),
        "requires at least one structured question",
    )
    assert_protocol_fails(
        NEEDS_CLARIFICATION_OUTPUT.replace(
            "blocking:\n- severity: blocking\n  area: \"acceptance criteria\"\n  problem: \"The failure behavior is unspecified.\"\n  impact: \"The implementation cannot be verified deterministically.\"\n  required_fix: \"Define the observable failure response.\"",
            "blocking:\n- None",
        ).replace(
            'issues:"1 blocking, 0 warning, 0 low-risk"',
            'issues:"none"',
        ),
        "needs_clarification review_result requires at least one finding",
    )
    assert_protocol_fails(
        LEGACY_V1_PASS
        + CLEAN_WITH_LOW_RISK_OUTPUT.replace(
            "low-risk:\n- severity: low-risk",
            "blocking:\n- severity: blocking",
        ),
        "Issues section must contain exactly three buckets",
    )
    assert_protocol_fails(
        LEGACY_V1_PASS + "\n[output: artifact-review-loop]\n",
        "marker count does not match parsed blocks",
    )
    assert_protocol_fails(
        "[validate: artifact-review-loop | PASS | checks:contract]",
        "requires exactly one parsed compact output block",
    )
    assert_protocol_fails(
        "## Review Result\nreview_result: clean",
        "requires exactly one parsed compact output block",
    )
    assert_protocol_passes(
        CANONICAL_NAMED_OUTPUT + "\n## Validation\n- targeted test passed\n"
    )
    assert_protocol_fails(
        COMPLETE_SELF_DELIVERY_OUTPUT.replace(
            "[output: artifact-review-loop | completed high",
            "[output: artifact-review-loop | partial high",
        ),
        "status must be `completed`",
    )
    assert_protocol_fails(
        COMPLETE_SELF_DELIVERY_OUTPUT.replace(
            "[output: artifact-review-loop | completed high",
            "[output: artifact-review-loop | completed unknown",
        ),
        "confidence must be high, medium, or low",
    )
    assert_protocol_fails(
        COMPLETE_SELF_DELIVERY_OUTPUT.replace(
            "[output: artifact-review-loop | completed high",
            "[output: artifact-review-loop | completed",
        ),
        "confidence must be high, medium, or low",
    )
    assert_protocol_fails(
        COMPLETE_SELF_DELIVERY_OUTPUT.replace(
            "[validate: artifact-review-loop | PASS | checks:contract]",
            "[validate: artifact-review-loop | FAIL | checks:contract]",
        ),
        "validation result must be `PASS`",
    )
    assert_protocol_fails(
        COMPLETE_SELF_DELIVERY_OUTPUT.replace(
            "checks:contract", "checks:not-contract"
        ),
        "checks must be exactly `contract`",
    )
    assert_protocol_fails(
        COMPLETE_SELF_DELIVERY_OUTPUT.replace(" | checks:contract", ""),
        "checks must be exactly `contract`",
    )
    assert_protocol_fails(
        COMPLETE_SELF_DELIVERY_OUTPUT
        + "\n[validate: artifact-review-loop | PASS | checks:contract]\n",
        "exactly one matching validation block",
    )
    print("OK: artifact review output contract self-tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
