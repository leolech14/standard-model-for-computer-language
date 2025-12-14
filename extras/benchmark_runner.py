#!/usr/bin/env python3
"""
🧪 BENCHMARK RUNNER — Single Command Full Pipeline

1. Clone curated repos with architecture docs
2. Extract developer-declared truth from each
3. Run analysis
4. Score against extracted truth
5. Generate comprehensive report

Usage:
    python3 benchmark_runner.py --clone --extract --score --output ./results
    python3 benchmark_runner.py --use-existing --score --output ./results
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "core"))


@dataclass
class RepoScorecard:
    """Complete scorecard for one repo."""
    repo: str
    clone_url: str
    status: str  # cloned, extracted, scored, error
    
    # Truth extraction
    truth_confidence: float = 0.0
    truth_sources: int = 0
    declared_components: int = 0
    
    # Analysis
    files: int = 0
    classes: int = 0
    functions: int = 0
    coverage_pct: float = 0.0
    
    # Scoring
    matched_components: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    grade: str = "N/A"
    
    # Meta
    time_ms: int = 0
    error: str = ""


@dataclass
class BenchmarkReport:
    """Complete benchmark report."""
    run_id: str
    timestamp: str
    
    # Repos
    total_repos: int = 0
    cloned_repos: int = 0
    scored_repos: int = 0
    failed_repos: int = 0
    
    # Aggregates
    avg_truth_confidence: float = 0.0
    avg_coverage: float = 0.0
    avg_f1_score: float = 0.0
    
    # Scorecards
    scorecards: List[Dict] = field(default_factory=list)
    
    # Grade distribution
    grade_distribution: Dict[str, int] = field(default_factory=dict)


class BenchmarkRunner:
    """
    Complete benchmark pipeline.
    """
    
    def __init__(self, curated_path: str = None, repos_dir: str = None):
        self.curated_path = Path(curated_path) if curated_path else (
            Path(__file__).parent / "validation" / "benchmarks" / "CURATED_REPOS.json"
        )
        self.repos_dir = Path(repos_dir) if repos_dir else (
            Path(__file__).parent / "validation" / "benchmarks" / "repos"
        )
        self.truth_dir = Path(__file__).parent / "validation" / "benchmarks" / "extracted_truth"
        
        self.curated = self._load_curated()
    
    def _load_curated(self) -> Dict:
        """Load curated repos list."""
        if self.curated_path.exists():
            return json.loads(self.curated_path.read_text())
        return {"repos": []}
    
    def clone_repos(self, max_repos: int = None) -> Dict[str, Path]:
        """Clone curated repos."""
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        
        repos = self.curated.get("repos", [])
        if max_repos:
            repos = repos[:max_repos]
        
        print(f"\n📥 Cloning {len(repos)} curated repos...")
        print("=" * 70)
        
        cloned = {}
        
        for repo_info in repos:
            repo = repo_info["repo"]
            repo_name = repo.replace("/", "__")
            clone_url = repo_info.get("clone_url")
            vendored = repo_info.get("vendored_path")
            
            local_path = self.repos_dir / repo_name
            
            # Check vendored first
            if vendored:
                vendored_path = Path(__file__).parent / vendored
                if vendored_path.exists():
                    print(f"  ✓ {repo}: using vendored copy")
                    cloned[repo] = vendored_path
                    continue
            
            # Check if already cloned
            if local_path.exists() and any(local_path.iterdir()):
                print(f"  ✓ {repo}: already exists")
                cloned[repo] = local_path
                continue
            
            # Clone
            if clone_url:
                print(f"  ↓ {repo}: cloning...")
                try:
                    result = subprocess.run(
                        ["git", "clone", "--depth=1", clone_url, str(local_path)],
                        capture_output=True,
                        timeout=120,
                    )
                    if result.returncode == 0:
                        cloned[repo] = local_path
                        print(f"  ✓ {repo}: cloned")
                    else:
                        print(f"  ✗ {repo}: clone failed")
                except Exception as e:
                    print(f"  ✗ {repo}: {e}")
        
        return cloned
    
    def extract_all_truth(self, cloned: Dict[str, Path]) -> Dict[str, Dict]:
        """Extract truth from all cloned repos."""
        from truth_extractor import TruthExtractor
        
        self.truth_dir.mkdir(parents=True, exist_ok=True)
        extractor = TruthExtractor()
        
        print(f"\n🔍 Extracting truth from {len(cloned)} repos...")
        print("=" * 70)
        
        truths = {}
        
        for repo, path in cloned.items():
            try:
                truth = extractor.extract(str(path))
                spec = extractor.to_golden_spec(truth)
                
                # Save
                spec_name = repo.replace("/", "__") + ".truth.json"
                (self.truth_dir / spec_name).write_text(json.dumps(spec, indent=2))
                
                truths[repo] = spec
                print(f"  ✓ {repo}: {len(spec['expected_components'])} components, "
                      f"{spec['confidence']:.0%} confidence")
                
            except Exception as e:
                print(f"  ✗ {repo}: {e}")
        
        return truths
    
    def score_all(self, cloned: Dict[str, Path], truths: Dict[str, Dict]) -> BenchmarkReport:
        """Score all repos against their extracted truth."""
        from learning_engine import LearningEngine
        
        print(f"\n🎯 Scoring {len(cloned)} repos against their truth...")
        print("=" * 70)
        
        report = BenchmarkReport(
            run_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            timestamp=datetime.now().isoformat(),
            total_repos=len(cloned),
        )
        
        engine = LearningEngine(auto_learn=False)
        
        for repo, path in cloned.items():
            import time
            start = time.time()
            
            scorecard = RepoScorecard(
                repo=repo,
                clone_url=next((r["clone_url"] for r in self.curated["repos"] 
                               if r["repo"] == repo), ""),
                status="scoring",
            )
            
            try:
                # Get truth
                truth = truths.get(repo, {})
                expected = truth.get("expected_components", [])
                
                scorecard.truth_confidence = truth.get("confidence", 0)
                scorecard.truth_sources = len(truth.get("truth_sources", []))
                scorecard.declared_components = len(expected)
                
                # Get declared language
                repo_info = next((r for r in self.curated["repos"] if r["repo"] == repo), None)
                lang = repo_info.get("language", "python") if repo_info else "python"

                # Analyze
                analysis = engine.analyze_repo(str(path), language=lang)
                codebase = engine.complete_extractor.extract(str(path), language=lang)
                
                scorecard.files = analysis.files
                scorecard.classes = len(codebase.classes)
                scorecard.functions = len(codebase.functions)
                scorecard.coverage_pct = analysis.coverage_pct
                
                # Score against truth
                detected_names = {c.name.lower() for c in codebase.classes.values()}
                expected_names = {e["name"].lower() for e in expected}
                
                matched = len(detected_names & expected_names)
                # Also check partial matches
                for exp_name in expected_names:
                    for det_name in detected_names:
                        if exp_name in det_name or det_name in exp_name:
                            matched += 0.5  # Partial credit
                
                matched = min(matched, len(expected))  # Cap at expected
                
                scorecard.matched_components = int(matched)
                
                if scorecard.classes > 0:
                    scorecard.precision = matched / scorecard.classes
                if len(expected) > 0:
                    scorecard.recall = matched / len(expected)
                if scorecard.precision + scorecard.recall > 0:
                    scorecard.f1_score = (
                        2 * scorecard.precision * scorecard.recall /
                        (scorecard.precision + scorecard.recall)
                    )
                
                # Grade
                if scorecard.f1_score >= 0.9:
                    scorecard.grade = "A"
                elif scorecard.f1_score >= 0.8:
                    scorecard.grade = "B"
                elif scorecard.f1_score >= 0.7:
                    scorecard.grade = "C"
                elif scorecard.f1_score >= 0.6:
                    scorecard.grade = "D"
                else:
                    scorecard.grade = "F"
                
                scorecard.status = "scored"
                report.scored_repos += 1
                
                print(f"  ✓ {repo}: {scorecard.grade} ({scorecard.f1_score:.0%} F1) | "
                      f"{scorecard.matched_components}/{len(expected)} matched")
                
            except Exception as e:
                scorecard.status = "error"
                scorecard.error = str(e)
                report.failed_repos += 1
                print(f"  ✗ {repo}: {e}")
            
            scorecard.time_ms = int((time.time() - start) * 1000)
            report.scorecards.append(asdict(scorecard))
        
        # Aggregate
        scored = [s for s in report.scorecards if s["status"] == "scored"]
        if scored:
            report.avg_truth_confidence = sum(s["truth_confidence"] for s in scored) / len(scored)
            report.avg_coverage = sum(s["coverage_pct"] for s in scored) / len(scored)
            report.avg_f1_score = sum(s["f1_score"] for s in scored) / len(scored)
        
        # Grade distribution
        for s in scored:
            grade = s["grade"]
            report.grade_distribution[grade] = report.grade_distribution.get(grade, 0) + 1
        
        return report
    
    def export(self, report: BenchmarkReport, output_dir: str) -> Path:
        """Export benchmark report."""
        out = Path(output_dir) / report.run_id
        out.mkdir(parents=True, exist_ok=True)
        
        # JSON
        (out / "benchmark_report.json").write_text(json.dumps(asdict(report), indent=2))
        
        # Markdown summary
        md = self._generate_markdown(report)
        (out / "BENCHMARK_REPORT.md").write_text(md)
        
        print(f"\n💾 Exported to: {out}")
        return out
    
    def _generate_markdown(self, report: BenchmarkReport) -> str:
        """Generate markdown report."""
        lines = [
            "# 🧪 Benchmark Report",
            "",
            f"**Run ID:** `{report.run_id}`",
            f"**Timestamp:** {report.timestamp}",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "|--------|------:|",
            f"| Total Repos | {report.total_repos} |",
            f"| Scored | {report.scored_repos} |",
            f"| Failed | {report.failed_repos} |",
            f"| Avg Truth Confidence | {report.avg_truth_confidence:.0%} |",
            f"| Avg Coverage | {report.avg_coverage:.1f}% |",
            f"| Avg F1 Score | {report.avg_f1_score:.0%} |",
            "",
            "## Grade Distribution",
            "",
            "| Grade | Count |",
            "|-------|------:|",
        ]
        
        for grade in ["A", "B", "C", "D", "F"]:
            count = report.grade_distribution.get(grade, 0)
            bar = "█" * count
            lines.append(f"| {grade} | {count} {bar} |")
        
        lines.extend([
            "",
            "## Scorecards",
            "",
            "| Repo | Grade | F1 | Matched | Expected | Coverage |",
            "|------|-------|---:|--------:|---------:|---------:|",
        ])
        
        for s in sorted(report.scorecards, key=lambda x: x.get("f1_score", 0), reverse=True):
            lines.append(
                f"| {s['repo'].split('/')[-1]} | {s['grade']} | {s['f1_score']:.0%} | "
                f"{s['matched_components']} | {s['declared_components']} | {s['coverage_pct']:.1f}% |"
            )
        
        return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

def main():
    # Pre-Flight Checklist
    from core.system_health import SystemHealth
    SystemHealth.print_checklist()

    import argparse
    
    parser = argparse.ArgumentParser(
        description="🧪 Benchmark Runner — Single command full pipeline"
    )
    parser.add_argument("--clone", action="store_true", help="Clone repos from curated list")
    parser.add_argument("--extract", action="store_true", help="Extract truth from repos")
    parser.add_argument("--score", action="store_true", help="Score repos against their truth")
    parser.add_argument("--max-repos", type=int, help="Max repos to process")
    parser.add_argument("--output", default="validation/benchmarks/runs", help="Output directory")
    parser.add_argument("--use-existing", action="store_true", help="Use existing clones and truth")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🧪 BENCHMARK RUNNER — Single Command Full Pipeline")
    print("=" * 70)
    
    runner = BenchmarkRunner()
    
    print(f"\n📋 Curated repos: {len(runner.curated.get('repos', []))}")
    
    # Clone
    if args.clone or not args.use_existing:
        cloned = runner.clone_repos(args.max_repos)
    else:
        # Use existing
        cloned = {}
        for repo_info in runner.curated.get("repos", [])[:args.max_repos]:
            repo = repo_info["repo"]
            vendored = repo_info.get("vendored_path")
            if vendored:
                path = Path(__file__).parent / vendored
                if path.exists():
                    cloned[repo] = path
            else:
                path = runner.repos_dir / repo.replace("/", "__")
                if path.exists():
                    cloned[repo] = path
        print(f"\n📂 Using {len(cloned)} existing repos")
    
    # Extract truth
    if args.extract or not args.use_existing:
        truths = runner.extract_all_truth(cloned)
    else:
        # Load existing
        truths = {}
        for repo in cloned:
            truth_file = runner.truth_dir / (repo.replace("/", "__") + ".truth.json")
            if truth_file.exists():
                truths[repo] = json.loads(truth_file.read_text())
        print(f"📁 Loaded {len(truths)} existing truth files")
    
    # Score
    if args.score:
        report = runner.score_all(cloned, truths)
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 70)
        print(f"   Scored: {report.scored_repos}/{report.total_repos}")
        print(f"   Avg F1: {report.avg_f1_score:.0%}")
        print(f"   Grades: {report.grade_distribution}")
        
        # Export
        out_path = runner.export(report, args.output)
        print(f"\n📁 Report: {out_path / 'BENCHMARK_REPORT.md'}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
