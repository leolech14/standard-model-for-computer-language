#!/usr/bin/env python3
"""
📊 CHART DATA EXTRACTOR
Extracts real metrics from Spectrometer outputs for paper charts.
Outputs JSON that can be consumed by Chart.js or other viz tools.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Any


@dataclass
class CodebaseMetrics:
    """Metrics for a single codebase analysis."""
    name: str
    language: str
    files: int
    entities: int  # L2+L3 particles
    nodes: int     # all graph nodes
    edges: int
    by_phase: Dict[str, int]
    by_family: Dict[str, int]
    by_atom: Dict[str, int]
    top_functions: List[Dict[str, Any]]
    antimatter: Dict[str, int]


def extract_metrics(output_dir: Path, name: str, language: str) -> CodebaseMetrics:
    """Extract all metrics from a Spectrometer output directory."""
    
    # Load semantic IDs
    sids_path = output_dir / "semantic_ids.json"
    sids = []
    if sids_path.exists():
        with open(sids_path) as f:
            data = json.load(f)
            sids = data.get("ids", [])
    
    # Load graph
    graph_path = output_dir / "graph.json"
    nodes, edges = 0, 0
    if graph_path.exists():
        with open(graph_path) as f:
            graph = json.load(f)
            nodes = len(graph.get("nodes", []))
            edges = len(graph.get("edges", graph.get("relationships", [])))
    
    # Load learning report for file count
    report_path = output_dir / "learning_report.json"
    files = 0
    if report_path.exists():
        with open(report_path) as f:
            report = json.load(f)
            files = report.get("total_files", 0)
    
    # Count by phase/family/atom
    by_phase = Counter()
    by_family = Counter()
    by_atom = Counter()
    
    for sid in sids:
        if "|" in sid:
            parts = sid.split("|")
            atom_id = parts[0]  # e.g., LOG.FNC.M
            
            id_parts = atom_id.split(".")
            if len(id_parts) >= 2:
                phase = id_parts[0]
                family = id_parts[1]
                
                phase_map = {"DAT": "DATA", "LOG": "LOGIC", "ORG": "ORGANIZATION", "EXE": "EXECUTION"}
                phase_name = phase_map.get(phase, phase)
                
                by_phase[phase_name] += 1
                by_family[family] += 1
                by_atom[atom_id] += 1
    
    # Load redundancy report if exists
    redundancy_path = output_dir / "REDUNDANCY_REPORT.md"
    antimatter = {
        "god_functions": 0,
        "pass_through": 0,
        "semantic_duplicates": 0,
        "structural_duplicates": 0
    }
    
    if redundancy_path.exists():
        content = redundancy_path.read_text()
        # Parse counts from the report
        import re
        sem_match = re.search(r"(\d+)\s+semantic duplicate groups", content)
        struct_match = re.search(r"(\d+)\s+structural duplicate groups", content)
        god_match = re.search(r"(\d+)\s+over-engineering signals", content)
        
        if sem_match:
            antimatter["semantic_duplicates"] = int(sem_match.group(1))
        if struct_match:
            antimatter["structural_duplicates"] = int(struct_match.group(1))
        if god_match:
            antimatter["god_functions"] = int(god_match.group(1))
    
    # Get top functions by call count
    top_functions = []
    for sid in sids[:20]:
        if "|" in sid:
            parts = sid.split("|")
            if len(parts) >= 4:
                name_part = parts[2]
                calls_match = [p for p in parts if p.startswith("calls:")]
                calls = int(calls_match[0].replace("calls:", "")) if calls_match else 0
                top_functions.append({"name": name_part, "calls": calls})
    
    top_functions.sort(key=lambda x: -x["calls"])
    
    return CodebaseMetrics(
        name=name,
        language=language,
        files=files,
        entities=len(sids),
        nodes=nodes,
        edges=edges,
        by_phase=dict(by_phase),
        by_family=dict(by_family),
        by_atom=dict(by_atom.most_common(30)),
        top_functions=top_functions[:10],
        antimatter=antimatter
    )


def aggregate_metrics(metrics_list: List[CodebaseMetrics]) -> Dict:
    """Aggregate metrics across multiple codebases."""
    
    total_entities = sum(m.entities for m in metrics_list)
    total_nodes = sum(m.nodes for m in metrics_list)
    total_edges = sum(m.edges for m in metrics_list)
    total_files = sum(m.files for m in metrics_list)
    
    # Aggregate phases
    phase_totals = Counter()
    for m in metrics_list:
        for phase, count in m.by_phase.items():
            phase_totals[phase] += count
    
    # Aggregate atoms
    atom_totals = Counter()
    for m in metrics_list:
        for atom, count in m.by_atom.items():
            atom_totals[atom] += count
    
    return {
        "summary": {
            "codebases": len(metrics_list),
            "total_files": total_files,
            "total_entities": total_entities,
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "avg_edges_per_node": round(total_edges / total_nodes, 2) if total_nodes else 0
        },
        "by_codebase": [asdict(m) for m in metrics_list],
        "phase_distribution": dict(phase_totals),
        "top_atoms": dict(atom_totals.most_common(20)),
        "chart_data": {
            "taxonomy": {
                "labels": ["DATA", "LOGIC", "ORGANIZATION", "EXECUTION"],
                "values": [26, 61, 45, 35],
                "description": "167 atoms by phase"
            },
            "validation": {
                "labels": [m.name for m in metrics_list],
                "entities": [m.entities for m in metrics_list],
                "nodes": [m.nodes for m in metrics_list],
                "edges": [m.edges for m in metrics_list]
            },
            "phase_distribution": {
                "labels": list(phase_totals.keys()),
                "values": list(phase_totals.values()),
                "percentages": {k: round(100*v/total_entities, 1) for k, v in phase_totals.items()}
            },
            "antimatter": {
                "labels": ["God Functions", "Pass-Through", "Semantic Dups", "Structural Dups"],
                "values": [
                    sum(m.antimatter.get("god_functions", 0) for m in metrics_list),
                    sum(m.antimatter.get("pass_through", 0) for m in metrics_list),
                    sum(m.antimatter.get("semantic_duplicates", 0) for m in metrics_list),
                    sum(m.antimatter.get("structural_duplicates", 0) for m in metrics_list)
                ]
            }
        }
    }


def main():
    base_dir = Path(__file__).resolve().parents[1]
    
    # Define codebases to analyze
    codebases = [
        (base_dir / "output/atman_final", "ATMAN", "Node.js"),
        (base_dir / "output/atman_current_20251219", "ATMAN (Current)", "Node.js"),
        (Path("/tmp/poetry_test"), "Poetry", "Python"),
        (Path("/tmp/spectrometer_self_test"), "Spectrometer", "Python+JS"),
    ]
    
    metrics_list = []
    
    print("📊 Extracting metrics from Spectrometer outputs...")
    print()
    
    for output_dir, name, language in codebases:
        if output_dir.exists():
            print(f"  → {name}: {output_dir}")
            m = extract_metrics(output_dir, name, language)
            metrics_list.append(m)
            print(f"     Files: {m.files}, Entities: {m.entities}, Nodes: {m.nodes}, Edges: {m.edges}")
    
    if not metrics_list:
        print("❌ No output directories found")
        return
    
    print()
    print("📈 Aggregating across codebases...")
    
    aggregated = aggregate_metrics(metrics_list)
    
    # Save to JSON for Chart.js consumption
    output_path = base_dir / "output" / "chart_data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(aggregated, f, indent=2)
    
    print(f"✅ Saved to: {output_path}")
    print()
    print("=== SUMMARY ===")
    print(f"   Codebases: {aggregated['summary']['codebases']}")
    print(f"   Total Entities: {aggregated['summary']['total_entities']:,}")
    print(f"   Total Nodes: {aggregated['summary']['total_nodes']:,}")
    print(f"   Total Edges: {aggregated['summary']['total_edges']:,}")
    print()
    print("Phase Distribution:")
    for phase, pct in aggregated["chart_data"]["phase_distribution"]["percentages"].items():
        print(f"   {phase}: {pct}%")


if __name__ == "__main__":
    main()
