#!/usr/bin/env python3
"""
Output Parity Check — Diff JSON vs HTML field coverage.

Compares unified_analysis.json with collider_report.html to identify
which fields are present in JSON but missing from HTML visualization.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set


def extract_json_fields(analysis_path: str) -> Dict[str, Set[str]]:
    """Extract field names present in JSON output."""
    
    with open(analysis_path, 'r') as f:
        data = json.load(f)
    
    nodes = data.get('nodes', [])
    
    # Collect all unique fields across nodes
    node_fields: Set[str] = set()
    dimension_fields: Set[str] = set()
    metadata_fields: Set[str] = set()
    
    for node in nodes:
        node_fields.update(node.keys())
        if 'dimensions' in node:
            dimension_fields.update(node['dimensions'].keys())
        if 'metadata' in node:
            metadata_fields.update(node['metadata'].keys())
    
    return {
        'node_fields': node_fields,
        'dimension_fields': dimension_fields,
        'metadata_fields': metadata_fields,
        'node_count': len(nodes),
        'edge_count': len(data.get('edges', []))
    }


def extract_html_rendered(html_path: str) -> Dict[str, any]:
    """Extract what fields are rendered in HTML."""
    
    with open(html_path, 'r') as f:
        html = f.read()
    
    # Extract node count from rendered HTML
    node_match = re.search(r'(\d+)\s*ATOMS', html, re.IGNORECASE)
    edge_match = re.search(r'(\d+)\s*BONDS', html, re.IGNORECASE)
    
    node_count = int(node_match.group(1)) if node_match else 0
    edge_count = int(edge_match.group(1)) if edge_match else 0
    
    # Check for presence of key visualization elements
    has_layers = 'LAYERS' in html
    has_physics = 'PHYSICS' in html or 'Gravity' in html
    has_legend = 'LOG' in html and 'DAT' in html and 'ORG' in html
    has_tooltip = 'tooltip' in html.lower() or 'node.name' in html
    
    # Check which fields appear in the JavaScript data injection
    rendered_fields = set()
    
    field_patterns = [
        (r'"atom":', 'atom'),
        (r'"layer":', 'layer'),
        (r'"name":', 'name'),
        (r'"file_path":', 'file_path'),
        (r'"radius":', 'radius'),
        (r'"group":', 'group'),
        (r'"role":', 'role'),
    ]
    
    for pattern, field in field_patterns:
        if re.search(pattern, html):
            rendered_fields.add(field)
    
    return {
        'node_count': node_count,
        'edge_count': edge_count,
        'has_layers': has_layers,
        'has_physics': has_physics,
        'has_legend': has_legend,
        'has_tooltip': has_tooltip,
        'rendered_fields': rendered_fields
    }


def compare_outputs(json_data: Dict, html_data: Dict) -> Dict:
    """Compare JSON vs HTML and report parity."""
    
    results = {
        'node_count_match': json_data['node_count'] == html_data['node_count'],
        'edge_count_match': json_data['edge_count'] == html_data['edge_count'],
        'json_node_count': json_data['node_count'],
        'html_node_count': html_data['node_count'],
        'json_edge_count': json_data['edge_count'],
        'html_edge_count': html_data['edge_count'],
    }
    
    # Fields in JSON but not rendered in HTML
    core_fields = {'id', 'name', 'atom', 'layer', 'file_path'}
    rendered = html_data['rendered_fields']
    
    results['missing_core_fields'] = list(core_fields - rendered)
    results['rendered_fields'] = list(rendered)
    
    # Dimension coverage
    json_dims = json_data['dimension_fields']
    results['json_dimensions'] = list(json_dims)
    results['dimension_coverage'] = 'partial'  # HTML shows subset
    
    # Metadata coverage
    json_meta = json_data['metadata_fields']
    results['json_metadata_fields'] = list(json_meta)
    results['metadata_rendered'] = False  # Most metadata not in viz yet
    
    # Feature flags
    results['ui_features'] = {
        'layers': html_data['has_layers'],
        'physics': html_data['has_physics'],
        'legend': html_data['has_legend'],
        'tooltip': html_data['has_tooltip']
    }
    
    # Calculate parity score
    core_parity = len(rendered & core_fields) / len(core_fields) * 100
    count_parity = 100 if results['node_count_match'] and results['edge_count_match'] else 50
    feature_parity = sum(results['ui_features'].values()) / len(results['ui_features']) * 100
    
    results['parity_score'] = round((core_parity + count_parity + feature_parity) / 3, 1)
    
    return results


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        # Default paths
        json_path = None
        html_path = None
        
        for candidate in ['/tmp/official_viz', 'output/core_analysis', '.']:
            j = Path(candidate) / 'unified_analysis.json'
            h = Path(candidate) / 'collider_report.html'
            if j.exists() and h.exists():
                json_path = str(j)
                html_path = str(h)
                break
        
        if not json_path:
            print("Usage: python output_parity.py <unified_analysis.json> <collider_report.html>")
            sys.exit(1)
    else:
        json_path = sys.argv[1]
        html_path = sys.argv[2]
    
    print(f"🔍 OUTPUT PARITY CHECK")
    print(f"   JSON: {json_path}")
    print(f"   HTML: {html_path}")
    print("=" * 60)
    
    json_data = extract_json_fields(json_path)
    html_data = extract_html_rendered(html_path)
    results = compare_outputs(json_data, html_data)
    
    # Node/Edge counts
    status = "✅" if results['node_count_match'] else "⚠️"
    print(f"\n   Node Count: JSON={results['json_node_count']}, HTML={results['html_node_count']} {status}")
    
    status = "✅" if results['edge_count_match'] else "⚠️"
    print(f"   Edge Count: JSON={results['json_edge_count']}, HTML={results['html_edge_count']} {status}")
    
    # Rendered fields
    print(f"\n   Rendered Fields: {', '.join(results['rendered_fields'])}")
    if results['missing_core_fields']:
        print(f"   ⚠️ Missing Core: {', '.join(results['missing_core_fields'])}")
    
    # Dimensions
    print(f"\n   JSON Dimensions: {', '.join(results['json_dimensions'][:5])}...")
    print(f"   Dimension Coverage: {results['dimension_coverage']}")
    
    # Metadata
    print(f"\n   JSON Metadata Fields: {', '.join(results['json_metadata_fields'][:5])}")
    print(f"   Metadata in HTML: {'Yes' if results['metadata_rendered'] else 'Partial/No'}")
    
    # UI Features
    print(f"\n   UI Features:")
    for feat, present in results['ui_features'].items():
        status = "✅" if present else "❌"
        print(f"     {feat}: {status}")
    
    # Parity score
    print("\n" + "=" * 60)
    score = results['parity_score']
    status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
    print(f"   OUTPUT PARITY SCORE: {score}% {status}")
    print("=" * 60)
    
    # JSON output
    print(f"\n📦 JSON Output:")
    print(json.dumps(results, indent=2, default=list))
    
    return 0


if __name__ == '__main__':
    main()
