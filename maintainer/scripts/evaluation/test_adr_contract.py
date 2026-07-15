#!/usr/bin/env python3
"""Static contract checks for vendor-neutral ADR producer and consumer skills."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = REPO_ROOT / "skills"

GENERIC_SKILLS = (
    "design-before-plan",
    "architecture-design",
    "design-review-loop",
    "implementation-planning",
    "plan-review-loop",
)
PRODUCERS = ("design-before-plan", "architecture-design")
REQUIRED_HEADINGS = (
    "## Context",
    "## Decision Drivers",
    "## Considered Alternatives",
    "## Decision",
    "## Consequences",
    "### Positive",
    "### Negative",
    "## Revisit Conditions",
    "## Links",
)
STATUS_ENUM = "Proposed | Accepted | Deprecated | Superseded"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_adr_template(text: str, path: Path) -> str:
    match = re.search(
        r"```markdown\n(# <ADR-ID>: <title>.*?\n)```",
        text,
        flags=re.DOTALL,
    )
    assert match, f"{path}: missing canonical ADR Markdown template"
    return match.group(1).strip()


def assert_producer_contracts() -> None:
    templates: list[str] = []
    for skill in PRODUCERS:
        path = SKILLS_ROOT / skill / "adr-format.md"
        text = read(path)
        template = extract_adr_template(text, path)
        templates.append(template)
        assert STATUS_ENUM in template, f"{path}: status enum drift"
        for heading in REQUIRED_HEADINGS:
            assert heading in template, f"{path}: missing {heading}"
        assert "ADR-NNNN" in text, f"{path}: missing numeric ADR ID rule"
        assert "ADR-YYYYMMDD-<slug>" in text, f"{path}: missing date-slug ADR ID rule"
        assert "Accepted ADRs use `Supersedes`" in text, f"{path}: missing Accepted relationship rule"
        assert "Proposed ADRs use only `Proposes to supersede`" in text, f"{path}: missing Proposed relationship rule"
    assert templates[0] == templates[1], "producer ADR Markdown templates differ"


def assert_consumer_contracts() -> None:
    review = read(SKILLS_ROOT / "design-review-loop" / "adr-review.md")
    for phrase in (
        "Decision Drivers",
        "realistic alternatives",
        "Positive and negative consequences",
        "Revisit conditions",
        "Accepted ADRs use `Supersedes`",
        "Proposed ADRs use only `Proposes to supersede`",
    ):
        assert phrase.lower() in review.lower(), f"ADR review contract missing {phrase!r}"

    planning = read(SKILLS_ROOT / "implementation-planning" / "upstream-artifacts.md")
    plan_review = read(SKILLS_ROOT / "plan-review-loop" / "upstream-adr-alignment.md")
    for path, text in (
        ("implementation-planning/upstream-artifacts.md", planning),
        ("plan-review-loop/upstream-adr-alignment.md", plan_review),
    ):
        for phrase in ("Accepted", "Proposed", "Deprecated", "Superseded", "historical", "retired", "Supersedes"):
            assert phrase in text, f"{path}: missing activity rule {phrase!r}"

    architecture = read(SKILLS_ROOT / "architecture-design" / "SKILL.md")
    assert re.search(r'adrs:"ADR-0001:[^"]+:Proposed', architecture), (
        "architecture-design compact ADR example must include id + artifact/path + status"
    )


def assert_decoupled_and_compact() -> None:
    for skill in GENERIC_SKILLS:
        skill_dir = SKILLS_ROOT / skill
        main = skill_dir / "SKILL.md"
        line_count = len(read(main).splitlines())
        assert line_count < 500, f"{main}: {line_count} lines exceeds hard limit"
        assert 150 <= line_count <= 250, f"{main}: {line_count} lines misses target 150-250"
        for path in skill_dir.glob("*.md"):
            text = read(path)
            assert not re.search(r"(?i)\bworktrail\b|\.worktrail", text), (
                f"{path}: generic skill contains persistence-specific coupling"
            )


def main() -> int:
    assert_producer_contracts()
    assert_consumer_contracts()
    assert_decoupled_and_compact()
    print("OK: ADR producer, review, planning, and decoupling contracts passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
