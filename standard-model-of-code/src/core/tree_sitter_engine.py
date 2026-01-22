#!/usr/bin/env python3
"""
🚀 SPECTROMETER V12 - Tree-sitter Universal Engine
Minimal, maximum output, works across 160+ languages
============================================
"""

import os
import ast
import fnmatch
import json
import logging
import re
import subprocess
import sys
import threading
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set

try:
    from type_registry import normalize_type
except ImportError:
    try:
        from core.type_registry import normalize_type
    except ImportError:
        def normalize_type(t): return t

# NEW: Import Delegated Components
try:
    from core.classification.universal_classifier import UniversalClassifier
    from core.parser.python_extractor import PythonASTExtractor
except ImportError:
    # Try local import (if running from core)
    try:
        from classification.universal_classifier import UniversalClassifier
        from parser.python_extractor import PythonASTExtractor
    except ImportError:
        # Fallback for direct script execution without package structure
        sys.path.append(str(Path(__file__).parent))
        from classification.universal_classifier import UniversalClassifier
        from parser.python_extractor import PythonASTExtractor

# NEW: Import QueryLoader for external .scm queries
try:
    from src.core.queries import get_query_loader
except ImportError:
    try:
        from core.queries import get_query_loader
    except ImportError:
        # Fallback: QueryLoader not available (backward compatibility)
        def get_query_loader():
            return None


def get_query_for_language(language: str, query_type: str = 'symbols') -> Optional[str]:
    """
    Get tree-sitter query for a language, with fallback to inline queries.

    P1-08: Integration wrapper for external .scm queries with inline fallback.
    Attempts to load from QueryLoader first, returns None if not found.
    Caller responsible for implementing inline query fallback.

    Args:
        language: Language name (python, javascript, typescript, go, rust, etc.)
        query_type: Query type (symbols, locals, highlights, injections, patterns)

    Returns:
        Query string if found, None if not found (caller uses inline fallback)
    """
    loader = get_query_loader()
    if loader is None:
        return None

    try:
        query = loader.load_query(language, query_type)
        if query:
            return query
    except Exception:
        # Fall through to inline queries if loading fails
        pass

    return None


class ParseTimeout(Exception):
    """Raised when parsing exceeds time limit."""
    pass


def count_parse_errors(tree) -> dict:
    """
    Count ERROR and MISSING nodes in a parsed tree.

    Tree-sitter inserts ERROR nodes when it encounters syntax errors,
    and MISSING nodes for expected tokens that weren't found.

    Args:
        tree: tree-sitter Tree object

    Returns:
        Dict with 'error_count', 'missing_count', 'error_locations', 'missing_locations'
    """
    errors = []
    missing = []

    cursor = tree.walk()

    while True:
        node = cursor.node

        if node.type == 'ERROR':
            errors.append({
                'start_line': node.start_point[0] + 1,
                'end_line': node.end_point[0] + 1,
                'start_col': node.start_point[1],
                'end_col': node.end_point[1],
            })

        if node.is_missing:
            missing.append({
                'expected': node.type,
                'line': node.start_point[0] + 1,
                'col': node.start_point[1],
            })

        # Tree traversal: depth-first
        if cursor.goto_first_child():
            continue
        if cursor.goto_next_sibling():
            continue

        while cursor.goto_parent():
            if cursor.goto_next_sibling():
                break
        else:
            break

    return {
        'error_count': len(errors),
        'missing_count': len(missing),
        'error_locations': errors,
        'missing_locations': missing,
    }


def _find_containing_class(node) -> Optional[str]:
    """
    Walk up the AST to find the containing class for a node.
    Returns the class name if found, None otherwise.

    This enables structural 'contains' edges (class contains method).
    """
    # Node types that represent class containers
    CLASS_TYPES = {
        'class_declaration',      # JS/TS
        'class_definition',       # Python
        'class_specifier',        # C++
        'struct_item',            # Rust
        'impl_item',              # Rust impl block
        'interface_declaration',  # TS
        'type_declaration',       # Go (for struct/interface)
    }

    current = node.parent
    while current:
        if current.type in CLASS_TYPES:
            # Extract the class name
            name_node = current.child_by_field_name('name')
            if name_node:
                return name_node.text.decode('utf8')
            # Go type_declaration wraps type_spec
            if current.type == 'type_declaration':
                for child in current.children:
                    if child.type == 'type_spec':
                        name_node = child.child_by_field_name('name')
                        if name_node:
                            return name_node.text.decode('utf8')
        current = current.parent
    return None


def parse_with_timeout(parser, source_bytes: bytes, timeout_seconds: int = 30):
    """Parse source with timeout protection.

    Uses threading for cross-platform compatibility (no signal.SIGALRM).
    """
    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = parser.parse(source_bytes)
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=timeout_seconds)

    if thread.is_alive():
        # Thread still running - timeout occurred
        # Note: Cannot forcefully kill thread in Python
        raise ParseTimeout(f"Parse timed out after {timeout_seconds}s")

    if exception[0]:
        raise exception[0]

    return result[0]


def load_colliderignore(base_path: Path) -> Set[str]:
    """Load .colliderignore patterns from a directory.

    Returns a set of patterns to ignore (similar to .gitignore format).
    """
    ignore_file = base_path / '.colliderignore'
    patterns = set()

    # Default patterns always ignored
    default_patterns = {
        '.git', '__pycache__', 'node_modules', 'venv', '.venv',
        '.archive', 'archive', '.collider', 'blender', 'experiments'
    }
    patterns.update(default_patterns)

    if ignore_file.exists():
        try:
            with open(ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    # Remove trailing slash for directory patterns
                    pattern = line.rstrip('/')
                    patterns.add(pattern)
        except Exception as e:
            logging.warning(f"Failed to read .colliderignore: {e}")

    return patterns


def should_ignore_path(path: Path, patterns: Set[str], base_path: Path) -> bool:
    """Check if a path should be ignored based on patterns.

    Supports:
    - Exact directory names: '.archive', 'node_modules'
    - Glob patterns: '*.min.js', '*/vendor/*'
    - Path prefixes: '.collider_*'
    """
    # Get relative path from base
    try:
        rel_path = path.relative_to(base_path)
    except ValueError:
        rel_path = path

    path_str = str(rel_path)
    path_parts = rel_path.parts

    for pattern in patterns:
        # Check if any path component matches pattern directly
        for part in path_parts:
            if part == pattern:
                return True
            # Check glob patterns (e.g., .collider_*)
            if fnmatch.fnmatch(part, pattern):
                return True

        # Check if full path matches glob pattern
        if fnmatch.fnmatch(path_str, pattern):
            return True

        # Check if path contains the pattern as a component
        if f'/{pattern}/' in f'/{path_str}/':
            return True

    return False


class TreeSitterUniversalEngine:
    """
    Universal Tree-sitter engine for cross-language pattern detection.
    
    REFACTORED (2025-12-24): Now acts as a Facade to:
    - UniversalClassifier (classification logic)
    - PythonASTExtractor (parsing logic)
    """

    def __init__(self):
        self.supported_languages = {
            '.py': 'python',
            '.java': 'java',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.mjs': 'javascript',
            '.cjs': 'javascript',
            '.go': 'go',
            '.rs': 'rust',
            '.kt': 'kotlin',
            '.cs': 'c_sharp',
            '.rb': 'ruby',
            '.php': 'php',
            '.yaml': 'yaml',
            '.yml': 'yaml',
        }

        # Load universal patterns
        patterns_file = Path(__file__).parent.parent / 'patterns' / 'universal_patterns.json'
        try:
            with open(patterns_file) as f:
                self.patterns = json.load(f)
        except Exception:
            self.patterns = {}

        # INITIALIZE DELEGATES
        self.classifier = UniversalClassifier()
        self.python_extractor = PythonASTExtractor(self.classifier)

        self._ts_symbol_extractor = (Path(__file__).parent.parent / "tools" / "ts_symbol_extractor.cjs").resolve()
        self.python_depth_margin = int(os.environ.get("COLLIDER_DEPTH_MARGIN", "50"))
        self.python_recursion_hard_cap = int(os.environ.get("COLLIDER_RECURSION_LIMIT", "10000"))
        self.depth_summary: Dict[str, Any] = {}

    def _tokenize_identifier(self, name: str) -> List[str]:
        """Tokenize identifier into lowercase tokens (snake_case + CamelCase)."""
        if not name:
            return []

        parts = re.split(r'[_\-\s]+', name)
        tokens: List[str] = []
        for part in parts:
            if not part:
                continue
            tokens.extend(
                t.lower()
                for t in re.findall(
                    r'[A-Z]+(?=[A-Z][a-z]|[0-9]|$)|[A-Z]?[a-z]+|[0-9]+',
                    part,
                )
                if t
            )
        return tokens

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for universal patterns"""

        # Determine language
        ext = Path(file_path).suffix
        language = self.supported_languages.get(ext)

        if not language:
            return self._fallback_analysis(file_path)

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return {'particles': [], 'touchpoints': [], 'language': 'unknown'}

        # Parse (simplified for minimal version)
        depth_metrics: Dict[str, Any] = {}
        if language in {'javascript', 'javascript_react', 'typescript', 'rust', 'go'}:  # JS/TS/JSX/TSX/Rust/Go
             try:
                 # print(f"DEBUG: Attempting tree-sitter for {file_path}")
                 particles = self._extract_particles_tree_sitter(content, language, file_path)
                 # print(f"DEBUG: Tree-sitter success. {len(particles)} particles.")
             except Exception as e:
                 print(f"DEBUG: Tree-sitter failed: {e}")
                 # Fallback to regex
                 particles = self._extract_particles(content, language, file_path)
        elif language == 'python':
            # DELEGATE to PythonASTExtractor
            particles, depth_metrics = self.python_extractor.extract_particles_ast(
                content, file_path, include_depth_metrics=True
            )
        elif language == 'yaml':
            # Use specialized K8s manifest extraction
            try:
                particles = self._extract_particles_yaml(content, file_path)
            except Exception as e:
                print(f"DEBUG: YAML extraction failed: {e}")
                particles = []
        else:
            particles = self._extract_particles(content, language, file_path)
            
        touchpoints = self._extract_touchpoints(content, particles)
        raw_imports = self._extract_raw_imports(content, language, file_path)

        result = {
            'file_path': file_path,
            'language': language,
            'particles': particles,
            'touchpoints': touchpoints,
            'raw_imports': raw_imports,
            'lines_analyzed': len(content.split('\n')),
            'chars_analyzed': len(content),
            'raw_content': content,  # For JS module resolution
        }
        if depth_metrics:
            result['depth_metrics'] = depth_metrics
        return result

    def _extract_particles_yaml(self, content: str, file_path: str) -> List[Dict]:
        """Extract particles from YAML files, specialized for Kubernetes manifests.
        
        Parses YAML to find Kubernetes resource definitions (Deployment, Service, Pod, etc.)
        and creates particles for each resource.
        """
        import re
        particles = []
        
        # Split multi-document YAML (separated by ---)
        documents = re.split(r'^---\s*$', content, flags=re.MULTILINE)
        
        for doc_idx, doc in enumerate(documents):
            if not doc.strip():
                continue
            
            # Extract kind
            kind_match = re.search(r'^kind:\s*(\w+)', doc, re.MULTILINE)
            if not kind_match:
                continue
            kind = kind_match.group(1)
            
            # Extract metadata.name
            name_match = re.search(r'^\s+name:\s*([^\s\n]+)', doc, re.MULTILINE)
            name = name_match.group(1) if name_match else f"{kind}_{doc_idx}"
            
            # Extract apiVersion
            api_match = re.search(r'^apiVersion:\s*([^\s\n]+)', doc, re.MULTILINE)
            api_version = api_match.group(1) if api_match else "v1"
            
            # Find line number of this document
            doc_start = content.find(doc)
            line_num = content[:doc_start].count('\n') + 1 if doc_start > 0 else 1
            
            # Create particle for this K8s resource
            particle = self.classifier.classify_extracted_symbol(
                name=name,
                symbol_kind='k8s_resource',
                file_path=file_path,
                line_num=line_num,
                end_line=line_num + doc.count('\n'),
                evidence=f"kind: {kind}",
                body_source=doc[:500],  # Truncate for large manifests
            )
            
            # Add K8s-specific metadata
            particle.setdefault('metadata', {})['k8s_kind'] = kind
            particle['metadata']['api_version'] = api_version
            particle['tags'] = ['yaml', 'kubernetes', kind.lower()]
            
            particles.append(particle)
        
        return particles

    def _extract_particles_tree_sitter(self, content: str, language: str, file_path: str) -> List[Dict]:
        """Extract particles using Tree-sitter for JS/TS/JSX/TSX."""
        import tree_sitter
        import tree_sitter_python
        import tree_sitter_go

        # Optional imports - may not be installed
        try:
            import tree_sitter_javascript
            import tree_sitter_typescript
            import tree_sitter_rust
            has_js_ts_rust = True
        except ImportError:
            has_js_ts_rust = False

        # Map extensions to (language_object, parser_name)
        ts_supported_languages = {
            ".py": (tree_sitter_python.language(), "python"),
            ".go": (tree_sitter_go.language(), "go"),
        }

        # Add JS/TS/Rust if available
        if has_js_ts_rust:
            ts_supported_languages.update({
                ".js": (tree_sitter_javascript.language(), "javascript"),
                ".jsx": (tree_sitter_javascript.language(), "javascript"),
                ".ts": (tree_sitter_typescript.language_typescript(), "typescript"),
                ".tsx": (tree_sitter_typescript.language_tsx(), "tsx"),
                ".rs": (tree_sitter_rust.language(), "rust"),
            })

        ext = Path(file_path).suffix
        lang_obj, parser_name = ts_supported_languages.get(ext, (None, None))

        if not lang_obj:
            raise ValueError(f"Tree-sitter parsing not supported for extension: {ext}")

        parser = tree_sitter.Parser()
        ts_lang = tree_sitter.Language(lang_obj)
        parser.language = ts_lang

        try:
            tree = parse_with_timeout(parser, bytes(content, "utf8"), timeout_seconds=30)
        except ParseTimeout as e:
            logging.warning(f"Parse timeout for {file_path}: {e}")
            return []  # Return empty particles for this file

        root_node = tree.root_node

        particles = []

        # Language-specific queries
        if parser_name == "rust":
            # Rust-specific query for structs, traits, impls, functions
            query_scm = """
            (function_item name: (identifier) @func.name) @func
            (struct_item name: (type_identifier) @struct.name) @struct
            (trait_item name: (type_identifier) @trait.name) @trait
            (impl_item) @impl
            (enum_item name: (type_identifier) @enum.name) @enum
            """
        elif parser_name == "go":
            # Go-specific query for functions, methods, structs, interfaces
            query_scm = """
            (function_declaration name: (identifier) @func.name) @func
            (method_declaration name: (field_identifier) @method.name) @method
            (type_declaration (type_spec name: (type_identifier) @struct.name type: (struct_type))) @struct
            (type_declaration (type_spec name: (type_identifier) @interface.name type: (interface_type))) @interface
            (func_literal) @func
            """
        else:
            # JS/TS/JSX/TSX query for ALL functions, classes, and methods
            query_scm = """
            ; All function declarations (not filtered by case)
            (function_declaration name: (identifier) @func.name) @func

            ; Arrow functions assigned to variables
            (variable_declarator
              name: (identifier) @func.name
              value: (arrow_function) @func
            )

            ; Function expressions assigned to variables
            (variable_declarator
              name: (identifier) @func.name
              value: (function_expression) @func
            )

            ; Class declarations
            (class_declaration name: (identifier) @class.name) @class

            ; Class methods (method_definition inside class_body)
            (method_definition name: (property_identifier) @method.name) @method

            ; Hook calls (for React analysis)
            (call_expression
              function: (identifier) @hook.name
              (#match? @hook.name "^use[A-Z]")
            ) @hook_call
            """
        
        try:
            query = tree_sitter.Query(ts_lang, query_scm)
        except Exception as e:
            # Fallback for languages that might error on the complex query
            logging.debug(f"Complex query failed ({e}), using simple query")
            if parser_name == "rust":
                query_scm = """
                (function_item) @func
                (struct_item) @struct
                """
            else:
                query_scm = """
                (function_declaration) @func
                (class_declaration) @class
                """
            query = tree_sitter.Query(ts_lang, query_scm)

        cursor = tree_sitter.QueryCursor(query)
        captures = cursor.captures(root_node)

        particles = []
        seen_nodes = set()  # Avoid duplicates

        # Capture outputs a dict: { capture_name: [nodes] }
        for tag, nodes in captures.items():
            for node in nodes:
                # Skip already processed nodes
                if id(node) in seen_nodes:
                    continue

                p_type = 'Function'
                p_name = 'Unknown'
                symbol_kind = 'function'

                # Handle Rust/Go-specific node types
                if tag == 'struct':
                    p_type = 'Struct'
                    symbol_kind = 'struct'
                    # Go structs: type_declaration wraps type_spec with name
                    if node.type == 'type_declaration':
                        # Find the type_spec child which has the name
                        for child in node.children:
                            if child.type == 'type_spec':
                                name_node = child.child_by_field_name('name')
                                if name_node:
                                    p_name = name_node.text.decode('utf8')
                                break
                    else:
                        # Rust struct_item
                        name_node = node.child_by_field_name('name')
                        if name_node:
                            p_name = name_node.text.decode('utf8')
                elif tag == 'interface':
                    # Go interface
                    p_type = 'Interface'
                    symbol_kind = 'interface'
                    if node.type == 'type_declaration':
                        for child in node.children:
                            if child.type == 'type_spec':
                                name_node = child.child_by_field_name('name')
                                if name_node:
                                    p_name = name_node.text.decode('utf8')
                                break
                elif tag == 'method':
                    # Method (Go or JS/TS)
                    p_type = 'Method'
                    symbol_kind = 'method'
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        p_name = name_node.text.decode('utf8')

                    # Go method (has receiver)
                    receiver_node = node.child_by_field_name('receiver')
                    if receiver_node:
                        # Extract receiver type (e.g., (s *Server) -> Server)
                        for child in receiver_node.children:
                            if child.type == 'parameter_declaration':
                                type_child = child.child_by_field_name('type')
                                if type_child:
                                    receiver_type = type_child.text.decode('utf8').lstrip('*')
                                    p_name = f"{receiver_type}.{p_name}"
                                break

                    # JS/TS method_definition: parent chain to class_declaration
                    if node.type == 'method_definition':
                        class_name = _find_containing_class(node)
                        if class_name:
                            p_name = f"{class_name}.{p_name}"
                elif tag == 'trait':
                    p_type = 'Trait'
                    symbol_kind = 'trait'
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        p_name = name_node.text.decode('utf8')
                elif tag == 'impl':
                    p_type = 'Impl'
                    symbol_kind = 'impl'
                    # Impl blocks: extract type name from type field
                    type_node = node.child_by_field_name('type')
                    if type_node:
                        p_name = type_node.text.decode('utf8')
                    else:
                        # Try to extract from first type identifier child
                        for child in node.children:
                            if child.type == 'type_identifier':
                                p_name = child.text.decode('utf8')
                                break
                elif tag == 'enum':
                    p_type = 'Enum'
                    symbol_kind = 'enum'
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        p_name = name_node.text.decode('utf8')
                # Handle JS/TS node types
                elif tag == 'class':
                    p_type = 'Class'
                    symbol_kind = 'class'
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        p_name = name_node.text.decode('utf8')
                elif tag == 'func':
                    # Rust function_item or JS function_declaration
                    if node.type in ('function_item', 'function_declaration'):
                        name_node = node.child_by_field_name('name')
                        if name_node:
                            p_name = name_node.text.decode('utf8')
                    elif node.type in ('arrow_function', 'function_expression', 'function', 'func_literal'):
                        # For arrow/function expressions inside variable_declarator
                        if node.parent and node.parent.type == 'variable_declarator':
                            name_node = node.parent.child_by_field_name('name')
                            if name_node:
                                p_name = name_node.text.decode('utf8')
                        elif node.type == 'func_literal':
                             # Go anonymous function (e.g. go func() {})
                             p_name = 'Anonymous'
                else:
                    continue

                # Skip if no valid name
                if p_name == 'Unknown':
                    continue

                seen_nodes.add(id(node))
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                node_source = node.text.decode('utf8')
                first_line = node_source.split('\n')[0] if node_source else ""

                # Use classifier for dimension derivation (including T2 detection)
                particle = self.classifier.classify_extracted_symbol(
                    name=p_name,
                    symbol_kind=symbol_kind,
                    file_path=file_path,
                    line_num=start_line,
                    end_line=end_line,
                    evidence=first_line,
                    body_source=node_source,
                )
                particle['tags'] = ['tree-sitter', parser_name]

                # Find containing class for structural 'contains' edges
                containing_class = _find_containing_class(node)
                if containing_class:
                    particle['parent'] = containing_class
                    # Update kind to 'method' if it's a function inside a class
                    if symbol_kind == 'function':
                        particle['kind'] = 'method'

                # Store byte ranges for hook enrichment
                particle['_node_start_byte'] = node.start_byte
                particle['_node_end_byte'] = node.end_byte
                particles.append(particle)

        # === HOOK COUNTING ENRICHMENT ===
        # Run separate query for hook calls (use* pattern)
        hook_calls = self._extract_hook_calls(ts_lang, root_node, content)

        # Enrich React components with hook usage metadata
        for particle in particles:
            dims = particle.get('dimensions', {})
            d1_what = dims.get('D1_WHAT', '')

            # Only enrich React components (EXT.REACT.001-006 are component atoms)
            if not d1_what.startswith('EXT.REACT.'):
                continue

            comp_start = particle.get('_node_start_byte')
            comp_end = particle.get('_node_end_byte')
            if comp_start is None or comp_end is None:
                continue

            # Find hooks used inside this component
            hooks_inside = [
                h for h in hook_calls
                if comp_start <= h['start_byte'] and h['end_byte'] <= comp_end
            ]

            if hooks_inside:
                particle.setdefault('metadata', {})['hooks_used'] = len(hooks_inside)
                particle['metadata']['hooks'] = [h['name'] for h in hooks_inside]

        # Clean up internal byte range fields (not needed in output)
        for particle in particles:
            particle.pop('_node_start_byte', None)
            particle.pop('_node_end_byte', None)

        return particles

    def _extract_hook_calls(self, ts_lang, root_node, content: str) -> List[Dict]:
        """Extract React hook calls (use* pattern) from AST."""
        import tree_sitter

        hook_query_scm = """
        (call_expression
          function: (identifier) @hook_name)
        """

        try:
            hook_query = tree_sitter.Query(ts_lang, hook_query_scm)
            cursor = tree_sitter.QueryCursor(hook_query)
            captures = cursor.captures(root_node)

            hook_calls = []
            for tag, nodes in captures.items():
                if tag != 'hook_name':
                    continue
                for node in nodes:
                    name = node.text.decode('utf8') if node.text else ''
                    # Filter to use* pattern (React hooks)
                    if name.startswith('use') and len(name) > 3 and name[3].isupper():
                        # Get parent call_expression for full byte range
                        call_node = node.parent
                        if call_node and call_node.type == 'call_expression':
                            hook_calls.append({
                                'name': name,
                                'start_byte': call_node.start_byte,
                                'end_byte': call_node.end_byte,
                                'line': call_node.start_point[0] + 1
                            })
            return hook_calls
        except Exception as e:
            # If hook query fails, return empty list (non-blocking)
            return []
        
    def analyze_directory(self, dir_path: str, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """Analyze all supported files in a directory.

        Respects .colliderignore file if present in the directory.
        """
        results = []
        path = Path(dir_path)

        if not path.exists():
            return []

        # Load ignore patterns from .colliderignore
        ignore_patterns = load_colliderignore(path)

        for root, dirs, files in os.walk(path):
            root_path = Path(root)

            # Skip ignored directories (modify dirs in-place to prevent descent)
            if should_ignore_path(root_path, ignore_patterns, path):
                dirs[:] = []  # Don't descend into this directory
                continue

            for file in files:
                file_path = root_path / file

                # Skip ignored files
                if should_ignore_path(file_path, ignore_patterns, path):
                    continue

                ext = Path(file).suffix

                if extensions and ext not in extensions:
                    continue

                if ext in self.supported_languages:
                    results.append(self.analyze_file(str(file_path)))

        return results

    def _extract_particles(self, content: str, language: str, file_path: str) -> List[Dict]:
        """Extract particles using universal pattern matching"""
        particles = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # JS/TS: keep to top-level declarations (no indentation) to avoid nested helpers and class methods.
            if language in {'javascript', 'typescript'}:
                if line != line.lstrip():
                    continue

                if re.match(r'^\s*(export\s+)?(default\s+)?(abstract\s+)?class\s+\w+', line):
                    # DELEGATE to Classifier
                    particle = self.classifier.classify_class_pattern(line, i, file_path)
                    if particle:
                        particles.append(particle)
                    continue

                if re.match(r'^\s*interface\s+\w+', line) or re.match(r'^\s*type\s+\w+\s*=', line):
                    # DELEGATE to Classifier
                    particle = self.classifier.classify_class_pattern(line, i, file_path)
                    if particle:
                        particles.append(particle)
                    continue

                if re.match(r'^\s*(export\s+)?(default\s+)?(async\s+)?function\s+\w+', line) or re.match(
                    r'^\s*(export\s+)?(const|let|var)\s+\w+\s*=\s*(async\s*)?\(?[^=]*=>',
                    line,
                ):
                    # DELEGATE to Classifier
                    particle = self.classifier.classify_function_pattern(line, i, file_path, language)
                    if particle:
                        particles.append(particle)
                    continue

            # Other languages: keep permissive matching (indentation is less meaningful)
            # Classes/Structs: Rust uses 'struct', Go uses 'type X struct'
            if re.match(r'^\s*(class|public class|private class|interface|type|pub\s+struct|struct|impl)\s+\w+', line):
                # DELEGATE to Classifier
                particle = self.classifier.classify_class_pattern(line, i, file_path)
                if particle:
                    particles.append(particle)
                continue

            # Functions: Added 'pub fn', 'pub async fn' for Rust
            if re.match(r'^\s*(async\s+def|def|public|private|protected|static|func|fn|pub\s+fn|pub\s+async\s+fn)\s+\w+', line):
                # DELEGATE to Classifier
                particle = self.classifier.classify_function_pattern(line, i, file_path, language)
                if particle:
                    particles.append(particle)

        return particles

    # === DELEGATED METHODS (Required for compatibility with tests/external code) ===

    def _classify_class_pattern(self, line: str, line_num: int, file_path: str) -> Optional[Dict]:
        """Delegate to classifier (compat wrapper)."""
        return self.classifier.classify_class_pattern(line, line_num, file_path)

    def _classify_function_pattern(self, line: str, line_num: int, file_path: str, language: str) -> Optional[Dict]:
        """Delegate to classifier (compat wrapper)."""
        return self.classifier.classify_function_pattern(line, line_num, file_path, language)

    def _classify_extracted_symbol(self, **kwargs) -> Dict[str, Any]:
        """Delegate to classifier (compat wrapper)."""
        return self.classifier.classify_extracted_symbol(**kwargs)

    # === Original Methods (Kept for now if self-contained) ===

    def _extract_touchpoints(self, content: str, particles: List[Dict]) -> List[Dict[str, str]]:
        """Extract touchpoints (API endpoints, CLI commands, etc)."""
        touchpoints = []
        # Simplified logic
        for p in particles:
            if p.get('type') == 'Controller' or p.get('type') == 'Command':
                touchpoints.append({
                    "type": p['type'],
                    "name": p['name'],
                    "file_path": p.get('file_path', ''),
                    "line": p.get('line', 0)
                })
        return touchpoints

    def _extract_raw_imports(self, content: str, language: str, file_path: str = "") -> List[Any]:
        """Extract raw import statements using multi-language extractor."""
        # Skip import extraction for data files that might contain embedded code strings
        if file_path and Path(file_path).name == 'data.js':
            return []

        # For Python: use AST-based extraction (handles imports inside functions/try-except)
        # AST is more reliable than regex because it understands Python syntax
        if language == 'python':
            imports = []
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            imports.append({'module': n.name, 'alias': n.asname or '', 'items': []})
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        items = [n.name for n in node.names]
                        imports.append({'module': module, 'items': items, 'is_relative': node.level > 0})
            except SyntaxError:
                pass  # Invalid Python, return empty
            return imports

        # For other languages: use regex-based import_extractor
        try:
            from core.parser.import_extractor import extract_imports
            from dataclasses import asdict
        except ImportError:
            try:
                from parser.import_extractor import extract_imports
                from dataclasses import asdict
            except ImportError:
                return []  # No extractor available for this language

        try:
            extracted = extract_imports(content, language)
            return [asdict(imp) for imp in extracted]
        except Exception:
            return []

    def _fallback_analysis(self, file_path: str) -> Dict[str, Any]:
        """Minimal fallback for unsupported files."""
        return {
            'file_path': file_path,
            'language': 'unknown',
            'particles': [],
            'touchpoints': [],
            'raw_imports': [],
            'lines_analyzed': 0,
            'chars_analyzed': 0
        }

    # === DEPRECATED / REMOVED METHODS (Moved to Delegates) ===
    # _get_particle_type_by_name -> classifier
    # _detect_by_keywords -> classifier
    # _calculate_confidence -> classifier
    # _extract_function_name -> classifier
    # _get_base_class_names -> extractor
    # _get_decorators -> extractor
    # _get_function_body -> extractor
    # _get_function_params -> extractor
    # _get_docstring -> extractor
    # _get_return_type -> extractor
    # _measure_python_ast_depth -> extractor
    # _extract_python_particles_ast_recursive -> extractor
    # _extract_python_particles_ast_iterative -> extractor
    
    # Minimal stubs if absolutely needed by obscure tests, otherwise removed.
    def _extract_python_particles_ast(self, content, file_path, include_depth_metrics=False):
        return self.python_extractor.extract_particles_ast(content, file_path, include_depth_metrics)

