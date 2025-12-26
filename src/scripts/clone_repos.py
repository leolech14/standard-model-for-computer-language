#!/usr/bin/env python3
"""Bulk clone repositories from curated list."""
import json
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def clone_repo(repo_info, base_dir):
    """Clone a single repo."""
    name = repo_info['name'].replace('/', '__')
    target = base_dir / name
    
    if target.exists():
        return f"SKIP: {name} (exists)"
    
    try:
        subprocess.run(
            ['git', 'clone', '--depth', '1', repo_info['url'], str(target)],
            capture_output=True, timeout=120
        )
        return f"OK: {name}"
    except Exception as e:
        return f"FAIL: {name} ({e})"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/benchmark/repo_list_v2.json")
    parser.add_argument("--output-dir", default="validation/benchmarks/repos_v2")
    parser.add_argument("--max-workers", type=int, default=5)
    args = parser.parse_args()
    
    with open(args.input, 'r') as f:
        data = json.load(f)
    
    all_repos = []
    for category, repos in data.items():
        all_repos.extend(repos)
    
    print(f"📦 Cloning {len(all_repos)} repos...")
    
    base_dir = Path(args.output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {executor.submit(clone_repo, r, base_dir): r for r in all_repos}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            print(f"[{i}/{len(all_repos)}] {result}")
    
    print("✅ Done")

if __name__ == "__main__":
    main()
