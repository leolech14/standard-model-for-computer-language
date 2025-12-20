#!/usr/bin/env python3
"""
🚀 100-REPO ANALYSIS PIPELINE

Runs the Spectrometer analysis across all 100+ GitHub repos and produces:
1. Per-repo analysis outputs (graph.json, semantic_ids.json, etc.)
2. Aggregated cross-repo statistics
3. Type distribution analysis
4. Suite-level comparisons (DDD vs Web Frameworks vs CLI, etc.)

Usage:
    python run_100_repos.py                    # Analyze all cloned repos
    python run_100_repos.py --clone-missing     # Clone missing repos first
    python run_100_repos.py --suite ddd_clean_arch  # Only analyze one suite
    python run_100_repos.py --limit 10          # Limit to first N repos
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

# Add spectrometer root to path for imports
SPECTROMETER_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SPECTROMETER_ROOT))
sys.path.insert(0, str(SPECTROMETER_ROOT / "core"))

from tree_sitter_engine import TreeSitterUniversalEngine
from smart_extractor import SmartExtractor, ComponentCard
from llm_classifier import ALLOWED_ROLES, format_system_prompt, EvidenceValidator

# =============================================================================
# CONFIGURATION
# =============================================================================

MANIFEST_PATH = SPECTROMETER_ROOT / "validation" / "benchmarks" / "REPO_MANIFEST_100.json"
REPOS_DIR = SPECTROMETER_ROOT / "validation" / "benchmarks" / "repos"
OUTPUT_DIR = SPECTROMETER_ROOT / "validation" / "100_repo_results"

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class RepoAnalysisResult:
    """Results from analyzing a single repository."""
    repo_id: int
    repo_name: str
    suite: str
    size_category: str
    status: str  # success, error, skipped
    
    # Counts
    total_files: int = 0
    total_nodes: int = 0
    total_edges: int = 0
    
    # Type distribution
    type_counts: Dict[str, int] = field(default_factory=dict)
    layer_counts: Dict[str, int] = field(default_factory=dict)
    
    # Timing
    analysis_time_ms: int = 0
    
    # Error info
    error_message: str = ""
    
    # Output paths
    output_dir: str = ""


@dataclass
class AggregateResults:
    """Aggregated results across all repos."""
    run_id: str
    timestamp: str
    repos_total: int = 0
    repos_analyzed: int = 0
    repos_failed: int = 0
    repos_skipped: int = 0
    
    # Totals
    total_files: int = 0
    total_nodes: int = 0
    total_edges: int = 0
    
    # Aggregated type counts
    type_counts: Dict[str, int] = field(default_factory=dict)
    layer_counts: Dict[str, int] = field(default_factory=dict)
    suite_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    # Per-repo results
    results: List[RepoAnalysisResult] = field(default_factory=list)


# =============================================================================
# PIPELINE
# =============================================================================

class HundredRepoPipeline:
    """Orchestrates analysis across 100+ repos."""
    
    def __init__(self, repos_dir: Path = REPOS_DIR, output_dir: Path = OUTPUT_DIR):
        self.repos_dir = repos_dir
        self.output_dir = output_dir
        self.manifest = self._load_manifest()
        
        # Layer mapping from canonical types
        self.type_to_layer = self._load_type_layers()
    
    def _load_manifest(self) -> Dict:
        """Load the 100-repo manifest."""
        with open(MANIFEST_PATH, 'r') as f:
            return json.load(f)
    
    def _load_type_layers(self) -> Dict[str, str]:
        """Load type-to-layer mapping from canonical_types.json."""
        types_path = Path(__file__).parent.parent / "patterns" / "canonical_types.json"
        if not types_path.exists():
            return {}
        
        with open(types_path, 'r') as f:
            data = json.load(f)
        
        mapping = {}
        for layer_name, layer_data in data.get("layers", {}).items():
            for type_def in layer_data.get("types", []):
                mapping[type_def["id"]] = layer_name
        return mapping
    
    def get_repos_to_analyze(self, 
                              suite: Optional[str] = None,
                              limit: Optional[int] = None,
                              only_cloned: bool = True) -> List[Dict]:
        """Get list of repos to analyze."""
        repos = self.manifest.get("repos", [])
        
        # Filter by suite
        if suite:
            repos = [r for r in repos if r.get("suite") == suite]
        
        # Filter to only cloned repos
        if only_cloned:
            cloned = []
            for r in repos:
                repo_dir = self._get_repo_dir(r)
                if repo_dir.exists():
                    cloned.append(r)
            repos = cloned
        
        # Apply limit
        if limit:
            repos = repos[:limit]
        
        return repos
    
    def _get_repo_dir(self, repo: Dict) -> Path:
        """Get the local directory for a repo."""
        if "local_path" in repo:
            path = Path(repo["local_path"])
            if path.is_absolute():
                return path
            return Path(__file__).parent.parent / path
        
        # Default: repos/owner__name
        repo_name = repo["repo"].replace("/", "__")
        return self.repos_dir / repo_name
    
    def clone_repo(self, repo: Dict) -> bool:
        """Clone a repo if not already present."""
        repo_dir = self._get_repo_dir(repo)
        if repo_dir.exists():
            return True
        
        print(f"  📥 Cloning {repo['repo']}...")
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo["clone_url"], str(repo_dir)],
                capture_output=True,
                timeout=120,
                check=True
            )
            return True
        except Exception as e:
            print(f"  ❌ Clone failed: {e}")
            return False
    
    def analyze_repo(self, repo: Dict) -> RepoAnalysisResult:
        """Analyze a single repository using TreeSitterUniversalEngine."""
        repo_name = repo["repo"].replace("/", "__")
        repo_dir = self._get_repo_dir(repo)
        
        result = RepoAnalysisResult(
            repo_id=repo.get("id", 0),
            repo_name=repo["repo"],
            suite=repo.get("suite", "unknown"),
            size_category=repo.get("size_category", "unknown"),
            status="pending"
        )
        
        if not repo_dir.exists():
            result.status = "skipped"
            result.error_message = "Repo not cloned"
            return result
        
        # Create output directory
        run_output = self.output_dir / repo_name
        run_output.mkdir(parents=True, exist_ok=True)
        result.output_dir = str(run_output)
        
        try:
            import time
            start = time.time()
            
            # Run analysis with TreeSitterUniversalEngine
            engine = TreeSitterUniversalEngine()
            file_results = engine.analyze_directory(str(repo_dir))
            
            # Collect all particles
            all_particles = []
            all_edges = []
            file_count = 0
            
            for file_result in file_results:
                file_count += 1
                particles = file_result.get("particles", [])
                all_particles.extend(particles)
                
                # Count touchpoints as edges
                touchpoints = file_result.get("touchpoints", [])
                all_edges.extend(touchpoints)
            
            result.total_files = file_count
            result.total_nodes = len(all_particles)
            result.total_edges = len(all_edges)
            
            # Count by type
            type_counts = Counter()
            layer_counts = Counter()
            
            for p in all_particles:
                ptype = p.get("type", "Unknown")
                type_counts[ptype] += 1
                
                layer = self.type_to_layer.get(ptype, "unknown")
                layer_counts[layer] += 1
            
            result.type_counts = dict(type_counts)
            result.layer_counts = dict(layer_counts)
            
            # Save graph.json output
            graph_data = {
                "repo_name": repo["repo"],
                "repo_path": str(repo_dir),
                "components": {p.get("name", f"node_{i}"): p for i, p in enumerate(all_particles)},
                "stats": {
                    "total_files": file_count,
                    "total_nodes": len(all_particles),
                    "type_distribution": dict(type_counts)
                }
            }
            
            graph_path = run_output / "graph.json"
            with open(graph_path, 'w') as f:
                json.dump(graph_data, f, indent=2)
            
            result.analysis_time_ms = int((time.time() - start) * 1000)
            result.status = "success"
            
        except Exception as e:
            import traceback
            result.status = "error"
            result.error_message = str(e)[:200]
        
        return result
    
    def llm_classify_repo(self, repo: Dict, sample_size: int = 50) -> Dict[str, int]:
        """
        Run LLM classification on Unknown nodes for a repo.
        
        Returns dict of type -> count for newly classified nodes.
        """
        import subprocess
        
        repo_name = repo["repo"].replace("/", "__")
        repo_dir = self._get_repo_dir(repo)
        graph_path = self.output_dir / repo_name / "graph.json"
        
        if not graph_path.exists():
            return {}
        
        # Load graph
        with open(graph_path) as f:
            graph_data = json.load(f)
        
        components = graph_data.get("components", {})
        unknowns = [(name, c) for name, c in components.items() if c.get("type") == "Unknown"]
        
        if not unknowns:
            return {}
        
        # Sample unknowns
        sample = unknowns[:sample_size]
        
        # Extract and classify
        extractor = SmartExtractor(str(repo_dir))
        validator = EvidenceValidator(strict=False)
        system_prompt = format_system_prompt()
        
        new_classifications = Counter()
        
        for name, node in sample:
            try:
                card = extractor.extract_card(node)
                
                # Build prompt
                user_prompt = f"""Classify this component:

NODE ID: {card.node_id}
NAME: {card.name}
KIND: {card.kind}
DECORATORS: {', '.join(card.decorators) or '(none)'}
BASE CLASSES: {', '.join(card.base_classes) or '(none)'}
FOLDER: {card.folder_layer}
SIGNATURE: {card.signature}

CODE (first 500 chars):
{card.code_excerpt[:500]}

Reply with JSON: {{"role": "<one of: Test, Factory, Service, UseCase, Repository, Entity, DTO, Configuration, Utility, Unknown>", "confidence": 0.0-1.0}}"""

                # Call Ollama
                result = subprocess.run(
                    ["ollama", "run", "qwen2.5:7b-instruct"],
                    input=f"{system_prompt}\n\n{user_prompt}\n\nRespond with JSON only.",
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Parse response
                response = result.stdout.strip()
                if "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()
                    if response.startswith("json"):
                        response = response[4:].strip()
                
                try:
                    parsed = json.loads(response)
                    role = parsed.get("role", "Unknown")
                    confidence = parsed.get("confidence", 0)
                    
                    if role in ALLOWED_ROLES and role != "Unknown" and confidence > 0.5:
                        # Update component
                        components[name]["type"] = role
                        components[name]["llm_confidence"] = confidence
                        new_classifications[role] += 1
                except:
                    pass
                    
            except Exception:
                pass
        
        # Save updated graph
        with open(graph_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        return dict(new_classifications)
    
    def run_pipeline(self,
                     suite: Optional[str] = None,
                     limit: Optional[int] = None,
                     clone_missing: bool = False,
                     workers: int = 4,
                     use_llm: bool = False,
                     llm_sample: int = 50) -> AggregateResults:
        """Run the complete pipeline."""
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("=" * 60)
        print("🚀 100-REPO ANALYSIS PIPELINE")
        print("=" * 60)
        print()
        
        # Get repos
        repos = self.get_repos_to_analyze(
            suite=suite,
            limit=limit,
            only_cloned=not clone_missing
        )
        
        print(f"📋 Repos to analyze: {len(repos)}")
        if suite:
            print(f"   Suite filter: {suite}")
        if limit:
            print(f"   Limit: {limit}")
        print()
        
        # Clone missing if requested
        if clone_missing:
            all_repos = self.manifest.get("repos", [])
            if suite:
                all_repos = [r for r in all_repos if r.get("suite") == suite]
            if limit:
                all_repos = all_repos[:limit]
            
            for repo in all_repos:
                repo_dir = self._get_repo_dir(repo)
                if not repo_dir.exists():
                    self.clone_repo(repo)
            
            # Refresh list
            repos = self.get_repos_to_analyze(suite=suite, limit=limit, only_cloned=True)
        
        # Initialize aggregate results
        aggregate = AggregateResults(
            run_id=run_id,
            timestamp=datetime.now().isoformat(),
            repos_total=len(repos)
        )
        
        # Analyze repos
        print(f"🔬 Analyzing {len(repos)} repositories...")
        print()
        
        for i, repo in enumerate(repos, 1):
            repo_name = repo["repo"]
            print(f"[{i}/{len(repos)}] {repo_name}...", end=" ", flush=True)
            
            result = self.analyze_repo(repo)
            aggregate.results.append(result)
            
            if result.status == "success":
                aggregate.repos_analyzed += 1
                aggregate.total_files += result.total_files
                aggregate.total_nodes += result.total_nodes
                aggregate.total_edges += result.total_edges
                
                # Aggregate type counts
                for t, c in result.type_counts.items():
                    aggregate.type_counts[t] = aggregate.type_counts.get(t, 0) + c
                
                # Aggregate layer counts
                for l, c in result.layer_counts.items():
                    aggregate.layer_counts[l] = aggregate.layer_counts.get(l, 0) + c
                
                # Suite-level stats
                suite_name = result.suite
                if suite_name not in aggregate.suite_counts:
                    aggregate.suite_counts[suite_name] = {}
                for t, c in result.type_counts.items():
                    aggregate.suite_counts[suite_name][t] = \
                        aggregate.suite_counts[suite_name].get(t, 0) + c
                
                print(f"✅ {result.total_nodes} nodes, {result.total_edges} edges ({result.analysis_time_ms}ms)")
            elif result.status == "error":
                aggregate.repos_failed += 1
                print(f"❌ {result.error_message[:50]}")
            else:
                aggregate.repos_skipped += 1
                print(f"⏭️ skipped")
        
        # =============================================================================
        # LLM POST-PROCESSING (if enabled)
        # =============================================================================
        if use_llm:
            print()
            print("🤖 Running LLM classification on Unknown nodes...")
            print()
            
            llm_total = Counter()
            
            for i, repo in enumerate(repos, 1):
                if any(r.repo_name == repo["repo"] and r.status == "success" for r in aggregate.results):
                    repo_name = repo["repo"]
                    print(f"   [{i}/{len(repos)}] {repo_name}...", end=" ", flush=True)
                    
                    new_types = self.llm_classify_repo(repo, sample_size=llm_sample)
                    
                    if new_types:
                        for t, c in new_types.items():
                            llm_total[t] += c
                        total = sum(new_types.values())
                        top = max(new_types.items(), key=lambda x: x[1])[0] if new_types else ""
                        print(f"✅ {total} classified (top: {top})")
                    else:
                        print("⏭️ no unknowns")
            
            print()
            print(f"🤖 LLM classified {sum(llm_total.values())} additional nodes:")
            for t, c in llm_total.most_common(10):
                print(f"   {t}: {c}")
            
            # Update aggregate type counts with LLM classifications
            for t, c in llm_total.items():
                aggregate.type_counts[t] = aggregate.type_counts.get(t, 0) + c
                aggregate.type_counts["Unknown"] = aggregate.type_counts.get("Unknown", 0) - c
        
        # Save aggregate results
        self._save_aggregate(aggregate)
        
        # Print summary
        self._print_summary(aggregate)
        
        return aggregate
    
    def _save_aggregate(self, aggregate: AggregateResults) -> None:
        """Save aggregate results to JSON and markdown."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON
        json_path = self.output_dir / f"aggregate_{aggregate.run_id}.json"
        with open(json_path, 'w') as f:
            json.dump(asdict(aggregate), f, indent=2)
        
        # Markdown summary
        md_path = self.output_dir / f"SUMMARY_{aggregate.run_id}.md"
        md = self._generate_markdown(aggregate)
        with open(md_path, 'w') as f:
            f.write(md)
        
        print(f"\n💾 Results saved to:")
        print(f"   {json_path}")
        print(f"   {md_path}")
    
    def _generate_markdown(self, agg: AggregateResults) -> str:
        """Generate markdown summary report."""
        lines = [
            f"# 100-Repo Analysis Summary",
            f"",
            f"**Run ID:** `{agg.run_id}`",
            f"**Timestamp:** {agg.timestamp}",
            f"",
            f"## Overview",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Repos Analyzed | {agg.repos_analyzed}/{agg.repos_total} |",
            f"| Repos Failed | {agg.repos_failed} |",
            f"| Total Files | {agg.total_files:,} |",
            f"| Total Nodes | {agg.total_nodes:,} |",
            f"| Total Edges | {agg.total_edges:,} |",
            f"",
            f"## Type Distribution",
            f"",
            f"| Type | Count | % |",
            f"|------|------:|---:|",
        ]
        
        total_nodes = agg.total_nodes or 1
        for t, c in sorted(agg.type_counts.items(), key=lambda x: -x[1])[:20]:
            pct = (c / total_nodes) * 100
            lines.append(f"| {t} | {c:,} | {pct:.1f}% |")
        
        lines.extend([
            f"",
            f"## Layer Distribution",
            f"",
            f"| Layer | Count | % |",
            f"|-------|------:|---:|",
        ])
        
        for l, c in sorted(agg.layer_counts.items(), key=lambda x: -x[1]):
            pct = (c / total_nodes) * 100
            lines.append(f"| {l} | {c:,} | {pct:.1f}% |")
        
        lines.extend([
            f"",
            f"## By Suite",
            f"",
        ])
        
        for suite, types in sorted(agg.suite_counts.items()):
            suite_total = sum(types.values())
            lines.append(f"### {suite} ({suite_total:,} nodes)")
            lines.append("")
            lines.append("| Type | Count |")
            lines.append("|------|------:|")
            for t, c in sorted(types.items(), key=lambda x: -x[1])[:10]:
                lines.append(f"| {t} | {c:,} |")
            lines.append("")
        
        return "\n".join(lines)
    
    def _print_summary(self, agg: AggregateResults) -> None:
        """Print summary to console."""
        print()
        print("=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"  Repos analyzed: {agg.repos_analyzed}/{agg.repos_total}")
        print(f"  Total nodes:    {agg.total_nodes:,}")
        print(f"  Total edges:    {agg.total_edges:,}")
        print()
        print("  Top types:")
        for t, c in sorted(agg.type_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"    {t}: {c:,}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Run Spectrometer on 100+ repos")
    parser.add_argument("--suite", help="Only analyze repos in this suite")
    parser.add_argument("--limit", type=int, help="Limit number of repos")
    parser.add_argument("--clone-missing", action="store_true", help="Clone missing repos")
    parser.add_argument("--workers", type=int, default=1, help="Parallel workers")
    parser.add_argument("--llm", action="store_true", help="Enable LLM classification for Unknown nodes")
    parser.add_argument("--llm-sample", type=int, default=50, help="Max Unknown nodes to classify per repo")
    
    args = parser.parse_args()
    
    pipeline = HundredRepoPipeline()
    pipeline.run_pipeline(
        suite=args.suite,
        limit=args.limit,
        clone_missing=args.clone_missing,
        workers=args.workers,
        use_llm=args.llm,
        llm_sample=args.llm_sample
    )


if __name__ == "__main__":
    main()
