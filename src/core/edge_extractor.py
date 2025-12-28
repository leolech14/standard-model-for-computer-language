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
from typing import Dict, List


def extract_call_edges(particles: List[Dict], results: List[Dict]) -> List[Dict]:
    """
    Extract call relationships from particles and raw imports.
    Creates edges: {source, target, edge_type, file_path, line}

    Args:
        particles: List of classified particles
        results: Raw AST parse results with import data

    Returns:
        List of edge dictionaries
    """
    edges = []

    # Build particle lookup by name
    particle_by_name = {}
    for p in particles:
        name = p.get('name', '')
        if name:
            particle_by_name[name] = p
            # Also register short name
            short = name.split('.')[-1] if '.' in name else name
            if short not in particle_by_name:
                particle_by_name[short] = p

    # Extract imports from each file
    for result in results:
        file_path = result.get('file_path', '')
        raw_imports = result.get('raw_imports', [])

        # Get file's particles
        file_particles = [p for p in particles if p.get('file_path') == file_path]

        for imp in raw_imports:
            # Create import edge - ensure target is always a string
            source_module = Path(file_path).stem if file_path else 'unknown'

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
                    'source': source_module,
                    'target': str(target_module),  # Ensure string
                    'edge_type': 'imports',
                    'file_path': file_path,
                    'line': line,
                    'confidence': 1.0,
                })

    # Extract containment edges (parent-child)
    for p in particles:
        parent = p.get('parent', '')
        if parent:
            edges.append({
                'source': parent,
                'target': p.get('name', ''),
                'edge_type': 'contains',
                'file_path': p.get('file_path', ''),
                'line': p.get('line', 0),
                'confidence': 1.0,
            })

    # Extract inheritance edges
    for p in particles:
        base_classes = p.get('base_classes', [])
        for base in base_classes:
            if base and base not in ('object', 'ABC', 'Protocol'):
                edges.append({
                    'source': p.get('name', ''),
                    'target': base,
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
                    edges.append({
                        'source': caller_name,
                        'target': call,
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
                    edges.append({
                        'source': caller_name,
                        'target': accessed,
                        'edge_type': 'uses',
                        'file_path': p.get('file_path', ''),
                        'line': p.get('line', 0),
                        'confidence': 0.8,  # Attribute access detection
                    })

    return edges


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
