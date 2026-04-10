#!/usr/bin/env python3
"""Check SKILL.md files for quality criteria.

This script validates that SKILL.md files follow the quality guidelines:
- Description has "what" and "when" triggers
- Third-person phrasing in description
- Body length under 500 lines target
- Shallow reference structure (avoid deep nesting)

Usage:
    python3 maintainer/scripts/analysis/check_skill_quality.py
    python3 maintainer/scripts/analysis/check_skill_quality.py --json
    python3 maintainer/scripts/analysis/check_skill_quality.py --skill scoped-tasking
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"


def parse_skill_file(skill_file: Path) -> dict[str, Any]:
    """Parse a SKILL.md file into frontmatter and body."""
    if not skill_file.exists():
        return {
            "exists": False,
            "frontmatter": {},
            "body": "",
            "body_lines": 0,
        }

    content = skill_file.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Find frontmatter boundaries
    frontmatter_start = -1
    frontmatter_end = -1
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_frontmatter:
                frontmatter_start = i
                in_frontmatter = True
            else:
                frontmatter_end = i
                break

    # Parse frontmatter
    frontmatter = {}
    if frontmatter_start >= 0 and frontmatter_end > frontmatter_start:
        for line in lines[frontmatter_start + 1:frontmatter_end]:
            if ":" in line:
                key, _, value = line.partition(":")
                frontmatter[key.strip()] = value.strip().strip('"')

    # Extract body
    body_start = frontmatter_end + 1 if frontmatter_end >= 0 else 0
    body_lines = lines[body_start:]
    body = "\n".join(body_lines)

    return {
        "exists": True,
        "frontmatter": frontmatter,
        "body": body,
        "body_lines": len(body_lines),
    }


def check_description_has_what_and_when(description: str) -> dict[str, Any]:
    """Check if description contains 'what' and 'when' triggers.

    'What' is the purpose/capability description.
    'When' is the trigger condition (often starts with phrases like
    'when', 'Use when', 'Do not use', etc.).
    """
    desc_lower = description.lower()

    # Check for 'when' indicators
    when_indicators = [
        "when ",
        "use when",
        "do not use",
        "don't use",
        "if ",
        "trigger",
        "activate",
    ]
    has_when = any(indicator in desc_lower for indicator in when_indicators)

    # Check for 'what' indicators (purpose/capability words)
    what_indicators = [
        "find",
        "guide",
        "force",
        "teach",
        "prevent",
        "require",
        "assess",
        "review",
        "compare",
        "narrow",
        "constrain",
        "choose",
        "split",
        "execute",
        "design",
        "clarify",
        "compress",
        "refocus",
        "diagnose",
        "provide",
        "define",
        "validate",
        "verify",
    ]
    has_what = any(indicator in desc_lower for indicator in what_indicators)

    # Simple heuristic: description should be reasonably long
    has_substance = len(description) > 50

    return {
        "pass": has_what and has_when and has_substance,
        "has_what": has_what,
        "has_when": has_when,
        "has_substance": has_substance,
        "length": len(description),
    }


def check_third_person_phrasing(description: str) -> dict[str, Any]:
    """Check if description uses third-person phrasing.

    Third-person descriptions typically:
    - Start with verbs (Find, Guide, Force, etc.) or "Skill that [verb]..."
    - Use present-tense third-person forms (Provides, Diagnoses, etc.)
    - Avoid first-person (I, we, our)
    - Avoid second-person imperatives directed at agent (you should)
    """
    desc_lower = description.lower()

    # Check for first-person indicators (bad)
    first_person_indicators = ["i ", " i ", "we ", " we ", "our ", " our "]
    has_first_person = any(indicator in desc_lower for indicator in first_person_indicators)

    # Check for second-person imperatives (acceptable in skill but prefer third-person in description)
    second_person_indicators = ["you ", " you "]
    has_second_person = any(indicator in desc_lower for indicator in second_person_indicators)

    # Check if starts with action verb (good for third-person)
    action_verbs = [
        "find", "guide", "force", "teach", "prevent", "require",
        "assess", "review", "compare", "narrow", "constrain",
        "choose", "split", "execute", "design", "clarify",
    ]
    starts_with_action = any(description.lower().startswith(verb) for verb in action_verbs)

    # Check for "Skill that [verb]..." pattern (valid third-person)
    starts_with_skill_that = description.lower().startswith("skill that ")

    # Check for third-person verb forms (Provides, Diagnoses, etc.)
    third_person_verbs = [
        "provides", "diagnoses", "compresses", "requires", "guides",
        "forces", "teaches", "prevents", "assesses", "reviews",
        "compares", "narrows", "constrains", "chooses", "splits",
        "executes", "designs", "clarifies", "defines", "ensures",
        "triggers", "activates", "loads", "validates", "verifies",
    ]
    starts_with_third_person_verb = any(
        description.lower().startswith(verb) for verb in third_person_verbs
    )

    is_third_person = (
        not has_first_person
        and (starts_with_action or starts_with_skill_that or starts_with_third_person_verb)
    )

    return {
        "pass": is_third_person,
        "has_first_person": has_first_person,
        "has_second_person": has_second_person,
        "starts_with_action": starts_with_action,
        "starts_with_skill_that": starts_with_skill_that,
        "starts_with_third_person_verb": starts_with_third_person_verb,
    }


def check_body_length_under_500(body_lines: int) -> dict[str, Any]:
    """Check if body is under 500 lines (target guideline)."""
    return {
        "pass": body_lines <= 500,
        "body_lines": body_lines,
        "over_by": max(0, body_lines - 500),
    }


def check_shallow_reference_structure(body: str) -> dict[str, Any]:
    """Check for shallow reference structure.

    Avoid deep nesting like:
    - Too many nested lists (####, #####, etc.)
    - Deeply nested bullet points
    - Complex cross-references

    This is a heuristic check.
    """
    lines = body.splitlines()

    # Count heading levels
    max_heading_level = 0
    for line in lines:
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            max_heading_level = max(max_heading_level, level)

    # Count max bullet indentation
    max_bullet_indent = 0
    for line in lines:
        if line.lstrip().startswith(("-", "*", "+")):
            indent = len(line) - len(line.lstrip())
            max_bullet_indent = max(max_bullet_indent, indent)

    # Heuristic: shallow structure means:
    # - Heading level <= 3 (###)
    # - Bullet indent <= 4 spaces (one level)
    is_shallow = max_heading_level <= 3 and max_bullet_indent <= 4

    return {
        "pass": is_shallow,
        "max_heading_level": max_heading_level,
        "max_bullet_indent": max_bullet_indent,
    }


def check_skill(skill_name: str, skill_file: Path) -> dict[str, Any]:
    """Run all quality checks on a skill file."""
    parsed = parse_skill_file(skill_file)

    if not parsed["exists"]:
        return {
            "skill_name": skill_name,
            "exists": False,
            "checks": {},
            "overall_pass": False,
        }

    description = parsed["frontmatter"].get("description", "")

    checks = {
        "description_what_when": check_description_has_what_and_when(description),
        "third_person": check_third_person_phrasing(description),
        "body_length": check_body_length_under_500(parsed["body_lines"]),
        "shallow_structure": check_shallow_reference_structure(parsed["body"]),
    }

    overall_pass = all(check["pass"] for check in checks.values())

    return {
        "skill_name": skill_name,
        "exists": True,
        "description": description,
        "body_lines": parsed["body_lines"],
        "checks": checks,
        "overall_pass": overall_pass,
    }


def main() -> None:
    """Run quality checks on all or selected skills."""
    parser = argparse.ArgumentParser(
        description="Check SKILL.md files for quality criteria"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of human-readable format",
    )
    parser.add_argument(
        "--skill",
        type=str,
        help="Check only the specified skill",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Show detailed explanations for why checks fail with examples",
    )
    args = parser.parse_args()

    if not SKILLS_DIR.exists():
        print(f"Error: Skills directory not found: {SKILLS_DIR}")
        return

    # Collect skills to check
    skills_to_check = []
    if args.skill:
        skill_file = SKILLS_DIR / args.skill / "SKILL.md"
        if skill_file.exists():
            skills_to_check.append((args.skill, skill_file))
        else:
            print(f"Error: Skill not found: {args.skill}")
            return
    else:
        for skill_dir in sorted(SKILLS_DIR.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skills_to_check.append((skill_dir.name, skill_file))

    # Run checks
    results = []
    for skill_name, skill_file in skills_to_check:
        result = check_skill(skill_name, skill_file)
        results.append(result)

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 80)
        print("SKILL.md Quality Check")
        print("=" * 80)
        print()

        pass_count = sum(1 for r in results if r.get("overall_pass", False))
        total_count = len(results)

        print(f"Overall: {pass_count}/{total_count} skills pass all quality checks")
        print()

        # Show failing skills
        failing_skills = [r for r in results if not r.get("overall_pass", False)]
        if failing_skills:
            print("Skills with quality issues:")
            print()
            for result in failing_skills:
                print(f"  {result['skill_name']}:")
                checks = result.get("checks", {})
                description = result.get("description", "")

                if not checks.get("description_what_when", {}).get("pass"):
                    print("    ✗ Description missing 'what' or 'when' triggers")
                    dww = checks["description_what_when"]
                    print(f"      has_what={dww['has_what']}, has_when={dww['has_when']}, "
                          f"length={dww['length']}")
                    if args.explain:
                        print()
                        print("      Explanation:")
                        print("        'What' = purpose/capability words (find, guide, prevent, etc.)")
                        print("        'When' = trigger conditions (when, use when, if, trigger, etc.)")
                        print("        Current description:", description[:100] + "..." if len(description) > 100 else description)
                        print()
                        print("      Examples of good descriptions:")
                        print("        ✓ 'Find relevant files when edit points are unknown'")
                        print("        ✓ 'Prevent scope creep when diff grows beyond task'")
                        print()

                if not checks.get("third_person", {}).get("pass"):
                    print("    ✗ Description not in third-person")
                    tp = checks["third_person"]
                    print(f"      has_first_person={tp['has_first_person']}, "
                          f"starts_with_action={tp.get('starts_with_action', False)}")
                    if args.explain:
                        print()
                        print("      Explanation:")
                        print("        Third-person phrasing uses:")
                        print("          - Action verbs: 'Find...', 'Guide...', 'Prevent...'")
                        print("          - 'Skill that [verb]...': 'Skill that diagnoses...'")
                        print("          - Third-person verbs: 'Provides...', 'Diagnoses...', 'Compresses...'")
                        print("        Current description:", description[:100] + "..." if len(description) > 100 else description)
                        print()
                        print("      Examples of valid third-person:")
                        print("        ✓ 'Find relevant files and edit points' (action verb)")
                        print("        ✓ 'Skill that diagnoses bugs efficiently' (Skill that...)")
                        print("        ✓ 'Provides protocol for parallel execution' (third-person verb)")
                        print()
                        print("      Examples of INVALID (imperative):")
                        print("        ✗ 'Diagnose and fix bugs' (imperative, not third-person)")
                        print("        ✗ 'Review your code for issues' (second-person)")
                        print()

                if not checks.get("body_length", {}).get("pass"):
                    bl = checks["body_length"]
                    print(f"    ✗ Body over 500 lines: {bl['body_lines']} lines "
                          f"(over by {bl['over_by']})")
                    if args.explain:
                        print()
                        print("      Explanation:")
                        print("        Target guideline: SKILL.md body should be under 500 lines")
                        print("        Consider splitting large sections into sidecar files")
                        print("        Use progressive disclosure: link to details rather than inline")
                        print()

                if not checks.get("shallow_structure", {}).get("pass"):
                    ss = checks["shallow_structure"]
                    print(f"    ✗ Deep reference structure: "
                          f"max_heading={ss['max_heading_level']}, "
                          f"max_indent={ss['max_bullet_indent']}")
                    if args.explain:
                        print()
                        print("      Explanation:")
                        print("        Shallow structure guidelines:")
                        print("          - Heading level ≤ 3 (use #, ##, ### only)")
                        print("          - Bullet indent ≤ 4 spaces (max one level of nesting)")
                        print(f"        Current structure: heading={ss['max_heading_level']}, indent={ss['max_bullet_indent']}")
                        print()

                print()

        # Show passing skills
        passing_skills = [r for r in results if r.get("overall_pass", False)]
        if passing_skills:
            print(f"Skills passing all checks ({len(passing_skills)}):")
            for result in passing_skills:
                print(f"  ✓ {result['skill_name']} ({result['body_lines']} lines)")
            print()


if __name__ == "__main__":
    main()
