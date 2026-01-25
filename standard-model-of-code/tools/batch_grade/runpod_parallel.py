#!/usr/bin/env python3
"""
RunPod PARALLEL Agent - 10x Speed with Multiple Pods
====================================================

Splits 999 repos across N pods for parallel processing.

Usage:
    doppler run --project ai-tools --config dev -- python runpod_parallel.py run --pods 10
"""

import os
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import from runpod_agent
from runpod_agent import (
    get_runpod, get_ssh_public_key, POD_CONFIG, BATCH_CONFIG,
    wait_for_pod_ready, run_ssh_command, get_ssh_connection_info,
    SSH_KEY_PATH
)

SCRIPT_DIR = Path(__file__).parent
REPOS_FILE = SCRIPT_DIR / "repos_999.json"

# Lighter setup - skip tmate, faster pip
SETUP_SCRIPT_FAST = '''#!/bin/bash
set -e
cd /workspace
if [ -d "collider" ]; then
    cd collider && git pull --quiet
else
    git clone --depth 1 --quiet {github_repo} collider
    cd collider
fi
cd standard-model-of-code
pip install -q -e . pyyaml 2>/dev/null
echo "READY"
'''

RUN_SCRIPT_CHUNK = '''#!/bin/bash
set -e
cd /workspace/collider/standard-model-of-code
echo "Processing chunk {chunk_id}: repos {start}-{end}"
PYTHONUNBUFFERED=1 python -u tools/batch_grade/run_batch_local.py \
    --workers {workers} \
    --timeout {timeout} \
    --start {start} \
    --end {end} \
    --output /workspace/grades 2>&1
echo "CHUNK {chunk_id} COMPLETE"
'''


def create_pod_fast(runpod_sdk, name_suffix: str):
    """Create a pod with minimal config."""
    ssh_pub_key = get_ssh_public_key()

    pod = runpod_sdk.create_pod(
        name=f"collider-batch-{name_suffix}",
        image_name=POD_CONFIG["image_name"],
        gpu_type_id=POD_CONFIG["gpu_type_id"],
        cloud_type=POD_CONFIG["cloud_type"],
        volume_in_gb=20,  # Smaller volume
        container_disk_in_gb=20,
        min_vcpu_count=16,
        min_memory_in_gb=32,
        ports=POD_CONFIG["ports"],
        volume_mount_path=POD_CONFIG["volume_mount_path"],
        env={"PUBLIC_KEY": ssh_pub_key},
    )
    return pod


def run_chunk_on_pod(runpod_sdk, chunk_id: int, start: int, end: int, workers: int = 16):
    """Run a chunk of repos on a single pod."""
    result = {
        "chunk_id": chunk_id,
        "start": start,
        "end": end,
        "status": "pending",
        "pod_id": None,
        "results_file": None,
        "error": None,
    }

    try:
        # Create pod
        print(f"[Chunk {chunk_id}] Creating pod for repos {start}-{end}...")
        pod = create_pod_fast(runpod_sdk, f"c{chunk_id}")
        pod_id = pod["id"]
        result["pod_id"] = pod_id

        # Wait for ready
        print(f"[Chunk {chunk_id}] Waiting for pod {pod_id}...")
        pod = wait_for_pod_ready(runpod_sdk, pod_id, timeout=180)

        # Setup
        print(f"[Chunk {chunk_id}] Running setup...")
        setup_cmd = SETUP_SCRIPT_FAST.format(github_repo=BATCH_CONFIG["github_repo"])
        run_ssh_command(pod, setup_cmd, timeout=120)

        # Run chunk
        print(f"[Chunk {chunk_id}] Processing repos {start}-{end}...")
        run_cmd = RUN_SCRIPT_CHUNK.format(
            chunk_id=chunk_id,
            start=start,
            end=end,
            workers=workers,
            timeout=120,  # Faster timeout
        )
        output = run_ssh_command(pod, run_cmd, timeout=3600)

        # Download results
        print(f"[Chunk {chunk_id}] Downloading results...")
        import paramiko
        ssh_host, ssh_port = get_ssh_connection_info(pod)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.Ed25519Key.from_private_key_file(str(SSH_KEY_PATH))
        client.connect(hostname=ssh_host, port=ssh_port, username="root", pkey=private_key, timeout=30)

        sftp = client.open_sftp()
        remote_dir = "/workspace/grades"
        local_dir = SCRIPT_DIR / "grades" / f"parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        local_dir.mkdir(parents=True, exist_ok=True)

        for f in sftp.listdir(remote_dir):
            if f.endswith(".json"):
                sftp.get(f"{remote_dir}/{f}", str(local_dir / f"chunk{chunk_id}_{f}"))
                result["results_file"] = str(local_dir / f"chunk{chunk_id}_{f}")

        sftp.close()
        client.close()

        result["status"] = "success"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:200]
        print(f"[Chunk {chunk_id}] ERROR: {e}")

    finally:
        # Terminate pod
        if result.get("pod_id"):
            try:
                print(f"[Chunk {chunk_id}] Terminating pod...")
                runpod_sdk.terminate_pod(result["pod_id"])
            except:
                pass

    return result


def cmd_run(args):
    """Run parallel batch processing."""
    runpod = get_runpod()

    # Load repos
    with open(REPOS_FILE) as f:
        repos = json.load(f)

    total = len(repos) if args.limit == 0 else min(args.limit, len(repos))
    num_pods = args.pods
    chunk_size = (total + num_pods - 1) // num_pods  # Ceiling division

    print("=" * 70)
    print("COLLIDER PARALLEL BATCH - TURBO MODE")
    print("=" * 70)
    print(f"Total repos: {total}")
    print(f"Pods: {num_pods}")
    print(f"Chunk size: ~{chunk_size} repos per pod")
    print(f"Estimated time: {total / (200 * num_pods) * 60:.0f} minutes")
    print(f"Estimated cost: ${0.34 * num_pods * (total / (200 * num_pods)) :.2f}")
    print("=" * 70)

    # Create chunks
    chunks = []
    for i in range(num_pods):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, total)
        if start < total:
            chunks.append((i, start, end))

    print(f"Created {len(chunks)} chunks")

    # Run in parallel
    start_time = datetime.now()
    results = []

    with ThreadPoolExecutor(max_workers=num_pods) as executor:
        futures = {
            executor.submit(run_chunk_on_pod, runpod, chunk_id, start, end, args.workers): chunk_id
            for chunk_id, start, end in chunks
        }

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"[Chunk {result['chunk_id']}] Done: {result['status']}")

    # Summary
    elapsed = (datetime.now() - start_time).total_seconds()
    success = sum(1 for r in results if r["status"] == "success")

    print("\n" + "=" * 70)
    print(f"COMPLETE: {success}/{len(chunks)} chunks succeeded")
    print(f"Time: {elapsed/60:.1f} minutes")
    print("=" * 70)

    # Merge results
    if success > 0:
        print("\nMerging results...")
        all_results = []
        for r in results:
            if r.get("results_file") and Path(r["results_file"]).exists():
                with open(r["results_file"]) as f:
                    data = json.load(f)
                    all_results.extend(data.get("results", []))

        final_file = SCRIPT_DIR / "grades" / f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(final_file, "w") as f:
            json.dump({
                "meta": {
                    "total": len(all_results),
                    "pods": num_pods,
                    "duration_sec": elapsed,
                },
                "results": all_results
            }, f, indent=2)
        print(f"Merged results: {final_file}")


def main():
    parser = argparse.ArgumentParser(description="Parallel RunPod batch grading")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run parallel batch")
    run_parser.add_argument("--pods", type=int, default=10, help="Number of pods")
    run_parser.add_argument("--workers", type=int, default=16, help="Workers per pod")
    run_parser.add_argument("--limit", type=int, default=0, help="Limit total repos")
    run_parser.set_defaults(func=cmd_run)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
