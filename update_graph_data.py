
import json
import re
import os
from pathlib import Path

# Paths
OUTPUT_DIR = Path("output/atman_post_refactor")
SEMANTIC_IDS_PATH = OUTPUT_DIR / "semantic_ids.json"
GRAPH_PATH = OUTPUT_DIR / "graph.json"
HTML_SOURCE = Path("output/atman_full_analysis/ARCHITECTURE_GRAPH.html")
HTML_DEST = OUTPUT_DIR / "ARCHITECTURE_GRAPH.html"
CLUSTER_DATA_JS_DEST = OUTPUT_DIR / "cluster_data.js"
BUSINESS_DOMAINS_PATH = Path("output/atman_full_analysis/business_domains.json")

# Regex Rules for Clustering
# Order matters: first match wins
RULES = [
    # --- PLUGGY INTEGRATION (Expanded for Phase 1 simulation) ---
    (r"(?i)pluggy", "pluggy_integration"),
    (r"(?i)connector", "pluggy_integration"),
    (r"(?i)sync", "pluggy_integration"),
    (r"(?i)webhook", "webhooks"), 
    (r"(?i)hook", "pluggy_integration"),
    (r"(?i)token", "pluggy_integration"), # often related to auth
    (r"(?i)credential", "pluggy_integration"),
    (r"(?i)aggregator", "pluggy_integration"),
    (r"(?i)fetch.*item", "pluggy_integration"),
    (r"(?i)update.*item", "pluggy_integration"),
    
    # --- DOMAIN LOGIC ---
    (r"(?i)account", "accounts"),
    (r"(?i)balance", "accounts"),
    
    (r"(?i)loan", "loans"),
    (r"(?i)debt", "loans"),
    (r"(?i)contract", "loans"),
    
    (r"(?i)bill", "billing"),
    (r"(?i)credit.*card", "billing"),
    (r"(?i)statement", "billing"),
    
    (r"(?i)invest", "investments"),
    (r"(?i)asset", "investments"),
    (r"(?i)position", "investments"),
    
    (r"(?i)finance", "finance"),
    (r"(?i)budget", "finance"),
    (r"(?i)spending", "finance"),
    
    (r"(?i)transaction", "transactions"),
    (r"(?i)category", "transactions"),
    (r"(?i)merchant", "transactions"),
    
    (r"(?i)csv", "csv_import"),
    (r"(?i)import", "csv_import"),
    (r"(?i)upload", "csv_import"),
    
    (r"(?i)entity", "entities"),
    (r"(?i)cpf", "entities"),
    (r"(?i)cnpj", "entities"),
    (r"(?i)user", "entities"),
    (r"(?i)identity", "entities"),
    (r"(?i)profile", "entities"),
    
    (r"(?i)chart", "visualization"),
    (r"(?i)graph", "visualization"),
    (r"(?i)viz", "visualization"),
    (r"(?i)dashboard", "visualization"),
    
    (r"(?i)cache", "caching"),
    (r"(?i)redis", "caching"),
    (r"(?i)store", "caching"),

    (r"(?i)assist", "assistant"),
    (r"(?i)gpt", "assistant"),
    (r"(?i)llm", "assistant"),
    (r"(?i)agent", "assistant"),
    (r"(?i)prompt", "assistant"),
    
    # --- INFRASTRUCTURE ---
    (r"(?i)validat", "validation"),
    (r"(?i)check", "validation"),
    (r"(?i)verify", "validation"),
    (r"(?i)sanitize", "validation"),
    
    (r"(?i)transform", "transformation"),
    (r"(?i)map", "transformation"),
    (r"(?i)convert", "transformation"),
    (r"(?i)parse", "transformation"),
    (r"(?i)format", "transformation"),
    
    (r"(?i)extract", "extraction"),
    (r"(?i)get.*from", "extraction"),
    (r"(?i)find", "extraction"),
    
    (r"(?i)compute", "computation"),
    (r"(?i)calc", "computation"),
    (r"(?i)math", "computation"),
    (r"(?i)sum", "computation"),
    (r"(?i)total", "computation"),
    
    (r"(?i)error", "error_handling"),
    (r"(?i)exception", "error_handling"),
    (r"(?i)fail", "error_handling"),
    (r"(?i)warn", "error_handling"),
    
    (r"(?i)diag", "diagnostics"),
    (r"(?i)log", "diagnostics"),
    (r"(?i)track", "diagnostics"),
    (r"(?i)monitor", "diagnostics"),
    (r"(?i)trace", "diagnostics"),
    (r"(?i)health", "diagnostics"),
    
    (r"(?i)mock", "mocking"),
    (r"(?i)fake", "mocking"),
    (r"(?i)seed", "mocking"),
    (r"(?i)fixture", "mocking"),
    
    (r"(?i)factory", "factory"),
    (r"(?i)build", "factory"),
    (r"(?i)make", "factory"),
    (r"(?i)create", "factory"), # Risky but often factory
    (r"(?i)init", "factory"),
    
    (r"(?i)api", "api_layer"),
    (r"(?i)route", "api_layer"),
    (r"(?i)endpoint", "api_layer"),
    (r"(?i)handler", "api_layer"),
    (r"(?i)controller", "api_layer"),
    (r"(?i)middleware", "api_layer"),
    (r"(?i)request", "api_layer"),
    (r"(?i)response", "api_layer"),
    (r"(?i)auth", "api_layer"),
    
    (r"(?i)io", "io_input"),
    (r"(?i)read", "io_input"),
    
    (r"(?i)write", "io_output"),
    
    (r"(?i)save", "persistence"),
    (r"(?i)load", "persistence"),
    (r"(?i)persist", "persistence"),
    
    (r"(?i)db", "database"),
    (r"(?i)query", "database"),
    (r"(?i)sql", "database"),
    (r"(?i)repo", "database"),
    
    # Fallback
    (r".*", "core") 
]

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    print(f"🔄 Loading data from {OUTPUT_DIR}...")
    
    if not SEMANTIC_IDS_PATH.exists():
        print(f"❌ Error: {SEMANTIC_IDS_PATH} not found.")
        return

    semantic_ids = load_json(SEMANTIC_IDS_PATH)
    print(f"📚 Loaded Semantic ID file")

    # Load business domains to get valid clusters/colors
    business_domains = load_json(BUSINESS_DOMAINS_PATH)
    valid_clusters = set()
    for domain in business_domains["domains"].values():
        valid_clusters.update(domain["clusters"])

    # --- Step 1: Cluster Atoms ---
    clusters = {name: {"count": 0, "functions": []} for name in valid_clusters}
    if "core" not in clusters: clusters["core"] = {"count": 0, "functions": []}

    id_list = semantic_ids.get("ids", [])
    print(f"🧩 Clustering {len(id_list)} atoms...")
    
    count_skipped = 0
    
    for item_str in id_list:
        # Parse semantic ID string
        # Format: CONTINENT.FUNDAMENTAL.MODULE|FILE|NAME|...
        parts = item_str.split('|')
        if len(parts) < 3:
            count_skipped += 1
            continue
            
        name = parts[2]
        file_name = parts[1]
        
        # Extract metadata from other parts
        line = 0
        type_tag = "Unknown"
        
        for p in parts:
            if p.startswith("lines:"): line = int(p.replace("lines:", ""))
            if p.startswith("type:"): type_tag = p.replace("type:", "")
            
        # Refine type based on ID prefix if not found
        if type_tag == "Unknown":
            if parts[0].startswith("LOG"): type_tag = "Logic"
            elif parts[0].startswith("DAT"): type_tag = "Data"
            elif parts[0].startswith("EXE"): type_tag = "Exec"
        
        atom_obj = {
            "id": item_str,
            "name": name,
            "filePath": f"ATMAN/{file_name}", # Explicit path
            "file_path": f"ATMAN/{file_name}",
            "line": line,
            "type": type_tag
        }

        assigned = "core"
        found = False
        for pattern, cluster_name in RULES:
            if re.search(pattern, name) and cluster_name in valid_clusters:
                assigned = cluster_name
                found = True
                break
        
        clusters[assigned]["count"] += 1
        clusters[assigned]["functions"].append(atom_obj)
        
    print(f"⚠️ Skipped {count_skipped} malformed IDs")

    print("📊 Clustering Results:")
    for name, data in clusters.items():
        if data["count"] > 0:
            print(f"   - {name}: {data['count']}")

    # --- Step 2: Generate cluster_data.js ---
    print("💾 Generating cluster_data.js...")
    # Wrap in variable assignment
    js_content = f"const clusterDetailsData = {json.dumps(clusters, indent=2)};"
    with open(CLUSTER_DATA_JS_DEST, 'w', encoding='utf-8') as f:
        f.write(js_content)

    # --- Step 3: Update ARCHITECTURE_GRAPH.html ---
    print("📝 Updating ARCHITECTURE_GRAPH.html...")
    
    try:
        with open(HTML_SOURCE, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Prepare new clusterData object (just counts)
        cluster_counts = {k: v["count"] for k, v in clusters.items() if v["count"] > 0}
        cluster_data_str = "const clusterData = " + json.dumps(cluster_counts, indent=12) + ";"

        # Replace the old clusterData
        # Regex to find 'const clusterData = { ... };'
        # Use dotall to match multiline
        html_content = re.sub(
            r"const clusterData = \{.*?\};", 
            cluster_data_str, 
            html_content, 
            flags=re.DOTALL
        )

        with open(HTML_DEST, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except Exception as e:
        print(f"❌ Failed to update HTML: {e}")
        return

    print(f"✅ Migration complete! Open {HTML_DEST} to view results.")

if __name__ == "__main__":
    main()
