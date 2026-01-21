#!/usr/bin/env python3
"""
Version Comparison Tool for Collider

Compares two Collider analysis outputs to detect regressions or improvements.

Usage:
    # Create baseline from current stable
    ./scripts/version_compare.py baseline

    # Run dev and compare to baseline
    ./scripts/version_compare.py compare

    # Compare two specific directories
    ./scripts/version_compare.py diff .collider_baseline .collider_test

    # Full workflow: baseline → edit → compare
    ./scripts/version_compare.py test
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import Dict, Any, Tuple, List

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
BASELINE_DIR = PROJECT_ROOT / ".collider_baseline"
TEST_DIR = PROJECT_ROOT / ".collider_test"
COLLIDER_CMD = PROJECT_ROOT / "collider"


def find_analysis_json(directory: Path) -> Path:
    """Find the unified_analysis.json or output_llm-oriented_*.json file."""
    # Try unified_analysis.json first
    unified = directory / "unified_analysis.json"
    if unified.exists():
        return unified

    # Try output_llm-oriented_*.json
    llm_files = list(directory.glob("output_llm-oriented_*.json"))
    if llm_files:
        return sorted(llm_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

    raise FileNotFoundError(f"No analysis JSON found in {directory}")


def load_analysis(path: Path) -> Dict[str, Any]:
    """Load analysis JSON file."""
    with open(path) as f:
        return json.load(f)


def extract_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key metrics from analysis data."""
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    stats = data.get("stats", {})
    classification = data.get("classification", {})

    # Role distribution
    role_counts = Counter(n.get("role", "Unknown") for n in nodes)

    # Layer distribution
    layer_counts = Counter(n.get("layer") for n in nodes if n.get("layer"))

    # Confidence distribution
    high_conf = sum(1 for n in nodes if n.get("role_confidence", 0) >= 80)
    med_conf = sum(1 for n in nodes if 50 <= n.get("role_confidence", 0) < 80)
    low_conf = sum(1 for n in nodes if n.get("role_confidence", 0) < 50)

    # Edge types
    edge_types = Counter(e.get("edge_type", "unknown") for e in edges)

    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "total_files": stats.get("total_files", 0),
        "coverage_pct": stats.get("coverage_percentage", stats.get("recognized_percentage", 0)),
        "unknown_pct": stats.get("unknown_percentage", 0),
        "role_counts": dict(role_counts),
        "layer_counts": dict(layer_counts),
        "confidence": {"high": high_conf, "medium": med_conf, "low": low_conf},
        "edge_types": dict(edge_types),
        "unique_roles": len(role_counts),
        "canonical_roles_used": sorted(role_counts.keys()),
    }


def compare_metrics(baseline: Dict, current: Dict) -> List[Dict]:
    """Compare two metric sets and return differences."""
    diffs = []

    # Scalar comparisons
    for key in ["total_nodes", "total_edges", "total_files", "coverage_pct", "unique_roles"]:
        b_val = baseline.get(key, 0)
        c_val = current.get(key, 0)
        if b_val != c_val:
            delta = c_val - b_val
            pct = (delta / b_val * 100) if b_val else 0
            diffs.append({
                "metric": key,
                "baseline": b_val,
                "current": c_val,
                "delta": delta,
                "pct_change": round(pct, 1),
                "status": "improved" if (key == "coverage_pct" and delta > 0) else
                          "regressed" if (key == "coverage_pct" and delta < 0) else "changed"
            })

    # Role distribution changes
    b_roles = baseline.get("role_counts", {})
    c_roles = current.get("role_counts", {})
    all_roles = set(b_roles.keys()) | set(c_roles.keys())

    role_changes = []
    for role in sorted(all_roles):
        b_count = b_roles.get(role, 0)
        c_count = c_roles.get(role, 0)
        if b_count != c_count:
            role_changes.append({
                "role": role,
                "baseline": b_count,
                "current": c_count,
                "delta": c_count - b_count
            })

    if role_changes:
        diffs.append({
            "metric": "role_distribution",
            "changes": role_changes,
            "status": "changed"
        })

    # New/removed roles
    new_roles = set(c_roles.keys()) - set(b_roles.keys())
    removed_roles = set(b_roles.keys()) - set(c_roles.keys())

    if new_roles:
        diffs.append({
            "metric": "new_roles",
            "roles": sorted(new_roles),
            "status": "info"
        })

    if removed_roles:
        diffs.append({
            "metric": "removed_roles",
            "roles": sorted(removed_roles),
            "status": "warning"
        })

    # Confidence changes
    b_conf = baseline.get("confidence", {})
    c_conf = current.get("confidence", {})
    conf_changes = []
    for level in ["high", "medium", "low"]:
        b_val = b_conf.get(level, 0)
        c_val = c_conf.get(level, 0)
        if b_val != c_val:
            conf_changes.append({
                "level": level,
                "baseline": b_val,
                "current": c_val,
                "delta": c_val - b_val
            })

    if conf_changes:
        diffs.append({
            "metric": "confidence_distribution",
            "changes": conf_changes,
            "status": "changed"
        })

    return diffs


def print_report(diffs: List[Dict], baseline_path: Path, current_path: Path):
    """Print a human-readable comparison report."""
    print("\n" + "=" * 70)
    print("COLLIDER VERSION COMPARISON REPORT")
    print("=" * 70)
    print(f"Baseline: {baseline_path}")
    print(f"Current:  {current_path}")
    print(f"Time:     {datetime.now().isoformat()}")
    print("-" * 70)

    if not diffs:
        print("\n✅ NO DIFFERENCES DETECTED - Outputs are identical\n")
        return True

    has_regression = False

    for diff in diffs:
        metric = diff["metric"]
        status = diff.get("status", "changed")

        # Status emoji
        emoji = {"improved": "✅", "regressed": "❌", "changed": "🔄",
                 "warning": "⚠️", "info": "ℹ️"}.get(status, "•")

        if status == "regressed":
            has_regression = True

        if metric == "role_distribution":
            print(f"\n{emoji} Role Distribution Changes:")
            for ch in diff["changes"]:
                sign = "+" if ch["delta"] > 0 else ""
                print(f"   {ch['role']:20} {ch['baseline']:5} → {ch['current']:5} ({sign}{ch['delta']})")

        elif metric in ["new_roles", "removed_roles"]:
            label = "New Roles" if metric == "new_roles" else "Removed Roles"
            print(f"\n{emoji} {label}: {', '.join(diff['roles'])}")

        elif metric == "confidence_distribution":
            print(f"\n{emoji} Confidence Distribution Changes:")
            for ch in diff["changes"]:
                sign = "+" if ch["delta"] > 0 else ""
                print(f"   {ch['level']:10} {ch['baseline']:5} → {ch['current']:5} ({sign}{ch['delta']})")

        else:
            delta = diff.get("delta", 0)
            pct = diff.get("pct_change", 0)
            sign = "+" if delta > 0 else ""
            print(f"\n{emoji} {metric}: {diff['baseline']} → {diff['current']} ({sign}{delta}, {sign}{pct}%)")

    print("\n" + "-" * 70)
    if has_regression:
        print("❌ REGRESSIONS DETECTED - Review changes before proceeding")
    else:
        print("✅ No regressions detected")
    print("=" * 70 + "\n")

    return not has_regression


def run_collider(output_dir: Path, target: str = ".") -> bool:
    """Run Collider and save output to directory."""
    print(f"\n🔬 Running Collider → {output_dir}")
    cmd = [str(COLLIDER_CMD), "full", target, "--output", str(output_dir)]
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def cmd_baseline():
    """Create baseline from current stable version."""
    print("\n📸 Creating baseline snapshot...")

    # Run Collider to baseline directory
    if not run_collider(BASELINE_DIR):
        print("❌ Failed to create baseline")
        return False

    # Save metadata
    meta = {
        "created": datetime.now().isoformat(),
        "git_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True
        ).stdout.strip(),
        "git_branch": subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True
        ).stdout.strip(),
    }

    meta_path = BASELINE_DIR / "baseline_meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"✅ Baseline created at {BASELINE_DIR}")
    print(f"   Commit: {meta['git_commit'][:8]}")
    return True


def cmd_compare():
    """Run dev version and compare to baseline."""
    if not BASELINE_DIR.exists():
        print("❌ No baseline found. Run 'version_compare.py baseline' first.")
        return False

    # Run Collider to test directory
    if not run_collider(TEST_DIR):
        print("❌ Failed to run test analysis")
        return False

    # Compare
    return cmd_diff(str(BASELINE_DIR), str(TEST_DIR))


def cmd_diff(baseline_path: str, current_path: str):
    """Compare two analysis directories."""
    baseline_dir = Path(baseline_path)
    current_dir = Path(current_path)

    try:
        baseline_json = find_analysis_json(baseline_dir)
        current_json = find_analysis_json(current_dir)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return False

    baseline_data = load_analysis(baseline_json)
    current_data = load_analysis(current_json)

    baseline_metrics = extract_metrics(baseline_data)
    current_metrics = extract_metrics(current_data)

    diffs = compare_metrics(baseline_metrics, current_metrics)

    return print_report(diffs, baseline_json, current_json)


def cmd_test():
    """Full test workflow: ensure baseline exists, run dev, compare."""
    if not BASELINE_DIR.exists():
        print("⚠️ No baseline found. Creating one first...")
        if not cmd_baseline():
            return False
        print("\n📝 Baseline created. Make your changes, then run 'version_compare.py compare'")
        return True

    return cmd_compare()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "baseline":
        success = cmd_baseline()
    elif cmd == "compare":
        success = cmd_compare()
    elif cmd == "diff" and len(sys.argv) >= 4:
        success = cmd_diff(sys.argv[2], sys.argv[3])
    elif cmd == "test":
        success = cmd_test()
    else:
        print(__doc__)
        return

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
