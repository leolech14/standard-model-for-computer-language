#!/usr/bin/env python3
"""
Pattern Extractor - Analyze repos and extract missing patterns

This script re-analyzes repos to find high-frequency naming patterns
that are currently missing from patterns.json.

Usage:
    python3 scripts/extract_patterns.py --tier platinum --top 10
"""

import json
import argparse
import subprocess
import tempfile
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "validation" / "benchmarks" / "validation_database.json"
PATTERNS_PATH = Path(__file__).parent.parent / "canonical" / "learned" / "patterns.json"
LEDGER_PATH = Path(__file__).parent.parent / "canonical" / "learned" / "ledger.md"


def load_db():
    return json.loads(DB_PATH.read_text())


def load_patterns():
    return json.loads(PATTERNS_PATH.read_text())


def save_patterns(patterns):
    with open(PATTERNS_PATH, 'w') as f:
        json.dump(patterns, f, indent=2)


def clone_and_analyze(repo_name):
    """Clone repo and run Collider analysis, return nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / repo_name.replace("/", "_")
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        # Clone
        result = subprocess.run(
            ["git", "clone", "--depth", "1", f"https://github.com/{repo_name}.git", str(repo_dir)],
            capture_output=True,
            timeout=120
        )
        
        if result.returncode != 0:
            return []
        
        # Analyze
        subprocess.run(
            ["python3", "cli.py", "analyze", str(repo_dir), "--output", str(output_dir)],
            capture_output=True,
            timeout=600
        )
        
        analysis_file = output_dir / "unified_analysis.json"
        if not analysis_file.exists():
            return []
        
        data = json.loads(analysis_file.read_text())
        return data.get("nodes", [])


def extract_patterns_from_nodes(nodes, existing_patterns, min_count=5):
    """Extract high-frequency naming patterns from low-confidence nodes."""
    
    existing_prefixes = set(existing_patterns.get("prefix_patterns", {}).keys())
    existing_suffixes = set(existing_patterns.get("suffix_patterns", {}).keys())
    
    # Collect low-confidence nodes
    low_conf_nodes = []
    for n in nodes:
        conf = n.get("role_confidence", n.get("confidence", 0))
        if conf > 1:
            conf = conf / 100
        if conf < 0.70:
            low_conf_nodes.append(n)
    
    if not low_conf_nodes:
        return [], []
    
    # Extract potential prefixes (3-10 char starting patterns)
    prefix_candidates = defaultdict(lambda: {"count": 0, "roles": Counter()})
    suffix_candidates = defaultdict(lambda: {"count": 0, "roles": Counter()})
    
    for n in low_conf_nodes:
        name = n.get("name", "")
        role = n.get("role", n.get("type", "Unknown"))
        
        # Skip if no useful name
        if not name or len(name) < 3:
            continue
        
        # Get the short name (after the last dot)
        short_name = name.split(".")[-1] if "." in name else name
        
        # Extract prefixes (common starting patterns)
        for length in [3, 4, 5, 6]:
            if len(short_name) >= length + 2:  # Need extra chars after prefix
                prefix = short_name[:length].lower()
                if prefix.isalpha():
                    prefix_candidates[prefix]["count"] += 1
                    prefix_candidates[prefix]["roles"][role] += 1
        
        # Extract suffixes (common ending patterns)
        for length in [4, 5, 6, 7, 8]:
            if len(short_name) >= length + 2:  # Need extra chars before suffix
                suffix = short_name[-length:]
                # Keep original case for suffixes (CamelCase matters)
                if suffix[0].isupper() or suffix.isalpha():
                    suffix_candidates[suffix]["count"] += 1
                    suffix_candidates[suffix]["roles"][role] += 1
    
    # Filter to high-frequency patterns not already in patterns.json
    new_prefixes = []
    for prefix, data in prefix_candidates.items():
        if data["count"] >= min_count and prefix not in existing_prefixes:
            # Get most common role
            most_common_role = data["roles"].most_common(1)
            if most_common_role:
                role, role_count = most_common_role[0]
                confidence = min(85, 60 + (role_count / data["count"]) * 25)
                new_prefixes.append({
                    "pattern": prefix,
                    "role": role,
                    "confidence": int(confidence),
                    "occurrences": data["count"]
                })
    
    new_suffixes = []
    for suffix, data in suffix_candidates.items():
        if data["count"] >= min_count and suffix not in existing_suffixes:
            most_common_role = data["roles"].most_common(1)
            if most_common_role:
                role, role_count = most_common_role[0]
                confidence = min(90, 65 + (role_count / data["count"]) * 25)
                new_suffixes.append({
                    "pattern": suffix,
                    "role": role,
                    "confidence": int(confidence),
                    "occurrences": data["count"]
                })
    
    # Sort by occurrences
    new_prefixes.sort(key=lambda x: -x["occurrences"])
    new_suffixes.sort(key=lambda x: -x["occurrences"])
    
    return new_prefixes, new_suffixes


def main():
    parser = argparse.ArgumentParser(description="Extract patterns from benchmark repos")
    parser.add_argument("--tier", type=str, default="platinum", help="Tier to analyze")
    parser.add_argument("--top", type=int, default=5, help="Number of repos to analyze")
    parser.add_argument("--apply", action="store_true", help="Apply patterns to patterns.json")
    args = parser.parse_args()
    
    db = load_db()
    patterns = load_patterns()
    
    # Get low-conf repos from tier
    tier_repos = [r for r in db["repos"] if r.get("tier") == args.tier and r["status"] == "tested"]
    tier_repos.sort(key=lambda x: x.get("avg_confidence", 100))
    
    # Take the lowest confidence repos
    target_repos = tier_repos[:args.top]
    
    print(f"🔬 PATTERN EXTRACTION: {args.tier.upper()} TIER")
    print("=" * 60)
    print(f"Analyzing {len(target_repos)} lowest-confidence repos...")
    
    all_nodes = []
    for r in target_repos:
        print(f"\n  📥 {r['name']} ({r['avg_confidence']:.1f}%)")
        nodes = clone_and_analyze(r["name"])
        print(f"     → {len(nodes)} nodes")
        all_nodes.extend(nodes)
    
    print(f"\n📊 Total nodes collected: {len(all_nodes)}")
    
    # Extract patterns
    new_prefixes, new_suffixes = extract_patterns_from_nodes(all_nodes, patterns, min_count=10)
    
    print(f"\n🔍 DISCOVERED PATTERNS:")
    print("-" * 60)
    
    print(f"\nPREFIXES ({len(new_prefixes)} new):")
    for p in new_prefixes[:15]:
        print(f"  {p['pattern']}* → {p['role']} ({p['confidence']}%) [{p['occurrences']} hits]")
    
    print(f"\nSUFFIXES ({len(new_suffixes)} new):")
    for s in new_suffixes[:15]:
        print(f"  *{s['pattern']} → {s['role']} ({s['confidence']}%) [{s['occurrences']} hits]")
    
    if args.apply and (new_prefixes or new_suffixes):
        print(f"\n✅ APPLYING PATTERNS...")
        
        for p in new_prefixes[:10]:  # Add top 10
            patterns["prefix_patterns"][p["pattern"]] = {
                "role": p["role"],
                "confidence": p["confidence"]
            }
        
        for s in new_suffixes[:10]:  # Add top 10
            patterns["suffix_patterns"][s["pattern"]] = {
                "role": s["role"],
                "confidence": s["confidence"]
            }
        
        save_patterns(patterns)
        
        # Log to ledger
        entry = f"""
## {datetime.now().strftime('%Y-%m-%d %H:%M')} - Auto-Extracted from {args.tier.upper()}

**Source**: Pattern extraction from {len(target_repos)} lowest-confidence repos

### New Prefixes
{chr(10).join(f"- `{p['pattern']}*` → {p['role']} ({p['confidence']}%)" for p in new_prefixes[:10])}

### New Suffixes
{chr(10).join(f"- `*{s['pattern']}` → {s['role']} ({s['confidence']}%)" for s in new_suffixes[:10])}

"""
        with open(LEDGER_PATH, 'a') as f:
            f.write(entry)
        
        print(f"📝 Applied {len(new_prefixes[:10])} prefixes, {len(new_suffixes[:10])} suffixes")
        print(f"📝 Logged to ledger.md")
    else:
        print(f"\n💡 Run with --apply to add these patterns")


if __name__ == "__main__":
    main()
