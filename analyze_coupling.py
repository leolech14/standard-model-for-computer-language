import json
import re
from pathlib import Path

# Paths
CLUSTER_DATA_JS = Path("output/atman_full_analysis/cluster_data.js")
EDGES_DATA_JS = Path("output/atman_full_analysis/edges_data.js")

def load_js_object(path):
    """Crude parser to extract JSON object from JS assignment"""
    content = path.read_text(encoding='utf-8')
    # Match everything between first { and last }
    match = re.search(r'(=)\s*(\{.*\}|\[.*\])\s*;?\s*$', content, re.DOTALL)
    if match:
        json_str = match.group(2)
        return json.loads(json_str)
    return None

def main():
    print("🔄 Loading cluster and edge data...")
    clusters = load_js_object(CLUSTER_DATA_JS)
    edges = load_js_object(EDGES_DATA_JS)
    
    if not clusters or not edges:
        print("❌ Failed to load data.")
        return

    # Build Map: Function ID -> Cluster Name
    func_to_cluster = {}
    for cluster_name, data in clusters.items():
        for func in data.get("functions", []):
            func_to_cluster[func["id"]] = cluster_name
            
    print(f"🧩 Mapped {len(func_to_cluster)} functions to clusters")

    # Analyze Core Dependencies
    core_outbound = {}  # Core -> Other
    core_inbound = {}   # Other -> Core
    
    # Internal Core Tangle
    core_internal_edges = 0
    
    for edge in edges:
        src = edge.get("source")
        tgt = edge.get("target")
        
        src_cluster = func_to_cluster.get(src)
        tgt_cluster = func_to_cluster.get(tgt)
        
        if not src_cluster or not tgt_cluster:
            continue
            
        if src_cluster == "core" and tgt_cluster != "core":
            core_outbound[tgt_cluster] = core_outbound.get(tgt_cluster, 0) + 1
        elif tgt_cluster == "core" and src_cluster != "core":
            core_inbound[src_cluster] = core_inbound.get(src_cluster, 0) + 1
        elif src_cluster == "core" and tgt_cluster == "core":
            core_internal_edges += 1

    print("\n📊 COUPLING ANALYSIS FOR 'CORE' (GOD CLASS)")
    print("===========================================")
    print(f"🕸️  Internal Tangle: {core_internal_edges} calls within Core")
    
    print("\n📤 Top Outbound Dependencies (Core depends on...):")
    for cluster, count in sorted(core_outbound.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {cluster}: {count} calls")
        
    print("\n📥 Top Inbound Dependencies (Core is used by...):")
    for cluster, count in sorted(core_inbound.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {cluster}: {count} calls")
        
    # Calculate "Easiness" Score for extraction
    # High specific coupling + Low scattering = Easy to extract?
    # Actually, we want to extract things FROM core. 
    # But since 'core' is a catch-all, we look at what Core calls that IS identified.
    # If Core calls 'pluggy_integration' 500 times, it means Core has a lot of Pluggy logic left in it?
    # No, it means Core USES Pluggy.
    
    # The real insight: We need to see if we can identify sub-clusters WITHIN core.
    # But for now, let's see the interface.

if __name__ == "__main__":
    main()
