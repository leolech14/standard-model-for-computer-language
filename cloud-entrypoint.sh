#!/bin/bash
set -e

echo "[Cloud Run] Starting Full-Power Socratic Audit..."

# Create the mirror directory if it doesn't exist
mkdir -p /app/repo_mirror

# Sync latest repository mirror from GCS
# This ensures we are analyzing the latest cloud-synced code, not image-build-time code.
echo "[Cloud Run] Syncing repository mirror from GCS..."
gsutil -m rsync -r gs://elements-archive-2026/repository_mirror/latest/ /app/repo_mirror

# Work inside the mirror
cd /app/repo_mirror

# Create virtual environment if it doesn't exist
if [ ! -d ".tools_venv" ]; then
    echo "[Cloud Run] Creating virtual environment..."
    python3 -m venv .tools_venv
    .tools_venv/bin/pip install --quiet google-genai pyyaml
fi

# Run the Socratic Audit
echo "[Cloud Run] Running Audit..."
# By default we verify the pipeline domain, but this can be overridden by arguments
python3 context-management/tools/ai/analyze.py "$@"

echo "[Cloud Run] Audit complete."
