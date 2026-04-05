#!/usr/bin/env python3
"""Smoke test manage-governance.py using temporary directories."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
INSTALLER_PATH = REPO_ROOT / "maintainer" / "scripts" / "install" / "manage-governance.py"


def fail(message: str) -> None:
    raise AssertionError(message)


def run_cli(args: list[str], *, home: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if home is not None:
        env["HOME"] = str(home)

    result = subprocess.run(
        [sys.executable, str(INSTALLER_PATH), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        fail(
            "installer command failed:\n"
            f"args: {args}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def load_installer_module():
    spec = importlib.util.spec_from_file_location("manage_governance_module", INSTALLER_PATH)
    if spec is None or spec.loader is None:
        fail(f"unable to load installer module from {INSTALLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def assert_exists(path: Path) -> None:
    if not path.exists():
        fail(f"expected path to exist: {path}")


def assert_missing(path: Path) -> None:
    if path.exists():
        fail(f"expected path to be absent: {path}")


def assert_contains(path: Path, snippet: str) -> None:
    text = path.read_text(encoding="utf-8")
    if snippet not in text:
        fail(f"expected {path} to contain {snippet!r}")


def assert_not_contains(path: Path, snippet: str) -> None:
    text = path.read_text(encoding="utf-8")
    if snippet in text:
        fail(f"expected {path} not to contain {snippet!r}")


def test_full_install_with_phase(module) -> None:
    with tempfile.TemporaryDirectory(prefix="install-home-") as home_dir, tempfile.TemporaryDirectory(
        prefix="install-project-"
    ) as project_dir:
        home = Path(home_dir)
        project = Path(project_dir)

        run_cli(
            ["--project", str(project), "--platform", "claude-code", "--include-phase", "--force"],
            home=home,
        )

        for skill in (*module.FULL_PROFILE.skills, *module.FULL_PROFILE.phase_skills):
            assert_exists(home / ".claude" / "skills" / skill / "SKILL.md")

        claude_md = project / "CLAUDE.md"
        assert_exists(claude_md)
        assert_contains(claude_md, "## Multi-Agent Rules")
        assert_contains(claude_md, "base-level CLAUDE.md rules")
        assert_contains(claude_md, "## Skill Escalation")
        assert_contains(claude_md, "## Skill Lifecycle")


def test_multi_agent_install(module) -> None:
    with tempfile.TemporaryDirectory(prefix="install-home-") as home_dir, tempfile.TemporaryDirectory(
        prefix="install-project-"
    ) as project_dir:
        home = Path(home_dir)
        project = Path(project_dir)

        run_cli(
            ["--profile", "multi-agent", "--project", str(project), "--platform", "claude-code", "--force"],
            home=home,
        )

        for skill in module.MULTI_AGENT_PROFILE.skills:
            assert_exists(home / ".claude" / "skills" / skill / "SKILL.md")

        assert_missing(home / ".claude" / "skills" / "scoped-tasking")

        claude_md = project / "CLAUDE.md"
        assert_exists(claude_md)
        assert_contains(claude_md, "## Multi-Agent Rules")
        assert_not_contains(claude_md, "## Skill Escalation")
        assert_not_contains(claude_md, "## Skill Lifecycle")


def test_agents_template_selection() -> None:
    with tempfile.TemporaryDirectory(prefix="install-project-") as project_dir:
        project = Path(project_dir)

        run_cli(["--rules-only", str(project), "--platform", "codex"])

        agents_md = project / "AGENTS.md"
        assert_exists(agents_md)
        assert_contains(agents_md, "base-level AGENTS.md rules")
        assert_not_contains(agents_md, "base-level CLAUDE.md rules")


def test_local_mirror_sync_and_check(module) -> None:
    with tempfile.TemporaryDirectory(prefix="install-mirror-", dir=REPO_ROOT) as temp_dir:
        temp_root = Path(temp_dir)
        mirror_target = module.MirrorTarget(
            key="cursor",
            display_name="Cursor",
            target_dir=temp_root / ".cursor" / "skills",
        )
        original_targets = module.LOCAL_MIRROR_TARGETS

        try:
            module.LOCAL_MIRROR_TARGETS = {"cursor": mirror_target}

            if module.main(["--sync-local", "cursor"]) != 0:
                fail("expected local mirror sync to succeed")

            assert_exists(mirror_target.target_dir / "phase-contract-tools" / "scripts")
            assert_missing(mirror_target.target_dir / "scoped-tasking" / "scripts")

            if module.main(["--check-local", "cursor"]) != 0:
                fail("expected local mirror check to pass after sync")

            skill_file = mirror_target.target_dir / "scoped-tasking" / "SKILL.md"
            skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")

            if module.main(["--check-local", "cursor"]) != 1:
                fail("expected local mirror check to detect drift")
        finally:
            module.LOCAL_MIRROR_TARGETS = original_targets


def main() -> int:
    module = load_installer_module()
    test_full_install_with_phase(module)
    test_multi_agent_install(module)
    test_agents_template_selection()
    test_local_mirror_sync_and_check(module)
    print("OK: manage-governance temporary-directory smoke tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
