#!/usr/bin/env python3
"""
Sync Registry to GCS - Mirror local registry to cloud.

This tool syncs the .agent/registry/ directory to GCS so that
Cloud Functions can access opportunities for auto-boost.

Usage:
    ./sync_registry.py              # Sync all
    ./sync_registry.py --inbox-only # Only sync inbox
    ./sync_registry.py --pull       # Pull from GCS to local
    ./sync_registry.py --diff       # Show diff without syncing

Prerequisites:
    - gcloud auth application-default login
    - GCS bucket exists: gs://elements-archive-2026/
"""

import argparse
import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from google.cloud import storage
except ImportError:
    print("ERROR: google-cloud-storage not installed")
    print("Install with: pip install google-cloud-storage")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
AGENT_DIR = SCRIPT_DIR.parent.parent
REGISTRY_DIR = AGENT_DIR / "registry"
GCS_BUCKET = os.environ.get("GCS_BUCKET", "elements-archive-2026")
GCS_PREFIX = ".agent/registry"

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def get_file_hash(path: Path) -> str:
    """Get MD5 hash of file."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def get_local_files(inbox_only: bool = False) -> dict:
    """Get all local registry files with hashes."""
    files = {}

    if inbox_only:
        patterns = ["inbox/*.yaml"]
    else:
        patterns = ["inbox/*.yaml", "active/*.yaml", "archive/*.yaml", "*.md"]

    for pattern in patterns:
        for path in REGISTRY_DIR.glob(pattern):
            if path.is_file():
                rel_path = path.relative_to(REGISTRY_DIR)
                files[str(rel_path)] = {
                    "path": path,
                    "hash": get_file_hash(path),
                    "size": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime),
                }

    return files


def get_gcs_files(client, inbox_only: bool = False) -> dict:
    """Get all GCS registry files with hashes."""
    bucket = client.bucket(GCS_BUCKET)
    files = {}

    prefix = GCS_PREFIX
    if inbox_only:
        prefix = f"{GCS_PREFIX}/inbox"

    for blob in bucket.list_blobs(prefix=prefix):
        rel_path = blob.name.replace(f"{GCS_PREFIX}/", "")
        if rel_path and (rel_path.endswith(".yaml") or rel_path.endswith(".md")):
            files[rel_path] = {
                "blob": blob,
                "hash": blob.md5_hash,
                "size": blob.size,
                "modified": blob.updated,
            }

    return files


def sync_to_gcs(client, local_files: dict, gcs_files: dict, dry_run: bool = False):
    """Sync local files to GCS."""
    bucket = client.bucket(GCS_BUCKET)

    uploaded = 0
    skipped = 0

    for rel_path, local in local_files.items():
        gcs_path = f"{GCS_PREFIX}/{rel_path}"

        # Check if file exists and is same
        if rel_path in gcs_files:
            # GCS uses base64 MD5, we use hex - just check size for now
            if local["size"] == gcs_files[rel_path]["size"]:
                skipped += 1
                continue

        # Upload
        if dry_run:
            print(f"  {CYAN}[DRY]{NC} Would upload: {rel_path}")
        else:
            blob = bucket.blob(gcs_path)
            blob.upload_from_filename(str(local["path"]))
            print(f"  {GREEN}[UP]{NC} {rel_path}")

        uploaded += 1

    return uploaded, skipped


def sync_from_gcs(client, local_files: dict, gcs_files: dict, dry_run: bool = False):
    """Sync GCS files to local."""
    downloaded = 0
    skipped = 0

    for rel_path, gcs in gcs_files.items():
        local_path = REGISTRY_DIR / rel_path

        # Check if file exists and is same
        if rel_path in local_files:
            if local_files[rel_path]["size"] == gcs["size"]:
                skipped += 1
                continue

        # Download
        local_path.parent.mkdir(parents=True, exist_ok=True)

        if dry_run:
            print(f"  {CYAN}[DRY]{NC} Would download: {rel_path}")
        else:
            gcs["blob"].download_to_filename(str(local_path))
            print(f"  {GREEN}[DOWN]{NC} {rel_path}")

        downloaded += 1

    return downloaded, skipped


def show_diff(local_files: dict, gcs_files: dict):
    """Show diff between local and GCS."""
    local_only = set(local_files.keys()) - set(gcs_files.keys())
    gcs_only = set(gcs_files.keys()) - set(local_files.keys())
    both = set(local_files.keys()) & set(gcs_files.keys())

    print(f"\n{YELLOW}LOCAL ONLY ({len(local_only)}):{NC}")
    for f in sorted(local_only):
        print(f"  + {f}")

    print(f"\n{YELLOW}GCS ONLY ({len(gcs_only)}):{NC}")
    for f in sorted(gcs_only):
        print(f"  - {f}")

    print(f"\n{YELLOW}DIFFERENT ({len(both)}):{NC}")
    for f in sorted(both):
        local_size = local_files[f]["size"]
        gcs_size = gcs_files[f]["size"]
        if local_size != gcs_size:
            print(f"  ~ {f} (local: {local_size}B, gcs: {gcs_size}B)")


def main():
    parser = argparse.ArgumentParser(
        description="Sync registry to/from GCS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--inbox-only", action="store_true",
                        help="Only sync inbox directory")
    parser.add_argument("--pull", action="store_true",
                        help="Pull from GCS to local (default: push)")
    parser.add_argument("--diff", action="store_true",
                        help="Show diff without syncing")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without syncing")

    args = parser.parse_args()

    print(f"\n{YELLOW}REGISTRY SYNC{NC}")
    print("=" * 50)
    print(f"Bucket: gs://{GCS_BUCKET}/{GCS_PREFIX}/")
    print(f"Local: {REGISTRY_DIR}")
    if args.inbox_only:
        print("Mode: inbox only")
    print()

    # Initialize client
    client = storage.Client()

    # Get file lists
    print("Scanning local files...", end=" ", flush=True)
    local_files = get_local_files(args.inbox_only)
    print(f"{len(local_files)} files")

    print("Scanning GCS files...", end=" ", flush=True)
    gcs_files = get_gcs_files(client, args.inbox_only)
    print(f"{len(gcs_files)} files")

    # Show diff
    if args.diff:
        show_diff(local_files, gcs_files)
        return

    print()

    # Sync
    if args.pull:
        print(f"{YELLOW}Pulling from GCS...{NC}")
        downloaded, skipped = sync_from_gcs(client, local_files, gcs_files, args.dry_run)
        print()
        print(f"Downloaded: {downloaded}")
        print(f"Skipped: {skipped}")
    else:
        print(f"{YELLOW}Pushing to GCS...{NC}")
        uploaded, skipped = sync_to_gcs(client, local_files, gcs_files, args.dry_run)
        print()
        print(f"Uploaded: {uploaded}")
        print(f"Skipped: {skipped}")

    print()
    print("=" * 50)
    print(f"{GREEN}Sync complete!{NC}")


if __name__ == "__main__":
    main()
