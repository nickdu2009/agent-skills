#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""run_eval.py — Run governance template evaluation on both CLIs.

Usage:
  uv run maintainer/governance_eval/run_eval.py
  uv run maintainer/governance_eval/run_eval.py --model sonnet   # cheaper, less accurate
  uv run maintainer/governance_eval/run_eval.py --runs 1         # fast smoke test
  uv run maintainer/governance_eval/run_eval.py --case lifecycle_coverage
"""

import argparse, json, re, subprocess, shutil, tempfile, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # maintainer/governance_eval/ → project root
CASES_FILE = Path(__file__).with_name("cases.yaml")
TIMEOUT = 120  # seconds per CLI invocation

assert (PROJECT_ROOT / "templates" / "governance").is_dir(), (
    f"PROJECT_ROOT miscalculated: {PROJECT_ROOT} — "
    "expected to find templates/governance/ at project root"
)

# --- Defaults ---
DEFAULT_MODELS = {"claude": "opus", "cursor": "claude-4.6-opus-high"}
DEFAULT_RUNS = {"static": 3, "behavioral": 5}

MODEL_MAP = {
    "opus":   {"claude": "opus",   "cursor": "claude-4.6-opus-high"},
    "sonnet": {"claude": "sonnet", "cursor": "claude-4.6-sonnet-medium"},
}


# --- CLI definitions ---

@dataclass
class CLIDef:
    name: str
    template_source: str   # relative to PROJECT_ROOT
    target_name: str       # deployed as (CLAUDE.md or AGENTS.md)
    model: str

    def build_cmd(self, prompt: str, workspace: Path) -> list[str]:
        raise NotImplementedError

class ClaudeCode(CLIDef):
    def build_cmd(self, prompt: str, workspace: Path) -> list[str]:
        return [
            "claude", "-p", prompt,
            "--output-format", "json",
            "--permission-mode", "plan",
            "--model", self.model,
            "--setting-sources", "project",
        ]

class CursorAgent(CLIDef):
    def build_cmd(self, prompt: str, workspace: Path) -> list[str]:
        return [
            "cursor", "agent", "-p", prompt,
            "--trust", "--workspace", str(workspace),
            "--output-format", "json",
            "--mode", "plan",
            "--model", self.model,
        ]


def build_clis(model_override: Optional[str] = None) -> list:
    if model_override and model_override in MODEL_MAP:
        models = MODEL_MAP[model_override]
    else:
        models = DEFAULT_MODELS
    return [
        ClaudeCode("claude", "templates/governance/CLAUDE-template.md",
                   "CLAUDE.md", models["claude"]),
        CursorAgent("cursor", "templates/governance/AGENTS-template.md",
                    "AGENTS.md", models["cursor"]),
    ]


# --- Isolation ---

def setup_isolated_workspace(template: Path, target_name: str) -> Path:
    ws = Path(tempfile.mkdtemp(prefix="governance_eval_"))
    shutil.copy2(template, ws / target_name)
    subprocess.run(["git", "init", "-q"], cwd=ws, check=True)
    subprocess.run(
        ["git", "config", "user.name", "governance-eval"], cwd=ws, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "eval@localhost"], cwd=ws, check=True
    )
    subprocess.run(["git", "add", "."], cwd=ws, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=ws, check=True)
    return ws


def teardown_isolated_workspace(ws: Path) -> None:
    if ws.is_dir():
        shutil.rmtree(ws, ignore_errors=True)


# --- Response extraction ---

def extract_response(raw: str) -> str:
    """Extract agent response text from CLI JSON envelope."""
    try:
        envelope = json.loads(raw)
        text = raw
        for key in ("result", "content", "text"):
            if key in envelope and envelope[key]:
                text = envelope[key]
                break
    except json.JSONDecodeError:
        text = raw
    # Extract JSON from markdown code fences (handles preamble text before the block)
    m = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Fallback: strip leading/trailing fences if no preamble
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text.strip())
    return text


def is_cli_error(proc: subprocess.CompletedProcess) -> Optional[str]:
    """Check if CLI invocation failed. Returns error message or None."""
    if proc.returncode != 0 and not proc.stdout.strip():
        return f"exit code {proc.returncode}: {proc.stderr.strip()[:200]}"
    for marker in ("API Error:", "Error:", "FATAL"):
        if marker in (proc.stderr or ""):
            return proc.stderr.strip()[:200]
    try:
        envelope = json.loads(proc.stdout)
        if envelope.get("is_error"):
            return envelope.get("result", "unknown CLI error")[:200]
    except (json.JSONDecodeError, AttributeError):
        pass
    return None


# --- Judge ---

def evaluate_judge(content: str, judge_expr: str) -> bool:
    """Evaluate a Python judge expression against the parsed JSON response.

    The expression has access to `d` (the parsed dict) and Python builtins.
    Returns False if JSON parsing fails or the expression raises.
    """
    try:
        d = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return False
    try:
        return bool(eval(judge_expr, {"__builtins__": {}, "d": d, "set": set, "len": len, "all": all, "any": any}))
    except Exception:
        return False


# --- Preflight ---

def preflight_check(cli: CLIDef, workspace: Path) -> Optional[str]:
    """Quick check that the CLI + model combination works. Returns error or None."""
    try:
        proc = subprocess.run(
            cli.build_cmd("Respond with exactly: {\"ok\":true}", workspace),
            cwd=workspace, capture_output=True, text=True, timeout=60,
        )
        err = is_cli_error(proc)
        if err:
            return err
    except subprocess.TimeoutExpired:
        return "preflight timed out after 60s"
    except FileNotFoundError:
        return f"CLI '{cli.name}' not found in PATH"
    return None


# --- Main ---

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Governance template evaluation")
    p.add_argument("--model", choices=list(MODEL_MAP), default=None,
                   help="Override model for both CLIs (default: opus)")
    p.add_argument("--runs", type=int, default=None,
                   help="Override run count for all cases (default: 3 static, 5 behavioral)")
    p.add_argument("--case", type=str, default=None,
                   help="Run only this case ID (e.g. lifecycle_coverage)")
    p.add_argument("--skip-preflight", action="store_true",
                   help="Skip CLI preflight check")
    p.add_argument("--verbose", action="store_true",
                   help="Print extracted content and judge details")
    return p.parse_args()


def main():
    args = parse_args()
    cases = yaml.safe_load(CASES_FILE.read_text())
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
        if not cases:
            print(f"Error: case '{args.case}' not found", file=sys.stderr)
            sys.exit(2)
    clis = build_clis(args.model)

    results: dict = {}

    for cli in clis:
        print(f"\n=== {cli.name} (model: {cli.model}) ===", flush=True)
        cli_results = []

        template_path = PROJECT_ROOT / cli.template_source
        ws = setup_isolated_workspace(template_path, cli.target_name)

        try:
            # Preflight check
            if not args.skip_preflight:
                print(f"  [preflight] ...", end="", flush=True)
                err = preflight_check(cli, ws)
                if err:
                    print(f" SKIP ({err})", flush=True)
                    results[cli.name] = []
                    continue
                print(" ok", flush=True)

            for case in cases:
                case_id = case["id"]
                category = case.get("category", "static")
                runs = args.runs or DEFAULT_RUNS.get(category, 3)
                majority = (runs // 2) + 1
                judge_expr = case["judge"]
                expected = case["expect_current"]

                prompt = case["prompt"].replace(
                    "{{GOVERNANCE_FILE}}", cli.target_name
                )
                cmd = cli.build_cmd(prompt, ws)

                pass_count = 0
                error_count = 0
                for run_i in range(runs):
                    try:
                        proc = subprocess.run(
                            cmd, cwd=ws,
                            capture_output=True, text=True,
                            timeout=TIMEOUT,
                        )
                        err = is_cli_error(proc)
                        if err:
                            error_count += 1
                            print(f"    [{case_id} run {run_i+1}] CLI error: {err}",
                                  flush=True)
                            continue
                        content = extract_response(proc.stdout)
                        if args.verbose:
                            print(f"    [{case_id} run {run_i+1}] extracted: {content[:300]}",
                                  flush=True)
                        if evaluate_judge(content, judge_expr):
                            pass_count += 1
                        elif args.verbose:
                            try:
                                d = json.loads(content)
                                print(f"    [{case_id} run {run_i+1}] judge FAIL on parsed JSON",
                                      flush=True)
                            except Exception as e:
                                print(f"    [{case_id} run {run_i+1}] JSON parse error: {e}",
                                      flush=True)
                    except subprocess.TimeoutExpired:
                        error_count += 1
                        print(f"    [{case_id} run {run_i+1}] timeout",
                              flush=True)

                if error_count == runs:
                    verdict = "ERROR"
                    cal = "(all runs errored)"
                else:
                    verdict = "PASS" if pass_count >= majority else "FAIL"
                    calibrated = verdict.lower() == expected.lower()
                    cal = ("(calibrated)" if calibrated
                           else f"(MISCALIBRATED: expected {expected})")

                print(f"  {case_id:<25} {verdict:<5} {cal}", flush=True)
                cli_results.append({
                    "id": case_id, "verdict": verdict,
                    "calibrated": verdict == "ERROR" or calibrated,
                    "runs": runs, "pass_count": pass_count,
                    "error_count": error_count,
                })
        finally:
            teardown_isolated_workspace(ws)

        results[cli.name] = cli_results

    # --- Summary ---
    print(flush=True)
    for name, cli_results in results.items():
        if not cli_results:
            print(f"  {name}: SKIPPED (preflight failed)", flush=True)
            continue
        p = sum(1 for r in cli_results if r["verdict"] == "PASS")
        f = sum(1 for r in cli_results if r["verdict"] == "FAIL")
        e = sum(1 for r in cli_results if r["verdict"] == "ERROR")
        cal = sum(1 for r in cli_results if r["calibrated"])
        mis = len(cli_results) - cal
        parts = [f"{p} pass", f"{f} fail"]
        if e:
            parts.append(f"{e} error")
        print(f"  {name}: {', '.join(parts)} "
              f"({cal} calibrated, {mis} miscalibrated)", flush=True)

    sys.exit(0 if all(
        r["calibrated"] for v in results.values() for r in v
    ) else 1)

if __name__ == "__main__":
    main()
