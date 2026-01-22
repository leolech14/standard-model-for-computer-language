#!/usr/bin/env python3
"""
Atom Coverage Analysis Tool

Computes coverage metrics from a Collider unified_analysis.json output.
Measures top-k mass, Unknown rate, and T2 enrichment.

Usage:
    python tools/research/atom_coverage.py .collider/unified_analysis.json
    python tools/research/atom_coverage.py analysis.json --output coverage.json
    python tools/research/atom_coverage.py analysis.json --check-unknown 10
"""

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any


# Base atoms that define structural coverage
BASE_ATOMS = {"LOG.FNC.M", "ORG.AGG.M", "DAT.VAR.A", "ORG.MOD.O"}


def load_analysis(filepath: Path) -> dict[str, Any]:
    """Load unified_analysis.json."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)


def compute_entropy(counts: dict[str, int]) -> float:
    """Compute Shannon entropy of distribution."""
    total = sum(counts.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


def compute_gini(counts: dict[str, int]) -> float:
    """Compute Gini coefficient (0 = equal, 1 = max inequality)."""
    values = sorted(counts.values())
    n = len(values)
    if n == 0:
        return 0.0

    total = sum(values)
    if total == 0:
        return 0.0

    cumsum = 0
    gini_sum = 0
    for i, v in enumerate(values):
        cumsum += v
        gini_sum += (2 * (i + 1) - n - 1) * v

    return gini_sum / (n * total)


def analyze_coverage(data: dict[str, Any]) -> dict[str, Any]:
    """Analyze coverage metrics from unified_analysis.json."""
    nodes = data.get("nodes", [])
    n_nodes = len(nodes)

    if n_nodes == 0:
        return {"error": "No nodes found in analysis"}

    # Count atoms
    atom_counts = Counter()
    t2_count = 0
    ecosystems = set()

    for node in nodes:
        atom = node.get("atom", "Unknown")
        atom_counts[atom] += 1

        # Check for T2 enrichment (various possible field names)
        t2_atom = (
            node.get("t2_atom")
            or node.get("semantic_atom")
            or node.get("ecosystem_atom")
        )
        if t2_atom:
            t2_count += 1

        # Track ecosystems
        eco = node.get("ecosystem") or node.get("detected_ecosystem")
        if eco:
            ecosystems.add(eco)

    # Sort by count descending
    sorted_atoms = atom_counts.most_common()

    # Compute top-k mass
    def topk_mass(k: int) -> float:
        top_k_count = sum(count for _, count in sorted_atoms[:k])
        return round(top_k_count / n_nodes * 100, 2)

    # Unknown rate
    unknown_count = atom_counts.get("Unknown", 0)
    unknown_rate = round(unknown_count / n_nodes * 100, 2)

    # Recognized rate (non-Unknown)
    recognized_rate = round((n_nodes - unknown_count) / n_nodes * 100, 2)

    # Base atom distribution
    base_distribution = {
        atom: atom_counts.get(atom, 0) for atom in BASE_ATOMS
    }
    base_distribution["Unknown"] = unknown_count
    base_distribution["other"] = n_nodes - sum(base_distribution.values())

    # T2 enrichment rate
    t2_rate = round(t2_count / n_nodes * 100, 2)

    # Entropy and Gini (excluding Unknown for structural analysis)
    structural_counts = {k: v for k, v in atom_counts.items() if k != "Unknown"}

    return {
        "metrics": {
            "n_nodes": n_nodes,
            "n_unique_atoms": len(atom_counts),
            "top_1_mass": topk_mass(1),
            "top_2_mass": topk_mass(2),
            "top_4_mass": topk_mass(4),
            "unknown_rate": unknown_rate,
            "recognized_rate": recognized_rate,
            "t2_enrichment_rate": t2_rate,
            "entropy": round(compute_entropy(structural_counts), 3),
            "gini": round(compute_gini(structural_counts), 3),
        },
        "atom_distribution": dict(sorted_atoms[:20]),  # Top 20
        "base_atom_distribution": base_distribution,
        "ecosystems_detected": sorted(ecosystems),
        "quality": {
            "unknown_count": unknown_count,
            "t2_count": t2_count,
            "pareto_check": topk_mass(4) >= 70,  # Hypothesis H1
        },
    }


def print_summary(analysis: dict[str, Any], filepath: str) -> None:
    """Print human-readable summary."""
    m = analysis["metrics"]

    print("=" * 60)
    print(f"COVERAGE ANALYSIS: {filepath}")
    print("=" * 60)
    print()
    print("STRUCTURAL METRICS:")
    print(f"  Total nodes:         {m['n_nodes']}")
    print(f"  Unique atoms:        {m['n_unique_atoms']}")
    print()
    print("TOP-K MASS:")
    print(f"  Top-1 mass:          {m['top_1_mass']}%")
    print(f"  Top-2 mass:          {m['top_2_mass']}%")
    print(f"  Top-4 mass:          {m['top_4_mass']}%")
    print()
    print("COVERAGE QUALITY:")
    print(f"  Recognized rate:     {m['recognized_rate']}%")
    print(f"  Unknown rate:        {m['unknown_rate']}%  (target: <5%)")
    print(f"  T2 enrichment:       {m['t2_enrichment_rate']}%")
    print()
    print("DISTRIBUTION METRICS:")
    print(f"  Entropy:             {m['entropy']} bits")
    print(f"  Gini coefficient:    {m['gini']}")
    print()

    print("BASE ATOM DISTRIBUTION:")
    base = analysis["base_atom_distribution"]
    for atom, count in sorted(base.items(), key=lambda x: -x[1]):
        pct = round(count / m["n_nodes"] * 100, 1)
        bar = "#" * int(pct / 2)
        print(f"  {atom:12} {count:6} ({pct:5.1f}%) {bar}")
    print()

    print("TOP ATOMS:")
    for atom, count in list(analysis["atom_distribution"].items())[:10]:
        pct = round(count / m["n_nodes"] * 100, 1)
        print(f"  {atom:25} {count:6} ({pct}%)")
    print()

    if analysis["ecosystems_detected"]:
        print(f"ECOSYSTEMS DETECTED: {', '.join(analysis['ecosystems_detected'][:10])}")
        print()

    # Quality verdict
    print("QUALITY VERDICT:")
    if analysis["quality"]["pareto_check"]:
        print("  [PASS] Pareto distribution confirmed (top-4 >= 70%)")
    else:
        print("  [WARN] Pareto distribution NOT confirmed (top-4 < 70%)")

    if m["unknown_rate"] <= 5:
        print(f"  [PASS] Unknown rate within target (<= 5%)")
    elif m["unknown_rate"] <= 10:
        print(f"  [WARN] Unknown rate elevated ({m['unknown_rate']}% > 5%)")
    else:
        print(f"  [FAIL] Unknown rate too high ({m['unknown_rate']}% > 10%)")


def main():
    parser = argparse.ArgumentParser(description="Analyze coverage from Collider output")
    parser.add_argument(
        "analysis_file",
        type=Path,
        help="Path to unified_analysis.json",
    )
    parser.add_argument(
        "--output", "-o", type=Path, help="Output JSON file (optional)"
    )
    parser.add_argument(
        "--check-unknown",
        type=float,
        metavar="THRESHOLD",
        help="Exit with error if Unknown rate exceeds threshold",
    )
    parser.add_argument(
        "--check-pareto",
        action="store_true",
        help="Exit with error if top-4 mass < 70 percent",
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress summary output")
    parser.add_argument(
        "--json", action="store_true", help="Output JSON to stdout"
    )

    args = parser.parse_args()

    data = load_analysis(args.analysis_file)
    analysis = analyze_coverage(data)

    if "error" in analysis:
        print(f"Error: {analysis['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(analysis, indent=2))
    elif not args.quiet:
        print_summary(analysis, str(args.analysis_file))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(analysis, f, indent=2)
        if not args.quiet and not args.json:
            print(f"\nSaved to: {args.output}")

    # Quality checks
    exit_code = 0

    if args.check_unknown is not None:
        if analysis["metrics"]["unknown_rate"] > args.check_unknown:
            print(
                f"ERROR: Unknown rate {analysis['metrics']['unknown_rate']}% exceeds threshold {args.check_unknown}%",
                file=sys.stderr,
            )
            exit_code = 1

    if args.check_pareto and not analysis["quality"]["pareto_check"]:
        print(
            f"ERROR: Top-4 mass {analysis['metrics']['top_4_mass']}% < 70%",
            file=sys.stderr,
        )
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
