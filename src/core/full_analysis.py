#!/usr/bin/env python3
"""
Collider Full Analysis
Single command for complete deterministic analysis with all theoretical frameworks.

Usage:
    ./collider full <path> [--output <dir>]

Outputs:
    - output_llm-oriented_<project>_<timestamp>.json (LLM knowledge bundle)
    - output_human-readable_<project>_<timestamp>.html (human report + graph)
"""
import json
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional


# =============================================================================
# FILE-CENTRIC VIEW: Bridges atom-centric analysis with file-based navigation
# =============================================================================

def _resolve_output_dir(target: Path, output_dir: Optional[str]) -> Path:
    """Resolve the canonical output directory."""
    if output_dir:
        return Path(output_dir)
    if target.is_dir():
        return target / ".collider"
    return target.parent / ".collider"


def build_file_index(nodes: List[Dict], edges: List[Dict], target_path: str = "") -> Dict[str, Any]:
    """
    Build a file-centric index of atoms for hybrid navigation.

    This bridges the atom-centric paradigm (Collider's core insight) with
    traditional file-based navigation that developers expect.

    Returns:
        {
            "file_path": {
                "atoms": [atom_indices...],
                "atom_names": ["name1", "name2"...],
                "line_range": [start, end],
                "atom_count": N,
                "imports": [...],
                "internal_edges": N,  # edges within this file
                "external_edges": N,  # edges to other files
                "purpose": "inferred purpose"
            }
        }
    """
    files_index: Dict[str, Dict[str, Any]] = {}

    # Group nodes by file
    for idx, node in enumerate(nodes):
        file_path = node.get("file_path", "")
        if not file_path:
            continue

        if file_path not in files_index:
            files_index[file_path] = {
                "atoms": [],
                "atom_names": [],
                "atom_types": [],
                "line_range": [float('inf'), 0],
                "atom_count": 0,
                "classes": [],
                "functions": [],
                "imports": [],
                "internal_edges": 0,
                "external_edges": 0,
                "purpose": ""
            }

        entry = files_index[file_path]
        entry["atoms"].append(idx)
        entry["atom_names"].append(node.get("name", ""))
        entry["atom_types"].append(node.get("type", "Unknown"))
        entry["atom_count"] += 1

        # Track line range
        line = node.get("line", 0)
        end_line = node.get("end_line", line)
        if line > 0:
            entry["line_range"][0] = min(entry["line_range"][0], line)
            entry["line_range"][1] = max(entry["line_range"][1], end_line)

        # Categorize by symbol kind
        kind = node.get("symbol_kind", "")
        name = node.get("name", "")
        if kind == "class":
            entry["classes"].append(name)
        elif kind in ("function", "method"):
            entry["functions"].append(name)

    # Compute edges (internal vs external)
    node_to_file = {idx: nodes[idx].get("file_path", "") for idx in range(len(nodes))}
    node_name_to_file = {n.get("name", ""): n.get("file_path", "") for n in nodes}

    for edge in edges:
        source = edge.get("source", "")
        target = edge.get("target", "")

        source_file = node_name_to_file.get(source, "")
        target_file = node_name_to_file.get(target, "")

        if source_file and source_file in files_index:
            if source_file == target_file:
                files_index[source_file]["internal_edges"] += 1
            else:
                files_index[source_file]["external_edges"] += 1

    # Infer file purpose from dominant atom types
    for file_path, entry in files_index.items():
        types = Counter(entry["atom_types"])
        dominant = types.most_common(1)
        if dominant:
            dom_type, count = dominant[0]
            if dom_type != "Unknown":
                entry["purpose"] = f"{dom_type}-dominant ({count}/{entry['atom_count']})"
            else:
                # Infer from file name
                fname = Path(file_path).stem.lower()
                if "test" in fname:
                    entry["purpose"] = "Test module"
                elif "util" in fname or "helper" in fname:
                    entry["purpose"] = "Utility module"
                elif "model" in fname or "entity" in fname:
                    entry["purpose"] = "Domain model"
                elif "service" in fname:
                    entry["purpose"] = "Service layer"
                elif "controller" in fname or "handler" in fname:
                    entry["purpose"] = "Interface layer"
                else:
                    entry["purpose"] = "General module"

        # Fix line_range if no lines found
        if entry["line_range"][0] == float('inf'):
            entry["line_range"] = [0, 0]

        # Clean up atom_types (don't need in output, was for computation)
        del entry["atom_types"]

    return files_index


def build_file_boundaries(files_index: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build file boundary data for visualization.

    Returns a list of boundary objects that can be used to draw
    visual separators between files in the atom graph.
    """
    boundaries = []

    for file_path, data in files_index.items():
        if data["atom_count"] == 0:
            continue

        boundaries.append({
            "file": file_path,
            "file_name": Path(file_path).name,
            "atom_indices": data["atoms"],
            "atom_count": data["atom_count"],
            "line_range": data["line_range"],
            "classes": data["classes"],
            "functions": data["functions"][:10],  # Limit for viz
            "cohesion": data["internal_edges"] / max(1, data["internal_edges"] + data["external_edges"]),
            "purpose": data["purpose"]
        })

    # Sort by file path for consistent ordering
    boundaries.sort(key=lambda b: b["file"])

    return boundaries


def _calculate_theory_completeness(nodes: List[Dict]) -> Dict[str, Any]:
    """
    Calculate theory completeness metrics for the analysis output.
    
    Measures what percentage of applicable Standard Model elements
    are captured in the analysis.
    """
    if not nodes:
        return {'overall_score': 0, 'error': 'No nodes'}
    
    total = len(nodes)
    
    # D1_WHAT (atom assignment)
    d1_what_assigned = sum(
        1 for n in nodes
        if n.get('dimensions', {}).get('D1_WHAT')
        and n['dimensions']['D1_WHAT'] != 'Unknown'
    )
    
    # D1_ECOSYSTEM
    d1_ecosystem_assigned = sum(
        1 for n in nodes
        if n.get('dimensions', {}).get('D1_ECOSYSTEM')
    )
    
    # React hook metadata
    react_components = [
        n for n in nodes
        if n.get('dimensions', {}).get('D1_WHAT', '').startswith('EXT.REACT.')
    ]
    hooks_enriched = sum(
        1 for n in react_components
        if n.get('metadata', {}).get('hooks_used') is not None
    )
    
    # K8s metadata
    k8s_resources = [
        n for n in nodes
        if n.get('dimensions', {}).get('D1_ECOSYSTEM') == 'kubernetes'
    ]
    k8s_kind_assigned = sum(
        1 for n in k8s_resources
        if n.get('metadata', {}).get('k8s_kind')
    )
    
    # Calculate percentages
    d1_what_pct = (d1_what_assigned / total) * 100
    d1_ecosystem_pct = (d1_ecosystem_assigned / total) * 100
    hooks_pct = (hooks_enriched / len(react_components) * 100) if react_components else 100.0
    k8s_pct = (k8s_kind_assigned / len(k8s_resources) * 100) if k8s_resources else 100.0
    
    # Overall score
    overall = (d1_what_pct * 0.4 + d1_ecosystem_pct * 0.3 + hooks_pct * 0.15 + k8s_pct * 0.15)
    
    return {
        'd1_what_percentage': round(d1_what_pct, 1),
        'd1_ecosystem_percentage': round(d1_ecosystem_pct, 1),
        'hooks_metadata_percentage': round(hooks_pct, 1),
        'k8s_metadata_percentage': round(k8s_pct, 1),
        'overall_score': round(overall, 1)
    }


def compute_markov_matrix(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """
    Compute Markov transition matrix from call graph.
    P(A → B) = calls from A to B / total calls from A
    """
    # Build adjacency counts
    out_counts = defaultdict(lambda: defaultdict(int))
    out_totals = defaultdict(int)
    
    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        if source and target:
            out_counts[source][target] += 1
            out_totals[source] += 1
    
    # Compute probabilities
    transitions = {}
    for source, targets in out_counts.items():
        total = out_totals[source]
        transitions[source] = {
            target: count / total
            for target, count in targets.items()
        }
    
    # Summary stats
    high_entropy_nodes = []
    for source, probs in transitions.items():
        if len(probs) > 5:  # Calls many things
            high_entropy_nodes.append({
                'node': source.split(':')[-1] if ':' in source else source,
                'fanout': len(probs),
                'max_prob': max(probs.values()) if probs else 0
            })
    
    return {
        'total_transitions': len(transitions),
        'avg_fanout': sum(len(t) for t in transitions.values()) / len(transitions) if transitions else 0,
        'high_entropy_nodes': sorted(high_entropy_nodes, key=lambda x: -x['fanout'])[:10],
        'matrix_sample': {k: v for k, v in list(transitions.items())[:5]}  # Sample
    }


def detect_knots(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """
    Detect dependency knots (cycles) and tangles in the graph.
    - Cycles: A → B → C → A
    - Tangles: High bidirectional coupling between modules
    """
    # Build adjacency
    graph = defaultdict(set)
    reverse = defaultdict(set)
    
    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        if source and target:
            graph[source].add(target)
            reverse[target].add(source)
    
    # Find strongly connected components (simplified Tarjan-like)
    visited = set()
    on_stack = set()
    cycles = []
    
    def find_cycle(node: str, path: List[str]) -> bool:
        if node in on_stack:
            cycle_start = path.index(node)
            cycle = path[cycle_start:]
            if len(cycle) > 1:
                cycles.append(cycle)
            return True
        if node in visited:
            return False
        
        visited.add(node)
        on_stack.add(node)
        path.append(node)
        
        for neighbor in list(graph.get(node, set()))[:10]:  # Limit for perf
            find_cycle(neighbor, path)
        
        path.pop()
        on_stack.remove(node)
        return False
    
    # Check for cycles from each unvisited node (limited)
    for node in list(graph.keys())[:200]:
        if node not in visited:
            find_cycle(node, [])
    
    # Find bidirectional edges (tangles)
    bidirectional = []
    for source, targets in graph.items():
        for target in targets:
            if source in graph.get(target, set()):
                pair = tuple(sorted([source, target]))
                if pair not in [tuple(sorted([b['a'], b['b']])) for b in bidirectional]:
                    bidirectional.append({
                        'a': source.split(':')[-1] if ':' in source else source,
                        'b': target.split(':')[-1] if ':' in target else target
                    })
    
    # Compute knot score: 0 = no knots, 10 = severely tangled
    knot_score = min(10, len(cycles) * 2 + len(bidirectional) * 0.5)
    
    return {
        'cycles_detected': len(cycles),
        'bidirectional_edges': len(bidirectional),
        'knot_score': round(knot_score, 1),
        'sample_cycles': [c[:5] for c in cycles[:5]],  # First 5, truncated
        'sample_tangles': bidirectional[:10]
    }


def compute_data_flow(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """
    Analyze data flow patterns across the codebase.
    """
    # Track flow by type
    flow_by_type = defaultdict(lambda: {'in': 0, 'out': 0})
    
    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        
        # Find source/target types
        source_type = None
        target_type = None
        for n in nodes:
            if n.get('id') == source:
                source_type = n.get('type', 'Unknown')
            if n.get('id') == target:
                target_type = n.get('type', 'Unknown')
        
        if source_type:
            flow_by_type[source_type]['out'] += 1
        if target_type:
            flow_by_type[target_type]['in'] += 1
    
    # Identify data sources and sinks
    sources = []  # High out, low in (data producers)
    sinks = []    # High in, low out (data consumers)
    
    for type_name, flow in flow_by_type.items():
        ratio = flow['out'] / flow['in'] if flow['in'] > 0 else flow['out']
        if ratio > 2 and flow['out'] > 10:
            sources.append({'type': type_name, 'ratio': round(ratio, 1), 'out': flow['out']})
        elif ratio < 0.5 and flow['in'] > 10:
            sinks.append({'type': type_name, 'ratio': round(ratio, 1), 'in': flow['in']})
    
    return {
        'flow_by_type': dict(flow_by_type),
        'data_sources': sorted(sources, key=lambda x: -x['out'])[:5],
        'data_sinks': sorted(sinks, key=lambda x: -x['in'])[:5],
        'total_flow_edges': len(edges)
    }


def run_full_analysis(target_path: str, output_dir: str = None, options: Dict[str, Any] = None) -> Dict:
    """Run complete analysis with all theoretical frameworks."""
    
    if options is None:
        options = {}
    
    start_time = time.time()
    target = Path(target_path).resolve()
    resolved_output_dir = _resolve_output_dir(target, output_dir)
    
    print("=" * 60)
    print("COLLIDER FULL ANALYSIS")
    print(f"Target: {target}")
    print("=" * 60)
    
    # Import analysis functions
    sys.path.insert(0, str(Path(__file__).parent))
    
    from unified_analysis import analyze
    from standard_model_enricher import enrich_with_standard_model
    from purpose_field import detect_purpose_field
    from execution_flow import detect_execution_flow
    from performance_predictor import predict_performance
    from roadmap_evaluator import RoadmapEvaluator
    from topology_reasoning import TopologyClassifier
    from semantic_cortex import ConceptExtractor
    # NOTE: standard_output_generator removed - consolidated into unified outputs
    
    # Stage 1: Base analysis
    print("\n🔬 Stage 1: Base Analysis...")
    analysis_options = dict(options)
    analysis_options.pop("roadmap", None)
    result = analyze(str(target), output_dir=str(resolved_output_dir), write_output=False, **analysis_options)
    nodes = result.nodes if hasattr(result, 'nodes') else result.get('nodes', [])
    edges = result.edges if hasattr(result, 'edges') else result.get('edges', [])
    unified_stats = getattr(result, 'stats', {}) if hasattr(result, 'stats') else result.get('stats', {})
    unified_classification = getattr(result, 'classification', {}) if hasattr(result, 'classification') else result.get('classification', {})
    unified_auto_discovery = getattr(result, 'auto_discovery', {}) if hasattr(result, 'auto_discovery') else result.get('auto_discovery', {})
    unified_dependencies = getattr(result, 'dependencies', {}) if hasattr(result, 'dependencies') else result.get('dependencies', {})
    unified_architecture = getattr(result, 'architecture', {}) if hasattr(result, 'architecture') else result.get('architecture', {})
    unified_llm_enrichment = getattr(result, 'llm_enrichment', {}) if hasattr(result, 'llm_enrichment') else result.get('llm_enrichment', {})
    unified_warnings = getattr(result, 'warnings', []) if hasattr(result, 'warnings') else result.get('warnings', [])
    unified_recommendations = getattr(result, 'recommendations', []) if hasattr(result, 'recommendations') else result.get('recommendations', [])
    print(f"   → {len(nodes)} nodes, {len(edges)} edges")
    
    # Stage 2: Standard Model enrichment
    print("\n🧬 Stage 2: Standard Model Enrichment...")
    nodes = enrich_with_standard_model(nodes)
    rpbl_count = sum(1 for n in nodes if n.get('rpbl'))
    print(f"   → {rpbl_count} nodes with RPBL scores")

    # Stage 2.5: Ecosystem discovery (hybrid T2 approach)
    print("\n🧭 Stage 2.5: Ecosystem Discovery...")
    try:
        from discovery_engine import discover_ecosystem_unknowns
        ecosystem_discovery = discover_ecosystem_unknowns(nodes)
        print(f"   → {ecosystem_discovery.get('total_unknowns', 0)} unknown ecosystem patterns")
    except Exception as e:
        ecosystem_discovery = {}
        print(f"   ⚠️ Ecosystem discovery skipped: {e}")
    
    # Stage 3: Purpose Field
    print("\n🎯 Stage 3: Purpose Field...")
    purpose_field = detect_purpose_field(nodes, edges)
    print(f"   → {len(purpose_field.nodes)} purpose nodes")
    print(f"   → {len(purpose_field.violations)} violations")
    
    # Stage 4: Execution Flow
    print("\n⚡ Stage 4: Execution Flow...")
    exec_flow = detect_execution_flow(nodes, edges, purpose_field)
    
    print(f"   → {len(exec_flow.entry_points)} entry points")
    print(f"   → {len(exec_flow.orphans)} orphans ({exec_flow.dead_code_percent}% dead code)")
    
    # Stage 5: Markov Matrix
    print("\n📊 Stage 5: Markov Transition Matrix...")
    markov = compute_markov_matrix(nodes, edges)
    print(f"   → {markov['total_transitions']} nodes with transitions")
    print(f"   → {markov['avg_fanout']:.1f} avg fanout")
    
    # Stage 6: Knot Detection
    print("\n🔗 Stage 6: Knot/Cycle Detection...")
    knots = detect_knots(nodes, edges)
    print(f"   → {knots['cycles_detected']} cycles detected")
    print(f"   → {knots['bidirectional_edges']} bidirectional edges")
    print(f"   → Knot score: {knots['knot_score']}/10")
    
    # Stage 7: Data Flow
    print("\n🌊 Stage 7: Data Flow Analysis...")
    data_flow = compute_data_flow(nodes, edges)
    print(f"   → {len(data_flow['data_sources'])} data sources")
    print(f"   → {len(data_flow['data_sinks'])} data sinks")
    
    # Stage 8: Performance Prediction
    print("\n⏱️  Stage 8: Performance Prediction...")
    try:
        perf = predict_performance(nodes, edges)
        perf_summary = perf.summary() if hasattr(perf, 'summary') else {}
    except Exception as e:
        print(f"   ⚠️  Performance prediction skipped: {e}")
        perf_summary = {}
    
    # Compute aggregate metrics
    total_time = time.time() - start_time
    
    # Type distribution
    types = Counter(n.get('type', 'Unknown') for n in nodes)
    
    # Ring distribution (Clean Architecture)
    rings = Counter(n.get('ring', 'unknown') for n in nodes)

    # Edge breakdown + KPIs
    edge_types = Counter(e.get('edge_type', 'unknown') for e in edges)
    total_edges = len(edges)
    unresolved_edges = sum(1 for e in edges if e.get('resolution') == 'unresolved')
    resolved_edges = total_edges - unresolved_edges
    edge_resolution_percent = (resolved_edges / total_edges * 100) if total_edges else 0.0
    call_edges = edge_types.get('calls', 0)
    import_edges = edge_types.get('imports', 0)
    call_ratio_percent = (call_edges / total_edges * 100) if total_edges else 0.0
    orphan_count = len(exec_flow.orphans)
    orphan_percent = (orphan_count / len(nodes) * 100) if nodes else 0.0
    reachability_percent = max(0.0, 100.0 - exec_flow.dead_code_percent)
    graph_density = (total_edges / (len(nodes) * (len(nodes) - 1))) if len(nodes) > 1 else 0.0
    
    # RPBL averages
    rpbl_sums = {'responsibility': 0, 'purity': 0, 'boundary': 0, 'lifecycle': 0}
    for n in nodes:
        rpbl = n.get('rpbl', {})
        for k in rpbl_sums:
            rpbl_sums[k] += rpbl.get(k, 0)
    rpbl_avgs = {k: round(v / len(nodes), 1) if nodes else 0 for k, v in rpbl_sums.items()}
    
    # Build complete output
    full_output = {
        'nodes': list(nodes),  # Required for report generator
        'edges': list(edges),  # Required for report generator
        'meta': {
            'target': str(target),
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'analysis_time_ms': int(total_time * 1000),
            'version': '4.0.0',
            'deterministic': True
        },
        'counts': {
            'nodes': len(nodes),
            'edges': len(edges),
            'files': len(set(n.get('file_path', '') for n in nodes)),
            'entry_points': len(exec_flow.entry_points),
            'orphans': len(exec_flow.orphans),
            'cycles': knots['cycles_detected']
        },
        'stats': unified_stats,
        'coverage': {
            'type_coverage': 100.0,
            'ring_coverage': (len(nodes) - rings.get('unknown', 0)) / len(nodes) * 100 if nodes else 0,
            'rpbl_coverage': rpbl_count / len(nodes) * 100 if nodes else 0,
            'dead_code_percent': exec_flow.dead_code_percent
        },
        'classification': unified_classification,
        'auto_discovery': unified_auto_discovery,
        'ecosystem_discovery': ecosystem_discovery,
        'dependencies': unified_dependencies,
        'architecture': unified_architecture,
        'llm_enrichment': unified_llm_enrichment,
        'warnings': unified_warnings,
        'recommendations': unified_recommendations,
        'theory_completeness': _calculate_theory_completeness(nodes),
        'distributions': {
            'types': dict(types.most_common(15)),
            'rings': dict(rings),
            'atoms': dict(Counter(n.get('atom', '') for n in nodes))
        },
        'edge_types': dict(edge_types),
        'rpbl_profile': rpbl_avgs,
        'kpis': {
            'nodes_total': len(nodes),
            'edges_total': total_edges,
            'edge_resolution_percent': round(edge_resolution_percent, 1),
            'resolved_edges': resolved_edges,
            'unresolved_edges': unresolved_edges,
            'call_edges': call_edges,
            'import_edges': import_edges,
            'call_ratio_percent': round(call_ratio_percent, 1),
            'reachability_percent': round(reachability_percent, 1),
            'dead_code_percent': round(exec_flow.dead_code_percent, 1),
            'orphan_count': orphan_count,
            'orphan_percent': round(orphan_percent, 1),
            'knot_score': knots.get('knot_score', 0),
            'cycles_detected': knots.get('cycles_detected', 0),
            'avg_fanout': round(markov.get('avg_fanout', 0.0), 2),
            'graph_density': round(graph_density, 4),
            'top_hub_count': 0,
            'topology_shape': 'UNKNOWN'
        },
        'purpose_field': purpose_field.summary(),
        'execution_flow': dict(exec_flow.summary(), **{
            'entry_points': exec_flow.entry_points,
            'orphans': exec_flow.orphans
        }),
        'markov': markov,
        'knots': knots,
        'data_flow': data_flow,
        'performance': perf_summary,
        'top_hubs': [],
        'orphans_list': exec_flow.orphans[:20]  # First 20
    }
    
    # Compute top hubs
    in_deg = Counter()
    for e in edges:
        in_deg[e.get('target', '')] += 1
    for node_id, deg in in_deg.most_common(10):
        name = node_id.split(':')[-1] if ':' in node_id else node_id.split('/')[-1]
        full_output['top_hubs'].append({'name': name, 'in_degree': deg})
    full_output['kpis']['top_hub_count'] = len(full_output['top_hubs'])

    # ==========================================================================
    # FILE-CENTRIC VIEW: Hybrid atom/file navigation
    # ==========================================================================
    print("\n📁 Building file index...")
    files_index = build_file_index(nodes, edges, str(target))
    file_boundaries = build_file_boundaries(files_index)

    full_output['files'] = files_index
    full_output['file_boundaries'] = file_boundaries
    full_output['counts']['files_with_atoms'] = len(files_index)

    print(f"   → {len(files_index)} files indexed")
    print(f"   → {sum(f['atom_count'] for f in file_boundaries)} atoms mapped to files")

    # Save output
    out_path = resolved_output_dir
    
    out_path.mkdir(parents=True, exist_ok=True)

    # NOTE: The LLM-oriented output JSON is the single source of truth for analysis results.

    # Stage 9: Roadmap Evaluation
    print("\n🛣️  Stage 9: Roadmap Evaluation...")
    roadmap_name = options.get('roadmap')
    if roadmap_name:
        try:
            roadmap_path = Path(__file__).parent / "roadmaps" / f"{roadmap_name}.json"
            if roadmap_path.exists():
                evaluator = RoadmapEvaluator(str(roadmap_path))
                # Collect all file paths
                all_files = [str(f) for f in Path(target_path).rglob('*') if f.is_file()]
                roadmap_result = evaluator.evaluate(all_files)
                full_output['roadmap'] = roadmap_result
                print(f"   → Roadmap '{roadmap_name}' analyzed: {roadmap_result['readiness_score']:.0f}% ready")
            else:
                print(f"   ⚠️ Roadmap '{roadmap_name}' not found in roadmaps directory")
        except Exception as e:
            print(f"   ⚠️ Roadmap analysis failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("   → Skipped (no --roadmap specified)")

    # Stage 10: Visual Topology Analysis
    print("\n🧠 Stage 10: Visual Reasoning...")
    try:
        topo = TopologyClassifier()
        topology_result = topo.classify(nodes, edges)
        full_output['topology'] = topology_result
        full_output['kpis']['topology_shape'] = topology_result.get('shape', 'UNKNOWN')
        print(f"   → Visual Shape: {topology_result['shape']}")
        print(f"   → Description: {topology_result['description']}")
    except Exception as e:
        print(f"   ⚠️ Topology analysis failed: {e}")

    # Stage 11: Semantic Cortex (Concept Extraction)
    print("\n🧠 Stage 11: Semantic Cortex...")
    try:
        cortex = ConceptExtractor()
        semantics = cortex.extract_concepts(nodes)
        full_output['semantics'] = semantics
        print(f"   → Domain Inference: {semantics['domain_inference']}")
        print(f"   → Top Concepts: {', '.join([t['term'] for t in semantics['top_concepts'][:5]])}")
    except Exception as e:
        print(f"   ⚠️ Semantic analysis failed: {e}")

    # ==========================================================================
    # OUTPUT CONSOLIDATION: 2 files only
    # 1. output_llm-oriented_<project>_<timestamp>.json - Structured knowledge bundle
    # 2. output_human-readable_<project>_<timestamp>.html - Visual report (embeds Brain Download)
    # ==========================================================================

    # Generate Brain Download content (for embedding in HTML)
    from brain_download import generate_brain_download
    brain_content = generate_brain_download(full_output)
    full_output['brain_download'] = brain_content  # Embed in JSON for HTML access

    # Stage 12: Write consolidated outputs
    print("\n📦 Stage 12: Generating Consolidated Outputs...")

    unified_json = None
    viz_file = None
    try:
        from src.core.output_generator import generate_outputs
        outputs = generate_outputs(full_output, out_path, target_name=target.name)
        unified_json = outputs["llm"]
        viz_file = outputs["html"]
        print(f"   → Data: {unified_json}")
        print(f"   → Visual: {viz_file}")
    except Exception as e:
        print(f"   ⚠️ Output generation failed: {e}")

    print("\n" + "=" * 60)
    print("✅ FULL ANALYSIS COMPLETE")
    print(f"   Time: {total_time:.1f}s")
    if unified_json:
        print(f"   Data:   {unified_json}")
    if viz_file:
        print(f"   Visual: {viz_file}")
    print("=" * 60)
    
    return full_output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python full_analysis.py <path> [--output <dir>]")
        sys.exit(1)
    
    target = sys.argv[1]
    output_dir = None
    
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
    
    run_full_analysis(target, output_dir)
