#!/bin/bash
# Cloud Automation Health Check
# Usage: ./check_status.sh
#
# Checks:
# 1. GCP authentication
# 2. Cloud Function deployment status
# 3. Cloud Scheduler job status
# 4. GCS registry sync status
# 5. Recent auto-boost activity

set -e

PROJECT_ID="elements-archive-2026"
REGION="us-central1"
FUNCTION_NAME="auto-boost"
BUCKET="elements-archive-2026"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "========================================================"
echo -e "${CYAN}CLOUD AUTOMATION HEALTH CHECK${NC}"
echo "========================================================"
echo ""

# 1. Check GCP Authentication
echo -e "${YELLOW}[1/5] GCP Authentication${NC}"
ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo -e "  ${RED}✗ Not authenticated${NC}"
    echo "  Fix: gcloud auth login leonardolech3@gmail.com"
    AUTH_OK=false
else
    echo -e "  Account: ${GREEN}$ACTIVE_ACCOUNT${NC}"
    if [[ "$ACTIVE_ACCOUNT" == *"leonardolech3"* ]]; then
        echo -e "  ${GREEN}✓ Correct account for $PROJECT_ID${NC}"
        AUTH_OK=true
    else
        echo -e "  ${YELLOW}⚠ May not have access to $PROJECT_ID${NC}"
        echo "  Recommended: gcloud auth login leonardolech3@gmail.com"
        AUTH_OK=false
    fi
fi
echo ""

# 2. Check Cloud Function
echo -e "${YELLOW}[2/5] Cloud Function Status${NC}"
if [ "$AUTH_OK" = true ]; then
    FUNC_STATUS=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --project=$PROJECT_ID --format="value(state)" 2>/dev/null || echo "NOT_FOUND")
    if [ "$FUNC_STATUS" = "ACTIVE" ]; then
        FUNC_URL=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --project=$PROJECT_ID --format="value(serviceConfig.uri)" 2>/dev/null)
        echo -e "  ${GREEN}✓ Deployed and ACTIVE${NC}"
        echo "  URL: $FUNC_URL"
    elif [ "$FUNC_STATUS" = "NOT_FOUND" ]; then
        echo -e "  ${RED}✗ Not deployed${NC}"
        echo "  Fix: cd .agent/tools/cloud && ./deploy.sh scheduler"
    else
        echo -e "  ${YELLOW}⚠ Status: $FUNC_STATUS${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ Skipped (auth required)${NC}"
fi
echo ""

# 3. Check Cloud Scheduler
echo -e "${YELLOW}[3/5] Cloud Scheduler Status${NC}"
if [ "$AUTH_OK" = true ]; then
    SCHED_STATUS=$(gcloud scheduler jobs describe auto-boost-hourly --location=$REGION --project=$PROJECT_ID --format="value(state)" 2>/dev/null || echo "NOT_FOUND")
    if [ "$SCHED_STATUS" = "ENABLED" ]; then
        LAST_RUN=$(gcloud scheduler jobs describe auto-boost-hourly --location=$REGION --project=$PROJECT_ID --format="value(lastAttemptTime)" 2>/dev/null || echo "Never")
        echo -e "  ${GREEN}✓ Scheduler ENABLED${NC}"
        echo "  Last run: $LAST_RUN"
    elif [ "$SCHED_STATUS" = "NOT_FOUND" ]; then
        echo -e "  ${RED}✗ Scheduler not created${NC}"
        echo "  Fix: cd .agent/tools/cloud && ./deploy.sh scheduler"
    else
        echo -e "  ${YELLOW}⚠ Status: $SCHED_STATUS${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ Skipped (auth required)${NC}"
fi
echo ""

# 4. Check GCS Registry Sync
echo -e "${YELLOW}[4/5] GCS Registry Status${NC}"
# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
REGISTRY_DIR="$PROJECT_ROOT/.agent/registry"

LOCAL_COUNT=$(ls -1 "$REGISTRY_DIR/inbox/OPP-"*.yaml 2>/dev/null | wc -l | tr -d ' ')
echo "  Local inbox: $LOCAL_COUNT opportunities"

if [ "$AUTH_OK" = true ]; then
    GCS_COUNT=$(gsutil ls "gs://$BUCKET/.agent/registry/inbox/OPP-*.yaml" 2>/dev/null | wc -l | tr -d ' ')
    echo "  GCS inbox: $GCS_COUNT opportunities"

    if [ "$LOCAL_COUNT" -gt "$GCS_COUNT" ]; then
        DIFF=$((LOCAL_COUNT - GCS_COUNT))
        echo -e "  ${RED}✗ $DIFF opportunities not synced to GCS${NC}"
        echo "  Fix: python .agent/tools/cloud/sync_registry.py"
    elif [ "$LOCAL_COUNT" -eq "$GCS_COUNT" ]; then
        echo -e "  ${GREEN}✓ Registries in sync${NC}"
    else
        echo -e "  ${YELLOW}⚠ GCS has more than local (pull needed?)${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ GCS check skipped (auth required)${NC}"
fi
echo ""

# 5. Check Recent Activity
echo -e "${YELLOW}[5/5] Recent Auto-Boost Activity${NC}"
if [ "$AUTH_OK" = true ]; then
    RECENT=$(gsutil ls -l "gs://$BUCKET/intelligence/auto_boost/" 2>/dev/null | tail -5 || echo "No reports found")
    if [ -z "$RECENT" ] || [ "$RECENT" = "No reports found" ]; then
        echo -e "  ${YELLOW}⚠ No auto-boost reports found${NC}"
        echo "  (Cloud Function may not have run yet)"
    else
        echo "  Recent reports:"
        echo "$RECENT" | sed 's/^/    /'
    fi
else
    echo -e "  ${YELLOW}⚠ Skipped (auth required)${NC}"
fi

echo ""
echo "========================================================"
echo -e "${CYAN}SUMMARY${NC}"
echo "========================================================"

# Summary
ISSUES=0
if [ "$AUTH_OK" != true ]; then
    echo -e "  ${RED}[BLOCKED]${NC} GCP authentication required"
    ISSUES=$((ISSUES + 1))
fi

if [ "$FUNC_STATUS" != "ACTIVE" ] 2>/dev/null; then
    echo -e "  ${RED}[ACTION]${NC} Deploy Cloud Function: ./deploy.sh scheduler"
    ISSUES=$((ISSUES + 1))
fi

if [ "$LOCAL_COUNT" -gt "${GCS_COUNT:-0}" ] 2>/dev/null; then
    echo -e "  ${YELLOW}[ACTION]${NC} Sync registry: python sync_registry.py"
    ISSUES=$((ISSUES + 1))
fi

if [ $ISSUES -eq 0 ]; then
    echo -e "  ${GREEN}✓ All systems operational${NC}"
fi

echo ""
