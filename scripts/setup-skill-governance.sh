#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

MULTI_AGENT_SNIPPET="$REPO_ROOT/templates/AGENTS-multi-agent-rules.md"
SKILL_LIFECYCLE_SNIPPET="$REPO_ROOT/templates/AGENTS-skill-lifecycle-rules.md"

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

get_skill_target_dir() {
  local skill_name="$1"
  local platform="$2"
  case "$platform" in
    codex)
      echo "${CODEX_HOME:-$HOME/.codex}/skills/$skill_name"
      ;;
    cursor|cursor-cli)
      echo "$HOME/.cursor/skills/$skill_name"
      ;;
    claude-code)
      # Claude Code skills are installed to the Codex/OpenSkills universal path.
      # Claude Code discovers skills via CLAUDE.md project rules; the universal
      # skill directory is shared with the OpenSkills ecosystem.
      echo "${CODEX_HOME:-$HOME/.codex}/skills/$skill_name"
      ;;
    *)
      echo ""
      ;;
  esac
}

install_skill() {
  local skill_name="$1"
  local source_dir="$REPO_ROOT/skills/$skill_name"
  local platform="$2"
  local target_dir
  target_dir="$(get_skill_target_dir "$skill_name" "$platform")"

  if [ -z "$target_dir" ]; then
    echo "  SKIP: unknown platform '$platform'"
    return 1
  fi

  if [ -d "$target_dir" ]; then
    if [ "${FORCE:-}" = "1" ]; then
      echo "  OVERWRITE: $target_dir"
      rm -rf "$target_dir"
    else
      echo "  EXISTS: $target_dir (use --force to overwrite)"
      return 1
    fi
  fi

  mkdir -p "$target_dir"
  cp -r "$source_dir"/* "$target_dir"/
  echo "  INSTALLED: $target_dir"
  return 0
}

check_skill() {
  local skill_name="$1"
  local platform="$2"
  local source="$REPO_ROOT/skills/$skill_name/SKILL.md"
  local target_dir
  target_dir="$(get_skill_target_dir "$skill_name" "$platform")"

  if [ -z "$target_dir" ]; then
    echo "  SKIP CHECK: unknown platform '$platform'"
    return 1
  fi
  if [ ! -f "$source" ]; then
    echo "  MISSING SOURCE: $source"
    return 1
  fi
  if [ ! -d "$target_dir" ] || [ ! -f "$target_dir/SKILL.md" ]; then
    echo "  NOT INSTALLED: $skill_name -> $target_dir"
    return 1
  fi
  if cmp -s "$source" "$target_dir/SKILL.md"; then
    echo "  OK: $skill_name ($platform)"
    return 0
  fi
  echo "  MISMATCH: $skill_name ($platform)"
  return 1
}

warn_phase_contract_if_missing() {
  local platform="$1"
  local skill_being_installed="$2"
  local tdir
  tdir="$(get_skill_target_dir "phase-contract-tools" "$platform")"
  if [ -n "$tdir" ] && [ ! -d "$tdir" ]; then
    echo "  WARNING: $skill_being_installed expects phase-contract-tools at $tdir (missing); continuing."
  fi
}

section_exists() {
  local file="$1"
  local heading="$2"
  grep -qFx "$heading" "$file"
}

extract_escalation_snippet() {
  awk '
    /^## Skill Escalation$/ { e = 1 }
    e {
      if ($0 == "## Skill Lifecycle") exit
      print
    }
  ' "$SKILL_LIFECYCLE_SNIPPET"
}

extract_lifecycle_snippet() {
  awk '
    /^## Skill Lifecycle$/ { l = 1 }
    l { print }
  ' "$SKILL_LIFECYCLE_SNIPPET"
}

replace_h2_section_from_file() {
  local file="$1"
  local heading="$2"
  local snippet_file="$3"
  local tmp
  tmp="$(mktemp)"
  awk -v h="$heading" -v snip="$snippet_file" '
    BEGIN {
      while ((getline line < snip) > 0) {
        new = new line "\n"
      }
      close(snip)
    }
    $0 == h {
      printf "%s", new
      skip = 1
      next
    }
    skip && /^## / {
      skip = 0
      print
      next
    }
    skip {
      next
    }
    { print }
  ' "$file" > "$tmp"
  mv "$tmp" "$file"
}

append_file_contents() {
  local target_file="$1"
  local snippet_file="$2"
  {
    echo ""
    cat "$snippet_file"
  } >>"$target_file"
}

insert_multi_agent_after_title_or_start() {
  local target_file="$1"
  local snippet_file="$2"
  local tmp
  tmp="$(mktemp)"
  awk -v snip="$snippet_file" '
    BEGIN {
      while ((getline line < snip) > 0) {
        m = m line "\n"
      }
      close(snip)
    }
    NR == 1 && $0 ~ /^# [^#]/ {
      print
      print ""
      printf "%s", m
      next
    }
    NR == 1 {
      printf "%s", m
      print
      next
    }
    { print }
  ' "$target_file" >"$tmp"
  mv "$tmp" "$target_file"
}

insert_escalation_before_lifecycle_heading() {
  local file="$1"
  local esc_tmp="$2"
  local tmp
  tmp="$(mktemp)"
  awk -v escfile="$esc_tmp" '
    BEGIN {
      while ((getline x < escfile) > 0) {
        esc = esc x "\n"
      }
      close(escfile)
    }
    $0 == "## Skill Lifecycle" {
      printf "%s", esc
    }
    { print }
  ' "$file" > "$tmp"
  mv "$tmp" "$file"
}

inject_rules_into_file() {
  local target_file="$1"
  local doc_title="$2"
  local esc_tmp
  local life_tmp
  esc_tmp="$(mktemp)"
  life_tmp="$(mktemp)"
  extract_escalation_snippet >"$esc_tmp"
  extract_lifecycle_snippet >"$life_tmp"

  if [ ! -f "$target_file" ]; then
    echo "  CREATE: $target_file"
    {
      printf '# %s\n\n' "$doc_title"
      cat "$MULTI_AGENT_SNIPPET"
      echo ""
      cat "$SKILL_LIFECYCLE_SNIPPET"
    } >"$target_file"
    rm -f "$esc_tmp" "$life_tmp"
    return 0
  fi

  local changed=0
  local ma="$MULTI_AGENT_SNIPPET"

  if section_exists "$target_file" "## Multi-Agent Rules"; then
    if [ "${UPDATE:-}" = "1" ]; then
      echo "  UPDATE: ## Multi-Agent Rules in $target_file"
      replace_h2_section_from_file "$target_file" "## Multi-Agent Rules" "$ma"
      changed=1
    else
      echo "  EXISTS: $target_file already has ## Multi-Agent Rules (use --update to replace)"
    fi
  else
    echo "  INSERT: ## Multi-Agent Rules (after title or at start) -> $target_file"
    insert_multi_agent_after_title_or_start "$target_file" "$ma"
    changed=1
  fi

  local has_esc has_life
  has_esc=0
  has_life=0
  section_exists "$target_file" "## Skill Escalation" && has_esc=1
  section_exists "$target_file" "## Skill Lifecycle" && has_life=1

  if [ "$has_esc" -eq 0 ] && [ "$has_life" -eq 0 ]; then
    echo "  APPEND: skill escalation + lifecycle -> $target_file"
    append_file_contents "$target_file" "$SKILL_LIFECYCLE_SNIPPET"
    changed=1
  elif [ "$has_esc" -eq 0 ] && [ "$has_life" -eq 1 ]; then
    echo "  INSERT: ## Skill Escalation before ## Skill Lifecycle in $target_file"
    insert_escalation_before_lifecycle_heading "$target_file" "$esc_tmp"
    changed=1
  else
    if [ "$has_esc" -eq 1 ]; then
      if [ "${UPDATE:-}" = "1" ]; then
        echo "  UPDATE: ## Skill Escalation in $target_file"
        replace_h2_section_from_file "$target_file" "## Skill Escalation" "$esc_tmp"
        changed=1
      else
        echo "  EXISTS: $target_file already has ## Skill Escalation (use --update to replace)"
      fi
    fi
    if [ "$has_life" -eq 0 ]; then
      echo "  APPEND: ## Skill Lifecycle -> $target_file"
      append_file_contents "$target_file" "$life_tmp"
      changed=1
    else
      if [ "${UPDATE:-}" = "1" ]; then
        echo "  UPDATE: ## Skill Lifecycle in $target_file"
        replace_h2_section_from_file "$target_file" "## Skill Lifecycle" "$life_tmp"
        changed=1
      else
        echo "  EXISTS: $target_file already has ## Skill Lifecycle (use --update to replace)"
      fi
    fi
  fi

  rm -f "$esc_tmp" "$life_tmp"
  if [ "$changed" -eq 1 ]; then
    return 0
  fi
  return 1
}

inject_agents_md() {
  local project_dir="$1"
  inject_rules_into_file "$project_dir/AGENTS.md" "AGENTS.md"
}

inject_claude_md() {
  local project_dir="$1"
  inject_rules_into_file "$project_dir/CLAUDE.md" "CLAUDE.md"
}

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install the full skill governance suite (all execution, orchestration, and
optionally phase skills) with AGENTS.md/CLAUDE.md rule injection.

For multi-agent governance only, use setup-multi-agent-governance.sh instead.

OPTIONS:
  --skills-only       Install skills only (no AGENTS.md/CLAUDE.md changes)
  --rules-only DIR    Inject governance rules into AGENTS.md/CLAUDE.md in DIR
  --project DIR       Install skills AND inject rules into DIR
  --include-phase     Also install phase-contract-tools, phase-plan, phase-execute
  --platform NAME     Force platform: codex, cursor, cursor-cli, claude-code (auto-detected by default)
  --force             Overwrite existing skill installations
  --check             Verify installed skills (SKILL.md matches source)
  --update            Replace existing rule sections instead of skipping
  --help              Show this help

EXAMPLES:
  ./scripts/setup-skill-governance.sh --skills-only

  ./scripts/setup-skill-governance.sh --project /path/to/my-repo

  ./scripts/setup-skill-governance.sh --skills-only --include-phase --force

  ./scripts/setup-skill-governance.sh --rules-only /path/to/my-repo --update

  ./scripts/setup-skill-governance.sh --check --include-phase
EOF
}

SKILLS=(
  "scoped-tasking"
  "plan-before-action"
  "minimal-change-strategy"
  "targeted-validation"
  "context-budget-awareness"
  "read-and-locate"
  "safe-refactor"
  "bugfix-workflow"
  "multi-agent-protocol"
  "conflict-resolution"
)

PHASE_SKILLS=(
  "phase-contract-tools"
  "phase-plan"
  "phase-execute"
)

MODE=""
PROJECT_DIR=""
PLATFORM=""
FORCE="0"
INCLUDE_PHASE="0"
CHECK="0"
UPDATE="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skills-only)  MODE="skills"; shift ;;
    --rules-only)   MODE="rules"; PROJECT_DIR="$2"; shift 2 ;;
    --project)      MODE="all"; PROJECT_DIR="$2"; shift 2 ;;
    --include-phase) INCLUDE_PHASE="1"; shift ;;
    --platform)     PLATFORM="$2"; shift 2 ;;
    --force)        FORCE="1"; shift ;;
    --check)        CHECK="1"; shift ;;
    --update)       UPDATE="1"; shift ;;
    --help|-h)      usage; exit 0 ;;
    *)              echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

if [ "$CHECK" = "1" ]; then
  :
elif [ -z "$MODE" ]; then
  echo "No mode specified. Use --help for usage."
  exit 1
fi

echo ""
echo "=== Skill Governance Setup ==="
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

run_skill_checks() {
  local failed=0
  local p s
  echo "--- Verifying skills ---"
  for p in "${PLATFORMS[@]}"; do
    echo "Platform: $p"
    for s in "${SKILLS[@]}"; do
      check_skill "$s" "$p" || failed=$((failed + 1))
    done
    if [ "$INCLUDE_PHASE" = "1" ]; then
      for s in "${PHASE_SKILLS[@]}"; do
        check_skill "$s" "$p" || failed=$((failed + 1))
      done
    fi
    echo ""
  done
  if [ "$failed" -gt 0 ]; then
    echo "Check failed: $failed issue(s)."
    return 1
  fi
  echo "All checked skills match source."
  return 0
}

if [ "$CHECK" = "1" ]; then
  run_skill_checks
  exit $?
fi

exec_count=0
phase_count=0

if [ "$MODE" = "skills" ] || [ "$MODE" = "all" ]; then
  echo "--- Installing skills ---"
  for platform in "${PLATFORMS[@]}"; do
    echo "Platform: $platform"
    for skill in "${SKILLS[@]}"; do
      if install_skill "$skill" "$platform"; then
        exec_count=$((exec_count + 1))
      fi
    done
    if [ "$INCLUDE_PHASE" = "1" ]; then
      for skill in "${PHASE_SKILLS[@]}"; do
        case "$skill" in
          phase-plan|phase-execute)
            warn_phase_contract_if_missing "$platform" "$skill"
            ;;
        esac
        if install_skill "$skill" "$platform"; then
          phase_count=$((phase_count + 1))
        fi
      done
    fi
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
        inject_agents_md "$PROJECT_DIR" || true
        ;;
      claude-code)
        inject_claude_md "$PROJECT_DIR" || true
        ;;
    esac
  done
  echo ""
fi

echo "=== Summary ==="
if [ "$MODE" = "skills" ] || [ "$MODE" = "all" ]; then
  echo "Installed $exec_count execution/orchestration skill(s)"
  if [ "$INCLUDE_PHASE" = "1" ]; then
    echo "Installed $phase_count phase skill(s)"
  fi
fi
if [ "$MODE" = "rules" ] || [ "$MODE" = "all" ]; then
  echo "Injected rules into AGENTS.md/CLAUDE.md"
fi
echo ""

echo "=== Done ==="
echo ""
echo "Next steps:"
if [ "$MODE" = "skills" ] || [ "$MODE" = "all" ]; then
  echo "  - Restart your agent (Cursor/Codex/Claude Code) to pick up new skills"
fi
if [ "$MODE" = "rules" ] || [ "$MODE" = "all" ]; then
  echo "  - Review governance sections in AGENTS.md/CLAUDE.md"
fi
echo ""
