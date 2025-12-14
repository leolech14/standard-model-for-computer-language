#!/usr/bin/env python3
"""
🧪 TEST BENCH — 100+ Real-World Repository Testing Suite

Single command to:
1. Clone repos from manifest (or use local)
2. Run comprehensive analysis on all repos
3. Auto-learn unknown patterns
4. Generate iteration-ready reports
5. Track progress over multiple runs

Usage:
    # Full suite (clone + analyze)
    python3 test_bench.py --clone --analyze --output runs/

    # Analyze only (use existing clones)
    python3 test_bench.py --analyze --repos-dir ./repos --output runs/

    # Specific suite
    python3 test_bench.py --suite ddd_clean_arch --analyze

    # Compare runs
    python3 test_bench.py --compare runs/20241214_1200 runs/20241214_1400
"""

import sys
import os
import json
import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# Add core to path
sys.path.insert(0, str(Path(__file__).parent / "core"))


@dataclass
class RepoResult:
    """Result from analyzing a single repo."""
    repo_id: int
    repo: str
    name: str
    suite: str
    status: str  # success, error, skipped
    
    # Metrics
    files: int = 0
    lines: int = 0
    nodes: int = 0
    coverage_pct: float = 0.0
    semantic_ids: int = 0
    
    # Graph
    classes: int = 0
    functions: int = 0
    call_edges: int = 0
    
    # Discoveries
    unknown_count: int = 0
    new_patterns: List[str] = field(default_factory=list)
    
    # Golden scoring
    has_golden_spec: bool = False
    golden_grade: str = ""
    golden_score: float = 0.0
    golden_recall: float = 0.0
    golden_precision: float = 0.0
    golden_f1: float = 0.0
    
    # Meta
    time_ms: int = 0
    error: str = ""


@dataclass
class BenchRun:
    """Complete benchmark run result."""
    run_id: str
    timestamp: str
    
    # Config
    manifest_version: int = 0
    repos_requested: int = 0
    repos_analyzed: int = 0
    repos_skipped: int = 0
    repos_errored: int = 0
    
    # Aggregates
    total_files: int = 0
    total_lines: int = 0
    total_nodes: int = 0
    total_known: int = 0
    total_unknown: int = 0
    avg_coverage: float = 0.0
    total_semantic_ids: int = 0
    
    # Registry
    atoms_before: int = 0
    atoms_after: int = 0
    atoms_learned: int = 0
    
    # Performance
    total_time_sec: float = 0.0
    
    # Details
    results: List[RepoResult] = field(default_factory=list)
    discovered_patterns: List[Dict] = field(default_factory=list)
    
    # Suite breakdown
    by_suite: Dict[str, Dict] = field(default_factory=dict)


class TestBench:
    """
    100+ Repository Test Bench.
    
    Orchestrates the complete testing pipeline:
    1. Load manifest
    2. Clone repos (optional)
    3. Analyze with learning engine
    4. Aggregate results
    5. Generate reports
    """
    
    def __init__(self, manifest_path: str = None):
        self.manifest_path = manifest_path or (
            Path(__file__).parent / "validation" / "benchmarks" / "REPO_MANIFEST_100.json"
        )
        self.manifest = self._load_manifest()
        self.learning_engine = None
    
    def _load_manifest(self) -> Dict:
        """Load the repo manifest."""
        path = Path(self.manifest_path)
        if path.exists():
            return json.loads(path.read_text())
        return {"repos": [], "version": 0}
    
    def _init_learning_engine(self):
        """Initialize the learning engine."""
        if self.learning_engine is None:
            from learning_engine import LearningEngine
            self.learning_engine = LearningEngine(auto_learn=True)
    
    def clone_repos(self, output_dir: str, suites: List[str] = None, 
                    max_repos: int = None, sizes: List[str] = None) -> Dict[str, str]:
        """
        Clone repos from manifest.
        
        Returns dict of repo_name -> local_path
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        
        cloned = {}
        repos = self._filter_repos(suites, sizes, max_repos)
        
        print(f"\n📥 Cloning {len(repos)} repositories...")
        print("=" * 70)
        
        for repo_info in repos:
            repo = repo_info["repo"]
            repo_dir = repo_info.get("repo_dir") or repo.replace("/", "__")
            local = out / repo_dir
            
            # Check if already exists
            if local.exists() and any(local.iterdir()):
                print(f"  ✓ {repo}: already exists")
                cloned[repo] = str(local)
                continue
            
            # Check for vendored copy
            if repo_info.get("local_path"):
                vendored = Path(repo_info["local_path"])
                if vendored.exists():
                    print(f"  ✓ {repo}: using vendored copy")
                    cloned[repo] = str(vendored)
                    continue
            
            # Clone
            clone_url = repo_info.get("clone_url")
            if clone_url:
                print(f"  ↓ {repo}: cloning...")
                try:
                    subprocess.run(
                        ["git", "clone", "--depth=1", clone_url, str(local)],
                        capture_output=True,
                        timeout=120,
                    )
                    cloned[repo] = str(local)
                    print(f"  ✓ {repo}: cloned")
                except Exception as e:
                    print(f"  ✗ {repo}: clone failed - {e}")
        
        return cloned
    
    def _filter_repos(self, suites: List[str] = None, sizes: List[str] = None,
                      max_repos: int = None) -> List[Dict]:
        """Filter repos by suite and size."""
        repos = self.manifest.get("repos", [])
        
        if suites:
            repos = [r for r in repos if r.get("suite") in suites]
        
        if sizes:
            repos = [r for r in repos if r.get("size_category") in sizes]
        
        if max_repos:
            repos = repos[:max_repos]
        
        return repos
    
    def analyze(self, repos_dir: str = None, suites: List[str] = None,
                sizes: List[str] = None, max_repos: int = None,
                workers: int = 4) -> BenchRun:
        """
        Run analysis on all repos.
        """
        import time
        start_time = time.time()
        
        self._init_learning_engine()
        
        run = BenchRun(
            run_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            timestamp=datetime.now().isoformat(),
            manifest_version=self.manifest.get("version", 0),
            atoms_before=len(self.learning_engine.registry.atoms),
        )
        
        # Get repos to analyze
        repos = self._filter_repos(suites, sizes, max_repos)
        run.repos_requested = len(repos)
        
        print(f"\n🔬 Analyzing {len(repos)} repositories...")
        print("=" * 70)
        
        # Build repo paths
        repos_path = Path(repos_dir) if repos_dir else Path(__file__).parent / "validation" / "test_repos"
        
        # Analyze each repo
        results: List[RepoResult] = []
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {}
            
            for repo_info in repos:
                repo = repo_info["repo"]
                repo_dir = repo_info.get("repo_dir") or repo.replace("/", "__")
                
                # Try multiple paths
                paths_to_try = [
                    repos_path / repo_dir,
                    repos_path / repo.split("/")[-1],
                ]
                
                if repo_info.get("local_path"):
                    paths_to_try.insert(0, Path(__file__).parent / repo_info["local_path"])
                
                repo_path = None
                for p in paths_to_try:
                    if p.exists() and any(p.rglob("*.py")):
                        repo_path = p
                        break
                
                if repo_path:
                    futures[executor.submit(
                        self._analyze_one, repo_info, str(repo_path)
                    )] = repo_info
                else:
                    # Skip - not found
                    results.append(RepoResult(
                        repo_id=repo_info.get("id", 0),
                        repo=repo,
                        name=repo.split("/")[-1],
                        suite=repo_info.get("suite", "unknown"),
                        status="skipped",
                        error="Repo not found locally",
                    ))
                    run.repos_skipped += 1
            
            for future in as_completed(futures):
                repo_info = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    status_icon = "✅" if result.status == "success" else "❌"
                    print(f"  {status_icon} {result.name}: {result.coverage_pct:.1f}% | "
                          f"{result.semantic_ids} IDs | {result.time_ms}ms")
                    
                    if result.status == "success":
                        run.repos_analyzed += 1
                    else:
                        run.repos_errored += 1
                        
                except Exception as e:
                    print(f"  ❌ {repo_info['repo']}: {e}")
                    run.repos_errored += 1
        
        run.results = results
        
        # Aggregate stats
        successful = [r for r in results if r.status == "success"]
        run.total_files = sum(r.files for r in successful)
        run.total_lines = sum(r.lines for r in successful)
        run.total_nodes = sum(r.nodes for r in successful)
        run.total_semantic_ids = sum(r.semantic_ids for r in successful)
        run.avg_coverage = sum(r.coverage_pct for r in successful) / len(successful) if successful else 0
        
        # Suite breakdown
        suites_seen: Set[str] = set()
        for r in successful:
            suites_seen.add(r.suite)
        
        for suite in suites_seen:
            suite_results = [r for r in successful if r.suite == suite]
            run.by_suite[suite] = {
                "repos": len(suite_results),
                "files": sum(r.files for r in suite_results),
                "avg_coverage": sum(r.coverage_pct for r in suite_results) / len(suite_results) if suite_results else 0,
                "semantic_ids": sum(r.semantic_ids for r in suite_results),
            }
        
        # Count discoveries
        all_patterns: Dict[str, int] = {}
        for r in results:
            for pattern in r.new_patterns:
                all_patterns[pattern] = all_patterns.get(pattern, 0) + 1
        
        run.discovered_patterns = [
            {"pattern": p, "count": c}
            for p, c in sorted(all_patterns.items(), key=lambda x: -x[1])
        ]
        
        # TRIGGER AUTO-LEARNING — this will persist new atoms
        if self.learning_engine.auto_learn and self.learning_engine.all_discoveries:
            learned = self.learning_engine._auto_learn()
            run.atoms_learned = len(learned)
        else:
            run.atoms_learned = 0
        
        run.atoms_after = run.atoms_before + run.atoms_learned
        run.total_time_sec = time.time() - start_time
        
        return run
    
    def _analyze_one(self, repo_info: Dict, repo_path: str) -> RepoResult:
        """Analyze a single repo."""
        import time
        start = time.time()
        
        result = RepoResult(
            repo_id=repo_info.get("id", 0),
            repo=repo_info["repo"],
            name=repo_info["repo"].split("/")[-1],
            suite=repo_info.get("suite", "unknown"),
            status="success",
        )
        
        try:
            analysis = self.learning_engine.analyze_repo(repo_path)
            
            result.files = analysis.files
            result.lines = analysis.lines
            result.nodes = analysis.total_nodes
            result.coverage_pct = analysis.coverage_pct
            result.semantic_ids = analysis.semantic_ids
            result.classes = analysis.classes
            result.functions = analysis.functions
            result.call_edges = analysis.call_edges
            result.unknown_count = analysis.unknown_atoms
            result.new_patterns = [p["type"] for p in analysis.new_patterns]
            
        except Exception as e:
            result.status = "error"
            result.error = str(e)
        
        result.time_ms = int((time.time() - start) * 1000)
        return result
    
    def export(self, run: BenchRun, output_dir: str):
        """Export run results."""
        out = Path(output_dir) / run.run_id
        out.mkdir(parents=True, exist_ok=True)
        
        # 1. Full JSON
        (out / "bench_run.json").write_text(json.dumps(asdict(run), indent=2, default=str))
        
        # 2. Summary markdown
        summary_md = self._generate_summary(run)
        (out / "SUMMARY.md").write_text(summary_md)
        
        # 3. Discoveries
        disc_md = self._generate_discoveries(run)
        (out / "DISCOVERIES.md").write_text(disc_md)
        
        # 4. Suite breakdown
        suite_md = self._generate_suite_breakdown(run)
        (out / "SUITES.md").write_text(suite_md)
        
        # 5. Semantic IDs export
        if self.learning_engine:
            ids_data = {
                "count": len(self.learning_engine.semantic_matrix.ids),
                "ids": [sid.to_string() for sid in self.learning_engine.semantic_matrix.ids],
            }
            (out / "semantic_ids.json").write_text(json.dumps(ids_data, indent=2))
        
        print(f"\n💾 Exported to: {out}")
        return out
    
    def _generate_summary(self, run: BenchRun) -> str:
        """Generate summary markdown."""
        return f"""# 🧪 Test Bench Run Summary

**Run ID:** `{run.run_id}`  
**Timestamp:** {run.timestamp}  
**Duration:** {run.total_time_sec:.1f}s

## Repos

| Metric | Count |
|--------|------:|
| Requested | {run.repos_requested} |
| Analyzed | {run.repos_analyzed} |
| Skipped | {run.repos_skipped} |
| Errors | {run.repos_errored} |

## Aggregates

| Metric | Value |
|--------|------:|
| Total Files | {run.total_files:,} |
| Total Lines | {run.total_lines:,} |
| Total Nodes | {run.total_nodes:,} |
| Avg Coverage | {run.avg_coverage:.1f}% |
| Semantic IDs | {run.total_semantic_ids:,} |

## Learning

| Metric | Value |
|--------|------:|
| Atoms Before | {run.atoms_before} |
| Atoms After | {run.atoms_after} |
| Learned | {run.atoms_learned} |

## Top 10 Repos by Coverage

| Repo | Coverage | Files | IDs |
|------|---------|------|-----|
""" + "\n".join([
    f"| {r.name} | {r.coverage_pct:.1f}% | {r.files} | {r.semantic_ids} |"
    for r in sorted([r for r in run.results if r.status == "success"], 
                    key=lambda x: -x.coverage_pct)[:10]
])
    
    def _generate_discoveries(self, run: BenchRun) -> str:
        """Generate discoveries markdown."""
        lines = [
            "# 🔬 Pattern Discoveries",
            "",
            f"**Run:** {run.run_id}",
            f"**New Patterns:** {len(run.discovered_patterns)}",
            "",
            "| # | Pattern | Occurrences |",
            "|---|---------|------------:|",
        ]
        
        for i, p in enumerate(run.discovered_patterns[:50], 1):
            lines.append(f"| {i} | `{p['pattern']}` | {p['count']} |")
        
        return "\n".join(lines)
    
    def _generate_suite_breakdown(self, run: BenchRun) -> str:
        """Generate suite breakdown markdown."""
        lines = [
            "# 📊 Suite Breakdown",
            "",
            "| Suite | Repos | Files | Avg Coverage | IDs |",
            "|-------|------:|------:|-------------:|----:|",
        ]
        
        for suite, stats in sorted(run.by_suite.items()):
            lines.append(
                f"| {suite} | {stats['repos']} | {stats['files']:,} | "
                f"{stats['avg_coverage']:.1f}% | {stats['semantic_ids']:,} |"
            )
        
        return "\n".join(lines)
    
    def compare_runs(self, run1_path: str, run2_path: str) -> str:
        """Compare two runs."""
        r1 = json.loads((Path(run1_path) / "bench_run.json").read_text())
        r2 = json.loads((Path(run2_path) / "bench_run.json").read_text())
        
        delta_coverage = r2["avg_coverage"] - r1["avg_coverage"]
        delta_atoms = r2["atoms_after"] - r1["atoms_after"]
        delta_ids = r2["total_semantic_ids"] - r1["total_semantic_ids"]
        
        return f"""# 📈 Run Comparison

| Metric | {r1['run_id']} | {r2['run_id']} | Delta |
|--------|------------|------------|------:|
| Repos | {r1['repos_analyzed']} | {r2['repos_analyzed']} | {r2['repos_analyzed'] - r1['repos_analyzed']:+d} |
| Coverage | {r1['avg_coverage']:.1f}% | {r2['avg_coverage']:.1f}% | {delta_coverage:+.1f}% |
| Atoms | {r1['atoms_after']} | {r2['atoms_after']} | {delta_atoms:+d} |
| Semantic IDs | {r1['total_semantic_ids']:,} | {r2['total_semantic_ids']:,} | {delta_ids:+,} |
"""


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="🧪 Test Bench — 100+ Real-World Repository Testing Suite"
    )
    
    # Actions
    parser.add_argument("--clone", action="store_true", help="Clone repos from manifest")
    parser.add_argument("--analyze", action="store_true", help="Run analysis")
    parser.add_argument("--compare", nargs=2, metavar=("RUN1", "RUN2"), help="Compare two runs")
    
    # Filters
    parser.add_argument("--suite", action="append", help="Filter by suite (can repeat)")
    parser.add_argument("--size", action="append", help="Filter by size (small/medium/large/huge)")
    parser.add_argument("--max-repos", type=int, help="Max repos to process")
    
    # Paths
    parser.add_argument("--repos-dir", default="validation/test_repos", help="Repos directory")
    parser.add_argument("--output", default="validation/benchmarks/runs", help="Output directory")
    parser.add_argument("--manifest", help="Custom manifest path")
    
    # Performance
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🧪 TEST BENCH — 100+ Real-World Repository Testing")
    print("=" * 70)
    
    bench = TestBench(args.manifest)
    
    manifest = bench.manifest
    print(f"\n📋 Manifest: {len(manifest.get('repos', []))} repos")
    print(f"   Suites: {list(manifest.get('suites', {}).keys())}")
    
    if args.compare:
        # Compare mode
        comparison = bench.compare_runs(args.compare[0], args.compare[1])
        print(comparison)
        return 0
    
    if args.clone:
        # Clone repos
        bench.clone_repos(
            args.repos_dir,
            suites=args.suite,
            sizes=args.size,
            max_repos=args.max_repos,
        )
    
    if args.analyze:
        # Run analysis
        run = bench.analyze(
            repos_dir=args.repos_dir,
            suites=args.suite,
            sizes=args.size,
            max_repos=args.max_repos,
            workers=args.workers,
        )
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 RUN SUMMARY")
        print("=" * 70)
        print(f"   Repos: {run.repos_analyzed}/{run.repos_requested}")
        print(f"   Files: {run.total_files:,}")
        print(f"   Lines: {run.total_lines:,}")
        print(f"   Nodes: {run.total_nodes:,}")
        print(f"   Coverage: {run.avg_coverage:.1f}%")
        print(f"   Semantic IDs: {run.total_semantic_ids:,}")
        print(f"   Atoms Learned: {run.atoms_learned}")
        print(f"   Time: {run.total_time_sec:.1f}s")
        
        # Export
        export_path = bench.export(run, args.output)
        print(f"\n📁 Results: {export_path}")
    
    if not args.clone and not args.analyze:
        # Demo mode
        print("\nUsage examples:")
        print("  python3 test_bench.py --analyze --repos-dir ./repos")
        print("  python3 test_bench.py --clone --analyze --suite ddd_clean_arch")
        print("  python3 test_bench.py --compare runs/run1 runs/run2")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
