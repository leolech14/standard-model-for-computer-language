import json
import sys
import os
import argparse
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.viz import AppearanceEngine, PhysicsEngine, ControlsEngine, get_resolver

# -----------------------------------------------------------------------------
# COLLIDER VISUALIZATION ENGINE V3 (WebGL + Token System)
# "The Final Form" - Now with DUAL SYSTEM: TOKENS → ENGINE
# -----------------------------------------------------------------------------

def generate_webgl_html(json_source, output_path):
    if isinstance(json_source, (str, Path)):
        print(f"Loading analysis data from {json_source}...")
        with open(json_source, 'r') as f:
            data = json.load(f)
    else:
        data = json_source
        print("Using in-memory analysis data...")

    # Initialize token-driven engines (THE TRIFECTA)
    appearance = AppearanceEngine()
    physics = PhysicsEngine()
    controls = ControlsEngine()
    resolver = get_resolver()

    nodes = data.get('nodes', [])
    edges = data.get('edges', [])
    meta = data.get('meta', {})

    # ==========================================================================
    # META FALLBACK: Prefer meta.* but fall back to root-level fields
    # This ensures backward compatibility with older output formats
    # ==========================================================================
    version = meta.get('version') or data.get('collider_version') or data.get('version', 'V3-Tokens')
    target_path = meta.get('target') or data.get('target_path') or data.get('target', 'Unknown')
    target_folder = Path(target_path).name if target_path and target_path != 'Unknown' else 'Unknown'
    timestamp = meta.get('timestamp') or data.get('timestamp', datetime.now().isoformat())

    # Format timestamp for display (just date + time, no seconds)
    try:
        ts_display = timestamp[:16].replace('T', ' ')  # "2026-01-15 01:21"
    except:
        ts_display = timestamp

    print(f"Processing {len(nodes)} nodes and {len(edges)} edges...")

    # ==========================================================================
    # DEGREE ENRICHMENT: Ensure sizes can reflect connectivity
    # ==========================================================================
    node_ids = {n.get('id') for n in nodes if n.get('id')}
    out_degree = defaultdict(int)
    in_degree = defaultdict(int)
    for e in edges:
        src = e.get('source')
        tgt = e.get('target')
        if src in node_ids:
            out_degree[src] += 1
        if tgt in node_ids:
            in_degree[tgt] += 1
    for n in nodes:
        nid = n.get('id')
        if not nid:
            continue
        if n.get('out_degree') is None:
            n['out_degree'] = out_degree.get(nid, 0)
        if n.get('in_degree') is None:
            n['in_degree'] = in_degree.get(nid, 0)
        if n.get('fan_out') is None:
            n['fan_out'] = n['out_degree']

    # ==========================================================================
    # FILE BOUNDARIES: Build file → node mapping for visualization
    # ==========================================================================
    file_boundaries = data.get('file_boundaries', []) or []
    files_index = data.get('files', {}) or {}

    # Fallback: synthesize file boundaries from nodes if missing
    if not file_boundaries:
        synthesized_index: Dict[str, Dict[str, Any]] = {}
        node_id_to_file: Dict[str, str] = {}
        for idx, node in enumerate(nodes):
            file_path = node.get('file_path') or node.get('file')
            if not file_path:
                continue
            entry = synthesized_index.setdefault(file_path, {
                "atoms": [],
                "atom_names": [],
                "classes": [],
                "functions": [],
                "line_range": [float('inf'), 0],
                "internal_edges": 0,
                "external_edges": 0,
                "atom_count": 0
            })
            entry["atoms"].append(idx)
            entry["atom_names"].append(node.get("name", ""))
            entry["atom_count"] += 1

            start_line = node.get("start_line") or node.get("line") or 0
            end_line = node.get("end_line") or start_line
            if start_line:
                entry["line_range"][0] = min(entry["line_range"][0], start_line)
                entry["line_range"][1] = max(entry["line_range"][1], end_line)

            kind = node.get("symbol_kind") or node.get("kind") or ""
            name = node.get("name", "")
            if kind == "class":
                entry["classes"].append(name)
            elif kind in ("function", "method"):
                entry["functions"].append(name)

            node_id = node.get("id")
            if node_id:
                node_id_to_file[node_id] = file_path

        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            src_file = node_id_to_file.get(src)
            tgt_file = node_id_to_file.get(tgt)
            if src_file and src_file in synthesized_index:
                if src_file == tgt_file:
                    synthesized_index[src_file]["internal_edges"] += 1
                else:
                    synthesized_index[src_file]["external_edges"] += 1

        synthesized_boundaries = []
        for file_path, entry in sorted(synthesized_index.items()):
            if entry["line_range"][0] == float("inf"):
                entry["line_range"] = [0, 0]
            cohesion = entry["internal_edges"] / max(1, entry["internal_edges"] + entry["external_edges"])
            file_name = Path(file_path).name
            lower_name = file_name.lower()
            if "test" in lower_name:
                purpose = "Test module"
            elif "util" in lower_name or "helper" in lower_name:
                purpose = "Utility module"
            elif "model" in lower_name or "entity" in lower_name:
                purpose = "Domain model"
            elif "service" in lower_name:
                purpose = "Service layer"
            elif "controller" in lower_name or "handler" in lower_name:
                purpose = "Interface layer"
            else:
                purpose = "General module"
            synthesized_boundaries.append({
                "file": file_path,
                "file_name": file_name,
                "atom_indices": entry["atoms"],
                "atom_count": entry["atom_count"],
                "line_range": entry["line_range"],
                "classes": entry["classes"],
                "functions": entry["functions"][:10],
                "cohesion": cohesion,
                "purpose": purpose
            })
        file_boundaries = synthesized_boundaries
        files_index = synthesized_index

    # Create node_id → file mapping
    node_to_file = {}
    file_to_index = {}
    for idx, boundary in enumerate(file_boundaries):
        file_path = boundary.get('file', '')
        file_to_index[file_path] = idx
        # Map node names to file index
        file_info = files_index.get(file_path, {})
        for atom_name in file_info.get('atom_names', []):
            node_to_file[atom_name] = idx

    total_files = len(file_boundaries)
    print(f"File boundaries: {total_files} files")

    # ==========================================================================
    # TOKEN-DRIVEN CONFIGURATION (via Engines - THE REMOTE CONTROL)
    # ==========================================================================
    # All visual parameters flow from schema/viz/tokens/*.json
    # SINGLE SOURCE OF TRUTH - no fallbacks in JS
    physics_config = physics.to_js_config()
    render_config = appearance.get_render_config()
    background_config = appearance.get_background_config()
    boundary_appearance = appearance.get_boundary_config()
    edge_modes_config = appearance.get_edge_modes_config()
    edge_color_config = appearance.get_edge_color_config()
    file_color_config = appearance.get_file_color_config()
    node_color_config = appearance.get_node_color_config()
    highlight_config = appearance.get_highlight_config()
    flow_mode_config = appearance.get_flow_mode_config()
    controls_config = controls.to_js_config()

    # ==========================================================================
    # KPI CALCULATION: Build KPIs from stats/architecture if not present
    # ==========================================================================
    kpis = data.get("kpis", {})
    if not kpis:
        stats = data.get("stats", {})
        arch = data.get("architecture", {})
        graph_inf = arch.get("graph_inference", {})

        # Calculate edge resolution from import_resolution stats
        import_res = stats.get("import_resolution", {})
        resolved = import_res.get("resolved", 0)
        unresolved = import_res.get("unresolved", 0)
        total_imports = resolved + unresolved
        edge_res_pct = (resolved / total_imports * 100) if total_imports > 0 else None

        # Calculate call ratio from edges
        call_edges = sum(1 for e in edges if e.get("type") == "calls")
        call_ratio_pct = (call_edges / len(edges) * 100) if edges else None

        # Get topology from graph inference
        topology = graph_inf.get("topology_class", "UNKNOWN")

        # Calculate orphan and hub counts from nodes
        orphan_count = sum(1 for n in nodes if n.get("in_degree", 0) == 0 and n.get("out_degree", 0) == 0)
        hub_threshold = 10
        top_hub_count = sum(1 for n in nodes if (n.get("in_degree", 0) + n.get("out_degree", 0)) > hub_threshold)

        # Get dead code percentage
        dead_code_pct = stats.get("unknown_percentage")

        kpis = {
            "edge_resolution_percent": edge_res_pct,
            "call_ratio_percent": call_ratio_pct,
            "reachability_percent": stats.get("coverage_percentage"),
            "dead_code_percent": dead_code_pct,
            "knot_score": graph_inf.get("knot_score"),
            "topology_shape": topology,
            "orphan_count": orphan_count,
            "top_hub_count": top_hub_count
        }

    # OPTIMIZATION: Minify payload for embedding
    graph_data = {
        "nodes": [],
        "links": [],
        "file_boundaries": file_boundaries,
        "brain_download": data.get("brain_download", ""),
        "kpis": kpis,
        "meta": meta,
        # Token-driven configs for JS (THE REMOTE CONTROL)
        "physics": physics_config,
        "appearance": {
            "render": render_config,
            "background": background_config,
            "boundary": boundary_appearance,
            "edge_modes": edge_modes_config,
            "edge_color": edge_color_config,
            "file_color": file_color_config,
            "node_color": node_color_config,
            "highlight": highlight_config,
            "flow_mode": flow_mode_config
        },
        "controls": controls_config,
        # Additional analysis layers
        "markov": data.get("markov", {}),
        "data_flow": data.get("data_flow", {})
    }

    # ==========================================================================
    # NODE PROCESSING: Apply appearance engine tokens
    # ==========================================================================
    # First, apply appearance tokens to all nodes (adds color, size)
    nodes_with_appearance = appearance.apply_to_nodes(nodes, file_boundaries, color_mode="tier")

    node_set = set()
    for n in nodes_with_appearance:
        nid = n.get('id')
        if not nid:
            continue
        atom = n.get('atom') or n.get('atom_id') or 'UNK'
        name = n.get('name', nid)
        file_path = n.get('file_path', '')

        # Get file index for grouping
        file_idx = file_to_index.get(file_path, -1)

        # Color comes from appearance engine (tier-based by default)
        color = n.get('color', '#888888')
        ring = n.get('ring') or n.get('layer') or 'Unknown'
        role = n.get('role') or (n.get('dimensions') or {}).get('D3_ROLE', 'Unknown')

        # Size comes from appearance engine
        size = n.get('size', 1.0)

        graph_data['nodes'].append({
            "id": nid,
            "name": name,
            "atom": atom,
            "val": size,
            "color": color,
            "layer": n.get('layer', 'Unknown'),
            "ring": ring,
            "role": role,
            "file": file_path,
            "fileIdx": file_idx,
            "body": n.get('body_source', '')[:500]  # First 500 chars for hover
        })
        node_set.add(nid)

    # ==========================================================================
    # EDGE PROCESSING: Apply appearance engine tokens
    # ==========================================================================
    edges_with_appearance = appearance.apply_to_edges(edges)
    default_edge_opacity = resolver.appearance(
        "color.edge-modes.opacity",
        resolver.appearance("opacity.edge", 0.2)
    )

    for e in edges_with_appearance:
        src = e.get('source')
        tgt = e.get('target')

        # Filter broken edges
        if src in node_set and tgt in node_set:
            graph_data['links'].append({
                "source": src,
                "target": tgt,
                "color": e.get('color', '#333333'),
                "opacity": e.get('opacity', default_edge_opacity),
                "edge_type": e.get('edge_type', e.get('type', 'default')),
                "weight": e.get('weight', 1.0),
                "markov_weight": e.get('markov_weight', 0.0),  # For flow visualization
                "confidence": e.get('confidence', 1.0),
                "resolution": e.get('resolution', 'unknown')
            })
            
    # Serialize Data
    print("optimizing payload (GZIP)...")
    import gzip
    import base64
    
    json_bytes = json.dumps(graph_data).encode('utf-8')
    compressed = gzip.compress(json_bytes)
    b64_payload = base64.b64encode(compressed).decode('utf-8')
    
    print(f"Original: {len(json_bytes)/1024/1024:.2f} MB")
    print(f"Compressed: {len(compressed)/1024/1024:.2f} MB")

    print("Generating HTML...")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Collider Universe v{version}</title>
    <style>
        body {{
            margin: 0;
            background-color: #050505;
            overflow: hidden;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #ffffff;
        }}

        body.hud-quiet .hud-panel {{
            background: rgba(6, 8, 12, 0.08);
            border-color: rgba(255, 255, 255, 0.02);
            box-shadow: none;
        }}

        body.hud-quiet .dock-btn {{
            background: rgba(255, 255, 255, 0.02);
            border-color: rgba(255, 255, 255, 0.03);
            color: #ffffff;
        }}

        body.hud-quiet .side-dock {{
            opacity: 0.4;
        }}
        
        /* HUD LIBRARIES */
        #hud {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none;
            z-index: 10;
            opacity: 0.32;
            transition: opacity 0.6s ease;
        }}
        
        /* HUD: Mission Control (Top Left) */
        .hud-panel {{
            position: absolute;
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(12px);
            padding: 15px;
            border-radius: 4px;
            pointer-events: auto;
            color: #ffffff;
            box-shadow: none;
        }}
        
        .top-left {{ top: 20px; left: 20px; width: 280px; }}
        .top-center {{
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            min-width: 200px;
            display: flex;
            gap: 20px;
            padding: 10px 25px;
        }}
        .top-center .stat {{ margin: 0; }}
        .metrics-panel {{ top: 20px; right: 20px; width: 260px; }}
        .report-panel {{
            top: 20px;
            right: 20px;
            width: 420px;
            height: 60vh;
            overflow: auto;
            display: none;
        }}
        .bottom-dock {{ 
            bottom: 20px; left: 50%; transform: translateX(-50%); 
            display: flex; gap: 10px; width: auto; 
            border-radius: 20px;
            padding: 10px 20px;
        }}

        .hud-toast {{
            position: absolute;
            top: 92px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(6, 8, 12, 0.7);
            border: 1px solid rgba(255,255,255,0.08);
            color: #ffffff;
            padding: 6px 14px;
            border-radius: 14px;
            font-size: 10px;
            letter-spacing: 0.6px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            z-index: 15;
        }}
        .hud-toast.visible {{
            opacity: 1;
        }}

        /* SIDE DOCK: Discrete Visibility + Appearance Controls */
        .side-dock {{
            --side-width: 260px;
            position: absolute;
            top: 120px;
            left: 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 30px;
            max-height: calc(100vh - 200px);
            opacity: 0.45;
            pointer-events: auto;
            transition: opacity 0.4s ease, width 0.4s ease;
            z-index: 12;
            overflow-y: auto;
            overflow-x: hidden;
        }}
        /* Hover to open (unless locked) */
        .side-dock:hover:not(.locked) {{
            opacity: 0.9;
            width: var(--side-width);
        }}
        .side-dock:hover:not(.locked) .side-content {{
            display: block;
        }}
        /* Locked state - always open */
        .side-dock.locked {{
            width: var(--side-width);
            opacity: 0.9;
        }}
        .side-dock.locked .side-content {{
            display: block;
        }}
        /* Legacy expanded class (kept for compatibility) */
        .side-dock.expanded {{
            width: var(--side-width);
            opacity: 0.9;
        }}
        .side-handle-row {{
            display: flex;
            gap: 6px;
            align-items: center;
        }}
        .side-handle {{
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.14);
            color: #ffffff;
            border-radius: 12px;
            padding: 6px 8px;
            font-size: 9px;
            cursor: pointer;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            flex-grow: 1;
        }}
        .side-lock {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            color: rgba(255,255,255,0.9);
            border-radius: 8px;
            padding: 4px 6px;
            font-size: 10px;
            cursor: pointer;
            display: none;
        }}
        .side-dock:hover .side-lock,
        .side-dock.locked .side-lock {{
            display: block;
        }}
        .side-dock.locked .side-lock {{
            background: rgba(255,200,50,0.2);
            border-color: rgba(255,200,50,0.4);
            color: rgba(255,200,50,0.9);
        }}
        .side-content {{
            display: none;
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            padding: 10px;
            backdrop-filter: blur(12px);
            overflow: hidden;
        }}
        .side-dock.expanded .side-content {{
            display: block;
        }}
        .side-section {{
            margin-bottom: 12px;
        }}
        .side-title {{
            font-size: 9px;
            color: rgba(255,255,255,0.9);
            letter-spacing: 1px;
            margin-bottom: 6px;
        }}
        .side-group {{
            margin-bottom: 10px;
        }}
        .side-group-title {{
            font-size: 9px;
            color: rgba(255,255,255,0.85);
            margin-bottom: 4px;
        }}
        .filter-list {{
            display: flex;
            flex-direction: column;
            gap: 4px;
            max-height: 160px;
            overflow: auto;
        }}
        .filter-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 10px;
            color: #ffffff;
            gap: 8px;
        }}
        .filter-item input[type="checkbox"] {{
            accent-color: #ffffff;
        }}
        .filter-count {{
            font-size: 9px;
            color: rgba(255,255,255,0.45);
        }}
        .filter-slider {{
            display: flex;
            flex-direction: column;
            gap: 4px;
            margin-bottom: 8px;
        }}
        .filter-slider label {{
            font-size: 9px;
            color: rgba(255,255,255,0.9);
        }}
        .filter-slider input[type="range"] {{
            width: 100%;
        }}
        
        h1 {{
            margin: 0 0 10px 0;
            font-size: 13px;
            font-weight: 500;
            letter-spacing: 0.6px;
            text-transform: none;
            color: #ffffff;
        }}
        .stat {{ display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 5px; color: #ffffff; }}
        .stat-val {{ color: #ffffff; font-weight: 500; }}
        .metric {{ display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 6px; color: #ffffff; }}
        .metric-val {{ color: #ffffff; font-weight: 500; }}
        
        /* Dock Buttons */
        .dock-btn {{
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            color: #ffffff;
            padding: 8px 16px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 10px;
            text-transform: none;
            transition: all 0.2s;
        }}
        .dock-btn:hover, .dock-btn.active {{
            border-color: rgba(255,255,255,0.3);
            color: #ffffff;
            box-shadow: none;
        }}
        .dock-btn.disabled {{
            opacity: 0.35;
            cursor: not-allowed;
            pointer-events: none;
        }}

        /* Datamap Toggles */
        .datamap-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        .datamap-toggle {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            color: #ffffff;
            padding: 6px 10px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 9px;
            text-transform: none;
            transition: all 0.2s;
        }}
        .datamap-toggle input {{
            accent-color: #6fe8ff;
        }}
        .datamap-toggle.disabled {{
            opacity: 0.35;
            cursor: not-allowed;
        }}
        .datamap-count {{
            font-size: 8px;
            color: rgba(255,255,255,0.55);
        }}
        .datamap-toggle:hover, .datamap-toggle.active {{
            border-color: rgba(255,255,255,0.3);
            color: #ffffff;
            box-shadow: none;
        }}
        .report-content {{
            color: #ffffff;
            font-family: Menlo, Monaco, Consolas, monospace;
            font-size: 11px;
            white-space: pre-wrap;
            line-height: 1.5;
        }}

        /* NODE HOVER PANEL - Quick info on hover */
        .hover-panel {{
            position: fixed;
            top: 100px;
            right: 20px;
            width: 280px;
            max-height: 300px;
            overflow: auto;
            display: none;
            z-index: 20;
            /* Dance animation: smooth repositioning */
            transition: left 150ms ease-out, top 150ms ease-out;
            will-change: left, top;
        }}
        .hover-panel.visible {{ display: block; }}
        .hover-panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            padding-bottom: 6px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .hover-panel-name {{
            font-size: 13px;
            font-weight: bold;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 200px;
        }}
        .hover-panel-kind {{
            font-size: 9px;
            padding: 2px 6px;
            border-radius: 8px;
            background: rgba(255,153,0,0.3);
            color: #ffcc80;
            text-transform: uppercase;
        }}
        .hover-panel-row {{
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            margin-bottom: 4px;
            color: #ffffff;
        }}
        .hover-panel-row .label {{
            color: rgba(255, 255, 255, 0.85);
            min-width: 70px;
        }}
        .hover-panel-row .value {{
            color: #ffffff;
            text-align: right;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 180px;
        }}
        .hover-panel-row .value.highlight {{
            color: #4ade80;
        }}
        .hover-panel-file {{
            font-size: 10px;
            color: rgba(255, 255, 255, 0.7);
            margin-top: 8px;
            padding-top: 6px;
            border-top: 1px solid rgba(255,255,255,0.15);
            word-break: break-all;
        }}

        /* SELECTION PANEL - Persistent selection summary */
        .selection-panel {{
            position: fixed;
            top: 140px;
            right: 20px;
            width: 320px;
            max-height: 360px;
            overflow: auto;
            display: none;
            z-index: 25;
            transition: left 150ms ease-out, top 150ms ease-out;
            will-change: left, top;
        }}
        .selection-panel.visible {{ display: block; }}
        .selection-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            padding-bottom: 6px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .selection-title {{
            font-size: 12px;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: 0.4px;
        }}
        .selection-clear {{
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            color: rgba(255,255,255,0.95);
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 9px;
            cursor: pointer;
        }}
        .selection-list {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .selection-item {{
            padding: 6px 8px;
            background: rgba(0, 0, 0, 0.50);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 6px;
        }}
        .selection-name {{
            font-size: 12px;
            color: #ffffff;
            font-weight: 500;
            margin-bottom: 4px;
        }}
        .selection-row {{
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            color: rgba(255,255,255,0.95);
        }}
        .selection-row .label {{
            color: rgba(255,255,255,0.85);
        }}
        .selection-summary {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            font-size: 10px;
            color: rgba(255,255,255,0.95);
        }}
        .selection-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 3px 8px;
            font-size: 9px;
            color: rgba(255,255,255,0.8);
        }}

        /* MODE TOAST - Brief hints when changing modes */
        .mode-toast {{
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 8px 16px;
            color: rgba(255, 255, 255, 0.9);
            font-size: 11px;
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.3px;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease-out;
            white-space: nowrap;
            backdrop-filter: blur(8px);
        }}
        .mode-toast.visible {{
            opacity: 1;
        }}

        /* FLOW LEGEND - Mini explanation for flow mode */
        .flow-legend {{
            position: fixed;
            bottom: 60px;
            right: 20px;
            background: rgba(0, 0, 0, 0.75);
            border: 1px solid rgba(255, 140, 0, 0.4);
            border-radius: 6px;
            padding: 6px 10px;
            color: rgba(255, 200, 100, 0.9);
            font-size: 10px;
            font-family: 'Inter', sans-serif;
            z-index: 50;
            display: none;
            backdrop-filter: blur(6px);
        }}
        .flow-legend.visible {{
            display: block;
        }}

        /* FILE HOVER PANEL - Smart Text Placement */
        .file-panel {{
            position: fixed;
            bottom: 100px;
            left: 20px;
            width: 400px;
            max-height: 350px;
            overflow: auto;
            display: none;
            /* Dance animation: smooth repositioning */
            transition: left 150ms ease-out, top 150ms ease-out;
            will-change: left, top;
        }}

        /* FILE MODE CONTROLS */
        .file-mode-controls {{
            display: none;
            gap: 5px;
            margin-left: 10px;
        }}
        .file-mode-controls.visible {{ display: flex; }}
        .file-expand-controls {{
            display: none;
            gap: 5px;
            margin-left: 8px;
        }}
        .file-expand-controls.visible {{ display: flex; }}
        .file-mode-btn,
        .file-expand-btn {{
            background: rgba(0,0,0,0.7);
            border: 1px solid #333;
            color: #ffffff;
            padding: 4px 10px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 9px;
            text-transform: uppercase;
        }}
        .file-mode-btn:hover, .file-mode-btn.active,
        .file-expand-btn:hover, .file-expand-btn.active {{
            border-color: #ff9900;
            color: #ffffff;
        }}
        .file-panel.visible {{ display: block; }}
        .file-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .file-name {{
            font-size: 14px;
            color: #ffffff;
            font-weight: bold;
        }}
        .file-cohesion {{
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 10px;
            background: rgba(0,243,255,0.2);
            color: #ffffff;
        }}
        .file-meta {{
            font-size: 11px;
            color: #ffffff;
            margin-bottom: 8px;
        }}
        .file-atoms {{
            font-size: 10px;
            color: #ffffff;
            margin-top: 8px;
            max-height: 100px;
            overflow: auto;
        }}
        .file-code {{
            font-family: Menlo, Monaco, Consolas, monospace;
            font-size: 10px;
            background: rgba(0,0,0,0.5);
            padding: 10px;
            border-radius: 4px;
            max-height: 150px;
            overflow: auto;
            white-space: pre;
            color: #ffffff;
        }}

        /* GROUPS LIST */
        .group-list {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .group-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 8px;
            border-radius: 8px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            cursor: pointer;
        }}
        .group-item.active {{
            border-color: rgba(140, 200, 255, 0.5);
            background: rgba(80, 140, 220, 0.18);
        }}
        .group-color {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
            border: 1px solid rgba(255,255,255,0.4);
        }}
        .group-name {{
            flex-grow: 1;
            font-size: 10px;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .group-count {{
            font-size: 9px;
            color: rgba(255,255,255,0.85);
        }}
        .group-toggle {{
            accent-color: #6fe8ff;
        }}

        /* SELECTION BOX (marquee) */
        #selection-box {{
            position: fixed;
            border: 1px solid rgba(100, 180, 255, 0.8);
            background: rgba(100, 180, 255, 0.12);
            display: none;
            pointer-events: none;
            z-index: 30;
        }}

        /* Loading Screen */
        #loader {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: #000;
            display: flex; flex-direction: column; 
            justify-content: center; align-items: center;
            z-index: 9999;
            color: #ffffff;
            font-family: monospace;
            font-size: 24px;
        }}
        #loader-status {{ font-size: 14px; margin-top: 10px; color: #ffffff; }}
        
    </style>
    
    <!-- ENGINE: UMD builds - works with file:// protocol (no CORS issues) -->
    <!-- Using older Three.js r149 that still has UMD support -->
    <script>
        window.process = window.process || {{ env: {{ NODE_ENV: "production" }} }};
        window.global = window.global || window;
    </script>
    <script src="https://unpkg.com/three@0.149.0/build/three.min.js"></script>
    <script src="https://unpkg.com/3d-force-graph@1.73.3/dist/3d-force-graph.min.js"></script>
    <script src="https://unpkg.com/pako@2.1.0/dist/pako.min.js"></script>
    <!-- Three.js Addons for r149 (examples/js still available) -->
    <script src="https://unpkg.com/three@0.149.0/examples/js/geometries/ConvexGeometry.js"></script>
</head>
<body>
    <div id="loader">
        <div>INITIALIZING UNIVERSE...</div>
        <div id="loader-status">DECOMPRESSING DATA...</div>
    </div>

    <div id="3d-graph"></div>

    <div id="hud">
        <div class="hud-panel top-left" id="header-panel">
            <h1 style="font-size: 16px; margin: 0 0 8px 0;">COLLIDER <span style="opacity: 0.5; font-size: 11px;">v{version}</span></h1>
            <div style="font-size: 11px; opacity: 0.7; margin-bottom: 4px;">{target_folder}</div>
            <div style="font-size: 10px; opacity: 0.5;">{ts_display}</div>
            <hr style="border-color: rgba(255,255,255,0.1); margin: 10px 0;">
            <div style="font-size: 9px; opacity: 0.5;">L-Drag Select · R-Drag Rotate · Space+Drag Pan · Scroll Zoom</div>
        </div>

        <!-- Central stats (moved from top-left for visual balance) -->
        <div class="hud-panel top-center" id="stats-panel">
            <div class="stat"><span>NODES</span><span class="stat-val">{len(nodes)}</span></div>
            <div class="stat"><span>EDGES</span><span class="stat-val">{len(edges)}</span></div>
            <div class="stat"><span>ENTROPY</span><span class="stat-val">OPTIMAL</span></div>
        </div>

        <div class="hud-panel metrics-panel" id="metrics-panel">
            <h1>System Metrics</h1>
            <div class="metric"><span>EDGE RES</span><span class="metric-val" id="metric-edge-resolution">--</span></div>
            <div class="metric"><span>CALL RATIO</span><span class="metric-val" id="metric-call-ratio">--</span></div>
            <div class="metric"><span>REACHABILITY</span><span class="metric-val" id="metric-reachability">--</span></div>
            <div class="metric"><span>DEAD CODE</span><span class="metric-val" id="metric-dead-code">--</span></div>
            <div class="metric"><span>KNOT SCORE</span><span class="metric-val" id="metric-knot-score">--</span></div>
            <div class="metric"><span>TOPOLOGY</span><span class="metric-val" id="metric-topology">--</span></div>
            <div class="metric"><span>ORPHANS</span><span class="metric-val" id="metric-orphans">--</span></div>
            <div class="metric"><span>TOP HUBS</span><span class="metric-val" id="metric-top-hubs">--</span></div>
        </div>

        <div class="hud-panel report-panel" id="report-panel">
            <h1>Collider Report</h1>
            <div class="report-content" id="report-content"></div>
        </div>

        <!-- NODE HOVER PANEL: Quick info when hovering a node -->
        <div class="hud-panel hover-panel" id="hover-panel">
            <div class="hover-panel-header">
                <span class="hover-panel-name" id="hover-name">Node Name</span>
                <span class="hover-panel-kind" id="hover-kind">function</span>
            </div>
            <div class="hover-panel-row">
                <span class="label">Atom</span>
                <span class="value" id="hover-atom">--</span>
            </div>
            <div class="hover-panel-row">
                <span class="label">Family</span>
                <span class="value highlight" id="hover-family">--</span>
            </div>
            <div class="hover-panel-row">
                <span class="label">Ring</span>
                <span class="value" id="hover-ring">--</span>
            </div>
            <div class="hover-panel-row">
                <span class="label">Tier</span>
                <span class="value" id="hover-tier">--</span>
            </div>
            <div class="hover-panel-row">
                <span class="label">Role</span>
                <span class="value" id="hover-role">--</span>
            </div>
            <div class="hover-panel-file" id="hover-file">file_path</div>
        </div>

        <!-- SELECTION PANEL: Persistent selection summary -->
        <div class="hud-panel selection-panel" id="selection-panel">
            <div class="selection-header">
                <span class="selection-title" id="selection-title">SELECTION</span>
                <button class="selection-clear" id="selection-clear">CLEAR</button>
            </div>
            <div class="selection-list" id="selection-body"></div>
        </div>

        <!-- FILE INFO PANEL: Shows on node hover -->
        <div class="hud-panel file-panel" id="file-panel">
            <div class="file-header">
                <span class="file-name" id="file-name">filename.py</span>
                <span class="file-cohesion" id="file-cohesion">Cohesion: 0%</span>
            </div>
            <div class="file-meta" id="file-meta">
                <div>Purpose: <span id="file-purpose">--</span></div>
                <div>Atoms: <span id="file-atom-count">0</span> | Lines: <span id="file-lines">0-0</span></div>
                <div>Classes: <span id="file-classes">--</span></div>
            </div>
            <div class="file-atoms" id="file-functions">Functions: loading...</div>
            <div class="file-code" id="file-code">// hover a node to see code</div>
        </div>

        <!-- SIDE DOCK: Hover-to-open filters with lock -->
        <div class="side-dock" id="side-dock">
            <div class="side-handle-row">
                <button class="side-handle" id="side-dock-toggle">FILTERS</button>
                <button class="side-lock" id="side-dock-lock" title="Lock sidebar open">🔓</button>
            </div>
            <div class="side-content" id="side-content">
                <div class="side-section" id="side-visibility">
                    <div class="side-title">VISIBILITY</div>
                    <div class="side-group">
                        <div class="side-group-title">TIERS</div>
                        <div class="filter-list" id="filter-tiers"></div>
                    </div>
                    <div class="side-group">
                        <div class="side-group-title">RINGS</div>
                        <div class="filter-list" id="filter-rings"></div>
                    </div>
                    <div class="side-group">
                        <div class="side-group-title">ROLES</div>
                        <div class="filter-list" id="filter-roles"></div>
                    </div>
                    <div class="side-group">
                        <div class="side-group-title">EDGES</div>
                        <div class="filter-list" id="filter-edges"></div>
                    </div>
                </div>
                <div class="side-section" id="side-appearance">
                    <div class="side-title">APPEARANCE</div>
                    <div class="side-group">
                        <div class="side-group-title">NODE COLOR</div>
                        <div class="filter-list" id="filter-node-color"></div>
                    </div>
                    <div class="side-group">
                        <div class="side-group-title">EDGE MODE</div>
                        <div class="filter-list" id="filter-edge-mode"></div>
                    </div>
                    <div id="appearance-sliders"></div>
                    <div class="side-group">
                        <div class="side-group-title">METADATA</div>
                        <div class="filter-list" id="filter-metadata"></div>
                    </div>
                </div>
                <div class="side-section" id="side-groups">
                    <div class="side-title">GROUPS</div>
                    <div class="group-list" id="group-list"></div>
                </div>
            </div>
        </div>

        <div class="hud-panel bottom-dock">
            <div class="datamap-controls" id="datamap-controls"></div>
            <button class="dock-btn disabled" id="btn-create-group" title="Create a group from selection">CREATE GROUP</button>
            <button class="dock-btn" id="btn-files">FILES</button>
            <!-- File visualization mode sub-controls -->
            <div class="file-mode-controls" id="file-mode-controls">
                <button class="file-mode-btn active" id="btn-file-color" title="Color atoms by file">COLOR</button>
                <button class="file-mode-btn" id="btn-file-hulls" title="Draw boundary hulls">HULLS</button>
                <button class="file-mode-btn" id="btn-file-cluster" title="Force cluster by file">CLUSTER</button>
                <button class="file-mode-btn" id="btn-file-map" title="Show file nodes">MAP</button>
            </div>
            <div class="file-expand-controls" id="file-expand-controls">
                <button class="file-expand-btn active" id="btn-expand-inline" title="Expand in place">INLINE</button>
                <button class="file-expand-btn" id="btn-expand-detach" title="Expand and detach">DETACH</button>
            </div>
            <button class="dock-btn" id="btn-flow" title="Markov chain - edge thickness by probability">FLOW</button>
            <button class="dock-btn" id="btn-edge-mode" title="Edge colors: type, resolution, weight, confidence">EDGE: TYPE</button>
            <button class="dock-btn" id="btn-report">REPORT</button>
            <button class="dock-btn active" id="btn-stars" title="Toggle background starfield">STARS</button>
            <button class="dock-btn" id="btn-reset-layout" title="Re-run physics simulation">RESET</button>
            <button class="dock-btn active" id="btn-hints" title="Show/hide mode hints">HINTS</button>
            <button class="dock-btn" id="btn-dimensions">2D</button>
        </div>
        <div class="flow-legend" id="flow-legend">FLOW: edge width = transition probability</div>
        <div class="hud-toast" id="hud-toast"></div>
    </div>

    <div id="selection-box"></div>

    <script>
        // UMD globals: THREE, ForceGraph3D, pako already loaded
        // Three.js addons attach to THREE global: THREE.ConvexGeometry
        const ConvexGeometry = THREE.ConvexGeometry;
        // Note: Post-processing (bloom) removed for simplicity - addons not available in r149+ UMD builds

        const COMPRESSED_PAYLOAD = "{b64_payload}";
        
        // --------------------------------------------------------------------
        // WEB WORKER: Decompression & Parsing (True Parallelism)
        // --------------------------------------------------------------------
        const workerScript = `
        importScripts('https://unpkg.com/pako@2.1.0/dist/pako.min.js');

        self.onmessage = function(e) {{
            const payload = e.data;
            try {{
                // 1. Decode Base64
                const charData = atob(payload);
                const binData = new Uint8Array(charData.length);
                for (let i = 0; i < charData.length; i++) {{
                    binData[i] = charData.charCodeAt(i);
                }}
                
                // 2. Inflate
                self.postMessage({{status: 'INFLATING...'}});
                const jsonStr = pako.inflate(binData, {{ to: 'string' }});
                
                // 3. Parse
                self.postMessage({{status: 'PARSING...'}});
                const data = JSON.parse(jsonStr);
                
                // 4. Pre-calc filter tiers (Optimization)
                // Filter out "noise" (orphans with 0 connections) if any
                // Calculate max density
                self.postMessage({{status: 'ANALYZING COSMOS...', result: data}});
                
            }} catch (err) {{
                self.postMessage({{error: err.message}});
            }}
        }};
        `;
        
        // Initialize Worker
        const blob = new Blob([workerScript], {{ type: 'application/javascript' }});
        const worker = new Worker(URL.createObjectURL(blob));
        
        let FULL_GRAPH = null;
        let Graph = null;
        let CURRENT_DENSITY = 1; // Default: show all nodes
        let ACTIVE_DATAMAPS = new Set();
        let DATAMAP_CONFIGS = [];
        let DATAMAP_INDEX = {{}};
        let DATAMAP_UI = new Map();
        let HOVERED_NODE = null;
        let SELECTED_NODE_IDS = new Set();
        let DATASET_KEY = 'default';
        let GROUPS_STORAGE_KEY = 'collider_groups_default';
        let GROUPS = [];
        let ACTIVE_GROUP_ID = null;
        let MARQUEE_ACTIVE = false;
        let MARQUEE_START = null;
        let SELECTION_BOX = null;
        let LAST_MARQUEE_END_TS = 0;
        const SELECTION_HALO_GEOMETRY = new THREE.SphereGeometry(1, 12, 12);
        const GROUP_HALO_GEOMETRY = new THREE.SphereGeometry(1, 12, 12);
        let IS_3D = true;
        let DIMENSION_TRANSITION = false;
        let STARFIELD = null;
        let STARFIELD_OPACITY = 0;
        let BLOOM_PASS = null;
        let BLOOM_STRENGTH = 0;
        let EDGE_MODE = 'type';
        let EDGE_DEFAULT_OPACITY = 0.2;
        let DEFAULT_LINK_DISTANCE = null;
        let EDGE_MODE_CONFIG = {{
            resolution: {{
                internal: '#4dd4ff',
                external: '#ff6b6b',
                unresolved: '#9aa0a6',
                unknown: '#666666'
            }},
            weight: {{ hue_min: 210, hue_max: 50, chroma: null, saturation: 45, lightness: 42 }},
            confidence: {{ hue_min: 20, hue_max: 120, chroma: null, saturation: 45, lightness: 44 }},
            width: {{ base: 0.8, weight_scale: 2.5, confidence_scale: 1.5 }},
            dim: {{ interfile_factor: 0.25 }},
            opacity: 0.12
        }};
        let EDGE_COLOR_CONFIG = {{
            default: '#333333',
            calls: '#4dd4ff',
            contains: '#00ff9d',
            uses: '#ffb800',
            imports: '#9aa0a6',
            inherits: '#ff6b6b'
        }};
        let FILE_COLOR_CONFIG = {{
            strategy: 'golden-angle',
            angle: 137.5,
            chroma: null,
            saturation: 70,
            lightness: 50
        }};
        let EDGE_RANGES = {{ weight: {{ min: 1, max: 1 }}, confidence: {{ min: 1, max: 1 }} }};
        let NODE_FILE_INDEX = new Map();
        let NODE_COLOR_CONFIG = {{ tier: {{}}, ring: {{}}, unknown: '#666666' }};
        let FLOW_CONFIG = {{}};  // Flow mode settings from THE REMOTE CONTROL
        let GRAPH_MODE = 'atoms'; // atoms | files | hybrid

        // Layout stability: cache node positions to prevent re-randomization on toggles
        let NODE_POSITION_CACHE = new Map();
        let LAYOUT_FROZEN = false;  // When true, don't reheat simulation
        let HINTS_ENABLED = true;   // Show mode toasts

        let FILE_GRAPH = null;
        let FILE_NODE_IDS = new Map();
        let FILE_NODE_POSITIONS = new Map();
        let EXPANDED_FILES = new Set();
        let FILE_EXPAND_MODE = 'inline'; // inline | detach
        let NODE_COLOR_MODE = 'tier';
        let COLOR_TWEAKS = {{
            hueShift: 0,
            chromaScale: 1,
            lightnessShift: 0
        }};
        let VIS_FILTERS = {{
            tiers: new Set(),
            rings: new Set(),
            roles: new Set(),
            edges: new Set(),
            metadata: {{
                showLabels: true,
                showFilePanel: true,
                showReportPanel: true,
                showEdges: true
            }}
        }};
        let SIDEBAR_STATE = {{
            open: false,
            locked: false
        }};
        let APPEARANCE_STATE = {{
            nodeScale: 1,
            edgeOpacity: null,
            boundaryFill: null,
            boundaryWire: null,
            backgroundBase: null,
            backgroundBrightness: 1,
            fileLightness: null,
            clusterStrength: null
        }};

        // =====================================================================
        // HUD LAYOUT MANAGER: Smart Text Placement with Collision Avoidance
        // =====================================================================
        const HudLayoutManager = {{
            // Margin from viewport edges
            MARGIN: 16,
            // Panels by priority (higher = more important, won't be moved)
            fixed: ['top-left-header', 'stats-panel', 'metrics-panel', 'bottom-dock', 'report-panel', 'side-dock'],
            // Dynamic panels in priority order (hover-panel > file-panel)
            dynamic: ['hover-panel', 'file-panel'],

            // Throttle state
            _rafPending: false,
            _lastReflow: 0,
            REFLOW_THROTTLE_MS: 50,

            // Mouse position for hover-panel placement
            _mouseX: 0,
            _mouseY: 0,

            // Get viewport rectangle
            getViewport() {{
                return {{
                    left: this.MARGIN,
                    top: this.MARGIN,
                    right: window.innerWidth - this.MARGIN,
                    bottom: window.innerHeight - this.MARGIN,
                    width: window.innerWidth - 2 * this.MARGIN,
                    height: window.innerHeight - 2 * this.MARGIN
                }};
            }},

            // Check if sidebar is effectively "open" (occupying space)
            isSidebarOpen() {{
                const sideDock = document.getElementById('side-dock');
                if (!sideDock) return false;
                return SIDEBAR_STATE.locked ||
                       SIDEBAR_STATE.open ||
                       sideDock.classList.contains('locked') ||
                       sideDock.classList.contains('expanded') ||
                       sideDock.matches(':hover');
            }},

            // Get rectangle for an element (returns null if hidden/missing)
            getRect(el) {{
                if (!el) return null;
                const style = window.getComputedStyle(el);
                if (style.display === 'none' || style.visibility === 'hidden') return null;
                const r = el.getBoundingClientRect();
                if (r.width === 0 && r.height === 0) return null;
                return {{ left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height }};
            }},

            // Get sidebar occupied region (full expanded width when open)
            getSidebarRect() {{
                const sideDock = document.getElementById('side-dock');
                if (!sideDock || !this.isSidebarOpen()) return null;
                const sideWidth = parseInt(getComputedStyle(sideDock).getPropertyValue('--side-width')) || 260;
                // Sidebar is on the left, vertically centered
                return {{
                    left: 0,
                    top: 0,
                    right: 16 + sideWidth + 20, // left margin + width + padding
                    bottom: window.innerHeight,
                    width: 16 + sideWidth + 20,
                    height: window.innerHeight
                }};
            }},

            // Get all occupied rectangles (fixed panels + sidebar when open)
            getOccupiedRects() {{
                const rects = [];

                // Sidebar takes priority when open
                const sidebarRect = this.getSidebarRect();
                if (sidebarRect) rects.push(sidebarRect);

                // Fixed panels
                this.fixed.forEach(id => {{
                    if (id === 'side-dock') return; // Handled separately above
                    const el = document.getElementById(id) || document.querySelector('.' + id);
                    const rect = this.getRect(el);
                    if (rect) rects.push(rect);
                }});

                // Top-left header (special case - class-based)
                const topLeft = document.querySelector('.top-left');
                const topLeftRect = this.getRect(topLeft);
                if (topLeftRect) rects.push(topLeftRect);

                return rects;
            }},

            // Calculate overlap area between two rectangles
            overlapArea(r1, r2) {{
                if (!r1 || !r2) return 0;
                const xOverlap = Math.max(0, Math.min(r1.right, r2.right) - Math.max(r1.left, r2.left));
                const yOverlap = Math.max(0, Math.min(r1.bottom, r2.bottom) - Math.max(r1.top, r2.top));
                return xOverlap * yOverlap;
            }},

            // Check if rect is fully inside viewport
            isInsideViewport(rect, viewport) {{
                return rect.left >= viewport.left &&
                       rect.top >= viewport.top &&
                       rect.right <= viewport.right &&
                       rect.bottom <= viewport.bottom;
            }},

            // Clamp position to keep panel inside viewport
            clampToViewport(pos, panelWidth, panelHeight, viewport) {{
                return {{
                    left: Math.max(viewport.left, Math.min(pos.left, viewport.right - panelWidth)),
                    top: Math.max(viewport.top, Math.min(pos.top, viewport.bottom - panelHeight))
                }};
            }},

            // Generate candidate positions for file panel (4 corners, biased away from sidebar)
            getFilePanelCandidates(panelWidth, panelHeight) {{
                const vp = this.getViewport();
                const margin = 20;
                const sidebarOpen = this.isSidebarOpen();
                const sidebarWidth = sidebarOpen ? 300 : 0;

                // Candidates: TR, BR, BL, TL (prefer right side when sidebar open)
                const candidates = sidebarOpen ? [
                    {{ left: vp.right - panelWidth - margin, top: vp.top + margin }},           // Top-right
                    {{ left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin }}, // Bottom-right
                    {{ left: sidebarWidth + margin, top: vp.bottom - panelHeight - margin }},  // Bottom-left (clear of sidebar)
                    {{ left: sidebarWidth + margin, top: vp.top + margin }}                     // Top-left (clear of sidebar)
                ] : [
                    {{ left: vp.left + margin, top: vp.bottom - panelHeight - margin }},       // Bottom-left (default)
                    {{ left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin }}, // Bottom-right
                    {{ left: vp.right - panelWidth - margin, top: vp.top + margin }},          // Top-right
                    {{ left: vp.left + margin, top: vp.top + margin }}                          // Top-left
                ];

                return candidates;
            }},

            // Generate candidate positions for selection panel (prefer right side)
            getSelectionPanelCandidates(panelWidth, panelHeight) {{
                const vp = this.getViewport();
                const margin = 20;
                const sidebarOpen = this.isSidebarOpen();
                const sidebarWidth = sidebarOpen ? 300 : 0;

                return sidebarOpen ? [
                    {{ left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin }}, // Bottom-right
                    {{ left: vp.right - panelWidth - margin, top: vp.top + margin }},                  // Top-right
                    {{ left: sidebarWidth + margin, top: vp.bottom - panelHeight - margin }},         // Bottom-left
                    {{ left: sidebarWidth + margin, top: vp.top + margin }}                           // Top-left
                ] : [
                    {{ left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin }},
                    {{ left: vp.right - panelWidth - margin, top: vp.top + margin }},
                    {{ left: vp.left + margin, top: vp.bottom - panelHeight - margin }},
                    {{ left: vp.left + margin, top: vp.top + margin }}
                ];
            }},

            // Generate candidate positions for hover panel (4 quadrants around mouse cursor)
            getHoverPanelCandidates(mouseX, mouseY, panelWidth, panelHeight) {{
                const vp = this.getViewport();
                const offset = 16;  // Offset from cursor

                // Account for sidebar when it's open
                const sidebarOpen = this.isSidebarOpen();
                const sidebarRect = sidebarOpen ? this.getSidebarRect() : null;
                const minLeft = sidebarRect ? sidebarRect.right + offset : vp.left;

                // Candidates: TR, BR, BL, TL around cursor position
                let candidates = [
                    {{ left: mouseX + offset, top: mouseY - panelHeight - offset }},        // Top-right of cursor
                    {{ left: mouseX + offset, top: mouseY + offset }},                       // Bottom-right of cursor
                    {{ left: mouseX - panelWidth - offset, top: mouseY + offset }},         // Bottom-left of cursor
                    {{ left: mouseX - panelWidth - offset, top: mouseY - panelHeight - offset }}  // Top-left of cursor
                ];

                // Ensure candidates clear the sidebar
                if (sidebarRect) {{
                    candidates = candidates.map(c => ({{
                        left: Math.max(c.left, minLeft),
                        top: c.top
                    }}));
                }}

                return candidates;
            }},

            // Update mouse position (called on mousemove)
            updateMousePosition(x, y) {{
                this._mouseX = x;
                this._mouseY = y;
            }},

            // Place a panel at the best position (least overlap)
            placePanel(panelEl, candidates, occupiedRects) {{
                if (!panelEl) return null;

                const rect = panelEl.getBoundingClientRect();
                const panelWidth = rect.width || 400;
                const panelHeight = rect.height || 350;
                const viewport = this.getViewport();

                let bestPos = candidates[0];
                let bestOverlap = Infinity;

                for (const pos of candidates) {{
                    const clampedPos = this.clampToViewport(pos, panelWidth, panelHeight, viewport);
                    const panelRect = {{
                        left: clampedPos.left,
                        top: clampedPos.top,
                        right: clampedPos.left + panelWidth,
                        bottom: clampedPos.top + panelHeight
                    }};

                    // Calculate total overlap with all occupied rects
                    let totalOverlap = 0;
                    for (const occRect of occupiedRects) {{
                        totalOverlap += this.overlapArea(panelRect, occRect);
                    }}

                    // Check viewport containment penalty
                    if (!this.isInsideViewport(panelRect, viewport)) {{
                        totalOverlap += 10000; // Heavy penalty for going outside viewport
                    }}

                    if (totalOverlap < bestOverlap) {{
                        bestOverlap = totalOverlap;
                        bestPos = clampedPos;
                        if (totalOverlap === 0) break; // Perfect position found
                    }}
                }}

                return bestPos;
            }},

            // Reflow all dynamic panels
            reflow() {{
                const now = Date.now();
                if (now - this._lastReflow < this.REFLOW_THROTTLE_MS) {{
                    // Throttle: schedule for later via RAF
                    if (!this._rafPending) {{
                        this._rafPending = true;
                        requestAnimationFrame(() => {{
                            this._rafPending = false;
                            this.reflow();
                        }});
                    }}
                    return;
                }}
                this._lastReflow = now;

                const occupiedRects = this.getOccupiedRects();

                // Place hover panel first (higher priority)
                const hoverPanel = document.getElementById('hover-panel');
                let hoverPanelRect = null;
                if (hoverPanel && hoverPanel.classList.contains('visible')) {{
                    const hoverWidth = hoverPanel.offsetWidth || 280;
                    const hoverHeight = hoverPanel.offsetHeight || 200;
                    const candidates = this.getHoverPanelCandidates(
                        this._mouseX, this._mouseY, hoverWidth, hoverHeight
                    );
                    const pos = this.placePanel(hoverPanel, candidates, occupiedRects);
                    if (pos) {{
                        hoverPanel.style.left = pos.left + 'px';
                        hoverPanel.style.top = pos.top + 'px';
                        hoverPanel.style.right = 'auto';
                        // Track hover panel rect for file panel to avoid
                        hoverPanelRect = {{
                            left: pos.left,
                            top: pos.top,
                            right: pos.left + hoverWidth,
                            bottom: pos.top + hoverHeight
                        }};
                    }}
                }}

                // Build occupied rects for file panel (includes hover panel if visible)
                const filePanelOccupied = [...occupiedRects];
                if (hoverPanelRect) {{
                    filePanelOccupied.push(hoverPanelRect);
                }}

                // Place selection panel (secondary priority)
                const selectionPanel = document.getElementById('selection-panel');
                let selectionPanelRect = null;
                if (selectionPanel && selectionPanel.classList.contains('visible')) {{
                    const candidates = this.getSelectionPanelCandidates(
                        selectionPanel.offsetWidth || 320,
                        selectionPanel.offsetHeight || 280
                    );
                    const pos = this.placePanel(selectionPanel, candidates, filePanelOccupied);
                    if (pos) {{
                        selectionPanel.style.left = pos.left + 'px';
                        selectionPanel.style.top = pos.top + 'px';
                        selectionPanel.style.right = 'auto';
                        selectionPanelRect = {{
                            left: pos.left,
                            top: pos.top,
                            right: pos.left + (selectionPanel.offsetWidth || 320),
                            bottom: pos.top + (selectionPanel.offsetHeight || 280)
                        }};
                        filePanelOccupied.push(selectionPanelRect);
                    }}
                }}

                // Place file panel (lower priority, avoids hover panel too)
                const filePanel = document.getElementById('file-panel');
                if (filePanel && filePanel.classList.contains('visible')) {{
                    const candidates = this.getFilePanelCandidates(
                        filePanel.offsetWidth || 400,
                        filePanel.offsetHeight || 350
                    );
                    const pos = this.placePanel(filePanel, candidates, filePanelOccupied);
                    if (pos) {{
                        filePanel.style.left = pos.left + 'px';
                        filePanel.style.top = pos.top + 'px';
                        filePanel.style.bottom = 'auto'; // Override default bottom positioning
                    }}
                }}
            }},

            // Initialize event listeners for reflow triggers
            init() {{
                // Window resize
                window.addEventListener('resize', () => this.reflow());

                // Track mouse position for hover-panel placement
                window.addEventListener('mousemove', (e) => {{
                    this.updateMousePosition(e.clientX, e.clientY);
                }}, {{ passive: true }});

                // Sidebar state changes (lock toggle is handled separately)
                const sideDock = document.getElementById('side-dock');
                if (sideDock) {{
                    sideDock.addEventListener('mouseenter', () => this.reflow());
                    sideDock.addEventListener('mouseleave', () => {{
                        // Delay reflow slightly to let CSS transition complete
                        setTimeout(() => this.reflow(), 200);
                    }});
                }}

                console.log('[HudLayoutManager] Initialized');
            }}
        }};

        worker.onmessage = function(e) {{
            if (e.data.status && !e.data.result) {{
                document.getElementById('loader-status').innerText = e.data.status;
            }} else if (e.data.error) {{
                document.getElementById('loader-status').innerText = "ERROR: " + e.data.error;
                document.getElementById('loader-status').style.color = "red";
            }} else if (e.data.result) {{
                FULL_GRAPH = e.data.result;
                FILE_GRAPH = null;
                FILE_NODE_POSITIONS = new Map();
                EXPANDED_FILES.clear();
                GRAPH_MODE = 'atoms';
                document.getElementById('loader-status').innerText = "INITIALIZING VISUALIZATION...";
                initGraph(FULL_GRAPH);
            }}
        }};
        
        // Start Work
        worker.postMessage(COMPRESSED_PAYLOAD);

        function initGraph(data) {{
            // =================================================================
            // TOKEN-DRIVEN CONFIG: Extract from payload
            // =================================================================
            const physicsConfig = data.physics || {{}};
            const appearanceConfig = data.appearance || {{}};
            const simulation = physicsConfig.simulation || {{}};
            const background = appearanceConfig.background || {{}};
            const stars = background.stars || {{}};
            const bloom = background.bloom || {{}};
            // NEW: Render, highlight, flow_mode from THE REMOTE CONTROL
            const renderConfig = appearanceConfig.render || {{}};
            const highlightConfig = appearanceConfig.highlight || {{}};
            FLOW_CONFIG = appearanceConfig.flow_mode || {{}};
            const edgeModes = appearanceConfig.edge_modes || {{}};
            EDGE_MODE_CONFIG = {{
                resolution: edgeModes.resolution || EDGE_MODE_CONFIG.resolution,
                weight: edgeModes.weight || EDGE_MODE_CONFIG.weight,
                confidence: edgeModes.confidence || EDGE_MODE_CONFIG.confidence,
                width: edgeModes.width || EDGE_MODE_CONFIG.width,
                dim: edgeModes.dim || EDGE_MODE_CONFIG.dim,
                opacity: (typeof edgeModes.opacity === 'number') ? edgeModes.opacity : EDGE_MODE_CONFIG.opacity
            }};
            FILE_COLOR_CONFIG = Object.assign({{}}, FILE_COLOR_CONFIG, appearanceConfig.file_color || {{}});
            EDGE_DEFAULT_OPACITY =
                (typeof EDGE_MODE_CONFIG.opacity === 'number') ? EDGE_MODE_CONFIG.opacity : EDGE_DEFAULT_OPACITY;
            const boundaryConfig = appearanceConfig.boundary || {{}};
            APPEARANCE_STATE.edgeOpacity = EDGE_DEFAULT_OPACITY;
            APPEARANCE_STATE.boundaryFill = boundaryConfig.fill_opacity ?? APPEARANCE_STATE.boundaryFill;
            APPEARANCE_STATE.boundaryWire = boundaryConfig.wire_opacity ?? APPEARANCE_STATE.boundaryWire;
            APPEARANCE_STATE.backgroundBase = background.color || '#000000';
            APPEARANCE_STATE.fileLightness = FILE_COLOR_CONFIG.lightness ?? APPEARANCE_STATE.fileLightness;
            const nodeColor = appearanceConfig.node_color || {{}};
            NODE_COLOR_CONFIG = {{
                tier: nodeColor.tier || {{}},
                ring: nodeColor.ring || {{}},
                unknown: nodeColor.unknown || '#666666'
            }};
            const edgeColor = appearanceConfig.edge_color || {{}};
            EDGE_COLOR_CONFIG = Object.assign({{}}, EDGE_COLOR_CONFIG, edgeColor);

            // Initial Filter: show full graph
            const filtered = filterGraph(data, CURRENT_DENSITY, ACTIVE_DATAMAPS, VIS_FILTERS);

            const div = document.getElementById('3d-graph');

            // TOKEN-DRIVEN: Read render config from THE REMOTE CONTROL
            const dimensions = renderConfig.dimensions || 3;
            const nodeRes = renderConfig.nodeResolution || 8;

            Graph = ForceGraph3D()
                (div)
                .graphData(filtered)
                .numDimensions(dimensions)
                .backgroundColor(toColorNumber(background.color, 0x000000))
                .nodeLabel('name')
                .nodeColor(node => toColorNumber(node.color, 0x888888))
                .nodeVal(node => (node.val || 1) * APPEARANCE_STATE.nodeScale)
                .linkColor(link => toColorNumber(getEdgeColor(link), 0x222222))
                .linkOpacity(link => (link.opacity ?? EDGE_DEFAULT_OPACITY))
                .nodeThreeObjectExtend(true)
                .nodeThreeObject(node => ensureNodeOverlays(node))
                .nodeResolution(nodeRes)
                .showNavInfo(false)
                .warmupTicks(simulation.warmupTicks || 30)
                .cooldownTicks(simulation.cooldownTicks || 0)
                .onNodeHover(node => handleNodeHover(node, data))
                .onNodeClick((node, event) => handleNodeClick(node, event))
                .onBackgroundClick(() => maybeClearSelection())
                .onEngineStop(() => {{
                    document.getElementById('loader').style.display = 'none';
                    drawFileBoundaries(data);
                    // LAYOUT STABILITY: Freeze layout after initial simulation completes
                    if (!LAYOUT_FROZEN) {{
                        saveNodePositions();
                        freezeLayout();
                    }}
                }});

            window.Graph = Graph;
            initSelectionState(data);
            setupSelectionInteractions();
            updateSelectionVisuals();

            // =================================================================
            // CONTROLS: keep default camera behavior, enable damping
            // =================================================================
            const controls = Graph.controls();
            if (controls) {{
                controls.enableDamping = true;
                controls.dampingFactor = 0.1;
            }}

            // =================================================================
            // TOKEN-DRIVEN: Force Configuration
            // =================================================================
            const forces = physicsConfig.forces || {{}};
            if (forces.charge?.enabled) {{
                Graph.d3Force('charge').strength(forces.charge.strength || -120);
                Graph.d3Force('charge').distanceMax(forces.charge.distanceMax || 500);
            }}
            if (forces.link?.enabled) {{
                const linkDistance = forces.link.distance || 50;
                Graph.d3Force('link').distance(linkDistance);
                DEFAULT_LINK_DISTANCE = linkDistance;
            }}
            if (forces.center?.enabled) {{
                Graph.d3Force('center').strength(forces.center.strength || 0.05);
            }}

            // =================================================================
            // TOKEN-DRIVEN: Starfield (Cosmic Background)
            // =================================================================
            const scene = Graph.scene();
            const starsGeometry = new THREE.BufferGeometry();
            const starsCount = stars.count || 2000;
            const starsSpread = stars.spread || 5000;
            const posArray = new Float32Array(starsCount * 3);

            for(let i = 0; i < starsCount * 3; i++) {{
                posArray[i] = (Math.random() - 0.5) * starsSpread;
            }}

            starsGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
            const starsMaterial = new THREE.PointsMaterial({{
                size: stars.size || 2,
                color: 0xffffff,
                transparent: true,
                opacity: stars.opacity || 0.8,
            }});
            const starMesh = new THREE.Points(starsGeometry, starsMaterial);
            scene.add(starMesh);
            STARFIELD = starMesh;
            STARFIELD_OPACITY = starsMaterial.opacity;

            // =================================================================
            // TOKEN-DRIVEN: Bloom Post-Processing (DISABLED - UMD build compatibility)
            // Post-processing addons require ES modules; using UMD for file:// support
            // =================================================================
            // Bloom disabled for compatibility - visualization works without it

            // Setup Hud Controls (TOKEN-DRIVEN)
            setupControls(data);
            setupReport(data);
            setupMetrics(data);
            setupHudFade();
            setupDimensionToggle();
            applyEdgeMode();

            // =================================================================
            // SELF-TEST: Deterministic validation of UI controls
            // =================================================================
            runSelfTest(data);
        }}

        function runSelfTest(data) {{
            const results = {{
                timestamp: new Date().toISOString(),
                passed: [],
                failed: []
            }};

            const test = (name, condition) => {{
                if (condition) {{
                    results.passed.push(name);
                }} else {{
                    results.failed.push(name);
                }}
            }};

            // Test 1: Core UI elements exist
            test('slider-density-exists', !!document.getElementById('density-slider'));
            const datamapContainer = document.getElementById('datamap-controls');
            test('datamap-controls-exist', !!datamapContainer);
            test('datamap-controls-has-input', !!datamapContainer?.querySelector('input[type="checkbox"]'));
            test('btn-files-exists', !!document.getElementById('btn-files'));
            test('btn-flow-exists', !!document.getElementById('btn-flow'));
            test('btn-edge-mode-exists', !!document.getElementById('btn-edge-mode'));
            test('btn-report-exists', !!document.getElementById('btn-report'));
            test('btn-stars-exists', !!document.getElementById('btn-stars'));
            test('btn-dimensions-exists', !!document.getElementById('btn-dimensions'));
            test('starfield-initialized', !!STARFIELD);
            test('side-dock-lock-exists', !!document.getElementById('side-dock-lock'));
            test('sidebar-state-has-locked', SIDEBAR_STATE && 'locked' in SIDEBAR_STATE);

            // Test 1b: Sidebar lock functional test (programmatic, no hover needed)
            const sideDock = document.getElementById('side-dock');
            const sideContent = document.getElementById('side-content');
            if (sideDock && sideContent) {{
                // Simulate lock
                sideDock.classList.add('locked');
                const contentVisible = window.getComputedStyle(sideContent).display !== 'none';
                test('sidebar-lock-reveals-content', contentVisible);
                // Clean up
                sideDock.classList.remove('locked');
            }}

            // Test 1c: HUD Layout Manager tests
            test('hud-layout-manager-exists', typeof HudLayoutManager === 'object' && HudLayoutManager !== null);
            test('hud-layout-manager-has-reflow', typeof HudLayoutManager.reflow === 'function');
            test('hud-layout-manager-has-placePanel', typeof HudLayoutManager.placePanel === 'function');

            // Test 1d: HUD placement with synthetic rects (collision avoidance)
            if (typeof HudLayoutManager.placePanel === 'function') {{
                // Create a test scenario: occupied rect on top-left, panel should avoid it
                const fakeOccupied = [{{ left: 0, top: 0, right: 300, bottom: 200 }}];
                const fakeCandidates = [
                    {{ left: 20, top: 100 }},   // Would overlap with occupied
                    {{ left: 400, top: 100 }}   // Should be clear
                ];
                // Create a mock panel element
                const mockPanel = document.createElement('div');
                mockPanel.style.width = '200px';
                mockPanel.style.height = '150px';
                mockPanel.style.position = 'fixed';
                document.body.appendChild(mockPanel);

                const result = HudLayoutManager.placePanel(mockPanel, fakeCandidates, fakeOccupied);
                // Should choose the second candidate (no overlap)
                const pickedNonOverlapping = result && result.left >= 300;
                test('hud-placement-avoids-overlap', pickedNonOverlapping);

                document.body.removeChild(mockPanel);
            }}

            // Test 1e: Canonical taxonomy field tests
            // Test that node.tier is preferred over atom prefix inference
            const mockNodeWithTier = {{ tier: 'T2', atom: 'CORE.001', ring: 'DOMAIN' }};
            const tierResult = getNodeTier(mockNodeWithTier);
            test('node-tier-prefers-field', tierResult === 'T2');  // Should use tier field, not infer T0 from CORE.

            // Test that node.ring is used when present
            const mockNodeWithRing = {{ ring: 'PRESENTATION', layer: 'APPLICATION' }};
            const ringResult = getNodeRing(mockNodeWithRing);
            test('node-ring-prefers-field', ringResult === 'PRESENTATION');  // Should use ring, not layer

            // Test tier aliases work (CORE → T0, EXT → T2)
            test('tier-alias-core-to-t0', normalizeTier('CORE') === 'T0');
            test('tier-alias-ext-to-t2', normalizeTier('EXT') === 'T2');

            // Test atom_family extraction
            const mockNodeWithFamily = {{ atom_family: 'LOG', atom: 'ORG.AGG.M' }};
            const familyResult = getNodeAtomFamily(mockNodeWithFamily);
            test('node-atom-family-prefers-field', familyResult === 'LOG');  // Should use atom_family, not infer ORG

            // Test 1f: Hover panel tests
            test('hover-panel-exists', document.getElementById('hover-panel') !== null);

            // Test hover panel uses canonical fields
            const mockCanonicalNode = {{
                name: 'TestNode',
                atom_family: 'LOG',
                ring: 'PRESENTATION',
                tier: 'T2',
                atom: 'ORG.AGG.M',
                kind: 'function',
                role: 'Utility'
            }};
            // Simulate updateHoverPanel with mock node
            if (typeof updateHoverPanel === 'function') {{
                updateHoverPanel(mockCanonicalNode);
                const hoverFamily = document.getElementById('hover-family')?.textContent;
                const hoverRing = document.getElementById('hover-ring')?.textContent;
                const hoverTier = document.getElementById('hover-tier')?.textContent;
                // Verify canonical fields are used (LOG not ORG, PRESENTATION, T2)
                test('hover-panel-uses-canonical-fields',
                    hoverFamily === 'LOG' && hoverRing === 'PRESENTATION' && hoverTier === 'T2');
                // Clean up: hide panel
                updateHoverPanel(null);
            }}

            // Test 2: Metrics panel populated
            test('metric-edge-resolution', document.getElementById('metric-edge-resolution')?.textContent !== '--');
            test('metric-call-ratio', document.getElementById('metric-call-ratio')?.textContent !== '--');
            test('metric-reachability', document.getElementById('metric-reachability')?.textContent !== '--');
            test('metric-dead-code', document.getElementById('metric-dead-code')?.textContent !== '--');
            test('metric-topology', document.getElementById('metric-topology')?.textContent !== '--');

            // Test 3: Data integrity
            test('nodes-count-positive', data.nodes && data.nodes.length > 0);
            test('links-count-positive', data.links && data.links.length > 0);
            test('graph-initialized', !!window.Graph);

            // Test 4: Controls config loaded
            test('controls-config-exists', !!data.controls);
            test('appearance-config-exists', !!data.appearance);
            test('physics-config-exists', !!data.physics);

            // Test 5: Initial state correct
            const densitySlider = document.getElementById('density-slider');
            test('density-slider-has-value', densitySlider && densitySlider.value !== undefined);
            test('3d-mode-default', IS_3D === true);

            // Expose results to window for external testing
            window.SELF_TEST_RESULTS = results;

            // Log summary
            const total = results.passed.length + results.failed.length;
            const passRate = ((results.passed.length / total) * 100).toFixed(1);

            if (results.failed.length === 0) {{
                console.log(`%c✅ SELF-TEST PASSED: ${{results.passed.length}}/${{total}} tests (${{passRate}}%)`, 'color: #00ff00; font-weight: bold');
            }} else {{
                console.warn(`%c⚠️ SELF-TEST: ${{results.passed.length}}/${{total}} passed (${{passRate}}%)`, 'color: #ffaa00; font-weight: bold');
                console.warn('Failed tests:', results.failed);
            }}

            return results;
        }}
        
        // Tier aliases: legacy names → canonical T0/T1/T2
        const TIER_ALIASES = {{
            'CORE': 'T0', 'T0': 'T0',
            'ARCH': 'T1', 'T1': 'T1',
            'EXT': 'T2', 'T2': 'T2',
            'DISCOVERED': 'T2',  // EXT.DISCOVERED → T2
            'UNKNOWN': 'UNKNOWN'
        }};

        function normalizeTier(tier) {{
            if (!tier) return 'UNKNOWN';
            const upper = String(tier).toUpperCase();
            return TIER_ALIASES[upper] || upper;
        }}

        // Prefer canonical node.tier field; fallback to atom prefix inference
        function getNodeTier(node) {{
            // If node is a string (backward compat: called with atomId), infer from prefix
            if (typeof node === 'string') {{
                const atomId = node;
                if (!atomId) return 'UNKNOWN';
                if (atomId.startsWith('CORE.')) return 'T0';
                if (atomId.startsWith('ARCH.')) return 'T1';
                if (atomId.startsWith('EXT.')) return 'T2';
                return 'UNKNOWN';
            }}
            // Prefer canonical field
            if (node.tier) {{
                return normalizeTier(node.tier);
            }}
            // Fallback: infer from atom prefix
            const atomId = String(node.atom || '');
            if (atomId.startsWith('CORE.')) return 'T0';
            if (atomId.startsWith('ARCH.')) return 'T1';
            if (atomId.startsWith('EXT.')) return 'T2';
            return 'UNKNOWN';
        }}

        // Get atom family from canonical field or infer from atom prefix
        function getNodeAtomFamily(node) {{
            // Prefer canonical field
            if (node.atom_family) {{
                return String(node.atom_family).toUpperCase();
            }}
            // Fallback: infer from atom (e.g., "LOG.FNC.M" → "LOG")
            const atomId = String(node.atom || '');
            const dotIdx = atomId.indexOf('.');
            if (dotIdx > 0) {{
                return atomId.substring(0, dotIdx).toUpperCase();
            }}
            return 'UNKNOWN';
        }}

        function getNodeRing(node) {{
            const ring = node.ring || node.layer || 'UNKNOWN';
            return String(ring).toUpperCase();
        }}

        function getNodeColorByMode(node) {{
            if (NODE_COLOR_MODE === 'file') {{
                const fileIdx = node.fileIdx ?? -1;
                if (fileIdx < 0) {{
                    return normalizeColorInput(NODE_COLOR_CONFIG.unknown || '#666666');
                }}
                const totalFiles = (FULL_GRAPH?.file_boundaries || []).length;
                const fileInfo = (FULL_GRAPH?.file_boundaries || [])[fileIdx] || {{}};
                const fileLabel = fileInfo.file || fileInfo.file_name || fileIdx;
                return getFileColor(fileIdx, totalFiles, fileLabel);
            }}

            // Atom family color palette (LOG=blue, DAT=green, ORG=purple, EXE=red, EXT=orange)
            const ATOM_FAMILY_COLORS = {{
                'LOG': '#4a9eff',   // Blue - logic/functions
                'DAT': '#4ade80',   // Green - data/DTOs
                'ORG': '#a78bfa',   // Purple - organizational
                'EXE': '#f87171',   // Red - execution/entry
                'EXT': '#fb923c',   // Orange - external/extensions
                'UNKNOWN': '#666666'
            }};

            if (NODE_COLOR_MODE === 'family') {{
                const atomFamily = getNodeAtomFamily(node);
                return ATOM_FAMILY_COLORS[atomFamily] || ATOM_FAMILY_COLORS.UNKNOWN;
            }}

            if (NODE_COLOR_MODE === 'ring') {{
                const ring = getNodeRing(node);
                const ringColor = NODE_COLOR_CONFIG.ring?.[ring];
                if (ringColor) {{
                    return normalizeColorInput(ringColor, '#666666');
                }}
                // Fallback: if ring is UNKNOWN or unmapped, use atom_family palette
                if (ring === 'UNKNOWN' || !NODE_COLOR_CONFIG.ring?.[ring]) {{
                    const atomFamily = getNodeAtomFamily(node);
                    return ATOM_FAMILY_COLORS[atomFamily] || ATOM_FAMILY_COLORS.UNKNOWN;
                }}
                const hue = hashToUnit(ring) * 360;
                return oklchColor(60, 0.12, hue);
            }}

            // Tier color mode (default)
            const tier = getNodeTier(node);
            const tierColor = NODE_COLOR_CONFIG.tier?.[tier] || NODE_COLOR_CONFIG.tier?.UNKNOWN;
            return normalizeColorInput(tierColor || NODE_COLOR_CONFIG.unknown || '#666666', '#666666');
        }}

        function applyNodeColors(nodes) {{
            nodes.forEach(node => {{
                if (node && node.isFileNode) {{
                    if (!node.color) {{
                        const totalFiles = (FULL_GRAPH?.file_boundaries || []).length;
                        const fileInfo = (FULL_GRAPH?.file_boundaries || [])[node.fileIdx] || {{}};
                        const fileLabel = fileInfo.file || fileInfo.file_name || node.fileIdx;
                        node.color = getFileColor(node.fileIdx, totalFiles, fileLabel);
                    }}
                    return;
                }}
                if (fileMode) {{
                    return;
                }}
                node.color = getNodeColorByMode(node);
            }});
        }}

        function filterGraph(data, minVal, datamapSet, filters) {{
            const tierFilter = filters?.tiers || new Set();
            const ringFilter = filters?.rings || new Set();
            const roleFilter = filters?.roles || new Set();
            const edgeFilter = filters?.edges || new Set();
            const showEdges = filters?.metadata?.showEdges !== false;

            // Filter nodes by size/importance
            let visibleNodes = data.nodes.filter(n => n.val >= minVal);

            if (datamapSet && datamapSet.size > 0) {{
                visibleNodes = visibleNodes.filter(n => {{
                    for (const id of datamapSet) {{
                        const config = DATAMAP_INDEX[id];
                        if (config && datamapMatches(n, config)) return true;
                    }}
                    return false;
                }});
            }}

            if (tierFilter.size > 0) {{
                visibleNodes = visibleNodes.filter(n => tierFilter.has(getNodeTier(n)));
            }}

            if (ringFilter.size > 0) {{
                visibleNodes = visibleNodes.filter(n => ringFilter.has(getNodeRing(n)));
            }}

            if (roleFilter.size > 0) {{
                visibleNodes = visibleNodes.filter(n => roleFilter.has(String(n.role || 'Unknown')));
            }}

            const visibleIds = new Set(visibleNodes.map(n => n.id));

            // Keep edges only between visible nodes
            let visibleLinks = data.links.filter(l =>
                visibleIds.has(l.source.id || l.source) &&
                visibleIds.has(l.target.id || l.target)
            );

            if (edgeFilter.size > 0) {{
                visibleLinks = visibleLinks.filter(l => edgeFilter.has(String(l.edge_type || l.type || 'default')));
            }}

            if (!showEdges) {{
                visibleLinks = [];
            }}

            return {{ nodes: visibleNodes, links: visibleLinks }};
        }}

        // ====================================================================
        // LAYOUT STABILITY: Preserve node positions across graph updates
        // ====================================================================
        function saveNodePositions() {{
            if (!Graph) return;
            const nodes = Graph.graphData().nodes || [];
            nodes.forEach(node => {{
                if (node.x !== undefined && node.y !== undefined) {{
                    NODE_POSITION_CACHE.set(node.id, {{
                        x: node.x, y: node.y, z: node.z || 0,
                        vx: node.vx || 0, vy: node.vy || 0, vz: node.vz || 0,
                        fx: node.fx, fy: node.fy, fz: node.fz
                    }});
                }}
            }});
        }}

        function restoreNodePositions(nodes) {{
            nodes.forEach(node => {{
                const cached = NODE_POSITION_CACHE.get(node.id);
                if (cached) {{
                    node.x = cached.x;
                    node.y = cached.y;
                    node.z = cached.z;
                    node.vx = cached.vx;
                    node.vy = cached.vy;
                    node.vz = cached.vz;
                    // Pin nodes in place when layout is frozen
                    if (LAYOUT_FROZEN) {{
                        node.fx = cached.x;
                        node.fy = cached.y;
                        node.fz = cached.z;
                    }}
                }}
            }});
        }}

        function freezeLayout() {{
            LAYOUT_FROZEN = true;
            if (!Graph) return;
            const nodes = Graph.graphData().nodes || [];
            nodes.forEach(node => {{
                if (node.x !== undefined) {{
                    node.fx = node.x;
                    node.fy = node.y;
                    node.fz = node.z;
                }}
            }});
            Graph.cooldownTicks(0);  // Stop simulation immediately
        }}

        function unfreezeLayout() {{
            LAYOUT_FROZEN = false;
            if (!Graph) return;
            const nodes = Graph.graphData().nodes || [];
            nodes.forEach(node => {{
                node.fx = undefined;
                node.fy = undefined;
                node.fz = undefined;
            }});
        }}

        function resetLayout() {{
            // Clear position cache and reheat simulation
            NODE_POSITION_CACHE.clear();
            unfreezeLayout();
            if (Graph) {{
                Graph.cooldownTicks(200);  // Allow simulation to run
                Graph.d3ReheatSimulation();
            }}
            showModeToast('Layout reset - physics running');
        }}

        // ====================================================================
        // MODE TOASTS: Brief hints when changing modes
        // ====================================================================
        let _toastTimeout = null;

        function showModeToast(message) {{
            if (!HINTS_ENABLED) return;

            let toast = document.getElementById('mode-toast');
            if (!toast) {{
                toast = document.createElement('div');
                toast.id = 'mode-toast';
                toast.className = 'mode-toast';
                document.body.appendChild(toast);
            }}

            toast.textContent = message;
            toast.classList.add('visible');

            if (_toastTimeout) clearTimeout(_toastTimeout);
            _toastTimeout = setTimeout(() => {{
                toast.classList.remove('visible');
            }}, 1200);
        }}

        function getLinkEndpointId(link, side) {{
            const endpoint = link?.[side];
            if (endpoint && typeof endpoint === 'object') {{
                return endpoint.id || endpoint;
            }}
            return endpoint;
        }}

        function getFileTarget(fileIdx, totalFiles, radius, zSpacing) {{
            if (totalFiles <= 0) {{
                return {{ x: 0, y: 0, z: 0 }};
            }}
            const angle = (fileIdx / totalFiles) * Math.PI * 2;
            return {{
                x: Math.cos(angle) * radius,
                y: Math.sin(angle) * radius,
                z: IS_3D ? (fileIdx - totalFiles / 2) * zSpacing : 0
            }};
        }}

        function stableOffset(node, salt, radius) {{
            const angle = stableSeed(node, `${{salt}}:angle`) * Math.PI * 2;
            const spread = 0.3 + stableSeed(node, `${{salt}}:radius`) * 0.7;
            const zJitter = (stableSeed(node, `${{salt}}:z`) - 0.5) * radius * 0.6;
            const dist = radius * spread;
            return {{
                x: Math.cos(angle) * dist,
                y: Math.sin(angle) * dist,
                z: zJitter
            }};
        }}

        function buildFileGraph(data) {{
            const boundaries = data.file_boundaries || [];
            const totalFiles = boundaries.length;
            const fileNodes = [];
            const fileNodeIds = new Map();
            const nodeFileIdx = new Map();

            data.nodes.forEach(n => {{
                if (n && n.id) {{
                    nodeFileIdx.set(n.id, n.fileIdx ?? -1);
                }}
            }});

            boundaries.forEach((boundary, idx) => {{
                const label = boundary.file_name || boundary.file || `file-${{idx}}`;
                const atomCount = boundary.atom_count || 1;
                const nodeId = `file:${{idx}}`;
                fileNodeIds.set(idx, nodeId);
                fileNodes.push({{
                    id: nodeId,
                    name: label,
                    fileIdx: idx,
                    isFileNode: true,
                    val: Math.max(2, Math.sqrt(atomCount)),
                    color: getFileColor(idx, totalFiles, label),
                    file_path: boundary.file || '',
                    atom_count: atomCount
                }});
            }});

            const edgeMap = new Map();
            (data.links || []).forEach(link => {{
                const srcId = getLinkEndpointId(link, 'source');
                const tgtId = getLinkEndpointId(link, 'target');
                const srcIdx = nodeFileIdx.get(srcId) ?? -1;
                const tgtIdx = nodeFileIdx.get(tgtId) ?? -1;
                if (srcIdx < 0 || tgtIdx < 0 || srcIdx === tgtIdx) return;
                const key = `${{srcIdx}}->${{tgtIdx}}`;
                const existing = edgeMap.get(key) || {{
                    source: fileNodeIds.get(srcIdx),
                    target: fileNodeIds.get(tgtIdx),
                    weight: 0,
                    edge_type: 'file',
                    resolution: 'file'
                }};
                existing.weight += 1;
                edgeMap.set(key, existing);
            }});

            FILE_NODE_IDS = fileNodeIds;
            return {{
                nodes: fileNodes,
                links: Array.from(edgeMap.values())
            }};
        }}

        function captureFileNodePositions() {{
            FILE_NODE_POSITIONS = new Map();
            const nodes = (Graph && Graph.graphData().nodes) ? Graph.graphData().nodes : [];
            nodes.forEach(node => {{
                if (node && node.isFileNode && Number.isFinite(node.x) && Number.isFinite(node.y)) {{
                    FILE_NODE_POSITIONS.set(node.fileIdx, {{
                        x: node.x,
                        y: node.y,
                        z: Number.isFinite(node.z) ? node.z : 0
                    }});
                }}
            }});
        }}

        function buildHybridGraph(data) {{
            if (!FILE_GRAPH) {{
                FILE_GRAPH = buildFileGraph(data);
            }}
            const boundaries = data.file_boundaries || [];
            const totalFiles = boundaries.length;
            const clusterConfig = data.physics?.cluster || {{}};
            const detachRadius = (typeof clusterConfig.radius === 'number') ? clusterConfig.radius * 1.3 : 200;
            const detachZ = (typeof clusterConfig.zSpacing === 'number') ? clusterConfig.zSpacing * 2 : 80;
            const expandRadius = 30;
            const expandedSet = new Set(EXPANDED_FILES);

            const fileNodes = FILE_GRAPH.nodes.map(node => {{
                const copy = Object.assign({{}}, node);
                const anchor = FILE_NODE_POSITIONS.get(node.fileIdx) || getFileTarget(node.fileIdx, totalFiles, 140, 30);
                const detachOffset = (FILE_EXPAND_MODE === 'detach' && expandedSet.has(node.fileIdx))
                    ? getFileTarget(node.fileIdx, totalFiles, detachRadius, detachZ)
                    : {{ x: 0, y: 0, z: 0 }};
                copy.x = anchor.x + detachOffset.x;
                copy.y = anchor.y + detachOffset.y;
                copy.z = (anchor.z || 0) + detachOffset.z;
                return copy;
            }});

            const nodeFileIdx = new Map();
            data.nodes.forEach(n => {{
                if (n && n.id) {{
                    nodeFileIdx.set(n.id, n.fileIdx ?? -1);
                }}
            }});

            const childNodes = [];
            data.nodes.forEach(node => {{
                if (!expandedSet.has(node.fileIdx)) return;
                const anchor = FILE_NODE_POSITIONS.get(node.fileIdx) || getFileTarget(node.fileIdx, totalFiles, 140, 30);
                const detachOffset = (FILE_EXPAND_MODE === 'detach')
                    ? getFileTarget(node.fileIdx, totalFiles, detachRadius, detachZ)
                    : {{ x: 0, y: 0, z: 0 }};
                const local = stableOffset(node, `file-${{node.fileIdx}}`, expandRadius);
                const copy = Object.assign({{}}, node);
                copy.x = anchor.x + detachOffset.x + local.x;
                copy.y = anchor.y + detachOffset.y + local.y;
                copy.z = (anchor.z || 0) + detachOffset.z + (IS_3D ? local.z : 0);
                childNodes.push(copy);
            }});

            const childLinks = [];
            (data.links || []).forEach(link => {{
                const srcId = getLinkEndpointId(link, 'source');
                const tgtId = getLinkEndpointId(link, 'target');
                const srcIdx = nodeFileIdx.get(srcId) ?? -1;
                const tgtIdx = nodeFileIdx.get(tgtId) ?? -1;
                if (srcIdx < 0 || tgtIdx < 0 || srcIdx !== tgtIdx) return;
                if (!expandedSet.has(srcIdx)) return;
                childLinks.push({{
                    source: srcId,
                    target: tgtId,
                    color: link.color,
                    opacity: link.opacity,
                    edge_type: link.edge_type,
                    weight: link.weight,
                    confidence: link.confidence,
                    resolution: link.resolution
                }});
            }});

            return {{
                nodes: fileNodes.concat(childNodes),
                links: FILE_GRAPH.links.concat(childLinks)
            }};
        }}

        function setupControls(data) {{
            // =================================================================
            // TOKEN-DRIVEN: Controls config from payload
            // =================================================================
            const controlsConfig = data.controls || {{}};
            const sliders = controlsConfig.sliders || {{}};
            const densityConfig = sliders.density || {{}};

            // Add slider to DOM
            const hud = document.querySelector('.bottom-dock');

            // Density Control (TOKEN-DRIVEN values)
            const sliderLabel = densityConfig.label || 'DETAIL';
            const sliderMin = densityConfig.min || 1;
            const sliderMax = densityConfig.max || 10;
            const sliderStep = densityConfig.step || 0.5;
            const sliderDefault = densityConfig.default || 1;

            const sliderContainer = document.createElement('div');
            sliderContainer.style.display = 'flex';
            sliderContainer.style.flexDirection = 'column';
            sliderContainer.style.marginRight = '20px';
            sliderContainer.style.color = 'rgba(255,255,255,0.5)';
            sliderContainer.style.fontSize = '10px';

            sliderContainer.innerHTML = `
                <div style="margin-bottom:4px">${{sliderLabel}}</div>
                <input type="range" id="density-slider" min="${{sliderMin}}" max="${{sliderMax}}" step="${{sliderStep}}" value="${{sliderDefault}}" style="width:100px">
            `;

            hud.prepend(sliderContainer);

            const slider = document.getElementById('density-slider');
            slider.oninput = (e) => {{
                CURRENT_DENSITY = parseFloat(e.target.value);
                refreshGraph();
            }};

            // Store interactions config for later use
            window.CONTROLS_CONFIG = controlsConfig;

            setupSidebar(data);
            buildDatamapControls(data);

            // Initialize Smart Text Placement
            HudLayoutManager.init();
        }}

        function refreshGraph() {{
            if (!FULL_GRAPH || !Graph) return;

            // LAYOUT STABILITY: Save current positions before any graph update
            saveNodePositions();

            if (GRAPH_MODE === 'files') {{
                if (!FILE_GRAPH) {{
                    FILE_GRAPH = buildFileGraph(FULL_GRAPH);
                }}
                restoreNodePositions(FILE_GRAPH.nodes);
                Graph.graphData(FILE_GRAPH);
                applyFileColors(FILE_GRAPH.nodes);
                Graph.nodeVal(node => (node.val || 1) * APPEARANCE_STATE.nodeScale);
                Graph.nodeLabel('name');
                applyEdgeMode();
                updateDatamapControls();
                syncSelectionAfterGraphUpdate();
                if (LAYOUT_FROZEN) freezeLayout();
                return;
            }}

            if (GRAPH_MODE === 'hybrid') {{
                const hybrid = buildHybridGraph(FULL_GRAPH);
                restoreNodePositions(hybrid.nodes);
                Graph.graphData(hybrid);
                applyFileColors(hybrid.nodes);
                Graph.nodeVal(node => (node.val || 1) * APPEARANCE_STATE.nodeScale);
                Graph.nodeLabel(VIS_FILTERS.metadata.showLabels ? 'name' : '');
                applyEdgeMode();
                updateDatamapControls();
                syncSelectionAfterGraphUpdate();
                if (LAYOUT_FROZEN) freezeLayout();
                return;
            }}

            const subset = filterGraph(FULL_GRAPH, CURRENT_DENSITY, ACTIVE_DATAMAPS, VIS_FILTERS);
            if (ACTIVE_DATAMAPS.size > 0 && subset.nodes.length === 0) {{
                showToast('No nodes for that datamap selection.');
                ACTIVE_DATAMAPS.clear();
                const fallback = filterGraph(FULL_GRAPH, CURRENT_DENSITY, new Set(), VIS_FILTERS);
                restoreNodePositions(fallback.nodes);
                Graph.graphData(fallback);
                applyNodeColors(fallback.nodes);
                Graph.nodeVal(node => (node.val || 1) * APPEARANCE_STATE.nodeScale);
                Graph.nodeLabel(VIS_FILTERS.metadata.showLabels ? 'name' : '');
                applyEdgeMode();
                if (fileMode && GRAPH_MODE === 'atoms') {{
                    applyFileVizMode();
                }}
                updateDatamapControls();
                syncSelectionAfterGraphUpdate();
                if (LAYOUT_FROZEN) freezeLayout();
                return;
            }}
            applyNodeColors(subset.nodes);
            restoreNodePositions(subset.nodes);
            Graph.graphData(subset);
            Graph.nodeVal(node => (node.val || 1) * APPEARANCE_STATE.nodeScale);
            Graph.nodeLabel(VIS_FILTERS.metadata.showLabels ? 'name' : '');
            applyEdgeMode();
            if (fileMode && GRAPH_MODE === 'atoms') {{
                applyFileVizMode();
            }}
            updateDatamapControls();
            syncSelectionAfterGraphUpdate();
            if (LAYOUT_FROZEN) freezeLayout();
        }}

        function collectCounts(items, keyFn) {{
            const counts = new Map();
            items.forEach(item => {{
                const key = keyFn(item);
                if (!key) return;
                counts.set(key, (counts.get(key) || 0) + 1);
            }});
            return Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
        }}

        function resolveDefaults(defaults, available) {{
            if (!Array.isArray(defaults) || defaults.length === 0) {{
                return available;
            }}
            const availableSet = new Set(available);
            const intersection = defaults.filter(value => availableSet.has(value));
            return intersection.length ? intersection : available;
        }}

        function buildCheckboxRow(container, id, label, count, checked, onChange) {{
            const row = document.createElement('div');
            row.className = 'filter-item';
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.id = id;
            input.checked = checked;
            input.onchange = () => onChange(input.checked);
            const text = document.createElement('label');
            text.setAttribute('for', id);
            text.textContent = label;
            const countEl = document.createElement('span');
            countEl.className = 'filter-count';
            countEl.textContent = (typeof count === 'number') ? String(count) : '';
            row.appendChild(input);
            row.appendChild(text);
            if (countEl.textContent) {{
                row.appendChild(countEl);
            }}
            container.appendChild(row);
            return input;
        }}

        function buildFilterGroup(containerId, items, stateSet, onUpdate) {{
            const container = document.getElementById(containerId);
            if (!container) return;
            container.innerHTML = '';

            const allId = `${{containerId}}-all`;
            let allCheckbox = null;

            allCheckbox = buildCheckboxRow(container, allId, 'ALL', null, true, (checked) => {{
                stateSet.clear();
                if (checked) {{
                    items.forEach(([value]) => stateSet.add(value));
                }}
                container.querySelectorAll('input[type="checkbox"]').forEach(box => {{
                    if (box.id !== allId) box.checked = checked;
                }});
                onUpdate();
            }});

            items.forEach(([value, count], index) => {{
                const id = `${{containerId}}-${{index}}`;
                const checked = stateSet.has(value);
                buildCheckboxRow(container, id, value, count, checked, (isChecked) => {{
                    if (isChecked) {{
                        stateSet.add(value);
                    }} else {{
                        stateSet.delete(value);
                    }}
                    const allChecked = items.every(([v]) => stateSet.has(v));
                    allCheckbox.checked = allChecked;
                    onUpdate();
                }});
            }});
        }}

        function normalizeDatamapConfig(raw) {{
            if (!raw || typeof raw !== 'object') return null;
            const id = String(raw.id || raw.key || raw.label || '').trim();
            if (!id) return null;
            const normalizeList = (value) => {{
                if (!Array.isArray(value)) return [];
                return value.map(item => String(item).toUpperCase());
            }};
            // Normalize tier list with aliases (CORE→T0, ARCH→T1, EXT→T2)
            const normalizeTierList = (value) => {{
                if (!Array.isArray(value)) return [];
                return value.map(item => normalizeTier(item));
            }};
            const match = raw.match || {{}};
            return {{
                id: id.toUpperCase(),
                label: String(raw.label || raw.id || id).toUpperCase(),
                match: {{
                    atom_families: normalizeList(match.atom_families),  // NEW: canonical atom family
                    atom_prefixes: normalizeList(match.atom_prefixes),  // backward compat
                    tiers: normalizeTierList(match.tiers),  // applies aliases
                    rings: normalizeList(match.rings),
                    roles: normalizeList(match.roles)
                }},
                default: Boolean(raw.default)
            }};
        }}

        function resolveDatamapConfigs(controlsConfig) {{
            const fromTokens = Array.isArray(controlsConfig.datamaps) ? controlsConfig.datamaps : [];
            const normalized = fromTokens
                .map(normalizeDatamapConfig)
                .filter(Boolean);
            if (normalized.length) return normalized;

            const fallback = controlsConfig.buttons?.datamaps || {{}};
            return Object.entries(fallback).map(([label, config]) => {{
                const prefix = config.filter || null;
                return normalizeDatamapConfig({{
                    id: label.toUpperCase(),
                    label: label.toUpperCase(),
                    match: prefix ? {{ atom_prefixes: [prefix] }} : {{}},
                    default: false
                }});
            }}).filter(Boolean);
        }}

        function datamapMatches(node, config) {{
            const match = config.match || {{}};
            const atomId = String(node.atom || '');
            const atomFamily = getNodeAtomFamily(node);  // canonical or inferred
            const tier = getNodeTier(node);  // canonical or inferred (with aliases)
            const ring = getNodeRing(node);
            const role = String(node.role || 'Unknown').toUpperCase();

            // NEW: atom_families matching (canonical field)
            if (Array.isArray(match.atom_families) && match.atom_families.length) {{
                if (!match.atom_families.includes(atomFamily)) return false;
            }}

            // Backward compat: atom_prefixes matches atom_family OR atom prefix
            if (Array.isArray(match.atom_prefixes) && match.atom_prefixes.length) {{
                const matchesFamily = match.atom_prefixes.includes(atomFamily);
                const matchesPrefix = match.atom_prefixes.some(prefix => atomId.startsWith(prefix));
                if (!matchesFamily && !matchesPrefix) return false;
            }}

            // Tier matching (aliases already normalized in config)
            if (Array.isArray(match.tiers) && match.tiers.length) {{
                if (!match.tiers.includes(tier)) return false;
            }}

            if (Array.isArray(match.rings) && match.rings.length) {{
                if (!match.rings.includes(ring)) return false;
            }}

            if (Array.isArray(match.roles) && match.roles.length) {{
                if (!match.roles.includes(role)) return false;
            }}
            return true;
        }}

        function buildDatamapToggle(container, id, label, checked, count, onChange) {{
            const wrapper = document.createElement('label');
            wrapper.className = 'datamap-toggle';
            wrapper.setAttribute('data-id', id);

            const input = document.createElement('input');
            input.type = 'checkbox';
            input.checked = checked;
            input.onchange = () => onChange(input.checked);

            const text = document.createElement('span');
            text.textContent = label;

            const countEl = document.createElement('span');
            countEl.className = 'datamap-count';
            countEl.textContent = (typeof count === 'number') ? String(count) : '';

            wrapper.appendChild(input);
            wrapper.appendChild(text);
            wrapper.appendChild(countEl);
            container.appendChild(wrapper);

            return {{ wrapper, input, count: countEl }};
        }}

        function buildDatamapControls(data) {{
            const controlsConfig = data.controls || {{}};
            const container = document.getElementById('datamap-controls');
            if (!container) return;
            container.innerHTML = '';
            DATAMAP_UI = new Map();

            DATAMAP_CONFIGS = resolveDatamapConfigs(controlsConfig);
            DATAMAP_INDEX = DATAMAP_CONFIGS.reduce((acc, cfg) => {{
                acc[cfg.id] = cfg;
                return acc;
            }}, {{}});

            if (ACTIVE_DATAMAPS.size === 0) {{
                DATAMAP_CONFIGS.forEach(cfg => {{
                    if (cfg.default) ACTIVE_DATAMAPS.add(cfg.id);
                }});
            }}

            const allUI = buildDatamapToggle(
                container,
                '__ALL__',
                'ALL',
                ACTIVE_DATAMAPS.size === 0,
                null,
                (checked) => {{
                    if (checked) {{
                        ACTIVE_DATAMAPS.clear();
                        refreshGraph();
                    }}
                }}
            );
            DATAMAP_UI.set('__ALL__', allUI);

            DATAMAP_CONFIGS.forEach(cfg => {{
                const ui = buildDatamapToggle(
                    container,
                    cfg.id,
                    cfg.label,
                    ACTIVE_DATAMAPS.has(cfg.id),
                    null,
                    () => {{
                        setDatamap(cfg.id);
                    }}
                );
                DATAMAP_UI.set(cfg.id, ui);
            }});

            updateDatamapControls();
        }}

        function buildExclusiveOptions(containerId, options, activeValue, onSelect) {{
            const container = document.getElementById(containerId);
            if (!container) return;
            container.innerHTML = '';

            const inputs = [];
            options.forEach((option, index) => {{
                const id = `${{containerId}}-${{index}}`;
                const input = buildCheckboxRow(
                    container,
                    id,
                    option.label,
                    null,
                    option.value === activeValue,
                    (checked) => {{
                        if (!checked) {{
                            input.checked = true;
                            return;
                        }}
                        inputs.forEach(other => {{
                            if (other !== input) other.checked = false;
                        }});
                        onSelect(option.value);
                    }}
                );
                inputs.push(input);
            }});
        }}

        function buildMetadataControls(containerId, metadata) {{
            const container = document.getElementById(containerId);
            if (!container) return;
            container.innerHTML = '';

            const toggles = [
                {{ id: 'meta-labels', label: 'LABELS', key: 'showLabels' }},
                {{ id: 'meta-file-panel', label: 'FILE PANEL', key: 'showFilePanel' }},
                {{ id: 'meta-report', label: 'REPORT', key: 'showReportPanel' }},
                {{ id: 'meta-edges', label: 'EDGES', key: 'showEdges' }}
            ];

            toggles.forEach((toggle) => {{
                buildCheckboxRow(container, toggle.id, toggle.label, null, metadata[toggle.key], (checked) => {{
                    metadata[toggle.key] = checked;
                    applyMetadataVisibility();
                    refreshGraph();
                }});
            }});
        }}

        function buildAppearanceSliders(containerId, sliderConfigs) {{
            const container = document.getElementById(containerId);
            if (!container) return;
            container.innerHTML = '';

            const resolveSlider = (key, fallback) => {{
                const config = (sliderConfigs && sliderConfigs[key]) ? sliderConfigs[key] : {{}};
                return {{
                    label: config.label || fallback.label,
                    min: (config.min !== undefined) ? config.min : fallback.min,
                    max: (config.max !== undefined) ? config.max : fallback.max,
                    step: (config.step !== undefined) ? config.step : fallback.step,
                    default: (config.default !== undefined) ? config.default : fallback.value
                }};
            }};

            const sliderDefs = [
                (() => {{
                    const config = resolveSlider('edgeOpacity', {{
                        label: 'EDGE OPACITY',
                        min: 0.02,
                        max: 0.4,
                        step: 0.01,
                        value: EDGE_DEFAULT_OPACITY
                    }});
                    return {{
                        id: 'edge-opacity',
                        label: config.label,
                        min: config.min,
                        max: config.max,
                        step: config.step,
                        value: APPEARANCE_STATE.edgeOpacity ?? config.default,
                        onChange: (val) => {{
                            APPEARANCE_STATE.edgeOpacity = val;
                            applyEdgeMode();
                        }}
                    }};
                }})(),
                (() => {{
                    const config = resolveSlider('nodeScale', {{
                        label: 'NODE SCALE',
                        min: 0.6,
                        max: 2.5,
                        step: 0.1,
                        value: 1
                    }});
                    return {{
                        id: 'node-scale',
                        label: config.label,
                        min: config.min,
                        max: config.max,
                        step: config.step,
                        value: APPEARANCE_STATE.nodeScale ?? config.default,
                        onChange: (val) => {{
                            APPEARANCE_STATE.nodeScale = val;
                            refreshGraph();
                        }}
                    }};
                }})(),
                (() => {{
                    const config = resolveSlider('backgroundBrightness', {{
                        label: 'BACKGROUND',
                        min: 0,
                        max: 1,
                        step: 0.05,
                        value: 1
                    }});
                    return {{
                        id: 'bg-brightness',
                        label: config.label,
                        min: config.min,
                        max: config.max,
                        step: config.step,
                        value: APPEARANCE_STATE.backgroundBrightness ?? config.default,
                        onChange: (val) => {{
                            APPEARANCE_STATE.backgroundBrightness = val;
                            updateBackgroundBrightness();
                        }}
                    }};
                }})(),
                (() => {{
                    const config = resolveSlider('fileLightness', {{
                        label: 'FILE LIGHT',
                        min: 20,
                        max: 80,
                        step: 1,
                        value: 50
                    }});
                    return {{
                        id: 'file-lightness',
                        label: config.label,
                        min: config.min,
                        max: config.max,
                        step: config.step,
                        value: APPEARANCE_STATE.fileLightness ?? config.default,
                        onChange: (val) => {{
                            FILE_COLOR_CONFIG.lightness = val;
                            APPEARANCE_STATE.fileLightness = val;
                            if (fileMode) {{
                                applyFileVizMode();
                            }}
                        }}
                    }};
                }})(),
                (() => {{
                    const config = resolveSlider('hueShift', {{
                        label: 'HUE SHIFT',
                        min: -180,
                        max: 180,
                        step: 1,
                        value: 0
                    }});
                    return {{
                        id: 'hue-shift',
                        label: config.label,
                        min: config.min,
                        max: config.max,
                        step: config.step,
                        value: COLOR_TWEAKS.hueShift ?? config.default,
                        onChange: (val) => {{
                            COLOR_TWEAKS.hueShift = val;
                            refreshGraph();
                        }}
                    }};
                }})(),
                (() => {{
                    const config = resolveSlider('chromaScale', {{
                        label: 'CHROMA SCALE',
                        min: 0,
                        max: 2,
                        step: 0.05,
                        value: 1
                    }});
                    return {{
                        id: 'chroma-scale',
                        label: config.label,
                        min: config.min,
                        max: config.max,
                        step: config.step,
                        value: COLOR_TWEAKS.chromaScale ?? config.default,
                        onChange: (val) => {{
                            COLOR_TWEAKS.chromaScale = val;
                            refreshGraph();
                        }}
                    }};
                }})(),
                (() => {{
                    const config = resolveSlider('lightnessShift', {{
                        label: 'LIGHT SHIFT',
                        min: -20,
                        max: 20,
                        step: 1,
                        value: 0
                    }});
                    return {{
                        id: 'lightness-shift',
                        label: config.label,
                        min: config.min,
                        max: config.max,
                        step: config.step,
                        value: COLOR_TWEAKS.lightnessShift ?? config.default,
                        onChange: (val) => {{
                            COLOR_TWEAKS.lightnessShift = val;
                            refreshGraph();
                        }}
                    }};
                }})(),
                (() => {{
                    const config = resolveSlider('boundaryOpacity', {{
                        label: 'HULL OPACITY',
                        min: 0.02,
                        max: 0.25,
                        step: 0.01,
                        value: 0.1
                    }});
                    return {{
                        id: 'boundary-fill',
                        label: config.label,
                        min: config.min,
                        max: config.max,
                        step: config.step,
                        value: APPEARANCE_STATE.boundaryFill ?? config.default,
                        onChange: (val) => {{
                            APPEARANCE_STATE.boundaryFill = val;
                            if (fileMode && fileVizMode === 'hulls') {{
                                drawFileBoundaries(FULL_GRAPH);
                            }}
                        }}
                    }};
                }})(),
                (() => {{
                    const config = resolveSlider('hullWireOpacity', {{
                        label: 'HULL WIRE',
                        min: 0.05,
                        max: 0.6,
                        step: 0.02,
                        value: 0.35
                    }});
                    return {{
                        id: 'boundary-wire',
                        label: config.label,
                        min: config.min,
                        max: config.max,
                        step: config.step,
                        value: APPEARANCE_STATE.boundaryWire ?? config.default,
                        onChange: (val) => {{
                            APPEARANCE_STATE.boundaryWire = val;
                            if (fileMode && fileVizMode === 'hulls') {{
                                drawFileBoundaries(FULL_GRAPH);
                            }}
                        }}
                    }};
                }})(),
                (() => {{
                    const config = resolveSlider('clusterStrength', {{
                        label: 'CLUSTER FORCE',
                        min: 0,
                        max: 1,
                        step: 0.1,
                        value: 0.45
                    }});
                    return {{
                        id: 'cluster-strength',
                        label: config.label,
                        min: config.min,
                        max: config.max,
                        step: config.step,
                        value: APPEARANCE_STATE.clusterStrength ?? config.default,
                        onChange: (val) => {{
                            APPEARANCE_STATE.clusterStrength = val;
                            if (fileMode && fileVizMode === 'cluster') {{
                                applyClusterForce(FULL_GRAPH);
                            }}
                        }}
                    }};
                }})()
            ];

            sliderDefs.forEach(def => {{
                const wrapper = document.createElement('div');
                wrapper.className = 'filter-slider';
                const label = document.createElement('label');
                label.textContent = def.label;
                const input = document.createElement('input');
                input.type = 'range';
                input.id = def.id;
                input.min = def.min;
                input.max = def.max;
                input.step = def.step;
                input.value = def.value;
                input.oninput = () => {{
                    def.onChange(parseFloat(input.value));
                }};
                wrapper.appendChild(label);
                wrapper.appendChild(input);
                container.appendChild(wrapper);
            }});
        }}

        function updateBackgroundBrightness() {{
            if (!Graph || !APPEARANCE_STATE.backgroundBase) return;
            const baseColor = new THREE.Color(APPEARANCE_STATE.backgroundBase);
            const brightness = APPEARANCE_STATE.backgroundBrightness ?? 1;
            const adjusted = baseColor.clone().multiplyScalar(brightness);
            Graph.backgroundColor(`#${{adjusted.getHexString()}}`);
        }}

        function applyMetadataVisibility() {{
            const reportPanel = document.getElementById('report-panel');
            const reportButton = document.getElementById('btn-report');
            const filePanel = document.getElementById('file-panel');
            if (!VIS_FILTERS.metadata.showReportPanel) {{
                reportPanel.style.display = 'none';
                reportButton.classList.remove('active');
                reportButton.style.display = 'none';
            }} else {{
                reportButton.style.display = 'inline-flex';
            }}
            if (!VIS_FILTERS.metadata.showFilePanel && filePanel) {{
                filePanel.classList.remove('visible');
            }}
        }}

        function setupSidebar(data) {{
            const controlsConfig = data.controls || {{}};
            const sidebarConfig = controlsConfig.sidebar || {{}};
            const filtersConfig = controlsConfig.filters || {{}};
            const sliderConfig = controlsConfig.sliders || {{}};
            const sideDock = document.getElementById('side-dock');

            if (!sideDock || sidebarConfig.visible === false) {{
                if (sideDock) sideDock.style.display = 'none';
                return;
            }}

            if (typeof sidebarConfig.width === 'number') {{
                sideDock.style.setProperty('--side-width', `${{sidebarConfig.width}}px`);
            }}

            const startOpen = sidebarConfig.collapsed === false;
            sideDock.classList.toggle('expanded', startOpen);
            SIDEBAR_STATE.open = startOpen;

            const toggle = document.getElementById('side-dock-toggle');
            if (toggle) {{
                toggle.onclick = () => {{
                    SIDEBAR_STATE.open = !SIDEBAR_STATE.open;
                    sideDock.classList.toggle('expanded', SIDEBAR_STATE.open);
                }};
            }}

            // Lock button: toggles locked state (sidebar stays open on mouse leave)
            const lockBtn = document.getElementById('side-dock-lock');
            if (lockBtn) {{
                lockBtn.onclick = (e) => {{
                    e.stopPropagation();
                    SIDEBAR_STATE.locked = !SIDEBAR_STATE.locked;
                    sideDock.classList.toggle('locked', SIDEBAR_STATE.locked);
                    lockBtn.textContent = SIDEBAR_STATE.locked ? '🔒' : '🔓';
                    lockBtn.title = SIDEBAR_STATE.locked ? 'Unlock sidebar' : 'Lock sidebar open';
                    // Trigger smart text placement reflow
                    HudLayoutManager.reflow();
                }};
            }}

            const tierCounts = collectCounts(data.nodes, n => getNodeTier(n));
            const ringCounts = collectCounts(data.nodes, n => getNodeRing(n));
            const roleCounts = collectCounts(data.nodes, n => String(n.role || 'Unknown'));
            const edgeCounts = collectCounts(data.links, l => String(l.edge_type || l.type || 'default'));

            const tierDefaults = Array.isArray(filtersConfig.tiers) ? filtersConfig.tiers : [];
            const ringDefaults = Array.isArray(filtersConfig.rings) ? filtersConfig.rings : [];
            const edgeDefaults = Array.isArray(filtersConfig.edges) ? filtersConfig.edges : [];

            const tierKeys = tierCounts.map(([key]) => key);
            const ringKeys = ringCounts.map(([key]) => key);
            const edgeKeys = edgeCounts.map(([key]) => key);

            VIS_FILTERS.tiers = new Set(resolveDefaults(tierDefaults, tierKeys));
            VIS_FILTERS.rings = new Set(resolveDefaults(ringDefaults, ringKeys));
            VIS_FILTERS.roles = new Set(roleCounts.map(([key]) => key));
            VIS_FILTERS.edges = new Set(resolveDefaults(edgeDefaults, edgeKeys));

            const metadataConfig = filtersConfig.metadata || {{}};
            VIS_FILTERS.metadata.showLabels = metadataConfig.showLabels !== false;
            VIS_FILTERS.metadata.showFilePanel = metadataConfig.showFilePanel !== false;
            VIS_FILTERS.metadata.showReportPanel = metadataConfig.showReportPanel !== false;
            VIS_FILTERS.metadata.showEdges = metadataConfig.showEdges !== false;

            const sliderDefault = (key, fallback) => {{
                const entry = sliderConfig[key] || {{}};
                return (entry.default !== undefined) ? entry.default : fallback;
            }};

            if (APPEARANCE_STATE.edgeOpacity === null) {{
                APPEARANCE_STATE.edgeOpacity = sliderDefault('edgeOpacity', EDGE_DEFAULT_OPACITY);
            }}
        if (APPEARANCE_STATE.boundaryFill === null) {{
            APPEARANCE_STATE.boundaryFill = sliderDefault('boundaryOpacity', 0.1);
        }}
        if (APPEARANCE_STATE.boundaryWire === null) {{
            APPEARANCE_STATE.boundaryWire = sliderDefault('hullWireOpacity', 0.35);
        }}
        if (APPEARANCE_STATE.clusterStrength === null) {{
            APPEARANCE_STATE.clusterStrength = sliderDefault('clusterStrength', 0.45);
        }}
            APPEARANCE_STATE.nodeScale = sliderDefault('nodeScale', APPEARANCE_STATE.nodeScale || 1);
            APPEARANCE_STATE.backgroundBrightness = sliderDefault(
                'backgroundBrightness',
                APPEARANCE_STATE.backgroundBrightness || 1
            );
            APPEARANCE_STATE.fileLightness = sliderDefault(
                'fileLightness',
                APPEARANCE_STATE.fileLightness ?? FILE_COLOR_CONFIG.lightness ?? 50
            );
            COLOR_TWEAKS.hueShift = sliderDefault('hueShift', COLOR_TWEAKS.hueShift || 0);
            COLOR_TWEAKS.chromaScale = sliderDefault('chromaScale', COLOR_TWEAKS.chromaScale || 1);
            COLOR_TWEAKS.lightnessShift = sliderDefault('lightnessShift', COLOR_TWEAKS.lightnessShift || 0);

            buildFilterGroup('filter-tiers', tierCounts, VIS_FILTERS.tiers, refreshGraph);
            buildFilterGroup('filter-rings', ringCounts, VIS_FILTERS.rings, refreshGraph);
            buildFilterGroup('filter-roles', roleCounts, VIS_FILTERS.roles, refreshGraph);
            buildFilterGroup('filter-edges', edgeCounts, VIS_FILTERS.edges, refreshGraph);
            buildExclusiveOptions('filter-node-color', [
                {{ label: 'TIER', value: 'tier' }},
                {{ label: 'RING', value: 'ring' }},
                {{ label: 'FAMILY', value: 'family' }},
                {{ label: 'FILE', value: 'file' }}
            ], NODE_COLOR_MODE, setNodeColorMode);
            buildExclusiveOptions('filter-edge-mode', [
                {{ label: 'TYPE', value: 'type' }},
                {{ label: 'RESOLUTION', value: 'resolution' }},
                {{ label: 'WEIGHT', value: 'weight' }},
                {{ label: 'CONFIDENCE', value: 'confidence' }},
                {{ label: 'MONO', value: 'mono' }}
            ], EDGE_MODE, setEdgeMode);
            buildMetadataControls('filter-metadata', VIS_FILTERS.metadata);
            buildAppearanceSliders('appearance-sliders', controlsConfig.sliders || {{}});

            applyMetadataVisibility();
            updateBackgroundBrightness();
            refreshGraph();
        }}

        function setupReport(data) {{
            const panel = document.getElementById('report-panel');
            const content = document.getElementById('report-content');
            const report = (data && data.brain_download) ? data.brain_download : '';
            content.textContent = report || 'No report available.';
        }}

        function setupMetrics(data) {{
            const kpis = (data && data.kpis) ? data.kpis : {{}};
            const setText = (id, value) => {{
                const el = document.getElementById(id);
                if (!el) return;
                el.textContent = value;
            }};
            const asNumber = (val) => {{
                const num = Number(val);
                return Number.isFinite(num) ? num : null;
            }};
            const formatPercent = (val) => {{
                const num = asNumber(val);
                return num === null ? '--' : `${{num.toFixed(1)}}%`;
            }};
            const formatCount = (val) => {{
                const num = asNumber(val);
                return num === null ? '--' : `${{Math.round(num)}}`;
            }};
            const formatScore = (val) => {{
                const num = asNumber(val);
                return num === null ? '--' : `${{num.toFixed(1)}}/10`;
            }};

            setText('metric-edge-resolution', formatPercent(kpis.edge_resolution_percent));
            setText('metric-call-ratio', formatPercent(kpis.call_ratio_percent));
            setText('metric-reachability', formatPercent(kpis.reachability_percent));
            setText('metric-dead-code', formatPercent(kpis.dead_code_percent));
            setText('metric-knot-score', formatScore(kpis.knot_score));
            setText('metric-topology', kpis.topology_shape || 'UNKNOWN');
            setText('metric-orphans', formatCount(kpis.orphan_count));
            setText('metric-top-hubs', formatCount(kpis.top_hub_count));
        }}

        function setupHudFade() {{
            const idleDelay = 2200;
            let timer = null;
            const activate = () => {{
                document.body.classList.remove('hud-quiet');
                if (timer) {{
                    clearTimeout(timer);
                }}
                timer = setTimeout(() => {{
                    document.body.classList.add('hud-quiet');
                }}, idleDelay);
            }};
            ['mousemove', 'mousedown', 'keydown', 'touchstart'].forEach((evt) => {{
                window.addEventListener(evt, activate, {{ passive: true }});
            }});
            activate();
        }}

        function showToast(message) {{
            const toast = document.getElementById('hud-toast');
            if (!toast) return;
            toast.textContent = message;
            toast.classList.add('visible');
            clearTimeout(toast._timer);
            toast._timer = setTimeout(() => {{
                toast.classList.remove('visible');
            }}, 2200);
        }}

        function updateDatamapControls() {{
            if (!FULL_GRAPH) return;
            const datamapEnabled = GRAPH_MODE === 'atoms';
            const base = filterGraph(FULL_GRAPH, CURRENT_DENSITY, new Set(), VIS_FILTERS);
            const nodes = base.nodes || [];
            const totalCount = nodes.length;

            const allUI = DATAMAP_UI.get('__ALL__');
            if (allUI) {{
                allUI.input.checked = ACTIVE_DATAMAPS.size === 0;
                if (allUI.count) {{
                    allUI.count.textContent = datamapEnabled ? String(totalCount) : '--';
                }}
                allUI.input.disabled = !datamapEnabled;
                allUI.wrapper.classList.toggle('disabled', !datamapEnabled);
                allUI.wrapper.classList.toggle('active', datamapEnabled && ACTIVE_DATAMAPS.size === 0);
            }}

            DATAMAP_CONFIGS.forEach((config) => {{
                const count = nodes.reduce((acc, node) => acc + (datamapMatches(node, config) ? 1 : 0), 0);
                const ui = DATAMAP_UI.get(config.id);
                if (!ui) return;
                if (ui.count) {{
                    ui.count.textContent = datamapEnabled ? String(count) : '--';
                }}
                ui.input.disabled = !datamapEnabled || count === 0;
                ui.wrapper.classList.toggle('disabled', !datamapEnabled || count === 0);
                ui.input.checked = ACTIVE_DATAMAPS.has(config.id);
                ui.wrapper.classList.toggle('active', datamapEnabled && ACTIVE_DATAMAPS.has(config.id));
            }});
        }}

        function setupDimensionToggle() {{
            const button = document.getElementById('btn-dimensions');
            const updateLabel = () => {{
                button.textContent = IS_3D ? '2D' : '3D';
            }};
            updateLabel();
            button.onclick = () => {{
                if (DIMENSION_TRANSITION) return;
                DIMENSION_TRANSITION = true;
                const target3d = !IS_3D;
                animateDimensionChange(target3d, () => {{
                    IS_3D = target3d;
                    DIMENSION_TRANSITION = false;
                    updateLabel();
                    if (fileMode && GRAPH_MODE === 'atoms') {{
                        applyFileVizMode();
                    }}
                }});
            }};
        }}

        function stableSeed(node, salt) {{
            const id = String(node.id || node.name || '');
            const combined = `${{id}}|${{salt}}`;
            let hash = 0;
            for (let i = 0; i < combined.length; i++) {{
                hash = ((hash << 5) - hash + combined.charCodeAt(i)) | 0;
            }}
            return ((hash >>> 0) % 1000) / 1000;
        }}

        function stableZ(node) {{
            const normalized = stableSeed(node, 'z');
            return (normalized - 0.5) * 60;
        }}

        function animateDimensionChange(target3d, done) {{
            const nodes = (Graph && Graph.graphData().nodes) ? Graph.graphData().nodes : [];
            const startTime = performance.now();
            const duration = 3000;
            const delayMin = 0;
            const delayMax = 2000;
            const lockPositionsAfterTransition = true;
            const easeInOutSine = (t) => 0.5 - 0.5 * Math.cos(Math.PI * t);
            const starStart = STARFIELD ? STARFIELD.material.opacity : 0;
            const starTarget = target3d ? STARFIELD_OPACITY : 0;
            const bloomStart = BLOOM_PASS ? BLOOM_PASS.strength : 0;
            const bloomTarget = BLOOM_PASS ? (target3d ? BLOOM_STRENGTH : 0) : 0;
            const previousVelocityDecay = (Graph && Graph.d3VelocityDecay) ? Graph.d3VelocityDecay() : null;
            const previousAlphaTarget = (Graph && Graph.d3AlphaTarget) ? Graph.d3AlphaTarget() : null;
            const previousCooldownTicks = (Graph && Graph.cooldownTicks) ? Graph.cooldownTicks() : null;
            const previousCooldownTime = (Graph && Graph.cooldownTime) ? Graph.cooldownTime() : null;
            if (Graph && Graph.cooldownTicks) {{
                Graph.cooldownTicks(Infinity);
            }}
            if (Graph && Graph.cooldownTime) {{
                Graph.cooldownTime(Infinity);
            }}
            if (Graph && Graph.d3VelocityDecay) {{
                Graph.d3VelocityDecay(1);
            }}
            if (Graph && Graph.d3AlphaTarget) {{
                Graph.d3AlphaTarget(0);
            }}
            if (Graph && Graph.d3ReheatSimulation) {{
                Graph.d3ReheatSimulation();
            }}

            nodes.forEach((node) => {{
                node.__xStart = node.x || 0;
                node.__yStart = node.y || 0;
                node.__zStart = node.z || 0;
                node.__delay = delayMin + (stableSeed(node, 'delay') * (delayMax - delayMin));
                node.fx = node.__xStart;
                node.fy = node.__yStart;
                node.vx = 0;
                node.vy = 0;
                node.vz = 0;
                if (target3d) {{
                    if (node.__z3d === undefined || node.__z3d === null) {{
                        node.__z3d = node.__zStart || stableZ(node);
                    }}
                }} else {{
                    node.__z3d = node.__zStart;
                }}
            }});

            const maxDistance = nodes.reduce((acc, node) => Math.max(acc, Math.abs(node.__zStart || 0)), 1);

            Graph.numDimensions(3);

            const animate = (now) => {{
                const elapsed = now - startTime;
                const t = Math.min(1, elapsed / duration);
                const eased = easeInOutSine(t);

                nodes.forEach((node) => {{
                    const startZ = node.__zStart || 0;
                    const targetZ = target3d ? (node.__z3d || 0) : 0;
                    const delay = node.__delay || 0;
                    const localDuration = Math.max(600, duration - delay);
                    const localElapsed = Math.max(0, elapsed - delay);
                    const localT = Math.min(1, localElapsed / localDuration);
                    const localEase = easeInOutSine(localT);
                    const distanceRatio = maxDistance > 0 ? Math.abs(startZ) / maxDistance : 0;
                    const distanceCurve = 0.6 + (1 - distanceRatio) * 0.6;
                    const progress = Math.pow(localEase, distanceCurve);
                    const nextZ = startZ + (targetZ - startZ) * progress;
                    node.z = nextZ;
                    node.fz = nextZ;
                    node.vz = 0;
                }});

                if (STARFIELD) {{
                    const nextOpacity = starStart + (starTarget - starStart) * eased;
                    STARFIELD.material.opacity = nextOpacity;
                    STARFIELD.visible = nextOpacity > 0.02;
                }}
                if (BLOOM_PASS) {{
                    BLOOM_PASS.strength = bloomStart + (bloomTarget - bloomStart) * eased;
                }}

                if (t < 1) {{
                    requestAnimationFrame(animate);
                }} else {{
                    nodes.forEach((node) => {{
                        delete node.fz;
                        delete node.__zStart;
                        delete node.__xStart;
                        delete node.__yStart;
                        delete node.__delay;
                        if (!target3d) {{
                            node.z = 0;
                            node.fz = 0;
                        }} else if (lockPositionsAfterTransition) {{
                            node.z = node.__z3d || node.z || 0;
                            node.fz = node.z;
                        }} else {{
                            delete node.fx;
                            delete node.fy;
                        }}
                    }});
                    Graph.numDimensions(target3d ? 3 : 2);
                    if (!target3d && STARFIELD) {{
                        STARFIELD.visible = false;
                    }}
                    if (Graph && Graph.d3VelocityDecay && previousVelocityDecay !== null) {{
                        Graph.d3VelocityDecay(previousVelocityDecay);
                    }}
                    if (Graph && Graph.d3AlphaTarget && previousAlphaTarget !== null) {{
                        Graph.d3AlphaTarget(previousAlphaTarget);
                    }}
                    if (Graph && Graph.cooldownTicks && previousCooldownTicks !== null) {{
                        Graph.cooldownTicks(previousCooldownTicks);
                    }}
                    if (Graph && Graph.cooldownTime && previousCooldownTime !== null) {{
                        Graph.cooldownTime(previousCooldownTime);
                    }}
                    if (done) done();
                }}
            }};

            requestAnimationFrame(animate);
        }}

        // ====================================================================
        // EDGE VISUALIZATION MODES
        // ====================================================================
        const EDGE_MODE_ORDER = ['type', 'resolution', 'weight', 'confidence', 'mono'];
        const EDGE_MODE_LABELS = {{
            type: 'EDGE: TYPE',
            resolution: 'EDGE: RES',
            weight: 'EDGE: WEIGHT',
            confidence: 'EDGE: CONF',
            mono: 'EDGE: MONO'
        }};
        const EDGE_MODE_HINTS = {{
            type: 'Edge color by type (calls, imports, etc.)',
            resolution: 'Edge color by resolution (0-1, resolved vs unresolved)',
            weight: 'Edge width by weight (call frequency)',
            confidence: 'Edge opacity by confidence (0-1)',
            mono: 'Monochrome edges (no color encoding)'
        }};

        function clamp01(value) {{
            return Math.max(0, Math.min(1, value));
        }}

        function clampValue(value, min, max) {{
            return Math.max(min, Math.min(max, value));
        }}

        function hslColor(hue, saturation, lightness) {{
            return `hsl(${{hue}}, ${{saturation}}%, ${{lightness}}%)`;
        }}

        function parseOklchString(value) {{
            if (typeof value !== 'string') return null;
            const match = value.trim().match(/^oklch\\(\\s*([\\d.]+)%\\s+([\\d.]+)\\s+([\\d.]+)(?:\\s*\\/\\s*([\\d.]+))?\\s*\\)$/i);
            if (!match) return null;
            return {{
                L: parseFloat(match[1]),
                C: parseFloat(match[2]),
                H: parseFloat(match[3]),
                A: match[4] !== undefined ? parseFloat(match[4]) : 1
            }};
        }}

        function applyColorTweaks(lightness, chroma, hue, alpha = 1) {{
            const L = clampValue(lightness + (COLOR_TWEAKS.lightnessShift || 0), 0, 100);
            const C = clampValue(chroma * (COLOR_TWEAKS.chromaScale || 1), 0, 0.4);
            const H = (hue + (COLOR_TWEAKS.hueShift || 0) + 360) % 360;
            return [L, C, H, alpha];
        }}

        function oklchToSrgb(L, C, H) {{
            const hRad = (H * Math.PI) / 180;
            const a = C * Math.cos(hRad);
            const b = C * Math.sin(hRad);

            const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
            const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
            const s_ = L - 0.0894841775 * a - 1.2914855480 * b;

            const l = l_ ** 3;
            const m = m_ ** 3;
            const s = s_ ** 3;

            let r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s;
            let g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s;
            let bChan = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s;

            const linearToSrgb = (channel) => {{
                if (channel <= 0.0031308) {{
                    return 12.92 * channel;
                }}
                return 1.055 * Math.pow(channel, 1 / 2.4) - 0.055;
            }};

            r = linearToSrgb(r);
            g = linearToSrgb(g);
            bChan = linearToSrgb(bChan);

            if (![r, g, bChan].every(Number.isFinite)) {{
                return [0.5, 0.5, 0.5];
            }}

            return [
                Math.min(1, Math.max(0, r)),
                Math.min(1, Math.max(0, g)),
                Math.min(1, Math.max(0, bChan))
            ];
        }}

        function oklchColor(lightness, chroma, hue, alpha = 1) {{
            const rawL = (typeof lightness === 'number') ? lightness : 50;
            const rawC = (typeof chroma === 'number') ? chroma : 0.1;
            const rawH = (typeof hue === 'number') ? hue : 0;
            const [LAdj, CAdj, HAdj, alphaAdj] = applyColorTweaks(rawL, rawC, rawH, alpha);
            const L = LAdj / 100;
            const C = CAdj;
            const H = HAdj;
            const [r, g, b] = oklchToSrgb(L, C, H);
            const rByte = Math.round(r * 255);
            const gByte = Math.round(g * 255);
            const bByte = Math.round(b * 255);
            if (![rByte, gByte, bByte].every(Number.isFinite)) {{
                return 'rgb(128, 128, 128)';
            }}
            if (alphaAdj < 1) {{
                return `rgba(${{rByte}}, ${{gByte}}, ${{bByte}}, ${{alphaAdj}})`;
            }}
            return `rgb(${{rByte}}, ${{gByte}}, ${{bByte}})`;
        }}

        function normalizeColorInput(color, fallback = 'rgb(128, 128, 128)') {{
            if (color === null || color === undefined) {{
                return fallback;
            }}
            if (typeof color !== 'string') {{
                return color;
            }}
            const parsed = parseOklchString(color);
            if (parsed) {{
                return oklchColor(parsed.L, parsed.C, parsed.H, parsed.A);
            }}
            return color;
        }}

        function toColorNumber(color, fallback = '#777777') {{
            // Returns CSS hex string (polished-compatible) instead of JS hex int
            if (typeof color === 'number') {{
                // Convert JS hex int to CSS hex string
                return '#' + color.toString(16).padStart(6, '0');
            }}
            if (typeof color !== 'string') {{
                return fallback;
            }}
            const normalized = normalizeColorInput(color);
            if (typeof normalized === 'string') {{
                color = normalized;
            }}
            if (color.startsWith('#') || color.startsWith('rgb') || color.startsWith('hsl')) {{
                return color;  // Already valid CSS color
            }}
            try {{
                // Convert any valid color to CSS hex string
                const hex = new THREE.Color(color).getHex();
                return '#' + hex.toString(16).padStart(6, '0');
            }} catch (err) {{
                return fallback;
            }}
        }}

        function updateEdgeRanges() {{
            const links = (Graph && Graph.graphData().links) ? Graph.graphData().links : [];
            let minWeight = Infinity;
            let maxWeight = -Infinity;
            let minConf = Infinity;
            let maxConf = -Infinity;
            links.forEach(link => {{
                const weight = typeof link.weight === 'number' ? link.weight : 1;
                const confidence = typeof link.confidence === 'number' ? link.confidence : 1;
                minWeight = Math.min(minWeight, weight);
                maxWeight = Math.max(maxWeight, weight);
                minConf = Math.min(minConf, confidence);
                maxConf = Math.max(maxConf, confidence);
            }});
            EDGE_RANGES = {{
                weight: {{
                    min: isFinite(minWeight) ? minWeight : 1,
                    max: isFinite(maxWeight) ? maxWeight : 1
                }},
                confidence: {{
                    min: isFinite(minConf) ? minConf : 1,
                    max: isFinite(maxConf) ? maxConf : 1
                }}
            }};
        }}

        function refreshNodeFileIndex() {{
            NODE_FILE_INDEX = new Map();
            const nodes = (Graph && Graph.graphData().nodes) ? Graph.graphData().nodes : [];
            nodes.forEach(node => {{
                if (node && node.id) {{
                    NODE_FILE_INDEX.set(node.id, node.fileIdx ?? -1);
                }}
            }});
        }}

        function getLinkFileIdx(link, side) {{
            const endpoint = link?.[side];
            if (endpoint && typeof endpoint === 'object') {{
                return endpoint.fileIdx ?? -1;
            }}
            if (endpoint) {{
                return NODE_FILE_INDEX.get(endpoint) ?? -1;
            }}
            return -1;
        }}

        function normalizeMetric(value, range) {{
            // If range is degenerate (all same values), return based on absolute value:
            // - For 0-1 metrics like confidence: return the value itself
            // - This prevents "all low" coloring when all edges have same high confidence
            if (!range || range.max <= range.min) {{
                return clamp01(value);
            }}
            return clamp01((value - range.min) / (range.max - range.min));
        }}

        function getEdgeColor(link) {{
            const edgeKey = String(link.edge_type || link.type || 'default').toLowerCase();
            const edgeTypeColor = normalizeColorInput(
                EDGE_COLOR_CONFIG[edgeKey] || EDGE_COLOR_CONFIG.default || link.color || '#222222',
                '#222222'
            );
            if (EDGE_MODE === 'type') {{
                return edgeTypeColor;
            }}
            if (EDGE_MODE === 'resolution') {{
                const res = String(link.resolution || 'unknown').toLowerCase();
                const palette = EDGE_MODE_CONFIG.resolution || {{}};
                return normalizeColorInput(palette[res] || edgeTypeColor);
            }}
            if (EDGE_MODE === 'weight') {{
                const weight = typeof link.weight === 'number' ? link.weight : 1;
                const t = normalizeMetric(weight, EDGE_RANGES.weight);
                const weightConfig = EDGE_MODE_CONFIG.weight || {{}};
                const hueMin = weightConfig.hue_min ?? 210;
                const hueMax = weightConfig.hue_max ?? 50;
                const lightness = weightConfig.lightness ?? 42;
                const hue = hueMin + (hueMax - hueMin) * t;
                if (typeof weightConfig.chroma === 'number') {{
                    return oklchColor(lightness, weightConfig.chroma, hue);
                }}
                const saturation = weightConfig.saturation ?? 45;
                const adjustedHue = hue + (COLOR_TWEAKS.hueShift || 0);
                const adjustedLightness = clampValue(lightness + (COLOR_TWEAKS.lightnessShift || 0), 0, 100);
                return hslColor(adjustedHue, saturation, adjustedLightness);
            }}
            if (EDGE_MODE === 'confidence') {{
                const confidence = typeof link.confidence === 'number' ? link.confidence : 1;
                const t = normalizeMetric(confidence, EDGE_RANGES.confidence);
                const confidenceConfig = EDGE_MODE_CONFIG.confidence || {{}};
                const hueMin = confidenceConfig.hue_min ?? 20;
                const hueMax = confidenceConfig.hue_max ?? 120;
                const lightness = confidenceConfig.lightness ?? 44;
                const hue = hueMin + (hueMax - hueMin) * t;
                if (typeof confidenceConfig.chroma === 'number') {{
                    return oklchColor(lightness, confidenceConfig.chroma, hue);
                }}
                const saturation = confidenceConfig.saturation ?? 45;
                const adjustedHue = hue + (COLOR_TWEAKS.hueShift || 0);
                const adjustedLightness = clampValue(lightness + (COLOR_TWEAKS.lightnessShift || 0), 0, 100);
                return hslColor(adjustedHue, saturation, adjustedLightness);
            }}
            if (EDGE_MODE === 'mono') {{
                return normalizeColorInput(EDGE_COLOR_CONFIG.default || '#222222');
            }}
            return edgeTypeColor;
        }}

        function getEdgeWidth(link) {{
            const widthConfig = EDGE_MODE_CONFIG.width || {{}};
            const base = widthConfig.base ?? 0.8;
            if (EDGE_MODE === 'weight') {{
                const weight = typeof link.weight === 'number' ? link.weight : 1;
                const t = normalizeMetric(weight, EDGE_RANGES.weight);
                const scale = widthConfig.weight_scale ?? 2.5;
                return base + (t * scale);
            }}
            if (EDGE_MODE === 'confidence') {{
                const confidence = typeof link.confidence === 'number' ? link.confidence : 1;
                const t = normalizeMetric(confidence, EDGE_RANGES.confidence);
                const scale = widthConfig.confidence_scale ?? 1.5;
                return base + (t * scale);
            }}
            return base;
        }}

        function applyEdgeMode() {{
            updateEdgeRanges();
            refreshNodeFileIndex();
            if (Graph) {{
                Graph.linkColor(link => toColorNumber(getEdgeColor(link), 0x222222));
                Graph.linkOpacity(link => {{
                    const overrideOpacity = (typeof APPEARANCE_STATE.edgeOpacity === 'number')
                        ? APPEARANCE_STATE.edgeOpacity
                        : null;
                    const baseOpacity = (overrideOpacity !== null)
                        ? overrideOpacity
                        : (link.opacity ?? EDGE_DEFAULT_OPACITY);
                    if (fileMode && GRAPH_MODE === 'atoms') {{
                        const srcIdx = getLinkFileIdx(link, 'source');
                        const tgtIdx = getLinkFileIdx(link, 'target');
                        if (srcIdx >= 0 && tgtIdx >= 0 && srcIdx !== tgtIdx) {{
                            const dimFactor = EDGE_MODE_CONFIG.dim?.interfile_factor ?? 0.25;
                            return baseOpacity * dimFactor;
                        }}
                    }}
                    return baseOpacity;
                }});
                if (!flowMode) {{
                    Graph.linkWidth(link => getEdgeWidth(link));
                }}
            }}
        }}

        function cycleEdgeMode() {{
            const currentIndex = EDGE_MODE_ORDER.indexOf(EDGE_MODE);
            const nextIndex = (currentIndex + 1) % EDGE_MODE_ORDER.length;
            setEdgeMode(EDGE_MODE_ORDER[nextIndex]);
        }}

        function setEdgeMode(mode) {{
            if (!EDGE_MODE_ORDER.includes(mode)) return;
            EDGE_MODE = mode;
            const button = document.getElementById('btn-edge-mode');
            if (button) {{
                button.textContent = EDGE_MODE_LABELS[EDGE_MODE] || 'EDGE';
            }}
            applyEdgeMode();
            // Show mode toast hint
            showModeToast(EDGE_MODE_HINTS[mode] || `Edge mode: ${{mode}}`);
        }}

        // Datamap toggles are wired in buildDatamapControls().
        document.getElementById('btn-report').onclick = () => {{
            const panel = document.getElementById('report-panel');
            const btn = document.getElementById('btn-report');
            const isOpen = panel.style.display === 'block';
            panel.style.display = isOpen ? 'none' : 'block';
            btn.classList.toggle('active', !isOpen);
        }};

        // ====================================================================
        // STARFIELD TOGGLE: Show/hide background stars (with localStorage)
        // ====================================================================
        const STARS_STORAGE_KEY = 'collider_stars_visible';

        function setStarsVisible(visible) {{
            const btn = document.getElementById('btn-stars');
            if (btn) btn.classList.toggle('active', visible);
            if (STARFIELD) {{
                STARFIELD.visible = visible;
                STARFIELD.material.opacity = visible ? STARFIELD_OPACITY : 0;
            }}
            try {{
                localStorage.setItem(STARS_STORAGE_KEY, visible ? '1' : '0');
            }} catch (e) {{ /* localStorage unavailable */ }}
        }}

        // Initialize from localStorage (default: visible)
        try {{
            const stored = localStorage.getItem(STARS_STORAGE_KEY);
            if (stored === '0') {{
                // Defer to after STARFIELD is initialized
                setTimeout(() => setStarsVisible(false), 100);
            }}
        }} catch (e) {{ /* localStorage unavailable */ }}

        document.getElementById('btn-stars').onclick = () => {{
            const btn = document.getElementById('btn-stars');
            const isActive = btn.classList.contains('active');
            setStarsVisible(!isActive);
        }};

        // Reset Layout button - explicitly re-run physics
        document.getElementById('btn-reset-layout').onclick = () => {{
            resetLayout();
        }};

        // Hints toggle - enable/disable mode toasts
        document.getElementById('btn-hints').onclick = () => {{
            const btn = document.getElementById('btn-hints');
            HINTS_ENABLED = !HINTS_ENABLED;
            btn.classList.toggle('active', HINTS_ENABLED);
            if (HINTS_ENABLED) {{
                showModeToast('Hints enabled');
            }}
        }};

        document.getElementById('btn-edge-mode').onclick = () => cycleEdgeMode();

        // ====================================================================
        // FLOW MODE: Markov Chain Visualization (Token-Driven)
        // ====================================================================
        let flowMode = false;
        let originalLinkWidths = new Map();
        let highEntropyNodes = new Set();
        // FLOW_CONFIG is set in initGraph() from THE REMOTE CONTROL tokens

        document.getElementById('btn-flow').onclick = () => {{
            flowMode = !flowMode;
            const btn = document.getElementById('btn-flow');
            btn.classList.toggle('active', flowMode);

            // Show/hide flow legend
            const legend = document.getElementById('flow-legend');
            if (legend) legend.classList.toggle('visible', flowMode);

            if (flowMode) {{
                applyFlowVisualization();
                showModeToast('FLOW: edge width = transition probability, particles = direction');
            }} else {{
                clearFlowVisualization();
                showModeToast('Flow mode off');
            }}
        }};

        function applyFlowVisualization() {{
            const markov = FULL_GRAPH.markov || {{}};
            const highEntropy = markov.high_entropy_nodes || [];

            // Get flow config from tokens (THE REMOTE CONTROL)
            const flowCfg = FLOW_CONFIG || {{}};
            const highlightColor = flowCfg.highlightColor || '#ff8c00';
            const sizeMult = flowCfg.sizeMultiplier || 1.8;
            const edgeScale = flowCfg.edgeWidthScale || 3.0;  // Increased for visibility
            const particles = flowCfg.particles || {{}};
            const topK = flowCfg.topKEdges || 3;  // Show only top K outgoing edges per node
            const minWeight = flowCfg.minWeight || 0.1;  // Minimum weight threshold

            // Build set of high entropy node names
            highEntropyNodes.clear();
            highEntropy.forEach(n => highEntropyNodes.add(n.node));

            const graphNodes = Graph.graphData().nodes;
            const graphLinks = Graph.graphData().links;

            // THRESHOLDING: Build a map of top-K outgoing edges per source node
            const edgesBySource = new Map();
            graphLinks.forEach(link => {{
                const srcId = typeof link.source === 'object' ? link.source.id : link.source;
                if (!edgesBySource.has(srcId)) {{
                    edgesBySource.set(srcId, []);
                }}
                edgesBySource.get(srcId).push(link);
            }});

            // For each source, keep only top-K by markov_weight (transition probability)
            const visibleEdges = new Set();
            edgesBySource.forEach((edges, srcId) => {{
                const sorted = edges
                    .filter(e => (e.markov_weight || 0) >= minWeight)
                    .sort((a, b) => (b.markov_weight || 0) - (a.markov_weight || 0))
                    .slice(0, topK);
                sorted.forEach(e => visibleEdges.add(e));
            }});

            // Store original colors and apply flow coloring
            graphNodes.forEach(node => {{
                if (!originalNodeColors.has(node.id)) {{
                    originalNodeColors.set(node.id, node.color);
                }}
                // High entropy nodes highlighted (decision points)
                if (highEntropyNodes.has(node.name)) {{
                    node.color = highlightColor;
                    node.val = (node.val || 1) * sizeMult;
                }}
            }});

            // Update link widths based on markov_weight (with thresholding)
            Graph.linkWidth(link => {{
                if (!visibleEdges.has(link)) return 0.1;  // Dim non-top edges
                const mw = link.markov_weight || 0;
                return Math.max(0.5, mw * edgeScale);
            }});

            // Update link opacity to emphasize important edges
            Graph.linkOpacity(link => {{
                if (!visibleEdges.has(link)) return 0.05;  // Nearly invisible
                return 0.6 + (link.markov_weight || 0) * 0.4;  // 0.6 - 1.0 range
            }});

            // Add directional particles only on visible edges
            Graph.linkDirectionalParticles(link => {{
                if (!visibleEdges.has(link)) return 0;
                return particles.count || 3;
            }});
            Graph.linkDirectionalParticleWidth(particles.width || 2.5);
            Graph.linkDirectionalParticleSpeed(particles.speed || 0.008);
            Graph.linkDirectionalParticleColor(() => '#ffaa00');

            // Update node coloring
            Graph.nodeColor(n => toColorNumber(n.color, '#888888'));

            updateSelectionVisuals();

            // Debug: count edges with markov weights
            const edgesWithMarkov = graphLinks.filter(l => l.markov_weight > 0).length;
            console.log(`Flow mode: ${{highEntropyNodes.size}} high entropy nodes, ${{visibleEdges.size}} visible edges (top-${{topK}} per node), ${{edgesWithMarkov}}/${{graphLinks.length}} edges with markov weights`);
        }}

        function clearFlowVisualization() {{
            const graphNodes = Graph.graphData().nodes;
            const sizeMult = (FLOW_CONFIG || {{}}).sizeMultiplier || 1.8;

            // Restore original node colors and sizes
            graphNodes.forEach(node => {{
                if (originalNodeColors.has(node.id)) {{
                    node.color = originalNodeColors.get(node.id);
                }}
                // Reset size if it was a high entropy node
                if (highEntropyNodes.has(node.name)) {{
                    node.val = (node.val || sizeMult) / sizeMult;
                }}
            }});

            // Reset link widths
            Graph.linkWidth(1);

            // Remove directional particles
            Graph.linkDirectionalParticles(0);

            // Update coloring
            Graph.nodeColor(n => toColorNumber(n.color, '#888888'));

            highEntropyNodes.clear();
            applyEdgeMode();
            updateSelectionVisuals();
        }}

        function setDatamap(prefix) {{
            const nextSet = new Set(ACTIVE_DATAMAPS);
            if (!prefix) {{
                nextSet.clear();
            }} else if (nextSet.has(prefix)) {{
                nextSet.delete(prefix);
            }} else {{
                nextSet.add(prefix);
            }}

            if (!FULL_GRAPH) {{
                ACTIVE_DATAMAPS = nextSet;
                updateDatamapControls();
                return;
            }}

            const subset = filterGraph(FULL_GRAPH, CURRENT_DENSITY, nextSet, VIS_FILTERS);
            if (!subset.nodes.length) {{
                showToast('No nodes for that datamap selection.');
                updateDatamapControls();
                return;
            }}

            ACTIVE_DATAMAPS = nextSet;
            updateDatamapControls();
            refreshGraph();
        }}

        function setNodeColorMode(mode) {{
            NODE_COLOR_MODE = mode;
            refreshGraph();
        }}

        function applyDatamap(prefix) {{
            setDatamap(prefix);
        }}

        // ====================================================================
        // FILE BOUNDARIES & HOVER SYSTEM
        // ====================================================================
        let fileBoundaryMeshes = [];
        let fileMode = false;
        let fileVizMode = 'color'; // 'color' | 'hulls' | 'cluster'
        let originalNodeColors = new Map();
        let clusterForceActive = false;
        let hullRedrawTimer = null;
        let hullRedrawAttempts = 0;

        function hashToUnit(value) {{
            const str = String(value || '');
            let hash = 0;
            for (let i = 0; i < str.length; i++) {{
                hash = ((hash << 5) - hash) + str.charCodeAt(i);
                hash |= 0;
            }}
            return (hash >>> 0) / 0xffffffff;
        }}

        function getFileHue(fileIdx, totalFiles, fileName) {{
            const strategy = FILE_COLOR_CONFIG.strategy || 'golden-angle';
            if (strategy === 'sequential') {{
                const denom = Math.max(1, totalFiles);
                return (fileIdx / denom) * 360;
            }}
            if (strategy === 'hash') {{
                const seed = fileName || String(fileIdx);
                return hashToUnit(seed) * 360;
            }}
            const angle = FILE_COLOR_CONFIG.angle ?? 137.5;
            return (fileIdx * angle) % 360;
        }}

        function getFileColor(fileIdx, totalFiles, fileName, lightnessOverride = null) {{
            const saturation = FILE_COLOR_CONFIG.saturation ?? 70;
            const lightness = (lightnessOverride !== null)
                ? lightnessOverride
                : (FILE_COLOR_CONFIG.lightness ?? 50);
            const hue = getFileHue(fileIdx, totalFiles, fileName);
            if (typeof FILE_COLOR_CONFIG.chroma === 'number') {{
                return oklchColor(lightness, FILE_COLOR_CONFIG.chroma, hue);
            }}
            const adjustedHue = hue + (COLOR_TWEAKS.hueShift || 0);
            const adjustedLightness = clampValue(lightness + (COLOR_TWEAKS.lightnessShift || 0), 0, 100);
            return `hsl(${{adjustedHue}}, ${{saturation}}%, ${{adjustedLightness}}%)`;
        }}

        // Track last hovered node to avoid unnecessary re-renders
        let _lastHoveredNodeId = null;

        function updateHoverPanel(node) {{
            const hoverPanel = document.getElementById('hover-panel');
            if (!hoverPanel) return;

            if (!node) {{
                // Mouse left node - hide panel after delay
                setTimeout(() => {{
                    if (_lastHoveredNodeId === null) {{
                        hoverPanel.classList.remove('visible');
                    }}
                }}, 200);
                _lastHoveredNodeId = null;
                return;
            }}

            // Only update if node changed (performance)
            const nodeId = node.id || node.name || '';
            if (nodeId === _lastHoveredNodeId) return;
            _lastHoveredNodeId = nodeId;

            // Update hover panel content with canonical taxonomy fields
            document.getElementById('hover-name').textContent = node.name || node.id || 'Unknown';
            document.getElementById('hover-kind').textContent = node.kind || node.symbol_kind || 'node';
            document.getElementById('hover-atom').textContent = node.atom || '--';
            document.getElementById('hover-family').textContent = getNodeAtomFamily(node);
            document.getElementById('hover-ring').textContent = getNodeRing(node);
            document.getElementById('hover-tier').textContent = getNodeTier(node);
            document.getElementById('hover-role').textContent = node.role || '--';

            // Show file path (truncated if long)
            const filePath = node.file_path || node.file || '';
            const shortPath = filePath.length > 50 ? '...' + filePath.slice(-47) : filePath;
            document.getElementById('hover-file').textContent = shortPath || '--';

            // Show panel and trigger smart placement
            hoverPanel.classList.add('visible');
            HudLayoutManager.reflow();
        }}

        function buildDatasetKey(data) {{
            const meta = (data && data.meta) ? data.meta : {{}};
            const target = meta.target || meta.project || 'dataset';
            const version = meta.version || '';
            const nodeCount = Array.isArray(data?.nodes) ? data.nodes.length : 0;
            const edgeCount = Array.isArray(data?.links)
                ? data.links.length
                : (Array.isArray(data?.edges) ? data.edges.length : 0);
            const raw = `${{target}}|${{nodeCount}}|${{edgeCount}}|${{version}}`;
            return raw.replace(/[^a-zA-Z0-9_.-]/g, '_').slice(0, 180);
        }}

        function loadGroups() {{
            GROUPS = [];
            try {{
                const stored = localStorage.getItem(GROUPS_STORAGE_KEY);
                if (stored) {{
                    const parsed = JSON.parse(stored);
                    if (Array.isArray(parsed)) {{
                        GROUPS = parsed;
                    }}
                }}
            }} catch (e) {{
                // localStorage unavailable
            }}
            GROUPS = GROUPS.filter(group => group && group.id && Array.isArray(group.node_ids));
            GROUPS.forEach(group => {{
                if (group.visible === undefined) group.visible = true;
            }});
        }}

        function saveGroups() {{
            try {{
                localStorage.setItem(GROUPS_STORAGE_KEY, JSON.stringify(GROUPS));
            }} catch (e) {{
                // localStorage unavailable
            }}
        }}

        function getNextGroupColor() {{
            const hue = (GROUPS.length * 137.5) % 360;
            return hslColor(hue, 65, 55);
        }}

        function getGroupById(groupId) {{
            return GROUPS.find(group => group.id === groupId) || null;
        }}

        function getPrimaryGroupForNode(nodeId) {{
            const visibleGroups = GROUPS.filter(group =>
                group.visible !== false && Array.isArray(group.node_ids) && group.node_ids.includes(nodeId)
            );
            if (!visibleGroups.length) return null;
            if (ACTIVE_GROUP_ID) {{
                const active = visibleGroups.find(group => group.id === ACTIVE_GROUP_ID);
                if (active) return active;
            }}
            return visibleGroups[0];
        }}

        function renderGroupList() {{
            const container = document.getElementById('group-list');
            if (!container) return;
            container.innerHTML = '';

            if (!GROUPS.length) {{
                const empty = document.createElement('div');
                empty.style.fontSize = '9px';
                empty.style.color = 'rgba(255,255,255,0.4)';
                empty.textContent = 'No groups yet';
                container.appendChild(empty);
                return;
            }}

            GROUPS.forEach(group => {{
                const row = document.createElement('div');
                row.className = 'group-item';
                row.classList.toggle('active', group.id === ACTIVE_GROUP_ID);

                const dot = document.createElement('span');
                dot.className = 'group-color';
                dot.style.background = group.color || '#6fe8ff';

                const name = document.createElement('span');
                name.className = 'group-name';
                name.textContent = group.name || 'Group';

                const count = document.createElement('span');
                count.className = 'group-count';
                count.textContent = String((group.node_ids || []).length);

                const toggle = document.createElement('input');
                toggle.type = 'checkbox';
                toggle.className = 'group-toggle';
                toggle.checked = group.visible !== false;
                toggle.onchange = (e) => {{
                    e.stopPropagation();
                    group.visible = toggle.checked;
                    saveGroups();
                    updateSelectionVisuals();
                    renderGroupList();
                }};

                row.onclick = (e) => {{
                    if (e.target === toggle) return;
                    ACTIVE_GROUP_ID = group.id;
                    renderGroupList();
                    setSelection(group.node_ids || []);
                    updateSelectionVisuals();
                }};

                row.appendChild(dot);
                row.appendChild(name);
                row.appendChild(count);
                row.appendChild(toggle);
                container.appendChild(row);
            }});
        }}

        function updateGroupButtonState() {{
            const btn = document.getElementById('btn-create-group');
            if (!btn) return;
            const hasSelection = SELECTED_NODE_IDS.size > 0;
            btn.classList.toggle('disabled', !hasSelection);
            btn.disabled = !hasSelection;
        }}

        function createGroupFromSelection() {{
            if (SELECTED_NODE_IDS.size === 0) return;
            const nodeIds = Array.from(SELECTED_NODE_IDS);
            const groupId = `group_${{Date.now().toString(36)}}`;
            const groupName = `Group ${{GROUPS.length + 1}}`;
            const groupColor = getNextGroupColor();
            GROUPS.push({{
                id: groupId,
                name: groupName,
                color: groupColor,
                node_ids: nodeIds,
                visible: true
            }});
            ACTIVE_GROUP_ID = groupId;
            saveGroups();
            renderGroupList();
            updateSelectionVisuals();
            showToast(`Created ${{groupName}} (${{nodeIds.length}})`);
        }}

        function getSelectedNodes() {{
            if (!Graph || !Graph.graphData) return [];
            const nodes = Graph.graphData().nodes || [];
            return nodes.filter(node => node && node.id && SELECTED_NODE_IDS.has(node.id));
        }}

        function setSelection(ids, additive = false) {{
            if (!additive) {{
                SELECTED_NODE_IDS.clear();
            }}
            (ids || []).forEach(id => {{
                if (id) SELECTED_NODE_IDS.add(id);
            }});
            updateSelectionPanel();
            updateSelectionVisuals();
            updateGroupButtonState();
        }}

        function toggleSelection(node) {{
            if (!node || !node.id) return;
            if (SELECTED_NODE_IDS.has(node.id)) {{
                SELECTED_NODE_IDS.delete(node.id);
            }} else {{
                SELECTED_NODE_IDS.add(node.id);
            }}
            updateSelectionPanel();
            updateSelectionVisuals();
            updateGroupButtonState();
        }}

        function clearSelection() {{
            SELECTED_NODE_IDS.clear();
            updateSelectionPanel();
            updateSelectionVisuals();
            updateGroupButtonState();
        }}

        function maybeClearSelection() {{
            const now = Date.now();
            if (now - LAST_MARQUEE_END_TS < 250) return;
            clearSelection();
        }}

        function formatCountList(items, limit = 4) {{
            return items.slice(0, limit).map(([key, count]) => `${{key}} ${{count}}`).join(' · ') || '--';
        }}

        function appendSelectionRow(container, label, value) {{
            const row = document.createElement('div');
            row.className = 'selection-row';
            const labelEl = document.createElement('span');
            labelEl.className = 'label';
            labelEl.textContent = label;
            const valueEl = document.createElement('span');
            valueEl.textContent = value || '--';
            row.appendChild(labelEl);
            row.appendChild(valueEl);
            container.appendChild(row);
        }}

        function updateSelectionPanel() {{
            const panel = document.getElementById('selection-panel');
            const body = document.getElementById('selection-body');
            const title = document.getElementById('selection-title');
            if (!panel || !body) return;

            const nodes = getSelectedNodes();
            if (!nodes.length) {{
                panel.classList.remove('visible');
                body.innerHTML = '';
                return;
            }}

            panel.classList.add('visible');
            if (title) title.textContent = `SELECTION (${{nodes.length}})`;
            body.innerHTML = '';

            if (nodes.length <= 3) {{
                nodes.forEach(node => {{
                    const item = document.createElement('div');
                    item.className = 'selection-item';
                    const name = document.createElement('div');
                    name.className = 'selection-name';
                    name.textContent = node.name || node.id || 'Unknown';
                    item.appendChild(name);
                    appendSelectionRow(item, 'Family', getNodeAtomFamily(node));
                    appendSelectionRow(item, 'Ring', getNodeRing(node));
                    appendSelectionRow(item, 'Tier', getNodeTier(node));
                    appendSelectionRow(item, 'Role', node.role || '--');
                    const filePath = node.file_path || node.file || '';
                    if (filePath) {{
                        const shortPath = filePath.length > 48 ? '...' + filePath.slice(-45) : filePath;
                        appendSelectionRow(item, 'File', shortPath);
                    }}
                    body.appendChild(item);
                }});
            }} else {{
                const summary = document.createElement('div');
                summary.className = 'selection-summary';

                const families = collectCounts(nodes, n => getNodeAtomFamily(n));
                const rings = collectCounts(nodes, n => getNodeRing(n));
                const tiers = collectCounts(nodes, n => getNodeTier(n));

                const total = document.createElement('div');
                total.textContent = `Total: ${{nodes.length}} nodes`;
                summary.appendChild(total);

                const familyRow = document.createElement('div');
                familyRow.textContent = `Family: ${{formatCountList(families)}}`;
                summary.appendChild(familyRow);

                const ringRow = document.createElement('div');
                ringRow.textContent = `Ring: ${{formatCountList(rings)}}`;
                summary.appendChild(ringRow);

                const tierRow = document.createElement('div');
                tierRow.textContent = `Tier: ${{formatCountList(tiers)}}`;
                summary.appendChild(tierRow);

                const numericKeys = [
                    ['tokens', 'TOKENS'],
                    ['bytes', 'BYTES'],
                    ['loc', 'LOC'],
                    ['lines', 'LINES'],
                    ['lines_of_code', 'LOC'],
                    ['size', 'SIZE']
                ];
                const totals = {{}};
                nodes.forEach(node => {{
                    numericKeys.forEach(([key]) => {{
                        const value = Number(node[key]);
                        if (Number.isFinite(value)) {{
                            totals[key] = (totals[key] || 0) + value;
                        }}
                    }});
                }});
                numericKeys.forEach(([key, label]) => {{
                    if (totals[key]) {{
                        const row = document.createElement('div');
                        row.textContent = `${{label}}: ${{Math.round(totals[key])}}`;
                        summary.appendChild(row);
                    }}
                }});

                body.appendChild(summary);
            }}

            HudLayoutManager.reflow();
        }}

        function updateOverlayScale(node) {{
            const base = Math.max(0.6, (node.val || 1) * (APPEARANCE_STATE.nodeScale || 1));
            const selectionScale = base * 1.9;
            const groupScale = base * 1.5;
            if (node.__selectionHalo) {{
                node.__selectionHalo.scale.set(selectionScale, selectionScale, selectionScale);
            }}
            if (node.__groupHalo) {{
                node.__groupHalo.scale.set(groupScale, groupScale, groupScale);
            }}
        }}

        function ensureNodeOverlays(node) {{
            if (!node) return null;
            if (node.__overlayGroup) return node.__overlayGroup;

            const group = new THREE.Group();

            const selectionMaterial = new THREE.MeshBasicMaterial({{
                color: 0x88d0ff,
                transparent: true,
                opacity: 0.35,
                depthWrite: false
            }});
            const selectionHalo = new THREE.Mesh(SELECTION_HALO_GEOMETRY, selectionMaterial);
            selectionHalo.visible = false;
            selectionHalo.renderOrder = 3;

            const groupMaterial = new THREE.MeshBasicMaterial({{
                color: 0xffffff,
                transparent: true,
                opacity: 0.18,
                depthWrite: false
            }});
            const groupHalo = new THREE.Mesh(GROUP_HALO_GEOMETRY, groupMaterial);
            groupHalo.visible = false;
            groupHalo.renderOrder = 2;

            group.add(selectionHalo);
            group.add(groupHalo);

            node.__selectionHalo = selectionHalo;
            node.__groupHalo = groupHalo;
            node.__overlayGroup = group;
            return group;
        }}

        function updateSelectionVisuals() {{
            if (!Graph || !Graph.graphData) return;
            const nodes = Graph.graphData().nodes || [];
            nodes.forEach(node => {{
                ensureNodeOverlays(node);
                updateOverlayScale(node);
                if (node.__selectionHalo) {{
                    node.__selectionHalo.visible = SELECTED_NODE_IDS.has(node.id);
                }}
                if (node.__groupHalo) {{
                    const group = getPrimaryGroupForNode(node.id);
                    if (group) {{
                        node.__groupHalo.visible = group.visible !== false;
                        node.__groupHalo.material.color.set(group.color || '#88d0ff');
                        node.__groupHalo.material.opacity =
                            (group.id === ACTIVE_GROUP_ID) ? 0.45 : 0.18;
                    }} else {{
                        node.__groupHalo.visible = false;
                    }}
                }}
            }});
        }}

        function syncSelectionAfterGraphUpdate() {{
            if (!Graph || !Graph.graphData) return;
            const visibleIds = new Set((Graph.graphData().nodes || []).map(n => n.id));
            let changed = false;
            Array.from(SELECTED_NODE_IDS).forEach(id => {{
                if (!visibleIds.has(id)) {{
                    SELECTED_NODE_IDS.delete(id);
                    changed = true;
                }}
            }});
            if (changed) {{
                updateSelectionPanel();
            }}
            updateSelectionVisuals();
            updateGroupButtonState();
        }}

        function updateSelectionBox(rect) {{
            if (!SELECTION_BOX) return;
            SELECTION_BOX.style.display = 'block';
            SELECTION_BOX.style.left = `${{rect.left}}px`;
            SELECTION_BOX.style.top = `${{rect.top}}px`;
            SELECTION_BOX.style.width = `${{rect.width}}px`;
            SELECTION_BOX.style.height = `${{rect.height}}px`;
        }}

        function getBoxRect(start, end) {{
            const left = Math.min(start.x, end.x);
            const top = Math.min(start.y, end.y);
            const width = Math.abs(start.x - end.x);
            const height = Math.abs(start.y - end.y);
            return {{
                left,
                top,
                width,
                height,
                right: left + width,
                bottom: top + height
            }};
        }}

        function getNodeScreenPosition(node) {{
            if (!Graph || !Graph.camera || !node) return null;
            if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return null;
            const camera = Graph.camera();
            const vector = new THREE.Vector3(node.x, node.y, node.z || 0);
            vector.project(camera);
            const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
            const y = (-vector.y * 0.5 + 0.5) * window.innerHeight;
            return {{ x, y }};
        }}

        function selectNodesInBox(rect, additive = true) {{
            if (!Graph || !Graph.graphData) return;
            const nodes = Graph.graphData().nodes || [];
            const selected = [];
            nodes.forEach(node => {{
                const pos = getNodeScreenPosition(node);
                if (!pos) return;
                if (pos.x >= rect.left && pos.x <= rect.right &&
                    pos.y >= rect.top && pos.y <= rect.bottom) {{
                    if (node.id) selected.push(node.id);
                }}
            }});
            if (selected.length) {{
                setSelection(selected, additive);
            }}
        }}

        function setupSelectionInteractions() {{
            const clearBtn = document.getElementById('selection-clear');
            if (clearBtn) {{
                clearBtn.onclick = () => clearSelection();
            }}

            const groupBtn = document.getElementById('btn-create-group');
            if (groupBtn) {{
                groupBtn.onclick = () => createGroupFromSelection();
            }}

            SELECTION_BOX = document.getElementById('selection-box');
            if (!Graph || !Graph.renderer || !SELECTION_BOX) return;

            const canvas = Graph.renderer().domElement;
            if (!canvas) return;

            const onPointerDown = (e) => {{
                // Shift + left-drag = marquee selection
                if (e.button !== 0) return;
                if (!e.shiftKey) return;
                if (e.target !== canvas) return;
                if (HOVERED_NODE) return;
                MARQUEE_ACTIVE = true;
                MARQUEE_START = {{ x: e.clientX, y: e.clientY }};
                updateSelectionBox(getBoxRect(MARQUEE_START, MARQUEE_START));
                if (Graph.controls()) {{
                    Graph.controls().enabled = false;
                }}
                e.preventDefault();
            }};

            const onPointerMove = (e) => {{
                if (!MARQUEE_ACTIVE || !MARQUEE_START) return;
                updateSelectionBox(getBoxRect(MARQUEE_START, {{ x: e.clientX, y: e.clientY }}));
            }};

            const finishSelection = (e) => {{
                if (!MARQUEE_ACTIVE || !MARQUEE_START) return;
                const rect = getBoxRect(MARQUEE_START, {{ x: e.clientX, y: e.clientY }});
                SELECTION_BOX.style.display = 'none';
                MARQUEE_ACTIVE = false;
                MARQUEE_START = null;
                LAST_MARQUEE_END_TS = Date.now();
                if (Graph.controls()) {{
                    Graph.controls().enabled = true;
                }}
                if (rect.width > 4 && rect.height > 4) {{
                    selectNodesInBox(rect, true);
                }}
            }};

            canvas.addEventListener('pointerdown', onPointerDown, {{ passive: false }});
            canvas.addEventListener('pointermove', onPointerMove, {{ passive: true }});
            canvas.addEventListener('pointerup', finishSelection, {{ passive: true }});
            canvas.addEventListener('pointerleave', finishSelection, {{ passive: true }});
        }}

        function initSelectionState(data) {{
            DATASET_KEY = buildDatasetKey(data);
            GROUPS_STORAGE_KEY = `collider_groups_${{DATASET_KEY}}`;
            loadGroups();
            renderGroupList();
            updateSelectionPanel();
            updateGroupButtonState();
        }}

        function handleNodeHover(node, data) {{
            const filePanel = document.getElementById('file-panel');
            HOVERED_NODE = node || null;

            // Always update hover panel (separate from file panel)
            updateHoverPanel(node);

            if (!VIS_FILTERS.metadata.showFilePanel) {{
                filePanel.classList.remove('visible');
                return;
            }}

            if (!node) {{
                // Mouse left node - hide panel after delay
                setTimeout(() => {{
                    if (!fileMode) filePanel.classList.remove('visible');
                }}, 300);
                return;
            }}

            // Get file info from boundaries
            const boundaries = data.file_boundaries || [];
            const fileIdx = node.fileIdx;

            if (fileIdx < 0 || fileIdx >= boundaries.length) {{
                return;
            }}

            const fileInfo = boundaries[fileIdx];

            // Update panel content
            document.getElementById('file-name').textContent = fileInfo.file_name || 'unknown';
            document.getElementById('file-cohesion').textContent =
                `Cohesion: ${{(fileInfo.cohesion * 100).toFixed(0)}}%`;
            document.getElementById('file-purpose').textContent = fileInfo.purpose || '--';
            document.getElementById('file-atom-count').textContent = fileInfo.atom_count || 0;
            document.getElementById('file-lines').textContent =
                fileInfo.line_range ? `${{fileInfo.line_range[0]}}-${{fileInfo.line_range[1]}}` : '--';
            document.getElementById('file-classes').textContent =
                (fileInfo.classes || []).join(', ') || 'none';
            document.getElementById('file-functions').textContent =
                'Functions: ' + ((fileInfo.functions || []).slice(0, 8).join(', ') || 'none');

            // Show code preview from node body
            const code = node.body || '// no source available';
            document.getElementById('file-code').textContent = code;

            // Show panel and trigger smart placement
            filePanel.classList.add('visible');
            HudLayoutManager.reflow();
        }}

        function handleNodeClick(node, event) {{
            if (!node) return;
            const additive = event && event.shiftKey;
            if (additive) {{
                toggleSelection(node);
                return;
            }}
            if (node.id) {{
                setSelection([node.id]);
            }}
            if ((GRAPH_MODE === 'files' || GRAPH_MODE === 'hybrid') && node.isFileNode) {{
                toggleFileExpand(node.fileIdx);
            }}
        }}

        function toggleFileExpand(fileIdx) {{
            if (!Number.isFinite(fileIdx)) return;
            captureFileNodePositions();
            const fileInfo = (FULL_GRAPH?.file_boundaries || [])[fileIdx] || {{}};
            const fileLabel = fileInfo.file_name || fileInfo.file || `file-${{fileIdx}}`;
            if (EXPANDED_FILES.has(fileIdx)) {{
                EXPANDED_FILES.delete(fileIdx);
                showToast(`Collapsed ${{fileLabel}}`);
            }} else {{
                EXPANDED_FILES.clear();
                EXPANDED_FILES.add(fileIdx);
                showToast(`Expanded ${{fileLabel}}`);
            }}
            GRAPH_MODE = (EXPANDED_FILES.size > 0) ? 'hybrid' : 'files';
            refreshGraph();
        }}

        function sampleFileNodes(nodes, maxPoints) {{
            if (nodes.length <= maxPoints) return nodes;
            const step = Math.ceil(nodes.length / maxPoints);
            return nodes.filter((_, idx) => idx % step === 0);
        }}

        function buildHull2D(points) {{
            if (points.length < 3) return null;
            const unique = new Map();
            points.forEach(p => {{
                const key = `${{p.x.toFixed(4)}},${{p.y.toFixed(4)}}`;
                if (!unique.has(key)) unique.set(key, p);
            }});
            const pts = Array.from(unique.values()).sort((a, b) => {{
                if (a.x === b.x) return a.y - b.y;
                return a.x - b.x;
            }});
            if (pts.length < 3) return null;
            const cross = (o, a, b) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
            const lower = [];
            for (const p of pts) {{
                while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) {{
                    lower.pop();
                }}
                lower.push(p);
            }}
            const upper = [];
            for (let i = pts.length - 1; i >= 0; i--) {{
                const p = pts[i];
                while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) {{
                    upper.pop();
                }}
                upper.push(p);
            }}
            upper.pop();
            lower.pop();
            return lower.concat(upper);
        }}

        function computeCentroid(points) {{
            const centroid = new THREE.Vector3();
            points.forEach(p => centroid.add(p));
            return centroid.divideScalar(Math.max(1, points.length));
        }}

        function quantile(values, q) {{
            if (!values.length) return 0;
            const sorted = values.slice().sort((a, b) => a - b);
            const pos = (sorted.length - 1) * q;
            const base = Math.floor(pos);
            const rest = pos - base;
            if (sorted[base + 1] !== undefined) {{
                return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
            }}
            return sorted[base];
        }}

        function drawFileBoundaries(data) {{
            let drawn = 0;
            // TOKEN-DRIVEN: Get boundary appearance config
            const boundaryConfig = data.appearance?.boundary || {{}};
            const fillOpacity =
                (typeof APPEARANCE_STATE.boundaryFill === 'number')
                    ? APPEARANCE_STATE.boundaryFill
                    : (boundaryConfig.fill_opacity || 0.08);
            const wireOpacity =
                (typeof APPEARANCE_STATE.boundaryWire === 'number')
                    ? APPEARANCE_STATE.boundaryWire
                    : (boundaryConfig.wire_opacity || 0.3);
            const padding = boundaryConfig.padding || 1.2;
            const minExtent = boundaryConfig.min_extent || 6;
            const quantileRange = boundaryConfig.quantile || 0.9;
            const lowQ = Math.max(0, (1 - quantileRange) / 2);
            const highQ = Math.min(1, 1 - lowQ);
            const boundaryPhysics = data.physics?.boundary || {{}};
            const hullType = String(boundaryPhysics.hullType || 'convex').toLowerCase();
            const totalFiles = (data.file_boundaries || []).length;

            const graphNodes = Graph.graphData().nodes;
            const scene = Graph.scene();

            // Clear existing boundary meshes
            fileBoundaryMeshes.forEach(mesh => scene.remove(mesh));
            fileBoundaryMeshes = [];

            if (!fileMode) return drawn;

            // Group nodes by file (only use nodes with stable positions)
            const fileGroups = {{}};
            const validNodes = graphNodes.filter(node => {{
                if (!node) return false;
                if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return false;
                if (IS_3D && !Number.isFinite(node.z)) return false;
                return true;
            }});

            if (!validNodes.length) return drawn;

            validNodes.forEach(node => {{
                const idx = node.fileIdx;
                if (idx >= 0) {{
                    if (!fileGroups[idx]) fileGroups[idx] = [];
                    fileGroups[idx].push(node);
                }}
            }});

            // Draw boundary for each file group
            Object.entries(fileGroups).forEach(([fileIdx, nodes]) => {{
                const sampled = sampleFileNodes(nodes, 180);
                const xs = sampled.map(n => n.x || 0);
                const ys = sampled.map(n => n.y || 0);
                const zs = sampled.map(n => n.z || 0);

                const minX = quantile(xs, lowQ);
                const maxX = quantile(xs, highQ);
                const minY = quantile(ys, lowQ);
                const maxY = quantile(ys, highQ);
                const minZ = quantile(zs, lowQ);
                const maxZ = quantile(zs, highQ);

                const filtered = sampled.filter(n => {{
                    const x = n.x || 0;
                    const y = n.y || 0;
                    const z = n.z || 0;
                    return x >= minX && x <= maxX && y >= minY && y <= maxY && z >= minZ && z <= maxZ;
                }});
                const hullNodes = filtered.length >= 3 ? filtered : sampled;
                const positions = hullNodes.map(n => new THREE.Vector3(n.x || 0, n.y || 0, n.z || 0));
                const centroid = computeCentroid(positions);
                const zRange = maxZ - minZ;
                const extentX = Math.max(0.001, maxX - minX);
                const extentY = Math.max(0.001, maxY - minY);
                const extentZ = Math.max(0.001, maxZ - minZ);
                const scaleFixX = Math.max(1, minExtent / extentX);
                const scaleFixY = Math.max(1, minExtent / extentY);
                const scaleFixZ = IS_3D ? Math.max(1, minExtent / extentZ) : 1;
                const scaleX = padding * scaleFixX;
                const scaleY = padding * scaleFixY;
                const scaleZ = padding * scaleFixZ;
                const sizeX = extentX * scaleX;
                const sizeY = extentY * scaleY;
                const sizeZ = extentZ * scaleZ;

                const fileIndex = Number.parseInt(fileIdx, 10);
                const safeFileIdx = Number.isFinite(fileIndex) ? fileIndex : 0;
                const fileInfo = (data.file_boundaries || [])[safeFileIdx] || {{}};
                const fileLabel = fileInfo.file || fileInfo.file_name || fileIdx;
                const color = new THREE.Color(
                    getFileColor(safeFileIdx, totalFiles, fileLabel)
                );

                let mesh = null;
                let wireMesh = null;

                if (nodes.length < 3) {{
                    const rawPositions = nodes.map(n => new THREE.Vector3(n.x || 0, n.y || 0, n.z || 0));
                    const smallCentroid = computeCentroid(rawPositions);
                    const maxRadius = rawPositions.reduce((acc, p) => {{
                        return Math.max(acc, p.distanceTo(smallCentroid));
                    }}, 0);
                    const bubbleRadius = Math.max(minExtent * 0.5, maxRadius + minExtent * 0.35);
                    const material = new THREE.MeshBasicMaterial({{
                        color: color,
                        transparent: true,
                        opacity: fillOpacity,
                        wireframe: false,
                        side: THREE.DoubleSide
                    }});
                    if (IS_3D) {{
                        const geometry = new THREE.SphereGeometry(bubbleRadius, 14, 10);
                        mesh = new THREE.Mesh(geometry, material);
                        mesh.position.copy(smallCentroid);
                        const wireMaterial = new THREE.LineBasicMaterial({{
                            color: color,
                            transparent: true,
                            opacity: wireOpacity
                        }});
                        const edges = new THREE.EdgesGeometry(geometry);
                        wireMesh = new THREE.LineSegments(edges, wireMaterial);
                        wireMesh.position.copy(mesh.position);
                    }} else {{
                        const geometry = new THREE.CircleGeometry(bubbleRadius, 32);
                        mesh = new THREE.Mesh(geometry, material);
                        mesh.position.set(smallCentroid.x, smallCentroid.y, smallCentroid.z);
                        const wireMaterial = new THREE.LineBasicMaterial({{
                            color: color,
                            transparent: true,
                            opacity: wireOpacity
                        }});
                        const edges = new THREE.EdgesGeometry(geometry);
                        wireMesh = new THREE.LineSegments(edges, wireMaterial);
                        wireMesh.position.copy(mesh.position);
                    }}
                }}

                if (!mesh && hullType === 'convex') {{
                    if (IS_3D && zRange > 0.001 && positions.length >= 4) {{
                        const ConvexCtor =
                            (typeof ConvexGeometry !== 'undefined')
                                ? ConvexGeometry
                                : (THREE.ConvexGeometry || null);
                        const relPoints = positions.map(p => p.clone().sub(centroid));
                        let boundaryGeometry = null;
                        if (ConvexCtor) {{
                            try {{
                                boundaryGeometry = new ConvexCtor(relPoints);
                            }} catch (err) {{
                                boundaryGeometry = null;
                            }}
                        }}
                        if (boundaryGeometry) {{
                            const material = new THREE.MeshBasicMaterial({{
                                color: color,
                                transparent: true,
                                opacity: fillOpacity,
                                wireframe: false,
                                side: THREE.DoubleSide
                            }});
                            mesh = new THREE.Mesh(boundaryGeometry, material);
                            mesh.position.copy(centroid);
                            mesh.scale.set(scaleX, scaleY, scaleZ);

                            const wireMaterial = new THREE.LineBasicMaterial({{
                                color: color,
                                transparent: true,
                                opacity: wireOpacity
                            }});
                            const edges = new THREE.EdgesGeometry(boundaryGeometry);
                            wireMesh = new THREE.LineSegments(edges, wireMaterial);
                            wireMesh.position.copy(centroid);
                            wireMesh.scale.copy(mesh.scale);
                        }}
                    }}

                    if (!mesh) {{
                        const hull2d = buildHull2D(positions.map(p => new THREE.Vector2(p.x, p.y)));
                        if (!hull2d || hull2d.length < 3) return;
                        const localHull = hull2d.map(p => new THREE.Vector2(p.x - centroid.x, p.y - centroid.y));
                        const shape = new THREE.Shape(localHull);
                        const boundaryGeometry = new THREE.ShapeGeometry(shape);
                        const material = new THREE.MeshBasicMaterial({{
                            color: color,
                            transparent: true,
                            opacity: fillOpacity,
                            wireframe: false,
                            side: THREE.DoubleSide
                        }});
                        mesh = new THREE.Mesh(boundaryGeometry, material);
                        mesh.position.set(centroid.x, centroid.y, centroid.z);
                        mesh.scale.set(scaleX, scaleY, 1);

                        const wireMaterial = new THREE.LineBasicMaterial({{
                            color: color,
                            transparent: true,
                            opacity: wireOpacity
                        }});
                        const wireGeometry = new THREE.BufferGeometry().setFromPoints(
                            localHull.map(p => new THREE.Vector3(p.x, p.y, 0))
                        );
                        wireMesh = new THREE.LineLoop(wireGeometry, wireMaterial);
                        wireMesh.position.copy(mesh.position);
                        wireMesh.scale.copy(mesh.scale);
                    }}
                }} else if (!mesh && hullType === 'box') {{
                    const material = new THREE.MeshBasicMaterial({{
                        color: color,
                        transparent: true,
                        opacity: fillOpacity,
                        wireframe: false,
                        side: THREE.DoubleSide
                    }});
                    if (IS_3D) {{
                        const geometry = new THREE.BoxGeometry(sizeX, sizeY, sizeZ);
                        mesh = new THREE.Mesh(geometry, material);
                        mesh.position.copy(centroid);
                        const wireMaterial = new THREE.LineBasicMaterial({{
                            color: color,
                            transparent: true,
                            opacity: wireOpacity
                        }});
                        const edges = new THREE.EdgesGeometry(geometry);
                        wireMesh = new THREE.LineSegments(edges, wireMaterial);
                        wireMesh.position.copy(mesh.position);
                    }} else {{
                        const geometry = new THREE.PlaneGeometry(sizeX, sizeY);
                        mesh = new THREE.Mesh(geometry, material);
                        mesh.position.set(centroid.x, centroid.y, centroid.z);
                        const wireMaterial = new THREE.LineBasicMaterial({{
                            color: color,
                            transparent: true,
                            opacity: wireOpacity
                        }});
                        const edges = new THREE.EdgesGeometry(geometry);
                        wireMesh = new THREE.LineSegments(edges, wireMaterial);
                        wireMesh.position.copy(mesh.position);
                    }}
                }} else if (!mesh) {{
                    const radius = 0.5 * Math.max(sizeX, sizeY, IS_3D ? sizeZ : 0);
                    const material = new THREE.MeshBasicMaterial({{
                        color: color,
                        transparent: true,
                        opacity: fillOpacity,
                        wireframe: false,
                        side: THREE.DoubleSide
                    }});
                    if (IS_3D) {{
                        const geometry = new THREE.SphereGeometry(radius, 18, 14);
                        mesh = new THREE.Mesh(geometry, material);
                        mesh.position.copy(centroid);
                        const wireMaterial = new THREE.LineBasicMaterial({{
                            color: color,
                            transparent: true,
                            opacity: wireOpacity
                        }});
                        const edges = new THREE.EdgesGeometry(geometry);
                        wireMesh = new THREE.LineSegments(edges, wireMaterial);
                        wireMesh.position.copy(mesh.position);
                    }} else {{
                        const geometry = new THREE.CircleGeometry(radius, 40);
                        mesh = new THREE.Mesh(geometry, material);
                        mesh.position.set(centroid.x, centroid.y, centroid.z);
                        const wireMaterial = new THREE.LineBasicMaterial({{
                            color: color,
                            transparent: true,
                            opacity: wireOpacity
                        }});
                        const edges = new THREE.EdgesGeometry(geometry);
                        wireMesh = new THREE.LineSegments(edges, wireMaterial);
                        wireMesh.position.copy(mesh.position);
                    }}
                }}

                if (!mesh) return;
                scene.add(mesh);
                fileBoundaryMeshes.push(mesh);
                drawn += 1;
                if (wireMesh) {{
                    scene.add(wireMesh);
                    fileBoundaryMeshes.push(wireMesh);
                }}
            }});
            return drawn;
        }}

        // ====================================================================
        // FILE MODE HANDLERS
        // ====================================================================

        // FILES button - toggle file mode on/off
        function setFileModeState(enabled) {{
            fileMode = enabled;
            const btn = document.getElementById('btn-files');
            btn.classList.toggle('active', fileMode);

            const filePanel = document.getElementById('file-panel');
            const modeControls = document.getElementById('file-mode-controls');
            const expandControls = document.getElementById('file-expand-controls');

            if (fileMode) {{
                filePanel.classList.add('visible');
                modeControls.classList.add('visible');
                expandControls.classList.toggle('visible', fileVizMode === 'map');
                applyFileVizMode();
                applyEdgeMode();
                HudLayoutManager.reflow();
            }} else {{
                filePanel.classList.remove('visible');
                modeControls.classList.remove('visible');
                expandControls.classList.remove('visible');
                EXPANDED_FILES.clear();
                GRAPH_MODE = 'atoms';
                HudLayoutManager.reflow();
                clearAllFileModes();
                applyEdgeMode();
                refreshGraph();
            }}
        }}

        document.getElementById('btn-files').onclick = () => {{
            setFileModeState(!fileMode);
        }};

        // COLOR mode - atoms colored by file
        document.getElementById('btn-file-color').onclick = () => {{
            setFileVizMode('color');
        }};

        // HULLS mode - draw boundary spheres
        document.getElementById('btn-file-hulls').onclick = () => {{
            setFileVizMode('hulls');
        }};

        // CLUSTER mode - force clustering by file
        document.getElementById('btn-file-cluster').onclick = () => {{
            setFileVizMode('cluster');
        }};

        // MAP mode - show file nodes
        document.getElementById('btn-file-map').onclick = () => {{
            setFileVizMode('map');
        }};

        // Expand mode toggles (only relevant in MAP mode)
        document.getElementById('btn-expand-inline').onclick = () => {{
            FILE_EXPAND_MODE = 'inline';
            updateExpandButtons();
            if (GRAPH_MODE === 'hybrid') {{
                refreshGraph();
            }}
        }};

        document.getElementById('btn-expand-detach').onclick = () => {{
            FILE_EXPAND_MODE = 'detach';
            updateExpandButtons();
            if (GRAPH_MODE === 'hybrid') {{
                refreshGraph();
            }}
        }};

        function updateExpandButtons() {{
            document.getElementById('btn-expand-inline').classList.toggle('active', FILE_EXPAND_MODE === 'inline');
            document.getElementById('btn-expand-detach').classList.toggle('active', FILE_EXPAND_MODE === 'detach');
        }}

        function setFileVizMode(mode) {{
            fileVizMode = mode;
            // Update button states
            document.querySelectorAll('.file-mode-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('btn-file-' + mode).classList.add('active');
            const expandControls = document.getElementById('file-expand-controls');
            expandControls.classList.toggle('visible', fileVizMode === 'map');
            if (fileVizMode === 'map') {{
                updateExpandButtons();
            }}
            if (fileVizMode === 'map') {{
                GRAPH_MODE = (EXPANDED_FILES.size > 0) ? 'hybrid' : 'files';
            }} else {{
                EXPANDED_FILES.clear();
                GRAPH_MODE = 'atoms';
            }}
            if (!fileMode) {{
                setFileModeState(true);
            }} else if (fileVizMode === 'map') {{
                applyFileVizMode();
            }} else {{
                refreshGraph();
            }}
        }}

        function applyFileVizMode() {{
            if (!fileMode) return;

            // Clear previous state
            clearFileBoundaries();
            if (fileVizMode !== 'hulls') {{
                hullRedrawAttempts = 0;
            }}

            const data = FULL_GRAPH;
            const graphNodes = Graph.graphData().nodes;

            if (fileVizMode === 'color') {{
                // Color mode is already applied via node colors
                // Just ensure nodes have file colors
                applyFileColors(graphNodes);
            }}
            else if (fileVizMode === 'hulls') {{
                // Draw boundary hulls
                applyFileColors(graphNodes);
                const drawn = drawFileBoundaries(data);
                if (drawn === 0) {{
                    showToast('No hulls drawn. Try increasing HULL OPACITY.');
                }}
                scheduleHullRedraw();
            }}
            else if (fileVizMode === 'cluster') {{
                // Apply clustering force
                applyFileColors(graphNodes);
                applyClusterForce(data);
            }}
            else if (fileVizMode === 'map') {{
                // File map uses file nodes + optional expansion
                GRAPH_MODE = (EXPANDED_FILES.size > 0) ? 'hybrid' : 'files';
                refreshGraph();
                showToast('File map active. Click a file node to expand.');
            }}
        }}

        function scheduleHullRedraw(delayMs = 1200) {{
            if (hullRedrawTimer) {{
                clearTimeout(hullRedrawTimer);
            }}
            hullRedrawTimer = setTimeout(() => {{
                if (!(fileMode && fileVizMode === 'hulls')) {{
                    hullRedrawAttempts = 0;
                    return;
                }}
                const drawn = drawFileBoundaries(FULL_GRAPH);
                if (drawn === 0 && hullRedrawAttempts < 3) {{
                    hullRedrawAttempts += 1;
                    scheduleHullRedraw(1200 + (hullRedrawAttempts * 700));
                }} else {{
                    hullRedrawAttempts = 0;
                }}
            }}, delayMs);
        }}

        function applyFileColors(graphNodes) {{
            // Generate file colors and apply to nodes
            const boundaries = FULL_GRAPH.file_boundaries || [];
            const totalFiles = boundaries.length;
            graphNodes.forEach(node => {{
                if (node.fileIdx >= 0) {{
                    const fileInfo = boundaries[node.fileIdx] || {{}};
                    const fileLabel = fileInfo.file || fileInfo.file_name || node.fileIdx;
                    node.color = getFileColor(node.fileIdx, totalFiles, fileLabel);
                }}
            }});
            Graph.nodeColor(n => toColorNumber(n.color, 0x888888));
        }}

        function clearFileBoundaries() {{
            const scene = Graph.scene();
            fileBoundaryMeshes.forEach(mesh => scene.remove(mesh));
            fileBoundaryMeshes = [];
        }}

        function clearAllFileModes() {{
            clearFileBoundaries();
            // Reset cluster force if active
            if (clusterForceActive) {{
                Graph.d3Force('cluster', null);
                clusterForceActive = false;
                if (DEFAULT_LINK_DISTANCE !== null) {{
                    Graph.d3Force('link').distance(DEFAULT_LINK_DISTANCE);
                }}
                Graph.d3ReheatSimulation();
            }}
        }}

        function applyClusterForce(data) {{
            // TOKEN-DRIVEN: Get cluster config from physics
            const clusterConfig = data.physics?.cluster || {{}};
            const modeStrength =
                (typeof clusterConfig.modes?.strong === 'number') ? clusterConfig.modes.strong : null;
            const sliderStrength =
                (typeof APPEARANCE_STATE.clusterStrength === 'number') ? APPEARANCE_STATE.clusterStrength : null;
            const clusterStrength =
                (typeof sliderStrength === 'number')
                    ? sliderStrength
                    : ((typeof modeStrength === 'number')
                        ? modeStrength
                        : ((typeof clusterConfig.strength === 'number') ? clusterConfig.strength : 0.3));
            const clusterRadius =
                (typeof clusterConfig.radius === 'number') ? clusterConfig.radius : 150;
            const clusterZSpacing =
                (typeof clusterConfig.zSpacing === 'number') ? clusterConfig.zSpacing : 30;
            const linkDistance =
                (typeof clusterConfig.linkDistance === 'number')
                    ? clusterConfig.linkDistance
                    : (data.physics?.forces?.link?.distance || 50);

            const graphNodes = Graph.graphData().nodes;
            const boundaries = data.file_boundaries || [];
            const numFiles = boundaries.length;

            // FIXED TARGET POSITIONS: Arrange files in a circular pattern
            // This creates CLEAR visual separation instead of clustering around mixed centroids
            const radius = clusterRadius;  // Separation radius
            const fileTargets = {{}};

            for (let i = 0; i < numFiles; i++) {{
                fileTargets[i] = getFileTarget(i, numFiles, radius, clusterZSpacing);
            }}

            // Reduce link distance to keep intra-file nodes tighter
            Graph.d3Force('link').distance(linkDistance);

            // Apply strong clustering force toward fixed targets
            Graph.d3Force('cluster', (alpha) => {{
                const k = alpha * clusterStrength;
                graphNodes.forEach(node => {{
                    const target = fileTargets[node.fileIdx];
                    if (target) {{
                        node.vx = (node.vx || 0) + (target.x - node.x) * k;
                        node.vy = (node.vy || 0) + (target.y - node.y) * k;
                        if (IS_3D) {{
                            node.vz = (node.vz || 0) + (target.z - node.z) * k;
                        }}
                    }}
                }});
            }});

            clusterForceActive = true;
            Graph.d3ReheatSimulation();

            // Also draw hulls after clustering settles
            scheduleHullRedraw(1500);
        }}
    </script>
</body>
</html>
    """
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"Universe generated at {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collider WebGL Generator")
    parser.add_argument("input_json", help="Path to LLM-oriented output JSON")
    parser.add_argument("output_html", help="Path to output HTML")
    args = parser.parse_args()
    
    generate_webgl_html(args.input_json, args.output_html)
