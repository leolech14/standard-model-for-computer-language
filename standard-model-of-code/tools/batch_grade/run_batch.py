#!/usr/bin/env python3
"""
Batch grade 999 repos in parallel.
Designed for GCP VM with 16+ cores.

Usage:
  python run_batch.py --workers 16 --output gs://elements-archive-2026/grades/
"""

import argparse
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
import os

SCRIPT_DIR = Path(__file__).parent
COLLIDER_ROOT = SCRIPT_DIR.parent.parent


def grade_repo(repo: dict, work_dir: Path) -> dict:
    """Clone and grade a single repo."""
    name = repo["name"]
    url = repo["url"]
    repo_dir = work_dir / name.replace("/", "_")

    result = {
        "name": name,
        "url": url,
        "language": repo.get("language"),
        "stars": repo.get("stars"),
        "status": "pending",
        "grade": None,
        "health_index": None,
        "error": None,
        "duration_sec": None
    }

    start = datetime.now()

    try:
        # Clone (shallow, timeout 60s)
        clone_result = subprocess.run(
            ["git", "clone", "--depth", "1", "--quiet", url, str(repo_dir)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if clone_result.returncode != 0:
            result["status"] = "clone_failed"
            result["error"] = clone_result.stderr[:200]
            return result

        # Grade (timeout 5 min)
        grade_result = subprocess.run(
            ["python", str(COLLIDER_ROOT / "cli.py"), "grade", str(repo_dir), "--json"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(COLLIDER_ROOT)
        )

        if grade_result.returncode != 0:
            result["status"] = "grade_failed"
            result["error"] = grade_result.stderr[:200]
            return result

        # Parse JSON output - find the JSON object in the output
        # Output format: lots of log lines, then JSON object at the end
        stdout = grade_result.stdout

        # Find JSON by looking for the pattern that starts with {"path"
        json_start = stdout.find('{\n  "path"')
        if json_start == -1:
            json_start = stdout.find('{')

        if json_start >= 0:
            # Find matching closing brace
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
            result["error"] = "Could not parse grade output"

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Operation timed out"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:200]
    finally:
        # Cleanup
        if repo_dir.exists():
            shutil.rmtree(repo_dir, ignore_errors=True)

        result["duration_sec"] = (datetime.now() - start).total_seconds()

    return result


def main():
    parser = argparse.ArgumentParser(description="Batch grade repos")
    parser.add_argument("--workers", type=int, default=8, help="Parallel workers")
    parser.add_argument("--repos", default=str(SCRIPT_DIR / "repos_999.json"), help="Repos JSON file")
    parser.add_argument("--output", default="results", help="Output directory or gs:// path")
    parser.add_argument("--limit", type=int, default=None, help="Limit repos (for testing)")
    args = parser.parse_args()

    # Load repos
    with open(args.repos) as f:
        repos = json.load(f)

    if args.limit:
        repos = repos[:args.limit]

    print(f"Batch grading {len(repos)} repos with {args.workers} workers")

    # Work directory
    work_dir = Path(tempfile.mkdtemp(prefix="collider_batch_"))
    print(f"Work dir: {work_dir}")

    results = []
    success = 0
    failed = 0

    start_time = datetime.now()

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(grade_repo, repo, work_dir): repo
            for repo in repos
        }

        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)

            if result["status"] == "success":
                success += 1
                status_char = "+"
            else:
                failed += 1
                status_char = "x"

            elapsed = (datetime.now() - start_time).total_seconds()
            rate = i / elapsed * 3600  # repos/hour

            grade_str = result.get('grade') or '-'
            print(f"[{i}/{len(repos)}] {status_char} {result['name'][:40]:40} "
                  f"| {result['status']:12} | {grade_str:1} "
                  f"| {rate:.0f}/hr")

    # Summary
    total_time = (datetime.now() - start_time).total_seconds()
    print(f"\n{'='*60}")
    print(f"COMPLETE: {success}/{len(repos)} succeeded, {failed} failed")
    print(f"Time: {total_time/60:.1f} minutes")
    print(f"Rate: {len(repos)/total_time*3600:.0f} repos/hour")

    # Grade distribution
    grades = {}
    for r in results:
        g = r.get("grade", "FAIL")
        grades[g] = grades.get(g, 0) + 1
    print(f"Grades: {grades}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"batch_results_{timestamp}.json"

    output_data = {
        "meta": {
            "timestamp": timestamp,
            "total_repos": len(repos),
            "success": success,
            "failed": failed,
            "duration_sec": total_time,
            "workers": args.workers
        },
        "grade_distribution": grades,
        "results": results
    }

    # Local save
    local_path = SCRIPT_DIR / output_file
    with open(local_path, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nSaved: {local_path}")

    # GCS upload if specified
    if args.output.startswith("gs://"):
        gcs_path = f"{args.output.rstrip('/')}/{output_file}"
        subprocess.run(["gsutil", "cp", str(local_path), gcs_path])
        print(f"Uploaded: {gcs_path}")

    # Cleanup
    shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
