#!/usr/bin/env python3
"""
Architectural Mapper

Uses Collider's output (graph.json) to find disconnected modules 
and architectural flaws in the codebase itself.
"""

import json
import sys
from collections import defaultdict

def find_orphans(graph_path):
    print(f"🗺️  Mapping Architecture from {graph_path}...")
    
    with open(graph_path) as f:
        data = json.load(f)
        
    # Build Dependency Graph
    # file_path -> incoming_edges_count
    in_degree = defaultdict(int)
    files = set()
    
    # 1. Register all files
    for comp in data.get('components', {}).values():
        f = comp.get('file')
        if f:
            files.add(f)
            
    # 2. Count connections
    # We need to look at 'relations' or 'edges' if available.
    # The graph.json structure is: { "components": { id: { ... } }, "relations": [ {source, target, type} ] }
    # Let's check relation structure.
    
    relations = data.get('relations', [])
    for rel in relations:
        target_id = rel.get('target')
        # We need to map target_id back to file
        # Assuming component ID is the key in 'components'
        target_comp = data['components'].get(target_id)
        if target_comp:
            target_file = target_comp.get('file')
            if target_file:
                in_degree[target_file] += 1

    # 3. Identify Orphans (files with 0 incoming dependencies)
    # Exclude: scripts/, tests/, docs/, tools/ (entry points)
    orphans = []
    core_orphans = []
    
    for f in files:
        if in_degree[f] == 0:
            orphans.append(f)
            if 'core/' in f:
                core_orphans.append(f)
                
    print(f"\nFound {len(orphans)} total disconnected files.")
    
    print("\n🚨 CRITICAL: Disconnected Core Modules")
    print("These modules are likely unused or improperly wired:")
    for f in sorted(core_orphans):
        # Filter noise
        if '__init__' in f: continue
        print(f"  - {f}")
        
    # Also check for 'Islands' (clusters not connected to main graph)
    # (Simplified for now to just 0-in-degree)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 map_architecture.py <graph.json>")
        sys.exit(1)
    find_orphans(sys.argv[1])
