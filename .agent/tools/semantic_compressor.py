#!/usr/bin/env python3
"""
Semantic Compressor - Find and consolidate purpose-duplicate files.

Uses Collider's 8D vectors to detect collisions (files with same purpose).
No external embeddings. No fluff.

Usage:
    python semantic_compressor.py                 # Detect collisions
    python semantic_compressor.py --report        # Generate consolidation report
    python semantic_compressor.py --execute       # Actually archive demoted files
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent
INTELLIGENCE_DIR = REPO_ROOT / ".agent" / "intelligence"
COLLIDER_OUTPUT = REPO_ROOT / ".collider-full"

# Outputs
COLLISIONS_FILE = INTELLIGENCE_DIR / "COLLISION_CLUSTERS.json"
CONSOLIDATION_FILE = INTELLIGENCE_DIR / "CONSOLIDATION_REPORT.json"
ARCHIVE_DIR = REPO_ROOT / "archive" / "demoted"


def load_collider_data():
    """Load latest Collider output."""
    outputs = list(COLLIDER_OUTPUT.glob("output_llm-oriented_*.json"))
    if not outputs:
        print("No Collider output found. Run: ./pe wire")
        return None

    latest = max(outputs, key=lambda p: p.stat().st_mtime)
    print(f"Loading: {latest.name}")

    with open(latest) as f:
        return json.load(f)


def load_tdj():
    """Load temporal data for recency scoring."""
    tdj_path = INTELLIGENCE_DIR / "tdj.jsonl"
    if not tdj_path.exists():
        return {}

    mtimes = {}
    with open(tdj_path) as f:
        for line in f:
            entry = json.loads(line)
            if "_meta" not in entry:
                mtimes[entry["path"]] = entry.get("mtime", 0)
    return mtimes


def aggregate_file_signatures(data):
    """
    Aggregate node-level data to file-level signatures.
    Each file gets a signature based on dominant role/layer of its nodes.
    """
    file_data = defaultdict(lambda: {
        "nodes": [],
        "roles": defaultdict(int),
        "layers": defaultdict(int),
        "effects": defaultdict(int),
        "purposes": defaultdict(int),  # pi2_purpose - atomic function purpose
        "sys_purposes": defaultdict(int),  # pi4_purpose - system-level purpose
        "in_degree": 0,
        "node_count": 0
    })

    nodes = data.get("nodes", [])
    print(f"Processing {len(nodes)} nodes...")

    for node in nodes:
        file_path = node.get("file_path", "")
        if not file_path:
            continue

        fd = file_data[file_path]
        fd["nodes"].append(node)
        fd["node_count"] += 1
        fd["in_degree"] += node.get("in_degree", 0)

        # Count dimensions
        dims = node.get("dimensions", {})
        role = dims.get("D3_ROLE", node.get("role", "unknown"))
        layer = dims.get("D2_LAYER", node.get("layer", "unknown"))
        effect = dims.get("D6_EFFECT", node.get("effect", "unknown"))

        fd["roles"][role] += 1
        fd["layers"][layer] += 1
        fd["effects"][effect] += 1

        # Capture atomic purpose (pi2_purpose)
        purpose = node.get("pi2_purpose", "unknown")
        fd["purposes"][purpose] += 1

        # Capture system-level purpose (pi4_purpose)
        sys_purpose = node.get("pi4_purpose", "unknown")
        fd["sys_purposes"][sys_purpose] += 1

    return file_data


def get_dominant(counter):
    """Get most common value from a counter dict."""
    if not counter:
        return "unknown"
    return max(counter.items(), key=lambda x: x[1])[0]


def detect_collisions(data):
    """Group files by their dimensional signature."""
    file_data = aggregate_file_signatures(data)
    print(f"Aggregated {len(file_data)} files")

    clusters = defaultdict(list)

    for file_path, fd in file_data.items():
        # Get dominant characteristics
        role = get_dominant(fd["roles"])
        layer = get_dominant(fd["layers"])
        effect = get_dominant(fd["effects"])
        purpose = get_dominant(fd["purposes"])  # pi2_purpose - atomic function
        sys_purpose = get_dominant(fd["sys_purposes"])  # pi4_purpose - system level

        # Extract filename pattern for domain hint
        name = Path(file_path).stem.lower()
        # Simple domain extraction from filename
        if any(x in name for x in ["test", "spec", "_test", "test_"]):
            domain = "testing"
        elif any(x in name for x in ["util", "helper", "common"]):
            domain = "utility"
        elif any(x in name for x in ["config", "setting", "env"]):
            domain = "config"
        elif any(x in name for x in ["model", "schema", "entity"]):
            domain = "data"
        elif any(x in name for x in ["api", "route", "endpoint"]):
            domain = "api"
        elif any(x in name for x in ["cli", "command", "cmd"]):
            domain = "cli"
        else:
            domain = "general"

        # 4D signature: layer + atomic purpose + system purpose + domain
        sig = (layer, purpose, sys_purpose, domain)
        clusters[sig].append({
            "path": file_path,
            "node_count": fd["node_count"],
            "in_degree": fd["in_degree"],
            "effect": effect,
            "role": role,
            "purpose": purpose,
            "sys_purpose": sys_purpose,
            "roles": dict(fd["roles"]),
            "layers": dict(fd["layers"]),
            "purposes": dict(fd["purposes"]),
            "sys_purposes": dict(fd["sys_purposes"])
        })

    # Filter to only clusters with >1 file (actual collisions)
    collisions = {
        f"{sig[0]}|{sig[1]}|{sig[2]}|{sig[3]}": members
        for sig, members in clusters.items()
        if len(members) > 1
    }

    return collisions


def calculate_mass(file_info, mtimes):
    """Score a file for canonicality."""
    path = file_info.get("path", "")

    # Mass: node count (more nodes = more substantial)
    node_count = file_info.get("node_count", 1)

    # Gravity: in-degree (how many things import this)
    in_degree = file_info.get("in_degree", 0)

    # Purity: prefer stateless/pure
    effect = file_info.get("effect", "unknown")
    purity = 1.0 if effect in ("Pure", "ReadOnly", "Stateless") else 0.5

    # Recency: days since modification (lower = better)
    mtime = mtimes.get(path, 0)
    if mtime:
        days_old = (datetime.now().timestamp() - mtime) / 86400
        recency = max(0, 1 - (days_old / 365))  # 0-1 scale, 1 = today
    else:
        recency = 0.5

    # Weighted score
    score = (
        0.3 * min(node_count / 10, 1.0) +  # Mass (cap at 10 nodes)
        0.4 * min(in_degree / 5, 1.0) +     # Gravity (cap at 5 importers)
        0.1 * purity +                       # Purity
        0.2 * recency                        # Recency
    )

    return {
        "score": round(score, 3),
        "node_count": node_count,
        "in_degree": in_degree,
        "purity": effect,
        "recency": round(recency, 2)
    }


def generate_report(collisions, mtimes):
    """Generate consolidation report with canonical/demoted recommendations."""
    report = {
        "generated": datetime.now().isoformat(),
        "total_collisions": len(collisions),
        "clusters": []
    }

    for cluster_id, members in collisions.items():
        # Score each member
        scored = []
        for m in members:
            mass = calculate_mass(m, mtimes)
            scored.append({
                "path": m["path"],
                **mass
            })

        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)

        # Winner is canonical, rest are demoted
        canonical = scored[0]
        demoted = scored[1:]

        # Confidence: gap between top 2 scores
        if len(scored) > 1:
            confidence = round(canonical["score"] - demoted[0]["score"], 3)
        else:
            confidence = 1.0

        report["clusters"].append({
            "id": cluster_id,
            "signature": cluster_id.split("|"),
            "canonical": canonical,
            "demoted": demoted,
            "confidence": confidence,
            "needs_review": confidence < 0.1  # Close call
        })

    # Sort by number of demoted files (biggest wins first)
    report["clusters"].sort(key=lambda c: len(c["demoted"]), reverse=True)

    return report


def print_summary(report):
    """Print human-readable summary."""
    print(f"\n{'='*60}")
    print("SEMANTIC COMPRESSOR - Collision Report")
    print(f"{'='*60}")
    print(f"Generated: {report['generated']}")
    print(f"Total collision clusters: {report['total_collisions']}")

    total_demoted = sum(len(c["demoted"]) for c in report["clusters"])
    needs_review = sum(1 for c in report["clusters"] if c["needs_review"])

    print(f"Total files to archive: {total_demoted}")
    print(f"Needs manual review: {needs_review}")

    print(f"\n{'─'*60}")
    print("TOP 10 COLLISION CLUSTERS")
    print(f"{'─'*60}")

    for cluster in report["clusters"][:10]:
        sig = cluster["signature"]
        print(f"\n[{sig[0]} | {sig[1]} | {sig[2]}]")
        print(f"  CANONICAL: {cluster['canonical']['path']}")
        print(f"             score={cluster['canonical']['score']}")
        for d in cluster["demoted"]:
            print(f"  DEMOTED:   {d['path']}")
            print(f"             score={d['score']}")
        if cluster["needs_review"]:
            print("  ** NEEDS MANUAL REVIEW (close scores) **")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Semantic Compressor")
    parser.add_argument("--report", action="store_true", help="Generate full report")
    parser.add_argument("--execute", action="store_true", help="Archive demoted files")
    args = parser.parse_args()

    # Load data
    data = load_collider_data()
    if not data:
        return 1

    mtimes = load_tdj()
    print(f"Loaded temporal data for {len(mtimes)} files")

    # Detect collisions
    collisions = detect_collisions(data)
    print(f"Found {len(collisions)} collision clusters")

    if not collisions:
        print("No collisions detected. Codebase is clean or Collider data incomplete.")
        return 0

    # Save raw collisions
    with open(COLLISIONS_FILE, "w") as f:
        json.dump(collisions, f, indent=2)
    print(f"Saved: {COLLISIONS_FILE}")

    # Generate report
    report = generate_report(collisions, mtimes)

    with open(CONSOLIDATION_FILE, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Saved: {CONSOLIDATION_FILE}")

    print_summary(report)

    if args.execute:
        print("\n--execute not yet implemented. Review report first.")

    return 0


if __name__ == "__main__":
    exit(main())
