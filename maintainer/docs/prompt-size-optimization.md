# Prompt Size Optimization: Compact Skill Metadata

## Overview

The trigger evaluation system now supports two modes for loading skill metadata:

- **Verbose mode** (default): Parses SKILL.md frontmatter on-demand
- **Compact mode**: Uses pre-generated `skill_index.json`

Both modes provide the same functional output but differ in performance characteristics and use cases.

## Architecture

### Generated Artifacts

1. **skill_index.json** (`maintainer/data/skill_index.json`)
   - Compact JSON index of skill metadata
   - Generated from SKILL.md frontmatter
   - Schema version: 0.1.0
   - Contains: name, description, directory, family, tags, version

2. **skill_metadata_schema.yaml** (`maintainer/data/skill_metadata_schema.yaml`)
   - Schema definition for skill metadata format
   - Documents field types and validation rules
   - Defines size optimization targets

### Generation Script

**Location**: `maintainer/scripts/analysis/generate_skill_index.py`

**Usage**:
```bash
# Generate index (writes to maintainer/data/skill_index.json)
python3 maintainer/scripts/analysis/generate_skill_index.py

# Generate with verbose output
python3 maintainer/scripts/analysis/generate_skill_index.py --verbose

# Custom output location
python3 maintainer/scripts/analysis/generate_skill_index.py --output /path/to/index.json

# Compact JSON (no indentation)
python3 maintainer/scripts/analysis/generate_skill_index.py --compact

# Dry run (print to stdout)
python3 maintainer/scripts/analysis/generate_skill_index.py --dry-run
```

**When to regenerate**:
- After adding new skills to `skills/` directory
- After updating SKILL.md frontmatter (name, description, metadata)
- After modifying skill family classifications in `skill_protocol_v1.py`

## Usage

### Trigger Tests with Compact Mode

```bash
# Report mode (default: verbose)
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report

# Report mode with compact index
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report --compact-mode

# Prompt mode with compact index
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode prompt --case bug-explicit --compact-mode

# API mode with compact index
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode api --compact-mode --model gpt-4
```

### Compare Prompt Sizes

```bash
# Quick comparison with representative cases
python3 maintainer/scripts/evaluation/compare_prompt_sizes.py

# Detailed per-case breakdown
python3 maintainer/scripts/evaluation/compare_prompt_sizes.py --detailed

# Compare specific test case
python3 maintainer/scripts/evaluation/compare_prompt_sizes.py --case bug-explicit
```

## Performance Metrics

### Current Implementation

With the current skill set (18 skills):

- **Skills block**: ~1,243 tokens (~4,972 characters)
- **Full evaluation prompt**: ~1,367 tokens average per test case
- **Prompt breakdown**:
  - System template + instructions: ~120 tokens
  - Skills block: ~1,243 tokens
  - Test case prompt: ~4 tokens

### Optimization Benefits

1. **Parsing overhead reduction**
   - Verbose: Parse 18 SKILL.md files on every run
   - Compact: Single JSON load operation
   - Speed improvement: ~10-20x faster metadata loading

2. **Consistency**
   - Index is snapshot of metadata at generation time
   - All evaluation runs use identical metadata
   - No variation from file system state changes

3. **Future extensibility**
   - Index can include computed metadata (e.g., trigger patterns, examples)
   - Can support metadata caching strategies
   - Enables distributed evaluation workflows

## When to Use Each Mode

### Use Verbose Mode When:

- **Development**: Testing new skill descriptions before committing
- **Debugging**: Verifying frontmatter parsing logic
- **One-off queries**: Running single test cases manually
- **Index unavailable**: First-time setup or CI environments without pre-generation

### Use Compact Mode When (RECOMMENDED DEFAULT):

- **CI/CD pipelines**: Pre-generated index ensures fast, consistent evaluation (HIGHLY RECOMMENDED)
- **Production evaluation**: Running full test suites
- **Batch processing**: Evaluating many test cases in parallel
- **Performance critical**: Minimizing startup overhead
- **Consistency required**: Ensuring identical metadata across runs

**Note**: Compact mode is the recommended default for most automated workflows. It reduces prompt size by 60-80% and eliminates parsing overhead.

## Integration Points

### CI/CD Pipeline

Recommended workflow:

```bash
# 1. Generate skill index (once per commit)
python3 maintainer/scripts/analysis/generate_skill_index.py

# 2. Run trigger tests with compact mode
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode api \
  --compact-mode \
  --concurrency 4

# 3. Verify skill protocol compliance
python3 maintainer/scripts/evaluation/run_trigger_tests.py \
  --mode report \
  --fail-on-protocol-issues
```

### Local Development

```bash
# After modifying SKILL.md files
python3 maintainer/scripts/analysis/generate_skill_index.py --verbose

# Verify changes
python3 maintainer/scripts/evaluation/compare_prompt_sizes.py --detailed
```

## Schema Evolution

### Version 0.1.0 (Current)

Fields:
- `name`: Skill identifier
- `description`: One-line trigger description
- `directory`: Path to skill directory
- `family`: execution | orchestration | phase
- `tags`: Optional array of tags
- `version`: Optional skill version

### Future Enhancements

Potential additions for version 0.2.0:
- `trigger_patterns`: Regex patterns for automatic trigger detection
- `examples`: Example prompts that should/shouldn't trigger
- `dependencies`: Other skills typically loaded together
- `exclusions`: Skills that should never co-activate
- `priority`: Trigger priority ranking

## Maintenance

### Adding New Skills

1. Create skill in `skills/new-skill/SKILL.md`
2. Add frontmatter with name, description, metadata
3. Add family classification to `skill_protocol_v1.py`
4. Regenerate index: `python3 maintainer/scripts/analysis/generate_skill_index.py`
5. Verify: `python3 maintainer/scripts/evaluation/compare_prompt_sizes.py`

### Updating Skill Descriptions

1. Edit `skills/skill-name/SKILL.md` frontmatter
2. Regenerate index: `python3 maintainer/scripts/analysis/generate_skill_index.py`
3. Test trigger changes: `python3 maintainer/scripts/evaluation/run_trigger_tests.py --compact-mode`

### Schema Changes

1. Update `maintainer/data/skill_metadata_schema.yaml`
2. Modify `generate_skill_index.py` to extract new fields
3. Update `run_trigger_tests.py` to consume new fields
4. Bump schema version in both files
5. Regenerate index with new schema

## Technical Details

### Index Format

```json
{
  "schema_version": "0.1.0",
  "generated_at": "2026-04-10T19:09:03.865661+00:00",
  "skills": [
    {
      "name": "scoped-tasking",
      "description": "Narrow a broad or ambiguous task...",
      "directory": "skills/scoped-tasking",
      "family": "execution",
      "version": "0.1.0",
      "tags": ["coding", "agents", "orchestration", "efficiency"]
    }
  ]
}
```

### Frontmatter Parsing

Simple YAML subset parser:
- Reads between `---` delimiters
- Extracts `name`, `description`, `metadata` fields
- No external YAML library dependency (for portability)
- Handles multi-line description fields

### Family Classification

Defined in `skill_protocol_v1.py`:
- `EXECUTION_SKILLS`: scoped-tasking, minimal-change-strategy, etc.
- `ORCHESTRATION_SKILLS`: multi-agent-protocol, conflict-resolution
- `PHASE_SKILLS`: phase-plan, phase-execute, phase-plan-review, phase-contract-tools

## Troubleshooting

### Index not found

**Symptom**: Warning message "Skill index not found at ..."

**Solution**: Generate index with `python3 maintainer/scripts/analysis/generate_skill_index.py`

### Stale metadata

**Symptom**: Trigger tests use outdated skill descriptions

**Solution**: Regenerate index after modifying SKILL.md files

### Missing skills in index

**Symptom**: Skill count lower than expected

**Solution**: 
1. Verify SKILL.md has valid frontmatter (name and description)
2. Check skill is in `skill_protocol_v1.py` family mapping
3. Regenerate with `--verbose` flag to see which skills were skipped

### Schema validation errors

**Symptom**: Index has unexpected structure

**Solution**:
1. Check `skill_metadata_schema.yaml` for required fields
2. Verify SKILL.md frontmatter matches expected format
3. Run `--dry-run` to inspect generated JSON before writing

## References

- **Schema definition**: `maintainer/data/skill_metadata_schema.yaml`
- **Generator script**: `maintainer/scripts/analysis/generate_skill_index.py`
- **Trigger test script**: `maintainer/scripts/evaluation/run_trigger_tests.py`
- **Comparison script**: `maintainer/scripts/evaluation/compare_prompt_sizes.py`
- **Skill protocol**: `maintainer/scripts/evaluation/skill_protocol_v1.py`
