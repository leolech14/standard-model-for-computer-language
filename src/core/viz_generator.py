
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class VisualizationGenerator:
    """
    Generates interactive HTML visualizations for Spectrometer graphs.
    """

    def __init__(self, template_path: str = "demos/collider_viz.html"):
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            # Fallback to looking in source root if not found
            self.template_path = Path(__file__).parent.parent / "collider_viz.html"

    def generate(self, graph_path: str | Path, output_path: str | Path):
        """
        Generate HTML visualization from a graph.json file.
        """
        graph_path = Path(graph_path)
        output_path = Path(output_path)
        
        if not graph_path.exists():
            raise FileNotFoundError(f"Graph file not found: {graph_path}")

        logger.info(f"Loading graph from {graph_path}")
        with open(graph_path, 'r') as f:
            graph_data = json.load(f)

        # Process Data
        particles, connections = self._process_graph(graph_data)
        
        node_count = len(particles)
        edge_count = len(connections)
        logger.info(f"Processed {node_count} nodes and {edge_count} edges.")

        # Load Template
        if not self.template_path.exists():
             raise FileNotFoundError(f"Template not found at {self.template_path}")
             
        with open(self.template_path, 'r') as f:
            html = f.read()

        # Inject Data
        html = self._inject_data(html, particles, connections)

        # Optimize for Graph Size
        html = self._apply_optimizations(html, node_count)

        # Write Output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html)
        
        logger.info(f"Visualization saved to {output_path}")
        return output_path

    def _process_graph(self, graph_data: Dict[str, Any]):
        """
        Convert Spectrometer graph format (UnifiedAnalysisOutput) to Vis.js format.
        Now expects 'nodes' list from CodebaseState export.
        """
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        # Legacy fallback: 'components' dict
        if not nodes and "components" in graph_data:
            components = graph_data["components"]
            if isinstance(components, dict):
                nodes = list(components.values())
            elif isinstance(components, list):
                nodes = components

        # 1. Particles (Nodes)
        particles = []
        valid_ids = set()
        
        for node in nodes:
            # Flexible ID/Name handling
            nid = node.get("id")
            if not nid: continue
            
            # Use pre-calculated attributes from CodebaseState
            layer = node.get("layer", "App")
            role = node.get("role", "Worker")
            
            # Normalize layer case if needed
            if hasattr(layer, "capitalize"):
                layer = layer.capitalize()
                
            particles.append({
                "id": nid,
                "label": node.get("name", nid[:20]),
                "layer": layer,
                "role": role,
                "file": node.get("file_path", node.get("file", "")),
                "startLine": node.get("start_line", 0),
                "endLine": node.get("end_line", 0),
                # Visual attributes
                "complexity": node.get("complexity", 1),
                "kind": node.get("kind", "class"),
                # Pass through enrichment data
                "is_hotspot": node.get("is_hotspot", False),
                "is_orphan": node.get("is_orphan", False),
                "description": node.get("docstring", "")[:200],
                "intelligence": node.get("metadata", {}).get("intelligence", None)
            })
            valid_ids.add(nid)

        # 2. Connections (Edges)
        connection_list = []
        name_to_id = {p["label"]: p["id"] for p in particles}

        for e in edges:
            src = e.get("source") or e.get("from")
            dst = e.get("target") or e.get("to")
            
            # Resolve IDs
            final_src = src if src in valid_ids else name_to_id.get(src)
            final_dst = dst if dst in valid_ids else name_to_id.get(dst)
            
            if final_src and final_dst:
                connection_list.append({
                    "from": final_src,
                    "to": final_dst,
                    "type": (e.get("edge_type") or e.get("type", "CALLS")).upper()
                })

        return particles, connection_list

    def _inject_data(self, html: str, particles: List[Dict], connections: List[Dict]) -> str:
        """Inject JSON data into the HTML template using strict markers."""
        
        # Prepare JSON with HTML safety
        def safe_json_dumps(obj):
            return json.dumps(obj).replace('<', '\\u003c').replace('>', '\\u003e').replace('/', '\\u002f')
            
        particles_json = safe_json_dumps(particles)
        connections_json = safe_json_dumps(connections)
        
        # Injection Block
        injection_block = f"""
        /* <!-- DATA_INJECTION_START --> */
        const particles = {particles_json};
        const connections = {connections_json};
        
        // IDE: Source Map & File Tree
        const sourceMap = {self._generate_source_map(particles, None)};
        const fileTree = {self._generate_file_tree(particles)};
        /* <!-- DATA_INJECTION_END --> */
        """
        
        # Find Markers
        start_marker = "/* <!-- DATA_INJECTION_START --> */"
        end_marker = "/* <!-- DATA_INJECTION_END --> */"
        
        start_idx = html.find(start_marker)
        end_idx = html.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            logger.warning("Injection markers not found in template! Using naive replacement.")
            # Fallback to simple variable replacement if markers missing (legacy support)
            import re
            html = re.sub(r"const particles = \[.*?\];", f"const particles = {particles_json};", html, flags=re.DOTALL)
            html = re.sub(r"const connections = \[.*?\];", f"const connections = {connections_json};", html, flags=re.DOTALL)
            return html

        # Robust Replacement
        # We replace everything from start_marker to end_marker (inclusive of end marker)
        # with our new block.
        
        pre = html[:start_idx]
        post = html[end_idx + len(end_marker):]
        
        return pre + injection_block + post

    def _apply_optimizations(self, html: str, node_count: int) -> str:
        """Enable physics only for small graphs."""
        
        if node_count < 2000:
            # Enable physics for small graphs
            html = html.replace("let physicsEnabled = false;", "let physicsEnabled = true;")
            logger.info("Small graph detected: Enabled physics.")
        else:
            logger.info(f"Large graph ({node_count} nodes): Physics remain disabled.")
        
        # Inject concept images
        html = self._inject_concept_images(html)
            
        return html

    def _inject_concept_images(self, html: str) -> str:
        """Inject concept images as base64 data URIs for tooltip display."""
        import base64
        
        # Find assets folder relative to template
        assets_path = self.template_path.parent / "assets"
        
        concept_files = {
            "god_class": "concept_god_class.jpg",
            "coupling": "concept_coupling.jpg",
            "layer_violation": "concept_layer_violation.jpg",
            "clustering": "concept_clustering.jpg",
            "orphan": "concept_orphan.jpg"
        }
        
        concept_data = {}
        for concept, filename in concept_files.items():
            img_path = assets_path / filename
            if img_path.exists():
                with open(img_path, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                    concept_data[concept] = f"data:image/jpeg;base64,{encoded}"
                logger.info(f"Embedded concept image: {concept}")
            else:
                concept_data[concept] = "null"
                logger.warning(f"Concept image not found: {img_path}")
        
        # Build replacement block
        replacement_block = "// ___CONCEPT_IMAGES_START___\n"
        entries = []
        for concept, data_uri in concept_data.items():
            if data_uri == "null":
                entries.append(f'            {concept}: null')
            else:
                entries.append(f'            {concept}: "{data_uri}"')
        replacement_block += ",\n".join(entries)
        replacement_block += "\n            // ___CONCEPT_IMAGES_END___"
        
        # Find and replace the marker section
        start_marker = "// ___CONCEPT_IMAGES_START___"
        end_marker = "// ___CONCEPT_IMAGES_END___"
        
        start_idx = html.find(start_marker)
        end_idx = html.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            pre = html[:start_idx]
            post = html[end_idx + len(end_marker):]
            html = pre + replacement_block + post
            logger.info("Injected concept images into template.")
        else:
            logger.warning("Concept image markers not found in template.")
        
        return html

    def _generate_source_map(self, particles: List[Dict], repo_path: str = None) -> str:
        """Generate a source map for files in the graph."""
        import os
        source_map = {}
        
        # Limit total source map size to avoid crashing browser (e.g. 5MB)
        MAX_SIZE = 5 * 1024 * 1024 
        current_size = 0
        
        # Collect unique file paths
        files = {p.get("file") for p in particles if p.get("file")}
        
        for file_path in files:
            # Resolve absolute path
            abs_path = file_path
            if repo_path and not file_path.startswith('/'):
               abs_path = os.path.join(repo_path, file_path)
               
            if os.path.exists(abs_path) and os.path.isfile(abs_path):
                try:
                    with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Simple truncation for very large individual files
                        if len(content) > 50000:
                             content = content[:50000] + "\\n... (truncated)"
                        
                        source_map[file_path] = content
                        current_size += len(content)
                        
                        if current_size > MAX_SIZE:
                            break
                except Exception as e:
                    logger.warning(f"Failed to read source for map: {abs_path} - {e}")
                    
        return json.dumps(source_map)

    def _generate_file_tree(self, particles: List[Dict]) -> str:
        """Generate a hierarchical file tree structure from particles."""
        import json
        tree = []
        files = {p.get("file") for p in particles if p.get("file")}
        
        # Build tree structure
        # Use a simple list of paths for now, frontend converts to tree?
        # Or build a recursive structure here.
        # Let's matching the expected 'nodes' format in renderTree:
        # [{name, type: 'folder'|'file', path, children: []}, ...]
        
        def add_to_tree(path_parts, current_level, full_path):
            if not path_parts:
                return

            name = path_parts[0]
            is_file = len(path_parts) == 1
            type_ = 'file' if is_file else 'folder'
            
            existing = next((item for item in current_level if item['name'] == name), None)
            
            if not existing:
                existing = {
                    'name': name,
                    'type': type_,
                    'path': full_path if is_file else None, # Only files usually have openable paths
                    'children': []
                }
                current_level.append(existing)
            
            if not is_file:
                add_to_tree(path_parts[1:], existing['children'], full_path)
                
        for f in files:
            parts = f.split('/')
            # Filter out empty parts
            parts = [p for p in parts if p]
            add_to_tree(parts, tree, f)
            
        return json.dumps(tree)
