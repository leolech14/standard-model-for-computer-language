#!/usr/bin/env python3
"""
Collider Full Analysis
Single command for complete deterministic analysis with all theoretical frameworks.

Usage:
    ./collider full <path> [--output <dir>]
    
Outputs:
    - unified_analysis.json (complete graph with all enrichments)
    - full_analysis.json (comprehensive metrics and diagnostics)
"""
import json
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any


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
    # NOTE: standard_output_generator removed - consolidated into HTML viz
    
    # Import Visualization Engine (Dynamic Import to handle relative paths)
    import importlib.util
    try:
        viz_path = Path(__file__).parent.parent.parent / "tools" / "visualize_graph.py"
        spec = importlib.util.spec_from_file_location("visualize_graph", viz_path)
        visualize_graph = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(visualize_graph)
    except Exception as e:
        print(f"⚠️ Visualization module load warning: {e}")
        visualize_graph = None
    
    # Stage 1: Base analysis
    print("\n🔬 Stage 1: Base Analysis...")
    result = analyze(str(target), output_dir=output_dir)
    nodes = result.nodes if hasattr(result, 'nodes') else result.get('nodes', [])
    edges = result.edges if hasattr(result, 'edges') else result.get('edges', [])
    print(f"   → {len(nodes)} nodes, {len(edges)} edges")
    
    # Stage 2: Standard Model enrichment
    print("\n🧬 Stage 2: Standard Model Enrichment...")
    nodes = enrich_with_standard_model(nodes)
    rpbl_count = sum(1 for n in nodes if n.get('rpbl'))
    print(f"   → {rpbl_count} nodes with RPBL scores")
    
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
        'coverage': {
            'type_coverage': 100.0,
            'ring_coverage': (len(nodes) - rings.get('unknown', 0)) / len(nodes) * 100 if nodes else 0,
            'rpbl_coverage': rpbl_count / len(nodes) * 100 if nodes else 0,
            'dead_code_percent': exec_flow.dead_code_percent
        },
        'distributions': {
            'types': dict(types.most_common(15)),
            'rings': dict(rings),
            'atoms': dict(Counter(n.get('atom', '') for n in nodes))
        },
        'rpbl_profile': rpbl_avgs,
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
    
    # Save output
    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = target / "collider_output" if target.is_dir() else target.parent / "collider_output"
    
    out_path.mkdir(parents=True, exist_ok=True)

    # NOTE: Removed full_analysis.json write - unified_analysis.json is the single source of truth

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
    # 1. unified_analysis.json - Structured data (single source of truth)
    # 2. collider_report.html  - Visual report (embeds Brain Download)
    # ==========================================================================

    # Generate Brain Download content (for embedding in HTML)
    from brain_download import generate_brain_download
    brain_content = generate_brain_download(full_output)
    full_output['brain_download'] = brain_content  # Embed in JSON for HTML access

    # Stage 12: Write consolidated outputs
    print("\n📦 Stage 12: Generating Consolidated Outputs...")

    # Output 1: unified_analysis.json (SINGLE DATA SOURCE)
    unified_json = out_path / "unified_analysis.json"
    with open(unified_json, 'w') as f:
        json.dump(full_output, f, indent=2, default=str)
    print(f"   → Data: {unified_json}")

    # Output 2: collider_report.html (SINGLE VISUAL REPORT)
    viz_file = out_path / "collider_report.html"
    try:
        if visualize_graph:
            visualize_graph.generate_html(str(unified_json), str(viz_file))
            print(f"   → Visual: {viz_file}")
    except Exception as e:
        print(f"   ⚠️ Visualization generation failed: {e}")

    print("\n" + "=" * 60)
    print("✅ FULL ANALYSIS COMPLETE")
    print(f"   Time: {total_time:.1f}s")
    print(f"   Data:   {unified_json}")
    if visualize_graph:
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
