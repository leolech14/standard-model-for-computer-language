#!/usr/bin/env python3
"""
Multi-Repo Discovery Runner

Runs the discovery engine against multiple repos and tracks:
1. New patterns discovered that aren't in the registry
2. How patterns are being categorized
3. Overall coverage statistics
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Set

sys.path.insert(0, str(Path(__file__).parent))

from core.discovery_engine import DiscoveryEngine, UnknownAtom
from core.atom_registry import AtomRegistry


@dataclass
class RepoDiscoveryResult:
    """Results from analyzing a single repo."""
    repo_name: str
    repo_path: str
    files_analyzed: int
    total_nodes: int
    known_atoms: int
    unknown_atoms: int
    coverage_pct: float
    new_discoveries: List[UnknownAtom]
    timestamp: str = ""


class MultiRepoRunner:
    """
    Run discovery against multiple repos and track findings.
    """
    
    def __init__(self):
        self.registry = AtomRegistry()
        self.engine = DiscoveryEngine()
        self.results: List[RepoDiscoveryResult] = []
        self.all_discoveries: Dict[str, UnknownAtom] = {}
    
    def analyze_repo(self, repo_path: str, language: str = "python") -> RepoDiscoveryResult:
        """Analyze a single repo and return results."""
        path = Path(repo_path)
        repo_name = path.name
        
        print(f"\n🔍 Analyzing: {repo_name}")
        print("-" * 50)
        
        report = self.engine.analyze_repo(str(path), language=language)
        
        # Find truly new discoveries (not in registry)
        new_discoveries = []
        for ua in report.unknown_patterns:
            if ua.ast_type not in self.engine.known_atoms:
                new_discoveries.append(ua)
                # Track globally
                if ua.signature_hash not in self.all_discoveries:
                    self.all_discoveries[ua.signature_hash] = ua
                else:
                    # Merge counts
                    existing = self.all_discoveries[ua.signature_hash]
                    existing.occurrence_count += ua.occurrence_count
                    existing.repos_seen_in.update(ua.repos_seen_in)
        
        result = RepoDiscoveryResult(
            repo_name=repo_name,
            repo_path=str(path),
            files_analyzed=report.files_analyzed,
            total_nodes=report.total_nodes,
            known_atoms=report.known_atoms,
            unknown_atoms=report.unknown_atoms,
            coverage_pct=report.coverage_ratio * 100,
            new_discoveries=new_discoveries,
            timestamp=datetime.now().isoformat(),
        )
        
        self.results.append(result)
        
        print(f"  📁 Files: {result.files_analyzed}")
        print(f"  📊 Nodes: {result.total_nodes:,}")
        print(f"  ✅ Known: {result.known_atoms:,} ({result.coverage_pct:.1f}%)")
        print(f"  🔬 New discoveries: {len(new_discoveries)}")
        
        return result
    
    def print_summary(self):
        """Print summary of all repos analyzed."""
        print("\n" + "=" * 70)
        print("🧪 MULTI-REPO DISCOVERY SUMMARY")
        print("=" * 70)
        
        total_files = sum(r.files_analyzed for r in self.results)
        total_nodes = sum(r.total_nodes for r in self.results)
        total_known = sum(r.known_atoms for r in self.results)
        total_unknown = sum(r.unknown_atoms for r in self.results)
        avg_coverage = sum(r.coverage_pct for r in self.results) / len(self.results) if self.results else 0
        
        print(f"\n📊 AGGREGATED STATISTICS")
        print(f"   Repos analyzed: {len(self.results)}")
        print(f"   Total files: {total_files}")
        print(f"   Total AST nodes: {total_nodes:,}")
        print(f"   Known atoms: {total_known:,}")
        print(f"   Unknown atoms: {total_unknown:,}")
        print(f"   Average coverage: {avg_coverage:.1f}%")
        
        # Per-repo breakdown
        print(f"\n📋 PER-REPO BREAKDOWN")
        print(f"   {'Repo':<30} {'Files':>6} {'Known %':>8} {'New':>5}")
        print(f"   {'-'*30} {'-'*6} {'-'*8} {'-'*5}")
        for r in self.results:
            print(f"   {r.repo_name:<30} {r.files_analyzed:>6} {r.coverage_pct:>7.1f}% {len(r.new_discoveries):>5}")
        
        # New discoveries across all repos
        if self.all_discoveries:
            print(f"\n🎯 NEW PATTERNS DISCOVERED (Candidates for Registry)")
            print("-" * 70)
            
            # Sort by occurrences
            sorted_discoveries = sorted(
                self.all_discoveries.values(),
                key=lambda x: x.occurrence_count,
                reverse=True
            )
            
            for i, ua in enumerate(sorted_discoveries[:20], 1):
                repos = ", ".join(list(ua.repos_seen_in)[:3])
                if len(ua.repos_seen_in) > 3:
                    repos += f" +{len(ua.repos_seen_in)-3}"
                print(f"  {i:2}. {ua.ast_type:30} | {ua.occurrence_count:5}x | {repos}")
            
            if len(sorted_discoveries) > 20:
                print(f"\n   ... and {len(sorted_discoveries) - 20} more patterns")
        
        # Registry status
        stats = self.registry.get_stats()
        print(f"\n🧬 REGISTRY STATUS")
        print(f"   Current atoms: {stats['total_atoms']}")
        print(f"   AST types mapped: {stats['ast_types_mapped']}")
        print(f"   Next ID available: {stats['next_id']}")
    
    def generate_report(self) -> str:
        """Generate markdown discovery report."""
        lines = [
            "# 🔬 Multi-Repo Discovery Report",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Repos analyzed | {len(self.results)} |",
            f"| Total files | {sum(r.files_analyzed for r in self.results)} |",
            f"| Total AST nodes | {sum(r.total_nodes for r in self.results):,} |",
            f"| Average coverage | {sum(r.coverage_pct for r in self.results) / len(self.results):.1f}% |" if self.results else "",
            "",
            "## Per-Repo Results",
            "",
        ]
        
        for r in self.results:
            lines.extend([
                f"### {r.repo_name}",
                "",
                f"| Metric | Value |",
                f"|--------|-------|",
                f"| Files | {r.files_analyzed} |",
                f"| Nodes | {r.total_nodes:,} |",
                f"| Known | {r.known_atoms:,} ({r.coverage_pct:.1f}%) |",
                f"| New discoveries | {len(r.new_discoveries)} |",
                "",
            ])
        
        if self.all_discoveries:
            lines.extend([
                "## New Pattern Candidates",
                "",
                "These patterns were found but aren't in the registry:",
                "",
                "| # | AST Type | Occurrences | Repos | Proposed Name |",
                "|---|----------|-------------|-------|---------------|",
            ])
            
            for i, ua in enumerate(sorted(self.all_discoveries.values(), key=lambda x: -x.occurrence_count)[:30], 1):
                lines.append(f"| {i} | `{ua.ast_type}` | {ua.occurrence_count} | {len(ua.repos_seen_in)} | {ua.proposed_name} |")
        
        return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    runner = MultiRepoRunner()
    
    # Analyze available repos
    validation_path = Path(__file__).parent / "validation"
    
    repos_to_analyze = [
        validation_path / "dddpy_real",
    ]
    
    # Add any other Python projects we can find
    project_root = Path(__file__).parent.parent
    
    # Check for other test fixtures or repos
    for potential_repo in validation_path.iterdir():
        if potential_repo.is_dir() and (potential_repo / "__init__.py").exists():
            if potential_repo not in repos_to_analyze:
                repos_to_analyze.append(potential_repo)
    
    print("=" * 70)
    print("🧪 MULTI-REPO DISCOVERY RUNNER")
    print("=" * 70)
    print(f"\nFound {len(repos_to_analyze)} repos to analyze")
    
    for repo_path in repos_to_analyze:
        if repo_path.exists():
            runner.analyze_repo(str(repo_path))
    
    runner.print_summary()
    
    # Save report
    report_path = Path(__file__).parent / "output" / "multi_repo_discovery.md"
    report_path.write_text(runner.generate_report())
    print(f"\n💾 Report saved: {report_path}")
