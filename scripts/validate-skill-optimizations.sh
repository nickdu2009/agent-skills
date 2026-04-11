#!/bin/bash
# Comprehensive validation script for skill optimization project
# Created: 2026-04-11
# Purpose: Validate all P0-P2 optimizations across 18 skills

set -e -o pipefail

SKILLS_DIR="skills"
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

echo "=========================================="
echo "  Skill Optimization Validation Suite"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASS_COUNT++))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAIL_COUNT++))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    ((WARN_COUNT++))
}

# ============================================
# P0 CHECKS - Critical Issues
# ============================================

echo "=== P0: Critical Checks ==="
echo ""

# Check 1: Line count compliance (≤500 lines)
echo "1. Checking line count compliance..."
for skill in $SKILLS_DIR/*/SKILL.md; do
    lines=$(wc -l < "$skill")
    name=$(basename $(dirname "$skill"))
    if [ $lines -gt 500 ]; then
        fail "$name has $lines lines (exceeds 500 limit)"
    else
        # Only report if close to limit or was previously over
        if [ "$name" = "phase-plan-review" ] || [ $lines -gt 480 ]; then
            pass "$name has $lines lines (≤500)"
        fi
    fi
done
echo ""

# Check 2: Chain alias usage (no detailed "Combine with...to..." patterns)
echo "2. Checking chain alias usage..."
CHAIN_RESULTS=$(grep -r "Combine with \`[^']*\` to" $SKILLS_DIR/*/SKILL.md 2>/dev/null || true)
if [ -n "$CHAIN_RESULTS" ]; then
    fail "Found detailed composition prose, should use chain aliases"
    echo "$CHAIN_RESULTS"
else
    pass "All skills use chain alias references"
fi

# Verify chain references exist
chain_refs=$(grep -r "Part of.*chain" $SKILLS_DIR/*/SKILL.md 2>/dev/null | wc -l)
if [ $chain_refs -gt 0 ]; then
    pass "Found $chain_refs chain alias references"
else
    warn "No chain alias references found (may be expected for some skills)"
fi
echo ""

# ============================================
# P1 CHECKS - High Priority
# ============================================

echo "=== P1: High Priority Checks ==="
echo ""

# Check 3: Description word counts (40-100 word target)
echo "3. Checking description field word counts..."
SHORT_COUNT=0
LONG_COUNT=0
OK_COUNT=0

for skill in $SKILLS_DIR/*/SKILL.md; do
    name=$(basename $(dirname "$skill"))
    words=$(sed -n '/^description:/,/^[a-z_]*:/p' "$skill" | head -1 | sed 's/^description: *//' | wc -w)

    if [ $words -lt 40 ]; then
        warn "$name has only $words words (target: 40-100)"
        ((SHORT_COUNT++))
    elif [ $words -gt 100 ]; then
        warn "$name has $words words (target: 40-100, consider simplifying)"
        ((LONG_COUNT++))
    else
        ((OK_COUNT++))
    fi
done

pass "$OK_COUNT skills have descriptions in 40-100 word range"
if [ $SHORT_COUNT -gt 0 ]; then
    warn "$SHORT_COUNT skills have short descriptions (<40 words)"
fi
if [ $LONG_COUNT -gt 0 ]; then
    warn "$LONG_COUNT skills have long descriptions (>100 words)"
fi
echo ""

# Check 4: Description third-person check (manual review prompt)
echo "4. Description voice check..."
echo "   Manual review: Verify all descriptions use third person"
echo "   (Should use 'Guides...', 'Use when...', not 'I...' or 'You...')"
if grep -h "^description:" $SKILLS_DIR/*/SKILL.md | grep -i "I help\|you can\|I can" > /dev/null 2>&1; then
    fail "Found first/second person in descriptions"
else
    pass "No obvious first/second person language detected"
fi
echo ""

# ============================================
# P2 CHECKS - Medium Priority
# ============================================

echo "=== P2: Medium Priority Checks ==="
echo ""

# Check 5: Anti-pattern format standardization
echo "5. Checking anti-pattern format..."
ANTI_PATTERN_SKILLS=0
ANTI_PATTERN_OK=0

for skill in $SKILLS_DIR/*/SKILL.md; do
    name=$(basename $(dirname "$skill"))
    if grep "^# Common Anti-Patterns" "$skill" > /dev/null 2>&1; then
        ((ANTI_PATTERN_SKILLS++))

        # Check format: **Name.** Description. Consequence.
        if grep -A 5 "^# Common Anti-Patterns" "$skill" | grep "^\*\*.*\.\*\*" > /dev/null 2>&1; then
            ((ANTI_PATTERN_OK++))
        else
            fail "$name anti-patterns not in standard format"
        fi

        # Check for template reference
        if grep "skill-anti-pattern-template.md" "$skill" > /dev/null 2>&1; then
            # Good, has reference
            :
        else
            warn "$name missing anti-pattern template reference"
        fi
    fi
done

if [ $ANTI_PATTERN_SKILLS -eq $ANTI_PATTERN_OK ]; then
    pass "All $ANTI_PATTERN_OK skills with anti-patterns use standard format"
else
    fail "Only $ANTI_PATTERN_OK/$ANTI_PATTERN_SKILLS anti-pattern sections properly formatted"
fi
echo ""

# Check 6: Protocol v2 usage
echo "6. Checking protocol block format..."
V1_BLOCKS=$(grep -r "\[task-input-validation\]" $SKILLS_DIR/*/SKILL.md 2>/dev/null | wc -l)
V2_BLOCKS=$(grep -r "\[task-validation:" $SKILLS_DIR/*/SKILL.md 2>/dev/null | wc -l)

if [ $V1_BLOCKS -gt 0 ]; then
    warn "Found $V1_BLOCKS verbose protocol v1 blocks (consider migration to v2)"
fi
if [ $V2_BLOCKS -gt 0 ]; then
    pass "Found $V2_BLOCKS compact protocol v2 blocks"
fi
echo ""

# Check 7: Contract section structure
echo "7. Checking contract section structure..."
CONTRACT_SKILLS=0
CONTRACT_COMPLETE=0

for skill in $SKILLS_DIR/*/SKILL.md; do
    name=$(basename $(dirname "$skill"))
    if grep "^## Contract" "$skill" > /dev/null 2>&1; then
        ((CONTRACT_SKILLS++))

        # Check for standard subsections
        has_pre=$(grep "^### Preconditions" "$skill" > /dev/null 2>&1 && echo 1 || echo 0)
        has_post=$(grep "^### Postconditions" "$skill" > /dev/null 2>&1 && echo 1 || echo 0)
        has_inv=$(grep "^### Invariants" "$skill" > /dev/null 2>&1 && echo 1 || echo 0)
        has_sig=$(grep "^### Downstream Signals" "$skill" > /dev/null 2>&1 && echo 1 || echo 0)

        if [ $has_pre -eq 1 ] && [ $has_post -eq 1 ]; then
            ((CONTRACT_COMPLETE++))
        else
            warn "$name contract missing standard subsections"
        fi
    fi
done

pass "$CONTRACT_COMPLETE/$CONTRACT_SKILLS skills have complete contract structure"

# Check for backtick usage in field names
BACKTICK_COUNT=$(grep -A 30 "^### Downstream Signals" $SKILLS_DIR/*/SKILL.md 2>/dev/null | grep '`[a-z_][a-z_0-9]*`' | wc -l)
if [ $BACKTICK_COUNT -gt 10 ]; then
    pass "Found $BACKTICK_COUNT field names with backtick formatting"
else
    warn "Only found $BACKTICK_COUNT backtick-formatted field names (expected more)"
fi
echo ""

# ============================================
# SUMMARY
# ============================================

echo "=========================================="
echo "  Validation Summary"
echo "=========================================="
echo -e "${GREEN}Passed${NC}: $PASS_COUNT"
echo -e "${YELLOW}Warnings${NC}: $WARN_COUNT"
echo -e "${RED}Failed${NC}: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ All critical validations passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAIL_COUNT validation(s) failed${NC}"
    exit 1
fi
