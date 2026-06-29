#!/usr/bin/env python3
"""Single public installer for the published skill bundle and governance templates."""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = REPO_ROOT / "skills"
SKILL_FILE = "SKILL.md"
MANAGED_MARKER = ".agent-skills-managed"
AGENTS_TEMPLATE_PATH = REPO_ROOT / "templates" / "governance" / "AGENTS-template.md"
CLAUDE_TEMPLATE_PATH = REPO_ROOT / "templates" / "governance" / "CLAUDE-template.md"
CURSOR_MDC_TEMPLATE_PATH = REPO_ROOT / "templates" / "governance" / "cursor-agent-skills.mdc"
CURSOR_MDC_PLACEHOLDER = "{{GOVERNANCE_BODY}}"
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
SUPPORTED_PLATFORMS = ("codex", "cursor", "cursor-cli", "claude-code", "zcode")
FORCE_PLATFORM_HELP = (
    "Force platform: codex, cursor, cursor-cli, claude-code, zcode "
    "(auto-detected by default)"
)
REMOVED_LEGACY_FLAGS = {
    "--global",
    "--project",
    "--check",
    "--skills-only",
    "--rules-only",
    "--components",
    "--force",
    "--update",
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
    if (Path.home() / ".zcode").is_dir():
        platforms.append("zcode")
    return platforms


def discover_source_skills() -> list[Path]:
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"Source skills directory not found: {SOURCE_DIR}")

    skill_dirs: list[Path] = []
    for child in sorted(SOURCE_DIR.iterdir()):
        if child.is_dir() and (child / SKILL_FILE).exists():
            skill_dirs.append(child)
    return skill_dirs


def discover_installable_skills() -> list[Path]:
    return discover_source_skills()


def get_skill_root_dir(platform: str, project_dir: Path | None = None) -> Path | None:
    if project_dir is not None:
        if platform == "codex":
            return project_dir / ".codex" / "skills"
        if platform in {"cursor", "cursor-cli"}:
            return project_dir / ".cursor" / "skills"
        if platform == "claude-code":
            return project_dir / ".claude" / "skills"
        return None
    if platform == "codex":
        return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills"
    if platform in {"cursor", "cursor-cli"}:
        return Path.home() / ".cursor" / "skills"
    if platform == "claude-code":
        return Path.home() / ".claude" / "skills"
    if platform == "zcode":
        return Path.home() / ".zcode" / "skills"
    return None


def get_skill_target_dir(skill_name: str, platform: str, project_dir: Path | None = None) -> Path | None:
    root_dir = get_skill_root_dir(platform, project_dir)
    if root_dir is None:
        return None
    return root_dir / skill_name


def get_governance_target(platform: str, project_dir: Path | None = None) -> tuple[Path, GovernanceTemplate] | None:
    if project_dir is not None:
        if platform in {"codex", "cursor", "cursor-cli", "zcode"}:
            return project_dir / "AGENTS.md", AGENTS_TEMPLATE
        if platform == "claude-code":
            return project_dir / "CLAUDE.md", CLAUDE_TEMPLATE
        return None
    if platform == "codex":
        return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "AGENTS.md", AGENTS_TEMPLATE
    if platform == "claude-code":
        return Path.home() / ".claude" / "CLAUDE.md", CLAUDE_TEMPLATE
    if platform == "zcode":
        return Path.home() / ".zcode" / "AGENTS.md", AGENTS_TEMPLATE
    return None


def get_skill_skip_reason(platform: str, project_dir: Path | None = None) -> str | None:
    if project_dir is not None and platform == "zcode":
        return (
            "ZCode project-level skill installation is not automated because "
            "official docs only document the user-level path "
            "`~/.zcode/skills`. Use `install user --platform zcode` for shared "
            "skills or import them into the current project from ZCode Settings "
            "-> Skills."
        )
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


def render_cursor_mdc() -> str:
    """Render the Cursor .mdc rule by replacing the placeholder with governance body."""
    mdc_raw = read_text(CURSOR_MDC_TEMPLATE_PATH)
    parts = ["# AGENTS.md"]
    for section in AGENTS_TEMPLATE.sections:
        parts.append(section.text.rstrip("\n"))
    body = "\n\n".join(parts)
    return ensure_trailing_newline(mdc_raw.replace(CURSOR_MDC_PLACEHOLDER, body))


def get_cursor_mdc_target() -> Path:
    return Path.home() / ".cursor" / "rules" / "agent-skills.mdc"


def install_cursor_mdc(*, update: bool) -> bool:
    target = get_cursor_mdc_target()
    rendered = render_cursor_mdc()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if not update:
            print(f"  EXISTS: {target} (use --replace-rules to replace)")
            return False
        existing = read_text(target)
        if existing == rendered:
            print(f"  UP-TO-DATE: {target}")
            return False
        print(f"  UPDATE: {target}")
    else:
        print(f"  CREATE: {target}")
    target.write_text(rendered, encoding="utf-8")
    return True


def check_cursor_mdc() -> bool:
    target = get_cursor_mdc_target()
    if not target.is_file():
        print(f"  NOT INSTALLED: Cursor .mdc rule -> {target}")
        return False
    rendered = render_cursor_mdc()
    existing = read_text(target)
    if existing == rendered:
        print(f"  OK: Cursor .mdc rule -> {target}")
        return True
    print(f"  OUTDATED: Cursor .mdc rule -> {target}")
    return False


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
    target_file.parent.mkdir(parents=True, exist_ok=True)
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
                print(f"  EXISTS: {target_file} already has {section.heading} (use --replace-rules to replace)")
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


def inject_rules(project_dir: Path | None, platforms: list[str], *, update: bool) -> int:
    seen_targets: set[Path] = set()
    changed_count = 0
    for platform in platforms:
        target_info = get_governance_target(platform, project_dir)
        if target_info is None:
            if project_dir is None and platform in {"cursor", "cursor-cli"}:
                mdc_target = get_cursor_mdc_target()
                if mdc_target not in seen_targets:
                    seen_targets.add(mdc_target)
                    if install_cursor_mdc(update=update):
                        changed_count += 1
            else:
                print(f"  SKIP: unknown platform '{platform}'")
            continue
        target, template = target_info

        if target in seen_targets:
            continue
        seen_targets.add(target)

        if inject_full_rules(target, template, update=update):
            changed_count += 1
    return changed_count


def check_governance(
    platform: str,
    project_dir: Path | None = None,
    seen: set[Path] | None = None,
) -> bool:
    target_info = get_governance_target(platform, project_dir)
    if target_info is None:
        if project_dir is None and platform in {"cursor", "cursor-cli"}:
            mdc_target = get_cursor_mdc_target()
            if seen is not None:
                if mdc_target in seen:
                    return True
                seen.add(mdc_target)
            return check_cursor_mdc()
        print(f"  SKIP CHECK: unknown platform '{platform}'")
        return False
    target, template = target_info
    if not target.is_file():
        print(f"  NOT INSTALLED: governance rules -> {target}")
        return False

    text = read_text(target)
    lines = text.rstrip("\n").split("\n")
    ok = True
    for section in template.sections:
        bounds = find_section_bounds(lines, section.heading)
        if bounds is None:
            print(f"  MISSING: {section.heading} in {target}")
            ok = False
            continue
        start, end = bounds
        actual = ensure_trailing_newline("\n".join(lines[start:end]).rstrip("\n"))
        if actual != section.text:
            print(f"  OUTDATED: {section.heading} in {target}")
            ok = False
    if ok:
        print(f"  OK: governance rules ({platform}) -> {target}")
    return ok


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
            print(f"  EXISTS: {target_dir} (use --overwrite-skills to overwrite)")
            return False

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
    (target_dir / MANAGED_MARKER).write_text("agent-skills\n", encoding="utf-8")
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


def remove_stale_installed_skills(skill_dirs: list[Path], platform: str, project_dir: Path | None = None) -> int:
    root_dir = get_skill_root_dir(platform, project_dir)
    if root_dir is None or not root_dir.exists():
        return 0

    source_names = {skill_dir.name for skill_dir in skill_dirs}
    removed = 0
    for target_dir in sorted((child for child in root_dir.iterdir() if child.is_dir()), key=lambda p: p.name):
        if target_dir.name in source_names:
            continue
        if not (target_dir / MANAGED_MARKER).is_file():
            continue
        shutil.rmtree(target_dir)
        removed += 1
        print(f"  REMOVED STALE: {target_dir}")
    return removed


def check_stale_installed_skills(skill_dirs: list[Path], platform: str, project_dir: Path | None = None) -> int:
    root_dir = get_skill_root_dir(platform, project_dir)
    if root_dir is None or not root_dir.exists():
        return 0

    source_names = {skill_dir.name for skill_dir in skill_dirs}
    extra_count = 0
    for target_dir in sorted((child for child in root_dir.iterdir() if child.is_dir()), key=lambda p: p.name):
        if target_dir.name in source_names:
            continue
        if not (target_dir / MANAGED_MARKER).is_file():
            continue
        extra_count += 1
        print(f"  EXTRA: stale installed skill -> {target_dir}")
    return extra_count


def get_option_value(argv: list[str], option: str, fallback: str) -> str:
    try:
        idx = argv.index(option)
    except ValueError:
        return fallback
    if idx + 1 >= len(argv):
        return fallback
    value = argv[idx + 1]
    if value.startswith("-"):
        return fallback
    return value


def build_legacy_replacement(argv: list[str]) -> str | None:
    if "--global" in argv or "--project" in argv:
        command: list[str] = ["verify" if "--check" in argv else "install"]
        if "--global" in argv:
            command.append("user")
        else:
            project_dir = get_option_value(argv, "--project", "DIR")
            command.extend(["project", project_dir])

        platform = get_option_value(argv, "--platform", "")
        if platform:
            command.extend(["--platform", platform])
        if "--force" in argv:
            command.append("--overwrite-skills")
        if "--update" in argv or "--rules-only" in argv:
            command.append("--replace-rules")
        return " ".join(command)

    return None


def reject_removed_legacy_flags(
    argv: list[str], parser: argparse.ArgumentParser, entrypoint_name: str
) -> None:
    if argv and argv[0] == "mirror":
        parser.error(
            "\n".join(
                [
                    "Repo-local mirror support has been removed.",
                    "The public installer now only supports install/verify for user-level and project-level targets.",
                    "",
                    "Use one of:",
                    f"  python3 maintainer/scripts/install/{entrypoint_name} install user",
                    f"  python3 maintainer/scripts/install/{entrypoint_name} verify user",
                    f"  python3 maintainer/scripts/install/{entrypoint_name} install project DIR",
                    f"  python3 maintainer/scripts/install/{entrypoint_name} verify project DIR",
                ]
            )
        )

    legacy_flags = [token for token in argv if token in REMOVED_LEGACY_FLAGS]
    if not legacy_flags:
        return

    if "--sync-local" in argv or "--check-local" in argv:
        parser.error(
            "\n".join(
                [
                    "Repo-local mirror support has been removed.",
                    "The public installer now only supports install/verify for user-level and project-level targets.",
                    "",
                    "Use one of:",
                    f"  python3 maintainer/scripts/install/{entrypoint_name} install user",
                    f"  python3 maintainer/scripts/install/{entrypoint_name} verify user",
                    f"  python3 maintainer/scripts/install/{entrypoint_name} install project DIR",
                    f"  python3 maintainer/scripts/install/{entrypoint_name} verify project DIR",
                ]
            )
        )

    if "--components" in argv:
        parser.error(
            "\n".join(
                [
                    "Partial installation is no longer supported.",
                    "This installer always installs the full bundle: skills plus governance templates.",
                    "",
                    "Use one of:",
                    f"  python3 maintainer/scripts/install/{entrypoint_name} install user",
                    f"  python3 maintainer/scripts/install/{entrypoint_name} install project DIR",
                    "",
                    "Adjustment flags:",
                    "  --overwrite-skills",
                    "  --replace-rules",
                ]
            )
        )

    replacement = build_legacy_replacement(argv)
    lines = [
        "Legacy flag syntax has been removed.",
        "Use the subcommand-based CLI instead.",
    ]
    if replacement is not None:
        lines.extend(
            [
                "",
                "Closest replacement:",
                f"  python3 maintainer/scripts/install/{entrypoint_name} {replacement}",
            ]
        )

    lines.extend(
        [
            "",
            "Key migrations:",
            "  --global -> install user / verify user",
            "  --project DIR -> install project DIR / verify project DIR",
            "  partial install is no longer supported; install always installs the full bundle",
            "  --force -> --overwrite-skills",
            "  --update -> --replace-rules",
        ]
    )
    parser.error("\n".join(lines))


def build_modern_parser(entrypoint_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=entrypoint_name,
        description=(
            "Install and verify governance skills and AGENTS.md/CLAUDE.md rules. "
            "This is the single public CLI entrypoint for end users."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    install_parser = subparsers.add_parser(
        "install",
        help="Install the full bundle: skills plus governance templates.",
    )
    install_targets = install_parser.add_subparsers(dest="scope")
    install_targets.required = True

    install_user = install_targets.add_parser(
        "user",
        help="Install into user-level platform locations.",
    )
    install_user.add_argument(
        "--platform",
        choices=SUPPORTED_PLATFORMS,
        help=FORCE_PLATFORM_HELP,
    )
    install_user.add_argument(
        "--overwrite-skills",
        action="store_true",
        help="Overwrite existing managed skill installations.",
    )
    install_user.add_argument(
        "--replace-rules",
        action="store_true",
        help="Replace existing managed governance sections instead of skipping them.",
    )

    install_project = install_targets.add_parser(
        "project",
        help="Install into a target project directory.",
    )
    install_project.add_argument("directory", metavar="DIR", help="Target project directory.")
    install_project.add_argument(
        "--platform",
        choices=SUPPORTED_PLATFORMS,
        help=FORCE_PLATFORM_HELP,
    )
    install_project.add_argument(
        "--overwrite-skills",
        action="store_true",
        help="Overwrite existing managed skill installations.",
    )
    install_project.add_argument(
        "--replace-rules",
        action="store_true",
        help="Replace existing managed governance sections instead of skipping them.",
    )

    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify the installed bundle: skills plus governance templates.",
    )
    verify_targets = verify_parser.add_subparsers(dest="scope")
    verify_targets.required = True

    verify_user = verify_targets.add_parser(
        "user",
        help="Verify user-level platform installation.",
    )
    verify_user.add_argument(
        "--platform",
        choices=SUPPORTED_PLATFORMS,
        help=FORCE_PLATFORM_HELP,
    )

    verify_project = verify_targets.add_parser(
        "project",
        help="Verify a project installation.",
    )
    verify_project.add_argument("directory", metavar="DIR", help="Target project directory.")
    verify_project.add_argument(
        "--platform",
        choices=SUPPORTED_PLATFORMS,
        help=FORCE_PLATFORM_HELP,
    )

    parser.epilog = "\n".join(
        [
            "Examples:",
            f"  python3 maintainer/scripts/install/{entrypoint_name} install user",
            f"  python3 maintainer/scripts/install/{entrypoint_name} verify user",
            f"  python3 maintainer/scripts/install/{entrypoint_name} install user --replace-rules",
            f"  python3 maintainer/scripts/install/{entrypoint_name} install project /path/to/my-repo",
            f"  python3 maintainer/scripts/install/{entrypoint_name} verify project /path/to/my-repo",
        ]
    )
    return parser


def modern_args_to_runtime_namespace(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> argparse.Namespace:
    if args.command not in {"install", "verify"}:
        parser.error(f"Unsupported command: {args.command}")

    overwrite_skills = bool(getattr(args, "overwrite_skills", False))
    replace_rules = bool(getattr(args, "replace_rules", False))

    return argparse.Namespace(
        project=args.directory if args.scope == "project" else None,
        user_install=args.scope == "user",
        check=args.command == "verify",
        platform=getattr(args, "platform", None),
        force=overwrite_skills,
        update=replace_rules,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    entrypoint_name = Path(sys.argv[0]).name
    modern_parser = build_modern_parser(entrypoint_name)
    reject_removed_legacy_flags(list(argv), modern_parser, entrypoint_name)
    modern_args = modern_parser.parse_args(argv)
    return modern_args_to_runtime_namespace(modern_args, modern_parser)


def validate_mode(args: argparse.Namespace) -> tuple[str, Path | None]:
    has_project = bool(args.project)
    has_user = args.user_install

    target_count = sum([has_project, has_user])
    if target_count == 0:
        raise SystemExit(
            "No target specified. Use install user, install project DIR, verify user, or verify project DIR."
        )

    if has_user:
        if args.check:
            return "check-user", None
        return "user", None

    project_dir = Path(args.project)
    if args.check:
        return "check-project", project_dir
    return "project", project_dir


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parse_args(argv)
    mode, project_dir = validate_mode(args)

    # --- check-user / check-project ---
    if mode in {
        "check-user",
        "check-project",
    }:
        platforms = [args.platform] if args.platform else detect_platforms()
        if not platforms:
            print("No supported platform detected. Install Cursor, Codex, Claude Code, or ZCode first.")
            return 1

        is_project_check = mode == "check-project"
        check_dir = project_dir if is_project_check else None
        location = f"project ({project_dir})" if check_dir else "user-level"
        skill_dirs = discover_installable_skills()
        skill_names = tuple(skill_dir.name for skill_dir in skill_dirs)
        check_skills = True
        check_rules = True

        print("")
        print(f"=== Verifying Skill Governance Setup ({location}) ===")
        print("")

        failed = 0
        if check_skills:
            print("--- Verifying skills ---")
            checked_skill_roots: set[Path] = set()
            for platform in platforms:
                print(f"Platform: {platform}")
                skip_reason = get_skill_skip_reason(platform, check_dir)
                if skip_reason is not None:
                    print(f"  SKIP CHECK: {skip_reason}")
                    print("")
                    continue
                for skill in skill_names:
                    if not check_skill(skill, platform, check_dir):
                        failed += 1
                skill_root = get_skill_root_dir(platform, check_dir)
                if skill_root is not None and skill_root not in checked_skill_roots:
                    checked_skill_roots.add(skill_root)
                    failed += check_stale_installed_skills(skill_dirs, platform, check_dir)
                print("")
        if check_rules:
            print("--- Verifying governance rules ---")
            checked_governance_targets: set[Path] = set()
            for platform in platforms:
                print(f"Platform: {platform}")
                if not check_governance(platform, check_dir, checked_governance_targets):
                    failed += 1
                print("")
        if failed:
            print(f"Check failed: {failed} issue(s).")
            return 1
        print("All checked skills and governance rules match source.")
        return 0

    # --- install modes: user or project ---
    print("")
    print(f"=== {INSTALL_DISPLAY_NAME} ===")
    print("")

    platforms = [args.platform] if args.platform else detect_platforms()
    if not platforms:
        print("No supported platform detected. Install Cursor, Codex, Claude Code, or ZCode first.")
        return 1

    print(f"Detected platforms: {' '.join(platforms)}")
    print("")

    skill_dirs = discover_installable_skills()
    skill_names = tuple(skill_dir.name for skill_dir in skill_dirs)
    do_install_skills = mode in {"user", "project"}
    do_inject_rules = mode in {"user", "project"}
    skill_target_dir = project_dir if mode == "project" else None

    installed_count = 0
    injected_count = 0

    if do_install_skills:
        location = f"project ({project_dir})" if skill_target_dir else "user-level"
        print(f"--- Installing skills ({location}) ---")
        synced_skill_roots: set[Path] = set()
        for platform in platforms:
            print(f"Platform: {platform}")
            skip_reason = get_skill_skip_reason(platform, skill_target_dir)
            if skip_reason is not None:
                print(f"  SKIP: {skip_reason}")
                print("")
                continue
            skill_root = get_skill_root_dir(platform, skill_target_dir)
            if skill_root is not None and skill_root not in synced_skill_roots:
                synced_skill_roots.add(skill_root)
                remove_stale_installed_skills(skill_dirs, platform, skill_target_dir)
            for skill in skill_names:
                if install_skill(skill, platform, force=args.force, project_dir=skill_target_dir):
                    installed_count += 1
            print("")

    if do_inject_rules:
        if project_dir is not None and not project_dir.is_dir():
            print(f"ERROR: {project_dir} is not a directory")
            return 1
        location = f"project ({project_dir})" if project_dir else "user-level platform files"
        print(f"--- Injecting rules into {location} ---")
        injected_count = inject_rules(project_dir, platforms, update=args.update)
        print("")

    print("=== Summary ===")
    if do_install_skills:
        location = f"project ({project_dir})" if skill_target_dir else "user-level"
        print(f"Installed {installed_count} skill(s) ({location})")
    if do_inject_rules:
        location = "project governance file(s)" if project_dir else "user-level governance file(s)"
        print(f"Updated {injected_count} governance file(s) ({location})")
    print("")

    print("=== Done ===")
    print("")
    print("Next steps:")
    if do_install_skills:
        print("  - Restart your agent to pick up new skills")
    if do_inject_rules:
        if project_dir:
            print("  - Review governance sections in the generated project governance file")
        else:
            print("  - Review the user-level governance file for your platform")
    if project_dir is not None and "zcode" in platforms:
        zcode_project_note = get_skill_skip_reason("zcode", project_dir)
        if zcode_project_note is not None:
            print(f"  - {zcode_project_note}")
    print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
