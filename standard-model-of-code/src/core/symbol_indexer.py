#!/usr/bin/env python3
"""
SYMBOL INDEXER - Cross-file import/export resolution

Builds a global symbol index for a codebase, enabling:
- Resolution of import statements to actual definitions
- Detection of unused exports (dead code)
- Mapping of import aliases to their sources

Architecture:
- Uses imports.scm queries to extract import/export statements
- Builds bidirectional index: exports → files, imports → exports
- Integrates with edge_extractor for accurate cross-file edges

Usage:
    from src.core.symbol_indexer import SymbolIndexer

    indexer = SymbolIndexer()
    indexer.index_file(file_path, content, 'python')
    resolved = indexer.resolve_import('os', 'path', 'myfile.py')
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class ExportedSymbol:
    """A symbol exported from a module."""
    name: str
    file_path: str
    kind: str  # function, class, variable, default
    start_line: int
    is_default: bool = False
    is_reexport: bool = False
    source_module: Optional[str] = None  # For re-exports

    def __hash__(self):
        return hash((self.name, self.file_path))


@dataclass
class ImportedSymbol:
    """A symbol imported into a module."""
    local_name: str  # Name in the importing file (may be aliased)
    original_name: str  # Original name from source module
    source_module: str  # Module path (e.g., 'os.path' or './utils')
    file_path: str  # File that imports this
    start_line: int
    is_default: bool = False
    is_namespace: bool = False  # import * as X
    is_wildcard: bool = False  # from X import *

    def __hash__(self):
        return hash((self.local_name, self.file_path, self.source_module))


@dataclass
class SymbolIndex:
    """Global symbol index for a codebase."""
    # Exports: module_path -> list of exported symbols
    exports: Dict[str, List[ExportedSymbol]] = field(default_factory=dict)
    # Imports: file_path -> list of imported symbols
    imports: Dict[str, List[ImportedSymbol]] = field(default_factory=dict)
    # Quick lookup: (module, symbol_name) -> ExportedSymbol
    export_lookup: Dict[Tuple[str, str], ExportedSymbol] = field(default_factory=dict)
    # Module aliases: file_path -> {local_name: (source_module, original_name)}
    aliases: Dict[str, Dict[str, Tuple[str, str]]] = field(default_factory=dict)


# =============================================================================
# SYMBOL INDEXER
# =============================================================================

class SymbolIndexer:
    """
    Builds and maintains a cross-file symbol index.

    Supports:
    - Python imports (import X, from X import Y)
    - JavaScript ES6 imports (import X from, import { Y } from)
    - JavaScript CommonJS (require, module.exports)
    - Re-exports and wildcards
    """

    def __init__(self):
        self.index = SymbolIndex()
        self._queries: Dict[str, Any] = {}
        self._parsers: Dict[str, Any] = {}
        self._initialized = False

    def _ensure_initialized(self, language: str) -> bool:
        """Initialize parser and query for a language."""
        if language in self._queries:
            return True

        try:
            import tree_sitter

            # Load query
            try:
                from src.core.queries import get_query_loader
            except ImportError:
                try:
                    from core.queries import get_query_loader
                except ImportError:
                    from queries import get_query_loader

            loader = get_query_loader()
            query_text = loader.load_query(language, 'imports')

            if not query_text:
                logger.debug(f"No imports.scm for {language}")
                return False

            # Get language object
            if language == 'python':
                import tree_sitter_python
                lang_obj = tree_sitter_python.language()
            elif language == 'javascript':
                import tree_sitter_javascript
                lang_obj = tree_sitter_javascript.language()
            elif language == 'typescript':
                import tree_sitter_typescript
                lang_obj = tree_sitter_typescript.language_typescript()
            else:
                return False

            ts_lang = tree_sitter.Language(lang_obj)
            self._queries[language] = tree_sitter.Query(ts_lang, query_text)

            # Create parser
            parser = tree_sitter.Parser()
            parser.language = ts_lang
            self._parsers[language] = parser

            return True

        except Exception as e:
            logger.warning(f"Failed to initialize symbol indexer for {language}: {e}")
            return False

    def index_file(self, file_path: str, content: str, language: str) -> None:
        """
        Index a single file's imports and exports.

        Args:
            file_path: Path to the file
            content: File content
            language: Language name (python, javascript, typescript)
        """
        if not self._ensure_initialized(language):
            # Fallback to regex-based extraction
            self._index_file_regex(file_path, content, language)
            return

        source_bytes = content.encode('utf-8')
        parser = self._parsers[language]
        query = self._queries[language]

        try:
            tree = parser.parse(source_bytes)
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return

        import tree_sitter
        cursor = tree_sitter.QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        # Process captures
        exports: List[ExportedSymbol] = []
        imports: List[ImportedSymbol] = []
        aliases: Dict[str, Tuple[str, str]] = {}

        # Group captures by type
        for capture_name, nodes in captures.items():
            for node in nodes:
                name = content[node.start_byte:node.end_byte]
                line = node.start_point[0] + 1

                # Exports
                if capture_name.startswith('export.'):
                    kind = capture_name.split('.')[1]
                    is_default = 'default' in kind
                    exports.append(ExportedSymbol(
                        name=name,
                        file_path=file_path,
                        kind=kind,
                        start_line=line,
                        is_default=is_default,
                    ))

                # Imports
                elif capture_name.startswith('import.'):
                    import_type = capture_name.split('.')[1]
                    # Handle different import types based on language
                    if language == 'python':
                        self._process_python_import(
                            import_type, name, node, file_path, line,
                            imports, aliases, content, captures
                        )
                    else:
                        self._process_js_import(
                            import_type, name, node, file_path, line,
                            imports, aliases, content, captures
                        )

        # Store results
        self.index.exports[file_path] = exports
        self.index.imports[file_path] = imports
        self.index.aliases[file_path] = aliases

        # Build lookup index
        module_name = self._file_to_module(file_path)
        for exp in exports:
            key = (module_name, exp.name)
            self.index.export_lookup[key] = exp
            # Also index by file path
            self.index.export_lookup[(file_path, exp.name)] = exp

    def _process_python_import(
        self, import_type: str, name: str, node: Any, file_path: str, line: int,
        imports: List[ImportedSymbol], aliases: Dict[str, Tuple[str, str]],
        content: str, captures: Dict
    ):
        """Process Python import captures."""
        if import_type == 'module':
            # import os or import os.path
            imports.append(ImportedSymbol(
                local_name=name.split('.')[-1],
                original_name=name,
                source_module=name,
                file_path=file_path,
                start_line=line,
            ))
        elif import_type == 'symbol':
            # from os import path
            # Need to find the source module from sibling captures
            parent = node.parent
            if parent:
                source = self._find_sibling_capture(parent, 'import.source_module', content)
                if source:
                    imports.append(ImportedSymbol(
                        local_name=name,
                        original_name=name,
                        source_module=source,
                        file_path=file_path,
                        start_line=line,
                    ))
                    aliases[name] = (source, name)
        elif import_type == 'alias':
            # The alias name - need to find the original
            pass  # Handled in conjunction with symbol/module
        elif import_type == 'wildcard':
            # from module import *
            parent = node.parent
            if parent:
                source = self._find_sibling_capture(parent, 'import.source_module', content)
                if source:
                    imports.append(ImportedSymbol(
                        local_name='*',
                        original_name='*',
                        source_module=source,
                        file_path=file_path,
                        start_line=line,
                        is_wildcard=True,
                    ))

    def _process_js_import(
        self, import_type: str, name: str, node: Any, file_path: str, line: int,
        imports: List[ImportedSymbol], aliases: Dict[str, Tuple[str, str]],
        content: str, captures: Dict
    ):
        """Process JavaScript/TypeScript import captures."""
        # Strip quotes from source strings
        if name.startswith('"') or name.startswith("'"):
            name = name[1:-1]

        if import_type == 'default':
            # import X from 'module'
            parent = node.parent
            if parent and parent.parent:
                source = self._get_import_source(parent.parent, content)
                if source:
                    imports.append(ImportedSymbol(
                        local_name=name,
                        original_name='default',
                        source_module=source,
                        file_path=file_path,
                        start_line=line,
                        is_default=True,
                    ))
                    aliases[name] = (source, 'default')
        elif import_type == 'symbol':
            # import { X } from 'module'
            # Walk up to import_statement to get source
            current = node
            while current and current.type != 'import_statement':
                current = current.parent
            if current:
                source = self._get_import_source(current, content)
                if source:
                    imports.append(ImportedSymbol(
                        local_name=name,
                        original_name=name,
                        source_module=source,
                        file_path=file_path,
                        start_line=line,
                    ))
                    aliases[name] = (source, name)
        elif import_type == 'namespace':
            # import * as X from 'module'
            current = node
            while current and current.type != 'import_statement':
                current = current.parent
            if current:
                source = self._get_import_source(current, content)
                if source:
                    imports.append(ImportedSymbol(
                        local_name=name,
                        original_name='*',
                        source_module=source,
                        file_path=file_path,
                        start_line=line,
                        is_namespace=True,
                    ))
                    aliases[name] = (source, '*')
        elif import_type in ('cjs_default', 'cjs_symbol'):
            # CommonJS require
            pass  # Handle in separate capture processing
        elif import_type == 'source':
            # This is the source module string, handled by other captures
            pass

    def _find_sibling_capture(self, parent: Any, capture_name: str, content: str) -> Optional[str]:
        """Find a sibling node's captured value."""
        for child in parent.children:
            if child.type == 'dotted_name':
                return content[child.start_byte:child.end_byte]
        return None

    def _get_import_source(self, import_node: Any, content: str) -> Optional[str]:
        """Get the source module string from an import statement."""
        source_node = import_node.child_by_field_name('source')
        if source_node:
            text = content[source_node.start_byte:source_node.end_byte]
            # Strip quotes
            if text.startswith('"') or text.startswith("'"):
                text = text[1:-1]
            return text
        return None

    def _file_to_module(self, file_path: str) -> str:
        """Convert file path to module name."""
        # Remove extension and convert path separators
        path = Path(file_path)
        module = path.stem
        if path.parent.name and path.parent.name != '.':
            module = f"{path.parent.name}.{module}"
        return module

    def _index_file_regex(self, file_path: str, content: str, language: str):
        """Fallback regex-based extraction when queries unavailable."""
        import re

        exports: List[ExportedSymbol] = []
        imports: List[ImportedSymbol] = []

        if language == 'python':
            # Match: def func_name( or class ClassName
            for match in re.finditer(r'^(?:def|class)\s+(\w+)', content, re.MULTILINE):
                kind = 'function' if content[match.start():].startswith('def') else 'class'
                exports.append(ExportedSymbol(
                    name=match.group(1),
                    file_path=file_path,
                    kind=kind,
                    start_line=content[:match.start()].count('\n') + 1,
                ))

            # Match: from X import Y or import X
            for match in re.finditer(r'^(?:from\s+([\w.]+)\s+import\s+(\w+)|import\s+([\w.]+))', content, re.MULTILINE):
                if match.group(3):  # import X
                    imports.append(ImportedSymbol(
                        local_name=match.group(3).split('.')[-1],
                        original_name=match.group(3),
                        source_module=match.group(3),
                        file_path=file_path,
                        start_line=content[:match.start()].count('\n') + 1,
                    ))
                else:  # from X import Y
                    imports.append(ImportedSymbol(
                        local_name=match.group(2),
                        original_name=match.group(2),
                        source_module=match.group(1),
                        file_path=file_path,
                        start_line=content[:match.start()].count('\n') + 1,
                    ))

        self.index.exports[file_path] = exports
        self.index.imports[file_path] = imports

    def resolve_import(
        self, local_name: str, file_path: str
    ) -> Optional[ExportedSymbol]:
        """
        Resolve an imported name to its exported symbol.

        Args:
            local_name: The name as used in the importing file
            file_path: The file that imports this symbol

        Returns:
            The ExportedSymbol if found, None otherwise
        """
        aliases = self.index.aliases.get(file_path, {})
        if local_name in aliases:
            source_module, original_name = aliases[local_name]
            # Look up in export index
            key = (source_module, original_name)
            if key in self.index.export_lookup:
                return self.index.export_lookup[key]

            # Try resolving relative imports
            resolved_path = self._resolve_module_path(source_module, file_path)
            if resolved_path:
                key = (resolved_path, original_name)
                if key in self.index.export_lookup:
                    return self.index.export_lookup[key]

        return None

    def _resolve_module_path(self, module: str, importing_file: str) -> Optional[str]:
        """Resolve a module specifier to a file path."""
        if module.startswith('.'):
            # Relative import
            base_dir = Path(importing_file).parent
            if module.startswith('..'):
                base_dir = base_dir.parent
                module = module[2:]
            else:
                module = module[1:]

            if module.startswith('/'):
                module = module[1:]

            # Try common extensions
            for ext in ['.py', '.js', '.ts', '.tsx', '.jsx', '/index.js', '/index.ts']:
                candidate = base_dir / (module + ext)
                candidate_str = str(candidate)
                if candidate_str in self.index.exports:
                    return candidate_str

        return None

    def get_unused_exports(self) -> List[ExportedSymbol]:
        """Find exports that are never imported."""
        all_imports: Set[Tuple[str, str]] = set()

        for file_path, imports in self.index.imports.items():
            for imp in imports:
                all_imports.add((imp.source_module, imp.original_name))

        unused = []
        for file_path, exports in self.index.exports.items():
            module_name = self._file_to_module(file_path)
            for exp in exports:
                if (module_name, exp.name) not in all_imports:
                    if (file_path, exp.name) not in all_imports:
                        unused.append(exp)

        return unused

    def get_import_graph(self) -> Dict[str, Set[str]]:
        """
        Build a file-level import graph.

        Returns:
            Dict mapping file_path -> set of imported file paths
        """
        graph: Dict[str, Set[str]] = {}

        for file_path, imports in self.index.imports.items():
            if file_path not in graph:
                graph[file_path] = set()

            for imp in imports:
                resolved = self._resolve_module_path(imp.source_module, file_path)
                if resolved:
                    graph[file_path].add(resolved)

        return graph

    def clear(self):
        """Clear the symbol index."""
        self.index = SymbolIndex()


# =============================================================================
# MODULE-LEVEL FUNCTIONS
# =============================================================================

_indexer: Optional[SymbolIndexer] = None


def get_symbol_indexer() -> SymbolIndexer:
    """Get the singleton SymbolIndexer instance."""
    global _indexer
    if _indexer is None:
        _indexer = SymbolIndexer()
    return _indexer


def index_codebase(files: List[Tuple[str, str, str]]) -> SymbolIndex:
    """
    Index an entire codebase.

    Args:
        files: List of (file_path, content, language) tuples

    Returns:
        The complete SymbolIndex
    """
    indexer = get_symbol_indexer()
    indexer.clear()

    for file_path, content, language in files:
        indexer.index_file(file_path, content, language)

    return indexer.index


if __name__ == '__main__':
    # Test the indexer
    print("=" * 60)
    print("SYMBOL INDEXER TEST")
    print("=" * 60)

    test_python = '''
import os
from pathlib import Path
from typing import Dict, List

def helper_func():
    pass

class MyClass:
    def method(self):
        pass

CONSTANT = 42
'''

    test_js = '''
import React from 'react';
import { useState, useEffect } from 'react';
import * as utils from './utils';

export function MyComponent() {
    return null;
}

export class MyClass {}

export default function App() {}
'''

    indexer = SymbolIndexer()

    print("\nIndexing Python file...")
    indexer.index_file('test.py', test_python, 'python')

    print("\nIndexing JavaScript file...")
    indexer.index_file('test.js', test_js, 'javascript')

    print("\n--- Exports ---")
    for file_path, exports in indexer.index.exports.items():
        print(f"\n{file_path}:")
        for exp in exports:
            print(f"  {exp.kind}: {exp.name}")

    print("\n--- Imports ---")
    for file_path, imports in indexer.index.imports.items():
        print(f"\n{file_path}:")
        for imp in imports:
            print(f"  {imp.local_name} from {imp.source_module}")

    print("\n--- Aliases ---")
    for file_path, aliases in indexer.index.aliases.items():
        if aliases:
            print(f"\n{file_path}:")
            for local, (source, original) in aliases.items():
                print(f"  {local} -> {source}.{original}")
