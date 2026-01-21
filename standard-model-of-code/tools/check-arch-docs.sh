#!/bin/bash
# check-arch-docs.sh - Validate ARCHITECTURE.html against filesystem
#
# Usage: ./tools/check-arch-docs.sh
# Exit codes: 0 = valid, 1 = discrepancies found

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MODULES_DIR="$PROJECT_ROOT/src/core/viz/assets/modules"
ARCH_DOC="$PROJECT_ROOT/src/core/viz/assets/ARCHITECTURE.html"

# Allowlist: modules documented as "Planned / Not Implemented"
PLANNED_MODULES=("graph-core.js")

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "=== Architecture Documentation Validator ==="
echo ""

# 1. Get actual modules from filesystem
ACTUAL_MODULES=$(ls -1 "$MODULES_DIR"/*.js 2>/dev/null | xargs -n1 basename | sort)
ACTUAL_COUNT=$(echo "$ACTUAL_MODULES" | wc -l | tr -d ' ')

echo "Filesystem: $ACTUAL_COUNT modules in $MODULES_DIR"

# 2. Extract documented modules from ARCHITECTURE.html
# Only look within the MODULE_INVENTORY section (between BEGIN and END markers)
DOC_MODULES=$(sed -n '/BEGIN:MODULE_INVENTORY/,/END:MODULE_INVENTORY/p' "$ARCH_DOC" | grep -oE '<code>[a-z0-9-]+\.js</code>' | sed 's/<code>//g; s/<\/code>//g' | sort | uniq)
DOC_COUNT=$(echo "$DOC_MODULES" | wc -l | tr -d ' ')

echo "Documented: $DOC_COUNT modules in ARCHITECTURE.html"
echo ""

# 3. Check for modules in filesystem but not documented
ERRORS=0

echo "--- Checking for undocumented modules ---"
for module in $ACTUAL_MODULES; do
    if ! echo "$DOC_MODULES" | grep -q "^${module}$"; then
        # Check if it's in the allowlist
        if [[ " ${PLANNED_MODULES[@]} " =~ " ${module} " ]]; then
            echo -e "${YELLOW}[PLANNED]${NC} $module (in allowlist)"
        else
            echo -e "${RED}[MISSING]${NC} $module exists but not documented"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

# 4. Check for documented modules that don't exist
echo ""
echo "--- Checking for phantom modules ---"
for module in $DOC_MODULES; do
    if ! echo "$ACTUAL_MODULES" | grep -q "^${module}$"; then
        # Check if it's in the planned allowlist
        if [[ " ${PLANNED_MODULES[@]} " =~ " ${module} " ]]; then
            echo -e "${YELLOW}[PLANNED]${NC} $module (documented as not implemented)"
        else
            echo -e "${RED}[PHANTOM]${NC} $module documented but doesn't exist"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

# 5. Verify count in doc-meta section
DOC_META_COUNT=$(grep -oE 'Modules Implemented:</strong> [0-9]+' "$ARCH_DOC" | grep -oE '[0-9]+' || echo "0")
echo ""
echo "--- Checking module count in doc-meta ---"
if [ "$DOC_META_COUNT" = "$ACTUAL_COUNT" ]; then
    echo -e "${GREEN}[OK]${NC} Doc says $DOC_META_COUNT modules, filesystem has $ACTUAL_COUNT"
else
    echo -e "${RED}[MISMATCH]${NC} Doc says $DOC_META_COUNT modules, filesystem has $ACTUAL_COUNT"
    ERRORS=$((ERRORS + 1))
fi

# 6. Summary
echo ""
echo "=== Summary ==="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}PASS${NC}: Documentation matches filesystem"
    exit 0
else
    echo -e "${RED}FAIL${NC}: $ERRORS discrepancies found"
    echo ""
    echo "To fix: Update ARCHITECTURE.html or add missing modules to PLANNED_MODULES allowlist"
    exit 1
fi
