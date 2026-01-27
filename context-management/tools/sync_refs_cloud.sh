#!/bin/bash
# Sync reference library to Google Cloud Storage
# Bucket: gs://elements-archive-2026/references/

set -e

PROJECT="elements-archive-2026"
BUCKET="gs://${PROJECT}/references"
LOCAL="/Users/lech/PROJECTS_all/PROJECT_elements/context-management/docs/theory/references"

echo "=== SYNCING REFERENCE LIBRARY TO GCS ==="
echo "Local:  $LOCAL"
echo "Bucket: $BUCKET"
echo ""

# Check gcloud auth
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "Error: Not authenticated to gcloud. Run: gcloud auth login"
    exit 1
fi

# Metadata (small, always sync)
echo "[1/5] Syncing metadata/ (260KB)..."
gsutil -m rsync -r -d "$LOCAL/metadata" "$BUCKET/metadata/" 2>&1 | tail -3

# Index (tiny, always sync)
echo "[2/5] Syncing index/ (catalogs)..."
gsutil -m rsync -r -d "$LOCAL/index" "$BUCKET/index/" 2>&1 | tail -3

# TXT files (21MB, always sync)
echo "[3/5] Syncing txt/ (21MB)..."
gsutil -m rsync -r -d "$LOCAL/txt" "$BUCKET/txt/" 2>&1 | tail -3

# Schemas + docs (tiny, always sync)
echo "[4/5] Syncing schemas and documentation..."
gsutil cp "$LOCAL/library_schema.json" "$BUCKET/"
gsutil cp "$LOCAL/holon_hierarchy_schema.json" "$BUCKET/"
gsutil cp "$LOCAL/README.md" "$BUCKET/"
gsutil cp "$LOCAL/VALIDATION_AND_INTEGRATION_PLAN.md" "$BUCKET/"

# PDFs (322MB, optional)
if [ "$1" == "--include-pdfs" ]; then
    echo "[5/5] Syncing pdf/ (322MB)..."
    gsutil -m rsync -r -d "$LOCAL/pdf" "$BUCKET/pdf/"
else
    echo "[5/5] Skipping pdf/ (use --include-pdfs to sync)"
fi

echo ""
echo "=== SYNC COMPLETE ==="
gsutil du -sh "$BUCKET"
echo ""
echo "Cloud location: $BUCKET"
echo "View: https://console.cloud.google.com/storage/browser/${PROJECT}/references"
