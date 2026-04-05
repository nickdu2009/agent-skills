#!/usr/bin/env python3
"""Run fixture-backed Claude multi-turn acceptance scenarios.

This is a stable surrogate for fully driving Claude Code's interactive TTY.
Instead of scraping a full-screen session, the script:

- copies a small synthetic fixture repo into a fresh temp workspace
- mirrors the canonical skills tree into `.claude/skills/`
- runs one scenario per workspace with `claude -p`
- resumes later rounds via `--resume <session-id>`
- stores raw JSON outputs plus a lightweight pass/warn/fail heuristic

The goal is not perfect automated judging. The goal is a reproducible
maintainer-grade baseline for multi-turn behavior.
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


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
FIXTURE_DIR = REPO_ROOT / "maintainer" / "fixtures" / "claude-interactive-workspace"
REPORTS_DIR = REPO_ROOT / "maintainer" / "reports" / "runs"


@dataclass(frozen=True)
class Scenario:
    id: str
    description: str
    rounds: tuple[str, ...]
    round_expectations: tuple[tuple[str, ...] | None, ...]
    forbidden_patterns: tuple[str, ...] = ()
    timeout_seconds: int = 180
    notes: str = ""


@dataclass
class RoundResult:
    prompt: str
    returncode: int
    elapsed_seconds: float
    session_id: str | None
    total_cost_usd: float | None
    result: str
    stderr: str
    permission_denials: list[dict]
    matched_expectations: list[str]


@dataclass
class ScenarioResult:
    id: str
    description: str
    status: str
    workspace: str | None
    notes: str
    forbidden_hits: list[str]
    rounds: list[RoundResult]


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        id="scoped-to-plan",
        description="Broad investigation should narrow first, then upgrade into a plan.",
        rounds=(
            "Look into the performance issues across the reporting, billing, and notification systems — users say the daily summary email is slow.",
            "We will probably need changes in the service layer, client wrapper, and tests. I'm not sure where the timeout config lives.",
        ),
        round_expectations=(
            (r"\bscope\b", r"\bboundary\b", r"\bnarrow", r"daily summary email"),
            (r"\bassum", r"\bplan\b", r"\bfiles?\b", r"\btimeout\b", r"\bnext\b"),
        ),
    ),
    Scenario(
        id="context-budget-awareness",
        description="Noisy multi-turn investigation should compress into knowns, unknowns, and next steps.",
        rounds=(
            "We already checked src/cache/cache.py twice and the queue config three times. Still no root cause.",
            "I've read about 12 files and the logging issue still does not connect to any handler. I do not want more exploration yet.",
            "Stop and summarize what we actually know so far, what we still do not know, and the smallest next step.",
        ),
        round_expectations=(
            None,
            None,
            (
                r"what i know so far",
                r"what we actually know",
                r"what i don't know",
                r"still do not know",
                r"smallest next step",
            ),
        ),
    ),
    Scenario(
        id="multi-agent-protocol",
        description="Parallel investigation should be proposed only for decomposable work.",
        rounds=(
            "Investigate the auth middleware, session storage, and role checking in parallel to understand the full auth flow.",
            "Now compare that with a serial task: fix the off-by-one error in pkg/runtime/replay.go.",
        ),
        round_expectations=(
            (r"\bparallel\b", r"\bsubagents?\b", r"\bsplit\b", r"\blanes?\b"),
            (r"\bserial\b", r"single-file", r"stay serial", r"one file"),
        ),
    ),
    Scenario(
        id="phase-plan-to-execute",
        description="Phase planning should create document-driven execution artifacts, then require them for execution.",
        rounds=(
            "Using docs/db-migration-notes.md, create the normal phase 1 planning artifacts for this database migration. We need sequenced waves with clear ownership so multiple agents can work in parallel. Keep the textual summary short after writing the plan files.",
            "Execute wave 2 of the phase 1 plan.",
        ),
        round_expectations=(
            (r"phase1-plan\.yaml", r"\bwave\b", r"\bphase\b", r"\bparallel\b"),
            (r"phase1-plan\.yaml", r"\bwave 2\b", r"\bplan file\b", r"phase 1 plan"),
        ),
        timeout_seconds=300,
    ),
    Scenario(
        id="conflict-resolution",
        description="Competing hypotheses should be weighed by evidence quality.",
        rounds=(
            "Two subagents disagree: one says the cache invalidation path is broken, the other blames clock skew in expiry logic. Which is right?",
            "Subagent A cites src/cache/cache.py:13-16 where summary_key is checked but invoice_key is popped. Subagent B only has log timing correlation from expiry traces.",
        ),
        round_expectations=(
            (r"\bevidence\b", r"\bdisagree", r"\bclaim\b", r"\buncertain"),
            (r"direct code", r"cache invalidation", r"stronger evidence", r"correlation"),
        ),
    ),
    Scenario(
        id="phase-contract-tools",
        description="Direct validator maintenance should stay focused on schema and tooling.",
        rounds=("Fix a validation error in the phase schema validator script.",),
        round_expectations=((r"\bvalidator\b", r"\bschema\b", r"validation error", r"phase"),),
    ),
    Scenario(
        id="negative-control",
        description="A normal feature request should not be reframed as bugfix/refactor/phase work.",
        rounds=("Add a dark mode toggle to the settings page.",),
        round_expectations=((r"dark mode", r"settings page", r"toggle"),),
        forbidden_patterns=(r"bugfix-workflow", r"phase-plan", r"phase-execute", r"safe-refactor"),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run fixture-backed Claude multi-turn acceptance scenarios."
    )
    parser.add_argument(
        "--scenario",
        action="append",
        dest="scenarios",
        help="Run only the named scenario. Repeat to select multiple scenarios.",
    )
    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="List scenario IDs and exit.",
    )
    parser.add_argument(
        "--model",
        default="sonnet",
        help="Claude model alias or full model name. Defaults to sonnet.",
    )
    parser.add_argument(
        "--use-default-model",
        action="store_true",
        help="Use the Claude CLI default model instead of passing --model explicitly.",
    )
    parser.add_argument(
        "--timeout-multiplier",
        type=float,
        default=1.0,
        help="Multiply each scenario timeout by this factor. Defaults to 1.0.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON report path. Defaults to maintainer/reports/runs/claude-interactive-mainline-<timestamp>.json.",
    )
    parser.add_argument(
        "--keep-workspaces",
        action="store_true",
        help="Keep temporary workspaces on disk for inspection.",
    )
    return parser.parse_args()


def selected_scenarios(names: list[str] | None) -> tuple[Scenario, ...]:
    if not names:
        return SCENARIOS
    wanted = set(names)
    selected = tuple(s for s in SCENARIOS if s.id in wanted)
    missing = sorted(wanted - {s.id for s in selected})
    if missing:
        raise SystemExit(f"Unknown scenario(s): {', '.join(missing)}")
    return selected


def prepare_workspace() -> Path:
    workspace = Path(tempfile.mkdtemp(prefix="claude-interactive-mainline-"))
    shutil.copytree(FIXTURE_DIR, workspace, dirs_exist_ok=True)
    skills_target = workspace / ".claude" / "skills"
    skills_target.mkdir(parents=True, exist_ok=True)
    for child in SKILLS_DIR.iterdir():
        if child.is_dir():
            shutil.copytree(child, skills_target / child.name)
    return workspace


def parse_json_output(stdout: str) -> dict:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {}


def run_round(
    *,
    workspace: Path,
    model: str,
    use_default_model: bool,
    timeout_multiplier: float,
    scenario: Scenario,
    prompt: str,
    session_id: str | None,
) -> RoundResult:
    command = [
        "claude",
        "-p",
        "--output-format",
        "json",
        "--permission-mode",
        "acceptEdits",
    ]
    if not use_default_model:
        command.extend(["--model", model])
    if session_id is not None:
        command.extend(["-r", session_id])
    command.append(prompt)

    started = time.monotonic()
    timeout_seconds = max(1, int(round(scenario.timeout_seconds * timeout_multiplier)))
    try:
        proc = subprocess.run(
            command,
            cwd=workspace,
            text=True,
            capture_output=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout_seconds,
            check=False,
        )
        payload = parse_json_output(proc.stdout)
        result_text = payload.get("result", proc.stdout.strip())
        matched = []
        return RoundResult(
            prompt=prompt,
            returncode=proc.returncode,
            elapsed_seconds=round(time.monotonic() - started, 3),
            session_id=payload.get("session_id", session_id),
            total_cost_usd=payload.get("total_cost_usd"),
            result=result_text,
            stderr=proc.stderr.strip(),
            permission_denials=payload.get("permission_denials", []),
            matched_expectations=matched,
        )
    except subprocess.TimeoutExpired as exc:
        return RoundResult(
            prompt=prompt,
            returncode=124,
            elapsed_seconds=round(time.monotonic() - started, 3),
            session_id=session_id,
            total_cost_usd=None,
            result=(exc.stdout or "").strip(),
            stderr=f"timeout after {timeout_seconds}s",
            permission_denials=[],
            matched_expectations=[],
        )


def score_scenario(scenario: Scenario, rounds: list[RoundResult]) -> tuple[str, list[str]]:
    forbidden_hits: list[str] = []
    any_errors = any(r.returncode != 0 for r in rounds)

    for pattern in scenario.forbidden_patterns:
        for round_result in rounds:
            if re.search(pattern, round_result.result, flags=re.IGNORECASE):
                forbidden_hits.append(pattern)

    expected_rounds = 0
    matched_rounds = 0
    for round_result, expectations in zip(rounds, scenario.round_expectations, strict=True):
        if expectations is None:
            continue
        expected_rounds += 1
        matches = [
            pattern
            for pattern in expectations
            if re.search(pattern, round_result.result, flags=re.IGNORECASE)
        ]
        round_result.matched_expectations = matches
        if matches:
            matched_rounds += 1

    if expected_rounds == 0:
        status = "warn"
    elif not any_errors and matched_rounds == expected_rounds and not forbidden_hits:
        status = "pass"
    elif matched_rounds > 0 and not forbidden_hits:
        status = "warn"
    else:
        status = "fail"

    return status, forbidden_hits


def default_output_path() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return REPORTS_DIR / f"claude-interactive-mainline-{timestamp}.json"


def main() -> int:
    args = parse_args()
    scenarios = selected_scenarios(args.scenarios)

    if args.list_scenarios:
        for scenario in scenarios:
            print(f"{scenario.id}: {scenario.description}")
        return 0

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = args.output or default_output_path()

    results: list[ScenarioResult] = []
    for scenario in scenarios:
        workspace = prepare_workspace()
        session_id: str | None = None
        round_results: list[RoundResult] = []
        try:
            for prompt in scenario.rounds:
                round_result = run_round(
                    workspace=workspace,
                    model=args.model,
                    use_default_model=args.use_default_model,
                    timeout_multiplier=args.timeout_multiplier,
                    scenario=scenario,
                    prompt=prompt,
                    session_id=session_id,
                )
                session_id = round_result.session_id
                round_results.append(round_result)
        finally:
            if not args.keep_workspaces:
                shutil.rmtree(workspace, ignore_errors=True)

        status, forbidden_hits = score_scenario(scenario, round_results)
        results.append(
            ScenarioResult(
                id=scenario.id,
                description=scenario.description,
                status=status,
                workspace=str(workspace) if args.keep_workspaces else None,
                notes=scenario.notes,
                forbidden_hits=forbidden_hits,
                rounds=round_results,
            )
        )

    payload = {
        "timestamp": datetime.now().isoformat(),
        "model": None if args.use_default_model else args.model,
        "model_mode": "default-cli-model" if args.use_default_model else "explicit-model",
        "timeout_multiplier": args.timeout_multiplier,
        "fixture_dir": str(FIXTURE_DIR),
        "skills_dir": str(SKILLS_DIR),
        "keep_workspaces": args.keep_workspaces,
        "scenarios": [asdict(result) for result in results],
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "pass": sum(1 for result in results if result.status == "pass"),
        "warn": sum(1 for result in results if result.status == "warn"),
        "fail": sum(1 for result in results if result.status == "fail"),
    }
    print(f"Wrote {report_path}")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
