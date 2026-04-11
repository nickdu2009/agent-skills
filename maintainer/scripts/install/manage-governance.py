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
class MirrorTarget:
    key: str
    display_name: str
    target_dir: Path


@dataclass(frozen=True)
class GovernanceSection:
    heading: str
    text: str


@dataclass(frozen=True)
class GovernanceTemplate:
    path: Path
    title_line: str
    full_text: str
    sections: tuple[GovernanceSection, ...]


INSTALL_DISPLAY_NAME = "Skill Governance Setup"

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


def get_skill_target_dir(skill_name: str, platform: str, project_dir: Path | None = None) -> Path | None:
    if project_dir is not None:
        if platform == "codex":
            return project_dir / ".codex" / "skills" / skill_name
        if platform in {"cursor", "cursor-cli"}:
            return project_dir / ".cursor" / "skills" / skill_name
        if platform == "claude-code":
            return project_dir / ".claude" / "skills" / skill_name
        return None
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


def extract_sections(path: Path) -> tuple[GovernanceSection, ...]:
    lines = read_text(path).rstrip("\n").split("\n")
    headings = [line for line in lines if line.startswith("## ")]
    if not headings:
        raise ValueError(f"No governance sections found in {path}")
    return tuple(
        GovernanceSection(heading=heading, text=extract_section(path, heading))
        for heading in headings
    )


def load_governance_template(path: Path) -> GovernanceTemplate:
    full_text = ensure_trailing_newline(read_text(path).rstrip("\n"))
    first_line = full_text.splitlines()[0]
    return GovernanceTemplate(
        path=path,
        title_line=first_line,
        full_text=full_text,
        sections=extract_sections(path),
    )


AGENTS_TEMPLATE = load_governance_template(AGENTS_TEMPLATE_PATH)
CLAUDE_TEMPLATE = load_governance_template(CLAUDE_TEMPLATE_PATH)


def all_template_sections(template: GovernanceTemplate) -> tuple[GovernanceSection, ...]:
    return template.sections


def render_doc(template: GovernanceTemplate, sections: tuple[GovernanceSection, ...]) -> str:
    parts = [template.title_line]
    parts.extend(section.text.rstrip("\n") for section in sections)
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


def insert_after_heading(text: str, heading: str, snippet: str) -> str:
    lines = text.rstrip("\n").split("\n")
    bounds = find_section_bounds(lines, heading)
    if bounds is None:
        raise ValueError(f"Heading {heading!r} not present")
    _, end = bounds
    snippet_lines = snippet.rstrip("\n").split("\n")
    new_lines = lines[:end]
    if new_lines and new_lines[-1] != "":
        new_lines.append("")
    new_lines.extend(snippet_lines)
    if end < len(lines) and snippet_lines and snippet_lines[-1] != "":
        new_lines.append("")
    new_lines.extend(lines[end:])
    return ensure_trailing_newline("\n".join(new_lines).rstrip("\n"))


def section_exists(text: str, heading: str) -> bool:
    return find_section_bounds(text.rstrip("\n").split("\n"), heading) is not None


def insert_section_in_order(
    text: str,
    section: GovernanceSection,
    ordered_headings: tuple[str, ...],
) -> str:
    idx = ordered_headings.index(section.heading)
    for later_heading in ordered_headings[idx + 1:]:
        if section_exists(text, later_heading):
            return insert_before_heading(text, later_heading, section.text)
    for earlier_heading in reversed(ordered_headings[:idx]):
        if section_exists(text, earlier_heading):
            return insert_after_heading(text, earlier_heading, section.text)
    return insert_after_title_or_start(text, section.text)


def inject_rule_sections(
    target_file: Path,
    template: GovernanceTemplate,
    sections: tuple[GovernanceSection, ...],
    *,
    update: bool,
) -> bool:
    if not target_file.exists():
        print(f"  CREATE: {target_file}")
        target_file.write_text(render_doc(template, sections), encoding="utf-8")
        return True

    text = read_text(target_file)
    changed = False
    ordered_headings = tuple(section.heading for section in template.sections)

    for section in sections:
        if section_exists(text, section.heading):
            if update:
                print(f"  UPDATE: {section.heading} in {target_file}")
                text = replace_section(text, section.heading, section.text)
                changed = True
            else:
                print(f"  EXISTS: {target_file} already has {section.heading} (use --update to replace)")
            continue

        if section.heading == "## Multi-Agent Rules":
            print(f"  INSERT: {section.heading} (after title or at start) -> {target_file}")
        else:
            print(f"  INSERT: {section.heading} in template order -> {target_file}")
        text = insert_section_in_order(text, section, ordered_headings)
        changed = True

    if changed:
        target_file.write_text(text, encoding="utf-8")
    return changed


def inject_full_rules(target_file: Path, template: GovernanceTemplate, *, update: bool) -> bool:
    return inject_rule_sections(
        target_file,
        template,
        all_template_sections(template),
        update=update,
    )


def inject_rules(project_dir: Path, platforms: list[str], *, update: bool) -> None:
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

        inject_full_rules(target, template, update=update)


def install_skill(skill_name: str, platform: str, *, force: bool, project_dir: Path | None = None) -> bool:
    source_dir = REPO_ROOT / "skills" / skill_name
    target_dir = get_skill_target_dir(skill_name, platform, project_dir)
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


def check_skill(skill_name: str, platform: str, project_dir: Path | None = None) -> bool:
    source = REPO_ROOT / "skills" / skill_name / "SKILL.md"
    target_dir = get_skill_target_dir(skill_name, platform, project_dir)
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


def build_parser(entrypoint_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=entrypoint_name,
        description=(
            "Install governance skills and inject AGENTS.md/CLAUDE.md rules. "
            "This is the single public installer entrypoint for consumers and maintainers."
        ),
    )

    # --- Target (mutually exclusive) ---
    target = parser.add_mutually_exclusive_group()
    target.add_argument(
        "--project", metavar="DIR",
        help="Install skills + rules into project directory (skills go to DIR/.claude/skills/ etc.).",
    )
    target.add_argument(
        "--global", action="store_true", dest="global_install",
        help="Install skills to global platform directories (~/.claude/skills/ etc.).",
    )
    target.add_argument(
        "--sync-local",
        choices=tuple(LOCAL_MIRROR_TARGETS),
        metavar="TARGET",
        help="Sync the repo-local skill mirror for TARGET: cursor or claude.",
    )

    # --- Action modifier ---
    parser.add_argument(
        "--check", action="store_true",
        help="Verify installed skills instead of installing. Works with any target.",
    )

    # --- Install modifiers (--project only) ---
    parser.add_argument(
        "--rules-only", action="store_true",
        help="Skip skill installation, inject rules only (requires --project).",
    )
    parser.add_argument(
        "--skills-only", action="store_true",
        help="Skip rule injection, install skills only (requires --project).",
    )

    # --- Options ---
    parser.add_argument("--platform", help="Force platform: codex, cursor, cursor-cli, claude-code (auto-detected by default)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing skill installations")
    parser.add_argument("--update", action="store_true", help="Replace existing rule sections instead of skipping")

    parser.epilog = "\n".join(
        [
            "Examples:",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --project /path/to/my-repo",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --project /path/to/my-repo --rules-only",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --project /path/to/my-repo --check",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --global",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --global --check",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --sync-local cursor",
            f"  python3 maintainer/scripts/install/{entrypoint_name} --sync-local cursor --check",
        ]
    )
    return parser


def parse_args(argv: list[str]) -> argparse.Namespace:
    entrypoint_name = Path(sys.argv[0]).name
    parser = build_parser(entrypoint_name)
    return parser.parse_args(argv)


def validate_mode(args: argparse.Namespace) -> tuple[str, Path | None]:
    has_project = bool(args.project)
    has_global = args.global_install
    has_sync_local = bool(args.sync_local)

    target_count = sum([has_project, has_global, has_sync_local])
    if target_count == 0:
        raise SystemExit("No target specified. Use --project DIR, --global, or --sync-local TARGET.")

    if (args.rules_only or args.skills_only) and not has_project:
        raise SystemExit("--rules-only and --skills-only require --project.")
    if args.rules_only and args.skills_only:
        raise SystemExit("Cannot use --rules-only and --skills-only together.")

    if has_sync_local:
        return ("check-local" if args.check else "sync-local"), None

    if has_global:
        return ("check-global" if args.check else "global"), None

    project_dir = Path(args.project)
    if args.check:
        return "check-project", project_dir
    if args.rules_only:
        return "rules", project_dir
    if args.skills_only:
        return "skills-project", project_dir
    return "project", project_dir


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parse_args(argv)
    mode, project_dir = validate_mode(args)

    # --- sync-local / check-local ---
    if mode in {"sync-local", "check-local"}:
        if args.platform:
            print("ERROR: --platform does not apply to local mirror modes")
            return 1

        target_key = args.sync_local
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

    # --- check-global / check-project ---
    if mode in {"check-global", "check-project"}:
        platforms = [args.platform] if args.platform else detect_platforms()
        if not platforms:
            print("No supported platform detected. Install Cursor, Codex, or Claude Code first.")
            return 1

        check_dir = project_dir if mode == "check-project" else None
        location = f"project ({project_dir})" if check_dir else "global"
        skill_dirs = discover_source_skills()
        skill_names = tuple(skill_dir.name for skill_dir in skill_dirs)

        print("")
        print(f"=== Verifying Skills ({location}) ===")
        print("")

        failed = 0
        for platform in platforms:
            print(f"Platform: {platform}")
            for skill in skill_names:
                if not check_skill(skill, platform, check_dir):
                    failed += 1
            print("")
        if failed:
            print(f"Check failed: {failed} issue(s).")
            return 1
        print("All checked skills match source.")
        return 0

    # --- install modes: global, project, skills-project, rules ---
    print("")
    print(f"=== {INSTALL_DISPLAY_NAME} ===")
    print("")

    platforms = [args.platform] if args.platform else detect_platforms()
    if not platforms:
        print("No supported platform detected. Install Cursor, Codex, or Claude Code first.")
        return 1

    print(f"Detected platforms: {' '.join(platforms)}")
    print("")

    skill_dirs = discover_source_skills()
    skill_names = tuple(skill_dir.name for skill_dir in skill_dirs)
    do_install_skills = mode in {"global", "project", "skills-project"}
    do_inject_rules = mode in {"project", "rules"}
    skill_target_dir = project_dir if mode in {"project", "skills-project"} else None

    installed_count = 0

    if do_install_skills:
        location = f"project ({project_dir})" if skill_target_dir else "global"
        print(f"--- Installing skills ({location}) ---")
        for platform in platforms:
            print(f"Platform: {platform}")
            for skill in skill_names:
                if install_skill(skill, platform, force=args.force, project_dir=skill_target_dir):
                    installed_count += 1
            print("")

    if do_inject_rules:
        assert project_dir is not None
        if not project_dir.is_dir():
            print(f"ERROR: {project_dir} is not a directory")
            return 1
        print(f"--- Injecting rules into {project_dir} ---")
        inject_rules(project_dir, platforms, update=args.update)
        print("")

    print("=== Summary ===")
    if do_install_skills:
        location = f"project ({project_dir})" if skill_target_dir else "global"
        print(f"Installed {installed_count} skill(s) ({location})")
    if do_inject_rules:
        print("Injected rules into AGENTS.md/CLAUDE.md")
    print("")

    print("=== Done ===")
    print("")
    print("Next steps:")
    if do_install_skills:
        print("  - Restart your agent (Cursor/Codex/Claude Code) to pick up new skills")
    if do_inject_rules:
        print("  - Review governance sections in AGENTS.md/CLAUDE.md")
    print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
