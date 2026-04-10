# Token Efficiency Monitoring Guide

This guide explains how to use the token efficiency monitoring system to track and maintain optimization gains.

## Overview

The token efficiency monitoring system provides:

- **Quarterly audits**: Comprehensive reports comparing to baseline
- **Real-time dashboard**: Color-coded health indicators for quick status
- **Regression detection**: Automated detection of quality and token inflation
- **CI integration**: Automated checks on every PR and weekly scheduled runs

## Quick Start

### Check Current Status

```bash
# Terminal dashboard with color-coded status
python3 maintainer/scripts/audit/token_efficiency_dashboard.py

# Markdown report
python3 maintainer/scripts/audit/token_efficiency_dashboard.py --markdown

# JSON data for scripting
python3 maintainer/scripts/audit/token_efficiency_dashboard.py --json
```

### Run Quarterly Audit

```bash
# Run full audit for current quarter
python3 maintainer/scripts/audit/run_quarterly_audit.py

# Specify output file
python3 maintainer/scripts/audit/run_quarterly_audit.py --output 2026-Q2-audit-report.md

# Get JSON data
python3 maintainer/scripts/audit/run_quarterly_audit.py --json
```

### Detect Regressions

```bash
# Compare to latest audit
python3 maintainer/scripts/audit/detect_regressions.py

# Compare to specific baseline
python3 maintainer/scripts/audit/detect_regressions.py --baseline 2026-Q1-audit-report.md

# JSON output
python3 maintainer/scripts/audit/detect_regressions.py --json
```

## Dashboard Interpretation

### Color-Coded Health Indicators

- **🟢 Green (PASS)**: All metrics within target ranges
- **🟡 Yellow (WARN)**: Minor deviations, attention recommended
- **🔴 Red (FAIL)**: Critical issues requiring immediate action

### Component Status

#### Quality Metrics

- **Green**: 100% of skills pass all quality checks
- **Yellow**: 90-99% pass rate
- **Red**: <90% pass rate

**Action when yellow/red**: Review failing skills in quality check output and fix issues.

#### Token Metrics

- **Green**: At or below baseline
- **Yellow**: 1-5% increase from baseline
- **Red**: >5% increase from baseline

**Action when yellow/red**: Review recent changes for unnecessary verbosity, apply templates.

#### Cross-Reference Integrity

- **Green**: 0 broken references
- **Yellow**: 1-3 broken references
- **Red**: 4+ broken references

**Action when yellow/red**: Fix broken references immediately.

## Quarterly Audit Workflow

### 1. Run Audit

```bash
# At start of quarter (e.g., Q2 2026)
python3 maintainer/scripts/audit/run_quarterly_audit.py --output 2026-Q2-audit-report.md
```

### 2. Review Report

The audit report includes:

- **Executive Summary**: Overall status and key findings
- **Metrics Detail**: Quality, tokens, cross-references compared to baseline
- **Regressions**: Any detected issues with severity
- **Recommendations**: Actionable next steps

### 3. Address Issues

Priority order:

1. **Critical regressions** (red): Fix immediately
2. **Warnings** (yellow): Schedule for next sprint
3. **Recommendations**: Plan for ongoing maintenance

### 4. Archive Report

Reports are stored in `maintainer/data/audits/YYYY-QN-audit-report.md` and serve as baseline for next quarter.

## Thresholds and Alert Rules

### Quality Thresholds

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Pass rate | 100% | <100% | <95% |
| Failing skills | 0 | 1-2 | 3+ |

### Token Thresholds

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Total tokens | ≤41,783 | +5% | +10% |
| Avg tokens/skill | ≤2,321 | +5% | +10% |
| Skills >500 lines | 0 | 1 | 2+ |

### Cross-Reference Thresholds

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Broken refs | 0 | 1-3 | 4+ |

## Response Playbook

### Alert: Quality Regression

**Symptoms**: Skills that previously passed quality checks are now failing.

**Diagnosis**:

```bash
# Identify failing skills
python3 maintainer/scripts/analysis/check_skill_quality.py

# Check specific skill
python3 maintainer/scripts/analysis/check_skill_quality.py --skill <name> --explain
```

**Response**:

1. Review failing skill's SKILL.md
2. Check recent changes to the skill
3. Fix issues:
   - Missing what/when: Add trigger conditions to description
   - Third-person: Rewrite description with action verbs
   - Deep structure: Flatten heading/bullet nesting
   - Over 500 lines: Extract content to sidecar files

**Prevention**: Run quality check before committing skill changes.

### Alert: Token Inflation

**Symptoms**: Total skill tokens increased >5% without justification.

**Diagnosis**:

```bash
# Measure current state
python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens

# Compare to baseline
python3 maintainer/scripts/audit/detect_regressions.py

# Find largest skills
python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens | grep "Skills by size"
```

**Response**:

1. Identify skills with recent token increases
2. Review changes for:
   - Unnecessary verbosity
   - Duplicated content
   - Missing template usage
3. Apply token-saving templates:
   - Chain aliases (saves 60-75 tokens/skill)
   - Contract templates (saves 80-110 tokens/skill)
   - Protocol v2 compact (saves 40-50 tokens/skill)
4. Consider refactoring if justified

**Prevention**: Use templates for new content, run token measurement before commits.

### Alert: Broken Cross-References

**Symptoms**: References to skills, files, or sections that don't exist.

**Diagnosis**:

```bash
# Check all cross-references
python3 maintainer/scripts/analysis/check_cross_references.py

# JSON output for scripting
python3 maintainer/scripts/analysis/check_cross_references.py --json
```

**Response**:

1. Review broken references list
2. For each broken reference:
   - Verify if target was renamed/moved
   - Update reference or remove if obsolete
   - Check if reference syntax is correct
3. Re-run check to verify fixes

**Prevention**: Run cross-reference check before committing documentation changes.

### Alert: Template De-Adoption

**Symptoms**: Skills reverting to verbose format instead of using templates.

**Diagnosis**:

1. Compare current skill to template examples
2. Check if recent changes removed template usage
3. Review token count trend for affected skill

**Response**:

1. Re-apply templates:
   - `docs/maintainer/skill-chain-aliases.md`
   - `docs/maintainer/skill-contract-template.md`
   - `docs/maintainer/protocol-v2-compact.md`
2. Verify token count improvement
3. Update skill maintainer guide if needed

**Prevention**: Include template checklist in skill PR reviews.

## CI Workflow Integration

### PR Checks

Every PR that touches skills, governance, or templates triggers:

1. Quality check
2. Token measurement
3. Cross-reference validation
4. Regression detection

**PR fails if**:

- Quality pass rate drops below 90%
- Token count increases >10% without explanation
- New broken cross-references introduced

**PR comment includes**:

- Color-coded status summary
- Detailed impact metrics
- Full dashboard (expandable)

### Weekly Scheduled Runs

Every Monday at 9 AM UTC:

1. Full audit runs automatically
2. If regressions detected:
   - GitHub issue created with report
   - Issue labeled: `token-efficiency`, `regression`, `automated`
3. Results archived as artifacts

### Manual Runs

Trigger manually via GitHub Actions:

1. Go to Actions → Token Efficiency Check
2. Click "Run workflow"
3. Choose whether to create issue if regressions found

## Maintenance Cadence

### Weekly

- Review CI check results on merged PRs
- Monitor dashboard status
- Fix critical issues immediately

### Monthly

- Run full dashboard review
- Address accumulated warnings
- Update templates if patterns emerge

### Quarterly

- Run comprehensive audit
- Compare to previous quarter
- Update baseline if justified
- Review and adjust thresholds
- Plan optimization initiatives

## Baseline Management

### Current Baseline

Established: 2026-04-11  
File: `maintainer/data/token_efficiency_baseline.md`

Key metrics:

- Quality: 18/18 skills (100%)
- Total tokens: 41,783
- Avg tokens/skill: 2,321
- Cross-refs broken: 0
- Skills >500 lines: 0

### Updating Baseline

Baseline should be updated when:

1. Major optimization initiative completes successfully
2. Significant architectural changes justify new baseline
3. Quarterly audit shows sustained improvement over 2+ quarters

**Process**:

1. Run audit for current quarter
2. Verify improvements are:
   - Intentional (not accidental)
   - Sustainable (not temporary)
   - Documented (rationale clear)
3. Update `token_efficiency_baseline.md`
4. Update hardcoded targets in scripts:
   - `run_quarterly_audit.py`
   - `token_efficiency_dashboard.py`
   - `detect_regressions.py`
5. Commit with clear message explaining baseline change

## Troubleshooting

### Scripts Fail with "tiktoken not found"

**Solution**: Install tiktoken

```bash
pip install tiktoken
```

### Dashboard Shows "Error: Failed to collect metrics"

**Diagnosis**:

- Check if analysis scripts are executable
- Verify all required files exist
- Run underlying scripts manually to see errors

**Solution**: Re-run with direct script invocation:

```bash
python3 maintainer/scripts/analysis/check_skill_quality.py
python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens
```

### CI Workflow Fails

**Common causes**:

1. Missing dependencies (add to workflow)
2. Script path issues (verify paths are absolute in workflow)
3. Permission issues (check workflow permissions)

**Solution**: Check workflow logs, update workflow file as needed.

### Regressions Detected After Template Application

**Expected behavior**: Token count should decrease, not increase.

**Diagnosis**:

1. Verify template was applied correctly
2. Check if other content was added simultaneously
3. Run token savings calculator:

```bash
python3 maintainer/scripts/analysis/token_savings_calculator.py \
  --before before.json --after after.json
```

**Solution**: Review changes, ensure only template was applied.

## Related Documentation

- `token_efficiency_baseline.md` - Baseline metrics and targets
- `token-efficiency-optimization-plan.md` - Overall optimization strategy
- `skill-chain-aliases.md` - Chain alias templates
- `skill-contract-template.md` - Contract format guide
- `protocol-v2-compact.md` - Compact protocol notation

## Script Reference

### `run_quarterly_audit.py`

**Purpose**: Generate comprehensive quarterly audit report

**Usage**:

```bash
python3 maintainer/scripts/audit/run_quarterly_audit.py [--output FILE] [--json] [--quarter YYYY-QN]
```

**Output**: Audit report in `maintainer/data/audits/`

**Exit codes**:

- 0: Success, no critical regressions
- 1: Critical regressions detected

### `token_efficiency_dashboard.py`

**Purpose**: Display real-time monitoring dashboard

**Usage**:

```bash
python3 maintainer/scripts/audit/token_efficiency_dashboard.py [--markdown] [--no-color] [--json]
```

**Output**: Terminal dashboard (default), markdown, or JSON

**Exit codes**: Always 0 (informational only)

### `detect_regressions.py`

**Purpose**: Compare current state to baseline/last audit

**Usage**:

```bash
python3 maintainer/scripts/audit/detect_regressions.py [--baseline FILE] [--json]
```

**Output**: Regression report with severity

**Exit codes**:

- 0: No critical regressions
- 1: Critical regressions detected

## Best Practices

1. **Run checks locally before PR**: Catch issues early
2. **Address critical issues immediately**: Don't let them accumulate
3. **Review dashboard weekly**: Stay aware of trends
4. **Update baseline carefully**: Only after sustained improvements
5. **Document exceptions**: If token increase is justified, explain in commit message
6. **Use templates consistently**: Avoid reverting to verbose format
7. **Monitor CI results**: Don't ignore workflow failures
8. **Archive audit reports**: Maintain historical record

## Support

For questions or issues with the monitoring system:

1. Check this guide for troubleshooting steps
2. Review script comments for implementation details
3. Open issue with `token-efficiency` label
4. Tag maintainers in discussion

---

**Last updated**: 2026-04-11  
**Monitoring system version**: 1.0  
**Scripts location**: `maintainer/scripts/audit/`
