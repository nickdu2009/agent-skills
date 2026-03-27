#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Run deterministic smoke checks for the shared phase contract helpers."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def run(args: list[str], cwd: Path) -> str:
    proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit code {proc.returncode}"
        raise RuntimeError(f"{' '.join(args)} failed: {detail}")
    return proc.stdout


def assert_match(label: str, actual: str, expected_path: Path) -> None:
    expected = expected_path.read_text(encoding="utf-8")
    if actual != expected:
        raise AssertionError(f"{label} output diverged from {expected_path}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    fixture_docs = root / "fixtures" / "smoke" / "docs"
    golden_dir = root / "fixtures" / "smoke" / "golden"

    try:
        run(["uv", "run", "scripts/validate_phase_execution_schema.py", "--plan", str(fixture_docs / "smoke-plan.yaml")], root)
        run(["uv", "run", "scripts/validate_phase_doc_set.py", "--docs-dir", str(fixture_docs), "--phase", "smoke"], root)
        run(
            [
                "uv",
                "run",
                "scripts/preflight_phase_execution.py",
                "--plan",
                str(fixture_docs / "smoke-plan.yaml"),
                "--docs-dir",
                str(fixture_docs),
                "--phase",
                "smoke",
                "--wave",
                "1",
            ],
            root,
        )

        prompt = run(
            ["uv", "run", "scripts/render_agent_prompt.py", "--plan", str(fixture_docs / "smoke-plan.yaml"), "--pr", "P99-01"],
            root,
        )
        assert_match("render_agent_prompt", prompt, golden_dir / "render_agent_prompt_P99-01.txt")

        kickoff = run(
            ["uv", "run", "scripts/render_wave_kickoff.py", "--plan", str(fixture_docs / "smoke-plan.yaml"), "--wave", "1"],
            root,
        )
        assert_match("render_wave_kickoff", kickoff, golden_dir / "render_wave_kickoff_wave1.txt")

        snapshot = run(
            ["uv", "run", "scripts/render_wave_status_snapshot.py", "--plan", str(fixture_docs / "smoke-plan.yaml"), "--wave", "1"],
            root,
        )
        assert_match("render_wave_status_snapshot", snapshot, golden_dir / "render_wave_status_snapshot_wave1.yaml")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            handoff_path = temp_path / "smoke-handoff.md"
            snapshot_path = temp_path / "smoke-snapshot.yaml"
            run(
                [
                    "uv",
                    "run",
                    "scripts/render_lane_handoff.py",
                    "--plan",
                    str(fixture_docs / "smoke-plan.yaml"),
                    "--wave",
                    "1",
                    "--lane",
                    "smoke",
                    "--write",
                    str(handoff_path),
                ],
                root,
            )
            run(["uv", "run", "scripts/validate_handoff_manifest.py", "--handoff", str(handoff_path)], root)
            run(
                [
                    "uv",
                    "run",
                    "scripts/verify_lane_handoff.py",
                    "--plan",
                    str(fixture_docs / "smoke-plan.yaml"),
                    "--handoff",
                    str(handoff_path),
                    "--strict",
                ],
                root,
            )

            snapshot_path.write_text(snapshot, encoding="utf-8")
            run(["uv", "run", "scripts/validate_wave_status_snapshot.py", "--snapshot", str(snapshot_path)], root)
        print("Smoke checks passed.")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR run-smoke-checks: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
