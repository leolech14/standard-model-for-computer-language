#!/usr/bin/env python3
"""
Atom Inventory Analysis Tool

Counts and categorizes all atoms in the Standard Model of Code.
Outputs summary statistics and detailed inventory.

Usage:
    python tools/research/atom_inventory.py
    python tools/research/atom_inventory.py --output inventory.json
    python tools/research/atom_inventory.py --check-duplicates --check-overlaps
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def load_atoms_from_yaml(filepath: Path) -> list[dict]:
    """Load atoms from a YAML file."""
    try:
        with open(filepath) as f:
            data = yaml.safe_load(f)

        if data is None:
            return []

        # Handle different YAML structures
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "atoms" in data:
                return data["atoms"] if isinstance(data["atoms"], list) else []
            # Some files might have atoms at root level with different keys
            return [data] if "id" in data else []
        return []
    except Exception as e:
        print(f"Warning: Failed to load {filepath}: {e}", file=sys.stderr)
        return []


def load_atoms_from_json(filepath: Path) -> list[dict]:
    """Load atoms from a JSON file."""
    try:
        with open(filepath) as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "atoms" in data:
                return data["atoms"]
            return [data] if "id" in data else []
        return []
    except Exception as e:
        print(f"Warning: Failed to load {filepath}: {e}", file=sys.stderr)
        return []


def infer_tier(atom: dict, source_file: str) -> str:
    """Infer atom tier from atom data or source filename."""
    if "tier" in atom:
        return atom["tier"]

    source_lower = source_file.lower()
    if "tier0" in source_lower or "t0" in source_lower:
        return "T0"
    if "tier1" in source_lower or "t1" in source_lower:
        return "T1"
    if "tier2" in source_lower or "t2" in source_lower:
        return "T2"
    if "atoms.json" in source_lower:
        return "base"
    return "unknown"


def infer_category(atom: dict, source_file: str) -> str:
    """Infer category from atom data or source path."""
    if "category" in atom:
        return atom["category"]

    # Infer from source path (t2_mined = security)
    if "t2_mined" in source_file or "semgrep" in source_file.lower():
        return "security"

    return "unknown"


def infer_ecosystem(atom: dict) -> str:
    """Infer ecosystem from atom ID or data."""
    if "ecosystem" in atom:
        return atom["ecosystem"]

    atom_id = atom.get("id", "")
    # Pattern: EXT.ECOSYSTEM.* or similar
    match = re.match(r"EXT\.([A-Z]+)\.", atom_id)
    if match:
        return match.group(1).lower()

    return "core"


def normalize_name(name: str) -> str:
    """Normalize name for semantic comparison."""
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def analyze_inventory(patterns_dir: Path) -> dict[str, Any]:
    """Analyze all atoms in the patterns directory."""
    all_atoms = []
    sources = defaultdict(int)

    # Load from YAML files
    for yaml_file in patterns_dir.glob("**/*.yaml"):
        atoms = load_atoms_from_yaml(yaml_file)
        valid_atoms = 0
        for atom in atoms:
            if not isinstance(atom, dict):
                continue  # Skip non-dict entries
            atom["_source"] = str(yaml_file.relative_to(patterns_dir))
            atom["_tier"] = infer_tier(atom, str(yaml_file))
            atom["_category"] = infer_category(atom, str(yaml_file))
            atom["_ecosystem"] = infer_ecosystem(atom)
            all_atoms.append(atom)
            valid_atoms += 1
        sources[str(yaml_file.name)] = valid_atoms

    # Load from JSON files (e.g., atoms.json)
    for json_file in patterns_dir.glob("*.json"):
        atoms = load_atoms_from_json(json_file)
        valid_atoms = 0
        for atom in atoms:
            if not isinstance(atom, dict):
                continue  # Skip non-dict entries
            atom["_source"] = str(json_file.relative_to(patterns_dir))
            atom["_tier"] = infer_tier(atom, str(json_file))
            atom["_category"] = infer_category(atom, str(json_file))
            atom["_ecosystem"] = infer_ecosystem(atom)
            all_atoms.append(atom)
            valid_atoms += 1
        sources[str(json_file.name)] = valid_atoms

    # Count by various dimensions
    by_tier = Counter(a.get("_tier", "unknown") for a in all_atoms)
    by_category = Counter(a.get("_category", "unknown") for a in all_atoms)
    by_ecosystem = Counter(a.get("_ecosystem", "unknown") for a in all_atoms)

    # Find duplicates
    id_counts = Counter(a.get("id", "NO_ID") for a in all_atoms)
    duplicates = [(id_, count) for id_, count in id_counts.items() if count > 1]

    # Find semantic overlaps
    name_groups = defaultdict(list)
    for atom in all_atoms:
        norm = normalize_name(atom.get("name", ""))
        if norm:
            name_groups[norm].append(atom.get("id", "unknown"))
    overlaps = [(name, ids) for name, ids in name_groups.items() if len(ids) > 1]

    # Calculate ratios
    total = len(all_atoms)
    security_count = by_category.get("security", 0)
    functional_count = total - security_count

    return {
        "summary": {
            "total_atoms": total,
            "unique_ids": len(id_counts),
            "exact_duplicates": len(duplicates),
            "semantic_overlap_groups": len(overlaps),
            "security_ratio": round(security_count / total * 100, 1) if total else 0,
            "functional_ratio": round(functional_count / total * 100, 1) if total else 0,
        },
        "by_tier": dict(by_tier.most_common()),
        "by_category": dict(by_category.most_common()),
        "by_ecosystem": dict(by_ecosystem.most_common(30)),  # Top 30
        "by_source": dict(sorted(sources.items(), key=lambda x: -x[1])),
        "quality": {
            "duplicates": duplicates[:20],  # Top 20
            "overlap_sample": [
                {"name": n, "count": len(ids), "ids": ids[:5]}
                for n, ids in sorted(overlaps, key=lambda x: -len(x[1]))[:10]
            ],
        },
        "atoms": [
            {
                "id": a.get("id"),
                "name": a.get("name"),
                "tier": a.get("_tier"),
                "category": a.get("_category"),
                "ecosystem": a.get("_ecosystem"),
                "source": a.get("_source"),
            }
            for a in all_atoms
        ],
    }


def print_summary(analysis: dict[str, Any]) -> None:
    """Print human-readable summary."""
    s = analysis["summary"]
    print("=" * 60)
    print("ATOM INVENTORY SUMMARY")
    print("=" * 60)
    print(f"Total atoms:           {s['total_atoms']}")
    print(f"Unique IDs:            {s['unique_ids']}")
    print(f"Exact duplicates:      {s['exact_duplicates']}")
    print(f"Semantic overlaps:     {s['semantic_overlap_groups']}")
    print(f"Security ratio:        {s['security_ratio']}%")
    print(f"Functional ratio:      {s['functional_ratio']}%")
    print()

    print("BY TIER:")
    for tier, count in analysis["by_tier"].items():
        pct = round(count / s["total_atoms"] * 100, 1)
        print(f"  {tier:12} {count:6} ({pct}%)")
    print()

    print("BY CATEGORY (top 10):")
    for cat, count in list(analysis["by_category"].items())[:10]:
        pct = round(count / s["total_atoms"] * 100, 1)
        print(f"  {cat:20} {count:6} ({pct}%)")
    print()

    print("BY ECOSYSTEM (top 15):")
    for eco, count in list(analysis["by_ecosystem"].items())[:15]:
        pct = round(count / s["total_atoms"] * 100, 1)
        print(f"  {eco:15} {count:6} ({pct}%)")
    print()

    if analysis["quality"]["duplicates"]:
        print("DUPLICATE IDS (sample):")
        for id_, count in analysis["quality"]["duplicates"][:5]:
            print(f"  {id_}: {count}x")
        print()


def main():
    parser = argparse.ArgumentParser(description="Analyze atom inventory")
    parser.add_argument(
        "--patterns-dir",
        type=Path,
        default=Path("src/patterns"),
        help="Path to patterns directory",
    )
    parser.add_argument(
        "--output", "-o", type=Path, help="Output JSON file (optional)"
    )
    parser.add_argument(
        "--check-duplicates",
        action="store_true",
        help="Exit with error if duplicates found",
    )
    parser.add_argument(
        "--check-overlaps",
        action="store_true",
        help="Exit with error if overlaps exceed threshold",
    )
    parser.add_argument(
        "--overlap-threshold",
        type=int,
        default=500,
        help="Max allowed overlap groups (default: 500)",
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress summary output")

    args = parser.parse_args()

    if not args.patterns_dir.exists():
        print(f"Error: Patterns directory not found: {args.patterns_dir}", file=sys.stderr)
        sys.exit(1)

    analysis = analyze_inventory(args.patterns_dir)

    if not args.quiet:
        print_summary(analysis)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(analysis, f, indent=2)
        print(f"Saved to: {args.output}")

    # Quality checks
    exit_code = 0

    if args.check_duplicates and analysis["summary"]["exact_duplicates"] > 0:
        print(
            f"ERROR: {analysis['summary']['exact_duplicates']} duplicate IDs found",
            file=sys.stderr,
        )
        exit_code = 1

    if args.check_overlaps and analysis["summary"]["semantic_overlap_groups"] > args.overlap_threshold:
        print(
            f"ERROR: {analysis['summary']['semantic_overlap_groups']} overlap groups exceed threshold {args.overlap_threshold}",
            file=sys.stderr,
        )
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
