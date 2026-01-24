#!/usr/bin/env python3
"""
Cloud-optimized batch grading for GCP Cloud Run Jobs.

Architecture (validated 2026-01-24):
- Task sharding: Uses CLOUD_RUN_TASK_INDEX/COUNT for striping pattern
- Process isolation: start_new_session=True with process group kill on timeout
- Memory-safe: Explicit cleanup, gc.collect() between repos
- GCS output: Per-task files to avoid write contention

Environment variables (Cloud Run Jobs):
- CLOUD_RUN_TASK_INDEX: This task's index (0-based)
- CLOUD_RUN_TASK_COUNT: Total number of tasks
- GCS_BUCKET: Output bucket (default: elements-archive-2026)
- WORKERS: Parallel workers within this task (default: 4)
- MAX_REPO_SIZE_MB: Skip repos larger than this (default: 500)
- TIMEOUT_PER_REPO: Seconds per repo (default: 300)
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
import gc
import signal
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError
from typing import Optional, List

# GCS
try:
    from google.cloud import storage
    HAS_GCS = True
except ImportError:
    HAS_GCS = False
    print("WARNING: google-cloud-storage not installed, will save locally")

# Cloud Run Jobs task sharding
TASK_INDEX = int(os.environ.get("CLOUD_RUN_TASK_INDEX", "0"))
TASK_COUNT = int(os.environ.get("CLOUD_RUN_TASK_COUNT", "1"))

# Stable run ID: CLOUD_RUN_EXECUTION is guaranteed same across all tasks in one execution
# Fallback to RUN_ID env var or timestamp for local testing
RUN_ID = (
    os.environ.get("RUN_ID") or
    os.environ.get("CLOUD_RUN_EXECUTION") or
    datetime.now().strftime("%Y%m%dT%H%M%SZ")
)

# Config from env
GCS_BUCKET = os.environ.get("GCS_BUCKET", "elements-archive-2026")
WORKERS = int(os.environ.get("WORKERS", "4"))  # Per task, not total
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "25"))  # Flush to GCS every N repos
MAX_REPO_SIZE_MB = int(os.environ.get("MAX_REPO_SIZE_MB", "500"))
TIMEOUT_PER_REPO = int(os.environ.get("TIMEOUT_PER_REPO", "300"))

COLLIDER_ROOT = Path("/app/collider")
REPOS_FILE = Path("/app/repos_999.json")


def shard_repos(repos: List[dict], task_index: int, task_count: int) -> List[dict]:
    """
    Striping pattern: each task processes repos[task_index::task_count]

    Example with 999 repos and 20 tasks:
    - Task 0: repos[0, 20, 40, ...]  = ~50 repos
    - Task 1: repos[1, 21, 41, ...]  = ~50 repos
    - Task 19: repos[19, 39, 59, ...] = ~50 repos
    """
    return repos[task_index::task_count]


class GracefulKiller:
    """Handle SIGTERM for graceful shutdown."""
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        print("\n[SHUTDOWN] Graceful shutdown requested...")
        self.kill_now = True


def upload_to_gcs(local_path: Path, gcs_path: str) -> bool:
    """Upload file to GCS bucket."""
    if not HAS_GCS:
        return False

    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(str(local_path))
        print(f"[GCS] Uploaded: gs://{GCS_BUCKET}/{gcs_path}")
        return True
    except Exception as e:
        print(f"[GCS] Upload failed: {e}")
        return False


def grade_repo(repo: dict, work_dir: Path) -> dict:
    """Grade a single repo with memory safety."""
    name = repo["name"]
    url = repo["url"]
    size_kb = repo.get("size_kb", 0)

    result = {
        "name": name,
        "url": url,
        "language": repo.get("language"),
        "stars": repo.get("stars"),
        "size_kb": size_kb,
        "status": "pending",
        "grade": None,
        "health_index": None,
        "error": None,
        "duration_sec": None
    }

    # Skip large repos
    if size_kb > MAX_REPO_SIZE_MB * 1024:
        result["status"] = "skipped_too_large"
        result["error"] = f"Size {size_kb/1024:.0f}MB > {MAX_REPO_SIZE_MB}MB limit"
        return result

    repo_dir = work_dir / name.replace("/", "_")
    start = datetime.now()

    try:
        # Clone (shallow, single branch)
        # Use start_new_session=True for process group isolation
        clone_cmd = [
            "git", "clone",
            "--depth", "1",
            "--single-branch",
            "--quiet",
            url,
            str(repo_dir)
        ]
        clone_proc = subprocess.Popen(
            clone_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True  # Process group isolation
        )
        try:
            _, clone_stderr = clone_proc.communicate(timeout=60)
            if clone_proc.returncode != 0:
                result["status"] = "clone_failed"
                result["error"] = clone_stderr[:200]
                return result
        except subprocess.TimeoutExpired:
            # Kill entire process group
            os.killpg(os.getpgid(clone_proc.pid), signal.SIGKILL)
            clone_proc.wait()
            result["status"] = "clone_timeout"
            result["error"] = "Clone timed out after 60s"
            return result

        # Grade with process group isolation for clean timeout kill
        grade_cmd = [
            sys.executable,
            str(COLLIDER_ROOT / "cli.py"),
            "grade",
            str(repo_dir),
            "--json"
        ]
        grade_proc = subprocess.Popen(
            grade_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(COLLIDER_ROOT),
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            start_new_session=True  # Process group isolation
        )
        try:
            grade_stdout, grade_stderr = grade_proc.communicate(timeout=TIMEOUT_PER_REPO)
            if grade_proc.returncode != 0:
                result["status"] = "grade_failed"
                result["error"] = grade_stderr[:200]
                return result
        except subprocess.TimeoutExpired:
            # Kill entire process group (including any child processes)
            os.killpg(os.getpgid(grade_proc.pid), signal.SIGKILL)
            grade_proc.wait()
            result["status"] = "timeout"
            result["error"] = f"Exceeded {TIMEOUT_PER_REPO}s timeout (killed process group)"
            return result

        # Parse JSON from grade output
        stdout = grade_stdout
        json_start = stdout.find('{\n  "path"')
        if json_start == -1:
            json_start = stdout.find('{')

        if json_start >= 0:
            brace_count = 0
            json_end = json_start
            for i, char in enumerate(stdout[json_start:], json_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break

            json_str = stdout[json_start:json_end]
            grade_data = json.loads(json_str) if json_str else None
        else:
            grade_data = None

        if grade_data:
            result["status"] = "success"
            result["grade"] = grade_data.get("grade")
            result["health_index"] = grade_data.get("health_index")
            result["component_scores"] = grade_data.get("component_scores")
            result["nodes"] = grade_data.get("nodes")
            result["edges"] = grade_data.get("edges")
            result["betti"] = grade_data.get("betti")
        else:
            result["status"] = "parse_failed"
            result["error"] = "Could not parse JSON output"

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = f"Exceeded {TIMEOUT_PER_REPO}s timeout"
    except json.JSONDecodeError as e:
        result["status"] = "json_error"
        result["error"] = str(e)[:200]
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:200]
    finally:
        # CRITICAL: Clean up repo directory immediately
        if repo_dir.exists():
            shutil.rmtree(repo_dir, ignore_errors=True)

        result["duration_sec"] = round((datetime.now() - start).total_seconds(), 1)

        # Force garbage collection
        gc.collect()

    return result


def main():
    killer = GracefulKiller()

    print("=" * 60)
    print("COLLIDER BATCH GRADE - CLOUD RUN JOBS")
    print("=" * 60)
    print(f"Run ID: {RUN_ID}")
    print(f"Task: {TASK_INDEX + 1}/{TASK_COUNT}")  # 1-indexed for humans
    print(f"Workers per task: {WORKERS}")
    print(f"Batch flush size: {BATCH_SIZE}")
    print(f"Max repo size: {MAX_REPO_SIZE_MB}MB")
    print(f"Timeout per repo: {TIMEOUT_PER_REPO}s")
    print(f"GCS output: gs://{GCS_BUCKET}/grades/{RUN_ID}/")
    print("=" * 60)

    # Load repos
    if not REPOS_FILE.exists():
        print(f"ERROR: Repos file not found: {REPOS_FILE}")
        sys.exit(1)

    with open(REPOS_FILE) as f:
        all_repos = json.load(f)

    # Shard repos using striping pattern: repos[task_index::task_count]
    repos = shard_repos(all_repos, TASK_INDEX, TASK_COUNT)
    print(f"Total repos: {len(all_repos)}")
    print(f"This task's shard: {len(repos)} repos (indices [{TASK_INDEX}::{TASK_COUNT}])")

    # Create work directory
    work_dir = Path(tempfile.mkdtemp(prefix="collider_batch_"))
    print(f"Work dir: {work_dir}")

    # Results
    all_results = []
    success = 0
    failed = 0
    start_time = datetime.now()

    try:
        with ProcessPoolExecutor(max_workers=WORKERS) as executor:
            futures = {
                executor.submit(grade_repo, repo, work_dir): repo
                for repo in repos
            }

            for i, future in enumerate(as_completed(futures), 1):
                if killer.kill_now:
                    print("[SHUTDOWN] Stopping gracefully...")
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

                try:
                    result = future.result(timeout=TIMEOUT_PER_REPO + 60)
                except TimeoutError:
                    repo = futures[future]
                    result = {
                        "name": repo["name"],
                        "status": "future_timeout",
                        "error": "Future timed out"
                    }
                except Exception as e:
                    repo = futures[future]
                    result = {
                        "name": repo["name"],
                        "status": "future_error",
                        "error": str(e)[:200]
                    }

                all_results.append(result)

                if result.get("status") == "success":
                    success += 1
                    marker = "+"
                else:
                    failed += 1
                    marker = "x"

                elapsed = (datetime.now() - start_time).total_seconds()
                rate = i / elapsed * 3600 if elapsed > 0 else 0
                eta_min = (len(repos) - i) / (rate / 60) if rate > 0 else 0

                grade_str = result.get('grade') or '-'
                print(f"[{i:4d}/{len(repos)}] {marker} {result.get('name', '?')[:35]:35} "
                      f"| {result.get('status', '?')[:12]:12} | {grade_str} "
                      f"| {rate:.0f}/hr | ETA {eta_min:.0f}m")

                # Batch flush to GCS (per-task files avoid write contention)
                if i % BATCH_SIZE == 0:
                    batch_file = work_dir / f"batch_{i}.json"
                    with open(batch_file, "w") as f:
                        json.dump(all_results[-BATCH_SIZE:], f)
                    upload_to_gcs(batch_file, f"grades/{RUN_ID}/task-{TASK_INDEX:03d}/batch_{i:04d}.json")
                    batch_file.unlink()
                    gc.collect()

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Saving partial results...")

    # Final summary
    total_time = (datetime.now() - start_time).total_seconds()

    print("\n" + "=" * 60)
    print(f"COMPLETE: {success}/{len(all_results)} succeeded, {failed} failed")
    print(f"Time: {total_time/60:.1f} minutes")
    print(f"Rate: {len(all_results)/total_time*3600:.0f} repos/hour" if total_time > 0 else "")

    # Grade distribution
    grades = {}
    for r in all_results:
        g = r.get("grade") or "FAIL"
        grades[g] = grades.get(g, 0) + 1
    print(f"Grades: {dict(sorted(grades.items()))}")

    # Save final results (per-task to avoid GCS write contention)
    final_output = {
        "meta": {
            "run_id": RUN_ID,
            "task_index": TASK_INDEX,
            "task_count": TASK_COUNT,
            "shard_size": len(repos),
            "processed": len(all_results),
            "success": success,
            "failed": failed,
            "duration_sec": round(total_time, 1),
            "workers": WORKERS,
            "gcs_bucket": GCS_BUCKET
        },
        "grade_distribution": grades,
        "results": all_results
    }

    # Per-task output file: task-{index}.json for easy aggregation
    final_file = work_dir / f"task-{TASK_INDEX:03d}.json"
    with open(final_file, "w") as f:
        json.dump(final_output, f, indent=2)

    # Upload final results (per-task file avoids write contention)
    # All tasks use same RUN_ID (from CLOUD_RUN_EXECUTION) → single run directory
    gcs_path = f"grades/{RUN_ID}/task-{TASK_INDEX:03d}.json"
    if upload_to_gcs(final_file, gcs_path):
        print(f"\n[SUCCESS] Results: gs://{GCS_BUCKET}/{gcs_path}")
    else:
        # Fallback: print to stdout for Cloud Run logs
        print("\n[FALLBACK] Final results (GCS upload failed):")
        print(json.dumps(final_output["meta"], indent=2))

    # Cleanup
    print("\n[CLEANUP] Removing work directory...")
    shutil.rmtree(work_dir, ignore_errors=True)
    gc.collect()

    print("[DONE] Job complete. Container will auto-terminate.")
    sys.exit(0 if success > 0 else 1)


if __name__ == "__main__":
    main()
