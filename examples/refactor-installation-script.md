# Refactor Installation Script

## Scenario

The `maintainer/scripts/install/manage-governance.py` script may contain repeated path handling or file copying logic. Refactor the duplicated code into reusable functions while keeping all external behavior identical.

## Recommended Skill Composition

- `scoped-tasking`
- `read-and-locate`
- `safe-refactor`
- `minimal-change-strategy`
- `self-review`
- `targeted-validation`

## Why This Composition

- `scoped-tasking` ensures the refactoring stays within one file and doesn't expand to "improve" unrelated code.
- `read-and-locate` identifies repeated patterns in path resolution, file copying, or directory detection.
- `safe-refactor` guides structural changes while keeping all interfaces and behavior unchanged.
- `minimal-change-strategy` prevents "while we're here" improvements—no new features, no renamed variables unrelated to the refactoring goal.
- `self-review` verifies that command-line arguments, output, and side effects remain identical.
- `targeted-validation` runs existing install scenarios to confirm behavior preservation.

## Example Execution

1. **Scope the refactoring boundary.**
   - "Refactor `manage-governance.py` to extract repeated path or file-copy logic."
   - In scope: extracting reusable functions from repeated code.
   - Out of scope: adding features, changing argument parsing, renaming unrelated code, updating dependencies.

2. **Locate repeated patterns.**
   - Read the script and identify:
     - Duplicate path construction logic (e.g., `.cursor/skills/`, `.claude/skills/`)
     - Repeated file copy operations
     - Similar directory existence checks
     - Redundant platform detection logic

3. **Plan the refactoring.**
   - Extract functions with clear names (e.g., `copy_skill_tree()`, `resolve_platform_path()`)
   - Identify at least 2 reusable patterns
   - Ensure extracted functions have single responsibilities
   - Keep all original command-line behavior unchanged

4. **Apply safe refactoring guardrails.**
   - Do not change function signatures or module-level behavior.
   - Do not rename variables unrelated to extracted functions.
   - Do not add type hints, docstrings, or comments to untouched code.
   - Do not "improve" error messages or logging.
   - Preserve exact output format.

5. **Self-review for behavior changes.**
   - Compare: does `--project /path` still work identically?
   - Compare: does `--sync-local cursor` still produce the same tree?
   - Compare: does `--check-local claude` still output the same messages?
   - Check: are all exit codes unchanged?

6. **Validate with real scenarios.**
   ```bash
   # Test local mirror sync
   python3 maintainer/scripts/install/manage-governance.py --check-local cursor
   
   # Test skill-only install
   python3 maintainer/scripts/install/manage-governance.py --project /tmp/test-repo --skills-only --dry-run
   ```

## Expected Behavior

- Agent reads the script before proposing changes.
- Agent identifies specific repeated code patterns (with line numbers).
- Agent provides a refactoring plan before editing.
- Extracted functions have clear, single responsibilities.
- No behavior changes—all command-line scenarios work identically.
- Code line count decreases or stays the same.

## Common Anti-Patterns to Avoid

- ❌ Changing command-line argument names or formats.
- ❌ Adding new features or "enhancements" during refactoring.
- ❌ Renaming variables unrelated to the extracted logic.
- ❌ Adding type hints, docstrings, or linting fixes to untouched code.
- ❌ Changing error message formatting or logging output.
- ❌ Creating abstractions for patterns that appear only once.
- ❌ Refactoring without first reading the entire script.

## Acceptance Criteria

- [ ] At least 2 repeated patterns identified and extracted
- [ ] Extracted functions have clear, descriptive names
- [ ] All original command-line arguments work identically
- [ ] All original output messages unchanged
- [ ] All original error handling preserved
- [ ] Exit codes remain the same for all scenarios
- [ ] Code complexity reduced (fewer duplicated lines)
- [ ] No new dependencies introduced
- [ ] Script passes existing validation scenarios
