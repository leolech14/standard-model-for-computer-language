#!/bin/bash
# promote_opportunity.sh - Promote an opportunity from inbox to active task
#
# DELEGATES TO: promote_opportunity.py (Python version with proper YAML parsing)
#
# Usage:
#   ./promote_opportunity.sh <opportunity-file> [task-id]
#
# Example:
#   ./promote_opportunity.sh OPP-001.yaml TASK-125

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Delegate to Python version
exec "$SCRIPT_DIR/promote_opportunity.py" "$@"

# --- LEGACY BASH CODE BELOW (kept for reference) ---
exit 0

set -e
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
INBOX_DIR="$AGENT_DIR/registry/inbox"
ACTIVE_DIR="$AGENT_DIR/registry/active"
SCHEMA_DIR="$AGENT_DIR/schema"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: $0 <opportunity-file> [task-id]"
    echo ""
    echo "Promotes an opportunity from inbox to an active task."
    echo ""
    echo "Arguments:"
    echo "  opportunity-file  Path to opportunity YAML (relative to inbox/ or absolute)"
    echo "  task-id           Optional task ID (e.g., TASK-125). Auto-generates if not provided."
    echo ""
    echo "Example:"
    echo "  $0 OPP-001.yaml"
    echo "  $0 OPP-001.yaml TASK-125"
    exit 1
}

# Check arguments
if [ $# -lt 1 ]; then
    usage
fi

OPP_FILE="$1"
TASK_ID="$2"

# Resolve opportunity file path
if [[ "$OPP_FILE" != /* ]]; then
    if [ -f "$INBOX_DIR/$OPP_FILE" ]; then
        OPP_FILE="$INBOX_DIR/$OPP_FILE"
    elif [ -f "$OPP_FILE" ]; then
        OPP_FILE="$(pwd)/$OPP_FILE"
    else
        echo -e "${RED}ERROR: Opportunity file not found: $OPP_FILE${NC}"
        exit 1
    fi
fi

if [ ! -f "$OPP_FILE" ]; then
    echo -e "${RED}ERROR: File not found: $OPP_FILE${NC}"
    exit 1
fi

# Generate task ID if not provided
if [ -z "$TASK_ID" ]; then
    # Find highest existing task number
    HIGHEST=$(ls "$ACTIVE_DIR"/TASK-*.yaml 2>/dev/null | \
              sed 's/.*TASK-\([0-9]*\)\.yaml/\1/' | \
              sort -n | tail -1)

    if [ -z "$HIGHEST" ]; then
        HIGHEST=0
    fi

    NEXT=$((HIGHEST + 1))
    TASK_ID=$(printf "TASK-%03d" $NEXT)
fi

TASK_FILE="$ACTIVE_DIR/$TASK_ID.yaml"

if [ -f "$TASK_FILE" ]; then
    echo -e "${RED}ERROR: Task already exists: $TASK_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}Promoting opportunity to task...${NC}"
echo "  Source: $OPP_FILE"
echo "  Target: $TASK_FILE"

# Extract fields from opportunity
OPP_TITLE=$(grep -E "^title:" "$OPP_FILE" | head -1 | sed 's/title: *//' | tr -d '"')
OPP_DESC=$(grep -E "^description:" "$OPP_FILE" | head -1 | sed 's/description: *//' | tr -d '"')
OPP_ID=$(grep -E "^id:" "$OPP_FILE" | head -1 | sed 's/id: *//' | tr -d '"')
OPP_URGENCY=$(grep -E "^urgency:" "$OPP_FILE" | head -1 | sed 's/urgency: *//' | tr -d '"')

# Default urgency to MEDIUM if not set
if [ -z "$OPP_URGENCY" ]; then
    OPP_URGENCY="MEDIUM"
fi

# Map urgency to initial confidence
case "$OPP_URGENCY" in
    CRITICAL) CONFIDENCE=90 ;;
    HIGH)     CONFIDENCE=80 ;;
    MEDIUM)   CONFIDENCE=70 ;;
    LOW)      CONFIDENCE=60 ;;
    *)        CONFIDENCE=70 ;;
esac

# Create task file
cat > "$TASK_FILE" << EOF
# Task promoted from opportunity $OPP_ID
# Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

id: $TASK_ID
title: "$OPP_TITLE"
status: DISCOVERY

description: |
  $OPP_DESC

  ---
  Promoted from: $OPP_ID
  Original urgency: $OPP_URGENCY

confidence:
  factual: $CONFIDENCE
  alignment: $CONFIDENCE
  current: $CONFIDENCE
  onwards: $CONFIDENCE
  verdict: $CONFIDENCE

tracking:
  created_at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  promoted_from: "$OPP_ID"

steps_completed: []

output_artifacts: []
EOF

# Update opportunity file with promotion info
echo "" >> "$OPP_FILE"
echo "# --- PROMOTED ---" >> "$OPP_FILE"
echo "promoted_to: $TASK_ID" >> "$OPP_FILE"
echo "promoted_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$OPP_FILE"

# Move opportunity to processed (optional - could also delete)
# For now, keep it in inbox with the promoted_to marker

echo ""
echo -e "${GREEN}SUCCESS: Created $TASK_FILE${NC}"
echo ""
echo "Next steps:"
echo "  1. Review and refine the task: $TASK_FILE"
echo "  2. Score 4D confidence properly"
echo "  3. Add to sprint if appropriate"
echo "  4. Claim task when ready: ./claim_task.sh $TASK_ID"
