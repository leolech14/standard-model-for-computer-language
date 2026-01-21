#!/usr/bin/env python3
"""
COLLIDER EDGE EXTRACTOR
=======================

Extracts relationships (edges) between code elements.
Creates a call graph from particles and import data.

Polyglot Support:
Uses EdgeExtractionStrategy to handle language-specific call/usage extraction
from source bodies.

Edge Types:
- imports: Module imports another module
- contains: Class contains method, module contains class
- calls: Function/method calls another function
- inherits: Class inherits from another class
- uses: General usage relationship
- exposes: Module/file exports a symbol (CommonJS or ES6)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from abc import ABC, abstractmethod

# Tree-sitter imports (optional, for high-precision extraction)
try:
    import tree_sitter
    import tree_sitter_python
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    tree_sitter = None
    tree_sitter_python = None

try:
    import tree_sitter_javascript
except ImportError:
    tree_sitter_javascript = None

try:
    import tree_sitter_typescript
except ImportError:
    tree_sitter_typescript = None


# =============================================================================
# JS MODULE RESOLVER - Track aliases, window exports, and resolve member calls
# =============================================================================

class JSModuleResolver:
    """
    Resolves JavaScript module references across files.

    Tracks:
    - window.X = X patterns (global exports)
    - const X = require('./file') (CommonJS)
    - import X from './file' (ES6)
    - IIFE module patterns

    Usage:
        resolver = JSModuleResolver()
        resolver.analyze_file(file_path, content, parser)
        target = resolver.resolve_member_call('COLOR', 'subscribe', caller_file)
    """

    def __init__(self):
        # Map: global_name -> file_path (e.g., 'COLOR' -> 'color-engine.js')
        self.window_exports: Dict[str, str] = {}
        # Map: (file_path, local_name) -> source_module (e.g., ('app.js', 'COLOR') -> 'color-engine.js')
        self.import_aliases: Dict[Tuple[str, str], str] = {}
        # Map: file_path -> module_name (e.g., 'color-engine.js' -> 'COLOR')
        self.file_to_module: Dict[str, str] = {}
        # Parser for JS
        self.parser = None
        if TREE_SITTER_AVAILABLE and tree_sitter_javascript:
            try:
                lang = tree_sitter.Language(tree_sitter_javascript.language())
                self.parser = tree_sitter.Parser()
                self.parser.language = lang
            except Exception:
                pass

    def analyze_file(self, file_path: str, content: str) -> None:
        """Analyze a JS file to extract module aliases and exports."""
        if not self.parser or not content:
            return

        source_bytes = content.encode('utf-8')
        try:
            tree = self.parser.parse(source_bytes)
        except Exception:
            return

        file_name = Path(file_path).stem  # e.g., 'color-engine'

        def visit(node):
            # Pattern 1: window.X = X or window.X = {...}
            if node.type == 'assignment_expression':
                left = node.child_by_field_name('left')
                if left and left.type == 'member_expression':
                    obj = left.child_by_field_name('object')
                    prop = left.child_by_field_name('property')
                    if obj and prop and obj.text == b'window':
                        export_name = prop.text.decode()
                        self.window_exports[export_name] = file_path
                        self.file_to_module[file_path] = export_name

            # Pattern 2: const X = require('./file')
            if node.type == 'variable_declarator':
                name_node = node.child_by_field_name('name')
                value_node = node.child_by_field_name('value')
                if name_node and value_node and value_node.type == 'call_expression':
                    func = value_node.child_by_field_name('function')
                    if func and func.text == b'require':
                        args = value_node.child_by_field_name('arguments')
                        if args and args.child_count > 0:
                            arg = args.children[0] if args.children else None
                            if arg and arg.type == 'string':
                                module_path = arg.text.decode().strip('\'"')
                                local_name = name_node.text.decode()
                                self.import_aliases[(file_path, local_name)] = module_path

            # Pattern 3: import X from './file' or import { X } from './file'
            if node.type == 'import_statement':
                source_node = None
                for child in node.children:
                    if child.type == 'string':
                        source_node = child
                        break
                if source_node:
                    module_path = source_node.text.decode().strip('\'"')
                    # Find the imported names
                    for child in node.children:
                        if child.type == 'identifier':
                            local_name = child.text.decode()
                            self.import_aliases[(file_path, local_name)] = module_path
                        elif child.type == 'import_clause':
                            for subchild in child.children:
                                if subchild.type == 'identifier':
                                    local_name = subchild.text.decode()
                                    self.import_aliases[(file_path, local_name)] = module_path
                                elif subchild.type == 'named_imports':
                                    for spec in subchild.children:
                                        if spec.type == 'import_specifier':
                                            name = spec.child_by_field_name('name')
                                            if name:
                                                local_name = name.text.decode()
                                                self.import_aliases[(file_path, local_name)] = module_path

            # Pattern 4: const X = (function() {...})() - IIFE globals (browser script pattern)
            # These become globals in browser scripts loaded via <script> tags
            if node.type == 'lexical_declaration':
                for declarator in node.children:
                    if declarator.type == 'variable_declarator':
                        name_node = declarator.child_by_field_name('name')
                        value_node = declarator.child_by_field_name('value')
                        if name_node and name_node.type == 'identifier':
                            export_name = name_node.text.decode()
                            # Check if it's an IIFE: (function() {...})() or (() => {...})()
                            if value_node and value_node.type == 'call_expression':
                                func = value_node.child_by_field_name('function')
                                if func and func.type == 'parenthesized_expression':
                                    # It's an IIFE - register as a global
                                    if export_name not in self.window_exports:
                                        self.window_exports[export_name] = file_path
                                        self.file_to_module[file_path] = export_name

            for child in node.children:
                visit(child)

        visit(tree.root_node)

    def resolve_member_call(
        self,
        object_name: str,
        method_name: str,
        caller_file: str,
        particle_by_name: Dict[str, List[Dict]]
    ) -> Optional[Dict]:
        """
        Resolve a member call like COLOR.subscribe() to its target particle.

        Args:
            object_name: The object being called on (e.g., 'COLOR')
            method_name: The method being called (e.g., 'subscribe')
            caller_file: The file containing the call
            particle_by_name: Dict mapping names to particles

        Returns:
            The target particle, or None if not resolved
        """
        # Skip built-in objects
        if object_name in ('document', 'window', 'console', 'Math', 'JSON', 'Object', 'Array', 'String', 'Number'):
            return None

        # Strategy 1: Check window exports
        if object_name in self.window_exports:
            target_file = self.window_exports[object_name]
            # Look for method in that file
            candidates = particle_by_name.get(method_name, [])
            for c in candidates:
                if c.get('file_path') == target_file:
                    return c

        # Strategy 2: Check import aliases for this file
        alias_key = (caller_file, object_name)
        if alias_key in self.import_aliases:
            module_path = self.import_aliases[alias_key]
            # Resolve relative path
            if module_path.startswith('.'):
                caller_dir = str(Path(caller_file).parent)
                resolved = str(Path(caller_dir) / module_path)
                # Try with .js extension
                for ext in ['', '.js', '/index.js']:
                    test_path = resolved + ext
                    candidates = particle_by_name.get(method_name, [])
                    for c in candidates:
                        if test_path in c.get('file_path', ''):
                            return c

        # Strategy 3: Fuzzy match - object name might match file name
        # e.g., COLOR might come from color-engine.js or color.js
        # NOTE: Require match at START of filename to avoid false positives like
        # 'dm' matching 'legen-dm-anager' (substring match in wrong place)
        object_lower = object_name.lower()
        candidates = particle_by_name.get(method_name, [])
        for c in candidates:
            file_stem = Path(c.get('file_path', '')).stem.lower().replace('-', '').replace('_', '')
            # Match if object name starts the filename OR filename starts the object name
            # e.g., 'color' matches 'colorengine', 'data' matches 'datamanager'
            if file_stem.startswith(object_lower) or object_lower.startswith(file_stem):
                return c

        return None

    def get_stats(self) -> Dict[str, int]:
        """Return statistics about resolved modules."""
        return {
            'window_exports': len(self.window_exports),
            'import_aliases': len(self.import_aliases),
            'file_to_module': len(self.file_to_module),
        }


# Global resolver instance (populated during analysis)
_js_module_resolver: Optional[JSModuleResolver] = None


def get_js_module_resolver() -> JSModuleResolver:
    """Get or create the global JS module resolver."""
    global _js_module_resolver
    if _js_module_resolver is None:
        _js_module_resolver = JSModuleResolver()
    return _js_module_resolver


def reset_js_module_resolver() -> None:
    """Reset the global resolver (for testing or fresh analysis)."""
    global _js_module_resolver
    _js_module_resolver = None


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


def _find_target_particle(
    call_name: str,
    caller_file: str,
    particle_by_name: Dict[str, List[Dict]]
) -> Optional[Dict]:
    """
    Find target particle for a call, preferring same-file matches.

    This handles duplicate function names across files (e.g., 'init', 'clamp01').
    When a function calls another function with the same name as one in its own file,
    the same-file version should be preferred (respects module scope).

    Args:
        call_name: The name being called
        caller_file: The file path of the caller
        particle_by_name: Dict mapping names to LIST of particles with that name

    Returns:
        The best matching particle, or None if not found
    """
    candidates = particle_by_name.get(call_name, [])
    if not candidates:
        return None

    # Prefer same-file match (respects module scope)
    for candidate in candidates:
        if candidate.get('file_path') == caller_file:
            return candidate

    # Fallback to first match (cross-file reference)
    return candidates[0]


# =============================================================================
# STRATEGY PATTERN FOR BODY ANALYSIS
# =============================================================================

class EdgeExtractionStrategy(ABC):
    """Abstract base class for language-specific edge extraction from source bodies."""

    @abstractmethod
    def extract_edges(self, particle: Dict, particle_by_name: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Extract 'calls' and 'uses' edges from a single particle's body_source.

        Args:
            particle: The calling particle (function/method/class)
            particle_by_name: Dict mapping names to LIST of particles with that name
                             (supports duplicate names across files)
        """
        pass


class PythonEdgeStrategy(EdgeExtractionStrategy):
    """Extraction logic for Python (regex-based heuristics)."""

    def extract_edges(self, particle: Dict, particle_by_name: Dict[str, List[Dict]]) -> List[Dict]:
        edges = []
        body = particle.get('body_source', '')
        if not body:
            return edges

        caller_id = _get_particle_id(particle)
        caller_name = particle.get('name', '')
        caller_file = particle.get('file_path', '')
        caller_short = caller_name.split('.')[-1] if '.' in caller_name else caller_name

        # Look for function calls: func() or self.method()
        calls = re.findall(r'(?:self\.)?(\w+)\s*\(', body)

        for call in calls:
            # Skip self-calls and common built-ins
            if call == caller_short:
                continue
            if call in ('print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
                       'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'isinstance',
                       'hasattr', 'getattr', 'setattr', 'open', 'super', 'type', 'id'):
                continue

            target = _find_target_particle(call, caller_file, particle_by_name)
            if target:
                target_id = _get_particle_id(target)
                edges.append({
                    'source': caller_id,
                    'target': target_id,
                    'edge_type': 'calls',
                    'family': 'Dependency',
                    'file_path': caller_file,
                    'line': particle.get('line', 0),
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
            target = _find_target_particle(accessed, caller_file, particle_by_name)
            if target:
                target_id = _get_particle_id(target)
                edges.append({
                    'source': caller_id,
                    'target': target_id,
                    'edge_type': 'uses',
                    'family': 'Dependency',
                    'file_path': caller_file,
                    'line': particle.get('line', 0),
                    'confidence': 0.8,  # Attribute access detection
                })

        return edges


class JavascriptEdgeStrategy(EdgeExtractionStrategy):
    """Extraction logic for JavaScript/TypeScript."""

    def extract_edges(self, particle: Dict, particle_by_name: Dict[str, List[Dict]]) -> List[Dict]:
        edges = []
        body = particle.get('body_source', '')
        if not body:
            return edges

        caller_id = _get_particle_id(particle)
        caller_file = particle.get('file_path', '')

        # JS Calls: func(), obj.method(), this.method()
        # Heuristic: word followed by (
        calls = re.findall(r'(?:this\.|[\w]+\.)?(\w+)\s*\(', body)

        for call in calls:
            if call in ('console', 'log', 'alert', 'push', 'pop', 'map', 'filter', 'forEach',
                       'reduce', 'length', 'toString', 'parseInt', 'parseFloat', 'require'):
                continue

            target = _find_target_particle(call, caller_file, particle_by_name)
            if target:
                target_id = _get_particle_id(target)
                edges.append({
                    'source': caller_id,
                    'target': target_id,
                    'edge_type': 'calls',
                    'family': 'Dependency',
                    'file_path': caller_file,
                    'line': particle.get('line', 0),
                    'confidence': 0.7,
                })

        # New instantiation
        news = re.findall(r'new\s+(\w+)\s*\(', body)
        for cls in news:
            target = _find_target_particle(cls, caller_file, particle_by_name)
            if target:
                target_id = _get_particle_id(target)
                edges.append({
                    'source': caller_id,
                    'target': target_id,
                    'edge_type': 'calls',  # Constructor call
                    'family': 'Dependency',
                    'file_path': caller_file,
                    'line': particle.get('line', 0),
                    'confidence': 0.9,
                })

        return edges


class TypeScriptEdgeStrategy(JavascriptEdgeStrategy):
    """Extraction logic for TypeScript (inherits JS + type usages)."""
    # JS regex covers most calls. Could add type annotation extraction if needed.
    pass


class GoEdgeStrategy(EdgeExtractionStrategy):
    """Extraction logic for Go."""

    def extract_edges(self, particle: Dict, particle_by_name: Dict[str, List[Dict]]) -> List[Dict]:
        edges = []
        body = particle.get('body_source', '')
        if not body:
            return edges

        caller_id = _get_particle_id(particle)
        caller_file = particle.get('file_path', '')

        # Go calls: Pkg.Func(), func()
        calls = re.findall(r'(?:[\w]+\.)?(\w+)\s*\(', body)

        for call in calls:
            if call in ('println', 'fmt', 'len', 'append', 'make', 'new', 'panic', 'copy'):
                continue

            target = _find_target_particle(call, caller_file, particle_by_name)
            if target:
                target_id = _get_particle_id(target)
                edges.append({
                    'source': caller_id,
                    'target': target_id,
                    'edge_type': 'calls',
                    'family': 'Dependency',
                    'file_path': caller_file,
                    'line': particle.get('line', 0),
                    'confidence': 0.7,
                })
        return edges


class RustEdgeStrategy(EdgeExtractionStrategy):
    """Extraction logic for Rust."""

    def extract_edges(self, particle: Dict, particle_by_name: Dict[str, List[Dict]]) -> List[Dict]:
        edges = []
        body = particle.get('body_source', '')
        if not body:
            return edges

        caller_id = _get_particle_id(particle)
        caller_file = particle.get('file_path', '')

        # Rust calls: func(), module::func(), struct.method()
        calls = re.findall(r'(?:[\w:]+\.|[\w:]+::)?(\w+)\s*\(', body)

        for call in calls:
            if call in ('println', 'vec', 'Some', 'None', 'Ok', 'Err', 'unwrap', 'clone', 'to_string'):
                continue

            target = _find_target_particle(call, caller_file, particle_by_name)
            if target:
                target_id = _get_particle_id(target)
                edges.append({
                    'source': caller_id,
                    'target': target_id,
                    'edge_type': 'calls',
                    'family': 'Dependency',
                    'file_path': caller_file,
                    'line': particle.get('line', 0),
                    'confidence': 0.7,
                })
        return edges


class DefaultEdgeStrategy(EdgeExtractionStrategy):
    """Fallback strategy for unknown languages (no body analysis)."""

    def extract_edges(self, particle: Dict, particle_by_name: Dict[str, List[Dict]]) -> List[Dict]:
        return []


# =============================================================================
# TREE-SITTER BASED STRATEGIES (High Precision)
# =============================================================================

class TreeSitterEdgeStrategy(EdgeExtractionStrategy):
    """
    Base class for Tree-sitter based edge extraction.
    Parses body_source as AST and runs queries for precise call detection.
    """
    
    def __init__(self, parser: Any, language_name: str):
        self.parser = parser
        self.language_name = language_name
    
    def get_call_node_types(self) -> Set[str]:
        """Return set of AST node types that represent function calls."""
        return {'call', 'call_expression'}
    
    def extract_callee_name(self, node: Any, source_bytes: bytes) -> Optional[str]:
        """Extract the function/method name from a call node."""
        # Try 'function' field first (Python, JS)
        func_node = node.child_by_field_name('function')
        if func_node:
            # Direct identifier: func()
            if func_node.type == 'identifier':
                return func_node.text.decode()
            # Attribute access: obj.method() or self.method()
            if func_node.type in ('attribute', 'member_expression'):
                # Get the rightmost identifier (the method name)
                attr = func_node.child_by_field_name('attribute') or func_node.child_by_field_name('property')
                if attr:
                    return attr.text.decode()
        return None
    
    def extract_edges(self, particle: Dict, particle_by_name: Dict[str, List[Dict]]) -> List[Dict]:
        edges = []
        body = particle.get('body_source', '')
        if not body or not self.parser:
            return edges

        caller_id = _get_particle_id(particle)
        caller_file = particle.get('file_path', '')
        source_bytes = body.encode('utf-8')

        try:
            tree = self.parser.parse(source_bytes)
        except Exception:
            return edges  # Fallback to empty if parsing fails

        call_types = self.get_call_node_types()
        found_calls: Set[str] = set()

        def visit(node):
            if node.type in call_types:
                callee = self.extract_callee_name(node, source_bytes)
                if callee:
                    found_calls.add(callee)
            for child in node.children:
                visit(child)

        visit(tree.root_node)

        # Match against known particles (prefer same-file)
        for call in found_calls:
            target = _find_target_particle(call, caller_file, particle_by_name)
            if target:
                target_id = _get_particle_id(target)
                edges.append({
                    'source': caller_id,
                    'target': target_id,
                    'edge_type': 'calls',
                    'family': 'Dependency',
                    'file_path': caller_file,
                    'line': particle.get('line', 0),
                    'confidence': 0.95,  # High confidence from AST
                })

        return edges


class PythonTreeSitterStrategy(TreeSitterEdgeStrategy):
    """Tree-sitter based Python call extraction."""
    
    def __init__(self):
        parser = None
        if TREE_SITTER_AVAILABLE and tree_sitter_python:
            try:
                lang = tree_sitter.Language(tree_sitter_python.language())
                parser = tree_sitter.Parser()
                parser.language = lang
            except Exception:
                parser = None
        super().__init__(parser, 'python')
    
    def get_call_node_types(self) -> Set[str]:
        return {'call'}


class JavaScriptTreeSitterStrategy(TreeSitterEdgeStrategy):
    """
    Tree-sitter based JavaScript/JSX call extraction with module resolution.

    Enhanced to handle:
    - Direct calls: func()
    - Member calls: COLOR.subscribe() -> resolved via JSModuleResolver
    - Constructor calls: new ClassName()
    - Callbacks: addEventListener('click', handler)
    - Method chaining: obj.method1().method2()
    """

    def __init__(self):
        parser = None
        if TREE_SITTER_AVAILABLE and tree_sitter_javascript:
            try:
                lang = tree_sitter.Language(tree_sitter_javascript.language())
                parser = tree_sitter.Parser()
                parser.language = lang
            except Exception:
                parser = None
        super().__init__(parser, 'javascript')

    def get_call_node_types(self) -> Set[str]:
        return {'call_expression', 'new_expression'}

    def extract_member_call(self, node: Any, source_bytes: bytes) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract both object and method from a member call.

        Returns:
            (object_name, method_name) tuple, e.g., ('COLOR', 'subscribe')
            (None, method_name) for direct calls like func()
        """
        func_node = node.child_by_field_name('function')
        if not func_node:
            return (None, None)

        # Direct call: func()
        if func_node.type == 'identifier':
            return (None, func_node.text.decode())

        # Member call: obj.method() or this.method()
        if func_node.type == 'member_expression':
            obj_node = func_node.child_by_field_name('object')
            prop_node = func_node.child_by_field_name('property')
            if obj_node and prop_node:
                # Handle 'this' keyword - return 'this' as obj_name for semantic tracking
                # (resolution will use same-file preference which is correct for this)
                if obj_node.type == 'this':
                    obj_name = 'this'
                elif obj_node.type == 'identifier':
                    obj_name = obj_node.text.decode()
                else:
                    obj_name = None
                method_name = prop_node.text.decode() if prop_node.type == 'property_identifier' else None
                return (obj_name, method_name)

        return (None, None)

    def extract_callback_args(self, node: Any, source_bytes: bytes) -> List[str]:
        """
        Extract callback function references from call arguments.

        Handles patterns like:
        - addEventListener('click', handleClick)
        - array.map(processItem)
        - promise.then(onSuccess, onError)
        """
        callbacks = []
        args_node = node.child_by_field_name('arguments')
        if not args_node:
            return callbacks

        for arg in args_node.children:
            # Direct function reference: addEventListener('click', handler)
            if arg.type == 'identifier':
                callbacks.append(arg.text.decode())
            # Could also handle arrow functions with named calls inside, but that's complex

        return callbacks

    def extract_callee_name(self, node: Any, source_bytes: bytes) -> Optional[str]:
        """Extract just the method name (for backward compatibility)."""
        if node.type == 'new_expression':
            constructor = node.child_by_field_name('constructor')
            if constructor and constructor.type == 'identifier':
                return constructor.text.decode()
        _, method = self.extract_member_call(node, source_bytes)
        return method

    def extract_edges(self, particle: Dict, particle_by_name: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Extract edges with full module resolution for JS.

        Enhanced to:
        1. Resolve member calls via JSModuleResolver
        2. Track callback references
        3. Fall back to same-file preference for unresolved calls
        """
        edges = []
        body = particle.get('body_source', '')
        if not body or not self.parser:
            return edges

        caller_id = _get_particle_id(particle)
        caller_file = particle.get('file_path', '')
        source_bytes = body.encode('utf-8')

        try:
            tree = self.parser.parse(source_bytes)
        except Exception:
            return edges

        resolver = get_js_module_resolver()
        call_types = self.get_call_node_types()
        # Key by (obj_name, method_name) to avoid dropping edges when different objects
        # call the same method name (e.g., ANIM.init() vs GRAPH.init())
        processed: Set[Tuple[Optional[str], str]] = set()

        def visit(node):
            if node.type in call_types:
                # Extract full member call info
                obj_name, method_name = self.extract_member_call(node, source_bytes)

                if method_name:
                    edge_key = (obj_name, method_name)
                    if edge_key not in processed:
                        processed.add(edge_key)
                        target = None

                        # Strategy 1: If it's 'this.method()', use same-file preference directly
                        # (this refers to methods in the same class/object)
                        if obj_name == 'this':
                            target = _find_target_particle(method_name, caller_file, particle_by_name)

                        # Strategy 2: If it's a member call (obj.method), use resolver
                        elif obj_name:
                            target = resolver.resolve_member_call(
                                obj_name, method_name, caller_file, particle_by_name
                            )

                        # Strategy 3: Fall back to same-file preference for direct calls
                        if not target:
                            target = _find_target_particle(method_name, caller_file, particle_by_name)

                        if target:
                            target_id = _get_particle_id(target)
                            edges.append({
                                'source': caller_id,
                                'target': target_id,
                                'edge_type': 'calls',
                                'family': 'Dependency',
                                'file_path': caller_file,
                                'line': particle.get('line', 0),
                                'confidence': 0.95 if obj_name and obj_name != 'this' else 0.85,
                            })

                # Also extract callbacks from arguments
                callbacks = self.extract_callback_args(node, source_bytes)
                for cb_name in callbacks:
                    cb_key = (None, cb_name)  # Callbacks are direct references (no object)
                    if cb_key not in processed:
                        processed.add(cb_key)
                        target = _find_target_particle(cb_name, caller_file, particle_by_name)
                        if target:
                            target_id = _get_particle_id(target)
                            edges.append({
                                'source': caller_id,
                                'target': target_id,
                                'edge_type': 'calls',
                                'family': 'Dependency',
                                'file_path': caller_file,
                                'line': particle.get('line', 0),
                                'confidence': 0.80,  # Callback reference
                            })

            for child in node.children:
                visit(child)

        visit(tree.root_node)
        return edges


class TypeScriptTreeSitterStrategy(TreeSitterEdgeStrategy):
    """Tree-sitter based TypeScript/TSX call extraction."""
    
    def __init__(self):
        parser = None
        if TREE_SITTER_AVAILABLE and tree_sitter_typescript:
            try:
                lang = tree_sitter.Language(tree_sitter_typescript.language_typescript())
                parser = tree_sitter.Parser()
                parser.language = lang
            except Exception:
                parser = None
        super().__init__(parser, 'typescript')
    
    def get_call_node_types(self) -> Set[str]:
        return {'call_expression', 'new_expression'}
    
    def extract_callee_name(self, node: Any, source_bytes: bytes) -> Optional[str]:
        if node.type == 'new_expression':
            constructor = node.child_by_field_name('constructor')
            if constructor and constructor.type == 'identifier':
                return constructor.text.decode()
        return super().extract_callee_name(node, source_bytes)


# =============================================================================
# STRATEGY FACTORY (Updated with Tree-sitter priority)
# =============================================================================

def get_strategy_for_file(file_path: str) -> EdgeExtractionStrategy:
    """
    Factory to get the correct strategy based on file extension.
    Prefers Tree-sitter strategies when available, falls back to regex.
    """
    if file_path.endswith('.py'):
        # Try Tree-sitter first
        if TREE_SITTER_AVAILABLE and tree_sitter_python:
            strategy = PythonTreeSitterStrategy()
            if strategy.parser:
                return strategy
        return PythonEdgeStrategy()  # Regex fallback
    
    if file_path.endswith('.js') or file_path.endswith('.jsx'):
        if TREE_SITTER_AVAILABLE and tree_sitter_javascript:
            strategy = JavaScriptTreeSitterStrategy()
            if strategy.parser:
                return strategy
        return JavascriptEdgeStrategy()  # Regex fallback
    
    if file_path.endswith('.ts') or file_path.endswith('.tsx'):
        if TREE_SITTER_AVAILABLE and tree_sitter_typescript:
            strategy = TypeScriptTreeSitterStrategy()
            if strategy.parser:
                return strategy
        return TypeScriptEdgeStrategy()  # Regex fallback
    
    if file_path.endswith('.go'):
        return GoEdgeStrategy()
    if file_path.endswith('.rs'):
        return RustEdgeStrategy()
    return DefaultEdgeStrategy()


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

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

    # -------------------------------------------------------------------------
    # 0. INITIALIZE JS MODULE RESOLVER
    # -------------------------------------------------------------------------
    # Reset and populate the resolver with all JS files for cross-module resolution
    reset_js_module_resolver()
    resolver = get_js_module_resolver()

    # Populate resolver with JS file contents (need raw_content from results)
    for result in results:
        file_path = result.get('file_path', '')
        if file_path.endswith('.js') or file_path.endswith('.jsx'):
            # Get content from the result if available, or read from file
            content = result.get('raw_content', '')
            if not content and file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    content = ''
            if content:
                resolver.analyze_file(file_path, content)

    # Build particle lookup by name (storing LISTS to handle duplicates across files)
    # and by full ID (skip file nodes)
    from collections import defaultdict
    particle_by_name: Dict[str, List[Dict]] = defaultdict(list)
    particle_by_id = {}
    for p in particles:
        metadata = p.get("metadata") or {}
        if metadata.get("file_node"):
            continue
        name = p.get('name', '')
        particle_id = _get_particle_id(p)
        if name:
            particle_by_name[name].append(p)
            # Also register short name
            short = name.split('.')[-1] if '.' in name else name
            if short != name:
                particle_by_name[short].append(p)
        if particle_id:
            particle_by_id[particle_id] = p

    file_node_ids = _collect_file_node_ids(particles)

    # -------------------------------------------------------------------------
    # 1. IMPORTS
    # -------------------------------------------------------------------------
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
                    'family': 'Dependency',
                    'file_path': file_path,
                    'line': line,
                    'confidence': 1.0,
                })

    # -------------------------------------------------------------------------
    # 2. CONTAINMENT & INHERITANCE (Structure)
    # -------------------------------------------------------------------------
    for p in particles:
        # Containment
        parent = p.get('parent', '')
        if parent:
            file_path = p.get('file_path', '')
            source_id = _make_node_id(file_path, parent)
            target_id = _get_particle_id(p)
            edges.append({
                'source': source_id,
                'target': target_id,
                'edge_type': 'contains',
                'family': 'Structural',
                'file_path': file_path,
                'line': p.get('line', 0),
                'confidence': 1.0,
            })

        # Inheritance
        base_classes = p.get('base_classes', [])
        caller_file = p.get('file_path', '')
        for base in base_classes:
            if base and base not in ('object', 'ABC', 'Protocol'):
                source_id = _get_particle_id(p)
                # Look up base class in known particles (prefer same-file)
                target_particle = _find_target_particle(base, caller_file, particle_by_name)
                if target_particle:
                    target_id = _get_particle_id(target_particle)
                else:
                    target_id = base  # External class, keep as name
                edges.append({
                    'source': source_id,
                    'target': target_id,
                    'edge_type': 'inherits',
                    'family': 'Inheritance',
                    'file_path': caller_file,
                    'line': p.get('line', 0),
                    'confidence': 1.0,
                })

    # -------------------------------------------------------------------------
    # 3. CALLS & USES (Body Analysis via Strategy)
    # -------------------------------------------------------------------------
    for p in particles:
        file_path = p.get('file_path', '')
        strategy = get_strategy_for_file(file_path)
        
        # Use strategy to extract body-level edges
        body_edges = strategy.extract_edges(p, particle_by_name)
        edges.extend(body_edges)

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
                    'family': 'Semantic',
                    'file_path': p.get('file_path', ''),
                    'line': p.get('line', 0),
                    'confidence': 1.0,
                })

    return edges


def _extract_exposure_edges_from_body(body: str, file_path: str, particle_by_name: Dict[str, List[Dict]]) -> List[Tuple[str, str]]:
    """
    Extract module.exports, export statements from source code.

    Returns list of (exported_symbol_name, export_type) tuples.
    Export types: 'named', 'default', 'commonjs'
    """
    exposures = []

    if not body:
        return exposures

    # CommonJS patterns
    # Pattern 1: module.exports = X (not module.exports.X)
    module_exports = re.findall(r'module\.exports\s*=\s*(\w+)(?!\.)', body)
    for sym in module_exports:
        if sym and sym not in ('null', 'undefined'):
            exposures.append((sym, 'commonjs'))

    # Pattern 2: module.exports.X = Y
    module_exports_named = re.findall(r'module\.exports\.(\w+)\s*=', body)
    for sym in module_exports_named:
        if sym:
            exposures.append((sym, 'commonjs'))

    # Pattern 3: exports.X = Y (shorthand for module.exports.X, but NOT module.exports)
    # Use negative lookbehind to exclude "module.exports"
    exports_named = re.findall(r'(?<!module\.)exports\.(\w+)\s*=', body)
    for sym in exports_named:
        if sym:
            exposures.append((sym, 'commonjs'))

    # ES6 patterns
    # Pattern 4: export function X or export const X or export let X or export var X
    export_func_const = re.findall(r'export\s+(?:function|const|let|var)\s+(\w+)', body)
    for sym in export_func_const:
        if sym:
            exposures.append((sym, 'named'))

    # Pattern 5: export class X
    export_class = re.findall(r'export\s+class\s+(\w+)', body)
    for sym in export_class:
        if sym:
            exposures.append((sym, 'named'))

    # Pattern 6: export default X
    export_default = re.findall(r'export\s+default\s+(\w+|\{[^}]+\})', body)
    for sym in export_default:
        if sym and sym not in ('function', 'class'):
            # Clean up object literals
            sym = sym.strip('{}').split(',')[0].strip() if '{' in sym else sym
            if sym:
                exposures.append((sym, 'default'))

    # Pattern 7: export { X, Y, Z } - named exports
    export_named_list = re.findall(r'export\s+\{\s*([^}]+)\s*\}', body)
    for exports_str in export_named_list:
        # Split by comma and extract names
        names = re.findall(r'(\w+)(?:\s+as\s+\w+)?', exports_str)
        for name in names:
            if name:
                exposures.append((name, 'named'))

    # Python patterns
    # Pattern 8: __all__ = ['X', 'Y', 'Z']
    all_exports = re.findall(r'__all__\s*=\s*\[([^\]]+)\]', body)
    for exports_str in all_exports:
        # Extract quoted strings
        names = re.findall(r'[\'"](\w+)[\'"]', exports_str)
        for name in names:
            if name:
                exposures.append((name, 'python_all'))

    return exposures


def extract_exposure_edges(particles: List[Dict], particle_by_name: Optional[Dict[str, List[Dict]]] = None, results: Optional[List[Dict]] = None) -> List[Dict]:
    """
    Extract exposure relationships (module.exports, export statements).

    These represent what a module/file exposes to its consumers.

    Exposures can be detected at:
    1. Module level (from raw file content in results)
    2. Particle level (from function/class body_source)

    Args:
        particles: List of classified particles
        particle_by_name: Optional lookup dict for resolving symbol names
        results: Optional raw AST results with file content

    Returns:
        List of exposure edge dictionaries with edge_type='exposes'
    """
    edges = []
    seen_files = set()

    # Build particle_by_name lookup if not provided
    if particle_by_name is None:
        from collections import defaultdict
        particle_by_name = defaultdict(list)
        for p in particles:
            name = p.get('name', '')
            if name:
                particle_by_name[name].append(p)
                # Also register short name
                short = name.split('.')[-1] if '.' in name else name
                if short != name:
                    particle_by_name[short].append(p)

    # PHASE 1: Extract module-level exposures from results (raw file content)
    # This catches top-level exports/module.exports statements
    if results:
        for result in results:
            file_path = result.get('file_path', '')
            if not file_path:
                continue

            # Skip if we've already processed this file
            if file_path in seen_files:
                continue
            seen_files.add(file_path)

            # Get file content
            raw_content = result.get('raw_content', '')
            if not raw_content:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        raw_content = f.read()
                except Exception:
                    continue

            # Extract exposures from module-level code
            exposures = _extract_exposure_edges_from_body(raw_content, file_path, particle_by_name)

            if not exposures:
                continue

            # Create a module node ID for the source
            # Use the file path as the source module
            source_id = _make_node_id(file_path, '__module__')

            for exported_name, export_type in exposures:
                # Look up the exported symbol to get its full ID
                target_particle = _find_target_particle(exported_name, file_path, particle_by_name)

                if target_particle:
                    target_id = _get_particle_id(target_particle)
                else:
                    # Symbol not found in particles - might be external or unclassified
                    target_id = _make_node_id(file_path, exported_name)

                edges.append({
                    'source': source_id,
                    'target': target_id,
                    'edge_type': 'exposes',
                    'family': 'Exposure',
                    'file_path': file_path,
                    'line': 0,  # Top-level, no specific line
                    'confidence': 0.95,  # High confidence for explicit exports
                    'metadata': {
                        'export_type': export_type,
                        'exported_name': exported_name,
                    }
                })

    # PHASE 2: Extract particle-level exposures (exposures inside functions/classes)
    # Less common but possible in some patterns
    for p in particles:
        body = p.get('body_source', '')
        if not body:
            continue

        file_path = p.get('file_path', '')
        particle_id = _get_particle_id(p)

        # Skip if we already processed this file at module level
        if file_path in seen_files:
            continue

        # Extract exposure statements from this particle
        exposures = _extract_exposure_edges_from_body(body, file_path, particle_by_name)

        for exported_name, export_type in exposures:
            # Look up the exported symbol to get its full ID
            target_particle = _find_target_particle(exported_name, file_path, particle_by_name)

            if target_particle:
                target_id = _get_particle_id(target_particle)
            else:
                # Symbol not found in particles - might be external or unclassified
                target_id = _make_node_id(file_path, exported_name)

            edges.append({
                'source': particle_id,
                'target': target_id,
                'edge_type': 'exposes',
                'family': 'Exposure',
                'file_path': file_path,
                'line': p.get('line', 0),
                'confidence': 0.95,  # High confidence for explicit exports
                'metadata': {
                    'export_type': export_type,
                    'exported_name': exported_name,
                }
            })

    return edges


def deduplicate_edges(edges: List[Dict]) -> List[Dict]:
    """Remove duplicate edges based on source, target, and type."""
    seen = set()
    unique = []
    for edge in edges:
        key = (edge.get("source"), edge.get("target"), edge.get("type"))
        if key not in seen:
            seen.add(key)
            unique.append(edge)
    return unique


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
            # Check for ambiguity with stdlib/external
            root_module = _get_module_root(target_module)
            if root_module in STDLIB_MODULES:
                return None, True
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
