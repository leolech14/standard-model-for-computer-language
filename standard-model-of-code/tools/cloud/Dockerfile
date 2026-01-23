# Collider Cloud Runner
# Optimized for batch processing of repositories

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Collider source
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -e . \
    && pip install --no-cache-dir pyyaml google-cloud-storage

# Set environment
ENV PYTHONUNBUFFERED=1
ENV COLLIDER_CLOUD=1

# Entry point for single repo analysis
ENTRYPOINT ["python3", "tools/cloud/run_single_repo.py"]
