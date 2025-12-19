"""
God Class Strangler - Architecture Prescription Engine

Analyzes detected God Classes and generates actionable refactoring blueprints
using the Strangler Fig pattern.

Usage:
    from prescriptions.god_class_strangler import generate_prescription
    prescription = generate_prescription(graph_path, god_class_file)
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_graph(graph_path: str | Path) -> dict:
    """Load the Spectrometer graph.json output."""
    with open(graph_path) as f:
        return json.load(f)


def find_god_class_nodes(graph: dict, god_class_file: str) -> list[dict]:
    """Find all nodes belonging to a God Class file."""
    # Graph uses 'components' dict, not 'nodes' list
    components = graph.get("components", {})
    nodes = []
    
    for comp_id, comp_data in components.items():
        if isinstance(comp_data, dict):
            file_path = comp_data.get("file", "") or comp_data.get("rel_file", "")
            if god_class_file in file_path:
                comp_data["id"] = comp_id
                nodes.append(comp_data)
    
    return nodes


def get_outgoing_edges(graph: dict, node_ids: set) -> list[dict]:
    """Get edges originating from a set of node IDs."""
    edges = graph.get("edges", [])
    return [e for e in edges if e.get("source") in node_ids]


def cluster_by_prefix(nodes: list[dict]) -> dict[str, list[dict]]:
    """
    Cluster nodes by function name prefix patterns.
    
    Examples:
        sendJson, sendText, sendCsv -> "send*" cluster
        parseBodyJson, parseBodyBuffer -> "parseBody*" cluster
        buildRecentMonthWindow, buildPluggyConnectUrl -> "build*" cluster
    """
    clusters = defaultdict(list)
    
    # Common action prefixes that indicate cohesive functionality
    prefix_patterns = [
        (r"^(send|emit|publish)", "io_output"),
        (r"^(parse|read|load|fetch|get)", "io_input"),
        (r"^(build|create|make|construct|generate)", "factory"),
        (r"^(validate|check|is|has|ensure|verify)", "validation"),
        (r"^(handle|on|process)", "handler"),
        (r"^(compute|calculate|sum|count)", "computation"),
        (r"^(normalize|transform|map|convert)", "transformation"),
        (r"^(extract|find|filter|search)", "extraction"),
        (r"^(save|write|persist|store|upsert|delete)", "persistence"),
        (r"^(run|execute|trigger|invoke)", "execution"),
    ]
    
    for node in nodes:
        name = node.get("name", "")
        matched = False
        
        for pattern, cluster_name in prefix_patterns:
            if re.match(pattern, name, re.IGNORECASE):
                clusters[cluster_name].append(node)
                matched = True
                break
        
        if not matched:
            clusters["unclustered"].append(node)
    
    return dict(clusters)


def cluster_by_domain(nodes: list[dict], edges: list[dict]) -> dict[str, list[dict]]:
    """
    Cluster nodes by domain keywords in their names.
    """
    domain_keywords = {
        "pluggy": "pluggy_integration",
        "viz": "visualization",
        "cache": "caching",
        "transaction": "transactions",
        "account": "accounts",
        "connection": "connections",
        "mock": "mocking",
        "inventory": "inventory",
        "assistant": "assistant",
        "csv": "csv_import",
        "entity": "entities",
        "bill": "billing",
        "loan": "loans",
        "investment": "investments",
        "identity": "identity",
        "finance": "finance",
        "diag": "diagnostics",
        "error": "error_handling",
        "api": "api_layer",
        "db": "database",
        "webhook": "webhooks",
    }
    
    clusters = defaultdict(list)
    
    for node in nodes:
        name = node.get("name", "").lower()
        matched = False
        
        for keyword, domain in domain_keywords.items():
            if keyword in name:
                clusters[domain].append(node)
                matched = True
                break
        
        if not matched:
            clusters["core"].append(node)
    
    return dict(clusters)


def generate_extraction_order(clusters: dict[str, list[dict]]) -> list[dict]:
    """
    Generate recommended extraction order based on cluster size and coupling.
    
    Extraction priority:
    1. Leaf clusters (few outgoing deps) - easiest to extract
    2. Utility clusters (validation, transformation) - reusable
    3. I/O clusters - clear boundaries
    4. Domain clusters - business logic
    5. Core/unclustered - hardest, do last
    """
    priority_order = [
        "validation",
        "transformation",
        "extraction",
        "factory",
        "computation",
        "io_output",
        "io_input",
        "caching",
        "error_handling",
        "diagnostics",
        "mocking",
        "csv_import",
        "webhooks",
        "pluggy_integration",
        "visualization",
        "transactions",
        "accounts",
        "connections",
        "inventory",
        "billing",
        "loans",
        "investments",
        "identity",
        "finance",
        "assistant",
        "api_layer",
        "entities",
        "database",
        "persistence",
        "execution",
        "handler",
        "core",
        "unclustered",
    ]
    
    extraction_plan = []
    seen = set()
    
    for cluster_name in priority_order:
        if cluster_name in clusters and cluster_name not in seen:
            nodes = clusters[cluster_name]
            if nodes:
                extraction_plan.append({
                    "cluster": cluster_name,
                    "node_count": len(nodes),
                    "functions": [n.get("name", "unknown") for n in nodes[:10]],  # Top 10
                    "suggested_path": f"lib/{cluster_name}/",
                    "priority": len(extraction_plan) + 1,
                })
                seen.add(cluster_name)
    
    # Add any remaining clusters not in priority order
    for cluster_name, nodes in clusters.items():
        if cluster_name not in seen and nodes:
            extraction_plan.append({
                "cluster": cluster_name,
                "node_count": len(nodes),
                "functions": [n.get("name", "unknown") for n in nodes[:10]],
                "suggested_path": f"lib/{cluster_name}/",
                "priority": len(extraction_plan) + 1,
            })
    
    return extraction_plan


def generate_mermaid_diagram(clusters: dict[str, list[dict]], god_class_file: str) -> str:
    """Generate a Mermaid diagram showing the proposed decomposition."""
    lines = [
        "graph TD",
        f'    subgraph GOD_CLASS["{god_class_file} (God Class)"]',
    ]
    
    for cluster_name, nodes in clusters.items():
        if len(nodes) > 0:
            safe_name = cluster_name.replace("-", "_").upper()
            lines.append(f'        {safe_name}["{cluster_name} ({len(nodes)})"]')
    
    lines.append("    end")
    lines.append("")
    lines.append("    subgraph PROPOSED[Proposed Extraction]")
    
    for cluster_name, nodes in clusters.items():
        if len(nodes) > 2:  # Only show significant clusters
            safe_name = cluster_name.replace("-", "_").upper()
            lines.append(f'        NEW_{safe_name}["lib/{cluster_name}/ ({len(nodes)})"]')
    
    lines.append("    end")
    lines.append("")
    
    # Add extraction arrows
    for cluster_name, nodes in clusters.items():
        if len(nodes) > 2:
            safe_name = cluster_name.replace("-", "_").upper()
            lines.append(f"    {safe_name} -.-> NEW_{safe_name}")
    
    return "\n".join(lines)


def generate_prescription(
    graph_path: str | Path,
    god_class_file: str,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    Generate a complete refactoring prescription for a God Class.
    
    Args:
        graph_path: Path to Spectrometer graph.json
        god_class_file: Filename of the God Class (e.g., "server.js")
        output_path: Optional path to write prescription JSON
    
    Returns:
        Prescription dict with clusters, extraction plan, and Mermaid diagram
    """
    graph = load_graph(graph_path)
    
    # Find all nodes in the God Class
    god_nodes = find_god_class_nodes(graph, god_class_file)
    god_node_ids = {n.get("id") for n in god_nodes}
    
    # Get edges for coupling analysis
    edges = get_outgoing_edges(graph, god_node_ids)
    
    # Cluster by both prefix and domain
    prefix_clusters = cluster_by_prefix(god_nodes)
    domain_clusters = cluster_by_domain(god_nodes, edges)
    
    # Merge clusters (domain takes precedence)
    merged_clusters = {**prefix_clusters, **domain_clusters}
    
    # Generate extraction order
    extraction_plan = generate_extraction_order(merged_clusters)
    
    # Generate Mermaid diagram
    mermaid = generate_mermaid_diagram(merged_clusters, god_class_file)
    
    # Calculate metrics
    total_nodes = len(god_nodes)
    clustered_nodes = sum(len(nodes) for name, nodes in merged_clusters.items() 
                         if name not in ["unclustered", "core"])
    
    # Build detailed cluster metadata
    cluster_details = {}
    for cluster_name, nodes in merged_clusters.items():
        if not nodes:
            continue
            
        functions = []
        for node in nodes:
            func_info = {
                "name": node.get("name", "unknown"),
                "line": node.get("line", 0),
                "symbol_kind": node.get("symbol_kind", "unknown"),
                "type": node.get("type", "unknown"),
                "purpose": node.get("purpose", ""),
                "id": node.get("id", "")
            }
            functions.append(func_info)
        
        # Sort by line number
        functions.sort(key=lambda x: x["line"])
        
        cluster_details[cluster_name] = {
            "count": len(nodes),
            "functions": functions,
            "location": f"{god_class_file}:{functions[0]['line']}-{functions[-1]['line']}" if functions else god_class_file
        }
    
    prescription = {
        "god_class_file": god_class_file,
        "total_nodes": total_nodes,
        "total_edges": len(edges),
        "clustered_nodes": clustered_nodes,
        "unclustered_nodes": total_nodes - clustered_nodes,
        "cluster_count": len([c for c in merged_clusters if merged_clusters[c]]),
        "clusters": {name: len(nodes) for name, nodes in merged_clusters.items()},
        "cluster_details": cluster_details,  # NEW: detailed metadata
        "extraction_plan": extraction_plan,
        "mermaid_diagram": mermaid,
        "strangler_strategy": {
            "phase_1": "Extract utility functions (validation, transformation, factory)",
            "phase_2": "Extract I/O layer (sendJson, parseBody, etc.)",
            "phase_3": "Extract domain modules (pluggy, viz, transactions)",
            "phase_4": "Thin remaining file to pure orchestration",
        },
    }
    
    if output_path:
        with open(output_path, "w") as f:
            json.dump(prescription, f, indent=2)
    
    return prescription


def format_prescription_report(prescription: dict) -> str:
    """Format prescription as a human-readable Markdown report."""
    lines = [
        f"# 🏗️ Refactoring Prescription: {prescription['god_class_file']}",
        "",
        "## Diagnosis",
        "",
        f"- **Total Functions/Nodes:** {prescription['total_nodes']}",
        f"- **Internal Edges:** {prescription['total_edges']}",
        f"- **Clusterable:** {prescription['clustered_nodes']} ({prescription['clustered_nodes']*100//prescription['total_nodes']}%)",
        f"- **Identified Clusters:** {prescription['cluster_count']}",
        "",
        "## Cluster Breakdown",
        "",
        "| Cluster | Node Count | Priority |",
        "|---------|----------:|:--------:|",
    ]
    
    for step in prescription["extraction_plan"][:15]:  # Top 15
        lines.append(f"| `{step['cluster']}` | {step['node_count']} | {step['priority']} |")
    
    lines.extend([
        "",
        "## Strangler Fig Strategy",
        "",
    ])
    
    for phase, description in prescription["strangler_strategy"].items():
        lines.append(f"**{phase.replace('_', ' ').title()}:** {description}")
    
    lines.extend([
        "",
        "## Proposed Architecture",
        "",
        "```mermaid",
        prescription["mermaid_diagram"],
        "```",
        "",
        "## Extraction Order",
        "",
    ])
    
    for i, step in enumerate(prescription["extraction_plan"][:10], 1):
        funcs = ", ".join(step["functions"][:5])
        if len(step["functions"]) > 5:
            funcs += f", ... (+{len(step['functions'])-5} more)"
        lines.append(f"{i}. **{step['suggested_path']}** — {step['node_count']} functions")
        lines.append(f"   - Examples: `{funcs}`")
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python god_class_strangler.py <graph.json> <god_class_file>")
        sys.exit(1)
    
    graph_path = sys.argv[1]
    god_class_file = sys.argv[2]
    
    prescription = generate_prescription(graph_path, god_class_file)
    report = format_prescription_report(prescription)
    print(report)
