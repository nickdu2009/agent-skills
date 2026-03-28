#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# --- Detect platform ---
detect_platforms() {
  local platforms=()
  if command -v agent &>/dev/null; then
    platforms+=("cursor-cli")
  fi
  if [ -d "$HOME/.cursor" ]; then
    platforms+=("cursor")
  fi
  if [ -d "$HOME/.codex" ] || command -v codex &>/dev/null; then
    platforms+=("codex")
  fi
  if command -v claude &>/dev/null; then
    platforms+=("claude-code")
  fi
  echo "${platforms[@]}"
}

# --- Skill installation ---
install_skill() {
  local skill_name="$1"
  local source_dir="$REPO_ROOT/skills/$skill_name"
  local target_dir=""
  local platform="$2"

  case "$platform" in
    codex)
      target_dir="${CODEX_HOME:-$HOME/.codex}/skills/$skill_name"
      ;;
    cursor|cursor-cli)
      target_dir="$HOME/.cursor/skills/$skill_name"
      ;;
    claude-code)
      # Claude Code skills are installed to the Codex/OpenSkills universal path.
      # Claude Code discovers skills via CLAUDE.md project rules; the universal
      # skill directory is shared with the OpenSkills ecosystem.
      target_dir="${CODEX_HOME:-$HOME/.codex}/skills/$skill_name"
      ;;
  esac

  if [ -z "$target_dir" ]; then
    echo "  SKIP: unknown platform '$platform'"
    return
  fi

  if [ -d "$target_dir" ]; then
    if [ "${FORCE:-}" = "1" ]; then
      echo "  OVERWRITE: $target_dir"
      rm -rf "$target_dir"
    else
      echo "  EXISTS: $target_dir (use --force to overwrite)"
      return
    fi
  fi

  mkdir -p "$target_dir"
  cp -r "$source_dir"/* "$target_dir"/
  echo "  INSTALLED: $target_dir"
}

check_skill() {
  local skill_name="$1"
  local source_dir="$REPO_ROOT/skills/$skill_name"
  local target_dir=""
  local platform="$2"

  case "$platform" in
    codex)
      target_dir="${CODEX_HOME:-$HOME/.codex}/skills/$skill_name"
      ;;
    cursor|cursor-cli)
      target_dir="$HOME/.cursor/skills/$skill_name"
      ;;
    claude-code)
      target_dir="${CODEX_HOME:-$HOME/.codex}/skills/$skill_name"
      ;;
  esac

  if [ -z "$target_dir" ]; then
    echo "  SKIP: unknown platform '$platform'"
    return 0
  fi

  if [ ! -d "$target_dir" ]; then
    echo "MISSING: $target_dir"
    return 1
  fi

  if ! diff -q "$source_dir/SKILL.md" "$target_dir/SKILL.md" &>/dev/null; then
    echo "OUTDATED: $target_dir"
    return 1
  fi

  echo "OK: $skill_name"
  return 0
}

# --- AGENTS.md injection ---
_multi_agent_rules_section_end() {
  local file="$1"
  local start="$2"
  awk -v s="$start" '
    NR < s { next }
    NR == s { next }
    NR > s && /^## / { print NR - 1; done = 1; exit }
    { end = NR }
    END {
      if (done) exit
      if (s) {
        if (length(end) == 0) print s
        else print end
      }
    }
  ' "$file"
}

inject_agents_md() {
  local project_dir="$1"
  local agents_file="$project_dir/AGENTS.md"
  local snippet="$REPO_ROOT/templates/governance/AGENTS-multi-agent-rules.md"

  if [ ! -f "$agents_file" ]; then
    echo "  CREATE: $agents_file (new file with Multi-Agent Rules)"
    printf "# AGENTS.md\n\n" > "$agents_file"
    cat "$snippet" >> "$agents_file"
    return
  fi

  if grep -q "## Multi-Agent Rules" "$agents_file"; then
    if [ "$UPDATE" = "1" ]; then
      local start end
      start=$(sed -n '/## Multi-Agent Rules/=' "$agents_file" | head -1)
      end=$(_multi_agent_rules_section_end "$agents_file" "$start")
      {
        head -n $((start - 1)) "$agents_file"
        cat "$snippet"
        tail -n +$((end + 1)) "$agents_file"
      } > "${agents_file}.tmp"
      mv "${agents_file}.tmp" "$agents_file"
      echo "  UPDATED: Multi-Agent Rules section in $agents_file"
      return
    fi
    echo "  EXISTS: $agents_file already has Multi-Agent Rules section"
    echo "  To replace, remove the existing section and re-run, or use --update."
    return
  fi

  echo "" >> "$agents_file"
  cat "$snippet" >> "$agents_file"
  echo "  APPENDED: Multi-Agent Rules section to $agents_file"
}

# --- CLAUDE.md injection ---
inject_claude_md() {
  local project_dir="$1"
  local claude_file="$project_dir/CLAUDE.md"
  local snippet="$REPO_ROOT/templates/governance/AGENTS-multi-agent-rules.md"

  if [ ! -f "$claude_file" ]; then
    echo "  CREATE: $claude_file (new file with Multi-Agent Rules)"
    printf "# CLAUDE.md\n\n" > "$claude_file"
    cat "$snippet" >> "$claude_file"
    return
  fi

  if grep -q "## Multi-Agent Rules" "$claude_file"; then
    if [ "$UPDATE" = "1" ]; then
      local start end
      start=$(sed -n '/## Multi-Agent Rules/=' "$claude_file" | head -1)
      end=$(_multi_agent_rules_section_end "$claude_file" "$start")
      {
        head -n $((start - 1)) "$claude_file"
        cat "$snippet"
        tail -n +$((end + 1)) "$claude_file"
      } > "${claude_file}.tmp"
      mv "${claude_file}.tmp" "$claude_file"
      echo "  UPDATED: Multi-Agent Rules section in $claude_file"
      return
    fi
    echo "  EXISTS: $claude_file already has Multi-Agent Rules section"
    echo "  To replace, use --update."
    return
  fi

  echo "" >> "$claude_file"
  cat "$snippet" >> "$claude_file"
  echo "  APPENDED: Multi-Agent Rules section to $claude_file"
}

# --- Main ---
usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install multi-agent governance skills and inject AGENTS.md/CLAUDE.md rules.

OPTIONS:
  --skills-only       Install governance skills only (no AGENTS.md changes)
  --rules-only DIR    Inject Multi-Agent Rules into AGENTS.md/CLAUDE.md in DIR
  --project DIR       Install skills AND inject rules into DIR
  --check             Verify installed skills match repo (no changes)
  --update            Replace existing Multi-Agent Rules section when injecting rules
  --platform NAME     Force platform: codex, cursor, claude-code (auto-detected by default)
  --force             Overwrite existing skill installations
  --help              Show this help

EXAMPLES:
  # Auto-detect platform, install skills only
  ./maintainer/scripts/install/setup-multi-agent-governance.sh --skills-only

  # Install everything for a specific project
  ./maintainer/scripts/install/setup-multi-agent-governance.sh --project /path/to/my-repo

  # Inject rules into an existing AGENTS.md
  ./maintainer/scripts/install/setup-multi-agent-governance.sh --rules-only /path/to/my-repo

  # Force overwrite existing skills
  ./maintainer/scripts/install/setup-multi-agent-governance.sh --skills-only --force

  # Check skill installs without modifying anything
  ./maintainer/scripts/install/setup-multi-agent-governance.sh --check

  # Refresh Multi-Agent Rules in place
  ./maintainer/scripts/install/setup-multi-agent-governance.sh --rules-only /path/to/my-repo --update
EOF
}

SKILLS=(
  "multi-agent-protocol"
  "conflict-resolution"
)

MODE=""
PROJECT_DIR=""
PLATFORM=""
FORCE="0"
UPDATE="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skills-only)  MODE="skills"; shift ;;
    --rules-only)   MODE="rules"; PROJECT_DIR="$2"; shift 2 ;;
    --project)      MODE="all"; PROJECT_DIR="$2"; shift 2 ;;
    --check)        MODE="check"; shift ;;
    --update)       UPDATE="1"; shift ;;
    --platform)     PLATFORM="$2"; shift 2 ;;
    --force)        FORCE="1"; shift ;;
    --help|-h)      usage; exit 0 ;;
    *)              echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

if [ -z "$MODE" ]; then
  echo "No mode specified. Use --help for usage."
  exit 1
fi

echo ""
echo "=== Multi-Agent Governance Setup ==="
echo ""

if [ -n "$PLATFORM" ]; then
  PLATFORMS=("$PLATFORM")
else
  read -ra PLATFORMS <<< "$(detect_platforms)"
fi

if [ ${#PLATFORMS[@]} -eq 0 ]; then
  echo "No supported platform detected. Install Cursor, Codex, or Claude Code first."
  exit 1
fi

echo "Detected platforms: ${PLATFORMS[*]}"
echo ""

CHECK_EXIT=0

if [ "$MODE" = "check" ]; then
  echo "--- Checking skills ---"
  for platform in "${PLATFORMS[@]}"; do
    echo "Platform: $platform"
    for skill in "${SKILLS[@]}"; do
      check_skill "$skill" "$platform" || CHECK_EXIT=1
    done
    echo ""
  done
  echo "=== Done ==="
  echo ""
  exit "$CHECK_EXIT"
fi

if [ "$MODE" = "skills" ] || [ "$MODE" = "all" ]; then
  echo "--- Installing skills ---"
  for platform in "${PLATFORMS[@]}"; do
    echo "Platform: $platform"
    for skill in "${SKILLS[@]}"; do
      install_skill "$skill" "$platform"
    done
    echo ""
  done
fi

if [ "$MODE" = "rules" ] || [ "$MODE" = "all" ]; then
  if [ -z "$PROJECT_DIR" ]; then
    echo "ERROR: --project or --rules-only requires a directory"
    exit 1
  fi

  if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: $PROJECT_DIR is not a directory"
    exit 1
  fi

  echo "--- Injecting rules into $PROJECT_DIR ---"

  for platform in "${PLATFORMS[@]}"; do
    case "$platform" in
      codex|cursor|cursor-cli)
        inject_agents_md "$PROJECT_DIR"
        ;;
      claude-code)
        inject_claude_md "$PROJECT_DIR"
        ;;
    esac
  done
  echo ""
fi

echo "=== Done ==="
echo ""
echo "Next steps:"
if [ "$MODE" = "skills" ] || [ "$MODE" = "all" ]; then
  echo "  - Restart your agent (Cursor/Codex/Claude Code) to pick up new skills"
fi
if [ "$MODE" = "rules" ] || [ "$MODE" = "all" ]; then
  echo "  - Review the Multi-Agent Rules section in your AGENTS.md/CLAUDE.md"
fi
echo ""
