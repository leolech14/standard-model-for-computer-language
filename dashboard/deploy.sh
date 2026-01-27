#!/bin/bash
# Deploy Palace Dashboard to Cloud Run

set -e

PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="palace-dashboard"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "Deploying Palace Dashboard to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Build and push
echo "Building container..."
gcloud builds submit --tag "$IMAGE"

# Deploy
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5 \
    --set-env-vars "GCS_BUCKET=elements-archive-2026,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Dashboard URL:"
gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format="value(status.url)"
