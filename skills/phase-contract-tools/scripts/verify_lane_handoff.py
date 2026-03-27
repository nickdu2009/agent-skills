#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Verify that a lane handoff artifact still matches the phase plan."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import yaml
from _shared_phase_tools import find_lane, find_wave, load_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify an immutable lane handoff artifact.")
    parser.add_argument("--plan", required=True, help="Path to docs/phaseN-plan.yaml")
    parser.add_argument("--handoff", help="Path to the rendered handoff artifact. Defaults to stdin.")
    parser.add_argument("--strict", action="store_true", help="Re-render the lane body and compare it to the handoff body")
    parser.add_argument(
        "--contract-scripts",
        help="Optional path to the phase-contract-tools scripts directory",
    )
    return parser.parse_args()


def default_contract_scripts() -> Path:
    return Path(__file__).resolve().parent


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_handoff_text(args: argparse.Namespace) -> str:
    if args.handoff:
        return Path(args.handoff).expanduser().resolve().read_text(encoding="utf-8")
    return sys.stdin.read()


def parse_markdown_payload(text: str) -> tuple[dict[str, Any], str]:
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise ValueError("markdown handoff must start with YAML frontmatter")
    marker = "\n---\n"
    end = normalized.find(marker, 4)
    if end == -1:
        raise ValueError("markdown handoff frontmatter is not closed")
    manifest = yaml.safe_load(normalized[4:end])
    if not isinstance(manifest, dict):
        raise ValueError("handoff frontmatter must decode to a mapping")
    body = normalized[end + len(marker) :]
    if body.startswith("\n"):
        body = body[1:]
    return manifest, body


def parse_yaml_payload(text: str) -> tuple[dict[str, Any], str]:
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("yaml handoff must decode to a mapping")
    manifest = data.get("manifest")
    body = data.get("body")
    if not isinstance(manifest, dict) or not isinstance(body, str):
        raise ValueError("yaml handoff must contain mapping manifest and string body")
    return manifest, body


def parse_handoff_payload(text: str) -> tuple[dict[str, Any], str]:
    stripped = text.lstrip()
    if stripped.startswith("---\n"):
        return parse_markdown_payload(stripped)
    return parse_yaml_payload(text)


def render_expected_body(
    contract_scripts: Path,
    plan_path: Path,
    wave_id: int,
    lane_name: str,
) -> str:
    script = contract_scripts / "render_agent_prompt.py"
    if not script.exists():
        raise FileNotFoundError(f"missing render helper: {script}")
    proc = subprocess.run(
        ["uv", "run", str(script), "--plan", str(plan_path), "--wave", str(wave_id), "--lane", lane_name],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit code {proc.returncode}"
        raise RuntimeError(f"render_agent_prompt failed: {detail}")
    return proc.stdout.rstrip() + "\n"


def compare_field(manifest: dict[str, Any], key: str, expected: Any) -> None:
    if manifest.get(key) != expected:
        raise ValueError(f"handoff manifest {key!r} does not match plan value {expected!r}")


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    contract_scripts = (
        Path(args.contract_scripts).expanduser().resolve()
        if args.contract_scripts
        else default_contract_scripts()
    )

    try:
        handoff_text = load_handoff_text(args)
        manifest, body = parse_handoff_payload(handoff_text)
        required = {
            "handoff_schema_version",
            "phase",
            "wave_id",
            "wave_label",
            "lane",
            "owner",
            "ref_kind",
            "ref",
            "plan_path",
            "plan_sha256",
            "body_sha256",
            "generated_at",
        }
        missing = sorted(required - set(manifest))
        if missing:
            raise ValueError(f"handoff manifest is missing required keys: {missing}")

        plan_text = plan_path.read_text(encoding="utf-8")
        current_plan_sha = sha256_text(plan_text)
        if manifest["plan_sha256"] != current_plan_sha:
            raise ValueError("handoff plan_sha256 no longer matches the current plan file")
        if manifest["body_sha256"] != sha256_text(body):
            raise ValueError("handoff body_sha256 does not match the embedded body")

        data = load_plan(plan_path)
        wave = find_wave(data, int(manifest["wave_id"]))
        lane = find_lane(wave, str(manifest["lane"]))

        compare_field(manifest, "wave_label", wave.get("label"))
        compare_field(manifest, "owner", lane.get("owner"))
        compare_field(manifest, "ref_kind", lane.get("ref_kind"))
        compare_field(manifest, "ref", lane.get("ref"))

        resolved_plan_path = str(plan_path)
        if manifest["plan_path"] != resolved_plan_path:
            raise ValueError(f"handoff manifest 'plan_path' does not match {resolved_plan_path!r}")

        if args.strict:
            expected_body = render_expected_body(contract_scripts, plan_path, int(manifest["wave_id"]), str(manifest["lane"]))
            if body != expected_body:
                raise ValueError("handoff body no longer matches the renderer output for the current plan")

        print(
            f"OK verify-lane-handoff: wave {manifest['wave_id']} lane {manifest['lane']} "
            f"matches the current plan."
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR verify-lane-handoff: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
