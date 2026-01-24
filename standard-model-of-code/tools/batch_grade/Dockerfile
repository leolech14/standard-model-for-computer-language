# Collider Batch Grade - GCP Cloud Run Job
# Auto-deletes after completion, results to GCS

FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set memory limits for Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MALLOC_TRIM_THRESHOLD_=100000

WORKDIR /app

# Copy collider source
COPY . /app/collider/

# Install Python deps
RUN pip install --no-cache-dir \
    tree-sitter==0.20.4 \
    tree-sitter-python \
    tree-sitter-javascript \
    tree-sitter-go \
    tree-sitter-typescript \
    pyyaml \
    google-cloud-storage

# Copy batch scripts
COPY tools/batch_grade/run_batch_cloud.py /app/run_batch_cloud.py
COPY tools/batch_grade/repos_999.json /app/repos_999.json

# Run with memory limits
CMD ["python", "-u", "/app/run_batch_cloud.py"]
