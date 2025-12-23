#!/usr/bin/env python3
"""
Extended Visualization Generator

Generates interactive browser visualization from proof_output.json,
rendering all 4 semantic layers:
- Layer 1: Node Mapping (role, atom type)
- Layer 2: Purpose Field (architectural layer)
- Layer 3: Execution Flow (entry points, orphans)
- Layer 4: Performance (time types, hotspots, cost)

Usage:
    python tools/create_visualization.py [--input proof_output.json] [--output viz.html]
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

# Default paths
DEFAULT_INPUT = "proof_output.json"
DEFAULT_TEMPLATE = Path(__file__).parent.parent / "demos" / "spectrometer_pro.html"
DEFAULT_OUTPUT = "spectrometer_viz.html"

# Layer colors (matching DDD architectural layers)
LAYER_COLORS = {
    "presentation": {"bg": "#00d4ff", "border": "#00a8cc", "icon": "🌐"},
    "application": {"bg": "#a855f7", "border": "#7c3aed", "icon": "📱"},
    "domain": {"bg": "#ec4899", "border": "#db2777", "icon": "💎"},
    "infrastructure": {"bg": "#22c55e", "border": "#16a34a", "icon": "🔧"},
    "testing": {"bg": "#eab308", "border": "#ca8a04", "icon": "🧪"},
    "unknown": {"bg": "#6b7280", "border": "#4b5563", "icon": "❓"},
}

# Time type visual configs
TIME_TYPE_SHAPES = {
    "τ_instant": "dot",
    "τ_compute": "ellipse",
    "τ_io_local": "hexagon",
    "τ_io_network": "hexagon",
    "τ_blocking": "diamond",
}

# Role icons
ROLE_ICONS = {
    "Repository": "💾",
    "Service": "⚙️",
    "Controller": "🎮",
    "Entity": "📦",
    "UseCase": "🎯",
    "Gateway": "🌐",
    "Factory": "🏭",
    "Test": "🧪",
    "Validator": "✓",
    "Command": "📤",
    "Query": "📥",
}


def load_proof_data(proof_path: str) -> dict:
    """Load and parse proof_output.json"""
    with open(proof_path, 'r') as f:
        return json.load(f)


def load_unified_analysis(target_path: str) -> dict:
    """Load unified_analysis.json from spectrometer output"""
    ua_path = Path(target_path) / "spectrometer_output" / "unified_analysis.json"
    if ua_path.exists():
        with open(ua_path, 'r') as f:
            return json.load(f)
    return {"nodes": [], "edges": []}


def build_particles(proof: dict, unified: dict) -> list:
    """Build particle list with all 4 semantic layers"""
    particles = []
    
    # Get layer data
    purpose_layers = proof.get("purpose_field", {}).get("layers", {})
    exec_flow = proof.get("execution_flow", {})
    performance = proof.get("performance", {})
    
    # Get hotspots and orphans for quick lookup
    hotspots = set(performance.get("hotspots", []))
    orphans = set(exec_flow.get("orphans", []))
    entry_count = exec_flow.get("entry_points", 0)
    
    # Track seen IDs to avoid duplicates
    seen_ids = set()
    
    # Process nodes from unified analysis
    for node in unified.get("nodes", []):
        node_id = node.get("id") or node.get("name", "")
        
        # Skip duplicates
        if node_id in seen_ids:
            continue
        seen_ids.add(node_id)
        node_id = node.get("id") or node.get("name", "")
        name = node.get("name", node_id)
        role = node.get("role", "Unknown")
        layer = node.get("layer", "unknown")
        
        # Normalize layer name
        if layer and hasattr(layer, 'lower'):
            layer = layer.lower()
        layer = layer if layer in LAYER_COLORS else "unknown"
        
        # Get layer color info
        layer_info = LAYER_COLORS.get(layer, LAYER_COLORS["unknown"])
        
        # Execution flow properties
        is_entry = node.get("in_degree", 0) == 0
        is_orphan = node_id in orphans
        in_degree = node.get("in_degree", 0)
        out_degree = node.get("out_degree", 0)
        
        # Performance properties
        time_type = "τ_compute"  # Default
        estimated_cost = node.get("lines_of_code", 1) * node.get("complexity", 1)
        is_hotspot = node_id in hotspots
        
        # Get role icon
        role_icon = ROLE_ICONS.get(role, "⚡")
        
        particles.append({
            "id": node_id,
            "label": name[:30],  # Truncate long names
            
            # Layer 1: Node Mapping
            "role": role,
            "role_icon": role_icon,
            
            # Layer 2: Purpose Field
            "layer": layer,
            "layer_icon": layer_info["icon"],
            "layer_color": layer_info["bg"],
            
            # Layer 3: Execution Flow
            "is_entry_point": is_entry,
            "is_orphan": is_orphan,
            "in_degree": in_degree,
            "out_degree": out_degree,
            
            # Layer 4: Performance
            "time_type": time_type,
            "estimated_cost": estimated_cost,
            "is_hotspot": is_hotspot,
            
            # Legacy fields for template compatibility
            "boundary": "Internal",
            "state": "Stateless",
            "activation": "Direct",
            "lifetime": "Transient",
            "effect": "Pure" if role in ["DTO", "Entity", "ValueObject"] else "Side-Effect",
        })
    
    return particles


def build_connections(unified: dict) -> list:
    """Build connection list from edges"""
    connections = []
    
    for edge in unified.get("edges", []):
        source = edge.get("source", edge.get("from", ""))
        target = edge.get("target", edge.get("to", ""))
        edge_type = edge.get("type", edge.get("edge_type", "CALLS"))
        
        if source and target:
            connections.append({
                "from": source,
                "to": target,
                "type": edge_type.upper() if edge_type else "CALLS"
            })
    
    return connections


def build_metadata(proof: dict) -> dict:
    """Build metadata summary for the visualization"""
    return {
        "generated_at": datetime.now().isoformat(),
        "version": proof.get("metadata", {}).get("version", "2.3.0"),
        "target": proof.get("metadata", {}).get("target", ""),
        
        # Classification stats
        "total_nodes": proof.get("classification", {}).get("total_nodes", 0),
        "total_edges": proof.get("classification", {}).get("total_edges", 0),
        "coverage": proof.get("classification", {}).get("coverage_percent", 0),
        
        # Purpose field stats
        "layers": proof.get("purpose_field", {}).get("layers", {}),
        
        # Execution flow stats
        "entry_points": proof.get("execution_flow", {}).get("entry_points", 0),
        "orphan_count": proof.get("execution_flow", {}).get("orphan_count", 0),
        "dead_code_percent": proof.get("execution_flow", {}).get("dead_code_percent", 0),
        
        # Performance stats
        "critical_path_cost": proof.get("performance", {}).get("critical_path_cost", 0),
        "hotspot_count": proof.get("performance", {}).get("hotspot_count", 0),
        "time_by_type": proof.get("performance", {}).get("time_by_type", {}),
    }


def inject_into_template(template_path: str, particles: list, connections: list, metadata: dict) -> str:
    """Inject data into HTML template"""
    with open(template_path, 'r') as f:
        html = f.read()
    
    # Build JavaScript data
    particles_json = json.dumps(particles, indent=2)
    connections_json = json.dumps(connections, indent=2)
    metadata_json = json.dumps(metadata, indent=2)
    
    # Update layer colors to match our semantic layers
    layer_colors_js = """const layerColors = {
            'presentation': { bg: '#00d4ff', border: '#00a8cc', icon: '🌐' },
            'application': { bg: '#a855f7', border: '#7c3aed', icon: '📱' },
            'domain': { bg: '#ec4899', border: '#db2777', icon: '💎' },
            'infrastructure': { bg: '#22c55e', border: '#16a34a', icon: '🔧' },
            'testing': { bg: '#eab308', border: '#ca8a04', icon: '🧪' },
            'unknown': { bg: '#6b7280', border: '#4b5563', icon: '❓' },
        };"""
    
    # Replace the layerColors definition - find start and end manually
    import re
    
    # Find the start of layerColors
    start_match = re.search(r'const layerColors = \{', html)
    if start_match:
        start_pos = start_match.start()
        # Find matching closing brace by counting
        brace_count = 0
        end_pos = start_match.end()
        for i in range(start_match.end(), len(html)):
            if html[i] == '{':
                brace_count += 1
            elif html[i] == '}':
                if brace_count == 0:
                    end_pos = i + 2  # Include }; 
                    break
                brace_count -= 1
        html = html[:start_pos] + layer_colors_js + html[end_pos:]
    
    # Inject particles and connections using lambda to avoid escape issues
    particles_str = f'const particles = {particles_json};'
    connections_str = f'const connections = {connections_json};'
    
    html = re.sub(
        r'const particles = \[.*?\];',
        lambda m: particles_str,
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'const connections = \[.*?\];',
        lambda m: connections_str,
        html,
        flags=re.DOTALL
    )
    
    # Inject metadata (add after particles/connections)
    metadata_injection = f"const vizMetadata = {metadata_json};"
    html = html.replace(
        "/* <!-- DATA_INJECTION_END --> */",
        f"/* <!-- DATA_INJECTION_END --> */\n        {metadata_injection}"
    )
    
    # Update title
    target_name = Path(metadata.get("target", "")).name or "Analysis"
    html = html.replace(
        "<title>🔬 Spectrometer Pro - Code Architecture Visualizer</title>",
        f"<title>🔬 Spectrometer Pro - {target_name}</title>"
    )
    
    return html


def main():
    parser = argparse.ArgumentParser(description="Generate visualization from proof output")
    parser.add_argument("--input", "-i", default=DEFAULT_INPUT, help="Path to proof_output.json")
    parser.add_argument("--template", "-t", default=str(DEFAULT_TEMPLATE), help="Path to HTML template")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT, help="Output HTML file path")
    parser.add_argument("--target", help="Path to analyzed target (for unified_analysis.json)")
    args = parser.parse_args()
    
    print(f"🔬 Extended Visualization Generator")
    print(f"=" * 50)
    
    # Load proof data
    print(f"Loading proof data from {args.input}...")
    proof = load_proof_data(args.input)
    
    # Load unified analysis if target specified
    target = args.target or proof.get("metadata", {}).get("target", "")
    if target:
        print(f"Loading unified analysis from {target}...")
        unified = load_unified_analysis(target)
    else:
        # Fall back to building from proof data
        unified = {"nodes": [], "edges": []}
        print("⚠ No target specified, using proof data only")
    
    # Build visualization data
    print("Building particles with 4 semantic layers...")
    particles = build_particles(proof, unified)
    
    print("Building connections...")
    connections = build_connections(unified)
    
    print("Building metadata...")
    metadata = build_metadata(proof)
    
    # Inject into template
    print(f"Injecting into template {args.template}...")
    html = inject_into_template(args.template, particles, connections, metadata)
    
    # Save output
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"\n✅ Visualization saved to: {output_path.absolute()}")
    print(f"\n📊 Summary:")
    print(f"   Particles: {len(particles)}")
    print(f"   Connections: {len(connections)}")
    print(f"   Layers: {list(metadata.get('layers', {}).keys())}")
    print(f"   Entry points: {metadata.get('entry_points', 0)}")
    print(f"   Hotspots: {metadata.get('hotspot_count', 0)}")
    print(f"\n💡 Open in browser: open {output_path}")


if __name__ == "__main__":
    main()
