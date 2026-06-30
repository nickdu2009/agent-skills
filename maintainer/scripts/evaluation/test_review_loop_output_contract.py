#!/usr/bin/env python3
"""Self-tests for review-loop runtime output contract validation."""

from __future__ import annotations

from run_claude_trigger_smoke import validate_protocol_output


def assert_protocol_fails(text: str, expected_issue: str) -> None:
    status, _blocks, issues = validate_protocol_output(text)
    assert status == "fail", issues
    assert any(expected_issue in issue for issue in issues), issues


def assert_protocol_passes(text: str) -> None:
    status, _blocks, issues = validate_protocol_output(text)
    assert status == "pass", issues


COMPLETE_REQUIREMENTS_OUTPUT = """
## Review Result
review_result: issues_found
mode: review-only

## Issues
blocking:
- None
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

[output: requirements-review-loop | completed high | mode:"review-only" review_result:"issues_found" issues:"0 blocking, 0 warning, 0 low-risk" changes:"none" validation:"checked target document" | next:done]
[validate: requirements-review-loop | PASS | checks:contract]
"""


MISSING_MODE_OUTPUT = """
## Review Result
review_result: issues_found

## Clarification Questions
- None

[output: requirements-review-loop | completed high | review_result:"issues_found" issues:"0 blocking, 0 warning, 0 low-risk" changes:"none" validation:"checked target document" | next:done]
[validate: requirements-review-loop | PASS | checks:contract]
"""


MISSING_DESIGN_TYPE_OUTPUT = """
## Review Result
review_result: needs_clarification
mode: review-only

## Clarification Questions
- question: "Who owns retries?"
  why_blocked: "Ownership is undecided."

[output: design-review-loop | completed high | mode:"review-only" review_result:"needs_clarification" issues:"1 blocking, 0 warning, 0 low-risk" changes:"none" validation:"checked target document" | next:clarify]
[validate: design-review-loop | PASS | checks:contract]
"""


MISSING_CLARIFICATION_HEADING_OUTPUT = """
## Review Result
review_result: issues_found
mode: review-only

[output: code-review-loop | completed high | mode:"review-only" review_result:"issues_found" issues:"1 blocking, 0 warning, 0 low-risk" fixes:"none" validation:"checked target file" | next:fix]
[validate: code-review-loop | PASS | checks:contract]
"""


def main() -> int:
    assert_protocol_passes(COMPLETE_REQUIREMENTS_OUTPUT)
    assert_protocol_fails(MISSING_MODE_OUTPUT, "required `mode` field")
    assert_protocol_fails(MISSING_DESIGN_TYPE_OUTPUT, "required `type` field")
    assert_protocol_fails(MISSING_CLARIFICATION_HEADING_OUTPUT, "Clarification Questions")
    print("OK: review-loop output contract self-tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
