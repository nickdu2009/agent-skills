# Skill Definition Validator

## Scenario

Create a validation tool to ensure all skills in the repository have complete and properly structured `SKILL.md` files. The tool should check for required sections and provide actionable feedback.

## Recommended Skill Composition

- `scoped-tasking`
- `plan-before-action`
- `minimal-change-strategy`
- `self-review`
- `targeted-validation`

## Why This Composition

- `scoped-tasking` keeps the scope limited to a single validation script, not a full linting framework.
- `plan-before-action` forces the agent to declare the script structure, validation logic, and output format before writing code.
- `minimal-change-strategy` prevents over-engineering—no external dependencies, no complex abstractions for a straightforward checker.
- `self-review` catches edge cases like missing error handling for non-existent directories.
- `targeted-validation` runs the script on the actual `skills/` directory to verify it works.

## Example Execution

1. **Scope the boundary clearly.**
   - "Create a Python script that validates SKILL.md completeness."
   - In scope: checking for required sections (Purpose, When to Use, Input, Output).
   - Out of scope: content quality checks, grammar validation, cross-reference validation.

2. **Plan before writing code.**
   - Script location: `scripts/validate-skill-definition.py`
   - Required sections to check: `## Purpose`, `## When to Use`, `## Input`, `## Output`
   - Command-line interface: `--skill <name>`, `--all`, `--verbose`
   - Output format: colored checkmarks/crosses, summary statistics
   - Error handling: missing skills/ directory, invalid skill names

3. **Keep implementation minimal.**
   - Use only Python standard library (no external dependencies)
   - Single file, ~100 lines
   - Simple regex or string matching for section detection
   - Basic CLI argument parsing with argparse

4. **Self-review for common pitfalls.**
   - Does it handle missing `skills/` directory gracefully?
   - Does it skip non-directory entries in `skills/`?
   - Are file read errors handled?
   - Is the output format consistent?

5. **Validate on real data.**
   ```bash
   # Test on all skills
   python3 scripts/validate-skill-definition.py --all
   
   # Test on a single skill
   python3 scripts/validate-skill-definition.py --skill scoped-tasking
   
   # Verbose mode
   python3 scripts/validate-skill-definition.py --all --verbose
   ```

## Expected Behavior

- Agent declares scope before exploring the codebase.
- Agent provides a clear plan with script structure before writing code.
- Implementation is simple and avoids over-engineering.
- The script works on first run without requiring iterations.
- Exit code is 0 for success, 1 for validation failures.

## Common Anti-Patterns to Avoid

- ❌ Adding features beyond basic section validation (markdown linting, spell-check).
- ❌ Introducing dependencies like `markdown`, `pyyaml` when stdlib is sufficient.
- ❌ Creating a complex plugin architecture for extensibility.
- ❌ Over-abstracting with classes when simple functions suffice.
- ❌ Skipping error handling for missing files or directories.

## Acceptance Criteria

- [ ] Script exists at `scripts/validate-skill-definition.py`
- [ ] Checks for all four required sections
- [ ] Supports `--skill`, `--all`, and `--verbose` flags
- [ ] Provides clear, colored output (✓/✗)
- [ ] Shows summary statistics
- [ ] Uses only Python standard library
- [ ] Handles errors gracefully
- [ ] Returns correct exit codes
- [ ] Runs successfully on current repository
