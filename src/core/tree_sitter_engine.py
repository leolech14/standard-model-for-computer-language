#!/usr/bin/env python3
"""
🚀 SPECTROMETER V12 - Tree-sitter Universal Engine
Minimal, maximum output, works across 160+ languages
============================================
"""

import os
import ast
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

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
            '.php': 'php'
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
        self.python_depth_margin = 50
        self.python_recursion_hard_cap = 10000
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
        if language in {'javascript', 'javascript_react', 'typescript', 'rust'}:  # JS/TS/JSX/TSX/Rust
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
            'chars_analyzed': len(content)
        }
        if depth_metrics:
            result['depth_metrics'] = depth_metrics
        return result

    def _extract_particles_tree_sitter(self, content: str, language: str, file_path: str) -> List[Dict]:
        """Extract particles using Tree-sitter for JS/TS/JSX/TSX."""
        import tree_sitter
        import tree_sitter_javascript
        import tree_sitter_typescript
        import tree_sitter_python
        import tree_sitter_rust

        # Map extensions to (language_object, parser_name)
        ts_supported_languages = {
            ".py": (tree_sitter_python.language(), "python"),
            ".js": (tree_sitter_javascript.language(), "javascript"),
            ".jsx": (tree_sitter_javascript.language(), "javascript"),
            ".ts": (tree_sitter_typescript.language_typescript(), "typescript"),
            ".tsx": (tree_sitter_typescript.language_tsx(), "tsx"),
            ".rs": (tree_sitter_rust.language(), "rust"),
        }

        ext = Path(file_path).suffix
        lang_obj, parser_name = ts_supported_languages.get(ext, (None, None))

        if not lang_obj:
            raise ValueError(f"Tree-sitter parsing not supported for extension: {ext}")

        parser = tree_sitter.Parser()
        ts_lang = tree_sitter.Language(lang_obj)
        parser.language = ts_lang

        tree = parser.parse(bytes(content, "utf8"))
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
        else:
            # JS/TS/JSX/TSX query for React components + hooks
            query_scm = """
            (function_declaration name: (identifier) @func.name) @func
            (#match? @func.name "^[A-Z]")
            
            (variable_declarator
              name: (identifier) @func.name
              value: (arrow_function) @func
            )
            (#match? @func.name "^[A-Z]")
            
            (variable_declarator
              name: (identifier) @func.name
              value: (function_expression) @func
            )
            (#match? @func.name "^[A-Z]")
            
            (class_declaration name: (identifier) @class.name) @class
            (#match? @class.name "^[A-Z]")
            
            ; Hook calls
            (call_expression
              function: (identifier) @hook.name
              (#match? @hook.name "^use[A-Z]")
            ) @hook_call
            """
        
        try:
            query = tree_sitter.Query(tree_sitter.Language(lang_obj), query_scm)
        except Exception as e:
            # Fallback for languages that might error on the complex query
            print(f"DEBUG: Complex query failed ({e}), using simple query")
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
            query = tree_sitter.Query(tree_sitter.Language(lang_obj), query_scm)

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

                # Handle Rust-specific node types
                if tag == 'struct':
                    p_type = 'Struct'
                    symbol_kind = 'struct'
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        p_name = name_node.text.decode('utf8')
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
                    elif node.type in ('arrow_function', 'function_expression', 'function'):
                        # For arrow/function expressions inside variable_declarator
                        if node.parent and node.parent.type == 'variable_declarator':
                            name_node = node.parent.child_by_field_name('name')
                            if name_node:
                                p_name = name_node.text.decode('utf8')
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
        """Analyze all supported files in a directory."""
        results = []
        path = Path(dir_path)
        
        if not path.exists():
            return []
            
        for root, _, files in os.walk(path):
            if any(p in str(Path(root)) for p in ['.git', '__pycache__', 'node_modules', 'venv']):
                continue
                
            for file in files:
                file_path = str(Path(root) / file)
                ext = Path(file).suffix
                
                if extensions and ext not in extensions:
                    continue
                    
                if ext in self.supported_languages:
                    results.append(self.analyze_file(file_path))
                    
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

        # Try to import factory (lazy import to avoid circular dep issues)
        try:
            from core.parser.import_extractor import extract_imports
            from dataclasses import asdict
        except ImportError:
            try:
                from parser.import_extractor import extract_imports
                from dataclasses import asdict
            except ImportError:
                # Fallback to python-only manual extraction if module not found
                imports = []
                if language == 'python':
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for n in node.names:
                                    imports.append(n.name)
                            elif isinstance(node, ast.ImportFrom):
                                module = node.module or ''
                                for n in node.names:
                                    imports.append(f"{module}.{n.name}")
                    except:
                        pass
                return imports

        # Use the robust extractor
        try:
            extracted = extract_imports(content, language)
            # Convert dataclasses to dicts for serialization/compatibility
            return [asdict(imp) for imp in extracted]
        except Exception as e:
            # Fallback for errors
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

