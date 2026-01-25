import json
import sys
import os
import argparse
import gzip
import base64
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.core.viz import AppearanceEngine, ControlsEngine, PhysicsEngine, get_resolver
    # FileEnricher is used in full_analysis.py, not here (already enriched in JSON)
except ImportError:
    # Fallback if running from a different context or if imports fail
    print("WARNING: Could not import core engines. Ensure you are running from the project root.")
    sys.exit(1)

def generate_webgl_html(json_source: Any, output_path: str):
    """
    Generates a standalone WebGL visualization HTML file.

    Args:
        json_source: Path to the input JSON file or the data dict itself.
        output_path: Path where the output HTML file will be written.
    """
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

    # METADATA
    version = meta.get('version') or data.get('collider_version') or data.get('version', 'V3-Tokens')
    target_path = meta.get('target') or data.get('target_path') or data.get('target', 'Unknown')
    # target_folder = Path(target_path).name if target_path and target_path != 'Unknown' else 'Unknown'
    # timestamp = meta.get('timestamp') or data.get('timestamp', datetime.now().isoformat())

    print(f"Processing {len(nodes)} nodes and {len(edges)} edges...")

    # DEGREE ENRICHMENT
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

    # FILE BOUNDARIES
    file_boundaries = data.get('file_boundaries', []) or []
    files_index = data.get('files', {}) or {}

    # Fallback synthesis if missing
    if not file_boundaries:
        synthesized_index: Dict[str, Dict[str, Any]] = {}
        node_id_to_file_map: Dict[str, str] = {}
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
                node_id_to_file_map[node_id] = file_path

        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            src_file = node_id_to_file_map.get(src)
            tgt_file = node_id_to_file_map.get(tgt)
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

    # NOTE: File boundaries are already enriched in full_analysis.py
    # The JSON source contains: size_bytes, token_estimate, age_days, format_category, etc.

    # Create mappings (support absolute + relative file paths)
    node_to_file = {}
    file_to_index = {}
    root_path = None
    if target_path and target_path != 'Unknown':
        try:
            root_path = Path(target_path).resolve()
        except Exception:
            root_path = Path(target_path)

    def _rel_path(path_str: str) -> Optional[str]:
        if not path_str or not root_path:
            return None
        try:
            return str(Path(path_str).resolve().relative_to(root_path))
        except Exception:
            return None

    for idx, boundary in enumerate(file_boundaries):
        file_path = boundary.get('file', '')
        if file_path:
            file_to_index[file_path] = idx
            rel_path = _rel_path(file_path)
            if rel_path:
                file_to_index.setdefault(rel_path, idx)
        file_info = files_index.get(file_path, {})
        for atom_name in file_info.get('atom_names', []):
            node_to_file[atom_name] = idx

    print(f"File boundaries: {len(file_boundaries)} files")

    def _normalize_ring(value: Any) -> Optional[str]:
        if value is None:
            return None
        ring = str(value).strip().upper()
        if not ring:
            return None
        aliases = {
            "TEST": "TESTING"
        }
        return aliases.get(ring, ring)

    def _node_ring(node: Dict[str, Any]) -> str:
        ring = node.get("ring") or node.get("layer") or "UNKNOWN"
        normalized = _normalize_ring(ring)
        return normalized or "UNKNOWN"

    def _node_family(node: Dict[str, Any]) -> str:
        atom_family = node.get("atom_family")
        if atom_family:
            return str(atom_family).strip().upper()
        atom_id = str(node.get("atom") or "")
        if "." in atom_id:
            return atom_id.split(".", 1)[0].upper()
        return "UNKNOWN"

    available_rings = sorted({_node_ring(n) for n in nodes})
    available_families = sorted({_node_family(n) for n in nodes})
    strict_defaults = os.getenv("STRICT_DEFAULTS") == "1"

    # TOKEN CONFIG
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
    flow_presets_config = appearance.get_flow_presets_config()
    animation_config = appearance.get_animation_config()
    controls_config = controls.to_js_config(
        available_rings=available_rings,
        available_families=available_families,
        strict=strict_defaults
    )

    filters_config = controls_config.get("filters") or {}
    controls_config["filters"] = filters_config

    ring_defaults = list(filters_config.get("rings", []))
    invalid_rings = sorted(set(ring_defaults) - set(available_rings))
    if invalid_rings:
        msg = f"[Controls] invalid ring defaults in payload: {invalid_rings}"
        if strict_defaults:
            raise ValueError(msg)
        print(msg)
        filters_config["rings"] = [r for r in ring_defaults if r in available_rings]

    family_defaults = list(filters_config.get("families", []))
    invalid_families = sorted(set(family_defaults) - set(available_families))
    if invalid_families:
        msg = f"[Controls] invalid family defaults in payload: {invalid_families}"
        if strict_defaults:
            raise ValueError(msg)
        print(msg)
        filters_config["families"] = [f for f in family_defaults if f in available_families]

    # KPI CALCULATION
    kpis = data.get("kpis", {})
    if not kpis:
        stats = data.get("stats", {})
        arch = data.get("architecture", {})
        graph_inf = arch.get("graph_inference", {})
        import_res = stats.get("import_resolution", {})

        resolved = import_res.get("resolved", 0)
        unresolved = import_res.get("unresolved", 0)
        total_imports = resolved + unresolved
        edge_res_pct = (resolved / total_imports * 100) if total_imports > 0 else None

        call_edges = sum(1 for e in edges if e.get("type") == "calls")
        call_ratio_pct = (call_edges / len(edges) * 100) if edges else None

        orphan_count = sum(1 for n in nodes if n.get("in_degree", 0) == 0 and n.get("out_degree", 0) == 0)
        top_hub_count = sum(1 for n in nodes if (n.get("in_degree", 0) + n.get("out_degree", 0)) > 10)

        kpis = {
            "edge_resolution_percent": edge_res_pct,
            "call_ratio_percent": call_ratio_pct,
            "reachability_percent": stats.get("coverage_percentage"),
            "dead_code_percent": stats.get("unknown_percentage"),
            "knot_score": graph_inf.get("knot_score"),
            "topology_shape": graph_inf.get("topology_class", "UNKNOWN"),
            "orphan_count": orphan_count,
            "top_hub_count": top_hub_count
        }

    # BUILD GRAPH DATA (including ALL analytics for DataManager)
    graph_data = {
        "nodes": [],
        "links": [],
        "file_boundaries": file_boundaries,
        "kpis": kpis,
        "meta": meta,
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
            "flow_mode": flow_mode_config,
            "flow-presets": flow_presets_config,
            "animation": animation_config
        },
        "controls": controls_config,

        # ═══════════════════════════════════════════════════════════════════
        # ALL ANALYTICS DATA (for DataManager single-gate architecture)
        # ═══════════════════════════════════════════════════════════════════

        # Structural metrics
        "counts": data.get("counts", {}),
        "stats": data.get("stats", {}),
        "coverage": data.get("coverage", {}),
        "performance": data.get("performance", {}),

        # Classification & discovery
        "classification": data.get("classification", {}),
        "auto_discovery": data.get("auto_discovery", {}),
        "ecosystem_discovery": data.get("ecosystem_discovery", {}),

        # Architecture & dependencies
        "dependencies": data.get("dependencies", {}),
        "architecture": data.get("architecture", {}),
        "topology": data.get("topology", {}),

        # Flow analysis
        "execution_flow": data.get("execution_flow", {}),
        "data_flow": data.get("data_flow", {}),
        "markov": data.get("markov", {}),
        "knots": data.get("knots", {}),
        "analytics": data.get("analytics", {}),

        # Health & recommendations
        "warnings": data.get("warnings", []),
        "recommendations": data.get("recommendations", []),
        "theory_completeness": data.get("theory_completeness", {}),

        # Distributions
        "distributions": data.get("distributions", {}),
        "edge_types": data.get("edge_types", {}),

        # RPBL profile
        "rpbl_profile": data.get("rpbl_profile", {}),
        "purpose_field": data.get("purpose_field", {}),

        # Special nodes
        "top_hubs": data.get("top_hubs", []),
        "orphans_list": data.get("orphans_list", []),

        # Files
        "files": data.get("files", []),

        # Semantic analysis
        "semantics": data.get("semantics", {}),
        "llm_enrichment": data.get("llm_enrichment", {}),

        # Brain download (the full report)
        "brain_download": data.get("brain_download", ""),

        # AI Insights (Gemini-powered analysis)
        "ai_insights": data.get("ai_insights", None),

        # Graph Analytics (PageRank, Betweenness, Communities)
        "graph_analytics": data.get("graph_analytics", {}),

        # Statistical Metrics (Entropy, Cyclomatic, Halstead)
        "statistical_metrics": data.get("statistical_metrics", {}),

        # Theme configuration for runtime switching
        "theme_config": resolver.get_js_theme_config()
    }

    # NODE PROCESSING
    nodes_with_appearance = appearance.apply_to_nodes(nodes, file_boundaries, color_mode="tier")
    node_id_counts = {}
    canonical_id_map = {}

    def normalize_node_id(node, index):
        raw_id = node.get('id') or node.get('atom_id')
        if not raw_id:
            file_path = node.get('file_path') or node.get('file') or 'unknown'
            name = node.get('name') or node.get('symbol') or node.get('kind') or 'node'
            start_line = node.get('start_line') or node.get('line') or index
            raw_id = f"{file_path}::{name}:{start_line}"

        base_id = str(raw_id).strip() or f"node:{index}"
        count = node_id_counts.get(base_id, 0) + 1
        node_id_counts[base_id] = count
        if count == 1:
            canonical_id_map[base_id] = base_id
            return base_id
        return f"{base_id}#{count}"

    node_set = set()
    for idx, n in enumerate(nodes_with_appearance):
        nid = normalize_node_id(n, idx)
        file_path = n.get('file_path', '') or n.get('file', '')
        file_idx = file_to_index.get(file_path, -1)
        if file_idx < 0 and file_path:
            rel_guess = _rel_path(file_path)
            if rel_guess:
                file_idx = file_to_index.get(rel_guess, -1)
        if file_idx < 0 and root_path and file_path:
            try:
                abs_path = str((root_path / file_path).resolve())
                file_idx = file_to_index.get(abs_path, -1)
            except Exception:
                pass

        graph_data['nodes'].append({
            "id": nid,
            "name": n.get('name', nid),
            "atom": n.get('atom') or n.get('atom_id') or 'UNK',
            "val": n.get('size', 1.0),
            "color": n.get('color', '#888888'),
            "layer": n.get('layer', 'Unknown'),
            "ring": n.get('ring') or n.get('layer') or 'Unknown',
            "role": n.get('role') or (n.get('dimensions') or {}).get('D3_ROLE', 'Unknown'),
            "file": file_path,
            "fileIdx": file_idx,
            "body": n.get('body_source', '')[:500],
            # New octahedral dimensions
            "boundary": n.get('boundary', 'internal'),
            "state": n.get('state', 'stateless'),
            "lifecycle": n.get('lifecycle', 'use'),
            # ═══ CODOME BOUNDARY NODES (external callers) ═══
            "is_codome_boundary": n.get('is_codome_boundary', False),
            "kind": n.get('kind'),
            "codome_source": n.get('codome_source'),
            "color_hint": n.get('color_hint'),
            # ═══ METRIC FIELDS (required for interval color modes) ═══
            "in_degree": n.get('in_degree', 0),
            "out_degree": n.get('out_degree', 0),
            "fan_in": n.get('in_degree', 0),   # Alias for in_degree
            "fan_out": n.get('fan_out') or n.get('out_degree', 0),
            "complexity": n.get('complexity') or n.get('cyclomatic_complexity', 0),
            "loc": n.get('loc') or n.get('lines_of_code') or n.get('end_line', 0) - n.get('start_line', 0),
            "trust": n.get('trust') or n.get('confidence', 1.0),
            # RPBL DNA scores
            "responsibility": n.get('responsibility', 5),
            "purity": n.get('purity', 5),
            "lifecycle_score": n.get('lifecycle_score', 5),
            "boundary_score": n.get('boundary_score', 5),
            # Topology metrics
            "centrality": n.get('centrality', 0),
            "rank": n.get('rank') or n.get('pagerank', 0),
            "depth": n.get('depth') or n.get('call_depth', 0),
            # Evolution metrics
            "churn": n.get('churn', 0),
            "age": n.get('age', 0)
        })
        node_set.add(nid)

    # EDGE PROCESSING
    def normalize_edge_endpoint(value):
        if isinstance(value, dict):
            value = value.get('id')
        if value is None:
            return None
        key = str(value).strip()
        if not key:
            return None
        return canonical_id_map.get(key, key)

    edges_with_appearance = appearance.apply_to_edges(edges)
    default_edge_opacity = resolver.appearance("color.edge-modes.opacity", 0.2)

    for e in edges_with_appearance:
        src = normalize_edge_endpoint(e.get('source'))
        tgt = normalize_edge_endpoint(e.get('target'))

        if src in node_set and tgt in node_set:
            raw_markov = e.get('markov_weight', 0.0)
            try:
                markov = float(raw_markov) if raw_markov is not None else 0.0
            except (TypeError, ValueError):
                markov = 0.0

            graph_data['links'].append({
                "source": src,
                "target": tgt,
                "color": e.get('color', '#333333'),
                "opacity": e.get('opacity', default_edge_opacity),
                "edge_type": e.get('edge_type', e.get('type', 'default')),
                "weight": e.get('weight', 1.0),
                "markov_weight": markov,
                "confidence": e.get('confidence', 1.0),
                "resolution": e.get('resolution', 'unknown')
            })

    # PAYLOAD ENCODING
    print("optimizing payload (GZIP)...")
    json_bytes = json.dumps(graph_data).encode('utf-8')
    compressed = gzip.compress(json_bytes)
    b64_payload = base64.b64encode(compressed).decode('utf-8')

    print(f"Original: {len(json_bytes)/1024/1024:.2f} MB")
    print(f"Compressed: {len(compressed)/1024/1024:.2f} MB")

    # ASSET LOADING
    viz_assets = Path(__file__).parent.parent / "src/core/viz/assets"

    # MODULE ORDER: Load modules before app.js in dependency order
    # Foundation modules first (no dependencies), then dependent modules
    MODULE_ORDER = [
        "performance.js",                   # Performance subsystem (existing)
        "modules/utils.js",                 # Pure utility functions (zero deps)
        "modules/event-bus.js",             # Pub/sub for decoupled communication (zero deps)
        "modules/registry.js",              # Command/element registry (zero deps)
        "modules/perf-monitor.js",          # FPS/frame monitoring (zero deps)
        "modules/core.js",                  # Constants & utilities
        "modules/theory.js",                # SMC theory constants (zero deps)
        "modules/node-accessors.js",        # Node property functions
        "modules/node-helpers.js",          # Node classification & colors (Phase 1)
        "modules/color-helpers.js",         # Color utilities (Phase 1)
        "modules/color-telemetry.js",       # OKLCH observability (must load before color-engine)
        "modules/color-engine.js",          # OKLCH color system
        "modules/refresh-throttle.js",      # Throttled graph updates
        "modules/legend-manager.js",        # Legend system (depends: COLOR, NODE)
        "modules/data-manager.js",          # Data access layer (depends: NODE, COLOR, LEGEND)
        "modules/vis-state.js",             # Unified visualization state (depends: COLOR)
        "modules/ui-manager.js",            # UI orchestration (depends: vis-state, data-manager)
        "modules/physics.js",               # Force simulation controls (Phase 1)
        "modules/datamap.js",               # Data mapping & filtering (Phase 1)
        "modules/groups.js",                # Node grouping (Phase 1)
        "modules/hover.js",                 # Hover interactions (Phase 1)
        "modules/flow.js",                  # Flow visualization mode (Phase 2)
        "modules/ui-builders.js",           # DOM element builders (Phase 2)
        "modules/layout-helpers.js",        # Layout stability functions (Phase 2)
        "modules/spatial.js",               # Spatial algorithms (Phase 2)
        "modules/layout.js",                # UI Layout Engine (foundational)
        # stars.js REMOVED - nodes ARE the stars (archived to archive/removed_features/)
        "modules/hud.js",                   # HUD stats & fade (Phase 3)
        "modules/dimension.js",             # 2D/3D toggle animation (Phase 3)
        "modules/report.js",                # Report, AI insights, metrics (Phase 3)
        "modules/visibility.js",            # UI visibility controls (Phase 3)
        "modules/animation.js",             # Layout & animation controller
        "modules/selection.js",             # Selection system (depends: CORE, NODE)
        "modules/panels.js",                # Panel management
        "modules/sidebar.js",               # Sidebar controls
        "modules/filter-state.js",          # Centralized filter state (depends: Graph, EVENT_BUS)
        "modules/panel-system.js",          # Gridstack panel management (depends: EVENT_BUS)
        "modules/panel-handlers.js",        # Panel control bindings (depends: FILTER_STATE, PANEL_SYSTEM)
        "modules/edge-system.js",           # Edge coloring & modes
        "modules/file-color-model.js",       # Pure color generation (zero deps)
        "modules/layout-forces.js",          # D3 force manipulation (takes graph as arg)
        "modules/hull-visualizer.js",        # SDF-based organic membranes
        "modules/file-viz.js",              # File visualization controller (thin orchestrator)
        "modules/tooltips.js",              # Tooltip & toast notifications
        "modules/theme.js",                 # Theme management (needs toast)
        # UPB Module (Universal Property Binder) - BEFORE control-bar.js
        "modules/upb/scales.js",            # Scale functions (no deps)
        "modules/upb/endpoints.js",         # Source/target schemas (no deps)
        "modules/upb/blenders.js",          # Blend modes (no deps)
        "modules/upb/bindings.js",          # Binding graph (needs scales, endpoints)
        "modules/upb/index.js",             # Public API (needs all above)
        # Property Query System - unified property resolution
        "modules/vis-schema.js",            # Visual property schema (no deps)
        "modules/upb-defaults.js",          # Default UPB bindings (no deps)
        "modules/property-query.js",        # Core resolution engine (needs schema)
        "modules/property-query-init.js",   # Initialize & wire PQ (needs all above)
        "modules/control-bar.js",           # Visual mapping command bar (uses UPB)
        "modules/main.js",                  # Entry point + wiring
        "modules/circuit-breaker.js",       # UI control self-test (run with CIRCUIT.runAll())
        "modules/color-contract-test.js",   # COLOR engine contract tests (run with COLOR_TEST.runAll())
    ]

    print(f"Loading assets from {viz_assets}...")
    try:
        with open(viz_assets / "template.html", "r", encoding='utf-8') as f:
            template = f.read()
        with open(viz_assets / "styles.css", "r", encoding='utf-8') as f:
            styles = f.read()

        # Load modules in order and concatenate
        js_parts = []
        for module_path in MODULE_ORDER:
            module_file = viz_assets / module_path
            if module_file.exists():
                with open(module_file, "r", encoding='utf-8') as f:
                    js_parts.append(f"// ═══ MODULE: {module_path} ═══\n{f.read()}")
                print(f"  Loaded module: {module_path}")
            else:
                print(f"  Skipped module (not found): {module_path}")

        # Load app.js (the main application, will shrink as we migrate)
        with open(viz_assets / "app.js", "r", encoding='utf-8') as f:
            js_parts.append(f"// ═══ MAIN APPLICATION ═══\n{f.read()}")

        app_js = "\n\n".join(js_parts)
        print(f"  Total JS modules loaded: {len(js_parts)}")

    except FileNotFoundError as e:
        print(f"CRITICAL ERROR: Could not find asset file: {e}")
        print("Please ensure src/core/viz/assets contains template.html, styles.css, and app.js")
        return

    # INJECT CSS VARIABLES FROM TOKENS (with multi-theme support)
    # resolver is already available from the top-level import
    css_variables = resolver.generate_all_themes_css(include=["theme", "layout"])
    if css_variables:
        styles = f"/* === DESIGN TOKENS (auto-generated) === */\n{css_variables}\n\n/* === COMPONENT STYLES === */\n{styles}"

    # Get theme config for JS injection
    theme_config = resolver.get_js_theme_config()

    # INJECTION
    print("Generating HTML...")

    # Unescape Python f-string escaping in app.js:
    # - {{ }} → { } (double braces to single)
    # - \\\\ → \\ (double backslashes to single, for regex patterns)
    # Do this BEFORE injecting into template
    app_js_unescaped = app_js.replace("{{", "{").replace("}}", "}")
    app_js_unescaped = app_js_unescaped.replace("\\\\", "\\")
    # Replace the PAYLOAD placeholder in app.js with the actual payload
    app_js_unescaped = app_js_unescaped.replace('"{PAYLOAD}"', f'"{b64_payload}"')

    # MANGLED PLACEHOLDER FIX: Template has split braces
    mangled_styles = """            {
                {
                STYLES
            }
        }"""
    html_content = template.replace(mangled_styles, styles)
    html_content = html_content.replace("{{STYLES}}", styles)
    html_content = html_content.replace("{ { APP_JS } }", app_js_unescaped)
    html_content = html_content.replace("{{APP_JS}}", app_js_unescaped)
    html_content = html_content.replace("{{VERSION}}", str(version))
    # Note: {{PAYLOAD}} in template is already replaced via app_js_unescaped

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Universe generated at {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collider WebGL Generator")
    parser.add_argument("input_json", help="Path to LLM-oriented output JSON")
    parser.add_argument("output_html", help="Path to output HTML")
    args = parser.parse_args()

    generate_webgl_html(args.input_json, args.output_html)
