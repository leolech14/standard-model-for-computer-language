#!/usr/bin/env python3
"""
ARCHIVE MODULE
==============
Manages offloading large files to GCS and restoring them.

Usage:
    ./tools/archive/archive.py offload [--dry-run] [--delete]
    ./tools/archive/archive.py restore <archive_id> [<path>]
    ./tools/archive/archive.py list [--remote]
    ./tools/archive/archive.py status

Examples:
    # Preview what would be uploaded
    ./tools/archive/archive.py offload --dry-run

    # Upload to GCS (keep local copies)
    ./tools/archive/archive.py offload

    # Upload and delete local copies
    ./tools/archive/archive.py offload --delete

    # List local manifests
    ./tools/archive/archive.py list

    # List remote archives
    ./tools/archive/archive.py list --remote

    # Restore specific archive
    ./tools/archive/archive.py restore archive_20260118_135934

    # Restore specific path from archive
    ./tools/archive/archive.py restore archive_20260118_135934 standard-model-of-code/output/audit

IMPORTANT: This script requires the .tools_venv virtual environment.
If you get import errors, the script will auto-restart with the correct venv.
"""

import sys
import os
from pathlib import Path

# --- Auto-detect and use correct venv ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
TOOLS_VENV = PROJECT_ROOT / ".tools_venv"
VENV_PYTHON = TOOLS_VENV / "bin" / "python"

def _in_correct_venv():
    """Check if we're running from .tools_venv"""
    return TOOLS_VENV.as_posix() in sys.prefix

if not _in_correct_venv():
    if VENV_PYTHON.exists():
        # Re-execute with correct venv
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)
    else:
        print("=" * 60)
        print("ERROR: Required virtual environment not found!")
        print("=" * 60)
        print(f"Expected: {TOOLS_VENV}")
        print()
        print("To fix, run from PROJECT_elements root:")
        print("  python -m venv .tools_venv")
        print("  source .tools_venv/bin/activate")
        print("  pip install pyyaml")
        print("=" * 60)
        sys.exit(1)

# --- Now safe to import deps (we're in correct venv) ---
import fnmatch
import json
import shutil
import subprocess
from datetime import datetime

import yaml

# Module paths (SCRIPT_DIR and PROJECT_ROOT already defined above)
CONFIG_FILE = SCRIPT_DIR / "config.yaml"
MANIFESTS_DIR = SCRIPT_DIR / "manifests"


def load_config():
    """Load configuration from YAML file."""
    if not CONFIG_FILE.exists():
        print(f"Error: Config file not found: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def run_gcloud(args, check=True, capture=False):
    """Run a gcloud command."""
    cmd = ["gcloud"] + args
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result
    else:
        return subprocess.run(cmd, check=check)


def set_gcloud_account(account):
    """Set the active gcloud account."""
    run_gcloud(["config", "set", "account", account], capture=True)


def get_path_size(path: Path) -> int:
    """Get total size of a path (file or directory) in bytes."""
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for f in path.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def collect_offload_items(config) -> list:
    """Collect all items to offload based on config."""
    items = []
    for pattern in config["offload_paths"]:
        full_path = PROJECT_ROOT / pattern

        # Handle glob patterns
        if "*" in pattern:
            # Expand glob from project root
            parent = PROJECT_ROOT / Path(pattern).parent
            glob_pattern = Path(pattern).name
            if parent.exists():
                for match in parent.glob(glob_pattern):
                    if match.exists():
                        items.append({
                            "path": match,
                            "relative": str(match.relative_to(PROJECT_ROOT)),
                            "size": get_path_size(match),
                            "is_dir": match.is_dir(),
                        })
        elif full_path.exists():
            items.append({
                "path": full_path,
                "relative": pattern,
                "size": get_path_size(full_path),
                "is_dir": full_path.is_dir(),
            })
        else:
            items.append({
                "path": full_path,
                "relative": pattern,
                "size": 0,
                "is_dir": False,
                "missing": True,
            })
    return items


def cmd_offload(args):
    """Offload files to GCS."""
    config = load_config()
    dry_run = "--dry-run" in args
    delete_local = "--delete" in args

    bucket = config["gcloud"]["bucket"]
    account = config["gcloud"]["account"]

    print("=" * 50)
    print("ARCHIVE OFFLOAD")
    print("=" * 50)
    print(f"Bucket:  {bucket}")
    print(f"Account: {account}")
    print(f"Mode:    {'DRY RUN' if dry_run else ('UPLOAD + DELETE' if delete_local else 'UPLOAD ONLY')}")
    print()

    # Set gcloud account
    if not dry_run:
        set_gcloud_account(account)
        # Configure for sequential uploads (avoids multiprocessing bugs)
        run_gcloud(["config", "set", "storage/parallel_composite_upload_enabled", "False"], capture=True)
        run_gcloud(["config", "set", "storage/process_count", "1"], capture=True)
        run_gcloud(["config", "set", "storage/thread_count", "1"], capture=True)

    # Collect items
    items = collect_offload_items(config)

    print("=== FILES TO OFFLOAD ===")
    print()
    total_size = 0
    for item in items:
        if item.get("missing"):
            print(f"  [NOT FOUND] {item['relative']}")
        else:
            size_str = format_size(item["size"])
            print(f"  {size_str:>10}  {item['relative']}")
            total_size += item["size"]
    print()
    print(f"Total: {format_size(total_size)}")
    print()

    if dry_run:
        print("=== DRY RUN - No files uploaded ===")
        print()
        print("To upload: ./tools/archive/archive.py offload")
        print("To upload + delete: ./tools/archive/archive.py offload --delete")
        return

    # Create archive ID
    archive_id = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    archive_dest = f"{bucket}/{archive_id}"

    print(f"=== UPLOADING TO {archive_dest} ===")
    print()

    # Track uploaded items for manifest
    uploaded = []
    errors = []

    for item in items:
        if item.get("missing"):
            continue

        src = item["path"]
        rel = item["relative"]
        dest = f"{archive_dest}/{rel}"

        print(f"Uploading: {rel}")

        try:
            if item["is_dir"]:
                result = run_gcloud(
                    ["storage", "cp", "-r", str(src), dest],
                    check=False,
                    capture=True,
                )
            else:
                # For files, ensure destination is a directory
                result = run_gcloud(
                    ["storage", "cp", str(src), f"{dest}/"],
                    check=False,
                    capture=True,
                )

            if result.returncode == 0:
                print(f"  OK")
                uploaded.append({
                    "path": rel,
                    "size": item["size"],
                    "is_dir": item["is_dir"],
                    "gcs_path": dest,
                })

                # Delete local if requested
                if delete_local:
                    print(f"  Deleting local: {src}")
                    if src.is_dir():
                        shutil.rmtree(src)
                    else:
                        src.unlink()
            else:
                print(f"  ERROR: {result.stderr.strip()}")
                errors.append({"path": rel, "error": result.stderr.strip()})

        except Exception as e:
            print(f"  ERROR: {e}")
            errors.append({"path": rel, "error": str(e)})

        print()

    # Create manifest
    if config["options"].get("create_manifest", True) and uploaded:
        manifest = {
            "archive_id": archive_id,
            "created": datetime.now().isoformat(),
            "bucket": bucket,
            "account": account,
            "total_size": sum(u["size"] for u in uploaded),
            "total_files": len(uploaded),
            "items": uploaded,
            "errors": errors if errors else None,
            "local_deleted": delete_local,
        }

        MANIFESTS_DIR.mkdir(exist_ok=True)
        manifest_file = MANIFESTS_DIR / f"{archive_id}.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"Manifest saved: {manifest_file}")

    print()
    print("=== SUMMARY ===")
    print(f"Uploaded: {len(uploaded)} items ({format_size(sum(u['size'] for u in uploaded))})")
    if errors:
        print(f"Errors: {len(errors)}")
    print(f"Archive: {archive_dest}")
    if delete_local:
        print(f"Local files deleted: Yes")
    print()
    print("To restore:")
    print(f"  ./tools/archive/archive.py restore {archive_id}")


def cmd_restore(args):
    """Restore files from GCS."""
    if len(args) < 1:
        print("Usage: archive.py restore <archive_id> [<path>]")
        print()
        print("Examples:")
        print("  archive.py restore archive_20260118_135934")
        print("  archive.py restore archive_20260118_135934 standard-model-of-code/output/audit")
        sys.exit(1)

    archive_id = args[0]
    specific_path = args[1] if len(args) > 1 else None

    config = load_config()
    bucket = config["gcloud"]["bucket"]
    account = config["gcloud"]["account"]

    # Try to load manifest
    manifest_file = MANIFESTS_DIR / f"{archive_id}.json"
    manifest = None
    if manifest_file.exists():
        with open(manifest_file) as f:
            manifest = json.load(f)

    print("=" * 50)
    print("ARCHIVE RESTORE")
    print("=" * 50)
    print(f"Archive: {archive_id}")
    print(f"Bucket:  {bucket}")
    if manifest:
        print(f"Created: {manifest['created']}")
        print(f"Size:    {format_size(manifest['total_size'])}")
    print()

    set_gcloud_account(account)

    if specific_path:
        # Restore specific path
        src = f"{bucket}/{archive_id}/{specific_path}"
        dest = PROJECT_ROOT / specific_path

        print(f"Restoring: {specific_path}")
        print(f"  From: {src}")
        print(f"  To:   {dest}")

        dest.parent.mkdir(parents=True, exist_ok=True)

        result = run_gcloud(
            ["storage", "cp", "-r", src, str(dest.parent) + "/"],
            check=False,
            capture=True,
        )

        if result.returncode == 0:
            print("  OK")
        else:
            print(f"  ERROR: {result.stderr.strip()}")
    else:
        # Restore all items from manifest
        if not manifest:
            print("No manifest found. Listing remote contents...")
            result = run_gcloud(
                ["storage", "ls", f"{bucket}/{archive_id}/"],
                capture=True,
            )
            print(result.stdout)
            print()
            print("Specify a path to restore:")
            print(f"  ./tools/archive/archive.py restore {archive_id} <path>")
            return

        print("Restoring all items from manifest:")
        print()

        for item in manifest["items"]:
            rel = item["path"]
            src = item["gcs_path"]
            dest = PROJECT_ROOT / rel

            print(f"Restoring: {rel}")
            dest.parent.mkdir(parents=True, exist_ok=True)

            if item["is_dir"]:
                result = run_gcloud(
                    ["storage", "cp", "-r", src, str(dest.parent) + "/"],
                    check=False,
                    capture=True,
                )
            else:
                result = run_gcloud(
                    ["storage", "cp", src, str(dest)],
                    check=False,
                    capture=True,
                )

            if result.returncode == 0:
                print("  OK")
            else:
                print(f"  ERROR: {result.stderr.strip()}")

    print()
    print("Restore complete.")


def cmd_list(args):
    """List archives."""
    config = load_config()
    remote = "--remote" in args

    if remote:
        bucket = config["gcloud"]["bucket"]
        account = config["gcloud"]["account"]

        print("=== REMOTE ARCHIVES ===")
        print(f"Bucket: {bucket}")
        print()

        set_gcloud_account(account)
        result = run_gcloud(["storage", "ls", f"{bucket}/"], capture=True)

        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line:
                    archive_name = line.replace(bucket + "/", "").rstrip("/")
                    print(f"  {archive_name}")
        else:
            print(f"Error: {result.stderr}")
    else:
        print("=== LOCAL MANIFESTS ===")
        print()

        if not MANIFESTS_DIR.exists():
            print("No manifests found.")
            return

        manifests = sorted(MANIFESTS_DIR.glob("*.json"), reverse=True)
        if not manifests:
            print("No manifests found.")
            return

        for mf in manifests:
            with open(mf) as f:
                m = json.load(f)
            deleted_str = " [local deleted]" if m.get("local_deleted") else ""
            print(f"  {m['archive_id']}")
            print(f"    Created: {m['created'][:19]}")
            print(f"    Size:    {format_size(m['total_size'])}")
            print(f"    Items:   {m['total_files']}{deleted_str}")
            print()

    print()
    print("To restore: ./tools/archive/archive.py restore <archive_id>")



def get_gitignore_rules(root_path):
    """Load gitignore rules or defaults."""
    rules = []
    # Always ignore common artifacts
    rules.extend([".git", ".DS_Store", "__pycache__", "venv", ".venv", "node_modules", "*.pyc"])
    
    gitignore = root_path / ".gitignore"
    if gitignore.exists():
        with open(gitignore) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    rules.append(line)
    return rules


def get_project_files(root_path):
    """Get list of files to mirror (git or fallback)."""
    # Try git first
    try:
        if (root_path / ".git").exists():
            res = subprocess.run(
                ["git", "ls-files"], 
                cwd=root_path, 
                capture_output=True, 
                text=True, 
                check=True
            )
            files = [f for f in res.stdout.splitlines() if f.strip()]
            if files:
                return [(root_path / f, f) for f in files]
    except Exception:
        pass
    
    # Fallback walker
    print("Notice: Using fallback file discovery (non-git method).")
    rules = get_gitignore_rules(root_path)
    file_list = []
    
    for r, d, f in os.walk(root_path):
        # Filter directories in-place
        d[:] = [x for x in d if not any(fnmatch.fnmatch(x, pat.rstrip("/")) for pat in rules)]
        
        for filename in f:
            if not any(fnmatch.fnmatch(filename, pat) for pat in rules):
                full = Path(r) / filename
                rel = str(full.relative_to(root_path))
                file_list.append((full, rel))
    return file_list


def cmd_mirror(args):
    """Mirror repository to GCS.

    Options:
        --dry-run      Preview changes without uploading
        --no-registry  Skip auto-generating registry after mirror
    """
    config = load_config()
    dry_run = "--dry-run" in args
    skip_registry = "--no-registry" in args

    if "mirror" not in config:
        print("Error: 'mirror' section missing in config.yaml")
        return

    bucket = config["mirror"]["bucket"]
    prefix = config["mirror"]["prefix"]
    remote_base = f"{bucket}/{prefix}/latest"
    account = config["gcloud"]["account"]

    print("=" * 50)
    print("REPOSITORY MIRROR")
    print("=" * 50)
    print(f"Target:  {remote_base}")
    print(f"Account: {account}")
    print(f"Mode:    {'DRY RUN' if dry_run else 'SYNC'}")
    print()

    if not dry_run:
        set_gcloud_account(account)

    # 1. Local State
    print("Scanning local files...")
    local_files = {} # relative -> {path, size}
    for full_path, rel_path in get_project_files(PROJECT_ROOT):
        local_files[rel_path] = {
            "path": full_path,
            "size": get_path_size(full_path)
        }
    print(f"Found {len(local_files)} local files.")

    # 2. Remote State
    print("Scanning remote files...")
    remote_files = {} # relative -> size
    try:
        # Use recursive long listing
        res = run_gcloud(["storage", "ls", "-l", "-r", f"{remote_base}/"], capture=True)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                parts = line.split()
                # Expected: SIZE ... gs://...
                if len(parts) >= 3 and "gs://" in line:
                    try:
                        # Find the gs:// part
                        url_part = next(p for p in parts if p.startswith("gs://"))
                        size_part = parts[0] # Usually first
                        
                        size = int(size_part)
                        rel = url_part.replace(f"{remote_base}/", "")
                        remote_files[rel] = size
                    except (ValueError, StopIteration):
                        pass
    except Exception as e:
        print(f"Warning: Could not list remote files: {e}")

    print(f"Found {len(remote_files)} remote files.")
    print()

    # 3. Diff
    to_upload = []
    to_delete = []

    for rel, info in local_files.items():
        if rel not in remote_files or remote_files[rel] != info["size"]:
            to_upload.append(info)
    
    for rel in remote_files:
        if rel not in local_files:
            to_delete.append(rel)

    print(f"To Upload: {len(to_upload)} files")
    print(f"To Delete: {len(to_delete)} files")
    print()

    if dry_run:
        return

    # 4. Execute
    # Deletes
    if to_delete:
        print("Deleting removed files...")
        batch_size = 100
        for i in range(0, len(to_delete), batch_size):
            batch = to_delete[i:i+batch_size]
            urls = [f"{remote_base}/{r}" for r in batch]
            print(f"Deleting batch {i}-{i+len(batch)}...")
            # Using stdin for bulk delete if many? Just normal args for now.
            run_gcloud(["storage", "rm"] + urls, check=False)
    
    # Uploads
    if to_upload:
        print(f"Uploading {len(to_upload)} files...")
        
        # Group by directory to minimize gcloud calls
        from collections import defaultdict
        uploads_by_dir = defaultdict(list)
        
        for info in to_upload:
            src = info["path"]
            rel_path = str(src.relative_to(PROJECT_ROOT))
            
            # Group by remote parent directory
            parent_rel = str(Path(rel_path).parent)
            if parent_rel == ".":
                parent_rel = ""
            
            remote_dir = f"{remote_base}/{parent_rel}" if parent_rel else f"{remote_base}"
            uploads_by_dir[remote_dir].append(str(src))

        # Execute batched uploads
        total_batches = 0
        for files in uploads_by_dir.values():
            total_batches += (len(files) + 49) // 50

        current_batch = 0
        for r_dir, files in uploads_by_dir.items():
            # Batch to avoid command line length limits
            BATCH_SIZE = 50
            for j in range(0, len(files), BATCH_SIZE):
                batch = files[j:j+BATCH_SIZE]
                current_batch += 1
                
                # Progress
                if current_batch % 5 == 0 or current_batch == 1:
                     # Show a concise progress (last part of dir)
                     dir_name = r_dir.split('/')[-1] if r_dir.split('/')[-1] else 'root'
                     if dir_name == "latest": dir_name = "root"
                     print(f"Batch {current_batch}/{total_batches}: Uploading {len(batch)} files to .../{dir_name}")

                # Ensure dest dir has trailing slash
                dest = r_dir if r_dir.endswith("/") else f"{r_dir}/"
                run_gcloud(["storage", "cp"] + batch + [dest], check=False)

    print()
    print("Mirror complete.")

    # Auto-generate registry after mirror (unless --no-registry)
    if not skip_registry:
        generate_registry(bucket, prefix, account)
    else:
        print("Skipping registry generation (--no-registry)")



def generate_registry(bucket: str, prefix: str, account: str):
    """Generate and upload the Master Registry."""
    print("=" * 50)
    print("GENERATING REGISTRY")
    print("=" * 50)
    
    registry_dir = PROJECT_ROOT / "context-management/registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry_file = registry_dir / "REGISTRY.json"
    report_file = registry_dir / "REGISTRY_REPORT.md"
    
    remote_base = f"{bucket}/{prefix}/latest"
    
    # 1. Scan Local
    print("Scanning local state...")
    local_map = {rel: info for full, rel in get_project_files(PROJECT_ROOT) for info in [{"path": str(full), "size": get_path_size(full)}]}
    
    # 2. Scan Remote
    print("Scanning remote state...")
    remote_map = {}
    try:
        res = run_gcloud(["storage", "ls", "-l", "-r", f"{remote_base}/"], capture=True)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 3 and "gs://" in line:
                    try:
                        url_part = next(p for p in parts if p.startswith("gs://"))
                        size_part = parts[0]
                        rel = url_part.replace(f"{remote_base}/", "")
                        remote_map[rel] = {"uri": url_part, "size": int(size_part)}
                    except: pass
    except Exception as e:
        print(f"Warning: Remote scan failed: {e}")

    # 3. Build Registry
    all_files = sorted(set(local_map.keys()) | set(remote_map.keys()))
    
    registry_data = {
        "generated_at": datetime.now().isoformat(),
        "stats": {
            "total_files": len(all_files),
            "local_only": 0,
            "cloud_only": 0,
            "synced": 0
        },
        "files": {}
    }
    
    report_lines = ["# Master File Registry", f"", f"**Generated At**: {registry_data['generated_at']}", "", "| Status | File | Local Size | Cloud Size |", "|---|---|---|---|"]
    
    for f in all_files:
        l_info = local_map.get(f)
        r_info = remote_map.get(f)
        
        status = "SYNCED"
        if not l_info: status = "CLOUD_ONLY"
        elif not r_info: status = "LOCAL_ONLY"
        elif l_info["size"] != r_info["size"]: status = "DRIFT_MODIFIED"
        
        # Stats
        if status == "SYNCED": registry_data["stats"]["synced"] += 1
        if status == "LOCAL_ONLY": registry_data["stats"]["local_only"] += 1
        if status == "CLOUD_ONLY": registry_data["stats"]["cloud_only"] += 1
        
        registry_data["files"][f] = {
            "status": status,
            "local_path": l_info["path"] if l_info else None,
            "cloud_uri": r_info["uri"] if r_info else None,
            "local_size": l_info["size"] if l_info else 0,
            "cloud_size": r_info["size"] if r_info else 0
        }
        
        # Add to report (limit to 500 lines to keep readable)
        if len(report_lines) < 500:
             report_lines.append(f"| {status} | `{f}` | {l_info['size'] if l_info else '-'} | {r_info['size'] if r_info else '-'} |")

    # 4. Save & Upload
    with open(registry_file, "w") as f:
        json.dump(registry_data, f, indent=2)
        
    with open(report_file, "w") as f:
        f.write("\n".join(report_lines))
        
    print(f"Registry Saved: {registry_file}")
    
    # Upload Registry itself
    run_gcloud(["storage", "cp", str(registry_file), f"{bucket}/{prefix}/REGISTRY.json"], check=False)
    run_gcloud(["storage", "cp", str(report_file), f"{bucket}/{prefix}/REGISTRY_REPORT.md"], check=False)
    print("Registry Uploaded to Cloud.")


def cmd_registry(args):
    """Manually generate registry."""
    config = load_config()
    bucket = config["mirror"]["bucket"]
    prefix = config["mirror"]["prefix"]
    account = config["gcloud"]["account"]
    set_gcloud_account(account)
    generate_registry(bucket, prefix, account)

    """Show current offload status."""
    config = load_config()

    print("=== ARCHIVE STATUS ===")
    print()

    # Check what's currently offloadable
    items = collect_offload_items(config)
    existing = [i for i in items if not i.get("missing")]
    total_size = sum(i["size"] for i in existing)

    print("Current offloadable items:")
    for item in items:
        if item.get("missing"):
            print(f"  [MISSING] {item['relative']}")
        else:
            print(f"  {format_size(item['size']):>10}  {item['relative']}")

    print()
    print(f"Total offloadable: {format_size(total_size)}")
    print()

    # Check manifests
    if MANIFESTS_DIR.exists():
        manifests = list(MANIFESTS_DIR.glob("*.json"))
        if manifests:
            total_archived = 0
            for mf in manifests:
                with open(mf) as f:
                    m = json.load(f)
                total_archived += m["total_size"]
            print(f"Total archived (from {len(manifests)} archives): {format_size(total_archived)}")

    print()
    print("Commands:")
    print("  offload --dry-run  Preview what would be uploaded")
    print("  offload            Upload to GCS")
    print("  offload --delete   Upload and delete local")
    print("  list               Show local manifests")
    print("  list --remote      Show remote archives")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "offload":
        cmd_offload(args)
    elif cmd == "mirror":
        cmd_mirror(args)
    elif cmd == "restore":
        cmd_restore(args)
    elif cmd == "list":
        cmd_list(args)
    elif cmd == "status":
        cmd_status(args)
    elif cmd == "registry":
        cmd_registry(args)
    elif cmd in ["-h", "--help", "help"]:
        print(__doc__)
    else:
        print(f"Unknown command: {cmd}")
        print()
        print("Commands: offload, mirror, restore, list, status")
        sys.exit(1)


if __name__ == "__main__":
    main()
