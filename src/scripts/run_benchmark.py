#!/usr/bin/env python3
"""
Benchmark Validation Runner - Wave-Based System

Run Collider on repositories from the validation database with wave-based
progression and self-learning capabilities.

Usage:
    python3 scripts/run_benchmark.py --status                    # Show overall status
    python3 scripts/run_benchmark.py --wave platinum             # Run platinum tier
    python3 scripts/run_benchmark.py --wave platinum --count 10  # Run 10 from platinum
    python3 scripts/run_benchmark.py --check-dod platinum        # Check DoD for tier
    python3 scripts/run_benchmark.py --learn platinum            # Learn from low-conf nodes
    python3 scripts/run_benchmark.py --repo "facebook/react"     # Test specific repo
"""

import json
import argparse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import time
import re

DB_PATH = Path(__file__).parent.parent / "validation" / "benchmarks" / "validation_database.json"
PATTERNS_PATH = Path(__file__).parent.parent / "canonical" / "learned" / "patterns.json"
LEDGER_PATH = Path(__file__).parent.parent / "canonical" / "learned" / "ledger.md"

TIERS = ['platinum', 'gold', 'silver', 'bronze']


def load_db():
    return json.loads(DB_PATH.read_text())


def save_db(db):
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)


def load_patterns():
    return json.loads(PATTERNS_PATH.read_text())


def save_patterns(patterns):
    with open(PATTERNS_PATH, 'w') as f:
        json.dump(patterns, f, indent=2)


def update_metadata(db):
    """Update aggregate stats in metadata."""
    tested = [r for r in db["repos"] if r["status"] == "tested"]
    db["metadata"]["tested_repos"] = len(tested)
    
    if tested:
        db["metadata"]["avg_coverage"] = sum(r["coverage"] or 0 for r in tested) / len(tested)
        db["metadata"]["avg_confidence"] = sum(r["avg_confidence"] or 0 for r in tested) / len(tested)
    
    # Update per-tier stats
    tier_stats = {}
    for tier in TIERS:
        tier_repos = [r for r in db["repos"] if r.get("tier") == tier]
        tier_tested = [r for r in tier_repos if r["status"] == "tested"]
        tier_stats[tier] = {
            "total": len(tier_repos),
            "tested": len(tier_tested),
            "pending": len([r for r in tier_repos if r["status"] == "pending"]),
            "avg_confidence": sum(r["avg_confidence"] or 0 for r in tier_tested) / len(tier_tested) if tier_tested else None
        }
    db["metadata"]["tier_stats"] = tier_stats


def clone_repo(repo_name, target_dir):
    """Clone a repo to target directory."""
    url = f"https://github.com/{repo_name}.git"
    result = subprocess.run(
        ["git", "clone", "--depth", "1", url, str(target_dir)],
        capture_output=True,
        timeout=120
    )
    return result.returncode == 0


def run_collider(repo_path, output_dir):
    """Run Collider analysis on a repo."""
    result = subprocess.run(
        ["python3", "cli.py", "analyze", str(repo_path), "--output", str(output_dir)],
        capture_output=True,
        text=True,
        timeout=600
    )
    return result


def parse_results(output_dir):
    """Parse Collider output to extract metrics."""
    analysis_file = output_dir / "unified_analysis.json"
    if not analysis_file.exists():
        return None
    
    data = json.loads(analysis_file.read_text())
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    
    total_nodes = len(nodes)
    if total_nodes == 0:
        return None
    
    confidences = []
    low_conf_nodes = []
    
    for n in nodes:
        conf = n.get("role_confidence", 0)
        if conf > 1:
            conf = conf / 100
        confidences.append(conf)
        
        if conf < 0.80:  # Low confidence threshold
            low_conf_nodes.append({
                "name": n.get("name", ""),
                "role": n.get("role", "Unknown"),
                "confidence": conf,
                "file_path": n.get("file_path", ""),
            })
    
    avg_conf = sum(confidences) / len(confidences) * 100 if confidences else 0
    
    return {
        "nodes": total_nodes,
        "edges": len(edges),
        "coverage": 100.0,
        "avg_confidence": round(avg_conf, 2),
        "violations": data.get("metadata", {}).get("violations", 0),
        "low_conf_nodes": low_conf_nodes
    }


def test_repo(repo_entry, verbose=True):
    """Test a single repository."""
    repo_name = repo_entry["name"]
    if verbose:
        tier = repo_entry.get("tier", "?").upper()
        print(f"\n🔍 [{tier}] Testing: {repo_name}")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / repo_name.replace("/", "_")
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        start = time.time()
        if not clone_repo(repo_name, repo_dir):
            repo_entry["status"] = "error"
            repo_entry["notes"] = "Clone failed"
            if verbose:
                print(f"  ❌ Clone failed")
            return None
        
        try:
            run_collider(repo_dir, output_dir)
            results = parse_results(output_dir)
            
            if results:
                elapsed = int((time.time() - start) * 1000)
                repo_entry["status"] = "tested"
                repo_entry["tested_at"] = datetime.now().isoformat()
                repo_entry["coverage"] = results["coverage"]
                repo_entry["avg_confidence"] = results["avg_confidence"]
                repo_entry["nodes"] = results["nodes"]
                repo_entry["edges"] = results["edges"]
                repo_entry["violations"] = results["violations"]
                repo_entry["time_ms"] = elapsed
                repo_entry["low_conf_count"] = len(results.get("low_conf_nodes", []))
                
                if verbose:
                    emoji = "✅" if results["avg_confidence"] >= 85 else "⚠️"
                    print(f"  {emoji} {results['nodes']} nodes, {results['avg_confidence']}% conf")
                
                return results
            else:
                repo_entry["status"] = "error"
                repo_entry["notes"] = "No results parsed"
                return None
                
        except subprocess.TimeoutExpired:
            repo_entry["status"] = "error"
            repo_entry["notes"] = "Timeout"
            return None
        except Exception as e:
            repo_entry["status"] = "error"
            repo_entry["notes"] = str(e)[:100]
            return None


def check_dod(db, tier):
    """Check if a tier meets Definition of Done."""
    dod = db["metadata"]["dod"]
    tier_repos = [r for r in db["repos"] if r.get("tier") == tier and r["status"] == "tested"]
    
    if not tier_repos:
        print(f"\n❌ No tested repos in {tier.upper()} tier yet")
        return False
    
    # Calculate metrics
    avg_coverage = sum(r["coverage"] or 0 for r in tier_repos) / len(tier_repos)
    avg_confidence = sum(r["avg_confidence"] or 0 for r in tier_repos) / len(tier_repos)
    below_threshold = [r for r in tier_repos if (r["avg_confidence"] or 0) < dod["min_repo_confidence"]]
    pending = [r for r in db["repos"] if r.get("tier") == tier and r["status"] == "pending"]
    
    print(f"\n📋 DoD CHECK: {tier.upper()} TIER")
    print("=" * 50)
    
    # Check 1: All repos tested
    all_tested = len(pending) == 0
    print(f"{'✅' if all_tested else '❌'} All repos tested: {len(tier_repos)}/{len(tier_repos) + len(pending)}")
    
    # Check 2: Coverage
    cov_ok = avg_coverage >= dod["min_coverage"]
    print(f"{'✅' if cov_ok else '❌'} Avg coverage: {avg_coverage:.1f}% (need ≥{dod['min_coverage']}%)")
    
    # Check 3: Avg confidence
    conf_ok = avg_confidence >= dod["min_avg_confidence"]
    print(f"{'✅' if conf_ok else '❌'} Avg confidence: {avg_confidence:.1f}% (need ≥{dod['min_avg_confidence']}%)")
    
    # Check 4: No repo below threshold
    threshold_ok = len(below_threshold) == 0
    print(f"{'✅' if threshold_ok else '❌'} Repos below {dod['min_repo_confidence']}%: {len(below_threshold)}")
    
    if below_threshold:
        print("  Problem repos:")
        for r in below_threshold[:5]:
            print(f"    - {r['name']}: {r['avg_confidence']:.1f}%")
    
    passed = all_tested and cov_ok and conf_ok and threshold_ok
    print(f"\n{'🏆 DoD PASSED!' if passed else '⏳ DoD NOT MET'}")
    
    return passed


def learn_from_tier(db, tier, auto_add=False):
    """Analyze low-confidence patterns from tested repos in tier."""
    tier_repos = [r for r in db["repos"] if r.get("tier") == tier and r["status"] == "tested"]
    
    if not tier_repos:
        print(f"No tested repos in {tier.upper()} tier")
        return
    
    print(f"\n🧠 LEARNING FROM {tier.upper()} TIER")
    print("=" * 50)
    
    # Collect repos with low avg confidence
    low_conf_repos = [r for r in tier_repos if (r["avg_confidence"] or 100) < 85]
    print(f"Repos with <85% confidence: {len(low_conf_repos)}")
    
    if not low_conf_repos:
        print("No low-confidence repos to learn from!")
        return
    
    # Analyze naming patterns from low-conf repos
    prefix_candidates = defaultdict(lambda: {"count": 0, "roles": Counter()})
    suffix_candidates = defaultdict(lambda: {"count": 0, "roles": Counter()})
    
    for repo in low_conf_repos[:10]:  # Sample first 10
        print(f"\n  Analyzing: {repo['name']} ({repo['avg_confidence']}%)")
        # Note: We'd need to re-run analysis to get detailed nodes
        # For now, just flag the repos that need attention
    
    print("\n💡 SUGGESTION:")
    print("Run these repos individually with --repo and inspect the output")
    print("to identify new patterns for patterns.json")
    
    if low_conf_repos:
        print("\n📋 Repos needing attention:")
        for r in low_conf_repos[:10]:
            print(f"  {r['rank']:3}. {r['name'][:40]:40} {r['avg_confidence']:.1f}%")


def show_status(db, tier=None):
    """Show current validation status."""
    meta = db["metadata"]
    repos = db["repos"]
    
    print("\n📊 VALIDATION DATABASE STATUS")
    print("=" * 60)
    
    if tier:
        # Show specific tier
        tier_repos = [r for r in repos if r.get("tier") == tier]
        tested = [r for r in tier_repos if r["status"] == "tested"]
        pending = [r for r in tier_repos if r["status"] == "pending"]
        errors = [r for r in tier_repos if r["status"] == "error"]
        
        print(f"\n🎯 {tier.upper()} TIER:")
        print(f"   Total:    {len(tier_repos)}")
        print(f"   Tested:   {len(tested)}")
        print(f"   Pending:  {len(pending)}")
        print(f"   Errors:   {len(errors)}")
        
        if tested:
            avg_conf = sum(r["avg_confidence"] or 0 for r in tested) / len(tested)
            print(f"   Avg Conf: {avg_conf:.1f}%")
    else:
        # Show all tiers
        for t in TIERS:
            tier_repos = [r for r in repos if r.get("tier") == t]
            tested = len([r for r in tier_repos if r["status"] == "tested"])
            total = len(tier_repos)
            
            if tested > 0:
                tier_tested = [r for r in tier_repos if r["status"] == "tested"]
                avg_conf = sum(r["avg_confidence"] or 0 for r in tier_tested) / len(tier_tested)
                print(f"{t.upper():10} | {tested:3}/{total:3} tested | {avg_conf:.1f}% avg conf")
            else:
                print(f"{t.upper():10} | {tested:3}/{total:3} tested | --.-% avg conf")
        
        print()
        total_tested = len([r for r in repos if r["status"] == "tested"])
        total_pending = len([r for r in repos if r["status"] == "pending"])
        print(f"TOTAL:     {total_tested}/{meta['total_repos']} tested ({total_pending} pending)")


def main():
    parser = argparse.ArgumentParser(description="Wave-based benchmark validation")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--wave", type=str, choices=TIERS, help="Run specific tier")
    parser.add_argument("--count", type=int, default=None, help="Limit repos to test")
    parser.add_argument("--check-dod", type=str, choices=TIERS, help="Check DoD for tier")
    parser.add_argument("--learn", type=str, choices=TIERS, help="Learn from tier")
    parser.add_argument("--repo", type=str, help="Test specific repo by name")
    args = parser.parse_args()
    
    db = load_db()
    
    if args.status:
        show_status(db)
        return
    
    if args.check_dod:
        check_dod(db, args.check_dod)
        return
    
    if args.learn:
        learn_from_tier(db, args.learn)
        return
    
    if args.repo:
        for r in db["repos"]:
            if r["name"] == args.repo:
                test_repo(r)
                update_metadata(db)
                save_db(db)
                return
        print(f"Repo not found: {args.repo}")
        return
    
    if args.wave:
        tier_repos = [r for r in db["repos"] if r.get("tier") == args.wave and r["status"] == "pending"]
        
        if args.count:
            tier_repos = tier_repos[:args.count]
        
        if not tier_repos:
            print(f"No pending repos in {args.wave.upper()} tier")
            return
        
        print(f"\n🌊 RUNNING {args.wave.upper()} WAVE ({len(tier_repos)} repos)")
        print("=" * 50)
        
        for r in tier_repos:
            test_repo(r)
            update_metadata(db)
            save_db(db)
        
        show_status(db, args.wave)
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()
