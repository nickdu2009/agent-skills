#!/usr/bin/env python3
"""Single public installer for governance skills, rules injection, and local mirrors."""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = REPO_ROOT / "skills"
SKILL_FILE = "SKILL.md"
AGENTS_TEMPLATE_PATH = REPO_ROOT / "templates" / "governance" / "AGENTS-template.md"
CLAUDE_TEMPLATE_PATH = REPO_ROOT / "templates" / "governance" / "CLAUDE-template.md"


@dataclass(frozen=True)
class Profile:
    key: str
    display_name: str
    skills: tuple[str, ...]
    phase_skills: tuple[str, ...]
    inject_multi_agent_only: bool
    supports_phase: bool


@dataclass(frozen=True)
class MirrorTarget:
    key: str
    display_name: str
    target_dir: Path


@dataclass(frozen=True)
class GovernanceTemplate:
    path: Path
    title_line: str
    full_text: str
    multi_agent_text: str
    skill_escalation_text: str
    skill_lifecycle_text: str


FULL_PROFILE = Profile(
    key="full",
    display_name="Skill Governance Setup",
    skills=(
        "scoped-tasking",
        "plan-before-action",
        "minimal-change-strategy",
        "targeted-validation",
        "context-budget-awareness",
        "read-and-locate",
        "safe-refactor",
        "bugfix-workflow",
        "multi-agent-protocol",
        "conflict-resolution",
    ),
    phase_skills=(
        "phase-contract-tools",
        "phase-plan",
        "phase-execute",
    ),
    inject_multi_agent_only=False,
    supports_phase=True,
)

MULTI_AGENT_PROFILE = Profile(
    key="multi-agent",
    display_name="Multi-Agent Governance Setup",
    skills=(
        "multi-agent-protocol",
        "conflict-resolution",
    ),
    phase_skills=(),
    inject_multi_agent_only=True,
    supports_phase=False,
)

PROFILES = {
    FULL_PROFILE.key: FULL_PROFILE,
    MULTI_AGENT_PROFILE.key: MULTI_AGENT_PROFILE,
}

LOCAL_MIRROR_TARGETS = {
    "cursor": MirrorTarget(
        key="cursor",
        display_name="Cursor",
        target_dir=REPO_ROOT / ".cursor" / "skills",
    ),
    "claude": MirrorTarget(
        key="claude",
        display_name="Claude",
        target_dir=REPO_ROOT / ".claude" / "skills",
    ),
}


def detect_platforms() -> list[str]:
    platforms: list[str] = []
    if shutil.which("agent"):
        platforms.append("cursor-cli")
    if (Path.home() / ".cursor").is_dir():
        platforms.append("cursor")
    if (Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))).is_dir() or shutil.which("codex"):
        platforms.append("codex")
    if shutil.which("claude"):
        platforms.append("claude-code")
    return platforms


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def discover_source_skills() -> list[Path]:
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"Source skills directory not found: {SOURCE_DIR}")

    skill_dirs: list[Path] = []
    for child in sorted(SOURCE_DIR.iterdir()):
        if child.is_dir() and (child / SKILL_FILE).exists():
            skill_dirs.append(child)
    return skill_dirs


def discover_target_skills(target: MirrorTarget) -> list[Path]:
    if not target.target_dir.exists():
        return []
    return [child for child in sorted(target.target_dir.iterdir()) if child.is_dir()]


def collect_rel_files(root: Path) -> dict[str, Path]:
    if not root.exists():
        return {}

    out: dict[str, Path] = {}
    for path in root.rglob("*"):
        if path.is_file():
            out[path.relative_to(root).as_posix()] = path
    return out


def get_skill_target_dir(skill_name: str, platform: str) -> Path | None:
    if platform == "codex":
        return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills" / skill_name
    if platform in {"cursor", "cursor-cli"}:
        return Path.home() / ".cursor" / "skills" / skill_name
    if platform == "claude-code":
        return Path.home() / ".claude" / "skills" / skill_name
    return None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def find_section_bounds(lines: list[str], heading: str) -> tuple[int, int] | None:
    for start, line in enumerate(lines):
        if line != heading:
            continue
        end = len(lines)
        for idx in range(start + 1, len(lines)):
            if lines[idx].startswith("## "):
                end = idx
                break
        return start, end
    return None


def extract_section(path: Path, heading: str) -> str:
    lines = read_text(path).rstrip("\n").split("\n")
    bounds = find_section_bounds(lines, heading)
    if bounds is None:
        raise ValueError(f"Heading {heading!r} not found in {path}")
    start, end = bounds
    return ensure_trailing_newline("\n".join(lines[start:end]).rstrip("\n"))


def load_governance_template(path: Path) -> GovernanceTemplate:
    full_text = ensure_trailing_newline(read_text(path).rstrip("\n"))
    first_line = full_text.splitlines()[0]
    return GovernanceTemplate(
        path=path,
        title_line=first_line,
        full_text=full_text,
        multi_agent_text=extract_section(path, "## Multi-Agent Rules"),
        skill_escalation_text=extract_section(path, "## Skill Escalation"),
        skill_lifecycle_text=extract_section(path, "## Skill Lifecycle"),
    )


AGENTS_TEMPLATE = load_governance_template(AGENTS_TEMPLATE_PATH)
CLAUDE_TEMPLATE = load_governance_template(CLAUDE_TEMPLATE_PATH)


def create_initial_doc(template: GovernanceTemplate, profile: Profile) -> str:
    parts = [template.title_line, template.multi_agent_text.rstrip("\n")]
    if not profile.inject_multi_agent_only:
        parts.extend(
            [
                template.skill_escalation_text.rstrip("\n"),
                template.skill_lifecycle_text.rstrip("\n"),
            ]
        )
    return ensure_trailing_newline("\n\n".join(parts))


def replace_section(text: str, heading: str, replacement: str) -> str:
    lines = text.rstrip("\n").split("\n")
    bounds = find_section_bounds(lines, heading)
    if bounds is None:
        raise ValueError(f"Heading {heading!r} not present")
    start, end = bounds
    replacement_lines = replacement.rstrip("\n").split("\n")
    new_lines = lines[:start] + replacement_lines + lines[end:]
    return ensure_trailing_newline("\n".join(new_lines).rstrip("\n"))


def insert_after_title_or_start(text: str, snippet: str) -> str:
    lines = text.rstrip("\n").split("\n")
    snippet_lines = snippet.rstrip("\n").split("\n")
    if lines and lines[0].startswith("# ") and not lines[0].startswith("## "):
        new_lines = [lines[0], "", *snippet_lines]
        if len(lines) > 1:
            new_lines.extend(["", *lines[1:]])
        return ensure_trailing_newline("\n".join(new_lines).rstrip("\n"))
    new_lines = [*snippet_lines]
    if lines:
        new_lines.extend(["", *lines])
    return ensure_trailing_newline("\n".join(new_lines).rstrip("\n"))


def append_block(text: str, snippet: str) -> str:
    return ensure_trailing_newline(
        "\n\n".join([text.rstrip("\n"), snippet.rstrip("\n")]).rstrip("\n")
    )


def insert_before_heading(text: str, heading: str, snippet: str) -> str:
    lines = text.rstrip("\n").split("\n")
    bounds = find_section_bounds(lines, heading)
    if bounds is None:
        raise ValueError(f"Heading {heading!r} not present")
    start, _ = bounds
    snippet_lines = snippet.rstrip("\n").split("\n")
    new_lines = lines[:start]
    if new_lines and new_lines[-1] != "":
        new_lines.append("")
    new_lines.extend(snippet_lines)
    if start < len(lines) and snippet_lines and snippet_lines[-1] != "":
        new_lines.append("")
    new_lines.extend(lines[start:])
    return ensure_trailing_newline("\n".join(new_lines).rstrip("\n"))


def section_exists(text: str, heading: str) -> bool:
    return find_section_bounds(text.rstrip("\n").split("\n"), heading) is not None


def inject_multi_agent_rules(target_file: Path, template: GovernanceTemplate, *, update: bool) -> bool:
    if not target_file.exists():
        print(f"  CREATE: {target_file}")
        target_file.write_text(create_initial_doc(template, MULTI_AGENT_PROFILE), encoding="utf-8")
        return True

    text = read_text(target_file)
    changed = False
    if section_exists(text, "## Multi-Agent Rules"):
        if update:
            print(f"  UPDATE: ## Multi-Agent Rules in {target_file}")
            text = replace_section(text, "## Multi-Agent Rules", template.multi_agent_text)
            changed = True
        else:
            print(f"  EXISTS: {target_file} already has ## Multi-Agent Rules (use --update to replace)")
    else:
        print(f"  INSERT: ## Multi-Agent Rules (after title or at start) -> {target_file}")
        text = insert_after_title_or_start(text, template.multi_agent_text)
        changed = True

    if changed:
        target_file.write_text(text, encoding="utf-8")
    return changed


def inject_full_rules(target_file: Path, template: GovernanceTemplate, *, update: bool) -> bool:
    if not target_file.exists():
        print(f"  CREATE: {target_file}")
        target_file.write_text(create_initial_doc(template, FULL_PROFILE), encoding="utf-8")
        return True

    text = read_text(target_file)
    changed = False

    if section_exists(text, "## Multi-Agent Rules"):
        if update:
            print(f"  UPDATE: ## Multi-Agent Rules in {target_file}")
            text = replace_section(text, "## Multi-Agent Rules", template.multi_agent_text)
            changed = True
        else:
            print(f"  EXISTS: {target_file} already has ## Multi-Agent Rules (use --update to replace)")
    else:
        print(f"  INSERT: ## Multi-Agent Rules (after title or at start) -> {target_file}")
        text = insert_after_title_or_start(text, template.multi_agent_text)
        changed = True

    has_escalation = section_exists(text, "## Skill Escalation")
    has_lifecycle = section_exists(text, "## Skill Lifecycle")

    if not has_escalation and not has_lifecycle:
        print(f"  APPEND: skill escalation + lifecycle -> {target_file}")
        text = append_block(
            text,
            ensure_trailing_newline(
                "\n\n".join(
                    [
                        template.skill_escalation_text.rstrip("\n"),
                        template.skill_lifecycle_text.rstrip("\n"),
                    ]
                )
            ),
        )
        changed = True
    elif not has_escalation and has_lifecycle:
        print(f"  INSERT: ## Skill Escalation before ## Skill Lifecycle in {target_file}")
        text = insert_before_heading(text, "## Skill Lifecycle", template.skill_escalation_text)
        changed = True
    else:
        if has_escalation:
            if update:
                print(f"  UPDATE: ## Skill Escalation in {target_file}")
                text = replace_section(text, "## Skill Escalation", template.skill_escalation_text)
                changed = True
            else:
                print(f"  EXISTS: {target_file} already has ## Skill Escalation (use --update to replace)")
        if not has_lifecycle:
            print(f"  APPEND: ## Skill Lifecycle -> {target_file}")
            text = append_block(text, template.skill_lifecycle_text)
            changed = True
        else:
            if update:
                print(f"  UPDATE: ## Skill Lifecycle in {target_file}")
                text = replace_section(text, "## Skill Lifecycle", template.skill_lifecycle_text)
                changed = True
            else:
                print(f"  EXISTS: {target_file} already has ## Skill Lifecycle (use --update to replace)")

    if changed:
        target_file.write_text(text, encoding="utf-8")
    return changed


def inject_rules(project_dir: Path, platforms: list[str], profile: Profile, *, update: bool) -> None:
    seen_targets: set[Path] = set()
    for platform in platforms:
        if platform in {"codex", "cursor", "cursor-cli"}:
            target = project_dir / "AGENTS.md"
            template = AGENTS_TEMPLATE
        elif platform == "claude-code":
            target = project_dir / "CLAUDE.md"
            template = CLAUDE_TEMPLATE
        else:
            continue

        if target in seen_targets:
            continue
        seen_targets.add(target)

        if profile.inject_multi_agent_only:
            inject_multi_agent_rules(target, template, update=update)
        else:
            inject_full_rules(target, template, update=update)


def install_skill(skill_name: str, platform: str, *, force: bool) -> bool:
    source_dir = REPO_ROOT / "skills" / skill_name
    target_dir = get_skill_target_dir(skill_name, platform)
    if target_dir is None:
        print(f"  SKIP: unknown platform '{platform}'")
        return False

    if target_dir.exists():
        if force:
            print(f"  OVERWRITE: {target_dir}")
            shutil.rmtree(target_dir)
        else:
            print(f"  EXISTS: {target_dir} (use --force to overwrite)")
            return False

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
    print(f"  INSTALLED: {target_dir}")
    return True


def check_skill(skill_name: str, platform: str) -> bool:
    source = REPO_ROOT / "skills" / skill_name / "SKILL.md"
    target_dir = get_skill_target_dir(skill_name, platform)
    if target_dir is None:
        print(f"  SKIP CHECK: unknown platform '{platform}'")
        return False
    if not source.is_file():
        print(f"  MISSING SOURCE: {source}")
        return False
    target = target_dir / "SKILL.md"
    if not target_dir.is_dir() or not target.is_file():
        print(f"  NOT INSTALLED: {skill_name} -> {target_dir}")
        return False
    if filecmp.cmp(source, target, shallow=False):
        print(f"  OK: {skill_name} ({platform})")
        return True
    print(f"  MISMATCH: {skill_name} ({platform})")
    return False


def check_local_mirror(skill_dirs: list[Path], target: MirrorTarget) -> int:
    drift_found = False
    source_names = {skill_dir.name for skill_dir in skill_dirs}

    for skill_dir in sorted(skill_dirs, key=lambda p: p.name):
        dst_root = target.target_dir / skill_dir.name
        src_files = collect_rel_files(skill_dir)
        dst_files = collect_rel_files(dst_root) if dst_root.exists() else {}

        src_keys = set(src_files.keys())
        dst_keys = set(dst_files.keys())

        for rel in sorted(src_keys - dst_keys):
            drift_found = True
            print(f"MISSING {dst_root.relative_to(REPO_ROOT) / rel}")

        for rel in sorted(dst_keys - src_keys):
            drift_found = True
            print(f"EXTRA {dst_root.relative_to(REPO_ROOT) / rel}")

        for rel in sorted(src_keys & dst_keys):
            if file_sha256(src_files[rel]) != file_sha256(dst_files[rel]):
                drift_found = True
                print(f"OUTDATED {dst_root.relative_to(REPO_ROOT) / rel}")

    for target_dir in sorted(discover_target_skills(target), key=lambda p: p.name):
        if target_dir.name not in source_names:
            drift_found = True
            print(f"EXTRA {target_dir.relative_to(REPO_ROOT)}")

    if drift_found:
        print(f"{target.display_name} skill mirror is out of sync.")
        return 1

    print(f"{target.display_name} skill mirror is up to date.")
    return 0


def remove_stale_target_skills(skill_dirs: list[Path], target: MirrorTarget) -> None:
    source_names = {skill_dir.name for skill_dir in skill_dirs}

    for target_dir in discover_target_skills(target):
        if target_dir.name in source_names:
            continue

        shutil.rmtree(target_dir)
        print(f"REMOVED {target_dir.relative_to(REPO_ROOT)}")


def sync_local_mirror(skill_dirs: list[Path], target: MirrorTarget) -> int:
    target.target_dir.mkdir(parents=True, exist_ok=True)
    remove_stale_target_skills(skill_dirs, target)
    synced = 0

    for skill_dir in skill_dirs:
        dst = target.target_dir / skill_dir.name
        shutil.copytree(skill_dir, dst, dirs_exist_ok=True)
        synced += 1
        print(f"SYNCED {dst.relative_to(REPO_ROOT)}")

    print(f"Synced {synced} {target.display_name} skill(s).")
    return 0


def warn_phase_contract_if_missing(platform: str, skill_name: str) -> None:
    target_dir = get_skill_target_dir("phase-contract-tools", platform)
    if target_dir is not None and not target_dir.exists():
        print(f"  WARNING: {skill_name} expects phase-contract-tools at {target_dir} (missing); continuing.")


def build_parser(entrypoint_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=entrypoint_name,
        description=(
            "Install governance skills and inject AGENTS.md/CLAUDE.md rules. "
            "This is the single public installer entrypoint for consumers and maintainers. "
            "Use the default 'full' profile for the full skill governance suite, "
            "or '--profile multi-agent' for multi-agent governance only. "
            "Use the local mirror modes to rebuild repo-local Cursor/Claude mirrors."
        ),
    )
    parser.add_argument(
        "--profile",
        choices=tuple(PROFILES),
        default=FULL_PROFILE.key,
        help="Governance profile to install: 'full' (default) or 'multi-agent'.",
    )
    parser.add_argument("--skills-only", action="store_true", help="Install skills only (no AGENTS.md/CLAUDE.md changes)")
    parser.add_argument("--rules-only", metavar="DIR", help="Inject governance rules into AGENTS.md/CLAUDE.md in DIR")
    parser.add_argument("--project", metavar="DIR", help="Install skills AND inject rules into DIR")
    parser.add_argument("--check", action="store_true", help="Verify installed skills (SKILL.md matches source)")
    parser.add_argument("--update", action="store_true", help="Replace existing rule sections instead of skipping")
    parser.add_argument("--platform", help="Force platform: codex, cursor, cursor-cli, claude-code (auto-detected by default)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing skill installations")
    parser.add_argument(
        "--sync-local",
        choices=tuple(LOCAL_MIRROR_TARGETS),
        metavar="TARGET",
        help="Sync the repo-local skill mirror for TARGET: cursor or claude.",
    )
    parser.add_argument(
        "--check-local",
        choices=tuple(LOCAL_MIRROR_TARGETS),
        metavar="TARGET",
        help="Check whether the repo-local skill mirror for TARGET is in sync.",
    )
    parser.add_argument(
        "--include-phase",
        action="store_true",
        help="Also install phase-contract-tools, phase-plan, phase-execute (full profile only).",
    )

    parser.epilog = "\n".join(
        [
            "Examples:",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --project /path/to/my-repo",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --project /path/to/my-repo --include-phase",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --profile multi-agent --project /path/to/my-repo",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --profile multi-agent --rules-only /path/to/my-repo",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --check",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --sync-local cursor",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --check-local claude",
        ]
    )
    return parser


def parse_args(argv: list[str]) -> argparse.Namespace:
    entrypoint_name = Path(sys.argv[0]).name
    parser = build_parser(entrypoint_name)
    return parser.parse_args(argv)


def validate_mode(args: argparse.Namespace) -> tuple[str | None, Path | None]:
    selected = [
        args.skills_only,
        bool(args.rules_only),
        bool(args.project),
        args.check,
        bool(args.sync_local),
        bool(args.check_local),
    ]
    selected_count = sum(bool(x) for x in selected)
    if selected_count == 0:
        raise SystemExit("No mode specified. Use --help for usage.")
    if selected_count > 1:
        raise SystemExit("Choose exactly one mode: --skills-only, --rules-only, --project, --check, --sync-local, or --check-local.")

    if args.check:
        return "check", None
    if args.sync_local:
        return "sync-local", None
    if args.check_local:
        return "check-local", None
    if args.skills_only:
        return "skills", None
    if args.rules_only:
        return "rules", Path(args.rules_only)
    if args.project:
        return "all", Path(args.project)
    return None, None


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parse_args(argv)
    profile = PROFILES[args.profile]
    mode, project_dir = validate_mode(args)

    if mode in {"sync-local", "check-local"}:
        if args.platform:
            print("ERROR: --platform does not apply to local mirror modes")
            return 1
        if args.include_phase:
            print("ERROR: --include-phase does not apply to local mirror modes")
            return 1
        if args.profile != FULL_PROFILE.key:
            print("ERROR: --profile does not apply to local mirror modes")
            return 1

        target_key = args.sync_local or args.check_local
        assert target_key is not None
        target = LOCAL_MIRROR_TARGETS[target_key]

        try:
            skill_dirs = discover_source_skills()
        except FileNotFoundError as exc:
            print(str(exc), file=sys.stderr)
            return 2

        if not skill_dirs:
            print(f"No source skills found in {SOURCE_DIR}", file=sys.stderr)
            return 2

        print("")
        print(f"=== {target.display_name} Local Mirror ===")
        print("")
        if mode == "check-local":
            return check_local_mirror(skill_dirs, target)
        return sync_local_mirror(skill_dirs, target)

    if args.include_phase and not profile.supports_phase:
        print("ERROR: --include-phase is only supported with the 'full' profile")
        return 1

    print("")
    print(f"=== {profile.display_name} ===")
    print("")

    platforms = [args.platform] if args.platform else detect_platforms()
    if not platforms:
        print("No supported platform detected. Install Cursor, Codex, or Claude Code first.")
        return 1

    print(f"Detected platforms: {' '.join(platforms)}")
    print("")

    include_phase = bool(getattr(args, "include_phase", False))

    if mode == "check":
        failed = 0
        print("--- Verifying skills ---")
        for platform in platforms:
            print(f"Platform: {platform}")
            for skill in profile.skills:
                if not check_skill(skill, platform):
                    failed += 1
            if include_phase:
                for skill in profile.phase_skills:
                    if not check_skill(skill, platform):
                        failed += 1
            print("")
        if failed:
            print(f"Check failed: {failed} issue(s).")
            return 1
        print("All checked skills match source.")
        return 0

    exec_count = 0
    phase_count = 0

    if mode in {"skills", "all"}:
        print("--- Installing skills ---")
        for platform in platforms:
            print(f"Platform: {platform}")
            for skill in profile.skills:
                if install_skill(skill, platform, force=args.force):
                    exec_count += 1
            if include_phase:
                for skill in profile.phase_skills:
                    if skill in {"phase-plan", "phase-execute"}:
                        warn_phase_contract_if_missing(platform, skill)
                    if install_skill(skill, platform, force=args.force):
                        phase_count += 1
            print("")

    if mode in {"rules", "all"}:
        assert project_dir is not None
        if not project_dir.is_dir():
            print(f"ERROR: {project_dir} is not a directory")
            return 1
        print(f"--- Injecting rules into {project_dir} ---")
        inject_rules(project_dir, platforms, profile, update=args.update)
        print("")

    print("=== Summary ===")
    if mode in {"skills", "all"}:
        print(f"Installed {exec_count} execution/orchestration skill(s)")
        if include_phase:
            print(f"Installed {phase_count} phase skill(s)")
    if mode in {"rules", "all"}:
        print("Injected rules into AGENTS.md/CLAUDE.md")
    print("")

    print("=== Done ===")
    print("")
    print("Next steps:")
    if mode in {"skills", "all"}:
        print("  - Restart your agent (Cursor/Codex/Claude Code) to pick up new skills")
    if mode in {"rules", "all"}:
        if profile.inject_multi_agent_only:
            print("  - Review the Multi-Agent Rules section in your AGENTS.md/CLAUDE.md")
        else:
            print("  - Review governance sections in AGENTS.md/CLAUDE.md")
    print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
