#!/bin/bash
# Handler Wiring Coverage Checker
# Run this script to quickly assess handler wiring status

set -e

TEMPLATE_FILE="src/core/viz/assets/template.html"
PANEL_HANDLERS="src/core/viz/assets/modules/panel-handlers.js"
SIDEBAR_HANDLERS="src/core/viz/assets/modules/sidebar.js"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "Handler Coverage Check"
echo "======================================"
echo ""

# Extract template IDs
echo "Extracting control IDs from template..."
grep 'id="' "$TEMPLATE_FILE" | sed 's/.*id="//' | sed 's/".*//' | \
  grep -v 'panel-\|grid-stack\|3d-graph\|header\|loader\|toast' | sort -u > /tmp/template_ids.txt
TEMPLATE_COUNT=$(wc -l < /tmp/template_ids.txt)
echo -e "${GREEN}✓${NC} Found $TEMPLATE_COUNT controls in template"

# Extract handler IDs
echo "Extracting handler IDs from panel-handlers.js..."
grep -E "getElementById\(|_bindPanel" "$PANEL_HANDLERS" | sed -E "s/.*getElementById\(['\"]([^'\"]+).*/\1/" | \
  sed -E "s/.*_bindPanel[^(]*\('([^']+)'.*/\1/" | \
  grep -v "=\|function\|const\|let\|if\|this\|typeof\|document\|console" | sort -u > /tmp/panel_handler_ids.txt
PANEL_COUNT=$(wc -l < /tmp/panel_handler_ids.txt)
echo -e "${GREEN}✓${NC} Found $PANEL_COUNT handlers in panel-handlers.js"

echo "Extracting handler IDs from sidebar.js..."
grep -E "getElementById\(|_bind" "$SIDEBAR_HANDLERS" | sed -E "s/.*getElementById\(['\"]([^'\"]+).*/\1/" | \
  grep -v "=\|function\|const\|let\|if\|this\|typeof\|document\|console" | sort -u > /tmp/sidebar_handler_ids.txt
SIDEBAR_COUNT=$(wc -l < /tmp/sidebar_handler_ids.txt)
echo -e "${GREEN}✓${NC} Found $SIDEBAR_COUNT handlers in sidebar.js"

# Combine handlers
cat /tmp/panel_handler_ids.txt /tmp/sidebar_handler_ids.txt | sort -u > /tmp/all_handler_ids.txt
ALL_HANDLER_COUNT=$(wc -l < /tmp/all_handler_ids.txt)

# Find direct matches
comm -12 /tmp/template_ids.txt /tmp/all_handler_ids.txt | sort -u > /tmp/matched_ids.txt
MATCHED=$(wc -l < /tmp/matched_ids.txt)

# Find orphaned
comm -23 /tmp/template_ids.txt /tmp/all_handler_ids.txt > /tmp/orphaned_ids.txt
ORPHANED=$(wc -l < /tmp/orphaned_ids.txt)

echo ""
echo "======================================"
echo "Results"
echo "======================================"
COVERAGE=$((MATCHED * 100 / TEMPLATE_COUNT))
echo "Total controls: $TEMPLATE_COUNT"
echo "Total handlers: $ALL_HANDLER_COUNT"
echo "Direct matches: $MATCHED"
echo "Orphaned: $ORPHANED"
echo ""

if [ $COVERAGE -ge 80 ]; then
  echo -e "${GREEN}Coverage: $COVERAGE%${NC}"
elif [ $COVERAGE -ge 60 ]; then
  echo -e "${YELLOW}Coverage: $COVERAGE%${NC}"
else
  echo -e "${RED}Coverage: $COVERAGE%${NC}"
fi

echo ""
echo "======================================"
echo "Checking for naming mismatches..."
echo "======================================"

# Check cfg-* → panel-* conversions
CFG_MATCHES=0
echo ""
echo "cfg-* → panel-* conversions:"
grep '^cfg-' /tmp/template_ids.txt | while read id; do
  panel_equiv=$(echo "$id" | sed 's/^cfg-/panel-/')
  if grep -q "^$panel_equiv$" /tmp/panel_handler_ids.txt; then
    CFG_MATCHES=$((CFG_MATCHES + 1))
    echo "  ✓ $id → $panel_equiv"
  fi
done | head -5
CFG_MATCH_COUNT=$(grep '^cfg-' /tmp/template_ids.txt | while read id; do
  panel_equiv=$(echo "$id" | sed 's/^cfg-/panel-/')
  grep -q "^$panel_equiv$" /tmp/panel_handler_ids.txt && echo 1 || echo 0
done | grep 1 | wc -l)
echo "  Total cfg-* matches: $CFG_MATCH_COUNT"

# Check stats-* → panel-stat-* conversions
echo ""
echo "stats-* → panel-stat-* conversions:"
grep '^stats-' /tmp/template_ids.txt | while read id; do
  panel_equiv=$(echo "$id" | sed 's/^stats-/panel-stat-/')
  if grep -q "^$panel_equiv$" /tmp/panel_handler_ids.txt; then
    echo "  ✓ $id → $panel_equiv"
  fi
done
STATS_MATCH_COUNT=$(grep '^stats-' /tmp/template_ids.txt | while read id; do
  panel_equiv=$(echo "$id" | sed 's/^stats-/panel-stat-/')
  grep -q "^$panel_equiv$" /tmp/panel_handler_ids.txt && echo 1 || echo 0
done | grep 1 | wc -l)
echo "  Total stats-* matches: $STATS_MATCH_COUNT"

echo ""
echo "======================================"
echo "Top orphaned controls:"
echo "======================================"
head -15 /tmp/orphaned_ids.txt

echo ""
echo "======================================"
echo "Files:"
echo "======================================"
echo "Full orphaned list: /tmp/orphaned_ids.txt"
echo "All handler IDs: /tmp/all_handler_ids.txt"
echo "Template IDs: /tmp/template_ids.txt"
echo ""
echo "For detailed analysis, see:"
echo "  - HANDLER_COVERAGE_CORRECTED.md"
echo "  - CONTROL_HANDLER_MAPPING.md"
echo ""
