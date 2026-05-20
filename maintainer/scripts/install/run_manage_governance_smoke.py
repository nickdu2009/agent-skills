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
        env["CODEX_HOME"] = str(home / ".codex")

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


FORBIDDEN_RUNTIME_SNIPPETS = (
    "see CLAUDE.md § Skill Chain Triggers",
    "docs/maintainer/skill-chain-aliases.md",
    "docs/maintainer/protocol-v2-compact.md",
)
PARALLELISM_PLAN_SNIPPETS = (
    "Built-in planning tools and modes count as planning:",
    "[parallelism:",
    "- delegation: <delegate count, or 0 with reason>",
)


def assert_no_forbidden_runtime_references(project: Path, governance_file: Path) -> None:
    assert_exists(governance_file)
    for snippet in FORBIDDEN_RUNTIME_SNIPPETS:
        assert_not_contains(governance_file, snippet)

    for skill_file in project.rglob("SKILL.md"):
        for snippet in FORBIDDEN_RUNTIME_SNIPPETS:
            assert_not_contains(skill_file, snippet)


def assert_parallelism_plan_template(governance_file: Path) -> None:
    assert_exists(governance_file)
    for snippet in PARALLELISM_PLAN_SNIPPETS:
        assert_contains(governance_file, snippet)


def test_project_install_installs_installable_skills(module) -> None:
    with tempfile.TemporaryDirectory(prefix="install-project-") as project_dir:
        project = Path(project_dir)
        stale_skill = project / ".claude" / "skills" / "removed-skill"
        stale_skill.mkdir(parents=True)
        (stale_skill / "SKILL.md").write_text("# removed\n", encoding="utf-8")
        (stale_skill / module.MANAGED_MARKER).write_text("agent-skills\n", encoding="utf-8")

        run_cli(["--project", str(project), "--platform", "claude-code", "--force"])
        assert_missing(stale_skill)

        for skill_dir in module.discover_installable_skills():
            skill = skill_dir.name
            assert_exists(project / ".claude" / "skills" / skill / "SKILL.md")
        installed_skills = {
            child.name
            for child in (project / ".claude" / "skills").iterdir()
            if child.is_dir()
        }
        expected_skills = {skill_dir.name for skill_dir in module.discover_source_skills()}
        if installed_skills != expected_skills:
            fail(f"installed skills mismatch: expected {sorted(expected_skills)}, got {sorted(installed_skills)}")

        claude_md = project / "CLAUDE.md"
        assert_exists(claude_md)
        assert_contains(claude_md, "## Multi-Agent Rules")
        assert_contains(claude_md, "## Skill Activation")
        assert_contains(claude_md, "## Skill Lifecycle")
        assert_contains(claude_md, "## Common Flow Patterns")
        assert_parallelism_plan_template(claude_md)
        assert_no_forbidden_runtime_references(project, claude_md)


def test_agents_template_selection() -> None:
    with tempfile.TemporaryDirectory(prefix="install-project-") as project_dir:
        project = Path(project_dir)

        run_cli(["--project", str(project), "--platform", "codex", "--force"])

        agents_md = project / "AGENTS.md"
        assert_exists(agents_md)
        assert_contains(agents_md, "## Multi-Agent Rules")
        assert_contains(agents_md, "## Skill Activation")
        assert_parallelism_plan_template(agents_md)
        assert_no_forbidden_runtime_references(project, agents_md)


def test_global_install_installs_user_level_governance(module) -> None:
    with tempfile.TemporaryDirectory(prefix="install-global-home-") as home_dir:
        home = Path(home_dir)
        stale_codex_skill = home / ".codex" / "skills" / "removed-skill"
        stale_codex_skill.mkdir(parents=True)
        (stale_codex_skill / "SKILL.md").write_text("# removed\n", encoding="utf-8")
        (stale_codex_skill / module.MANAGED_MARKER).write_text("agent-skills\n", encoding="utf-8")

        run_cli(["--global", "--platform", "codex", "--force"], home=home)
        assert_missing(stale_codex_skill)
        codex_agents = home / ".codex" / "AGENTS.md"
        assert_exists(codex_agents)
        assert_contains(codex_agents, "## Multi-Agent Rules")
        assert_contains(codex_agents, "## Skill Activation")
        assert_parallelism_plan_template(codex_agents)
        for skill_dir in module.discover_installable_skills():
            assert_exists(home / ".codex" / "skills" / skill_dir.name / "SKILL.md")

        run_cli(["--global", "--platform", "codex", "--check"], home=home)

        stale_claude_skill = home / ".claude" / "skills" / "removed-skill"
        stale_claude_skill.mkdir(parents=True)
        (stale_claude_skill / "SKILL.md").write_text("# removed\n", encoding="utf-8")
        (stale_claude_skill / module.MANAGED_MARKER).write_text("agent-skills\n", encoding="utf-8")

        run_cli(["--global", "--platform", "claude-code", "--force"], home=home)
        assert_missing(stale_claude_skill)
        claude_md = home / ".claude" / "CLAUDE.md"
        assert_exists(claude_md)
        assert_contains(claude_md, "## Multi-Agent Rules")
        assert_contains(claude_md, "## Skill Activation")
        assert_parallelism_plan_template(claude_md)
        for skill_dir in module.discover_installable_skills():
            assert_exists(home / ".claude" / "skills" / skill_dir.name / "SKILL.md")

        run_cli(["--global", "--platform", "claude-code", "--check"], home=home)


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

            assert_missing(mirror_target.target_dir / "scoped-tasking" / "scripts")

            if module.main(["--sync-local", "cursor", "--check"]) != 0:
                fail("expected local mirror check to pass after sync")

            skill_file = mirror_target.target_dir / "scoped-tasking" / "SKILL.md"
            skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")

            if module.main(["--sync-local", "cursor", "--check"]) != 1:
                fail("expected local mirror check to detect drift")
        finally:
            module.LOCAL_MIRROR_TARGETS = original_targets


def main() -> int:
    module = load_installer_module()
    test_project_install_installs_installable_skills(module)
    test_agents_template_selection()
    test_global_install_installs_user_level_governance(module)
    test_local_mirror_sync_and_check(module)
    print("OK: manage-governance temporary-directory smoke tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
