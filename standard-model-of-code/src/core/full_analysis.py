#!/usr/bin/env python3
"""
Collider Full Analysis
Single command for complete deterministic analysis with all theoretical frameworks.

Usage:
    ./collider full <path> [--output <dir>]

Outputs:
    - output_llm-oriented_<project>_<timestamp>.json (LLM knowledge bundle)
    - output_human-readable_<project>_<timestamp>.html (human report + graph)
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional

from src.core.file_enricher import FileEnricher


# =============================================================================
# DISCONNECTION TAXONOMY: Rich classification of why nodes appear disconnected
# Replaces lazy "orphan" label with 7-type taxonomy (see ORPHAN_TAXONOMY.md)
# =============================================================================

def classify_disconnection(node: Dict[str, Any], in_deg: int, out_deg: int) -> Optional[Dict[str, Any]]:
    """
    Classify WHY a node appears disconnected in the dependency graph.

    Returns None if node is not disconnected (has both incoming and outgoing edges).
    Returns a dict with:
        - reachability_source: Why this node exists without standard edges
        - connection_gap: What kind of disconnection (isolated, no_incoming, no_outgoing)
        - isolation_confidence: How confident we are in this classification (0.0-1.0)
        - suggested_action: What to do about it (OK, CHECK, DELETE)

    This replaces the misleading "orphan" classification which conflated 7+ phenomena.
    """
    # Not disconnected - has both incoming and outgoing
    if in_deg > 0 and out_deg > 0:
        return None

    # Determine connection gap type
    if in_deg == 0 and out_deg == 0:
        connection_gap = 'isolated'
    elif in_deg == 0:
        connection_gap = 'no_incoming'
    else:
        connection_gap = 'no_outgoing'

    file_path = node.get('file_path', '')
    name = node.get('name', '')
    kind = node.get('kind', '')
    decorators = node.get('decorators', [])

    # Normalize file_path for pattern matching
    file_lower = file_path.lower()
    name_lower = name.lower()

    # 1. Test file detection (pytest, jest, unittest)
    if any(pattern in file_lower for pattern in ['test_', '_test.', '/tests/', 'conftest', 'spec.js', '.test.', '.spec.']):
        return {
            'reachability_source': 'test_entry',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.95,
            'suggested_action': 'OK - test framework invokes'
        }

    # 2. Entry point detection (__main__, CLI, scripts)
    if any([
        name_lower == 'main',
        name_lower == '__main__',
        'if __name__' in node.get('body_source', ''),
        kind == 'script',
        file_lower.endswith('cli.py'),
        file_lower.endswith('__main__.py'),
    ]):
        return {
            'reachability_source': 'entry_point',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.99,
            'suggested_action': 'OK - program entry point'
        }

    # 3. Framework-managed detection (decorators, dataclasses)
    framework_decorators = ['@dataclass', '@component', '@injectable', '@service', '@controller',
                           '@app.route', '@pytest.fixture', '@staticmethod', '@classmethod',
                           '@property', '@abstractmethod', '@override']
    if decorators:
        decorator_str = ' '.join(str(d).lower() for d in decorators)
        if any(fd.lower().lstrip('@') in decorator_str for fd in framework_decorators):
            return {
                'reachability_source': 'framework_managed',
                'connection_gap': connection_gap,
                'isolation_confidence': 0.90,
                'suggested_action': 'OK - framework instantiates'
            }

    # Also check for dataclass-like patterns in kind
    if kind in ['dataclass', 'namedtuple', 'TypedDict', 'Enum']:
        return {
            'reachability_source': 'framework_managed',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.90,
            'suggested_action': 'OK - instantiated at runtime'
        }

    # 4. Cross-language boundary (JS files analyzed but called from HTML/other)
    if any(file_lower.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte']):
        return {
            'reachability_source': 'cross_language',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.70,
            'suggested_action': 'CHECK - may have cross-language callers'
        }

    # 5. Config/schema files
    if any(pattern in file_lower for pattern in ['config', 'schema', 'settings', '.yaml', '.yml', '.json', '.toml']):
        return {
            'reachability_source': 'external_boundary',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.80,
            'suggested_action': 'OK - configuration/schema'
        }

    # 6. Dynamic dispatch patterns (reflection-like)
    body = node.get('body_source', '')
    if any(pattern in body for pattern in ['getattr(', 'eval(', 'exec(', '__getattr__', 'globals()[', 'locals()[']):
        return {
            'reachability_source': 'dynamic_target',
            'connection_gap': connection_gap,
            'isolation_confidence': 0.60,
            'suggested_action': 'CHECK - may be called via reflection'
        }

    # 7. Public API detection (exported, __all__, public functions)
    if name and not name.startswith('_'):
        # Check if it looks like a public interface
        if kind in ['function', 'class', 'method'] and out_deg > 0:
            return {
                'reachability_source': 'external_boundary',
                'connection_gap': connection_gap,
                'isolation_confidence': 0.75,
                'suggested_action': 'CHECK - may be public API'
            }

    # 8. Default: Truly unreachable (likely dead code)
    return {
        'reachability_source': 'unreachable',
        'connection_gap': connection_gap,
        'isolation_confidence': 0.85,
        'suggested_action': 'REVIEW - likely dead code'
    }



# =============================================================================
# EDGE DETECTORS: Heuristic discovery of implicit edges
# =============================================================================


def detect_js_imports(nodes: List[Dict], edges: List[Dict]) -> int:
    """
    detect_js_imports (Task #6):
    Find edges from JS files to imported modules/functions.
    Pattern: import { Foo } from './bar' -> invokes edge
    """
    new_edges = 0
    import re
    from pathlib import Path

    # 1. Index potential targets by name
    targets_by_name = defaultdict(list)
    for n in nodes:
        if n.get('name'):
            targets_by_name[n.get('name')].append(n.get('id'))
        
    # 2. Identify unique JS files
    js_files = set()
    file_to_node_id = {} # Map file path to a representative node ID (e.g. module or first function) to use as source
    
    for n in nodes:
        fpath = n.get('file_path', '')
        if fpath.lower().endswith(('.js', '.jsx', '.ts', '.tsx')):
            js_files.add(fpath)
            # Prefer 'module' kind as source, else any node
            if fpath not in file_to_node_id or n.get('kind') == 'module':
                file_to_node_id[fpath] = n.get('id')

    # 3. Scan files
    for fpath in js_files:
        if not fpath or fpath not in file_to_node_id:
            continue

        try:
            # Resolving path relative to CWD (Project Root)
            # Note: fpath in nodes is usually relative to project root
            full_path = Path(fpath).resolve()
            if not full_path.exists():
                # Try relative to cwd
                full_path = Path.cwd() / fpath
            
            if not full_path.exists():
                continue

            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Pattern: import { X, Y } from ...
            named_imports = re.findall(r'import\s*{([^}]+)}\s*from', content)
            
            source_id = file_to_node_id[fpath]
            
            for group in named_imports:
                names = [n.strip().split(' as ')[0] for n in group.split(',')]
                for name in names:
                    name = name.strip()
                    if name in targets_by_name:
                        for target_id in targets_by_name[name]:
                            if target_id == source_id: continue
                            
                            edges.append({
                                'source': source_id,
                                'target': target_id,
                                'edge_type': 'imports',
                                'family': 'Dependency',
                                'inferred': True,
                                'confidence': 0.8,
                                'description': f"JS import {name}"
                            })
                            new_edges += 1
        except Exception:
            continue

    return new_edges


def detect_class_instantiation(nodes: List[Dict], edges: List[Dict]) -> int:
    """
    detect_class_instantiation (Task #7):
    Find edges from code instantiating a class to the class definition.
    Pattern: x = MyClass() -> invokes edge
    """
    new_edges = 0
    
    classes_by_name = defaultdict(list)
    for n in nodes:
        # UPDATED: Check 'kind' OR 'type' for robustness
        if n.get('kind') == 'class' or n.get('type') == 'class':
            classes_by_name[n.get('name', '')].append(n.get('id'))
            
    # 2. Scan all nodes for usage
    for src_node in nodes:
        body = src_node.get('body_source', '')
        if not body:
            continue
            
        # Naive pattern: look for ClassName() 
        # (This is a heuristic, better would be AST analysis, but sticking to regex for 'light' Collider)
        import re
        for class_name, targets in classes_by_name.items():
            # Skip common/short names to avoid noise
            if len(class_name) < 4:
                continue
                
            # Regex: Word boundary + ClassName + (
            if re.search(r'\b' + re.escape(class_name) + r'\s*\(', body):
                for target_id in targets:
                    if target_id == src_node.get('id'):
                        continue
                    
                    edges.append({
                        'source': src_node.get('id'),
                        'target': target_id,
                        'edge_type': 'instantiates',
                        'family': 'Dependency',
                        'inferred': True,
                        'confidence': 0.6,
                        'description': f"Class instantiation {class_name}() detected"
                    })
                    new_edges += 1
                    
    return new_edges


# =============================================================================
# CODOME BOUNDARY: Synthetic nodes representing external calling contexts
# =============================================================================

# Boundary node definitions: source → metadata
CODOME_BOUNDARIES = {
    'test_entry': {
        'name': 'TestFramework',
        'description': 'Test frameworks (pytest, jest, unittest) invoke test functions',
        'color': '#4CAF50',  # Green - tests are healthy
        'icon': '🧪'
    },
    'entry_point': {
        'name': 'RuntimeEntry',
        'description': 'Program entry points (__main__, CLI, scripts)',
        'color': '#2196F3',  # Blue - entry
        'icon': '🚀'
    },
    'framework_managed': {
        'name': 'FrameworkDI',
        'description': 'Framework/DI container instantiates (decorators, dataclasses)',
        'color': '#9C27B0',  # Purple - framework magic
        'icon': '⚙️'
    },
    'cross_language': {
        'name': 'HTMLTemplate',
        'description': 'Cross-language callers (HTML onclick, script src)',
        'color': '#FF9800',  # Orange - cross-boundary
        'icon': '🌐'
    },
    'external_boundary': {
        'name': 'ExternalAPI',
        'description': 'External consumers (npm imports, public API)',
        'color': '#00BCD4',  # Cyan - external
        'icon': '📡'
    },
    'dynamic_target': {
        'name': 'DynamicDispatch',
        'description': 'Dynamic invocation (getattr, eval, reflection)',
        'color': '#E91E63',  # Pink - dynamic/uncertain
        'icon': '🔮'
    }
}


def create_codome_boundaries(nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
    """
    Create synthetic codome boundary nodes and inferred edges.

    For each disconnection type (test_entry, entry_point, etc.), creates:
    1. A synthetic boundary node (e.g., __codome__::pytest)
    2. Inferred edges from boundary → disconnected nodes

    Returns:
        {
            'boundary_nodes': [node_dicts...],
            'inferred_edges': [edge_dicts...],
            'summary': {source: count}
        }
    """
    # Run Detector #1: JS Imports
    js_count = detect_js_imports(nodes, edges)
    # Run Detector #2: Class Instantiation
    class_count = detect_class_instantiation(nodes, edges)
    
    print(f"   → [Codome] JS import edges detected: {js_count}")
    print(f"   → [Codome] Class instantiation edges detected: {class_count}")

    # Group disconnected nodes by reachability source
    by_source: Dict[str, List[Dict]] = {}
    for node in nodes:
        disconnection = node.get('disconnection')
        if disconnection:
            source = disconnection.get('reachability_source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(node)

    boundary_nodes = []
    inferred_edges = []
    summary = {}

    for source, disconnected_nodes in by_source.items():
        # Skip 'unreachable' - those are truly dead code
        if source == 'unreachable':
            summary[source] = len(disconnected_nodes)
            continue

        # Get boundary metadata
        boundary_meta = CODOME_BOUNDARIES.get(source)
        if not boundary_meta:
            summary[source] = len(disconnected_nodes)
            continue

        # Create synthetic boundary node
        boundary_id = f"__codome__::{source}"
        boundary_node = {
            'id': boundary_id,
            'name': boundary_meta['name'],
            'type': 'CodomeBoundary',
            'file_path': '__codome__',
            'kind': 'boundary',
            'is_codome_boundary': True,
            'codome_source': source,
            'description': boundary_meta['description'],
            'color_hint': boundary_meta['color'],
            'icon': boundary_meta['icon'],
            # Standard node fields for visualization
            'in_degree': 0,
            'out_degree': len(disconnected_nodes),
            'topology_role': 'external',
            'tier': 'T0',  # Entry tier
            'dimensions': {
                'D1_WHAT': 'BOUNDARY.CODOME',
                'D2_HOW': 'EXTERNAL',
                'D3_LAYER': 'BOUNDARY'
            }
        }
        boundary_nodes.append(boundary_node)

        # Create inferred edges from boundary → disconnected nodes
        for target_node in disconnected_nodes:
            target_id = target_node.get('id', '')
            confidence = target_node.get('disconnection', {}).get('isolation_confidence', 0.5)

            edge = {
                'source': boundary_id,
                'target': target_id,
                'edge_type': 'invokes',
                'family': 'Codome',
                'inferred': True,
                'confidence': confidence,
                'resolution': 'inferred',
                'codome_source': source,
                'description': f'{boundary_meta["name"]} invokes {target_node.get("name", "unknown")}'
            }
            inferred_edges.append(edge)

        summary[source] = len(disconnected_nodes)

    return {
        'boundary_nodes': boundary_nodes,
        'inferred_edges': inferred_edges,
        'summary': summary,
        'total_boundaries': len(boundary_nodes),
        'total_inferred_edges': len(inferred_edges)
    }


# =============================================================================
# FILE-CENTRIC VIEW: Bridges atom-centric analysis with file-based navigation
# =============================================================================

def _resolve_output_dir(target: Path, output_dir: Optional[str]) -> Path:
    """Resolve the canonical output directory."""
    if output_dir:
        return Path(output_dir)
    if target.is_dir():
        return target / ".collider"
    return target.parent / ".collider"


def _find_latest_html(output_dir: Path) -> Optional[Path]:
    """Return newest output_human-readable_*.html in output_dir, if any."""
    try:
        candidates = sorted(
            output_dir.glob("output_human-readable_*.html"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    except FileNotFoundError:
        return None
    return candidates[0] if candidates else None


def _open_file(path: Path) -> bool:
    """Open a file path with the OS default handler."""
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        elif os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception:
        return False
    return True


def _manual_open_command(path: Path) -> str:
    """Return a manual open command for the current OS."""
    if sys.platform == "darwin":
        return f'open "{path}"'
    if os.name == "nt":
        return f'start \"\" \"{path}\"'
    return f'xdg-open "{path}"'


def build_file_index(nodes: List[Dict], edges: List[Dict], target_path: str = "") -> Dict[str, Any]:
    """
    Build a file-centric index of atoms for hybrid navigation.

    This bridges the atom-centric paradigm (Collider's core insight) with
    traditional file-based navigation that developers expect.

    Returns:
        {
            "file_path": {
                "atoms": [atom_indices...],
                "atom_names": ["name1", "name2"...],
                "line_range": [start, end],
                "atom_count": N,
                "imports": [...],
                "internal_edges": N,  # edges within this file
                "external_edges": N,  # edges to other files
                "purpose": "inferred purpose"
            }
        }
    """
    files_index: Dict[str, Dict[str, Any]] = {}

    # Group nodes by file
    for idx, node in enumerate(nodes):
        file_path = node.get("file_path", "")
        if not file_path:
            continue

        if file_path not in files_index:
            files_index[file_path] = {
                "atoms": [],
                "atom_names": [],
                "atom_types": [],
                "line_range": [float('inf'), 0],
                "atom_count": 0,
                "classes": [],
                "functions": [],
                "imports": [],
                "internal_edges": 0,
                "external_edges": 0,
                "purpose": ""
            }

        entry = files_index[file_path]
        entry["atoms"].append(idx)
        entry["atom_names"].append(node.get("name", ""))
        entry["atom_types"].append(node.get("type", "Unknown"))
        entry["atom_count"] += 1

        # Track line range
        line = node.get("line", 0)
        end_line = node.get("end_line", line)
        if line > 0:
            entry["line_range"][0] = min(entry["line_range"][0], line)
            entry["line_range"][1] = max(entry["line_range"][1], end_line)

        # Categorize by symbol kind
        kind = node.get("symbol_kind", "")
        name = node.get("name", "")
        if kind == "class":
            entry["classes"].append(name)
        elif kind in ("function", "method"):
            entry["functions"].append(name)

    # Compute edges (internal vs external)
    node_to_file = {idx: nodes[idx].get("file_path", "") for idx in range(len(nodes))}
    node_name_to_file = {n.get("name", ""): n.get("file_path", "") for n in nodes}

    for edge in edges:
        source = edge.get("source", "")
        target = edge.get("target", "")

        source_file = node_name_to_file.get(source, "")
        target_file = node_name_to_file.get(target, "")

        if source_file and source_file in files_index:
            if source_file == target_file:
                files_index[source_file]["internal_edges"] += 1
            else:
                files_index[source_file]["external_edges"] += 1

    # Infer file purpose from dominant atom types
    for file_path, entry in files_index.items():
        types = Counter(entry["atom_types"])
        dominant = types.most_common(1)
        if dominant:
            dom_type, count = dominant[0]
            if dom_type != "Unknown":
                entry["purpose"] = f"{dom_type}-dominant ({count}/{entry['atom_count']})"
            else:
                # Infer from file name
                fname = Path(file_path).stem.lower()
                if "test" in fname:
                    entry["purpose"] = "Test module"
                elif "util" in fname or "helper" in fname:
                    entry["purpose"] = "Utility module"
                elif "model" in fname or "entity" in fname:
                    entry["purpose"] = "Domain model"
                elif "service" in fname:
                    entry["purpose"] = "Service layer"
                elif "controller" in fname or "handler" in fname:
                    entry["purpose"] = "Interface layer"
                else:
                    entry["purpose"] = "General module"

        # Fix line_range if no lines found
        if entry["line_range"][0] == float('inf'):
            entry["line_range"] = [0, 0]

        # Clean up atom_types (don't need in output, was for computation)
        del entry["atom_types"]

    return files_index


def build_file_boundaries(files_index: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build file boundary data for visualization.

    Returns a list of boundary objects that can be used to draw
    visual separators between files in the atom graph.
    """
    boundaries = []

    for file_path, data in files_index.items():
        if data["atom_count"] == 0:
            continue

        boundaries.append({
            "file": file_path,
            "file_name": Path(file_path).name,
            "atom_indices": data["atoms"],
            "atom_count": data["atom_count"],
            "line_range": data["line_range"],
            "classes": data["classes"],
            "functions": data["functions"][:10],  # Limit for viz
            "cohesion": data["internal_edges"] / max(1, data["internal_edges"] + data["external_edges"]),
            "purpose": data["purpose"]
        })

    # Sort by file path for consistent ordering
    boundaries.sort(key=lambda b: b["file"])

    return boundaries


def _calculate_theory_completeness(nodes: List[Dict]) -> Dict[str, Any]:
    """
    Calculate theory completeness metrics for the analysis output.
    
    Measures what percentage of applicable Standard Model elements
    are captured in the analysis.
    """
    if not nodes:
        return {'overall_score': 0, 'error': 'No nodes'}
    
    total = len(nodes)
    
    # D1_WHAT (atom assignment)
    d1_what_assigned = sum(
        1 for n in nodes
        if n.get('dimensions', {}).get('D1_WHAT')
        and n['dimensions']['D1_WHAT'] != 'Unknown'
    )
    
    # D1_ECOSYSTEM
    d1_ecosystem_assigned = sum(
        1 for n in nodes
        if n.get('dimensions', {}).get('D1_ECOSYSTEM')
    )
    
    # React hook metadata
    react_components = [
        n for n in nodes
        if n.get('dimensions', {}).get('D1_WHAT', '').startswith('EXT.REACT.')
    ]
    hooks_enriched = sum(
        1 for n in react_components
        if n.get('metadata', {}).get('hooks_used') is not None
    )
    
    # K8s metadata
    k8s_resources = [
        n for n in nodes
        if n.get('dimensions', {}).get('D1_ECOSYSTEM') == 'kubernetes'
    ]
    k8s_kind_assigned = sum(
        1 for n in k8s_resources
        if n.get('metadata', {}).get('k8s_kind')
    )
    
    # Calculate percentages
    d1_what_pct = (d1_what_assigned / total) * 100
    d1_ecosystem_pct = (d1_ecosystem_assigned / total) * 100
    hooks_pct = (hooks_enriched / len(react_components) * 100) if react_components else 100.0
    k8s_pct = (k8s_kind_assigned / len(k8s_resources) * 100) if k8s_resources else 100.0
    
    # Overall score
    overall = (d1_what_pct * 0.4 + d1_ecosystem_pct * 0.3 + hooks_pct * 0.15 + k8s_pct * 0.15)
    
    return {
        'd1_what_percentage': round(d1_what_pct, 1),
        'd1_ecosystem_percentage': round(d1_ecosystem_pct, 1),
        'hooks_metadata_percentage': round(hooks_pct, 1),
        'k8s_metadata_percentage': round(k8s_pct, 1),
        'overall_score': round(overall, 1)
    }


def compute_markov_matrix(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """
    Compute Markov transition matrix from call graph.
    P(A → B) = calls from A to B / total calls from A

    Also enriches edges with markov_weight for visualization.
    """
    # Build adjacency counts
    out_counts = defaultdict(lambda: defaultdict(int))
    out_totals = defaultdict(int)

    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        if source and target:
            out_counts[source][target] += 1
            out_totals[source] += 1

    # Compute probabilities
    transitions = {}
    for source, targets in out_counts.items():
        total = out_totals[source]
        transitions[source] = {
            target: count / total
            for target, count in targets.items()
        }

    # IMPORTANT: Enrich edges with markov_weight for flow visualization
    edges_with_weight = 0
    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        if source in transitions and target in transitions[source]:
            edge['markov_weight'] = transitions[source][target]
            edges_with_weight += 1
        else:
            edge['markov_weight'] = 0.0

    # Summary stats
    high_entropy_nodes = []
    for source, probs in transitions.items():
        if len(probs) > 5:  # Calls many things
            high_entropy_nodes.append({
                'node': source.split(':')[-1] if ':' in source else source,
                'fanout': len(probs),
                'max_prob': max(probs.values()) if probs else 0
            })

    return {
        'total_transitions': len(transitions),
        'edges_with_weight': edges_with_weight,
        'avg_fanout': sum(len(t) for t in transitions.values()) / len(transitions) if transitions else 0,
        'high_entropy_nodes': sorted(high_entropy_nodes, key=lambda x: -x['fanout'])[:10],
        'transitions': transitions  # Full transitions for frontend
    }


def detect_knots(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """
    Detect dependency knots (cycles) and tangles in the graph.
    - Cycles: A → B → C → A
    - Tangles: High bidirectional coupling between modules
    """
    # Build adjacency
    graph = defaultdict(set)
    reverse = defaultdict(set)
    
    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        if source and target:
            graph[source].add(target)
            reverse[target].add(source)
    
    # Find strongly connected components (simplified Tarjan-like)
    visited = set()
    on_stack = set()
    cycles = []
    
    def find_cycle(node: str, path: List[str]) -> bool:
        if node in on_stack:
            cycle_start = path.index(node)
            cycle = path[cycle_start:]
            if len(cycle) > 1:
                cycles.append(cycle)
            return True
        if node in visited:
            return False
        
        visited.add(node)
        on_stack.add(node)
        path.append(node)
        
        for neighbor in list(graph.get(node, set()))[:10]:  # Limit for perf
            find_cycle(neighbor, path)
        
        path.pop()
        on_stack.remove(node)
        return False
    
    # Check for cycles from each unvisited node (limited)
    for node in list(graph.keys())[:200]:
        if node not in visited:
            find_cycle(node, [])
    
    # Find bidirectional edges (tangles)
    bidirectional = []
    for source, targets in graph.items():
        for target in targets:
            if source in graph.get(target, set()):
                pair = tuple(sorted([source, target]))
                if pair not in [tuple(sorted([b['a'], b['b']])) for b in bidirectional]:
                    bidirectional.append({
                        'a': source.split(':')[-1] if ':' in source else source,
                        'b': target.split(':')[-1] if ':' in target else target
                    })
    
    # Compute knot score: 0 = no knots, 10 = severely tangled
    knot_score = min(10, len(cycles) * 2 + len(bidirectional) * 0.5)
    
    return {
        'cycles_detected': len(cycles),
        'bidirectional_edges': len(bidirectional),
        'knot_score': round(knot_score, 1),
        'sample_cycles': [c[:5] for c in cycles[:5]],  # First 5, truncated
        'sample_tangles': bidirectional[:10]
    }


def compute_data_flow(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """
    Analyze data flow patterns across the codebase.
    """
    # Track flow by type
    flow_by_type = defaultdict(lambda: {'in': 0, 'out': 0})
    
    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        
        # Find source/target types
        source_type = None
        target_type = None
        for n in nodes:
            if n.get('id') == source:
                source_type = n.get('type', 'Unknown')
            if n.get('id') == target:
                target_type = n.get('type', 'Unknown')
        
        if source_type:
            flow_by_type[source_type]['out'] += 1
        if target_type:
            flow_by_type[target_type]['in'] += 1
    
    # Identify data sources and sinks
    sources = []  # High out, low in (data producers)
    sinks = []    # High in, low out (data consumers)
    
    for type_name, flow in flow_by_type.items():
        ratio = flow['out'] / flow['in'] if flow['in'] > 0 else flow['out']
        if ratio > 2 and flow['out'] > 10:
            sources.append({'type': type_name, 'ratio': round(ratio, 1), 'out': flow['out']})
        elif ratio < 0.5 and flow['in'] > 10:
            sinks.append({'type': type_name, 'ratio': round(ratio, 1), 'in': flow['in']})
    
    return {
        'flow_by_type': dict(flow_by_type),
        'data_sources': sorted(sources, key=lambda x: -x['out'])[:5],
        'data_sinks': sorted(sinks, key=lambda x: -x['in'])[:5],
        'total_flow_edges': len(edges)
    }


def _generate_ai_insights(full_output: Dict, output_dir: Path, options: Dict) -> Optional[Dict]:
    """Generate AI insights using Vertex AI Gemini.

    This calls the context-management analyze.py tool with --mode insights.
    Returns the parsed JSON insights or None on failure.
    """
    import subprocess
    import tempfile

    # Find the analyze.py script (relative to project structure)
    project_root = Path(__file__).parent.parent.parent.parent  # standard-model-of-code -> PROJECT_elements
    analyze_script = project_root / "context-management" / "tools" / "ai" / "analyze.py"

    if not analyze_script.exists():
        print(f"   ⚠️ AI analyze script not found: {analyze_script}")
        return None

    # Write full_output to a temp file for the insights generator
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(full_output, f)
        temp_input = f.name

    try:
        model = options.get('ai_insights_model', 'gemini-2.0-flash-001')

        # Run the insights generator
        cmd = [
            sys.executable,
            str(analyze_script),
            "--mode", "insights",
            "--collider-json", temp_input,
            "--model", model,
            "--yes"  # Skip confirmation
        ]

        # Capture output to parse JSON result
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"   ⚠️ AI insights command failed: {result.stderr[:200] if result.stderr else 'Unknown error'}")
            return None

        # The analyze.py script writes to ai_insights.json in the same dir as input
        insights_file = Path(temp_input).parent / "ai_insights.json"
        if not insights_file.exists():
            # Try the default output location
            insights_file = output_dir / "ai_insights.json"

        if insights_file.exists():
            with open(insights_file, 'r') as f:
                return json.load(f)

        # Try to parse from stdout if script printed JSON
        try:
            # Look for JSON in output (between first { and last })
            stdout = result.stdout
            json_start = stdout.find('{')
            json_end = stdout.rfind('}')
            if json_start >= 0 and json_end > json_start:
                return json.loads(stdout[json_start:json_end+1])
        except (json.JSONDecodeError, ValueError):
            pass

        return None

    except subprocess.TimeoutExpired:
        print("   ⚠️ AI insights generation timed out")
        return None
    except Exception as e:
        print(f"   ⚠️ AI insights generation error: {e}")
        return None
    finally:
        # Clean up temp file
        try:
            Path(temp_input).unlink()
        except Exception:
            pass


def run_full_analysis(target_path: str, output_dir: str = None, options: Dict[str, Any] = None) -> Dict:
    """Run complete analysis with all theoretical frameworks."""

    if options is None:
        options = {}
    open_latest = options.get("open_latest")
    if open_latest is None:
        open_latest = False
    if options.get("no_open", False):
        open_latest = False

    start_time = time.time()
    target = Path(target_path).resolve()
    resolved_output_dir = _resolve_output_dir(target, output_dir)

    # Import analysis functions (must come before observability import)
    sys.path.insert(0, str(Path(__file__).parent))

    # Initialize observability
    timing_enabled = options.get("timing", False)
    verbose_timing = options.get("verbose_timing", False)
    from observability import PerformanceManager, StageTimer
    perf_manager = PerformanceManager(verbose=verbose_timing)
    perf_manager.start_pipeline()

    print("=" * 60)
    print("COLLIDER FULL ANALYSIS")
    print(f"Target: {target}")
    if timing_enabled or verbose_timing:
        print("Performance Tracking: ENABLED")
    print("=" * 60)
    
    from unified_analysis import analyze
    from standard_model_enricher import enrich_with_standard_model
    from purpose_field import detect_purpose_field
    from purpose_emergence import compute_pi2, compute_pi3, compute_pi4
    from execution_flow import detect_execution_flow

    from performance_predictor import predict_performance
    from roadmap_evaluator import RoadmapEvaluator
    from topology_reasoning import TopologyClassifier
    from semantic_cortex import ConceptExtractor
    # NOTE: standard_output_generator removed - consolidated into unified outputs
    
    # Stage 1: Base analysis
    print("\n🔬 Stage 1: Base Analysis...")
    with StageTimer(perf_manager, "Stage 1: Base Analysis") as timer:
        analysis_options = dict(options)
        analysis_options.pop("roadmap", None)
        result = analyze(str(target), output_dir=str(resolved_output_dir), write_output=False, **analysis_options)
        nodes = result.nodes if hasattr(result, 'nodes') else result.get('nodes', [])
        edges = result.edges if hasattr(result, 'edges') else result.get('edges', [])
        unified_stats = getattr(result, 'stats', {}) if hasattr(result, 'stats') else result.get('stats', {})
        unified_classification = getattr(result, 'classification', {}) if hasattr(result, 'classification') else result.get('classification', {})
        unified_auto_discovery = getattr(result, 'auto_discovery', {}) if hasattr(result, 'auto_discovery') else result.get('auto_discovery', {})
        unified_dependencies = getattr(result, 'dependencies', {}) if hasattr(result, 'dependencies') else result.get('dependencies', {})
        unified_architecture = getattr(result, 'architecture', {}) if hasattr(result, 'architecture') else result.get('architecture', {})
        unified_llm_enrichment = getattr(result, 'llm_enrichment', {}) if hasattr(result, 'llm_enrichment') else result.get('llm_enrichment', {})
        unified_warnings = getattr(result, 'warnings', []) if hasattr(result, 'warnings') else result.get('warnings', [])
        unified_recommendations = getattr(result, 'recommendations', []) if hasattr(result, 'recommendations') else result.get('recommendations', [])
        timer.set_output(nodes=len(nodes), edges=len(edges))
    print(f"   → {len(nodes)} nodes, {len(edges)} edges")
    
    # Stage 2: Standard Model enrichment
    print("\n🧬 Stage 2: Standard Model Enrichment...")
    with StageTimer(perf_manager, "Stage 2: Standard Model Enrichment") as timer:
        nodes = enrich_with_standard_model(nodes)
        rpbl_count = sum(1 for n in nodes if n.get('rpbl'))
        timer.set_output(nodes=len(nodes), rpbl_enriched=rpbl_count)
    print(f"   → {rpbl_count} nodes with RPBL scores")

    # Pipeline Assertion: Validate canonical roles
    try:
        from registry.role_registry import get_role_registry
        _registry = get_role_registry()
        _invalid = {n.get('role') for n in nodes if n.get('role') and not _registry.validate(n['role'])}
        if _invalid:
            import os
            if os.environ.get('COLLIDER_STRICT_ROLES', '').lower() == 'true':
                raise ValueError(f"Non-canonical roles detected: {_invalid}")
            else:
                print(f"   ⚠️ WARNING: Non-canonical roles: {_invalid}")
    except ImportError:
        pass  # Registry not available, skip validation

    # Stage 2.5: Ecosystem discovery (hybrid T2 approach)
    print("\n🧭 Stage 2.5: Ecosystem Discovery...")
    with StageTimer(perf_manager, "Stage 2.5: Ecosystem Discovery") as timer:
        try:
            from discovery_engine import discover_ecosystem_unknowns
            ecosystem_discovery = discover_ecosystem_unknowns(nodes)
            timer.set_output(unknowns=ecosystem_discovery.get('total_unknowns', 0))
            print(f"   → {ecosystem_discovery.get('total_unknowns', 0)} unknown ecosystem patterns")
        except Exception as e:
            ecosystem_discovery = {}
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Ecosystem discovery skipped: {e}")

    # Stage 2.7: Octahedral Dimension Classification (D4, D5, D7)
    print("\n📐 Stage 2.7: Octahedral Dimension Classification...")
    with StageTimer(perf_manager, "Stage 2.7: Dimension Classification") as timer:
        try:
            from dimension_classifier import classify_all_dimensions
            dim_count = classify_all_dimensions(nodes)
            timer.set_output(nodes_classified=dim_count)
            print(f"   → {dim_count} nodes with full 8-dimension coordinates")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Dimension classification skipped: {e}")

    # Stage 2.8: Scope Analysis (definitions, references, unused, shadowing)
    print("\n🔬 Stage 2.8: Scope Analysis...")
    with StageTimer(perf_manager, "Stage 2.8: Scope Analysis") as timer:
        try:
            from scope_analyzer import analyze_scopes, find_unused_definitions, find_shadowed_definitions
            import tree_sitter
            import tree_sitter_python
            import tree_sitter_javascript

            # Initialize parsers
            py_parser = tree_sitter.Parser()
            py_parser.language = tree_sitter.Language(tree_sitter_python.language())
            js_parser = tree_sitter.Parser()
            js_parser.language = tree_sitter.Language(tree_sitter_javascript.language())

            scope_stats = {'files_analyzed': 0, 'unused': 0, 'shadowed': 0}

            # Analyze scope per file
            files_analyzed = set()
            for node in nodes:
                file_path = node.get('file_path', '')
                if file_path in files_analyzed:
                    continue
                files_analyzed.add(file_path)

                # Determine language
                if file_path.endswith('.py'):
                    lang, parser = 'python', py_parser
                elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    lang, parser = 'javascript', js_parser
                else:
                    continue

                body = node.get('body_source', '')
                if not body or len(body) < 10:
                    continue

                try:
                    tree = parser.parse(bytes(body, 'utf8'))
                    graph = analyze_scopes(tree, bytes(body, 'utf8'), lang, file_path)
                    unused = find_unused_definitions(graph)
                    shadowed = find_shadowed_definitions(graph)

                    scope_stats['files_analyzed'] += 1
                    scope_stats['unused'] += len(unused)
                    scope_stats['shadowed'] += len(shadowed)

                    # Store in node metadata
                    node['scope_analysis'] = {
                        'definitions': len(graph.definitions),
                        'references': len(graph.references),
                        'unused_count': len(unused),
                        'shadowed_count': len(shadowed)
                    }
                except Exception:
                    pass  # Skip files that fail to parse

            timer.set_output(**scope_stats)
            print(f"   → {scope_stats['files_analyzed']} files analyzed")
            print(f"   → {scope_stats['unused']} unused definitions detected")
            print(f"   → {scope_stats['shadowed']} shadowing pairs found")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Scope analysis skipped: {e}")

    # Stage 2.9: Control Flow Metrics (cyclomatic complexity, nesting depth)
    print("\n📈 Stage 2.9: Control Flow Metrics...")
    with StageTimer(perf_manager, "Stage 2.9: Control Flow Metrics") as timer:
        try:
            from control_flow_analyzer import analyze_control_flow, get_complexity_rating, get_nesting_rating
            import tree_sitter
            import tree_sitter_python
            import tree_sitter_javascript

            # Reuse parsers if available, otherwise create
            if 'py_parser' not in dir():
                py_parser = tree_sitter.Parser()
                py_parser.language = tree_sitter.Language(tree_sitter_python.language())
                js_parser = tree_sitter.Parser()
                js_parser.language = tree_sitter.Language(tree_sitter_javascript.language())

            cf_stats = {'nodes_analyzed': 0, 'avg_cc': 0, 'max_cc': 0, 'avg_depth': 0, 'max_depth': 0}
            cc_sum, depth_sum = 0, 0

            for node in nodes:
                body = node.get('body_source', '')
                if not body or len(body) < 10:
                    continue

                file_path = node.get('file_path', '')
                if file_path.endswith('.py'):
                    lang, parser = 'python', py_parser
                elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    lang, parser = 'javascript', js_parser
                else:
                    continue

                try:
                    tree = parser.parse(bytes(body, 'utf8'))
                    metrics = analyze_control_flow(tree, bytes(body, 'utf8'), lang)

                    cc = metrics['cyclomatic_complexity']
                    depth = metrics['max_nesting_depth']

                    # Store in node
                    node['control_flow'] = {
                        'cyclomatic_complexity': cc,
                        'complexity_rating': get_complexity_rating(cc),
                        'max_nesting_depth': depth,
                        'nesting_rating': get_nesting_rating(depth),
                        'decision_points': metrics['decision_points'],
                        'branches': metrics['branches'],
                        'loops': metrics['loops'],
                        'early_returns': metrics['early_returns']
                    }

                    cf_stats['nodes_analyzed'] += 1
                    cc_sum += cc
                    depth_sum += depth
                    cf_stats['max_cc'] = max(cf_stats['max_cc'], cc)
                    cf_stats['max_depth'] = max(cf_stats['max_depth'], depth)
                except Exception:
                    pass

            if cf_stats['nodes_analyzed'] > 0:
                cf_stats['avg_cc'] = round(cc_sum / cf_stats['nodes_analyzed'], 2)
                cf_stats['avg_depth'] = round(depth_sum / cf_stats['nodes_analyzed'], 2)

            timer.set_output(**cf_stats)
            print(f"   → {cf_stats['nodes_analyzed']} nodes analyzed")
            print(f"   → Avg CC: {cf_stats['avg_cc']}, Max CC: {cf_stats['max_cc']}")
            print(f"   → Avg Depth: {cf_stats['avg_depth']}, Max Depth: {cf_stats['max_depth']}")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Control flow analysis skipped: {e}")

    # Stage 2.10: Pattern-Based Atom Detection
    print("\n🧬 Stage 2.10: Pattern-Based Atom Detection...")
    with StageTimer(perf_manager, "Stage 2.10: Pattern Detection") as timer:
        try:
            from pattern_matcher import PatternMatcher
            import tree_sitter
            import tree_sitter_python
            import tree_sitter_javascript

            # Initialize pattern matcher
            pattern_matcher = PatternMatcher()

            # Reuse parsers
            if 'py_parser' not in dir():
                py_parser = tree_sitter.Parser()
                py_parser.language = tree_sitter.Language(tree_sitter_python.language())
                js_parser = tree_sitter.Parser()
                js_parser.language = tree_sitter.Language(tree_sitter_javascript.language())

            pattern_stats = {'nodes_enriched': 0, 'atoms_detected': 0, 'by_type': {}}

            for node in nodes:
                body = node.get('body_source', '')
                if not body or len(body) < 10:
                    continue

                file_path = node.get('file_path', '')
                if file_path.endswith('.py'):
                    lang, parser = 'python', py_parser
                elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    lang, parser = 'javascript', js_parser
                else:
                    continue

                try:
                    tree = parser.parse(bytes(body, 'utf8'))
                    atoms = pattern_matcher.detect_atoms(tree, bytes(body, 'utf8'), lang)

                    if atoms:
                        # Store detected atoms in node
                        node['detected_atoms'] = [
                            {
                                'type': a.type,
                                'name': a.name,
                                'confidence': a.confidence,
                                'evidence': a.evidence
                            }
                            for a in atoms
                        ]

                        # Update node's atom type if high confidence detection
                        best_atom = max(atoms, key=lambda a: a.confidence)
                        if best_atom.confidence >= 0.85:
                            node['atom_type'] = best_atom.type
                            node['atom_confidence'] = best_atom.confidence

                        pattern_stats['nodes_enriched'] += 1
                        pattern_stats['atoms_detected'] += len(atoms)

                        for a in atoms:
                            pattern_stats['by_type'][a.type] = pattern_stats['by_type'].get(a.type, 0) + 1
                except Exception:
                    pass

            timer.set_output(**{k: v for k, v in pattern_stats.items() if k != 'by_type'})
            print(f"   → {pattern_stats['nodes_enriched']} nodes enriched with atom patterns")
            print(f"   → {pattern_stats['atoms_detected']} total atoms detected")
            if pattern_stats['by_type']:
                top_types = sorted(pattern_stats['by_type'].items(), key=lambda x: -x[1])[:5]
                print(f"   → Top types: {', '.join(f'{t}:{c}' for t, c in top_types)}")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Pattern detection skipped: {e}")

    # Stage 3: Purpose Field
    print("\n🎯 Stage 3: Purpose Field...")
    with StageTimer(perf_manager, "Stage 3: Purpose Field") as timer:
        purpose_field = detect_purpose_field(nodes, edges)
        timer.set_output(nodes=len(purpose_field.nodes), violations=len(purpose_field.violations))
    print(f"   → {len(purpose_field.nodes)} purpose nodes")
    print(f"   → {len(purpose_field.violations)} violations")

    # Stage 3.5: π₃ (Organelle Purpose) for containers
    print("\n🧬 Stage 3.5: Organelle Purpose (π₃)...")
    pi3_count = 0
    # Build parent-child index from names (Class.method pattern)
    children_by_parent = {}
    node_by_name = {n.get('name', ''): n for n in nodes}
    for node in nodes:
        name = node.get('name', '')
        if '.' in name:
            parent_name = name.rsplit('.', 1)[0]
            if parent_name not in children_by_parent:
                children_by_parent[parent_name] = []
            children_by_parent[parent_name].append(node)

    # Compute π₃ for containers
    for node in nodes:
        name = node.get('name', '')
        if name in children_by_parent and len(children_by_parent[name]) > 0:
            children = children_by_parent[name]
            pi3 = compute_pi3(node, children)
            node['pi3_purpose'] = pi3.purpose
            node['pi3_confidence'] = round(pi3.confidence, 2)
            node['pi3_child_count'] = len(children)
            pi3_count += 1
    print(f"   → {pi3_count} containers with π₃ purpose")

    # Stage 3.6: π₄ (System Purpose) for files
    print("\n📦 Stage 3.6: System Purpose (π₄)...")
    # Group nodes by file
    nodes_by_file = {}
    for node in nodes:
        fpath = node.get('file_path', 'unknown')
        if fpath not in nodes_by_file:
            nodes_by_file[fpath] = []
        nodes_by_file[fpath].append(node)

    # Compute π₄ for each file
    file_purposes = {}
    for fpath, file_nodes in nodes_by_file.items():
        pi4 = compute_pi4(fpath, file_nodes)
        file_purposes[fpath] = {
            'purpose': pi4.purpose,
            'confidence': round(pi4.confidence, 2),
            'node_count': len(file_nodes),
            'signals': pi4.signals
        }
        # Also tag each node with its file's π₄
        for node in file_nodes:
            node['pi4_purpose'] = pi4.purpose
            node['pi4_confidence'] = round(pi4.confidence, 2)

    print(f"   → {len(file_purposes)} files with π₄ purpose")

    # Stage 4: Execution Flow
    print("\n⚡ Stage 4: Execution Flow...")
    with StageTimer(perf_manager, "Stage 4: Execution Flow") as timer:
        exec_flow = detect_execution_flow(nodes, edges, purpose_field)
        timer.set_output(entry_points=len(exec_flow.entry_points), orphans=len(exec_flow.orphans))
    print(f"   → {len(exec_flow.entry_points)} entry points")
    print(f"   → {len(exec_flow.orphans)} orphans ({exec_flow.dead_code_percent}% dead code)")

    # Stage 4.5: Orphan Integration Analysis (REMOVED - Module Deleted)
    # orphan_integration was removed in remediation pass.
    orphan_analysis = []

    # Stage 5: Markov Matrix
    print("\n📊 Stage 5: Markov Transition Matrix...")
    with StageTimer(perf_manager, "Stage 5: Markov Transition Matrix") as timer:
        markov = compute_markov_matrix(nodes, edges)
        timer.set_output(transitions=markov['total_transitions'], edges_weighted=markov['edges_with_weight'])
    print(f"   → {markov['total_transitions']} nodes with transitions")
    print(f"   → {markov['edges_with_weight']} edges with markov_weight")
    print(f"   → {markov['avg_fanout']:.1f} avg fanout")

    # Stage 6: Knot Detection
    print("\n🔗 Stage 6: Knot/Cycle Detection...")
    with StageTimer(perf_manager, "Stage 6: Knot/Cycle Detection") as timer:
        knots = detect_knots(nodes, edges)
        timer.set_output(cycles=knots['cycles_detected'], bidirectional=knots['bidirectional_edges'])
    print(f"   → {knots['cycles_detected']} cycles detected")
    print(f"   → {knots['bidirectional_edges']} bidirectional edges")
    print(f"   → Knot score: {knots['knot_score']}/10")

    # Stage 6.5: Graph Analytics (Nerd Layer)
    print("\n🧮 Stage 6.5: Graph Analytics...")
    with StageTimer(perf_manager, "Stage 6.5: Graph Analytics") as timer:
        # Degree computation (always runs - needed for Control Bar mappings)
        try:
            import networkx as nx
            G = nx.DiGraph()
            for node in nodes:
                G.add_node(node.get('id', ''), **{k: v for k, v in node.items() if k != 'body_source'})
            # Only count behavioral edges (calls, invokes) for topology classification
            # Structural edges (contains, inherits) would give false in_degree to all nested nodes
            behavioral_edge_types = {'calls', 'invokes'}
            for edge in edges:
                if edge.get('edge_type') in behavioral_edge_types:
                    src = edge.get('source', edge.get('from', ''))
                    tgt = edge.get('target', edge.get('to', ''))
                    if src and tgt:
                        G.add_edge(src, tgt)

            # Compute in_degree and out_degree for each node
            in_degree_map = dict(G.in_degree())
            out_degree_map = dict(G.out_degree())
            degree_enriched = 0

            # Compute centrality metrics (research-backed: Zimmermann/Nagappan)
            betweenness = nx.betweenness_centrality(G) if len(G) > 0 else {}
            pagerank = nx.pagerank(G) if len(G) > 0 and G.is_directed() else {}

            # Threshold for hub classification (top 5% or min 10 connections)
            all_degrees = [in_degree_map.get(n.get('id', ''), 0) + out_degree_map.get(n.get('id', ''), 0) for n in nodes]
            hub_threshold = max(10, sorted(all_degrees, reverse=True)[len(all_degrees) // 20] if len(all_degrees) > 20 else 10)

            for node in nodes:
                node_id = node.get('id', '')
                in_deg = in_degree_map.get(node_id, 0)
                out_deg = out_degree_map.get(node_id, 0)
                node['in_degree'] = in_deg
                node['out_degree'] = out_deg

                # Add centrality metrics
                node['betweenness_centrality'] = round(betweenness.get(node_id, 0), 6)
                node['pagerank'] = round(pagerank.get(node_id, 0), 6)

                # Compute topology_role (relational property)
                if in_deg == 0 and out_deg == 0:
                    node['topology_role'] = 'orphan'
                elif in_deg == 0 and out_deg > 0:
                    node['topology_role'] = 'root'
                elif out_deg == 0 and in_deg > 0:
                    node['topology_role'] = 'leaf'
                elif (in_deg + out_deg) >= hub_threshold:
                    node['topology_role'] = 'hub'
                else:
                    node['topology_role'] = 'internal'

                # Compute π₂ (Molecular Purpose) - emergent from composition
                pi2 = compute_pi2(node)
                node['pi2_purpose'] = pi2.purpose
                node['pi2_confidence'] = round(pi2.confidence, 2)

                # Add disconnection taxonomy for nodes missing incoming edges
                # This includes orphans (no edges) AND roots (no incoming but have outgoing)
                # Roots are often: entry points, HTML event handlers, exported APIs
                if in_deg == 0:
                    disconnection = classify_disconnection(node, in_deg, out_deg)
                    if disconnection:
                        node['disconnection'] = disconnection

                if in_deg > 0 or out_deg > 0:
                    degree_enriched += 1

            # Count topology roles and disconnection sources for summary
            role_counts = {}
            disconnection_counts = {}
            for node in nodes:
                role = node.get('topology_role', 'unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
                if 'disconnection' in node:
                    source = node['disconnection'].get('reachability_source', 'unknown')
                    disconnection_counts[source] = disconnection_counts.get(source, 0) + 1
            print(f"   → {degree_enriched} nodes enriched with degree metrics")
            print(f"   → Topology roles: {role_counts}")
            if disconnection_counts:
                print(f"   → Disconnection taxonomy: {disconnection_counts}")
            # Report top centrality nodes
            if betweenness:
                top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:3]
                if top_betweenness:
                    print(f"   → Top betweenness: {[(n.split('::')[-1], round(v, 4)) for n, v in top_betweenness]}")
            if pagerank:
                top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:3]
                if top_pagerank:
                    print(f"   → Top PageRank: {[(n.split('::')[-1], round(v, 4)) for n, v in top_pagerank]}")
        except Exception as e:
            # Fallback: compute degrees without networkx
            print(f"   ⚠️ Graph analytics fallback: {type(e).__name__}: {e}")
            from collections import defaultdict
            in_counts = defaultdict(int)
            out_counts = defaultdict(int)
            # Only count behavioral edges (calls, invokes) for topology classification
            behavioral_edge_types = {'calls', 'invokes'}
            for edge in edges:
                if edge.get('edge_type') in behavioral_edge_types:
                    src = edge.get('source', edge.get('from', ''))
                    tgt = edge.get('target', edge.get('to', ''))
                    if src:
                        out_counts[src] += 1
                    if tgt:
                        in_counts[tgt] += 1

            # Threshold for hub classification (top 5% or min 10 connections)
            all_degrees = [in_counts.get(n.get('id', ''), 0) + out_counts.get(n.get('id', ''), 0) for n in nodes]
            hub_threshold = max(10, sorted(all_degrees, reverse=True)[len(all_degrees) // 20] if len(all_degrees) > 20 else 10)

            degree_enriched = 0
            for node in nodes:
                node_id = node.get('id', '')
                in_deg = in_counts.get(node_id, 0)
                out_deg = out_counts.get(node_id, 0)
                node['in_degree'] = in_deg
                node['out_degree'] = out_deg

                # Compute topology_role (relational property)
                if in_deg == 0 and out_deg == 0:
                    node['topology_role'] = 'orphan'
                elif in_deg == 0 and out_deg > 0:
                    node['topology_role'] = 'root'
                elif out_deg == 0 and in_deg > 0:
                    node['topology_role'] = 'leaf'
                elif (in_deg + out_deg) >= hub_threshold:
                    node['topology_role'] = 'hub'
                else:
                    node['topology_role'] = 'internal'

                # BUG FIX: Separate call degree from total degree for metrics
                # This ensures we report "behavioral" stats correctly in APIs
                node['call_in_degree'] = in_deg
                node['call_out_degree'] = out_deg
                
                # Add disconnection taxonomy for nodes missing incoming edges
                # This includes orphans (no edges) AND roots (no incoming but have outgoing)
                if in_deg == 0:
                    disconnection = classify_disconnection(node, in_deg, out_deg)
                    if disconnection:
                        node['disconnection'] = disconnection

                if in_deg > 0 or out_deg > 0:
                    degree_enriched += 1

            # Count topology roles and disconnection sources for summary
            role_counts = {}
            disconnection_counts = {}
            for node in nodes:
                role = node.get('topology_role', 'unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
                if 'disconnection' in node:
                    source = node['disconnection'].get('reachability_source', 'unknown')
                    disconnection_counts[source] = disconnection_counts.get(source, 0) + 1
            print(f"   → {degree_enriched} nodes enriched with degree metrics (fallback)")
            print(f"   → Topology roles: {role_counts}")
            if disconnection_counts:
                print(f"   → Disconnection taxonomy: {disconnection_counts}")
            G = None  # No graph for analytics

        # Advanced analytics (optional - requires graph_analyzer)
        try:
            from graph_analyzer import find_bottlenecks, find_pagerank, find_communities
            if G is not None:
                # Run analytics
                bottlenecks_raw = find_bottlenecks(G, top_n=20) if len(G) > 0 else []
                pagerank_raw = find_pagerank(G, top_n=20) if len(G) > 0 else []
                communities = find_communities(G) if len(G) > 5 else {}

                # Convert dataclass objects to dicts for JSON serialization
                from dataclasses import asdict
                bottlenecks = [asdict(b) if hasattr(b, '__dataclass_fields__') else b for b in bottlenecks_raw]
                pagerank_top = [asdict(p) if hasattr(p, '__dataclass_fields__') else p for p in pagerank_raw]

                graph_analytics = {
                    'bottlenecks': bottlenecks,
                    'pagerank_top': pagerank_top,
                    'communities_count': len(communities),
                    'communities': {str(k): len(v) for k, v in list(communities.items())[:10]} if communities else {},
                }
                timer.set_output(bottlenecks=len(bottlenecks), pagerank=len(pagerank_top), communities=len(communities))
                print(f"   → {len(bottlenecks)} bottlenecks identified")
                print(f"   → {len(pagerank_top)} PageRank leaders")
                print(f"   → {len(communities)} communities detected")
            else:
                graph_analytics = {}
        except Exception as e:
            graph_analytics = {}
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Advanced graph analytics skipped: {e}")

    # Stage 6.6: Statistical Metrics (Entropy, Complexity, Halstead)
    print("\n📊 Stage 6.6: Statistical Metrics...")
    with StageTimer(perf_manager, "Stage 6.6: Statistical Metrics") as timer:
        try:
            from analytics_engine import compute_all_metrics
            statistical_metrics = compute_all_metrics(nodes)
            timer.set_output(
                avg_cyclomatic=statistical_metrics['complexity']['avg'],
                total_volume=statistical_metrics['halstead']['total_volume'],
                estimated_bugs=statistical_metrics['halstead']['estimated_bugs']
            )
            print(f"   → Avg cyclomatic: {statistical_metrics['complexity']['avg']}")
            print(f"   → High complexity nodes: {statistical_metrics['complexity']['high_complexity_count']}")
            print(f"   → Est. bugs: {statistical_metrics['halstead']['estimated_bugs']}")
        except Exception as e:
            statistical_metrics = {}
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Statistical metrics skipped: {e}")

    # Stage 6.8: Codome Boundary Generation
    print("\n🌐 Stage 6.8: Codome Boundary Generation...")
    codome_result = {'boundary_nodes': [], 'inferred_edges': [], 'summary': {}}
    with StageTimer(perf_manager, "Stage 6.8: Codome Boundaries") as timer:
        try:
            codome_result = create_codome_boundaries(nodes, edges)
            timer.set_output(
                boundaries=codome_result['total_boundaries'],
                inferred_edges=codome_result['total_inferred_edges']
            )
            if codome_result['boundary_nodes']:
                print(f"   → {codome_result['total_boundaries']} codome boundary nodes created")
                print(f"   → {codome_result['total_inferred_edges']} inferred edges generated")
                print(f"   → Sources: {codome_result['summary']}")
                # Add boundary nodes and inferred edges to main lists for visualization
                # Mark with _fromCodome flag for UI filtering
                for bn in codome_result['boundary_nodes']:
                    bn['_fromCodome'] = True
                for ie in codome_result['inferred_edges']:
                    ie['_fromCodome'] = True
                nodes.extend(codome_result['boundary_nodes'])
                edges.extend(codome_result['inferred_edges'])
            else:
                print("   → No disconnected nodes to link")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Codome boundary generation skipped: {e}")

    # Stage 7: Data Flow
    print("\n🌊 Stage 7: Data Flow Analysis...")
    with StageTimer(perf_manager, "Stage 7: Data Flow Analysis") as timer:
        data_flow = compute_data_flow(nodes, edges)
        timer.set_output(sources=len(data_flow['data_sources']), sinks=len(data_flow['data_sinks']))
    print(f"   → {len(data_flow['data_sources'])} data sources")
    print(f"   → {len(data_flow['data_sinks'])} data sinks")

    # Stage 8: Performance Prediction
    print("\n⏱️  Stage 8: Performance Prediction...")
    with StageTimer(perf_manager, "Stage 8: Performance Prediction") as timer:
        try:
            perf = predict_performance(nodes, exec_flow)
            perf_summary = perf.summary() if hasattr(perf, 'summary') else {}
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️  Performance prediction skipped: {e}")
            perf_summary = {}

    # Stage 8.5: Constraint Field Validation
    print("\n🚧 Stage 8.5: Constraint Field Validation...")
    constraint_report = {}
    with StageTimer(perf_manager, "Stage 8.5: Constraint Validation") as timer:
        try:
            from constraint_engine import ConstraintEngine
            engine = ConstraintEngine()
            constraint_report = engine.validate_graph(nodes, edges)
            timer.set_output(
                antimatter=constraint_report['antimatter']['count'],
                policy=constraint_report['policy_violations']['count'],
                signals=constraint_report['signals']['count']
            )
            # Show architecture detection
            arch_detect = constraint_report.get('architecture_detection', {})
            if arch_detect:
                is_layered = arch_detect.get('is_layered', False)
                arch_type = "Layered" if is_layered else "Non-layered"
                print(f"   → Architecture: {arch_type} (confidence: {arch_detect.get('confidence', 0):.0%})")
                if constraint_report.get('layer_validation_skipped'):
                    print(f"   → Layer constraints: SKIPPED (non-layered codebase)")
            print(f"   → Antimatter (Tier A): {constraint_report['antimatter']['count']}")
            print(f"   → Policy (Tier B): {constraint_report['policy_violations']['count']}")
            print(f"   → Signals (Tier C): {constraint_report['signals']['count']}")
            print(f"   → Valid: {constraint_report['valid']}")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Constraint validation skipped: {e}")

    # Stage 8.6: Purpose Intelligence (Q-Scores)
    print("\n🧠 Stage 8.6: Purpose Intelligence...")
    codebase_intelligence = {}
    with StageTimer(perf_manager, "Stage 8.6: Purpose Intelligence") as timer:
        try:
            from purpose_intelligence import enrich_nodes_with_intelligence
            nodes, codebase_intelligence = enrich_nodes_with_intelligence(nodes, edges)
            timer.set_output(
                codebase_q=codebase_intelligence.get('codebase_intelligence', 0),
                interpretation=codebase_intelligence.get('interpretation', 'Unknown'),
            )
            print(f"   → Codebase Intelligence: {codebase_intelligence.get('codebase_intelligence', 0):.3f}")
            print(f"   → Interpretation: {codebase_intelligence.get('interpretation', 'Unknown')}")
            dist = codebase_intelligence.get('distribution', {})
            print(f"   → Distribution: {dist.get('excellent', 0)} excellent, {dist.get('good', 0)} good, {dist.get('moderate', 0)} moderate, {dist.get('poor', 0)} poor")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Purpose Intelligence skipped: {e}")

    # Compute aggregate metrics
    total_time = time.time() - start_time
    
    # Type distribution
    types = Counter(n.get('type', 'Unknown') for n in nodes)
    
    # Ring distribution (Clean Architecture)
    rings = Counter(n.get('ring', 'unknown') for n in nodes)

    # Edge breakdown + KPIs
    edge_types = Counter(e.get('edge_type', 'unknown') for e in edges)
    total_edges = len(edges)
    unresolved_edges = sum(1 for e in edges if e.get('resolution') == 'unresolved')
    resolved_edges = total_edges - unresolved_edges
    edge_resolution_percent = (resolved_edges / total_edges * 100) if total_edges else 0.0
    call_edges = edge_types.get('calls', 0)
    import_edges = edge_types.get('imports', 0)
    call_ratio_percent = (call_edges / total_edges * 100) if total_edges else 0.0
    orphan_count = len(exec_flow.orphans)
    orphan_percent = (orphan_count / len(nodes) * 100) if nodes else 0.0
    reachability_percent = max(0.0, 100.0 - exec_flow.dead_code_percent)
    graph_density = (total_edges / (len(nodes) * (len(nodes) - 1))) if len(nodes) > 1 else 0.0
    
    # RPBL averages
    rpbl_sums = {'responsibility': 0, 'purity': 0, 'boundary': 0, 'lifecycle': 0}
    for n in nodes:
        rpbl = n.get('rpbl', {})
        for k in rpbl_sums:
            rpbl_sums[k] += rpbl.get(k, 0)
    rpbl_avgs = {k: round(v / len(nodes), 1) if nodes else 0 for k, v in rpbl_sums.items()}
    
    # Build complete output
    full_output = {
        'nodes': list(nodes),  # Required for report generator
        'edges': list(edges),  # Required for report generator
        'meta': {
            'target': str(target),
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'analysis_time_ms': int(total_time * 1000),
            'version': '4.0.0',
            'deterministic': True
        },
        'counts': {
            'nodes': len(nodes),
            'edges': len(edges),
            'files': len(set(n.get('file_path', '') for n in nodes)),
            'entry_points': len(exec_flow.entry_points),
            'orphans': len(exec_flow.orphans),
            'cycles': knots['cycles_detected']
        },
        'stats': unified_stats,
        'coverage': {
            'type_coverage': 100.0,
            'ring_coverage': (len(nodes) - rings.get('unknown', 0)) / len(nodes) * 100 if nodes else 0,
            'rpbl_coverage': rpbl_count / len(nodes) * 100 if nodes else 0,
            'dead_code_percent': exec_flow.dead_code_percent
        },
        'classification': unified_classification,
        'auto_discovery': unified_auto_discovery,
        'ecosystem_discovery': ecosystem_discovery,
        'dependencies': unified_dependencies,
        'architecture': unified_architecture,
        'llm_enrichment': unified_llm_enrichment,
        'warnings': unified_warnings,
        'recommendations': unified_recommendations,
        'theory_completeness': _calculate_theory_completeness(nodes),
        'distributions': {
            'types': dict(types.most_common(15)),
            'rings': dict(rings),
            'atoms': dict(Counter(n.get('atom', '') for n in nodes))
        },
        'analytics': statistical_metrics,
        'edge_types': dict(edge_types),
        'rpbl_profile': rpbl_avgs,
        'kpis': {
            'nodes_total': len(nodes),
            'edges_total': total_edges,
            'edge_resolution_percent': round(edge_resolution_percent, 1),
            'resolved_edges': resolved_edges,
            'unresolved_edges': unresolved_edges,
            'call_edges': call_edges,
            'import_edges': import_edges,
            'call_ratio_percent': round(call_ratio_percent, 1),
            'reachability_percent': round(reachability_percent, 1),
            'dead_code_percent': round(exec_flow.dead_code_percent, 1),
            'orphan_count': orphan_count,
            'orphan_percent': round(orphan_percent, 1),
            'knot_score': knots.get('knot_score', 0),
            'cycles_detected': knots.get('cycles_detected', 0),
            'avg_fanout': round(markov.get('avg_fanout', 0.0), 2),
            'graph_density': round(graph_density, 4),
            'top_hub_count': 0,
            'topology_shape': 'UNKNOWN',
            # Constraint Field metrics
            'antimatter_count': constraint_report.get('antimatter', {}).get('count', 0) if constraint_report else 0,
            'policy_violation_count': constraint_report.get('policy_violations', {}).get('count', 0) if constraint_report else 0,
            'signal_count': constraint_report.get('signals', {}).get('count', 0) if constraint_report else 0,
            # Purpose Intelligence metrics
            'codebase_intelligence': codebase_intelligence.get('codebase_intelligence', 0) if codebase_intelligence else 0,
            'codebase_interpretation': codebase_intelligence.get('interpretation', 'Unknown') if codebase_intelligence else 'Unknown',
            'q_distribution': codebase_intelligence.get('distribution', {}) if codebase_intelligence else {},
            'rho_antimatter': round(constraint_report.get('antimatter', {}).get('rho_antimatter', 0), 4) if constraint_report else 0,
            'rho_policy': round(constraint_report.get('policy_violations', {}).get('rho_policy', 0), 4) if constraint_report else 0,
            'constraint_valid': constraint_report.get('valid', True) if constraint_report else True,
            # Codome boundary KPIs
            'codome_boundary_count': codome_result.get('total_boundaries', 0),
            'codome_inferred_edges': codome_result.get('total_inferred_edges', 0),
        },
        'purpose_field': purpose_field.summary(),
        'execution_flow': dict(exec_flow.summary(), **{
            'entry_points': exec_flow.entry_points,
            'orphans': exec_flow.orphans
        }),
        'markov': markov,
        'knots': knots,
        'graph_analytics': graph_analytics if 'graph_analytics' in dir() else {},
        'statistical_metrics': statistical_metrics if 'statistical_metrics' in dir() else {},
        'data_flow': data_flow,
        'performance': perf_summary,
        'constraint_field': constraint_report if constraint_report else {},
        'top_hubs': [],
        'orphans_list': exec_flow.orphans[:20],  # First 20
        'orphan_integration': [],
        # Codome boundary visualization layer
        'codome_boundaries': {
            'boundary_nodes': codome_result.get('boundary_nodes', []),
            'inferred_edges': codome_result.get('inferred_edges', []),
            'summary': codome_result.get('summary', {}),
            'total_boundaries': codome_result.get('total_boundaries', 0),
            'total_inferred_edges': codome_result.get('total_inferred_edges', 0)
        },
    }
    
    # Compute top hubs
    in_deg = Counter()
    for e in edges:
        in_deg[e.get('target', '')] += 1
    for node_id, deg in in_deg.most_common(10):
        name = node_id.split(':')[-1] if ':' in node_id else node_id.split('/')[-1]
        full_output['top_hubs'].append({'name': name, 'in_degree': deg})
    full_output['kpis']['top_hub_count'] = len(full_output['top_hubs'])

    # ==========================================================================
    # FILE-CENTRIC VIEW: Hybrid atom/file navigation
    # ==========================================================================
    print("\n📁 Building file index...")
    with StageTimer(perf_manager, "File Index Building") as timer:
        files_index = build_file_index(nodes, edges, str(target))
        file_boundaries = build_file_boundaries(files_index)

        # Enrich file boundaries with comprehensive metadata
        try:
            enricher = FileEnricher(root_path=str(target), enable_git=False)
            file_boundaries = enricher.enrich_boundaries(file_boundaries)
            print(f"   → File metadata enriched for {len(file_boundaries)} files")
        except Exception as e:
            print(f"   ⚠️ File enrichment failed: {e}")

        full_output['files'] = files_index
        full_output['file_boundaries'] = file_boundaries
        full_output['counts']['files_with_atoms'] = len(files_index)
        timer.set_output(files=len(files_index), atoms_mapped=sum(f['atom_count'] for f in file_boundaries))

    print(f"   → {len(files_index)} files indexed")
    print(f"   → {sum(f['atom_count'] for f in file_boundaries)} atoms mapped to files")

    # Save output
    out_path = resolved_output_dir

    out_path.mkdir(parents=True, exist_ok=True)

    # NOTE: The LLM-oriented output JSON is the single source of truth for analysis results.

    # Stage 9: Roadmap Evaluation
    print("\n🛣️  Stage 9: Roadmap Evaluation...")
    with StageTimer(perf_manager, "Stage 9: Roadmap Evaluation") as timer:
        roadmap_name = options.get('roadmap')
        if roadmap_name:
            try:
                roadmap_path = Path(__file__).parent / "roadmaps" / f"{roadmap_name}.json"
                if roadmap_path.exists():
                    evaluator = RoadmapEvaluator(str(roadmap_path))
                    # Collect all file paths
                    all_files = [str(f) for f in Path(target_path).rglob('*') if f.is_file()]
                    roadmap_result = evaluator.evaluate(all_files)
                    full_output['roadmap'] = roadmap_result
                    timer.set_output(readiness=roadmap_result.get('readiness_score', 0))
                    print(f"   → Roadmap '{roadmap_name}' analyzed: {roadmap_result['readiness_score']:.0f}% ready")
                else:
                    timer.set_status("WARN", f"Roadmap '{roadmap_name}' not found")
                    print(f"   ⚠️ Roadmap '{roadmap_name}' not found in roadmaps directory")
            except Exception as e:
                timer.set_status("WARN", str(e))
                print(f"   ⚠️ Roadmap analysis failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            timer.set_status("SKIP")
            print("   → Skipped (no --roadmap specified)")

    # Stage 10: Visual Topology Analysis
    print("\n🧠 Stage 10: Visual Reasoning...")
    with StageTimer(perf_manager, "Stage 10: Visual Reasoning") as timer:
        try:
            topo = TopologyClassifier()
            topology_result = topo.classify(nodes, edges)
            full_output['topology'] = topology_result
            full_output['kpis']['topology_shape'] = topology_result.get('shape', 'UNKNOWN')
            timer.set_output(shape=topology_result.get('shape', 'UNKNOWN'))
            print(f"   → Visual Shape: {topology_result['shape']}")
            print(f"   → Description: {topology_result['description']}")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Topology analysis failed: {e}")

    # Stage 11: Semantic Cortex (Concept Extraction)
    print("\n🧠 Stage 11: Semantic Cortex...")
    with StageTimer(perf_manager, "Stage 11: Semantic Cortex") as timer:
        try:
            cortex = ConceptExtractor()
            semantics = cortex.extract_concepts(nodes)
            full_output['semantics'] = semantics
            timer.set_output(concepts=len(semantics.get('top_concepts', [])))
            print(f"   → Domain Inference: {semantics['domain_inference']}")
            print(f"   → Top Concepts: {', '.join([t['term'] for t in semantics['top_concepts'][:5]])}")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Semantic analysis failed: {e}")

    # ==========================================================================
    # OUTPUT CONSOLIDATION: 2 files only
    # 1. output_llm-oriented_<project>_<timestamp>.json - Structured knowledge bundle
    # 2. output_human-readable_<project>_<timestamp>.html - Visual report (embeds Brain Download)
    # ==========================================================================

    # Add performance data BEFORE generating brain_download (so it's included in markdown)
    if timing_enabled or verbose_timing:
        full_output['pipeline_performance'] = perf_manager.to_dict()

    # Generate Brain Download content (for embedding in HTML)
    from brain_download import generate_brain_download
    brain_content = generate_brain_download(full_output)
    full_output['brain_download'] = brain_content  # Embed in JSON for HTML access

    # Stage 11b: AI Insights (optional - requires Vertex AI)
    if options.get('ai_insights'):
        print("\n✨ Stage 11b: AI Insights Generation (Vertex AI)...")
        with StageTimer(perf_manager, "Stage 11b: AI Insights") as timer:
            try:
                ai_insights = _generate_ai_insights(full_output, out_path, options)
                if ai_insights:
                    full_output['ai_insights'] = ai_insights
                    timer.set_output(insights=len(ai_insights) if isinstance(ai_insights, list) else 1)
                    print("   → AI insights generated successfully")
                else:
                    timer.set_status("WARN", "No results returned")
                    print("   ⚠️ AI insights generation returned no results")
            except Exception as e:
                timer.set_status("FAIL", str(e))
                print(f"   ⚠️ AI insights generation failed: {e}")

    # Stage 12: Write consolidated outputs
    print("\n📦 Stage 12: Generating Consolidated Outputs...")

    unified_json = None
    viz_file = None
    with StageTimer(perf_manager, "Stage 12: Output Generation") as timer:
        try:
            # Add performance data INSIDE timer but BEFORE write (includes stages 1-11)
            if timing_enabled or verbose_timing:
                full_output['pipeline_performance'] = perf_manager.to_dict()

            from src.core.output_generator import generate_outputs
            outputs = generate_outputs(full_output, out_path, target_name=target.name)
            unified_json = outputs["llm"]
            viz_file = outputs["html"]
            timer.set_output(json=1, html=1)
            print(f"   → Data: {unified_json}")
            print(f"   → Visual: {viz_file}")
        except Exception as e:
            timer.set_status("FAIL", str(e))
            print(f"   ⚠️ Output generation failed: {e}")

    # Final timing summary
    total_time = time.time() - start_time

    print("\n" + "=" * 60)
    print("✅ FULL ANALYSIS COMPLETE")
    print(f"   Time: {total_time:.1f}s")
    if unified_json:
        print(f"   Data:   {unified_json}")
    if viz_file:
        print(f"   Visual: {viz_file}")

    # Print timing summary if enabled
    if timing_enabled and not verbose_timing:
        perf_manager.print_summary()

    if open_latest:
        latest_html = _find_latest_html(out_path)
        if latest_html:
            print(f"   Open:   {latest_html}")
            print(f"   Manual: {_manual_open_command(latest_html)}")
            if not _open_file(latest_html):
                print("   ⚠️  Open failed (see system logs for details).")
        else:
            print("   ⚠️  No HTML outputs found to open.")
    print("=" * 60)

    return full_output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python full_analysis.py <path> [--output <dir>]")
        sys.exit(1)
    
    target = sys.argv[1]
    output_dir = None
    
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
    
    run_full_analysis(target, output_dir)
