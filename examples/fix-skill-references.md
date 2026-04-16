# Fix Skill References in Examples

## Scenario

Example documents in the `examples/` directory may reference skill names that don't exist in the `skills/` directory, or contain typos in skill names. Find and fix these incorrect references systematically.

## Recommended Skill Composition

- `scoped-tasking`
- `read-and-locate`
- `bugfix-workflow`
- `minimal-change-strategy`
- `self-review`
- `targeted-validation`

## Why This Composition

- `scoped-tasking` narrows the problem to skill name references in example documents only—not README.md, not SKILL.md files, not governance templates.
- `read-and-locate` systematically finds all skill references across multiple example files.
- `bugfix-workflow` treats this as a diagnosis problem: gather evidence (actual skills vs. referenced names), identify mismatches, fix only confirmed errors.
- `minimal-change-strategy` prevents "improving" examples beyond fixing broken references—no rewording, no structural changes.
- `self-review` verifies that all fixed references now point to real skills and no new errors were introduced.
- `targeted-validation` confirms all referenced skills actually exist in `skills/`.

## Example Execution

1. **Scope the investigation.**
   - "Find and fix skill name errors in `examples/` directory."
   - In scope: skill names in example files (`*.md` in `examples/`).
   - Out of scope: README.md, SKILL.md files, code comments, governance templates.

2. **Gather the baseline truth.**
   ```bash
   # List all actual skill names
   ls -1 skills/
   ```
   - Record: scoped-tasking, minimal-change-strategy, plan-before-action, etc.

3. **Locate all skill references.**
   - Search `examples/*.md` for skill name patterns:
     - Inline references: `scoped-tasking`, `plan-before-action`
     - Code blocks with skill compositions
     - Headings mentioning skill names
   - Use `grep` or `Grep` tool to find all occurrences

4. **Identify mismatches.**
   - Compare referenced names against actual skill directory names.
   - Flag any reference that doesn't match an existing skill.
   - Examples of potential errors:
     - `scope-task` instead of `scoped-tasking`
     - `plan-first` instead of `plan-before-action`
     - `minimal-changes` instead of `minimal-change-strategy`

5. **Fix only confirmed errors.**
   - If a reference clearly doesn't match any real skill → fix it.
   - If uncertain (could be a different concept) → flag for review, don't modify.
   - Preserve original sentence structure and formatting.
   - Fix only the skill name, not surrounding text.

6. **Self-review the fixes.**
   - Does each fixed skill name now exist in `skills/`?
   - Did any edits introduce typos or formatting errors?
   - Were any unrelated changes accidentally made?
   - Are there any false positives in the fix list?

7. **Validate the result.**
   ```bash
   # Re-scan for all skill references
   grep -r "scoped-tasking\|minimal-change-strategy\|plan-before-action" examples/
   
   # Verify each referenced skill exists
   for skill in $(grep -oh "[a-z-]*-[a-z-]*" examples/*.md | sort -u); do
       [ -d "skills/$skill" ] || echo "Still broken: $skill"
   done
   ```

8. **Report findings.**
   - If no errors found: "All skill references are valid."
   - If errors found and fixed: "Fixed N references in M files."
   - If uncertain cases found: "Found N potential issues requiring human review."

## Expected Behavior

- Agent systematically lists all actual skills first.
- Agent searches all example files for skill references.
- Agent identifies specific mismatches with line numbers.
- Agent fixes only confirmed errors, preserving context.
- Agent reports findings clearly, including "no errors found" if applicable.
- Agent doesn't force changes if no errors exist.

## Common Anti-Patterns to Avoid

- ❌ Making changes when no errors are found.
- ❌ "Improving" example text beyond fixing the broken reference.
- ❌ Renaming skills that are referenced correctly.
- ❌ Fixing references in files outside `examples/` without being asked.
- ❌ Changing formatting, sentence structure, or wording unrelated to the skill name.
- ❌ Creating false positives by misidentifying non-skill words as skill names.
- ❌ Skipping the validation step.

## Acceptance Criteria

- [ ] All actual skill names identified from `skills/` directory
- [ ] All example files scanned for skill references
- [ ] Specific mismatches identified with file paths and line numbers
- [ ] Only confirmed errors fixed (or none, if no errors exist)
- [ ] All fixed references now point to real skills
- [ ] No unrelated changes in example files
- [ ] Clear report of what was found and fixed
- [ ] Validation confirms all references are now correct

## Special Case: No Errors Found

If the investigation finds that all skill references are already correct:

- ✅ Report: "Scanned N files, all skill references are valid."
- ✅ Provide evidence: list of files checked, skills referenced.
- ❌ Do not make changes to "improve" documentation.
- ❌ Do not create work where none exists.

This scenario tests whether the agent can complete a bugfix workflow that concludes with "no bug found" rather than forcing an unnecessary fix.
