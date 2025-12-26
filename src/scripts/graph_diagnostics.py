#!/usr/bin/env python3
"""
ATMAN Graph Diagnostics Tool
Performs multiple structural analyses on the codebase graph.
"""

import json
from pathlib import Path
from collections import defaultdict
import heapq

GRAPH_PATH = Path("output/atman_current_20251219/graph.json")

def load_graph():
    """Load graph data and build adjacency structures."""
    data = json.loads(GRAPH_PATH.read_text())
    
    # Build adjacency lists
    adj_out = defaultdict(list)  # node -> [(neighbor, edge_type, weight)]
    adj_in = defaultdict(list)   # node -> [(caller, edge_type, weight)]
    
    nodes = {}
    for comp_id, comp in data.get("components", {}).items():
        nodes[comp.get("name", comp_id)] = comp
    
    for edge in data.get("edges", []):
        src = edge.get("source")
        tgt = edge.get("target")
        etype = edge.get("edge_type", "unknown")
        weight = edge.get("weight", 1)
        
        adj_out[src].append((tgt, etype, weight))
        adj_in[tgt].append((src, etype, weight))
    
    return data, nodes, adj_out, adj_in


def diagnostic_1_god_functions(data, nodes, adj_out, adj_in):
    """Find God Functions (high out-degree + high lines)."""
    print("\n" + "="*60)
    print("🔴 DIAGNOSTIC 1: GOD FUNCTIONS (High Complexity)")
    print("="*60)
    
    candidates = []
    for comp_id, comp in data.get("components", {}).items():
        out_deg = comp.get("out_degree", 0)
        name = comp.get("name", "")
        kind = comp.get("kind", "")
        file_path = comp.get("file", "")
        
        # Extract lines from semantic ID if present
        lines = 0
        if "|lines:" in comp_id:
            try:
                lines = int(comp_id.split("|lines:")[1].split("|")[0])
            except:
                pass
        
        if out_deg > 50 or lines > 200:
            risk = out_deg * 0.5 + lines * 0.1
            candidates.append((risk, name, out_deg, lines, file_path, kind))
    
    candidates.sort(reverse=True)
    
    print(f"\n{'Function':<40} {'Out-Deg':>8} {'Lines':>8} {'File':<30}")
    print("-"*90)
    for risk, name, out_deg, lines, file_path, kind in candidates[:15]:
        short_file = file_path[-28:] if len(file_path) > 28 else file_path
        print(f"{name[:38]:<40} {out_deg:>8} {lines:>8} {short_file:<30}")
    
    return candidates[:15]


def diagnostic_2_hub_nodes(data, nodes, adj_out, adj_in):
    """Find Hub Nodes (high in-degree = heavily depended upon)."""
    print("\n" + "="*60)
    print("🟡 DIAGNOSTIC 2: HUB NODES (Most Depended Upon)")
    print("="*60)
    
    in_degrees = []
    for comp_id, comp in data.get("components", {}).items():
        in_deg = comp.get("in_degree", 0)
        name = comp.get("name", "")
        file_path = comp.get("file", "")
        if in_deg > 10 and name:
            in_degrees.append((in_deg, name, file_path))
    
    in_degrees.sort(reverse=True)
    
    print(f"\n{'Function':<40} {'In-Degree':>10} {'File':<30}")
    print("-"*85)
    for in_deg, name, file_path in in_degrees[:15]:
        short_file = file_path[-28:] if len(file_path) > 28 else file_path
        print(f"{name[:38]:<40} {in_deg:>10} {short_file:<30}")
    
    return in_degrees[:15]


def diagnostic_3_orphan_nodes(data, nodes, adj_out, adj_in):
    """Find Orphan Nodes (no incoming or outgoing edges)."""
    print("\n" + "="*60)
    print("⚪ DIAGNOSTIC 3: ORPHAN NODES (Isolated Code)")
    print("="*60)
    
    orphans = []
    for comp_id, comp in data.get("components", {}).items():
        in_deg = comp.get("in_degree", 0)
        out_deg = comp.get("out_degree", 0)
        name = comp.get("name", "")
        kind = comp.get("kind", "")
        
        if in_deg == 0 and out_deg == 0 and kind == "FNC":
            orphans.append((name, comp.get("file", "")))
    
    print(f"\nFound {len(orphans)} orphan functions")
    print(f"\n{'Function':<40} {'File':<40}")
    print("-"*85)
    for name, file_path in orphans[:20]:
        short_file = file_path[-38:] if len(file_path) > 38 else file_path
        print(f"{name[:38]:<40} {short_file:<40}")
    
    return orphans


def diagnostic_4_file_coupling(data, nodes, adj_out, adj_in):
    """Analyze file-level coupling (which files are most tangled)."""
    print("\n" + "="*60)
    print("🔗 DIAGNOSTIC 4: FILE COUPLING MATRIX")
    print("="*60)
    
    # Build file -> file edge counts
    file_edges = defaultdict(lambda: defaultdict(int))
    
    # Map node -> file
    node_to_file = {}
    for comp_id, comp in data.get("components", {}).items():
        name = comp.get("name", comp_id)
        file_path = comp.get("file", "")
        if file_path:
            # Normalize file path
            node_to_file[name] = file_path
            node_to_file[comp_id] = file_path
    
    for edge in data.get("edges", []):
        src = edge.get("source")
        tgt = edge.get("target")
        src_file = node_to_file.get(src, "")
        tgt_file = node_to_file.get(tgt, "")
        
        if src_file and tgt_file and src_file != tgt_file:
            file_edges[src_file][tgt_file] += 1
    
    # Find most coupled file pairs
    pairs = []
    for src_file, targets in file_edges.items():
        for tgt_file, count in targets.items():
            pairs.append((count, src_file, tgt_file))
    
    pairs.sort(reverse=True)
    
    print(f"\n{'Source File':<35} {'Target File':<35} {'Edges':>8}")
    print("-"*85)
    for count, src, tgt in pairs[:15]:
        src_short = src[-33:] if len(src) > 33 else src
        tgt_short = tgt[-33:] if len(tgt) > 33 else tgt
        print(f"{src_short:<35} {tgt_short:<35} {count:>8}")
    
    return pairs[:15]


def diagnostic_5_layer_violations(data, nodes, adj_out, adj_in):
    """Detect potential layer violations (e.g., viz calling server internals)."""
    print("\n" + "="*60)
    print("🚨 DIAGNOSTIC 5: POTENTIAL LAYER VIOLATIONS")
    print("="*60)
    
    # Define rough layer categories
    def get_layer(file_path):
        if not file_path:
            return "unknown"
        fp = file_path.lower()
        if "ro-finance" in fp or "components" in fp:
            return "frontend"
        if "viz" in fp:
            return "visualization"
        if "routes" in fp or "api_" in fp:
            return "api"
        if "pluggy" in fp:
            return "integration"
        if "server" in fp:
            return "core"
        if "lib" in fp:
            return "lib"
        if "ingest" in fp:
            return "ingest"
        if "scripts" in fp:
            return "tooling"
        return "other"
    
    # Map nodes to layers
    node_to_file = {}
    for comp_id, comp in data.get("components", {}).items():
        name = comp.get("name", comp_id)
        node_to_file[name] = comp.get("file", "")
        node_to_file[comp_id] = comp.get("file", "")
    
    violations = []
    for edge in data.get("edges", []):
        src = edge.get("source")
        tgt = edge.get("target")
        src_file = node_to_file.get(src, "")
        tgt_file = node_to_file.get(tgt, "")
        
        src_layer = get_layer(src_file)
        tgt_layer = get_layer(tgt_file)
        
        # Frontend shouldn't call core directly
        if src_layer == "frontend" and tgt_layer == "core":
            violations.append(("frontend→core", src, tgt, src_file, tgt_file))
        # Visualization shouldn't call pluggy directly
        if src_layer == "visualization" and tgt_layer == "integration":
            violations.append(("viz→integration", src, tgt, src_file, tgt_file))
    
    print(f"\nFound {len(violations)} potential layer violations")
    print(f"\n{'Type':<18} {'Source':<25} {'Target':<25}")
    print("-"*70)
    for vtype, src, tgt, sf, tf in violations[:15]:
        print(f"{vtype:<18} {src[:23]:<25} {tgt[:23]:<25}")
    
    return violations


def diagnostic_6_dependency_depth(data, nodes, adj_out, adj_in):
    """Find functions with deepest dependency chains."""
    print("\n" + "="*60)
    print("📏 DIAGNOSTIC 6: DEEPEST DEPENDENCY CHAINS")
    print("="*60)
    
    # BFS to find max depth from each node
    def max_depth(start, adj, visited_global):
        if start in visited_global:
            return visited_global[start]
        
        visited = {start}
        queue = [(start, 0)]
        max_d = 0
        
        while queue:
            node, depth = queue.pop(0)
            max_d = max(max_d, depth)
            if depth > 20:  # Cap to avoid infinite loops
                break
            for neighbor, _, _ in adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
        
        visited_global[start] = max_d
        return max_d
    
    depths = []
    visited_cache = {}
    
    for comp_id, comp in data.get("components", {}).items():
        name = comp.get("name", "")
        if comp.get("kind") == "FNC" and comp.get("out_degree", 0) > 5:
            depth = max_depth(name, adj_out, visited_cache)
            if depth > 3:
                depths.append((depth, name, comp.get("file", "")))
    
    depths.sort(reverse=True)
    
    print(f"\n{'Function':<40} {'Max Depth':>10} {'File':<30}")
    print("-"*85)
    for depth, name, file_path in depths[:15]:
        short_file = file_path[-28:] if len(file_path) > 28 else file_path
        print(f"{name[:38]:<40} {depth:>10} {short_file:<30}")
    
    return depths[:15]


def diagnostic_7_edge_type_distribution(data, nodes, adj_out, adj_in):
    """Analyze distribution of edge types."""
    print("\n" + "="*60)
    print("📊 DIAGNOSTIC 7: EDGE TYPE DISTRIBUTION")
    print("="*60)
    
    edge_types = defaultdict(int)
    categories = defaultdict(int)
    
    for edge in data.get("edges", []):
        etype = edge.get("edge_type", "unknown")
        cat = edge.get("category", "unknown")
        edge_types[etype] += 1
        categories[cat] += 1
    
    print("\nEdge Types:")
    for etype, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {etype:<20} {count:>8} ({count*100/len(data.get('edges',[])):.1f}%)")
    
    print("\nCategories:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:<20} {count:>8} ({count*100/len(data.get('edges',[])):.1f}%)")
    
    return edge_types, categories


def main():
    print("\n" + "🔬 ATMAN CODEBASE GRAPH DIAGNOSTICS ".center(60, "="))
    print(f"Graph: {GRAPH_PATH}")
    
    data, nodes, adj_out, adj_in = load_graph()
    
    stats = data.get("stats", {})
    print(f"\n📈 Graph Stats:")
    print(f"   Components: {len(data.get('components', {})):,}")
    print(f"   Edges: {len(data.get('edges', [])):,}")
    for k, v in stats.items():
        print(f"   {k}: {v}")
    
    # Run all diagnostics
    results = {}
    results["god_functions"] = diagnostic_1_god_functions(data, nodes, adj_out, adj_in)
    results["hub_nodes"] = diagnostic_2_hub_nodes(data, nodes, adj_out, adj_in)
    results["orphans"] = diagnostic_3_orphan_nodes(data, nodes, adj_out, adj_in)
    results["file_coupling"] = diagnostic_4_file_coupling(data, nodes, adj_out, adj_in)
    results["layer_violations"] = diagnostic_5_layer_violations(data, nodes, adj_out, adj_in)
    results["dependency_depth"] = diagnostic_6_dependency_depth(data, nodes, adj_out, adj_in)
    results["edge_distribution"] = diagnostic_7_edge_type_distribution(data, nodes, adj_out, adj_in)
    
    print("\n" + "="*60)
    print("✅ DIAGNOSTICS COMPLETE")
    print("="*60)
    
    return results


if __name__ == "__main__":
    main()
