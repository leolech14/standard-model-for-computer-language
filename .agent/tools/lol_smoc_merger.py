#!/usr/bin/env python3
"""
LOL + SMoC Merger
=================
SMoC Role: Integration/Merger/D | static | orchestrator

Merges Collider SMoC output with LOL.csv to create a self-describing inventory.
This is the tool that makes PROJECT_elements eat its own dogfood.

Usage:
  python lol_smoc_merger.py                           # Auto-find latest Collider output
  python lol_smoc_merger.py --collider path/to.json   # Specific Collider output
  python lol_smoc_merger.py --stats                   # Show SMoC statistics
"""

import csv
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Optional

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
LOL_CSV = REPO_ROOT / ".agent" / "intelligence" / "LOL.csv"
LOL_SMOC_CSV = REPO_ROOT / ".agent" / "intelligence" / "LOL_SMOC.csv"
COLLIDER_DIR = REPO_ROOT / "standard-model-of-code" / ".collider"

# SMoC columns to add
SMOC_COLUMNS = [
    "smoc_atom",        # Atom classification (e.g., LOG.FNC.M, ORG.AGG.M)
    "smoc_atom_family", # Atom family (e.g., LOG, ORG, DAT)
    "smoc_role",        # Role (e.g., Query, Validator, Factory)
    "smoc_layer",       # Layer (e.g., Core, Domain, Infrastructure)
    "smoc_boundary",    # Boundary (e.g., Internal, External)
    "smoc_state",       # State (Stateful/Stateless)
    "smoc_effect",      # Effect/Purity
    "smoc_lifecycle",   # Lifecycle (Create/Use/Destroy)
    "smoc_confidence",  # Classification confidence (0-1)
    "smoc_node_count",  # Number of nodes (functions/classes) in file
]


def find_latest_collider_output() -> Optional[Path]:
    """Find the most recent Collider LLM-oriented JSON output."""
    if not COLLIDER_DIR.exists():
        return None

    outputs = list(COLLIDER_DIR.glob("output_llm-oriented_*.json"))
    if not outputs:
        return None

    # Sort by modification time, newest first
    outputs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return outputs[0]


def load_collider_output(path: Path) -> dict:
    """Load and parse Collider JSON output."""
    with open(path) as f:
        return json.load(f)


def build_file_smoc_map(collider_data: dict) -> dict:
    """
    Build a mapping from file path to aggregated SMoC data.

    For each file, we aggregate:
    - Most common atom/role/layer among its nodes
    - Average confidence
    - Node count
    """
    nodes = collider_data.get("nodes", [])
    # files_data = collider_data.get("files", {})  # Available for future use

    # Group nodes by file
    file_nodes = defaultdict(list)
    for node in nodes:
        file_path = node.get("file_path", "")
        if file_path and not file_path.startswith("__"):  # Skip codome boundaries
            file_nodes[file_path].append(node)

    # Build aggregated data per file
    file_smoc = {}
    for file_path, nodes_list in file_nodes.items():
        # Count atoms, roles, layers
        atoms = Counter()
        atom_families = Counter()
        roles = Counter()
        layers = Counter()
        boundaries = Counter()
        states = Counter()
        effects = Counter()
        lifecycles = Counter()
        confidences = []

        for node in nodes_list:
            atom = node.get("atom", "Unknown")
            atoms[atom] += 1

            family = node.get("atom_family", "Unknown")
            atom_families[family] += 1

            dims = node.get("dimensions", {})
            roles[dims.get("D3_ROLE", "Unknown")] += 1
            layers[dims.get("D2_LAYER", "Unknown")] += 1
            boundaries[dims.get("D4_BOUNDARY", "Unknown")] += 1
            states[dims.get("D5_STATE", "Unknown")] += 1
            effects[dims.get("D6_EFFECT", "Unknown")] += 1
            lifecycles[dims.get("D7_LIFECYCLE", "Unknown")] += 1

            conf = node.get("confidence", 0.5)
            confidences.append(conf)

        # Get most common values
        file_smoc[file_path] = {
            "smoc_atom": atoms.most_common(1)[0][0] if atoms else "Unknown",
            "smoc_atom_family": atom_families.most_common(1)[0][0] if atom_families else "Unknown",
            "smoc_role": roles.most_common(1)[0][0] if roles else "Unknown",
            "smoc_layer": layers.most_common(1)[0][0] if layers else "Unknown",
            "smoc_boundary": boundaries.most_common(1)[0][0] if boundaries else "Unknown",
            "smoc_state": states.most_common(1)[0][0] if states else "Unknown",
            "smoc_effect": effects.most_common(1)[0][0] if effects else "Unknown",
            "smoc_lifecycle": lifecycles.most_common(1)[0][0] if lifecycles else "Unknown",
            "smoc_confidence": round(sum(confidences) / len(confidences), 3) if confidences else 0,
            "smoc_node_count": len(nodes_list),
        }

    return file_smoc


def merge_lol_with_smoc(lol_path: Path, file_smoc: dict, output_path: Path):
    """Merge LOL.csv with SMoC data and write enhanced CSV."""

    # Read existing LOL.csv
    with open(lol_path, newline='') as f:
        reader = csv.DictReader(f)
        original_fields = list(reader.fieldnames or [])
        rows = list(reader)

    # Add SMoC columns
    new_fields = list(original_fields) + SMOC_COLUMNS

    # Merge data
    matched = 0
    unmatched = 0

    for row in rows:
        path = row["path"]

        # Try to find matching SMoC data
        # Paths in Collider are relative to standard-model-of-code/
        smoc_data = None

        # Try direct match
        if path in file_smoc:
            smoc_data = file_smoc[path]
        # Try with standard-model-of-code/ prefix stripped
        elif path.startswith("standard-model-of-code/"):
            rel_path = path[len("standard-model-of-code/"):]
            if rel_path in file_smoc:
                smoc_data = file_smoc[rel_path]
        # Try adding src/ prefix (common Collider pattern)
        elif f"src/{path}" in file_smoc:
            smoc_data = file_smoc[f"src/{path}"]

        if smoc_data:
            row.update(smoc_data)
            matched += 1
        else:
            # Fill with N/A for unmatched
            for col in SMOC_COLUMNS:
                row[col] = "N/A"
            unmatched += 1

    # Write enhanced CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(rows)

    return matched, unmatched


def print_smoc_stats(file_smoc: dict):
    """Print statistics about SMoC classifications."""
    print("\n" + "=" * 60)
    print("SMOC CLASSIFICATION STATISTICS")
    print("=" * 60)

    # Aggregate stats
    atoms = Counter()
    families = Counter()
    roles = Counter()
    layers = Counter()

    for data in file_smoc.values():
        atoms[data["smoc_atom"]] += 1
        families[data["smoc_atom_family"]] += 1
        roles[data["smoc_role"]] += 1
        layers[data["smoc_layer"]] += 1

    print("\n## By Atom Family")
    for family, count in families.most_common(10):
        print(f"  {family:15} {count}")

    print("\n## By Role")
    for role, count in roles.most_common(10):
        print(f"  {role:15} {count}")

    print("\n## By Layer")
    for layer, count in layers.most_common(10):
        print(f"  {layer:15} {count}")

    print("\n## Top Atoms")
    for atom, count in atoms.most_common(15):
        print(f"  {atom:15} {count}")

    print("=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Merge LOL with SMoC classifications")
    parser.add_argument("--collider", type=Path, help="Path to Collider JSON output")
    parser.add_argument("--stats", action="store_true", help="Show SMoC statistics")
    args = parser.parse_args()

    # Find Collider output
    collider_path = args.collider or find_latest_collider_output()
    if not collider_path or not collider_path.exists():
        print("ERROR: No Collider output found. Run './pe collider full .' first.")
        sys.exit(1)

    print(f"Loading Collider output: {collider_path.name}")
    collider_data = load_collider_output(collider_path)

    # Build file -> SMoC mapping
    print("Building SMoC file mapping...")
    file_smoc = build_file_smoc_map(collider_data)
    print(f"  Found SMoC data for {len(file_smoc)} files")

    if args.stats:
        print_smoc_stats(file_smoc)
        return

    # Check LOL.csv exists
    if not LOL_CSV.exists():
        print("ERROR: LOL.csv not found. Run 'python lol_sync.py' first.")
        sys.exit(1)

    # Merge
    print(f"Merging with LOL.csv...")
    matched, unmatched = merge_lol_with_smoc(LOL_CSV, file_smoc, LOL_SMOC_CSV)

    print(f"\nResults:")
    print(f"  Matched:   {matched} files with SMoC data")
    print(f"  Unmatched: {unmatched} files (N/A)")
    print(f"  Coverage:  {matched / (matched + unmatched) * 100:.1f}%")
    print(f"\nSaved to: {LOL_SMOC_CSV}")

    # Show stats
    print_smoc_stats(file_smoc)


if __name__ == "__main__":
    main()
