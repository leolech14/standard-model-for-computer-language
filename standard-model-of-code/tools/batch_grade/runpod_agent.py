#!/usr/bin/env python3
"""
RunPod Agent - Fully Automated Batch Grading
============================================

AI-agent accessible system for spinning up RunPod, running batch jobs,
collecting results, and terminating - all via API.

Prerequisites:
    pip install runpod paramiko

Credentials (from Doppler):
    RUNPOD_API_KEY - RunPod API key

Usage:
    # Full automated run (use Doppler to inject credentials)
    doppler run --project ai-tools --config dev -- python runpod_agent.py run

    # Test with 10 repos
    doppler run --project ai-tools --config dev -- python runpod_agent.py run --limit 10

    # Check pod status
    doppler run --project ai-tools --config dev -- python runpod_agent.py status

    # Emergency terminate all pods
    doppler run --project ai-tools --config dev -- python runpod_agent.py terminate-all
"""

import os
import sys
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Get API key from environment (Doppler injects this)
RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY")

# SSH key path - use runpod-specific key if available
SSH_KEY_PATH = Path.home() / ".ssh" / "runpod_ed25519"
SSH_PUB_KEY_PATH = Path.home() / ".ssh" / "runpod_ed25519.pub"

# Fallback to default key if runpod key doesn't exist
if not SSH_KEY_PATH.exists():
    SSH_KEY_PATH = Path.home() / ".ssh" / "id_ed25519"
    SSH_PUB_KEY_PATH = Path.home() / ".ssh" / "id_ed25519.pub"

# Pod configuration
POD_CONFIG = {
    "name": "collider-batch-grade",
    "image_name": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
    "gpu_type_id": "NVIDIA GeForce RTX 4090",  # $0.34/hr, 16 vCPU
    "cloud_type": "COMMUNITY",  # Cheaper than SECURE
    "volume_in_gb": 50,
    "container_disk_in_gb": 50,
    "min_vcpu_count": 16,
    "min_memory_in_gb": 32,
    "ports": "22/tcp",  # SSH
    "volume_mount_path": "/workspace",
}

# Batch job configuration
BATCH_CONFIG = {
    "workers": 32,
    "timeout_per_repo": 180,
    "github_repo": "https://github.com/leolech14/standard-model-of-code.git",
}

# Script to run inside the pod
SETUP_SCRIPT = '''#!/bin/bash
set -e

echo "=== COLLIDER BATCH GRADE - POD SETUP ==="
cd /workspace

# Clone or update repo
if [ -d "collider" ]; then
    cd collider && git pull
else
    git clone {github_repo} collider
    cd collider
fi

# Install dependencies
pip install -q tree-sitter==0.20.4 tree-sitter-python tree-sitter-javascript tree-sitter-go tree-sitter-typescript pyyaml

echo "=== SETUP COMPLETE ==="
'''

RUN_SCRIPT = '''#!/bin/bash
set -e

cd /workspace/collider
echo "=== STARTING BATCH GRADE ==="
python tools/batch_grade/run_batch_local.py --workers {workers} --timeout {timeout} {limit_arg}
echo "=== BATCH GRADE COMPLETE ==="

# Signal completion
touch /workspace/COMPLETE
'''


def get_runpod():
    """Import and configure runpod SDK."""
    try:
        import runpod
    except ImportError:
        print("Installing runpod SDK...")
        subprocess.run([sys.executable, "-m", "pip", "install", "runpod", "paramiko"], check=True)
        import runpod

    if not RUNPOD_API_KEY:
        print("ERROR: RUNPOD_API_KEY not set. Run with Doppler:")
        print("  doppler run --project ai-tools --config dev -- python runpod_agent.py run")
        sys.exit(1)

    runpod.api_key = RUNPOD_API_KEY
    return runpod


def get_ssh_public_key() -> str:
    """Read local SSH public key for injection into pod."""
    if not SSH_PUB_KEY_PATH.exists():
        print(f"SSH public key not found at {SSH_PUB_KEY_PATH}")
        print("Generating new SSH key pair...")
        subprocess.run([
            "ssh-keygen", "-t", "ed25519", "-f", str(SSH_KEY_PATH),
            "-N", "", "-C", "runpod-agent"
        ], check=True)

    return SSH_PUB_KEY_PATH.read_text().strip()


def create_pod(runpod_sdk) -> Dict[str, Any]:
    """Create a new pod for batch processing."""
    print(f"Creating pod: {POD_CONFIG['name']}...")

    # Get SSH public key to inject
    ssh_pub_key = get_ssh_public_key()
    print(f"Using SSH key: {ssh_pub_key[:50]}...")

    pod = runpod_sdk.create_pod(
        name=POD_CONFIG["name"],
        image_name=POD_CONFIG["image_name"],
        gpu_type_id=POD_CONFIG["gpu_type_id"],
        cloud_type=POD_CONFIG["cloud_type"],
        volume_in_gb=POD_CONFIG["volume_in_gb"],
        container_disk_in_gb=POD_CONFIG["container_disk_in_gb"],
        min_vcpu_count=POD_CONFIG["min_vcpu_count"],
        min_memory_in_gb=POD_CONFIG["min_memory_in_gb"],
        ports=POD_CONFIG["ports"],
        volume_mount_path=POD_CONFIG["volume_mount_path"],
        env={
            "PUBLIC_KEY": ssh_pub_key,  # RunPod uses PUBLIC_KEY, not SSH_PUBLIC_KEY
        },
    )

    print(f"Pod created: {pod['id']}")
    return pod


def wait_for_pod_ready(runpod_sdk, pod_id: str, timeout: int = 300) -> Dict[str, Any]:
    """Wait for pod to be ready (RUNNING status with SSH available)."""
    print(f"Waiting for pod {pod_id} to be ready...")
    start = time.time()

    while time.time() - start < timeout:
        pod = runpod_sdk.get_pod(pod_id)
        status = pod.get("desiredStatus", "UNKNOWN")
        runtime = pod.get("runtime") or {}

        # Check for SSH port availability
        ports = runtime.get("ports") or []
        has_ssh = any(p.get("privatePort") == 22 and p.get("ip") for p in ports)

        print(f"  Status: {status}, SSH ready: {has_ssh}")

        if status == "RUNNING" and has_ssh:
            print(f"  Pod ready! Ports: {ports}")
            return pod

        time.sleep(10)

    raise TimeoutError(f"Pod {pod_id} did not become ready in {timeout}s")


def get_ssh_connection_info(pod: Dict) -> tuple[str, int]:
    """Extract SSH host and port from pod info."""
    runtime = pod.get("runtime", {})
    ports = runtime.get("ports", [])

    for port_info in ports:
        if port_info.get("privatePort") == 22:
            ssh_host = port_info.get("ip")
            ssh_port = port_info.get("publicPort")
            if ssh_host and ssh_port:
                return str(ssh_host), int(ssh_port)

    raise ValueError(f"Could not find SSH connection info in pod: {ports}")


def run_ssh_command(pod: Dict, command: str, timeout: int = 3600) -> str:
    """Run command on pod via SSH."""
    import paramiko

    ssh_host, ssh_port = get_ssh_connection_info(pod)
    print(f"Connecting to {ssh_host}:{ssh_port}...")

    # Connect via SSH using private key
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Use private key for authentication
    private_key = paramiko.Ed25519Key.from_private_key_file(str(SSH_KEY_PATH))

    client.connect(
        hostname=ssh_host,
        port=ssh_port,
        username="root",
        pkey=private_key,
        timeout=30,
    )

    print(f"Executing command...")
    _, stdout, stderr = client.exec_command(command, timeout=timeout)

    # Stream output
    output = []
    for line in iter(stdout.readline, ""):
        print(line, end="")
        output.append(line)

    exit_status = stdout.channel.recv_exit_status()
    client.close()

    if exit_status != 0:
        error = stderr.read().decode()
        raise RuntimeError(f"Command failed (exit {exit_status}): {error}")

    return "".join(output)


def download_results(pod: Dict, local_dir: Path) -> Path:
    """Download results from pod via SCP."""
    import paramiko

    ssh_host, ssh_port = get_ssh_connection_info(pod)
    local_dir.mkdir(parents=True, exist_ok=True)

    # Use SCP to download with private key
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.Ed25519Key.from_private_key_file(str(SSH_KEY_PATH))
    client.connect(hostname=ssh_host, port=ssh_port, username="root", pkey=private_key, timeout=30)

    sftp = client.open_sftp()

    # List and download result files
    remote_dir = "/workspace/collider/tools/batch_grade/grades"
    try:
        files = sftp.listdir(remote_dir)
        for f in files:
            if f.endswith(".json"):
                remote_path = f"{remote_dir}/{f}"
                local_path = local_dir / f
                print(f"Downloading: {f}")
                sftp.get(remote_path, str(local_path))
    except FileNotFoundError:
        print(f"No results directory found at {remote_dir}")

    sftp.close()
    client.close()

    return local_dir


def cmd_run(args):
    """Run the full batch grade pipeline."""
    runpod = get_runpod()

    print("=" * 60)
    print("COLLIDER BATCH GRADE - RUNPOD AGENT")
    print("=" * 60)

    pod = None
    try:
        # 1. Create pod
        pod = create_pod(runpod)
        pod_id = pod["id"]

        # 2. Wait for ready
        pod = wait_for_pod_ready(runpod, pod_id)

        # 3. Run setup
        print("\n=== RUNNING SETUP ===")
        setup_cmd = SETUP_SCRIPT.format(github_repo=BATCH_CONFIG["github_repo"])
        run_ssh_command(pod, setup_cmd, timeout=300)

        # 4. Run batch grade
        print("\n=== RUNNING BATCH GRADE ===")
        limit_arg = f"--limit {args.limit}" if args.limit else ""
        run_cmd = RUN_SCRIPT.format(
            workers=args.workers or BATCH_CONFIG["workers"],
            timeout=BATCH_CONFIG["timeout_per_repo"],
            limit_arg=limit_arg,
        )
        run_ssh_command(pod, run_cmd, timeout=7200)  # 2hr max

        # 5. Download results
        print("\n=== DOWNLOADING RESULTS ===")
        results_dir = Path(__file__).parent / "grades" / datetime.now().strftime("%Y%m%d_%H%M%S")
        download_results(pod, results_dir)
        print(f"Results saved to: {results_dir}")

        # 6. Terminate pod
        print("\n=== TERMINATING POD ===")
        runpod.terminate_pod(pod_id)
        print(f"Pod {pod_id} terminated.")

        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: {e}")
        if pod:
            print(f"Pod {pod['id']} may still be running. Check status or terminate manually.")
        raise


def cmd_status(args):
    """Check status of all pods."""
    runpod = get_runpod()

    pods = runpod.get_pods()

    if not pods:
        print("No pods found.")
        return

    print(f"Found {len(pods)} pod(s):\n")
    for pod in pods:
        print(f"  ID: {pod['id']}")
        print(f"  Name: {pod.get('name', 'N/A')}")
        print(f"  Status: {pod.get('desiredStatus', 'UNKNOWN')}")
        print(f"  GPU: {pod.get('machine', {}).get('gpuDisplayName', 'N/A')}")
        print(f"  Cost: ${pod.get('costPerHr', 0):.2f}/hr")
        print()


def cmd_terminate_all(args):
    """Emergency: terminate all pods."""
    runpod = get_runpod()

    pods = runpod.get_pods()

    if not pods:
        print("No pods to terminate.")
        return

    print(f"Terminating {len(pods)} pod(s)...")
    for pod in pods:
        pod_id = pod["id"]
        print(f"  Terminating {pod_id}...")
        runpod.terminate_pod(pod_id)

    print("All pods terminated.")


def main():
    parser = argparse.ArgumentParser(description="RunPod Agent for Collider Batch Grading")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # run command
    run_parser = subparsers.add_parser("run", help="Run full batch grade pipeline")
    run_parser.add_argument("--limit", type=int, help="Limit number of repos (for testing)")
    run_parser.add_argument("--workers", type=int, help="Number of parallel workers")
    run_parser.set_defaults(func=cmd_run)

    # status command
    status_parser = subparsers.add_parser("status", help="Check pod status")
    status_parser.set_defaults(func=cmd_status)

    # terminate-all command
    term_parser = subparsers.add_parser("terminate-all", help="Emergency: terminate all pods")
    term_parser.set_defaults(func=cmd_terminate_all)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
