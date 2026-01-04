#!/usr/bin/env python3
"""
COLLIDER EDGE EXTRACTOR
=======================

Extracts relationships (edges) between code elements.
Creates a call graph from particles and import data.

Edge Types:
- imports: Module imports another module
- contains: Class contains method, module contains class
- calls: Function/method calls another function
- inherits: Class inherits from another class
- uses: General usage relationship
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# Standard library module names (common ones for quick classification)
STDLIB_MODULES = frozenset([
    'abc', 'argparse', 'ast', 'asyncio', 'base64', 'builtins', 'collections',
    'contextlib', 'copy', 'dataclasses', 'datetime', 'decimal', 'enum',
    'functools', 'glob', 'hashlib', 'heapq', 'http', 'importlib', 'inspect',
    'io', 'itertools', 'json', 'logging', 'math', 'multiprocessing', 'os',
    'pathlib', 'pickle', 'platform', 'pprint', 're', 'shutil', 'signal',
    'socket', 'sqlite3', 'ssl', 'statistics', 'string', 'subprocess', 'sys',
    'tempfile', 'textwrap', 'threading', 'time', 'traceback', 'typing',
    'unittest', 'urllib', 'uuid', 'warnings', 'weakref', 'xml', 'zipfile',
])


FILE_NODE_SUFFIX = "__file__"


def _normalize_file_path(file_path: str) -> str:
    """Normalize file path to a resolved absolute string."""
    if not file_path:
        return ""
    try:
        return str(Path(file_path).resolve())
    except Exception:
        return file_path


def module_name_from_path(file_path: str) -> str:
    """Derive a module name from a file path."""
    path = Path(file_path)
    if path.stem == "__init__":
        return path.parent.name or path.stem
    return path.stem


def file_node_name(file_path: str, existing_ids: Optional[Set[str]] = None) -> str:
    """Compute a unique file-node name derived from the file path."""
    normalized = _normalize_file_path(file_path)
    base = module_name_from_path(normalized)
    if not existing_ids:
        return base

    candidate = _make_node_id(normalized, base)
    if candidate not in existing_ids:
        return base

    candidate_name = f"{base}.{FILE_NODE_SUFFIX}"
    candidate_id = _make_node_id(normalized, candidate_name)
    if candidate_id not in existing_ids:
        return candidate_name

    index = 2
    while True:
        candidate_name = f"{base}.{FILE_NODE_SUFFIX}{index}"
        candidate_id = _make_node_id(normalized, candidate_name)
        if candidate_id not in existing_ids:
            return candidate_name
        index += 1


def file_node_id(file_path: str, existing_ids: Optional[Set[str]] = None) -> str:
    """Build a canonical file-node id for a file path."""
    normalized = _normalize_file_path(file_path)
    name = file_node_name(normalized, existing_ids)
    return _make_node_id(normalized, name)


def _make_node_id(file_path: str, name: str) -> str:
    """Create a node ID in the canonical format: {full_path}:{name}"""
    return f"{file_path}:{name}"


def _get_particle_id(particle: Dict) -> str:
    """Get the canonical ID for a particle."""
    file_path = particle.get('file_path', '')
    name = particle.get('name', '')
    # Check if particle already has a full ID
    if particle.get('id'):
        return particle['id']
    return _make_node_id(file_path, name)


def _collect_file_node_ids(particles: List[Dict]) -> Dict[str, str]:
    """Collect file-node ids keyed by normalized file path."""
    mapping: Dict[str, str] = {}
    for particle in particles:
        metadata = particle.get("metadata") or {}
        if not metadata.get("file_node"):
            continue
        file_path = particle.get("file_path", "")
        if not file_path:
            continue
        mapping[_normalize_file_path(file_path)] = _get_particle_id(particle)
    return mapping


def extract_call_edges(particles: List[Dict], results: List[Dict], target_path: Optional[str] = None) -> List[Dict]:
    """
    Extract call relationships from particles and raw imports.
    Creates edges: {source, target, edge_type, file_path, line}

    Args:
        particles: List of classified particles
        results: Raw AST parse results with import data
        target_path: Base path for resolving relative paths

    Returns:
        List of edge dictionaries with resolution and confidence
    """
    edges = []

    # Build particle lookup by name AND by full ID (skip file nodes)
    particle_by_name = {}
    particle_by_id = {}
    for p in particles:
        metadata = p.get("metadata") or {}
        if metadata.get("file_node"):
            continue
        name = p.get('name', '')
        particle_id = _get_particle_id(p)
        if name:
            particle_by_name[name] = p
            # Also register short name
            short = name.split('.')[-1] if '.' in name else name
            if short not in particle_by_name:
                particle_by_name[short] = p
        if particle_id:
            particle_by_id[particle_id] = p

    file_node_ids = _collect_file_node_ids(particles)

    # Extract imports from each file
    for result in results:
        file_path = result.get('file_path', '')
        raw_imports = result.get('raw_imports', [])

        # Use file-node id when available
        file_key = _normalize_file_path(file_path)
        source_id = file_node_ids.get(file_key)
        if not source_id:
            source_id = _make_node_id(file_path, module_name_from_path(file_path)) if file_path else 'unknown'

        for imp in raw_imports:
            # Create import edge - target is module name (external reference)
            if isinstance(imp, dict):
                target_module = imp.get('module', '')
                if isinstance(target_module, dict):
                    target_module = target_module.get('name', str(target_module))
                line = imp.get('line', 0)
            else:
                target_module = str(imp)
                line = 0

            if target_module:  # Only add if we have a valid target
                edges.append({
                    'source': source_id,
                    'target': str(target_module),  # External module - keep as module name
                    'edge_type': 'imports',
                    'file_path': file_path,
                    'line': line,
                    'confidence': 1.0,
                })

    # Extract containment edges (parent-child)
    for p in particles:
        parent = p.get('parent', '')
        if parent:
            file_path = p.get('file_path', '')
            source_id = _make_node_id(file_path, parent)
            target_id = _get_particle_id(p)
            edges.append({
                'source': source_id,
                'target': target_id,
                'edge_type': 'contains',
                'file_path': file_path,
                'line': p.get('line', 0),
                'confidence': 1.0,
            })

    # Extract inheritance edges
    for p in particles:
        base_classes = p.get('base_classes', [])
        for base in base_classes:
            if base and base not in ('object', 'ABC', 'Protocol'):
                source_id = _get_particle_id(p)
                # Look up base class in known particles
                if base in particle_by_name:
                    target_id = _get_particle_id(particle_by_name[base])
                else:
                    target_id = base  # External class, keep as name
                edges.append({
                    'source': source_id,
                    'target': target_id,
                    'edge_type': 'inherits',
                    'file_path': p.get('file_path', ''),
                    'line': p.get('line', 0),
                    'confidence': 1.0,
                })

    # Extract call edges from body_source (heuristic)
    for p in particles:
        body = p.get('body_source', '')
        if body:
            # Look for function calls in body
            calls = re.findall(r'(?:self\.)?(\w+)\s*\(', body)
            caller_id = _get_particle_id(p)
            caller_name = p.get('name', '')
            caller_short = caller_name.split('.')[-1] if '.' in caller_name else caller_name

            for call in calls:
                # Skip self-calls and common built-ins
                if call == caller_short:
                    continue
                if call in ('print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
                           'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'isinstance',
                           'hasattr', 'getattr', 'setattr', 'open', 'super', 'type', 'id'):
                    continue

                if call in particle_by_name:
                    target_id = _get_particle_id(particle_by_name[call])
                    edges.append({
                        'source': caller_id,
                        'target': target_id,
                        'edge_type': 'calls',
                        'file_path': p.get('file_path', ''),
                        'line': p.get('line', 0),
                        'confidence': 0.7,  # Heuristic detection
                    })

            # Look for attribute access (e.g., Enum.MEMBER, Class.method)
            # Pattern: CapitalizedName.something (likely class/enum access)
            attr_accesses = re.findall(r'\b([A-Z][a-zA-Z0-9_]*)\.[a-zA-Z_]\w*', body)
            for accessed in attr_accesses:
                if accessed == caller_short:
                    continue
                if accessed in ('Path', 'Dict', 'List', 'Optional', 'Union', 'Any', 'Type', 'Set', 'Tuple'):
                    continue  # Skip typing imports
                if accessed in particle_by_name:
                    target_id = _get_particle_id(particle_by_name[accessed])
                    edges.append({
                        'source': caller_id,
                        'target': target_id,
                        'edge_type': 'uses',
                        'file_path': p.get('file_path', ''),
                        'line': p.get('line', 0),
                        'confidence': 0.8,  # Attribute access detection
                    })

    node_ids = {
        _get_particle_id(p)
        for p in particles
        if _get_particle_id(p)
    }
    return resolve_edges(
        edges,
        node_ids,
        target_root=str(target_path) if target_path else None,
        file_node_ids=file_node_ids,
    )


def extract_decorator_edges(particles: List[Dict]) -> List[Dict]:
    """
    Extract decorator relationships.

    Args:
        particles: List of classified particles

    Returns:
        List of decorator edge dictionaries
    """
    edges = []

    for p in particles:
        decorators = p.get('decorators', [])
        for decorator in decorators:
            # Clean decorator name (remove @ and arguments)
            dec_name = decorator.lstrip('@').split('(')[0].strip()
            if dec_name:
                edges.append({
                    'source': dec_name,
                    'target': p.get('name', ''),
                    'edge_type': 'decorates',
                    'file_path': p.get('file_path', ''),
                    'line': p.get('line', 0),
                    'confidence': 1.0,
                })

    return edges


def deduplicate_edges(edges: List[Dict]) -> List[Dict]:

def _is_canonical_id(target: str) -> bool:
    """Check if target looks like a canonical ID (path:name format)."""
    return ':' in target and ('/' in target or '\\' in target)


def _extract_node_path(node_id: str) -> Optional[str]:
    """Extract the file path portion from a canonical node id."""
    if not node_id:
        return None
    if "::" in node_id:
        path_part = node_id.split("::", 1)[0]
    elif ":" in node_id:
        path_part = node_id.rsplit(":", 1)[0]
    else:
        return None
    try:
        return str(Path(path_part).resolve())
    except Exception:
        return path_part


def _build_file_to_node_ids(node_ids: Set[str]) -> Dict[str, List[str]]:
    """Build a mapping from absolute file path to node ids for that file."""
    mapping: Dict[str, List[str]] = {}
    for node_id in node_ids:
        path = _extract_node_path(node_id)
        if not path:
            continue
        mapping.setdefault(path, []).append(node_id)
    for key in mapping:
        mapping[key].sort()
    return mapping


def _collect_file_node_ids(particles: List[Dict]) -> Dict[str, str]:
    """Collect file-node ids keyed by normalized file path."""
    mapping: Dict[str, str] = {}
    for particle in particles:
        metadata = particle.get("metadata") or {}
        if not metadata.get("file_node"):
            continue
        file_path = particle.get("file_path", "")
        if not file_path:
            continue
        mapping[_normalize_file_path(file_path)] = _get_particle_id(particle)
    return mapping


def resolve_import_target_to_file(
    target_module: str,
    target_root: str,
) -> Tuple[Optional[str], bool]:
    """
    Resolve a module name to a file path inside target_root.

    Returns:
        (resolved_path, ambiguous)
    """
    if not target_module or target_module.startswith("."):
        return None, False

    root = Path(target_root)
    root_name = root.name

    base_names = [target_module]
    if "." in target_module:
        base_names.append(target_module.rsplit(".", 1)[0])

    prefixes = [f"{root_name}.", f"src.{root_name}."]
    candidates: List[str] = []
    for name in base_names:
        if name not in candidates:
            candidates.append(name)
        for prefix in prefixes:
            if name.startswith(prefix):
                trimmed = name[len(prefix):]
                if trimmed and trimmed not in candidates:
                    candidates.append(trimmed)

    for candidate in candidates:
        module_path = candidate.replace(".", "/")
        file_candidate = root / f"{module_path}.py"
        init_candidate = root / module_path / "__init__.py"
        existing = [str(p.resolve()) for p in (file_candidate, init_candidate) if p.exists()]
        if len(existing) > 1:
            return None, True
        if len(existing) == 1:
            return existing[0], False

    return None, False


def _get_module_root(target: str) -> str:
    """Extract root module name from a dotted path."""
    if '.' in target:
        return target.split('.')[0]
    return target


def _is_stdlib_or_external(target: str, target_root: Optional[str] = None) -> bool:
    """
    Check if target appears to be stdlib or third-party.

    Heuristics:
    - Root module is in STDLIB_MODULES
    - Target contains 'site-packages'
    - Target has no file path component (bare module name)
    """
    # If it's a canonical ID with a path, check if path is under target_root
    if _is_canonical_id(target):
        # Extract path portion
        path_part = target.rsplit(':', 1)[0]
        if target_root:
            try:
                target_root_resolved = str(Path(target_root).resolve())
                if not path_part.startswith(target_root_resolved):
                    return True  # Path is outside target root
            except Exception:
                pass
        if 'site-packages' in path_part:
            return True
        return False

    # Bare name - check if it's a known stdlib module
    root_module = _get_module_root(target)
    if root_module in STDLIB_MODULES:
        return True

    # Common third-party packages (non-exhaustive, for quick wins)
    common_third_party = {
        'numpy', 'pandas', 'requests', 'flask', 'django', 'fastapi',
        'pytest', 'click', 'pydantic', 'sqlalchemy', 'aiohttp', 'httpx',
        'redis', 'celery', 'boto3', 'google', 'azure', 'openai', 'anthropic',
    }
    if root_module in common_third_party:
        return True

    return False


def resolve_edges(
    edges: List[Dict],
    node_ids: Set[str],
    target_root: Optional[str] = None,
    file_node_ids: Optional[Dict[str, str]] = None,
) -> List[Dict]:
    """
    Post-process edges to add resolution status.

    Resolution logic:
    - resolved_internal: target is in node_ids
    - external: target is stdlib/third-party (not in node_ids, looks external)
    - unresolved: cannot confidently resolve (target not in node_ids, not clearly external)

    Args:
        edges: List of edge dictionaries (must have source, target, edge_type)
        node_ids: Set of canonical node IDs from the analysis
        target_root: Root path of the analyzed codebase (for external detection)
        file_node_ids: Optional mapping of file path -> file-node id

    Returns:
        List of edges with 'resolution' field added

    Invariants:
    - Every returned edge has: source, target, edge_type, resolution
    - resolution="resolved_internal" ⇒ target ∈ node_ids
    - target is never empty
    """
    resolved_edges = []
    file_to_node_ids = _build_file_to_node_ids(node_ids)
    file_to_node_ids_casefold = {
        key.lower(): value for key, value in file_to_node_ids.items()
    }
    file_node_ids_casefold = {}
    if file_node_ids:
        file_node_ids_casefold = {key.lower(): value for key, value in file_node_ids.items()}
    target_root_resolved = str(Path(target_root).resolve()) if target_root else None

    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        edge_type = edge.get('edge_type', '')

        # Copy edge and add resolution
        resolved_edge = dict(edge)

        # Skip edges with empty target (shouldn't happen, but defensive)
        if not target:
            resolved_edge['resolution'] = 'unresolved'
            resolved_edges.append(resolved_edge)
            continue

        import_resolution_reason = None
        if edge_type == 'imports' and isinstance(target, str):
            if target.startswith('.'):
                import_resolution_reason = 'relative_import'
            elif target_root_resolved:
                resolved_path, ambiguous = resolve_import_target_to_file(
                    target, target_root_resolved
                )
                if ambiguous:
                    import_resolution_reason = 'ambiguous'
                elif resolved_path:
                    file_node_id_value = None
                    if file_node_ids:
                        file_node_id_value = file_node_ids.get(resolved_path)
                        if not file_node_id_value:
                            file_node_id_value = file_node_ids_casefold.get(resolved_path.lower())
                    if file_node_id_value:
                        resolved_edge['resolution'] = 'resolved_internal'
                        resolved_edge['target'] = file_node_id_value
                        resolved_edge['confidence'] = 1.0
                    else:
                        node_candidates = file_to_node_ids.get(resolved_path, [])
                        if not node_candidates:
                            node_candidates = file_to_node_ids_casefold.get(resolved_path.lower(), [])
                        if node_candidates:
                            resolved_edge['resolution'] = 'resolved_internal'
                            resolved_edge['target'] = node_candidates[0]
                            resolved_edge['confidence'] = 1.0
                        else:
                            import_resolution_reason = 'resolved_to_file_no_node'

        if resolved_edge.get('resolution') == 'resolved_internal':
            resolved_edges.append(resolved_edge)
            continue

        if import_resolution_reason:
            resolved_edge['resolution'] = 'unresolved'
            metadata = dict(resolved_edge.get('metadata') or {})
            metadata['import_resolution'] = import_resolution_reason
            resolved_edge['metadata'] = metadata
            resolved_edges.append(resolved_edge)
            continue

        # Check if both source and target are in our node set
        source_internal = source in node_ids
        target_internal = target in node_ids

        if target_internal:
            # Target is a known node → resolved_internal
            resolved_edge['resolution'] = 'resolved_internal'
        elif _is_stdlib_or_external(target, target_root):
            # Target looks like stdlib or third-party → external
            resolved_edge['resolution'] = 'external'
        elif edge_type == 'contains' and source_internal:
            # Containment edges where parent is known but child isn't
            # This can happen with nested classes/functions not fully extracted
            resolved_edge['resolution'] = 'unresolved'
        else:
            # Cannot confidently resolve → unresolved
            resolved_edge['resolution'] = 'unresolved'

        if 'confidence' not in resolved_edge:
            resolved_edge['confidence'] = 1.0

        resolved_edges.append(resolved_edge)

    return resolved_edges


def get_proof_edges(edges: List[Dict]) -> List[Dict]:
    """
    Filter edges for proof metrics calculation.

    Returns only edges where:
    - edge_type == "calls"
    - resolution == "resolved_internal"

    These are the only edges that count toward self-proof score.

    Args:
        edges: List of edge dictionaries with resolution field

    Returns:
        Filtered list of proof-relevant edges
    """
    return [
        edge for edge in edges
        if edge.get('edge_type') == 'calls'
        and edge.get('resolution') == 'resolved_internal'
    ]


def get_edge_resolution_summary(edges: List[Dict]) -> Dict[str, Dict[str, int]]:
    """
    Summarize edge resolution status by edge type.

    Returns:
        Dict mapping edge_type -> {resolution -> count}
    """
    summary: Dict[str, Dict[str, int]] = {}

    for edge in edges:
        edge_type = edge.get('edge_type', 'unknown')
        resolution = edge.get('resolution', 'missing')

        if edge_type not in summary:
            summary[edge_type] = {}

        summary[edge_type][resolution] = summary[edge_type].get(resolution, 0) + 1

    return summary


def get_import_resolution_diagnostics(edges: List[Dict]) -> Tuple[Dict[str, int], List[str]]:
    """
    Summarize import resolution diagnostics.

    Returns:
        (counts, top_unresolved_roots)
    """
    counts = {
        "attempted": 0,
        "resolved_internal": 0,
        "external": 0,
        "unresolved": 0,
        "resolved_to_file_no_node": 0,
        "ambiguous": 0,
    }
    root_counts: Dict[str, int] = {}

    for edge in edges:
        if edge.get("edge_type") != "imports":
            continue
        target = edge.get("target", "")
        if not target:
            continue
        if isinstance(target, str) and not target.startswith("."):
            counts["attempted"] += 1

        resolution = edge.get("resolution", "unresolved")
        if resolution == "resolved_internal":
            counts["resolved_internal"] += 1
        elif resolution == "external":
            counts["external"] += 1
        else:
            counts["unresolved"] += 1

        metadata = edge.get("metadata", {}) or {}
        reason = metadata.get("import_resolution")
        if reason == "resolved_to_file_no_node":
            counts["resolved_to_file_no_node"] += 1
        if reason == "ambiguous":
            counts["ambiguous"] += 1

        if resolution == "unresolved" and isinstance(target, str) and not target.startswith(".") and ":" not in target:
            root = target.split(".")[0]
            if root:
                root_counts[root] = root_counts.get(root, 0) + 1

    top_roots = [
        root for root, _ in sorted(root_counts.items(), key=lambda item: (-item[1], item[0]))
    ][:20]

    return counts, top_roots
    """
    Remove duplicate edges, keeping highest confidence.

    Args:
        edges: List of edge dictionaries

    Returns:
        Deduplicated list of edges
    """
    seen = {}

    for edge in edges:
        key = (edge['source'], edge['target'], edge['edge_type'])
        if key not in seen or edge.get('confidence', 0) > seen[key].get('confidence', 0):
            seen[key] = edge

    return list(seen.values())
