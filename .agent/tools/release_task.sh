#!/bin/bash
# Release a claimed task (success or failure)
# Hybrid validation: warns on unusual transitions but allows them

set -e

REGISTRY_DIR="$(dirname "$0")/../registry"
TASK_ID="${1:-}"
STATUS="${2:-COMPLETE}"  # COMPLETE, FAILED, or RETRY

if [ -z "$TASK_ID" ]; then
    echo "Usage: $0 <TASK-ID> [STATUS]"
    echo "STATUS: COMPLETE (default), FAILED, or RETRY"
    exit 1
fi

# Find the claimed file
CLAIMED_FILE=$(ls "${REGISTRY_DIR}/claimed/"*"_${TASK_ID}.yaml" 2>/dev/null | head -1)

if [ -z "$CLAIMED_FILE" ] || [ ! -f "$CLAIMED_FILE" ]; then
    echo "ERROR: No claimed file found for ${TASK_ID}"
    echo "Claimed tasks:"
    ls -1 "${REGISTRY_DIR}/claimed/" 2>/dev/null || echo "(none)"
    exit 1
fi

# STATE VALIDATION (warn mode - log but allow)
TASK_STATUS=$(grep -E "^status:" "$CLAIMED_FILE" | head -1 | awk '{print $2}')
CLAIM_TIME=$(basename "$CLAIMED_FILE" | cut -d'_' -f1)
CLAIM_AGE=$(( ($(date +%s) - CLAIM_TIME) / 60 ))

# Warn on unusual patterns
if [ "$STATUS" = "COMPLETE" ] && [ "$CLAIM_AGE" -lt 2 ]; then
    echo "WARNING: Task completed in <2 minutes. Verify work is actually done."
fi

if [ "$STATUS" = "COMPLETE" ] && [ "$TASK_STATUS" = "SCOPED" ]; then
    echo "WARNING: Completing task that was SCOPED (skipped PLANNED/EXECUTING states)"
    echo "         This is allowed but may indicate rushed work."
fi

case "$STATUS" in
    COMPLETE|FAILED)
        # Move to archive
        TARGET="${REGISTRY_DIR}/archive/${STATUS}_${TASK_ID}.yaml"
        mv "$CLAIMED_FILE" "$TARGET"
        echo "SUCCESS: Task ${TASK_ID} archived as ${STATUS}"
        echo "Archive file: ${TARGET}"
        echo "Claim duration: ${CLAIM_AGE} minutes"
        ;;
    RETRY)
        # Move back to active for retry
        TARGET="${REGISTRY_DIR}/active/${TASK_ID}.yaml"
        mv "$CLAIMED_FILE" "$TARGET"
        echo "SUCCESS: Task ${TASK_ID} returned to active for retry"
        echo "Claim duration: ${CLAIM_AGE} minutes"
        ;;
    *)
        echo "ERROR: Unknown status '${STATUS}'"
        echo "Valid: COMPLETE, FAILED, RETRY"
        exit 1
        ;;
esac
