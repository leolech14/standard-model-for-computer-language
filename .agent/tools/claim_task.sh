#!/bin/bash
# Atomic Task Claim Script
# Uses filesystem mv for race-condition-free task reservation
# Enforces state machine: only READY tasks can be claimed (v2.0)

set -e

REGISTRY_DIR="$(dirname "$0")/../registry"
TASK_ID="${1:-}"
AGENT_ID="${2:-$(whoami)}"

if [ -z "$TASK_ID" ]; then
    echo "Usage: $0 <TASK-ID> [AGENT-ID]"
    echo "Example: $0 TASK-001 claude-opus"
    exit 1
fi

TIMESTAMP=$(date +%s)
SOURCE="${REGISTRY_DIR}/active/${TASK_ID}.yaml"
TARGET="${REGISTRY_DIR}/claimed/${TIMESTAMP}_${AGENT_ID}_${TASK_ID}.yaml"

# Check if task exists
if [ ! -f "$SOURCE" ]; then
    echo "ERROR: Task ${TASK_ID} not found in active/"
    echo "Available tasks:"
    ls -1 "${REGISTRY_DIR}/active/"
    exit 1
fi

# STATE MACHINE ENFORCEMENT (strict gate)
# Valid claimable states: READY (v2.0 simplified lifecycle)
# Legacy support: SCOPED, PLANNED also accepted for migration period
TASK_STATUS=$(grep -E "^status:" "$SOURCE" | head -1 | awk '{print $2}')
case "$TASK_STATUS" in
    READY|SCOPED|PLANNED)
        # Valid - proceed with claim (SCOPED/PLANNED = legacy support)
        ;;
    DISCOVERY)
        echo "ERROR: Task ${TASK_ID} is in DISCOVERY state"
        echo "Tasks must be READY before claiming."
        echo "Tip: Update the task file to set status: READY"
        exit 1
        ;;
    EXECUTING)
        echo "ERROR: Task ${TASK_ID} is already EXECUTING"
        echo "Another agent may be working on it."
        exit 1
        ;;
    COMPLETE|ARCHIVED)
        echo "ERROR: Task ${TASK_ID} is ${TASK_STATUS}"
        echo "This task is already finished."
        exit 1
        ;;
    *)
        echo "WARNING: Unknown status '${TASK_STATUS}' - proceeding with caution"
        ;;
esac

# Atomic claim attempt
if mv "$SOURCE" "$TARGET" 2>/dev/null; then
    echo "SUCCESS: Claimed ${TASK_ID}"
    echo "Claim file: ${TARGET}"
    echo "Timestamp: ${TIMESTAMP}"
    echo "Agent: ${AGENT_ID}"
    echo "Previous status: ${TASK_STATUS}"
else
    echo "FAILED: Task ${TASK_ID} already claimed or moved"
    exit 1
fi
