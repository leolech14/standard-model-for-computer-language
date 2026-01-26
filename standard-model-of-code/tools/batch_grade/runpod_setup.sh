#!/bin/bash
# RunPod VM setup for Collider batch grading
# Run this INSIDE the RunPod pod after SSH'ing in

set -e

echo "=============================================="
echo "COLLIDER BATCH GRADE - RUNPOD SETUP"
echo "=============================================="

# Install system deps
apt-get update && apt-get install -y git python3-pip python3-venv

# Clone collider
cd /workspace
git clone https://github.com/anthropics/standard-model-of-code.git collider 2>/dev/null || \
    (cd collider && git pull)

cd /workspace/collider

# Create venv and install deps
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install \
    tree-sitter==0.20.4 \
    tree-sitter-python \
    tree-sitter-javascript \
    tree-sitter-go \
    tree-sitter-typescript \
    pyyaml \
    requests

# Copy repos list
cp tools/batch_grade/repos_999.json /workspace/repos_999.json

echo ""
echo "=============================================="
echo "SETUP COMPLETE"
echo "=============================================="
echo ""
echo "To run batch grade:"
echo "  cd /workspace/collider"
echo "  source .venv/bin/activate"
echo "  python tools/batch_grade/run_batch_local.py"
echo ""
