#!/usr/bin/env python3
"""
Mini-Validation Sampler

Randomly sample 500 code elements from existing analysis for manual annotation.
"""

import json
import random
import csv
from pathlib import Path
from typing import List, Dict

def load_analysis(analysis_path: Path) -> Dict:
    """Load unified_analysis.json from a repository."""
    with open(analysis_path) as f:
        return json.load(f)

def extract_elements(analysis: Dict) -> List[Dict]:
    """Extract code elements with their predictions."""
    elements = []
    
    for node in analysis.get('nodes', []):
        # Only sample concrete code elements (skip modules, imports)
        if node.get('kind') in ['function', 'method', 'class']:
            element = {
                'id': node.get('id', ''),
                'name': node.get('name', ''),
                'kind': node.get('kind', ''),
                'file': node.get('file_path', ''),
                'line': node.get('line', 0),
                'signature': node.get('signature', ''),
                'docstring': node.get('docstring', '')[:200],  # First 200 chars
                'predicted_atom': node.get('atom', ''),
                'predicted_role': node.get('role', ''),
                'confidence': node.get('role_confidence', 0.0)
            }
            elements.append(element)
    
    return elements

def sample_elements(output_dir: Path, n_samples: int = 500, seed: int = 42) -> None:
    """Sample n elements from graph.json."""
    random.seed(seed)
    
    # Find graph.json
    graph_file = output_dir / 'graph.json'
    
    if not graph_file.exists():
        print(f"❌ No graph.json found in {output_dir}")
        print(f"   Run 'python cli.py audit .' first")
        return
    
    print(f"Loading {graph_file}...")
    
    # Load graph (large file)
    with open(graph_file) as f:
        graph = json.load(f)
    
    # Extract elements (components is a dict)
    all_elements = []
    for component_id, node in graph.get('components', {}).items():
        # Only sample code elements (FNC=function, AGG=class/aggregate, HDL=handler)
        if node.get('kind') in ['FNC', 'AGG', 'HDL']:
            element = {
                'id': node.get('id', component_id),
                'name': node.get('name', ''),
                'kind': node.get('kind', ''),
                'file': node.get('file', ''),
                'line': node.get('start_line', 0),
                'signature': node.get('signature', '')[:200],  # Limit length
                'docstring': node.get('docstring', '')[:200],
                'predicted_atom': '',  # Not in this format
                'predicted_role': node.get('role', ''),
                'confidence': node.get('role_confidence', 0.0)
            }
            all_elements.append(element)
    
    print(f"Total elements available: {len(all_elements)}")
    
    # Stratified sampling by kind
    elements_by_kind = {}
    for elem in all_elements:
        kind = elem['kind']
        if kind not in elements_by_kind:
            elements_by_kind[kind] = []
        elements_by_kind[kind].append(elem)
    
    # Sample proportionally
    samples = []
    for kind, elements in elements_by_kind.items():
        proportion = len(elements) / len(all_elements)
        n_for_kind = int(n_samples * proportion)
        samples.extend(random.sample(elements, min(n_for_kind, len(elements))))
    
    # If we're short, fill randomly
    if len(samples) < n_samples:
        remaining = [e for e in all_elements if e not in samples]
        samples.extend(random.sample(remaining, min(n_samples - len(samples), len(remaining))))
    
    # Shuffle
    random.shuffle(samples)
    samples = samples[:n_samples]
    
    # Save to CSV
    output_file = Path('data/mini_validation_samples.csv')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'sample_id', 'name', 'kind', 'file', 'line', 'signature', 'docstring',
            'predicted_atom', 'predicted_role', 'confidence',
            'annotated_atom', 'annotated_role', 'notes'
        ])
        writer.writeheader()
        
        for i, elem in enumerate(samples, 1):
            writer.writerow({
                'sample_id': i,
                'name': elem['name'],
                'kind': elem['kind'],
                'file': elem['file'],
                'line': elem['line'],
                'signature': elem['signature'],
                'docstring': elem['docstring'],
                'predicted_atom': elem['predicted_atom'],
                'predicted_role': elem['predicted_role'],
                'confidence': elem['confidence'],
                'annotated_atom': '',  # To be filled manually
                'annotated_role': '',  # To be filled manually
                'notes': ''
            })
    
    print(f"\n✅ Sampled {len(samples)} elements")
    print(f"📄 Output: {output_file}")
    print(f"\nDistribution:")
    for kind in elements_by_kind.keys():
        count = sum(1 for s in samples if s['kind'] == kind)
        print(f"  {kind}: {count} ({count/len(samples)*100:.1f}%)")
    
    print(f"\n📋 Next steps:")
    print(f"1. Open {output_file} in Excel/Google Sheets")
    print(f"2. Fill in 'annotated_atom' and 'annotated_role' columns")
    print(f"3. Run: python scripts/validate_annotations.py")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Sample elements for mini-validation')
    parser.add_argument('--output-dir', type=Path, default=Path('output/audit'),
                       help='Directory containing analysis files')
    parser.add_argument('--n', type=int, default=500,
                       help='Number of samples')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    
    args = parser.parse_args()
    sample_elements(args.output_dir, args.n, args.seed)
