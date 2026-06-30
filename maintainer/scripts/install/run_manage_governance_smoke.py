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


def run_cli_allow_failure(args: list[str], *, home: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if home is not None:
        env["HOME"] = str(home)
        env["CODEX_HOME"] = str(home / ".codex")

    return subprocess.run(
        [sys.executable, str(INSTALLER_PATH), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


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


def assert_stdout_contains(result: subprocess.CompletedProcess[str], snippet: str) -> None:
    if snippet not in result.stdout:
        fail(f"expected stdout to contain {snippet!r}, got:\n{result.stdout}")


FORBIDDEN_RUNTIME_SNIPPETS = (
    "see CLAUDE.md § Skill Chain Triggers",
    "docs/maintainer/skill-chain-aliases.md",
    "docs/maintainer/protocol-v2-compact.md",
)
PARALLELISM_PLAN_SNIPPETS = (
    "Use `implementation-planning` when the work spans multiple files, steps, or PR-sized increments and needs a written, reviewable plan artifact.",
    "[parallelism:",
    "- delegation: <delegate count, or 0 with reason>",
)
GOVERNANCE_BOUNDARY_SNIPPETS = (
    "Continue without an extra user confirmation when the next step is local, non-destructive",
    "Stop and ask when the next step would change requirements, public interfaces, cross-module contracts, persistence schema",
    "Parallelism is opt-in, not automatic.",
)
ROUTING_SEMANTICS_SNIPPETS = (
    "Stay on the selected implementation workflow when scope is clear and no escalation signal appears;",
    "Continue from a completed `implementation-planning` plan into implementation, `self-review`, and `targeted-validation`",
    "Continue after `review_result: issues_found` into a local revision of the same artifact when scope, ownership, and artifact identity stay the same.",
    "Continue from that revision back into the same review-loop and do not `drop` the review skill until `review_result: clean` or `clean_with_assumptions`, explicit handoff, or superseding work changes the artifact/boundary.",
    "Continue after a review loop returns `review_result: clean` or `clean_with_assumptions` when the next step is explicit, local, and non-destructive.",
    "Stop after `review_result: needs_clarification` and ask the bounded clarification questions before continuing any further revision.",
    "Once an escalation path is triggered, stop the current implementation path and move into `design-before-plan`, `architecture-design`, or `impact-analysis`",
)
PROTOCOL_SEMANTICS_SNIPPETS = (
    "Fast paths may omit the full protocol block set.",
    "The task-validation protocol block records the scoped goal, key constraints, and validation boundary before a non-trivial skill chain or review loop.",
    "`precheck`: emit only when a skill has a real prerequisite",
    "`output`: summarize the concrete deliverable from the active skill;",
    "`drop`: explicitly retire the skill when its deliverable is complete, superseded, or handed off downstream.",
    "`review_result: issues_found` means the review-loop deliverable is still incomplete; keep the review skill active and do not `drop` it as completed yet.",
    "`review_result: clean_with_assumptions` is a valid clean exit when only tracked low-risk assumptions remain with explicit validation methods.",
    "`review_result: needs_clarification` means the review-loop is blocked on a missing decision; stop and ask bounded clarification questions instead of revising through the gap.",
    "A local `修订` on the same artifact stays inside the active review loop when scope, ownership, and artifact identity do not change, including in-thread drafts that have not been written to files yet.",
    "If the same skill path is retried without new evidence, stop and re-scope, escalate, or ask instead of looping on the same action.",
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


def assert_governance_boundaries(governance_file: Path) -> None:
    assert_exists(governance_file)
    for snippet in GOVERNANCE_BOUNDARY_SNIPPETS:
        assert_contains(governance_file, snippet)


def assert_routing_semantics(governance_file: Path) -> None:
    assert_exists(governance_file)
    for snippet in ROUTING_SEMANTICS_SNIPPETS:
        assert_contains(governance_file, snippet)


def assert_protocol_semantics(governance_file: Path) -> None:
    assert_exists(governance_file)
    for snippet in PROTOCOL_SEMANTICS_SNIPPETS:
        assert_contains(governance_file, snippet)


def test_project_install_installs_installable_skills(module) -> None:
    with tempfile.TemporaryDirectory(prefix="install-project-") as project_dir:
        project = Path(project_dir)
        stale_skill = project / ".claude" / "skills" / "removed-skill"
        stale_skill.mkdir(parents=True)
        (stale_skill / "SKILL.md").write_text("# removed\n", encoding="utf-8")
        (stale_skill / module.MANAGED_MARKER).write_text("agent-skills\n", encoding="utf-8")

        run_cli(["install", "project", str(project), "--platform", "claude-code", "--overwrite-skills"])
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
        assert_governance_boundaries(claude_md)
        assert_routing_semantics(claude_md)
        assert_protocol_semantics(claude_md)
        assert_no_forbidden_runtime_references(project, claude_md)


def test_agents_template_selection() -> None:
    with tempfile.TemporaryDirectory(prefix="install-project-") as project_dir:
        project = Path(project_dir)

        run_cli(["install", "project", str(project), "--platform", "codex", "--overwrite-skills"])

        agents_md = project / "AGENTS.md"
        assert_exists(agents_md)
        assert_contains(agents_md, "## Multi-Agent Rules")
        assert_contains(agents_md, "## Skill Activation")
        assert_parallelism_plan_template(agents_md)
        assert_governance_boundaries(agents_md)
        assert_routing_semantics(agents_md)
        assert_protocol_semantics(agents_md)
        assert_no_forbidden_runtime_references(project, agents_md)


def test_user_install_installs_user_level_governance(module) -> None:
    with tempfile.TemporaryDirectory(prefix="install-user-home-") as home_dir:
        home = Path(home_dir)
        stale_codex_skill = home / ".codex" / "skills" / "removed-skill"
        stale_codex_skill.mkdir(parents=True)
        (stale_codex_skill / "SKILL.md").write_text("# removed\n", encoding="utf-8")
        (stale_codex_skill / module.MANAGED_MARKER).write_text("agent-skills\n", encoding="utf-8")

        run_cli(["install", "user", "--platform", "codex", "--overwrite-skills"], home=home)
        assert_missing(stale_codex_skill)
        codex_agents = home / ".codex" / "AGENTS.md"
        assert_exists(codex_agents)
        assert_contains(codex_agents, "## Multi-Agent Rules")
        assert_contains(codex_agents, "## Skill Activation")
        assert_parallelism_plan_template(codex_agents)
        assert_governance_boundaries(codex_agents)
        assert_routing_semantics(codex_agents)
        assert_protocol_semantics(codex_agents)
        for skill_dir in module.discover_installable_skills():
            assert_exists(home / ".codex" / "skills" / skill_dir.name / "SKILL.md")

        run_cli(["verify", "user", "--platform", "codex"], home=home)

        stale_claude_skill = home / ".claude" / "skills" / "removed-skill"
        stale_claude_skill.mkdir(parents=True)
        (stale_claude_skill / "SKILL.md").write_text("# removed\n", encoding="utf-8")
        (stale_claude_skill / module.MANAGED_MARKER).write_text("agent-skills\n", encoding="utf-8")

        run_cli(["install", "user", "--platform", "claude-code", "--overwrite-skills"], home=home)
        assert_missing(stale_claude_skill)
        claude_md = home / ".claude" / "CLAUDE.md"
        assert_exists(claude_md)
        assert_contains(claude_md, "## Multi-Agent Rules")
        assert_contains(claude_md, "## Skill Activation")
        assert_parallelism_plan_template(claude_md)
        assert_governance_boundaries(claude_md)
        assert_routing_semantics(claude_md)
        assert_protocol_semantics(claude_md)
        for skill_dir in module.discover_installable_skills():
            assert_exists(home / ".claude" / "skills" / skill_dir.name / "SKILL.md")

        run_cli(["verify", "user", "--platform", "claude-code"], home=home)


def test_cursor_user_install_creates_mdc_rule(module) -> None:
    with tempfile.TemporaryDirectory(prefix="install-cursor-user-") as home_dir:
        home = Path(home_dir)

        run_cli(["install", "user", "--platform", "cursor", "--overwrite-skills"], home=home)

        mdc_file = home / ".cursor" / "rules" / "agent-skills.mdc"
        assert_exists(mdc_file)
        assert_contains(mdc_file, "alwaysApply: true")
        assert_contains(mdc_file, "# AGENTS.md")
        assert_contains(mdc_file, "## Behavioral Guidelines")
        assert_contains(mdc_file, "## Skill Activation")
        assert_contains(mdc_file, "## Multi-Agent Rules")
        assert_parallelism_plan_template(mdc_file)
        assert_governance_boundaries(mdc_file)
        assert_routing_semantics(mdc_file)
        assert_protocol_semantics(mdc_file)

        for skill_dir in module.discover_installable_skills():
            assert_exists(home / ".cursor" / "skills" / skill_dir.name / "SKILL.md")

        run_cli(["verify", "user", "--platform", "cursor"], home=home)


def test_zcode_user_install_installs_user_level_governance(module) -> None:
    with tempfile.TemporaryDirectory(prefix="install-zcode-user-") as home_dir:
        home = Path(home_dir)
        stale_zcode_skill = home / ".zcode" / "skills" / "removed-skill"
        stale_zcode_skill.mkdir(parents=True)
        (stale_zcode_skill / "SKILL.md").write_text("# removed\n", encoding="utf-8")
        (stale_zcode_skill / module.MANAGED_MARKER).write_text("agent-skills\n", encoding="utf-8")

        run_cli(["install", "user", "--platform", "zcode", "--overwrite-skills"], home=home)
        assert_missing(stale_zcode_skill)

        zcode_agents = home / ".zcode" / "AGENTS.md"
        assert_exists(zcode_agents)
        assert_contains(zcode_agents, "## Multi-Agent Rules")
        assert_contains(zcode_agents, "## Skill Activation")
        assert_parallelism_plan_template(zcode_agents)
        assert_governance_boundaries(zcode_agents)
        assert_routing_semantics(zcode_agents)
        assert_protocol_semantics(zcode_agents)
        for skill_dir in module.discover_installable_skills():
            assert_exists(home / ".zcode" / "skills" / skill_dir.name / "SKILL.md")

        run_cli(["verify", "user", "--platform", "zcode"], home=home)


def test_zcode_project_install_injects_agents_and_skips_project_skills() -> None:
    with tempfile.TemporaryDirectory(prefix="install-zcode-project-") as project_dir:
        project = Path(project_dir)

        result = run_cli(["install", "project", str(project), "--platform", "zcode", "--overwrite-skills"])
        assert_stdout_contains(result, "ZCode project-level skill installation is not automated")

        agents_md = project / "AGENTS.md"
        assert_exists(agents_md)
        assert_contains(agents_md, "## Multi-Agent Rules")
        assert_contains(agents_md, "## Skill Activation")
        assert_parallelism_plan_template(agents_md)
        assert_governance_boundaries(agents_md)
        assert_routing_semantics(agents_md)
        assert_protocol_semantics(agents_md)
        assert_missing(project / ".zcode" / "skills")

        verify_result = run_cli(["verify", "project", str(project), "--platform", "zcode"])
        assert_stdout_contains(verify_result, "ZCode project-level skill installation is not automated")


def test_legacy_flag_syntax_is_rejected() -> None:
    result = run_cli_allow_failure(["--global"])
    if result.returncode == 0:
        fail("expected legacy --global syntax to be rejected")
    if "Legacy flag syntax has been removed." not in result.stderr:
        fail(f"expected legacy-removal guidance, got stderr:\n{result.stderr}")
    if "install user" not in result.stderr:
        fail(f"expected replacement command in stderr, got stderr:\n{result.stderr}")


def test_partial_install_options_are_rejected() -> None:
    result = run_cli_allow_failure(["install", "user", "--components", "skills"])
    if result.returncode == 0:
        fail("expected partial install options to be rejected")
    if "Partial installation is no longer supported." not in result.stderr:
        fail(f"expected partial-install guidance, got stderr:\n{result.stderr}")


def test_mirror_command_is_rejected() -> None:
    result = run_cli_allow_failure(["mirror", "sync", "cursor"])
    if result.returncode == 0:
        fail("expected mirror command to be rejected")
    if "Repo-local mirror support has been removed." not in result.stderr:
        fail(f"expected mirror-removal guidance, got stderr:\n{result.stderr}")


def main() -> int:
    module = load_installer_module()
    test_project_install_installs_installable_skills(module)
    test_agents_template_selection()
    test_user_install_installs_user_level_governance(module)
    test_cursor_user_install_creates_mdc_rule(module)
    test_zcode_user_install_installs_user_level_governance(module)
    test_zcode_project_install_injects_agents_and_skips_project_skills()
    test_legacy_flag_syntax_is_rejected()
    test_partial_install_options_are_rejected()
    test_mirror_command_is_rejected()
    print("OK: manage-governance temporary-directory smoke tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
