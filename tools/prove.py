#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     COLLIDER - Standard Model of Code                     ║
║                                                                           ║
║  This single script is THE PROOF of the Standard Model.                   ║
║  Run it on any codebase to get reproducible classification.               ║
║                                                                           ║
║  Usage: python prove.py <path_to_code>                                    ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import sys
import json
import time
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# Add core to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'core'))

from unified_analysis import analyze

from antimatter_evaluator import AntimatterEvaluator
from insights_engine import generate_insights
from purpose_field import detect_purpose_field, Layer
from execution_flow import detect_execution_flow
from performance_predictor import predict_performance
from purpose_field import detect_purpose_field, Layer
from execution_flow import detect_execution_flow
from performance_predictor import predict_performance
from data_management import CodebaseState

def run_proof(target_path: str, **kwargs) -> dict:
    """
    Run the complete Standard Model proof on a codebase.
    
    Returns a reproducible proof document with:
    1. Classification results (atoms, roles, RPBL)
    2. Accuracy metrics
    3. Antimatter violations
    4. Predictions (missing components)
    5. Summary statistics
    """
    
    target = Path(target_path).resolve()
    if not target.exists():
        print(f"❌ Path not found: {target}")
        sys.exit(1)
    
    print("=" * 70)
    print("🔬 COLLIDER - Standard Model of Code")
    print("=" * 70)
    print(f"\nTarget: {target}")
    print(f"Time:   {datetime.now().isoformat()}")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 1: CLASSIFICATION
    # ═══════════════════════════════════════════════════════════════════════
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ STAGE 1: CLASSIFICATION                                        │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    start_time = time.time()
    
    try:
        result = analyze(str(target), **kwargs)
        nodes = result.nodes if hasattr(result, 'nodes') else result.get('nodes', [])
        edges = result.edges if hasattr(result, 'edges') else result.get('edges', [])
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)
    
    classification_time = time.time() - start_time
    
    print(f"  ✓ Nodes extracted: {len(nodes)}")
    print(f"  ✓ Edges extracted: {len(edges)}")
    print(f"  ✓ Time: {classification_time:.2f}s")
    print()

    # INITIALIZE STATE
    state = CodebaseState(str(target))
    state.load_initial_graph(nodes, edges)
    print(f"  ✓ State initialized with {len(nodes)} nodes")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 2: ROLE DISTRIBUTION
    # ═══════════════════════════════════════════════════════════════════════
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ STAGE 2: ROLE DISTRIBUTION                                     │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    role_counts = Counter()
    confidence_sum = 0
    confidence_count = 0
    
    for node in nodes:
        if hasattr(node, 'role'):
            role = node.role
            conf = node.role_confidence
        else:
            role = node.get('role', 'Unknown')
            conf = node.get('role_confidence', 0)
        
        role_counts[role] += 1
        if conf:
            confidence_sum += conf
            confidence_count += 1
    
    avg_confidence = confidence_sum / confidence_count if confidence_count else 0
    unknown_count = role_counts.get('Unknown', 0)
    coverage = (len(nodes) - unknown_count) / len(nodes) * 100 if nodes else 0
    
    print(f"  Roles detected:")
    for role, count in role_counts.most_common(10):
        pct = count / len(nodes) * 100
        print(f"    {role:25} {count:6} ({pct:5.1f}%)")
    if len(role_counts) > 10:
        print(f"    ... and {len(role_counts) - 10} more roles")
    
    print()
    print(f"  ✓ Coverage: {coverage:.1f}% (non-Unknown)")
    print(f"  ✓ Average confidence: {avg_confidence:.1f}%")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 3: ANTIMATTER VIOLATIONS
    # ═══════════════════════════════════════════════════════════════════════
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ STAGE 3: ANTIMATTER VIOLATIONS                                 │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    try:
        evaluator = AntimatterEvaluator()
        # Convert nodes to dict format if they're objects
        particles = []
        for node in nodes:
            if hasattr(node, '__dict__'):
                particles.append(vars(node))
            elif hasattr(node, 'to_dict'):
                particles.append(node.to_dict())
            else:
                particles.append(node)
        
        result = evaluator.evaluate(particles)
        violations = result.violations
        violation_count = len(violations)
    except Exception as e:
        violations = []
        violation_count = 0
        print(f"  ⚠ Antimatter evaluation skipped: {e}")
    
    if violation_count > 0:
        print(f"  ❌ Found {violation_count} violations:")
        for v in violations[:5]:
            print(f"    - [{v.severity.upper()}] {v.law_name}: {v.particle_name}")
        if violation_count > 5:
            print(f"    ... and {violation_count - 5} more")
    else:
        print(f"  ✓ No antimatter violations detected")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 4: PREDICTIONS (Missing Components)
    # ═══════════════════════════════════════════════════════════════════════
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ STAGE 4: PREDICTIONS (Missing Components)                      │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    # Count structural pairs
    entities = role_counts.get('Entity', 0) + role_counts.get('DTO', 0)
    repositories = role_counts.get('Repository', 0)
    services = role_counts.get('Service', 0) + role_counts.get('ApplicationService', 0)
    controllers = role_counts.get('Controller', 0)
    tests = role_counts.get('Test', 0)
    
    predictions = []
    
    # Prediction: Missing repositories
    if entities > 0 and repositories < entities:
        missing = entities - repositories
        predictions.append(f"Missing ~{missing} Repositories for {entities} Entities")
    
    # Prediction: Missing tests
    total_logic = services + controllers + role_counts.get('UseCase', 0)
    if total_logic > 0 and tests < total_logic:
        missing = total_logic - tests
        predictions.append(f"Missing ~{missing} Tests for {total_logic} logic components")
    
    # Prediction: Missing services
    if entities > 3 and services == 0:
        predictions.append(f"Missing Services layer for {entities} Entities")
    
    if predictions:
        print(f"  ⚠ Predictions:")
        for p in predictions:
            print(f"    → {p}")
    else:
        print(f"  ✓ Architecture appears complete")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 5: ACTIONABLE INSIGHTS
    # ═══════════════════════════════════════════════════════════════════════
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ STAGE 5: ACTIONABLE INSIGHTS                                   │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    try:
        insights, insights_report = generate_insights(nodes, edges)
        
        if insights:
            print(f"  Found {len(insights)} actionable insights:")
            for insight in insights[:5]:
                priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                icon = priority_icon.get(insight.priority.value, "⚪")
                print(f"    {icon} [{insight.priority.value.upper()}] {insight.title}")
                if insight.schema:
                    print(f"       └─ Schema: {insight.schema}")
            if len(insights) > 5:
                print(f"    ... and {len(insights) - 5} more")
        else:
            print("  ✓ No significant issues detected")
    except Exception as e:
        insights = []
        insights_report = ""
        print(f"  ⚠ Insights generation skipped: {e}")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 6: PURPOSE FIELD
    # ═══════════════════════════════════════════════════════════════════════
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ STAGE 6: PURPOSE FIELD                                         │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    try:
        purpose_field = detect_purpose_field(nodes, edges)
        field_summary = purpose_field.summary()
        
        # Show layer distribution
        print("  Layer distribution:")
        for layer, count in field_summary.get('layers', {}).items():
            if layer != 'unknown':
                pct = count / len(nodes) * 100 if nodes else 0
                print(f"    {layer.capitalize():20} {count:5} ({pct:5.1f}%)")
        
        # Show purpose flow violations
        pf_violations = purpose_field.violations
        if pf_violations:
            print(f"\n  ⚠ Purpose flow violations: {len(pf_violations)}")
            for v in pf_violations[:3]:
                print(f"    - {v}")
            if len(pf_violations) > 3:
                print(f"    ... and {len(pf_violations) - 3} more")
        else:
            print("\n  ✓ No purpose flow violations")
    except Exception as e:
        purpose_field = None
        field_summary = {}
        pf_violations = []
        print(f"  ⚠ Purpose field detection skipped: {e}")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 7: EXECUTION FLOW
    # ═══════════════════════════════════════════════════════════════════════
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ STAGE 7: EXECUTION FLOW                                        │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    try:
        exec_flow = detect_execution_flow(nodes, edges, purpose_field)
        flow_summary = exec_flow.summary()
        
        print(f"  Entry points:     {flow_summary['entry_points']}")
        print(f"  Reachable nodes:  {flow_summary['reachable_nodes']}")
        print(f"  Orphans:          {flow_summary['orphan_count']}")
        print(f"  Dead code:        {flow_summary['dead_code_percent']:.1f}%")
        print(f"  Causality chains: {flow_summary['chains_count']}")
        
        if exec_flow.orphans:
            print(f"\n  ⚠ Orphan functions (unreachable):")
            for orphan in exec_flow.orphans[:5]:
                print(f"    - {orphan}")
            if len(exec_flow.orphans) > 5:
                print(f"    ... and {len(exec_flow.orphans) - 5} more")
        else:
            print("\n  ✓ No dead code detected")
    except Exception as e:
        exec_flow = None
        flow_summary = {}
        print(f"  ⚠ Execution flow analysis skipped: {e}")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 8: PERFORMANCE PREDICTION
    # ═══════════════════════════════════════════════════════════════════════
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ STAGE 8: PERFORMANCE PREDICTION                                │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    try:
        perf_profile = predict_performance(nodes, exec_flow)
        perf_summary = perf_profile.summary()
        
        print(f"  Time types:")
        for ttype, cost in sorted(perf_summary['time_by_type'].items(), key=lambda x: -x[1]):
            pct = cost / perf_summary['total_estimated_cost'] * 100 if perf_summary['total_estimated_cost'] else 0
            print(f"    {ttype:15} {cost:10.0f} ({pct:5.1f}%)")
        
        print(f"\n  Critical path: {perf_summary['critical_path_length']} nodes, cost={perf_summary['critical_path_cost']:.0f}")
        print(f"  Hotspots: {perf_summary['hotspot_count']}")
        
        if perf_profile.hotspots:
            print(f"\n  Top hotspots:")
            for hs in perf_profile.hotspots[:3]:
                if hs in perf_profile.nodes:
                    hn = perf_profile.nodes[hs]
                    print(f"    - {hn.name} ({hn.time_type.value}, score={hn.hotspot_score:.0f})")
    except Exception as e:
        perf_profile = None
        perf_summary = {}
        print(f"  ⚠ Performance prediction skipped: {e}")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 9: SUMMARY
    # ═══════════════════════════════════════════════════════════════════════
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ STAGE 9: SUMMARY                                               │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    # Build insights summary for JSON
    insights_summary = []
    for insight in insights[:10] if insights else []:
        insights_summary.append({
            "type": insight.type.value,
            "priority": insight.priority.value,
            "title": insight.title,
            "description": insight.description,
            "recommendation": insight.recommendation,
            "schema": insight.schema
        })
    
    proof_document = {
        "metadata": {
            "target": str(target),
            "timestamp": datetime.now().isoformat(),
            "version": "2.3.0",
            "model": "Standard Model of Code",
            "tool": "Collider",
            "pipeline_stages": 9
        },
        "classification": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "role_distribution": dict(role_counts),
            "coverage_percent": round(coverage, 2),
            "average_confidence": round(avg_confidence, 2),
            "classification_time_seconds": round(classification_time, 2)
        },
        "antimatter": {
            "violations_count": violation_count,
            "violations": [{"law": v.law_name, "particle": v.particle_name} for v in violations[:10]] if violations else []
        },
        "predictions": predictions,
        "insights": {
            "count": len(insights) if insights else 0,
            "items": insights_summary
        },
        "purpose_field": {
            "layers": field_summary.get('layers', {}),
            "layer_purposes": field_summary.get('layer_purposes', {}),
            "violations_count": len(pf_violations) if pf_violations else 0,
            "violations": pf_violations[:5] if pf_violations else []
        },
        "execution_flow": {
            "entry_points": flow_summary.get('entry_points', 0) if flow_summary else 0,
            "reachable_nodes": flow_summary.get('reachable_nodes', 0) if flow_summary else 0,
            "orphan_count": flow_summary.get('orphan_count', 0) if flow_summary else 0,
            "dead_code_percent": flow_summary.get('dead_code_percent', 0) if flow_summary else 0,
            "chains_count": flow_summary.get('chains_count', 0) if flow_summary else 0,
            "orphans": exec_flow.orphans[:10] if exec_flow and exec_flow.orphans else []
        },
        "performance": {
            "total_estimated_cost": perf_summary.get('total_estimated_cost', 0) if perf_summary else 0,
            "critical_path_cost": perf_summary.get('critical_path_cost', 0) if perf_summary else 0,
            "critical_path_length": perf_summary.get('critical_path_length', 0) if perf_summary else 0,
            "hotspot_count": perf_summary.get('hotspot_count', 0) if perf_summary else 0,
            "time_by_type": perf_summary.get('time_by_type', {}) if perf_summary else {},
            "hotspots": perf_profile.hotspots[:5] if perf_profile and perf_profile.hotspots else []
        },
        "metrics": {
            "entities": entities,
            "repositories": repositories,
            "services": services,
            "controllers": controllers,
            "tests": tests
        }
    }
    
    print(f"  Total nodes:      {len(nodes)}")
    print(f"  Coverage:         {coverage:.1f}%")
    print(f"  Avg confidence:   {avg_confidence:.1f}%")
    print(f"  Violations:       {violation_count}")
    print(f"  Predictions:      {len(predictions)}")
    print(f"  Speed:            {len(nodes)/classification_time:.0f} nodes/sec")
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 10: VISUALIZATION GENERATION (FULL STREAM)
    # ═══════════════════════════════════════════════════════════════════════
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ STAGE 10: VISUALIZATION GENERATION                             │")
    print("└─────────────────────────────────────────────────────────────────┘")

    try:

        # 1. ENRICH NODES VIA STATE
        
        # Enriched Purpose
        if purpose_field:
            for node in purpose_field.nodes.values():
                 layer_val = node.layer.value if hasattr(node.layer, 'value') else str(node.layer)
                 state.enrich_node(node.id, "purpose", 
                                  layer=layer_val, 
                                  composite_purpose=node.composite_purpose)

        # Enrich Flow
        if exec_flow:
            for orphan_id in exec_flow.orphans:
                state.enrich_node(orphan_id, "flow", is_orphan=True)

        # Enrich Performance
        if perf_profile:
            for nid, pnode in perf_profile.nodes.items():
                is_hotspot = pnode.hotspot_score > 50
                state.enrich_node(nid, "performance", 
                                 hotspot_score=pnode.hotspot_score,
                                 is_hotspot=is_hotspot)
        
        # Final Polish (Labels, defaults)
        for nid, node in state.nodes.items():
            if 'layer' not in node:
                state.enrich_node(nid, "default", layer="unknown")
            
            label = node.get('name', '').split('.')[-1]
            state.enrich_node(nid, "ui", label=label)

        # 2. GENERATE JSON PAYLOAD
        export_data = state.export()
        viz_data = {
            "particles": export_data['nodes'],
            "connections": export_data['edges'],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "stats": proof_document['classification']
            }
        }

        # 3. INJECT INTO TEMPLATE
        # Locate template (try local dir, then root)
        repo_root = Path(__file__).resolve().parent.parent
        template_path = repo_root / "collider_viz.html"
        
        if not template_path.exists():
            print(f"  ⚠ Template not found at {template_path}")
        else:
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Safe JSON serialization for HTML embedding
            def safe_json_dumps(obj):
                return json.dumps(obj).replace('<', '\\u003c').replace('>', '\\u003e').replace('/', '\\u002f')

            # Construct injection block
            injection_block = f"""
    const particles = {safe_json_dumps(viz_data['particles'])};
    const connections = {safe_json_dumps(viz_data['connections'])};
    const vizMetadata = {safe_json_dumps(viz_data['metadata'])};
            """
            
            # Replace marker
            start_marker = "/* <!-- DATA_INJECTION_START --> */"
            end_marker = "/* <!-- DATA_INJECTION_END --> */"
            
            if start_marker in html_content and end_marker in html_content:
                # Use simple string replacement to avoid regex issues with JSON data
                parts_before = html_content.split(start_marker)[0]
                parts_after = html_content.split(end_marker)[1]
                new_content = parts_before + start_marker + injection_block + end_marker + parts_after
                
                output_dir = kwargs.get('output_dir', '.')
                out_path = Path(output_dir)
                out_path.mkdir(parents=True, exist_ok=True)
                
                report_path = out_path / "collider_report.html"
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                print(f"  ✓ Report generated: {report_path.resolve()}")
            else:
                print("  ⚠ Injection markers not found in template")

    except Exception as e:
        print(f"  ⚠ Visualization generation failed: {e}")
        import traceback
        traceback.print_exc()

    print()
    output_dir = kwargs.get('output_dir', '.')
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    output_file = out_path / "proof_output.json"
    with open(output_file, 'w') as f:
        json.dump(proof_document, f, indent=2, default=str)
    print(f"  ✓ Proof saved to: {output_file}")
    
    print()
    print("=" * 70)
    print("🎯 PROOF COMPLETE")
    print("=" * 70)
    print()
    print("This analysis is REPRODUCIBLE. Run again to verify.")
    print()
    
    return proof_document


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prove.py <path_to_code>")
        print()
        print("Example:")
        print("  python prove.py .")
        print("  python prove.py /path/to/repo")
        sys.exit(1)
    
    target = sys.argv[1]
    run_proof(target)
