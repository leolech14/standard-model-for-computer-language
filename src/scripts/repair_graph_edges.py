import json
import os
from pathlib import Path

# Paths
INPUT_GRAPH = Path("output/atman_post_refactor/graph.json")
OUTPUT_EDGES_JS = Path("output/atman_post_refactor/edges_data.js")

def load_json(path):
    print(f"📖 Loading {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    if not INPUT_GRAPH.exists():
        print(f"❌ {INPUT_GRAPH} not found.")
        return

    data = load_json(INPUT_GRAPH)
    
    # The graph.json structure from learning_engine seems to be:
    # { "repo_name": ..., "components": { ID: COMPONENT }, "edges": [ ... ] } or similar.
    # Wait, the JSON I viewed had "components" at top level?
    # Let's verify structure assumption. 
    # Based on view_file:
    # Root keys: repo_name, repo_path, components
    # BUT where are the edges?
    # The grep showed edges exist. They might be in a top-level "edges" key I missed or inside components?
    # Standard IR graph typically has "edges": [] at root.
    
    components = data.get("components", {})
    edges_raw = data.get("edges", [])
    
    if not edges_raw:
        # Fallback: maybe they are inside an "edges" object or different key?
        # Let's check keys
        print(f"Keys found: {list(data.keys())}")
        if "graph" in data:
            # Maybe it's nested?
            pass
            
    print(f"🧩 Found {len(components)} components")
    print(f"🔗 Found {len(edges_raw)} raw edges")

    # 1. Build Name Index (Simple Name -> [List of IDs])
    name_index = {}
    for cid, comp in components.items():
        name = comp.get("name")
        if name:
            if name not in name_index:
                name_index[name] = []
            name_index[name].append(cid)
            
    # 2. Resolve Edges
    resolved_edges = []
    
    skipped_count = 0
    ambiguous_count = 0
    resolved_count = 0
    
    for edge in edges_raw:
        src_name = edge.get("source")
        tgt_name = edge.get("target")
        e_type = edge.get("edge_type")
        
        # We want call/usage edges, often labeled 'import' in this engine or 'reference'
        # We specifically want to see structure, so 'contains' is boring (hierarchy).
        if e_type == "contains":
            continue
            
        # Resolve Source
        src_ids = name_index.get(src_name)
        # Resolve Target
        tgt_ids = name_index.get(tgt_name)
        
        if not src_ids:
            # Try to see if src_name IS an ID
            if src_name in components:
                src_ids = [src_name]
        
        if not tgt_ids:
             if tgt_name in components:
                tgt_ids = [tgt_name]

        if src_ids and tgt_ids:
            # Heuristic: If multiple matches, we create edges for ALL combinations?
            # Or try to match file scope?
            # For now, let's just take the first one or explode them.
            # Exploding reveals the "potential" structure.
            
            # Optimization: core/ATMAN usually has unique names for functions?
            # Let's link all for now.
            for s_id in src_ids:
                for t_id in tgt_ids:
                    if s_id == t_id: continue # Self loop?
                    
                    resolved_edges.append({
                        "source": s_id,
                        "target": t_id,
                        "type": e_type
                    })
            resolved_count += 1
        else:
            skipped_count += 1
            
    print(f"✅ Resolved {len(resolved_edges)} edges ({resolved_count} original edges matched)")
    print(f"⚠️ Skipped {skipped_count} edges (node not found)")

    # 3. Export to JS
    # Format: const edgesData = [ ... ];
    js_content = f"const edgesData = {json.dumps(resolved_edges, indent=2)};"
    
    with open(OUTPUT_EDGES_JS, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"💾 Saved to {OUTPUT_EDGES_JS}")

if __name__ == "__main__":
    main()
