#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from skill_test_data import ALL_SKILLS, EXAMPLE_CASES, GLOBAL_RUBRIC_DIMENSIONS, resolve_example


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TRANSCRIPTS_DIR = (
    Path.home()
    / ".cursor"
    / "projects"
    / "Users-duxiaobo-workspaces-nickdu-agent-skills"
    / "agent-transcripts"
)
CRITICAL_GLOBAL_DIMENSIONS: tuple[str, ...] = (
    GLOBAL_RUBRIC_DIMENSIONS[0],
    GLOBAL_RUBRIC_DIMENSIONS[1],
    GLOBAL_RUBRIC_DIMENSIONS[3],
)


@dataclass(frozen=True)
class TranscriptMessage:
    index: int
    role: str
    text: str
    visible_text: str


@dataclass(frozen=True)
class ScoreRule:
    label: str
    positive_patterns: tuple[str, ...]
    strong_negative_patterns: tuple[str, ...] = ()


GLOBAL_SCORE_RULES: dict[str, ScoreRule] = {
    GLOBAL_RUBRIC_DIMENSIONS[0]: ScoreRule(
        label="Scope discipline",
        positive_patterns=(
            r"\bscope\b",
            r"\bboundary\b",
            r"\bworking set\b",
            r"\bin[- ]scope\b",
            r"\bsmallest plausible boundary\b",
            r"范围",
            r"边界",
            r"工作集",
        ),
        strong_negative_patterns=(
            r"whole repo",
            r"entire repository",
            r"scan everything",
            r"全仓",
            r"整个仓库",
        ),
    ),
    GLOBAL_RUBRIC_DIMENSIONS[1]: ScoreRule(
        label="Planning discipline",
        positive_patterns=(
            r"\bgoal\b",
            r"\bassumptions?\b",
            r"\bintended files\b",
            r"\bplanned actions\b",
            r"\bdone\b",
            r"\bnot done\b",
            r"\bnext\b",
            r"目标",
            r"假设",
            r"预计文件",
            r"计划",
            r"done / not done / next",
        ),
        strong_negative_patterns=(
            r"edit first",
            r"patch first",
            r"直接修改",
        ),
    ),
    GLOBAL_RUBRIC_DIMENSIONS[2]: ScoreRule(
        label="Change discipline",
        positive_patterns=(
            r"\bsmallest viable\b",
            r"\bminimal change\b",
            r"\blocal patch\b",
            r"\bpreserve\b",
            r"最小",
            r"局部",
            r"保留现有",
        ),
        strong_negative_patterns=(
            r"broad refactor",
            r"rewrite the whole",
            r"大重构",
            r"整体重写",
        ),
    ),
    GLOBAL_RUBRIC_DIMENSIONS[3]: ScoreRule(
        label="Validation discipline",
        positive_patterns=(
            r"\bvalidate\b",
            r"\btargeted\b",
            r"\bnarrow\b",
            r"\bfocused test\b",
            r"\bverification command\b",
            r"验证",
            r"定向",
            r"窄验证",
            r"受影响范围",
        ),
        strong_negative_patterns=(
            r"full suite",
            r"run everything",
            r"全量测试",
            r"全量构建",
        ),
    ),
    GLOBAL_RUBRIC_DIMENSIONS[4]: ScoreRule(
        label="Uncertainty handling",
        positive_patterns=(
            r"\buncertainty\b",
            r"\bresidual risk\b",
            r"\bopen questions?\b",
            r"\bassumption\b",
            r"不确定",
            r"残余风险",
            r"开放问题",
        ),
        strong_negative_patterns=(
            r"definitely solved",
            r"certainly correct",
            r"完全确定",
        ),
    ),
}


SKILL_SCORE_RULES: dict[str, ScoreRule] = {
    "scoped-tasking": ScoreRule(
        label="scoped-tasking",
        positive_patterns=(
            r"\bscope\b",
            r"\bboundary\b",
            r"\bentry point\b",
            r"\bexpand scope\b",
            r"范围",
            r"边界",
            r"入口点",
            r"扩展范围",
        ),
    ),
    "plan-before-action": ScoreRule(
        label="plan-before-action",
        positive_patterns=(
            r"\bgoal\b",
            r"\bassumptions?\b",
            r"\bintended files\b",
            r"\bplanned actions\b",
            r"\bdone\b",
            r"\bnext\b",
            r"目标",
            r"假设",
            r"计划",
        ),
    ),
    "minimal-change-strategy": ScoreRule(
        label="minimal-change-strategy",
        positive_patterns=(
            r"\bsmallest viable\b",
            r"\blocal patch\b",
            r"\bminimal fix\b",
            r"\bdeferred cleanup\b",
            r"最小改动",
            r"局部修复",
            r"延后清理",
        ),
    ),
    "targeted-validation": ScoreRule(
        label="targeted-validation",
        positive_patterns=(
            r"\btargeted\b",
            r"\bnarrow validation\b",
            r"\bfocused\b",
            r"\bverification command\b",
            r"窄验证",
            r"定向验证",
            r"受影响范围",
        ),
        strong_negative_patterns=(
            r"full suite",
            r"run everything",
            r"全量测试",
        ),
    ),
    "context-budget-awareness": ScoreRule(
        label="context-budget-awareness",
        positive_patterns=(
            r"\bcompress\b",
            r"\bstale hypotheses\b",
            r"\bfresh pass\b",
            r"压缩",
            r"陈旧假设",
            r"重新聚焦",
        ),
    ),
    "read-and-locate": ScoreRule(
        label="read-and-locate",
        positive_patterns=(
            r"\bentry point\b",
            r"\blikely edit points\b",
            r"\bconfirmed locations\b",
            r"\btentative leads\b",
            r"入口点",
            r"可能编辑点",
            r"已确认",
            r"线索",
        ),
    ),
    "safe-refactor": ScoreRule(
        label="safe-refactor",
        positive_patterns=(
            r"\binvariants?\b",
            r"\bbehavior-preserving\b",
            r"\bsmall steps\b",
            r"不变式",
            r"保持行为",
            r"小步",
        ),
    ),
    "bugfix-workflow": ScoreRule(
        label="bugfix-workflow",
        positive_patterns=(
            r"\bsymptom\b",
            r"\bfault domain\b",
            r"\bevidence\b",
            r"\brepro",
            r"症状",
            r"故障域",
            r"证据",
            r"复现",
        ),
    ),
    "multi-agent-protocol": ScoreRule(
        label="multi-agent-protocol",
        positive_patterns=(
            r"\bsubagent\b",
            r"\bparallel\b",
            r"\blow-coupling\b",
            r"\bfindings\b",
            r"\brecommendation\b",
            r"\btier\s*[12]\b",
            r"\bdelegate\b",
            r"\bexplore\b",
            r"\bgate\b",
            r"子代理",
            r"并行",
            r"低耦合",
            r"委派",
            r"探索",
        ),
    ),
    "conflict-resolution": ScoreRule(
        label="conflict-resolution",
        positive_patterns=(
            r"\bconsensus\b",
            r"\bdisagreement\b",
            r"\buncertainty\b",
            r"\badjudication\b",
            r"共识",
            r"分歧",
            r"不确定",
            r"裁决",
        ),
    ),
}


@dataclass(frozen=True)
class ScoreResult:
    score: int
    evidence: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Heuristically score a Cursor transcript against the skill testing rubric."
    )
    parser.add_argument(
        "transcript",
        type=Path,
        nargs="?",
        help="Path to a transcript JSONL file. If omitted, --example-path under the default transcripts directory is used.",
    )
    parser.add_argument(
        "--example",
        choices=[case.file_name for case in EXAMPLE_CASES],
        help="Example scenario used to choose the primary skills under review.",
    )
    parser.add_argument(
        "--skills",
        help="Comma-separated skill names to score instead of deriving them from --example.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--write-report",
        type=Path,
        help="Write the rendered report to the given path.",
    )
    parser.add_argument(
        "--list-examples",
        action="store_true",
        help="List available example identifiers and exit.",
    )
    return parser.parse_args()


def list_examples() -> str:
    lines = ["Available examples:"]
    for case in EXAMPLE_CASES:
        lines.append(f"- {case.file_name}: {case.title}")
    return "\n".join(lines)


def extract_text_parts(message: dict[str, Any]) -> str:
    content = message.get("content", [])
    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "text" and isinstance(item.get("text"), str):
            parts.append(item["text"])
    return "\n".join(parts).strip()


def extract_visible_text(text: str) -> str:
    # Cursor transcripts may contain extra planning/debug prose after the
    # user-visible reply. Prefer the leading user-facing section as evidence.
    marker_match = re.search(r"\n\s*\*\*[^\n]+\*\*", text)
    candidate = text[: marker_match.start()] if marker_match else text
    candidate = candidate.strip()
    return candidate or text.strip()


def load_transcript(path: Path) -> list[TranscriptMessage]:
    messages: list[TranscriptMessage] = []
    for index, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        payload = json.loads(raw_line)
        role = payload.get("role", "unknown")
        message = payload.get("message", {})
        text = extract_text_parts(message)
        messages.append(
            TranscriptMessage(
                index=index,
                role=role,
                text=text,
                visible_text=extract_visible_text(text),
            )
        )
    return messages


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def clamp_to_delimiter(text: str, index: int, delimiters: tuple[str, ...], direction: str) -> int:
    if direction == "left":
        positions = [text.rfind(delimiter, 0, index) for delimiter in delimiters]
        best = max(positions)
        return 0 if best == -1 else best + 1
    positions = [text.find(delimiter, index) for delimiter in delimiters]
    candidates = [position for position in positions if position != -1]
    return len(text) if not candidates else min(candidates) + 1


def extract_snippet(text: str, start: int, end: int, radius: int = 80) -> str:
    delimiters = ("\n", "。", "！", "？", ".", "!", "?")
    left = clamp_to_delimiter(text, start, delimiters, "left")
    right = clamp_to_delimiter(text, end, delimiters, "right")

    if right - left > 220:
        left = max(0, start - radius)
        right = min(len(text), end + radius)

    snippet = normalize_whitespace(text[left:right])
    if left > 0:
        snippet = "..." + snippet
    if right < len(text):
        snippet = snippet + "..."
    return snippet


def compile_matches(messages: list[TranscriptMessage], patterns: tuple[str, ...]) -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    for pattern in patterns:
        for message in messages:
            visible_match = re.search(pattern, message.visible_text, flags=re.IGNORECASE)
            if visible_match:
                snippet = extract_snippet(message.visible_text, visible_match.start(), visible_match.end())
                matches.append((pattern, f"msg {message.index}: `{snippet}`"))
                break

            fallback_match = re.search(pattern, message.text, flags=re.IGNORECASE)
            if fallback_match:
                snippet = extract_snippet(message.text, fallback_match.start(), fallback_match.end())
                matches.append((pattern, f"msg {message.index} fallback: `{snippet}`"))
                break
    return matches


def score_rule(messages: list[TranscriptMessage], rule: ScoreRule) -> ScoreResult:
    positive_matches = compile_matches(messages, rule.positive_patterns)
    negative_matches = compile_matches(messages, rule.strong_negative_patterns)

    if negative_matches and not positive_matches:
        evidence = tuple(
            f"matched negative signal `{pattern}` in {snippet}"
            for pattern, snippet in negative_matches[:3]
        )
        return ScoreResult(score=0, evidence=evidence)
    if len(positive_matches) >= 3:
        evidence = tuple(
            f"matched positive signal `{pattern}` in {snippet}"
            for pattern, snippet in positive_matches[:4]
        )
        return ScoreResult(score=2, evidence=evidence)
    if positive_matches:
        evidence = tuple(
            f"matched positive signal `{pattern}` in {snippet}"
            for pattern, snippet in positive_matches[:3]
        )
        if negative_matches:
            evidence += tuple(
                f"matched caution signal `{pattern}` in {snippet}"
                for pattern, snippet in negative_matches[:2]
            )
        return ScoreResult(score=1, evidence=evidence)
    evidence = ("no strong matching signals found in assistant messages",)
    return ScoreResult(score=0, evidence=evidence)


def derive_skills(args: argparse.Namespace) -> tuple[str, ...]:
    if args.skills:
        skills = tuple(skill.strip() for skill in args.skills.split(",") if skill.strip())
        unknown = [skill for skill in skills if skill not in ALL_SKILLS]
        if unknown:
            joined = ", ".join(sorted(unknown))
            raise ValueError(f"Unknown skills: {joined}")
        return skills
    if args.example:
        return resolve_example(args.example).skills
    raise ValueError("Provide either --example or --skills.")


def summarize_overall(global_scores: dict[str, ScoreResult], skill_scores: dict[str, ScoreResult]) -> str:
    if any(global_scores[dimension].score == 0 for dimension in CRITICAL_GLOBAL_DIMENSIONS):
        return "fail"
    if any(result.score == 0 for result in skill_scores.values()):
        return "fail"
    if any(result.score == 1 for result in global_scores.values()) or any(
        result.score == 1 for result in skill_scores.values()
    ):
        return "conditional pass"
    return "pass"


def render_markdown(
    transcript_path: Path,
    message_count: int,
    assistant_count: int,
    user_count: int,
    example_name: str | None,
    skills: tuple[str, ...],
    global_scores: dict[str, ScoreResult],
    skill_scores: dict[str, ScoreResult],
    overall: str,
) -> str:
    lines = [
        "# Transcript Skill Score",
        "",
        "## Run Metadata",
        "",
        f"- Transcript: `{transcript_path}`",
        f"- Example: `{example_name}`" if example_name else "- Example: not provided",
        f"- Skills under review: {', '.join(f'`{skill}`' for skill in skills)}",
        f"- Messages parsed: {message_count}",
        f"- Assistant messages: {assistant_count}",
        f"- User messages: {user_count}",
        f"- Suggested outcome: `{overall}`",
        "",
        "## Global Rubric Scores",
        "",
        "| Dimension | Score | Evidence |",
        "| --- | --- | --- |",
    ]

    for dimension in GLOBAL_RUBRIC_DIMENSIONS:
        result = global_scores[dimension]
        evidence = "<br>".join(result.evidence)
        lines.append(f"| {dimension} | {result.score} | {evidence} |")

    lines.extend(
        [
            "",
            "## Skill Scores",
            "",
            "| Skill | Score | Evidence |",
            "| --- | --- | --- |",
        ]
    )

    for skill in skills:
        result = skill_scores[skill]
        evidence = "<br>".join(result.evidence)
        lines.append(f"| `{skill}` | {result.score} | {evidence} |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This script is heuristic. Use it to shortlist likely rubric drift, not to replace manual review.",
            "- Scores are based only on assistant text found in the transcript JSONL.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_json(
    transcript_path: Path,
    message_count: int,
    assistant_count: int,
    user_count: int,
    example_name: str | None,
    skills: tuple[str, ...],
    global_scores: dict[str, ScoreResult],
    skill_scores: dict[str, ScoreResult],
    overall: str,
) -> str:
    payload = {
        "transcript": str(transcript_path),
        "example": example_name,
        "skills": list(skills),
        "message_count": message_count,
        "assistant_count": assistant_count,
        "user_count": user_count,
        "overall": overall,
        "global_scores": {
            dimension: {"score": result.score, "evidence": list(result.evidence)}
            for dimension, result in global_scores.items()
        },
        "skill_scores": {
            skill: {"score": result.score, "evidence": list(result.evidence)}
            for skill, result in skill_scores.items()
        },
    }
    return json.dumps(payload, indent=2)


def write_output(path: Path, content: str) -> None:
    output_path = path if path.is_absolute() else REPO_ROOT / path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()

    if args.list_examples:
        print(list_examples())
        return 0

    try:
        skills = derive_skills(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not args.transcript:
        print("Provide a transcript path.", file=sys.stderr)
        return 2

    transcript_path = args.transcript if args.transcript.is_absolute() else REPO_ROOT / args.transcript
    if not transcript_path.exists():
        print(f"Transcript not found: {transcript_path}", file=sys.stderr)
        return 2

    messages = load_transcript(transcript_path)
    message_count = len(messages)
    assistant_count = sum(1 for message in messages if message.role == "assistant")
    user_count = sum(1 for message in messages if message.role == "user")
    assistant_messages = [message for message in messages if message.role == "assistant"]

    global_scores = {
        dimension: score_rule(assistant_messages, GLOBAL_SCORE_RULES[dimension])
        for dimension in GLOBAL_RUBRIC_DIMENSIONS
    }
    skill_scores = {skill: score_rule(assistant_messages, SKILL_SCORE_RULES[skill]) for skill in skills}
    overall = summarize_overall(global_scores, skill_scores)

    example_name = args.example
    if args.format == "json":
        rendered = render_json(
            transcript_path,
            message_count,
            assistant_count,
            user_count,
            example_name,
            skills,
            global_scores,
            skill_scores,
            overall,
        )
    else:
        rendered = render_markdown(
            transcript_path,
            message_count,
            assistant_count,
            user_count,
            example_name,
            skills,
            global_scores,
            skill_scores,
            overall,
        )

    if args.write_report:
        write_output(args.write_report, rendered)

    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
