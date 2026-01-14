#!/usr/bin/env python3
"""
Theory Coverage Metrics — Measure Standard Model completeness.

Reports:
- D1_WHAT assignment rate
- D1_ECOSYSTEM assignment rate
- Hook metadata enrichment rate
- K8s kind metadata rate
- Overall theory completeness score
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any


def calculate_theory_coverage(analysis_path: str) -> Dict[str, Any]:
    """Calculate theory coverage metrics from unified_analysis.json."""
    
    with open(analysis_path, 'r') as f:
        data = json.load(f)
    
    nodes = data.get('nodes', [])
    total = len(nodes)
    
    if total == 0:
        return {'error': 'No nodes found', 'overall_score': 0}
    
    # D1_WHAT coverage (particles with assigned atom, not Unknown)
    d1_what_assigned = sum(
        1 for n in nodes
        if n.get('dimensions', {}).get('D1_WHAT') 
        and n['dimensions']['D1_WHAT'] != 'Unknown'
    )
    
    # D1_ECOSYSTEM coverage
    d1_ecosystem_assigned = sum(
        1 for n in nodes
        if n.get('dimensions', {}).get('D1_ECOSYSTEM')
    )
    
    # Hook metadata (for React components)
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
    
    # Overall score: weighted average
    overall = (d1_what_pct * 0.4 + d1_ecosystem_pct * 0.3 + hooks_pct * 0.15 + k8s_pct * 0.15)
    
    return {
        'total_nodes': total,
        'd1_what': {
            'assigned': d1_what_assigned,
            'total': total,
            'percentage': round(d1_what_pct, 1)
        },
        'd1_ecosystem': {
            'assigned': d1_ecosystem_assigned,
            'total': total,
            'percentage': round(d1_ecosystem_pct, 1)
        },
        'hook_metadata': {
            'enriched': hooks_enriched,
            'total_react': len(react_components),
            'percentage': round(hooks_pct, 1)
        },
        'k8s_metadata': {
            'assigned': k8s_kind_assigned,
            'total_k8s': len(k8s_resources),
            'percentage': round(k8s_pct, 1)
        },
        'overall_score': round(overall, 1)
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        # Default: Look for unified_analysis.json in common locations
        candidates = [
            'output/unified_analysis.json',
            'unified_analysis.json',
            '/tmp/official_viz/unified_analysis.json'
        ]
        analysis_path = None
        for c in candidates:
            if Path(c).exists():
                analysis_path = c
                break
        
        if not analysis_path:
            print("Usage: python theory_coverage.py <path/to/unified_analysis.json>")
            sys.exit(1)
    else:
        analysis_path = sys.argv[1]
    
    print(f"📊 THEORY COVERAGE METRICS")
    print(f"   Source: {analysis_path}")
    print("=" * 60)
    
    metrics = calculate_theory_coverage(analysis_path)
    
    if 'error' in metrics:
        print(f"❌ Error: {metrics['error']}")
        sys.exit(1)
    
    print(f"\n   Total Nodes: {metrics['total_nodes']}")
    print()
    
    # D1_WHAT
    d1 = metrics['d1_what']
    bar = "█" * int(d1['percentage'] / 5)
    print(f"   D1_WHAT (Atom Assignment)")
    print(f"     {d1['assigned']}/{d1['total']} = {d1['percentage']}% {bar}")
    
    # D1_ECOSYSTEM
    eco = metrics['d1_ecosystem']
    bar = "█" * int(eco['percentage'] / 5)
    print(f"\n   D1_ECOSYSTEM")
    print(f"     {eco['assigned']}/{eco['total']} = {eco['percentage']}% {bar}")
    
    # Hook metadata
    hooks = metrics['hook_metadata']
    bar = "█" * int(hooks['percentage'] / 5)
    print(f"\n   React Hook Metadata")
    print(f"     {hooks['enriched']}/{hooks['total_react']} = {hooks['percentage']}% {bar}")
    
    # K8s metadata
    k8s = metrics['k8s_metadata']
    bar = "█" * int(k8s['percentage'] / 5)
    print(f"\n   K8s Kind Metadata")
    print(f"     {k8s['assigned']}/{k8s['total_k8s']} = {k8s['percentage']}% {bar}")
    
    # Overall
    print("\n" + "=" * 60)
    overall = metrics['overall_score']
    status = "✅" if overall >= 80 else "⚠️" if overall >= 60 else "❌"
    print(f"   OVERALL THEORY COMPLETENESS: {overall}% {status}")
    print("=" * 60)
    
    # Output JSON for CI
    print(f"\n📦 JSON Output:")
    print(json.dumps(metrics, indent=2))
    
    # Exit code based on threshold
    if overall < 60:
        sys.exit(1)
    return 0


if __name__ == '__main__':
    main()
