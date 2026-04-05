#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Run representative Claude Code trigger smoke tests in non-interactive mode.

This script mirrors the canonical `skills/` tree into clean temporary
workspaces under `.claude/skills/` and invokes `claude -p` against one
representative case per skill. Most cases use natural-language prompts from
`maintainer/data/trigger_test_data.py`; a small number use slash invocation
because they depend on prior session state or are otherwise not faithful to
single-turn auto-trigger testing.

The goal is not perfect automated scoring. Instead, the script provides:

- a reproducible clean-workspace harness
- captured stdout/stderr for each case
- a lightweight `pass` / `warn` / `fail` heuristic
- a JSON report under `maintainer/reports/runs/`

Usage:
  python3 maintainer/scripts/evaluation/run_claude_trigger_smoke.py
  python3 maintainer/scripts/evaluation/run_claude_trigger_smoke.py --list-cases
  python3 maintainer/scripts/evaluation/run_claude_trigger_smoke.py --case phase-execute
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
DATA_DIR = REPO_ROOT / "maintainer" / "data"
REPORTS_DIR = REPO_ROOT / "maintainer" / "reports" / "runs"

sys.path.insert(0, str(DATA_DIR))

from skill_test_data import ALL_SKILLS
from trigger_test_data import TriggerCase, resolve_trigger_case


CaseStrategy = Literal["auto", "slash"]
CaseStatus = Literal["pass", "warn", "fail"]


@dataclass(frozen=True)
class SmokeCase:
    id: str
    skill: str | None
    strategy: CaseStrategy
    budget_usd: float | None = None
    source_case_id: str | None = None
    prompt_override: str | None = None
    timeout_seconds: int = 180
    expected_patterns: tuple[str, ...] = ()
    forbidden_patterns: tuple[str, ...] = ()
    notes: str = ""

    def resolved_prompt(self) -> str:
        if self.prompt_override is not None:
            prompt = self.prompt_override
        elif self.source_case_id is not None:
            prompt = resolve_trigger_case(self.source_case_id).prompt
        else:
            raise ValueError(f"{self.id} has no prompt source")

        if self.strategy == "slash":
            if not self.skill:
                raise ValueError(f"{self.id} uses slash strategy but has no skill")
            return f"/{self.skill} {prompt}"
        return prompt

    def trigger_case(self) -> TriggerCase | None:
        if self.source_case_id is None:
            return None
        return resolve_trigger_case(self.source_case_id)


@dataclass
class CaseResult:
    id: str
    skill: str | None
    strategy: CaseStrategy
    prompt: str
    budget_usd: float | None
    returncode: int
    elapsed_seconds: float
    status: CaseStatus
    matched_patterns: list[str]
    forbidden_hits: list[str]
    mentioned_skills: list[str]
    notes: str
    workspace: str | None
    stdout: str
    stderr: str


REPRESENTATIVE_CASES: tuple[SmokeCase, ...] = (
    SmokeCase(
        id="bugfix-workflow",
        skill="bugfix-workflow",
        strategy="auto",
        source_case_id="bug-explicit",
        expected_patterns=(r"bugfix-workflow", r"\bsymptom\b", r"\brepro", r"\bfault domain\b"),
    ),
    SmokeCase(
        id="safe-refactor",
        skill="safe-refactor",
        strategy="auto",
        source_case_id="refactor-explicit",
        expected_patterns=(r"safe-refactor", r"\bextract\b", r"\bshared helper\b", r"\bduplicate\b"),
    ),
    SmokeCase(
        id="plan-before-action",
        skill="plan-before-action",
        strategy="auto",
        source_case_id="multi-file-uncertain",
        expected_patterns=(r"plan-before-action", r"multiple files", r"\bassum", r"\bplan\b"),
    ),
    SmokeCase(
        id="scoped-tasking",
        skill="scoped-tasking",
        strategy="auto",
        source_case_id="broad-request-small-surface",
        expected_patterns=(r"scoped-tasking", r"\bscope\b", r"\bboundary\b"),
    ),
    SmokeCase(
        id="minimal-change-strategy",
        skill="minimal-change-strategy",
        strategy="auto",
        source_case_id="diff-growing-beyond-task",
        expected_patterns=(r"minimal-change-strategy", r"minimal", r"undo the extra changes", r"smallest"),
    ),
    SmokeCase(
        id="targeted-validation",
        skill="targeted-validation",
        strategy="auto",
        source_case_id="what-to-test-after-patch",
        expected_patterns=(r"targeted-validation", r"\btargeted\b", r"\bfocused\b", r"without running the full"),
    ),
    SmokeCase(
        id="read-and-locate",
        skill="read-and-locate",
        strategy="auto",
        source_case_id="unfamiliar-codebase",
        expected_patterns=(r"read-and-locate", r"\bfind\b", r"\bsearch\b", r"where that code lives"),
    ),
    SmokeCase(
        id="context-budget-awareness",
        skill="context-budget-awareness",
        strategy="slash",
        prompt_override="We have been circling for a while. Summarize what we know and what is still unclear. Keep it short.",
        expected_patterns=(r"compressed", r"current state", r"what i know", r"working set", r"still unclear"),
        notes="Uses slash invocation because single-turn auto-trigger lacks genuine session history.",
    ),
    SmokeCase(
        id="multi-agent-protocol",
        skill="multi-agent-protocol",
        strategy="slash",
        prompt_override="Investigate auth middleware, session storage, and role checking in parallel. Keep it short.",
        expected_patterns=(r"\bsubagents?\b", r"\bparallel\b", r"\bsynthesis\b", r"\bconclusion\b"),
        notes="Uses slash invocation because direct load is more stable than one-shot auto-trigger in a clean temp workspace.",
    ),
    SmokeCase(
        id="conflict-resolution",
        skill="conflict-resolution",
        strategy="auto",
        source_case_id="conflicting-subagent-results",
        expected_patterns=(r"\bdisagreement\b", r"\bevidence\b", r"\bclaim\b", r"\bsubagent\b"),
    ),
    SmokeCase(
        id="phase-plan",
        skill="phase-plan",
        strategy="auto",
        source_case_id="plan-large-migration",
        expected_patterns=(r"\bwave\b", r"\bphase\b", r"\bparallel\b", r"phase1-plan\.yaml"),
    ),
    SmokeCase(
        id="phase-execute",
        skill="phase-execute",
        strategy="auto",
        source_case_id="execute-wave",
        expected_patterns=(r"phase3-plan\.yaml", r"execution framework", r"\bwave 2\b", r"\bplan file\b"),
    ),
    SmokeCase(
        id="phase-contract-tools",
        skill="phase-contract-tools",
        strategy="auto",
        source_case_id="contract-tools-direct",
        expected_patterns=(r"\bvalidator\b", r"validation error", r"\bschema\b", r"validate_phase_execution_schema"),
    ),
    SmokeCase(
        id="no-trigger-control",
        skill=None,
        strategy="auto",
        source_case_id="feature-not-bug",
        expected_patterns=(r"not a web application", r"not.*application", r"not.*settings page", r"not.*ui"),
        notes="Negative control: no skill should be required for this repository context.",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run representative Claude Code trigger smoke tests in clean temporary workspaces."
    )
    parser.add_argument(
        "--case",
        action="append",
        dest="cases",
        help="Run only the named representative case. Repeat to run multiple cases.",
    )
    parser.add_argument(
        "--list-cases",
        action="store_true",
        help="List the representative case IDs and exit.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional Claude model alias or full name. Defaults to the Claude CLI's configured model.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON report path. Defaults to maintainer/reports/runs/claude-trigger-smoke-<timestamp>.json.",
    )
    parser.add_argument(
        "--max-budget-usd",
        type=float,
        default=None,
        help="Optional budget cap passed through to Claude for every selected case. Defaults to no explicit budget limit.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=None,
        help="Override the per-case timeout for all selected cases.",
    )
    parser.add_argument(
        "--keep-workspaces",
        action="store_true",
        help="Keep each temporary case workspace instead of deleting it after capture.",
    )
    return parser.parse_args()


def selected_cases(case_ids: list[str] | None) -> list[SmokeCase]:
    by_id = {case.id: case for case in REPRESENTATIVE_CASES}
    if not case_ids:
        return list(REPRESENTATIVE_CASES)

    resolved: list[SmokeCase] = []
    for case_id in case_ids:
        try:
            resolved.append(by_id[case_id])
        except KeyError as exc:
            available = ", ".join(sorted(by_id))
            raise KeyError(f"Unknown case '{case_id}'. Available: {available}") from exc
    return resolved


def default_output_path() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return REPORTS_DIR / f"claude-trigger-smoke-{timestamp}.json"


def ensure_claude_available() -> str:
    claude_path = shutil.which("claude")
    if claude_path is None:
        raise RuntimeError("`claude` CLI not found in PATH.")
    return claude_path


def mentioned_skills(text: str) -> list[str]:
    hits: list[str] = []
    for skill in ALL_SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            hits.append(skill)
    return hits


def classify_result(case: SmokeCase, returncode: int, output_text: str) -> tuple[CaseStatus, list[str], list[str], list[str]]:
    matched_patterns = [
        pattern for pattern in case.expected_patterns
        if re.search(pattern, output_text, re.IGNORECASE | re.DOTALL)
    ]
    forbidden_hits = [
        pattern for pattern in case.forbidden_patterns
        if re.search(pattern, output_text, re.IGNORECASE | re.DOTALL)
    ]
    skill_hits = mentioned_skills(output_text)

    if returncode != 0:
        return "fail", matched_patterns, forbidden_hits, skill_hits

    if forbidden_hits:
        return "fail", matched_patterns, forbidden_hits, skill_hits

    if case.skill is None:
        if matched_patterns and not skill_hits:
            return "pass", matched_patterns, forbidden_hits, skill_hits
        if matched_patterns:
            return "warn", matched_patterns, forbidden_hits, skill_hits
        return "warn", matched_patterns, forbidden_hits, skill_hits

    if matched_patterns:
        return "pass", matched_patterns, forbidden_hits, skill_hits

    return "warn", matched_patterns, forbidden_hits, skill_hits


def create_workspace(root: Path, keep: bool) -> tuple[Path, str | None]:
    if keep:
        workspace = Path(tempfile.mkdtemp(prefix="claude-trigger-smoke-"))
        workspace_hint = str(workspace)
    else:
        workspace = root
        workspace_hint = None

    target = workspace / ".claude" / "skills"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SKILLS_DIR, target)
    return workspace, workspace_hint


def run_case(claude_path: str, case: SmokeCase, model: str | None, timeout_override: int | None, budget_override: float | None, keep_workspaces: bool) -> CaseResult:
    if keep_workspaces:
        workspace, workspace_hint = create_workspace(Path("."), keep=True)
        cleanup_needed = False
    else:
        temp_root = Path(tempfile.mkdtemp(prefix="claude-trigger-smoke-"))
        workspace, workspace_hint = create_workspace(temp_root, keep=False)
        cleanup_needed = True

    prompt = case.resolved_prompt()
    timeout_seconds = timeout_override if timeout_override is not None else case.timeout_seconds
    budget_usd = budget_override if budget_override is not None else case.budget_usd

    command = [
        claude_path,
        "-p",
        "--output-format",
        "text",
        "--permission-mode",
        "dontAsk",
        "--no-session-persistence",
        prompt,
    ]
    if model:
        command[2:2] = ["--model", model]
    if budget_usd is not None:
        command[2:2] = ["--max-budget-usd", f"{budget_usd:.2f}"]

    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\nTimeout after {timeout_seconds} seconds."
    finally:
        elapsed = time.perf_counter() - started
        if cleanup_needed:
            shutil.rmtree(workspace, ignore_errors=True)

    output_text = stdout if stdout.strip() else stderr
    status, matched, forbidden_hits, skill_hits = classify_result(case, returncode, output_text)

    return CaseResult(
        id=case.id,
        skill=case.skill,
        strategy=case.strategy,
        prompt=prompt,
        budget_usd=budget_usd,
        returncode=returncode,
        elapsed_seconds=round(elapsed, 3),
        status=status,
        matched_patterns=matched,
        forbidden_hits=forbidden_hits,
        mentioned_skills=skill_hits,
        notes=case.notes or (case.trigger_case().notes if case.trigger_case() else ""),
        workspace=workspace_hint,
        stdout=stdout,
        stderr=stderr,
    )


def write_report(output_path: Path, cases: list[SmokeCase], results: list[CaseResult], model: str | None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now().isoformat(),
        "cwd": str(REPO_ROOT),
        "model": model or "cli-default",
        "suite": "representative",
        "cases": [asdict(result) for result in results],
        "selected_case_ids": [case.id for case in cases],
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def print_summary(results: list[CaseResult], output_path: Path) -> None:
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for result in results:
        counts[result.status] += 1
        label = result.skill or "control"
        print(
            f"[{result.status}] {result.id:24} "
            f"skill={label:24} strategy={result.strategy:5} rc={result.returncode:3} "
            f"time={result.elapsed_seconds:6.2f}s"
        )

    print()
    print(
        "Summary: "
        f"{counts['pass']} pass, {counts['warn']} warn, {counts['fail']} fail "
        f"out of {len(results)} case(s)"
    )
    print(f"Report: {output_path}")


def main() -> int:
    args = parse_args()

    if args.list_cases:
        for case in REPRESENTATIVE_CASES:
            target = case.skill or "control"
            print(f"{case.id:24} strategy={case.strategy:5} skill={target}")
        return 0

    try:
        claude_path = ensure_claude_available()
        cases = selected_cases(args.cases)
    except (RuntimeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_path = args.output if args.output is not None else default_output_path()

    results: list[CaseResult] = []
    for case in cases:
        print(f"Running {case.id} ({case.strategy}, skill={case.skill or 'control'})...")
        results.append(
            run_case(
                claude_path=claude_path,
                case=case,
                model=args.model,
                timeout_override=args.timeout_seconds,
                budget_override=args.max_budget_usd,
                keep_workspaces=args.keep_workspaces,
            )
        )

    write_report(output_path, cases, results, args.model)
    print_summary(results, output_path)

    return 1 if any(result.status == "fail" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
