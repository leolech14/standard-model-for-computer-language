#!/bin/bash
# Deploy auto-boost Cloud Function to GCP
#
# Prerequisites:
#   - gcloud CLI authenticated
#   - GEMINI_API_KEY set in Secret Manager
#
# Usage:
#   ./deploy.sh              # Deploy function
#   ./deploy.sh scheduler    # Also create hourly scheduler

set -e

PROJECT_ID="elements-archive-2026"
REGION="us-central1"
FUNCTION_NAME="auto-boost"
BUCKET="elements-archive-2026"
ENTRY_POINT="main"
RUNTIME="python311"

echo "========================================"
echo "Deploying auto-boost Cloud Function"
echo "========================================"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Bucket: $BUCKET"
echo ""

# Check authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1; then
    echo "ERROR: Not authenticated. Run: gcloud auth login"
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Get GEMINI_API_KEY from Doppler or Secret Manager
if command -v doppler &> /dev/null; then
    GEMINI_KEY=$(doppler secrets get GEMINI_API_KEY --plain 2>/dev/null || true)
fi

if [ -z "$GEMINI_KEY" ]; then
    echo "Getting GEMINI_API_KEY from Secret Manager..."
    GEMINI_KEY=$(gcloud secrets versions access latest --secret=GEMINI_API_KEY 2>/dev/null || true)
fi

if [ -z "$GEMINI_KEY" ]; then
    echo "ERROR: GEMINI_API_KEY not found in Doppler or Secret Manager"
    echo "Set it with:"
    echo "  gcloud secrets create GEMINI_API_KEY --replication-policy=automatic"
    echo "  echo -n 'your-key' | gcloud secrets versions add GEMINI_API_KEY --data-file=-"
    exit 1
fi

# Create requirements.txt for Cloud Function
cat > /tmp/requirements.txt << 'EOF'
google-cloud-storage>=2.14.0
google-genai>=0.4.0
pyyaml>=6.0
functions-framework>=3.5.0
EOF

# Deploy function
echo ""
echo "Deploying function..."
cd "$(dirname "$0")"

gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=$RUNTIME \
    --region=$REGION \
    --source=. \
    --entry-point=$ENTRY_POINT \
    --trigger-http \
    --allow-unauthenticated \
    --memory=512MB \
    --timeout=300s \
    --set-env-vars="GEMINI_API_KEY=$GEMINI_KEY,GCS_BUCKET=$BUCKET,AUTO_PROMOTE_THRESHOLD=90"

FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --format='value(serviceConfig.uri)')
echo ""
echo "Function deployed: $FUNCTION_URL"

# Create scheduler if requested
if [ "$1" == "scheduler" ]; then
    echo ""
    echo "Creating hourly scheduler..."

    gcloud scheduler jobs create http auto-boost-hourly \
        --location=$REGION \
        --schedule="0 * * * *" \
        --uri="$FUNCTION_URL" \
        --http-method=GET \
        --description="Hourly auto-boost of opportunities" \
        --attempt-deadline=600s \
        2>/dev/null || \
    gcloud scheduler jobs update http auto-boost-hourly \
        --location=$REGION \
        --schedule="0 * * * *" \
        --uri="$FUNCTION_URL"

    echo "Scheduler created: runs every hour"
fi

echo ""
echo "========================================"
echo "Deployment complete!"
echo "========================================"
echo ""
echo "Test with:"
echo "  curl $FUNCTION_URL"
echo ""
echo "View logs:"
echo "  gcloud functions logs read $FUNCTION_NAME --region=$REGION --gen2"
