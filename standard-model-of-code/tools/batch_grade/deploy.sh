#!/bin/bash
# Deploy and run Collider batch grade on GCP Cloud Run Jobs
# Architecture (validated 2026-01-24):
# - Uses Artifact Registry (gcr.io deprecated March 2025)
# - 20 parallel tasks, each processing ~50 repos (striping pattern)
# - Per-task output files to avoid GCS write contention
# - Auto-deletes job after completion, results persist in GCS

set -e

PROJECT_ID="elements-archive-2026"
REGION="us-central1"
JOB_NAME="collider-batch-grade"
AR_REPO="collider"  # Artifact Registry repository name
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${JOB_NAME}"
GCS_BUCKET="${PROJECT_ID}"

# Cloud Run Jobs configuration - TURBO MODE
TASKS=20           # Number of parallel tasks (each handles ~50 repos)
PARALLELISM=20     # TURBO: All tasks run simultaneously
MEMORY="8Gi"       # Per task
CPU="4"            # Per task
TASK_TIMEOUT="7200s"   # 2 hours per task (turbo = faster completion)
MAX_RETRIES=0      # No retries to control costs
SERVICE_ACCOUNT="collider-batch@${PROJECT_ID}.iam.gserviceaccount.com"

echo "=============================================="
echo "COLLIDER BATCH GRADE - GCP DEPLOYMENT"
echo "=============================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Image: ${IMAGE}"
echo "Tasks: ${TASKS} (parallelism: ${PARALLELISM})"
echo "Resources: ${CPU} vCPU, ${MEMORY} memory"
echo "Timeout: ${TASK_TIMEOUT} per task"
echo "Output: gs://${GCS_BUCKET}/grades/"
echo "=============================================="

# Navigate to collider root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COLLIDER_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${COLLIDER_ROOT}"

echo ""
echo "[1/7] Ensuring service account exists with GCS write permissions..."
SA_NAME="collider-batch"
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT}" --project="${PROJECT_ID}" 2>/dev/null; then
    gcloud iam service-accounts create "${SA_NAME}" \
        --project="${PROJECT_ID}" \
        --display-name="Collider Batch Grade Service Account"
fi

# Grant bucket write permission
gsutil iam ch "serviceAccount:${SERVICE_ACCOUNT}:objectCreator" "gs://${GCS_BUCKET}" 2>/dev/null || true
gsutil iam ch "serviceAccount:${SERVICE_ACCOUNT}:objectViewer" "gs://${GCS_BUCKET}" 2>/dev/null || true

echo ""
echo "[2/7] Ensuring Artifact Registry repository exists..."
gcloud artifacts repositories describe "${AR_REPO}" \
    --location="${REGION}" \
    --project="${PROJECT_ID}" 2>/dev/null || \
gcloud artifacts repositories create "${AR_REPO}" \
    --repository-format=docker \
    --location="${REGION}" \
    --project="${PROJECT_ID}" \
    --description="Collider container images"

echo ""
echo "[3/7] Configuring Docker for Artifact Registry..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

echo ""
echo "[4/7] Building Docker image..."
docker build -f tools/batch_grade/Dockerfile -t "${IMAGE}" .

echo ""
echo "[5/7] Pushing to Artifact Registry..."
docker push "${IMAGE}"

echo ""
echo "[6/7] Creating Cloud Run Job..."
gcloud run jobs delete "${JOB_NAME}" --region="${REGION}" --quiet 2>/dev/null || true

gcloud run jobs create "${JOB_NAME}" \
    --image="${IMAGE}" \
    --region="${REGION}" \
    --memory="${MEMORY}" \
    --cpu="${CPU}" \
    --max-retries="${MAX_RETRIES}" \
    --task-timeout="${TASK_TIMEOUT}" \
    --tasks="${TASKS}" \
    --parallelism="${PARALLELISM}" \
    --service-account="${SERVICE_ACCOUNT}" \
    --set-env-vars="GCS_BUCKET=${GCS_BUCKET},WORKERS=6,TIMEOUT_PER_REPO=180"

echo ""
echo "[7/7] Starting job execution - TURBO MODE..."
echo ">>> ${TASKS} tasks ALL running simultaneously"
echo ">>> 20 containers × 6 workers = 120 concurrent graders"
echo ">>> ~50 repos per task @ 3min timeout → estimated 15-30 minutes"
echo ""

EXECUTION_START=$(date +%s)
gcloud run jobs execute "${JOB_NAME}" \
    --region="${REGION}" \
    --wait

EXECUTION_END=$(date +%s)
DURATION=$((EXECUTION_END - EXECUTION_START))

echo ""
echo "=============================================="
echo "EXECUTION COMPLETE"
echo "=============================================="
echo "Duration: $((DURATION / 60)) minutes $((DURATION % 60)) seconds"
echo ""

# List results
echo "Results in GCS:"
gsutil ls "gs://${GCS_BUCKET}/grades/" | head -20

echo ""
echo "To aggregate all task results:"
echo "  gsutil cat 'gs://${GCS_BUCKET}/grades/*/task-*.json' | jq -s 'map(.results) | flatten'"
echo ""
echo "To view grade distribution:"
echo "  gsutil cat 'gs://${GCS_BUCKET}/grades/*/task-*.json' | jq -s 'map(.grade_distribution) | add'"
echo ""

# Ask before cleanup
read -p "Delete the Cloud Run Job? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleaning up job..."
    gcloud run jobs delete "${JOB_NAME}" --region="${REGION}" --quiet
    echo "Job deleted. Image retained in Artifact Registry for re-runs."
else
    echo "Job retained. To delete later:"
    echo "  gcloud run jobs delete ${JOB_NAME} --region=${REGION}"
fi

echo ""
echo "=============================================="
echo "DONE"
echo "=============================================="
