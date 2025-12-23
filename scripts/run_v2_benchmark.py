#!/usr/bin/env python3
"""
Run v2 Benchmark (Sample)
=========================
Runs the Standard Model analysis on a sample of the new v2 repositories.
Demonstrates the system's ability to analyze previously unseen code.
"""
import sys
import random
from pathlib import Path
import time

# Ensure we can import core and tools
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "tools"))

from learning_engine import LearningEngine

def run_benchmark(limit=5):
    print("🚀 RUNNING STANDAD MODEL ON NEW REPOS (v2)")
    print("==========================================")
    
    repos_dir = root_dir / "validation" / "benchmarks" / "repos_v2"
    if not repos_dir.exists():
        print(f"❌ Repos directory not found: {repos_dir}")
        return

    # Get all repos
    all_repos = [d for d in repos_dir.iterdir() if d.is_dir()]
    print(f"Found {len(all_repos)} total repositories in v2 set.")
    
    # Pick random sample
    sample = random.sample(all_repos, min(limit, len(all_repos)))
    print(f"Selected {len(sample)} repositories for this run:\n")
    for r in sample:
        print(f"  - {r.name}")
    print("\n" + "-"*60 + "\n")

    # Initialize Engine
    engine = LearningEngine(auto_learn=True, llm_model=None) # No LLM for speed in sample run
    
    # Run Analysis
    results = []
    start_time = time.time()
    
    for repo_path in sample:
        try:
            print(f"\n📦 Analyzing: {repo_path.name}")
            analysis = engine.analyze_repo(str(repo_path))
            results.append(analysis)
        except Exception as e:
            print(f"❌ Failed to analyze {repo_path.name}: {e}")

    duration = time.time() - start_time
    
    # Report
    print("\n" + "="*60)
    print(f"📊 BENCHMARK COMPLETE ({duration:.1f}s)")
    print("="*60)
    
    print(f"{'REPO':<30} | {'FILES':<8} | {'ATOMS':<8} | {'PATTERNS':<8} | {'COVERAGE':<8}")
    print("-" * 75)
    
    total_atoms = 0
    total_new_patterns = 0
    
    for r in results:
        new_pats = len(r.new_patterns) if r.new_patterns else 0
        print(f"{r.name[:30]:<30} | {r.files:<8} | {r.total_nodes:<8} | {new_pats:<8} | {r.coverage_pct:.1f}%")
        total_atoms += r.total_nodes
        total_new_patterns += new_pats
        
    print("-" * 75)
    print(f"TOTAL: {len(results)} repos, {total_atoms} atoms, {total_new_patterns} new patterns found.")

if __name__ == "__main__":
    run_benchmark()
