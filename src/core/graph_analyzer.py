#!/usr/bin/env python3
"""
🔬 GRAPH PATTERN ANALYZER
Network analysis for codebase architecture using NetworkX.

Provides:
- Bottleneck detection (betweenness centrality)
- Importance ranking (PageRank)
- Shortest path analysis
- Community detection (Louvain)
- Bridge edge detection
"""

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

try:
    import networkx as nx
except ImportError:
    nx = None

try:
    import community as community_louvain
except ImportError:
    community_louvain = None

try:
    import igraph as ig
    import leidenalg
    HAS_LEIDEN = True
except ImportError:
    ig = None
    leidenalg = None
    HAS_LEIDEN = False


@dataclass
class NodeStats:
    """Statistics for a single node."""
    id: str
    name: str
    kind: str
    file: str
    in_degree: int = 0
    out_degree: int = 0
    betweenness: float = 0.0
    pagerank: float = 0.0
    community: int = -1


@dataclass
class GraphAnalysisResult:
    """Complete analysis result."""
    node_count: int = 0
    edge_count: int = 0
    bottlenecks: list = field(default_factory=list)
    top_pagerank: list = field(default_factory=list)
    communities: dict = field(default_factory=dict)
    bridges: list = field(default_factory=list)
    shortest_paths: dict = field(default_factory=dict)


def load_graph(path: str | Path) -> "nx.DiGraph":
    """Load graph.json into a NetworkX DiGraph."""
    if nx is None:
        raise ImportError("NetworkX not installed. Run: pip install networkx")
    
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    G = nx.DiGraph()
    
    # Add nodes from components
    components = data.get("components", {})
    for node_id, info in components.items():
        G.add_node(
            node_id,
            name=info.get("name", node_id),
            kind=info.get("kind", "unknown"),
            file=info.get("file", ""),
            role=info.get("role"),
        )
    
    # Add edges - try multiple possible formats
    edges = data.get("edges", data.get("relationships", []))
    edge_count = 0
    for rel in edges:
        # Try different key names
        src = rel.get("source") or rel.get("from") or rel.get("src")
        tgt = rel.get("target") or rel.get("to") or rel.get("dst")
        if src and tgt:
            # Add nodes if they don't exist (edge-first format)
            if not G.has_node(src):
                G.add_node(src, name=src.split("|")[-2] if "|" in src else src, kind="unknown", file="")
            if not G.has_node(tgt):
                G.add_node(tgt, name=tgt.split("|")[-2] if "|" in tgt else tgt, kind="unknown", file="")
            G.add_edge(src, tgt, kind=rel.get("kind", "calls"))
            edge_count += 1
    
    print(f"   Loaded {len(G.nodes)} nodes, {edge_count} edges")
    return G


def find_bottlenecks(G: "nx.DiGraph", top_n: int = 20, sample_size: int = 500) -> list[NodeStats]:
    """
    Find bottleneck nodes using betweenness centrality.
    
    High betweenness = many shortest paths go through this node.
    These are coupling hotspots / God Functions.
    
    Uses sampling for large graphs (>1000 nodes) for performance.
    """
    if nx is None:
        return []
    
    # Sample for large graphs
    k = min(sample_size, len(G.nodes)) if len(G.nodes) > 1000 else None
    bc = nx.betweenness_centrality(G, k=k, normalized=True)
    
    # Sort by centrality
    sorted_nodes = sorted(bc.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    results = []
    for node_id, centrality in sorted_nodes:
        info = G.nodes.get(node_id, {})
        results.append(NodeStats(
            id=node_id,
            name=info.get("name", node_id.split("|")[-2] if "|" in node_id else node_id),
            kind=info.get("kind", ""),
            file=info.get("file", ""),
            in_degree=G.in_degree(node_id),
            out_degree=G.out_degree(node_id),
            betweenness=centrality,
        ))
    
    return results


def find_pagerank(G: "nx.DiGraph", top_n: int = 20) -> list[NodeStats]:
    """
    Rank nodes by PageRank (importance based on incoming links).
    
    High PageRank = many important nodes depend on this one.
    Uses power iteration method (no scipy required).
    """
    if nx is None:
        return []
    
    try:
        # Try scipy-based first (faster for large graphs)
        pr = nx.pagerank(G, alpha=0.85)
    except ImportError:
        # Fallback to power iteration (no scipy)
        pr = nx.pagerank(G, alpha=0.85, max_iter=100, tol=1e-6)
    except Exception:
        # If graph has issues, return empty
        return []
    
    sorted_nodes = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    results = []
    for node_id, rank in sorted_nodes:
        info = G.nodes.get(node_id, {})
        results.append(NodeStats(
            id=node_id,
            name=info.get("name", node_id),
            kind=info.get("kind", ""),
            file=info.get("file", ""),
            in_degree=G.in_degree(node_id),
            out_degree=G.out_degree(node_id),
            pagerank=rank,
        ))
    
    return results


def find_communities_leiden(G: "nx.DiGraph", resolution: float = 1.0) -> dict[int, list[str]]:
    """
    Detect communities using the Leiden algorithm (preferred).
    
    Leiden is an improvement over Louvain that guarantees connected communities
    and typically finds higher quality partitions.
    
    Args:
        G: NetworkX directed graph
        resolution: Higher values = more smaller communities
    
    Returns dict: community_id -> list of node IDs.
    """
    if not HAS_LEIDEN:
        print("   ⚠️  Leiden not available, falling back to Louvain")
        return find_communities_louvain(G)
    
    # Convert NetworkX to igraph
    # igraph works with integer node IDs, so we need a mapping
    node_list = list(G.nodes())
    node_to_idx = {node: i for i, node in enumerate(node_list)}
    
    # Create igraph from edges
    edges = [(node_to_idx[u], node_to_idx[v]) for u, v in G.edges() 
             if u in node_to_idx and v in node_to_idx]
    
    ig_graph = ig.Graph(n=len(node_list), edges=edges, directed=False)
    
    # Run Leiden algorithm with Modularity optimization
    partition = leidenalg.find_partition(
        ig_graph, 
        leidenalg.ModularityVertexPartition,
        seed=42  # reproducible
    )
    
    # Convert back to our format: community_id -> [node_ids]
    communities = {}
    for comm_id, members in enumerate(partition):
        node_ids = [node_list[idx] for idx in members]
        if node_ids:  # skip empty communities
            communities[comm_id] = node_ids
    
    return communities


def find_communities_louvain(G: "nx.DiGraph") -> dict[int, list[str]]:
    """
    Detect communities using Louvain algorithm (fallback).
    
    Returns dict: community_id -> list of node IDs.
    """
    if community_louvain is None:
        # Ultimate fallback: use connected components
        undirected = G.to_undirected()
        communities = {}
        for i, component in enumerate(nx.connected_components(undirected)):
            communities[i] = list(component)
        return communities
    
    # Louvain works on undirected graphs
    undirected = G.to_undirected()
    partition = community_louvain.best_partition(undirected)
    
    # Invert: community_id -> [nodes]
    communities = {}
    for node, comm_id in partition.items():
        if comm_id not in communities:
            communities[comm_id] = []
        communities[comm_id].append(node)
    
    return communities


def find_communities(G: "nx.DiGraph", algorithm: str = "auto") -> dict[int, list[str]]:
    """
    Detect communities using the best available algorithm.
    
    Args:
        G: NetworkX directed graph
        algorithm: "leiden", "louvain", or "auto" (default, uses Leiden if available)
    
    Returns dict: community_id -> list of node IDs.
    """
    if algorithm == "leiden" or (algorithm == "auto" and HAS_LEIDEN):
        return find_communities_leiden(G)
    else:
        return find_communities_louvain(G)


def find_bridges(G: "nx.DiGraph", limit: int = 50) -> list[tuple[str, str]]:
    """
    Find bridge edges whose removal would disconnect the graph.
    
    These are critical coupling points - potential refactoring targets.
    """
    if nx is None:
        return []
    
    # Bridges only defined for undirected graphs
    undirected = G.to_undirected()
    bridges = list(nx.bridges(undirected))
    return bridges[:limit]


def shortest_path(G: "nx.DiGraph", source: str, target: str) -> list[str]:
    """
    Find shortest path between two nodes.
    
    Accepts either full ID or just function name (will search).
    """
    if nx is None:
        return []
    
    # Resolve partial names to full IDs
    def resolve(name):
        if name in G.nodes:
            return name
        for node_id in G.nodes:
            if f"|{name}|" in node_id or node_id.endswith(f"|{name}"):
                return node_id
        # Try name attribute
        for node_id, info in G.nodes(data=True):
            if info.get("name") == name:
                return node_id
        return None
    
    src = resolve(source)
    tgt = resolve(target)
    
    if not src or not tgt:
        return []
    
    try:
        return nx.shortest_path(G, src, tgt)
    except nx.NetworkXNoPath:
        return []


def suggest_refactoring_cuts(G: "nx.DiGraph", top_n: int = 10) -> list[dict]:
    """
    Suggest edges to remove that would best decouple the graph.
    
    Uses edge betweenness: edges that appear on many shortest paths.
    Removing these would create more isolated clusters.
    """
    if nx is None:
        return []
    
    # Sample for performance
    k = min(200, len(G.nodes)) if len(G.nodes) > 500 else None
    eb = nx.edge_betweenness_centrality(G, k=k, normalized=True)
    
    sorted_edges = sorted(eb.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    results = []
    for (src, tgt), centrality in sorted_edges:
        src_name = G.nodes.get(src, {}).get("name", src)
        tgt_name = G.nodes.get(tgt, {}).get("name", tgt)
        results.append({
            "source": src,
            "target": tgt,
            "source_name": src_name,
            "target_name": tgt_name,
            "centrality": centrality,
            "recommendation": f"Consider extracting {tgt_name} or introducing interface"
        })
    
    return results


def analyze_full(graph_path: str | Path, top_n: int = 20) -> GraphAnalysisResult:
    """Run full analysis on a graph."""
    G = load_graph(graph_path)
    
    result = GraphAnalysisResult(
        node_count=len(G.nodes),
        edge_count=len(G.edges),
    )
    
    print(f"📊 Analyzing graph: {result.node_count} nodes, {result.edge_count} edges")
    
    print("🔍 Finding bottlenecks (betweenness centrality)...")
    result.bottlenecks = find_bottlenecks(G, top_n=top_n)
    
    print("📈 Computing PageRank...")
    result.top_pagerank = find_pagerank(G, top_n=top_n)
    
    print("🧩 Detecting communities...")
    result.communities = find_communities(G)
    print(f"   Found {len(result.communities)} communities")
    
    print("🌉 Finding bridge edges...")
    result.bridges = find_bridges(G)
    
    return result


def generate_report(result: GraphAnalysisResult, output_path: str | Path = None) -> str:
    """Generate markdown report from analysis results."""
    lines = [
        "# 🔬 Graph Analysis Report",
        "",
        f"**Nodes:** {result.node_count} | **Edges:** {result.edge_count} | **Communities:** {len(result.communities)}",
        "",
        "---",
        "",
        "## 🚨 Bottleneck Functions (High Betweenness Centrality)",
        "",
        "These nodes appear on many shortest paths—coupling hotspots that everything flows through.",
        "",
        "| Rank | Function | File | In | Out | Centrality |",
        "|-----:|----------|------|---:|----:|-----------:|",
    ]
    
    for i, node in enumerate(result.bottlenecks[:15], 1):
        lines.append(f"| {i} | `{node.name}` | {node.file} | {node.in_degree} | {node.out_degree} | {node.betweenness:.4f} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 📈 Most Important Nodes (PageRank)",
        "",
        "Nodes that many other important nodes depend on.",
        "",
        "| Rank | Function | File | PageRank |",
        "|-----:|----------|------|--------:|",
    ])
    
    for i, node in enumerate(result.top_pagerank[:15], 1):
        lines.append(f"| {i} | `{node.name}` | {node.file} | {node.pagerank:.6f} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 🧩 Community Summary",
        "",
        f"Detected **{len(result.communities)}** natural clusters.",
        "",
        "| Community | Size | Sample Members |",
        "|----------:|-----:|----------------|",
    ])
    
    for comm_id in sorted(result.communities.keys(), key=lambda k: len(result.communities[k]), reverse=True)[:10]:
        members = result.communities[comm_id]
        sample = [m.split("|")[-2] if "|" in m else m[:30] for m in members[:3]]
        lines.append(f"| {comm_id} | {len(members)} | {', '.join(sample)} |")
    
    if result.bridges:
        lines.extend([
            "",
            "---",
            "",
            "## 🌉 Critical Bridge Edges",
            "",
            "Removing these edges would split the graph—key coupling points.",
            "",
        ])
        for src, tgt in result.bridges[:10]:
            src_short = src.split("|")[-2] if "|" in src else src[:30]
            tgt_short = tgt.split("|")[-2] if "|" in tgt else tgt[:30]
            lines.append(f"- `{src_short}` → `{tgt_short}`")
    
    report = "\n".join(lines)
    
    if output_path:
        Path(output_path).write_text(report, encoding="utf-8")
        print(f"📝 Report saved to: {output_path}")
    
    return report


# CLI entry point
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python graph_analyzer.py <graph.json> [--report output.md]")
        sys.exit(1)
    
    graph_path = sys.argv[1]
    output_path = None
    
    if "--report" in sys.argv:
        idx = sys.argv.index("--report")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]
    
    result = analyze_full(graph_path)
    report = generate_report(result, output_path)
    
    if not output_path:
        print(report)
