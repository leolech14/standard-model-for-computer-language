#!/usr/bin/env python3
"""
RunPod/Local VM batch grading - TURBO MODE
Single powerful machine, maximum parallelism.

Usage:
    python run_batch_local.py                    # Default: 32 workers
    python run_batch_local.py --workers 64       # More workers
    python run_batch_local.py --limit 100        # Test with 100 repos
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
import argparse
import signal
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Optional

# Config
SCRIPT_DIR = Path(__file__).parent
COLLIDER_ROOT = SCRIPT_DIR.parent.parent
REPOS_FILE = SCRIPT_DIR / "repos_999.json"
OUTPUT_DIR = Path("/workspace/grades") if Path("/workspace").exists() else SCRIPT_DIR / "grades"

# Defaults for RunPod (typically 16-48 vCPU available)
DEFAULT_WORKERS = 32
DEFAULT_TIMEOUT = 180  # 3 min per repo
MAX_REPO_SIZE_MB = 500


class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    def exit_gracefully(self, *args):
        print("\n[SHUTDOWN] Graceful shutdown requested...")
        self.kill_now = True


def grade_repo(args: tuple) -> dict:
    """Grade a single repo. Args passed as tuple for multiprocessing."""
    repo, work_dir, timeout = args
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
        # Clone (shallow)
        clone_result = subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch", "--quiet", url, str(repo_dir)],
            capture_output=True, text=True, timeout=60
        )
        if clone_result.returncode != 0:
            result["status"] = "clone_failed"
            result["error"] = clone_result.stderr[:200]
            return result

        # Grade
        grade_result = subprocess.run(
            [sys.executable, str(COLLIDER_ROOT / "cli.py"), "grade", str(repo_dir), "--json"],
            capture_output=True, text=True, timeout=timeout, cwd=str(COLLIDER_ROOT)
        )

        if grade_result.returncode != 0:
            result["status"] = "grade_failed"
            result["error"] = grade_result.stderr[:200]
            return result

        # Parse JSON
        stdout = grade_result.stdout
        json_start = stdout.find('{')
        if json_start >= 0:
            brace_count = 0
            json_end = json_start
            for i, char in enumerate(stdout[json_start:], json_start):
                if char == '{': brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break
            grade_data = json.loads(stdout[json_start:json_end])
            result["status"] = "success"
            result["grade"] = grade_data.get("grade")
            result["health_index"] = grade_data.get("health_index")
            result["component_scores"] = grade_data.get("component_scores")
            result["nodes"] = grade_data.get("nodes")
            result["edges"] = grade_data.get("edges")
        else:
            result["status"] = "parse_failed"
            result["error"] = "No JSON in output"

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = f"Exceeded {timeout}s"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:200]
    finally:
        if repo_dir.exists():
            shutil.rmtree(repo_dir, ignore_errors=True)
        result["duration_sec"] = round((datetime.now() - start).total_seconds(), 1)

    return result


def main():
    parser = argparse.ArgumentParser(description="Batch grade repos - TURBO MODE")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Parallel workers")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout per repo (seconds)")
    parser.add_argument("--limit", type=int, default=0, help="Limit repos (0 = all)")
    parser.add_argument("--output", type=str, default=str(OUTPUT_DIR), help="Output directory")
    args = parser.parse_args()

    killer = GracefulKiller()

    print("=" * 70)
    print("COLLIDER BATCH GRADE - TURBO MODE (RunPod/Local)")
    print("=" * 70)
    print(f"Workers: {args.workers}")
    print(f"Timeout: {args.timeout}s per repo")
    print(f"Output: {args.output}")
    print("=" * 70)

    # Load repos
    with open(REPOS_FILE) as f:
        repos = json.load(f)

    if args.limit > 0:
        repos = repos[:args.limit]
        print(f"LIMITED to {args.limit} repos (testing mode)")

    print(f"Processing {len(repos)} repos...")

    # Create work and output dirs
    work_dir = Path(tempfile.mkdtemp(prefix="collider_batch_"))
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Process
    all_results = []
    success = failed = 0
    start_time = datetime.now()

    # Prepare args for multiprocessing
    task_args = [(repo, work_dir, args.timeout) for repo in repos]

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(grade_repo, arg): arg[0] for arg in task_args}

        for i, future in enumerate(as_completed(futures), 1):
            if killer.kill_now:
                print("[SHUTDOWN] Stopping...")
                executor.shutdown(wait=False, cancel_futures=True)
                break

            try:
                result = future.result(timeout=args.timeout + 30)
            except Exception as e:
                repo = futures[future]
                result = {"name": repo["name"], "status": "future_error", "error": str(e)[:100]}

            all_results.append(result)

            if result.get("status") == "success":
                success += 1
                marker = "+"
            else:
                failed += 1
                marker = "x"

            elapsed = (datetime.now() - start_time).total_seconds()
            rate = i / elapsed * 3600 if elapsed > 0 else 0
            eta = (len(repos) - i) / (i / elapsed) if elapsed > 0 else 0

            grade_str = result.get('grade') or '-'
            print(f"[{i:4d}/{len(repos)}] {marker} {result.get('name', '?')[:40]:40} "
                  f"| {grade_str:2} | {rate:.0f}/hr | ETA {eta/60:.1f}m")

            # Incremental save every 100 repos
            if i % 100 == 0:
                partial_file = output_dir / f"partial_{timestamp}_{i}.json"
                with open(partial_file, "w") as f:
                    json.dump(all_results[-100:], f)
                print(f"    [SAVED] {partial_file}")

    # Final summary
    total_time = (datetime.now() - start_time).total_seconds()

    print("\n" + "=" * 70)
    print(f"COMPLETE: {success}/{len(all_results)} succeeded, {failed} failed")
    print(f"Time: {total_time/60:.1f} minutes ({total_time:.0f}s)")
    print(f"Rate: {len(all_results)/total_time*3600:.0f} repos/hour")

    # Grade distribution
    grades = {}
    for r in all_results:
        g = r.get("grade") or "FAIL"
        grades[g] = grades.get(g, 0) + 1
    print(f"Grades: {dict(sorted(grades.items()))}")

    # Save final results
    final_output = {
        "meta": {
            "timestamp": timestamp,
            "total_repos": len(repos),
            "processed": len(all_results),
            "success": success,
            "failed": failed,
            "duration_sec": round(total_time, 1),
            "rate_per_hour": round(len(all_results) / total_time * 3600, 1),
            "workers": args.workers
        },
        "grade_distribution": grades,
        "results": all_results
    }

    final_file = output_dir / f"final_results_{timestamp}.json"
    with open(final_file, "w") as f:
        json.dump(final_output, f, indent=2)

    print(f"\n[SAVED] {final_file}")
    print(f"[SIZE] {final_file.stat().st_size / 1024 / 1024:.1f} MB")

    # Cleanup
    shutil.rmtree(work_dir, ignore_errors=True)

    print("\n[DONE]")


if __name__ == "__main__":
    main()
