#!/usr/bin/env python3
"""
SCOPE ANALYZER - Query-based lexical scope analysis using tree-sitter.

Provides scope-aware analysis for:
- Variable binding resolution (ref → def)
- Unused definition detection (dead code)
- Variable shadowing detection (code smell)

Architecture:
- Uses .scm query files (locals.scm) with @local.scope, @local.definition, @local.reference
- Implements tree-sitter-highlight algorithm for resolution
- Supports Python PEP 227 (class bodies don't propagate scope)
- Supports JavaScript TDZ (Temporal Dead Zone for let/const)

Usage:
    from src.core.scope_analyzer import analyze_scopes, find_unused_definitions

    scope_graph = analyze_scopes(tree, source, 'python')
    unused = find_unused_definitions(scope_graph)
    shadowed = find_shadowed_definitions(scope_graph)
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class Definition:
    """A variable/function definition in a scope."""
    name: str
    node_id: int  # tree-sitter node id
    start_byte: int
    end_byte: int
    start_line: int
    end_line: int
    scope_id: int
    kind: str = 'variable'  # variable, function, parameter, class, import
    available_after_byte: int = 0  # When the definition becomes usable (for TDZ)

    def __hash__(self):
        return hash((self.name, self.node_id, self.scope_id))


@dataclass
class Reference:
    """A reference to a name that needs resolution."""
    name: str
    node_id: int
    start_byte: int
    start_line: int
    scope_id: int
    resolved_def: Optional[Definition] = None

    def __hash__(self):
        return hash((self.name, self.node_id))


@dataclass
class Scope:
    """A lexical scope containing definitions."""
    id: int
    parent_id: Optional[int]
    start_byte: int
    end_byte: int
    start_line: int
    end_line: int
    kind: str  # module, function, class, block, comprehension
    inherits: bool = True  # False for class bodies (PEP 227)
    definitions: List[Definition] = field(default_factory=list)
    children: List[int] = field(default_factory=list)  # child scope ids


@dataclass
class ScopeGraph:
    """Complete scope analysis result for a file."""
    file_path: str
    language: str
    scopes: Dict[int, Scope] = field(default_factory=dict)
    definitions: Dict[int, Definition] = field(default_factory=dict)  # by node_id
    references: List[Reference] = field(default_factory=list)
    root_scope_id: int = 0
    query_based: bool = False  # True if used .scm queries

    def get_scope(self, scope_id: int) -> Optional[Scope]:
        return self.scopes.get(scope_id)

    def get_parent_scope(self, scope_id: int) -> Optional[Scope]:
        scope = self.scopes.get(scope_id)
        if scope and scope.parent_id is not None:
            return self.scopes.get(scope.parent_id)
        return None


# =============================================================================
# QUERY-BASED SCOPE ANALYZER
# =============================================================================

class QueryBasedScopeAnalyzer:
    """
    Scope analyzer using tree-sitter .scm queries.

    Uses locals.scm with:
    - @local.scope: Node that creates a new scope
    - @local.definition: Node that defines a name
    - @local.definition-value: Initializer (for available_after_byte)
    - @local.reference: Node that references a name
    """

    # Scope types that don't inherit (Python PEP 227)
    NON_INHERITING_SCOPES = {
        'python': {'class_definition'},
    }

    # Hoisted definitions (JavaScript var, function declarations)
    HOISTED_PATTERNS = {
        'javascript': {'variable_declaration', 'function_declaration'},
        'typescript': {'variable_declaration', 'function_declaration'},
    }

    def __init__(self):
        self._queries: Dict[str, Any] = {}
        self._parsers: Dict[str, Any] = {}

    def _ensure_query(self, language: str) -> bool:
        """Load the locals.scm query for a language."""
        if language in self._queries:
            return True

        try:
            import tree_sitter

            # Get query loader
            try:
                from src.core.queries import get_query_loader
            except ImportError:
                try:
                    from core.queries import get_query_loader
                except ImportError:
                    from queries import get_query_loader

            loader = get_query_loader()
            query_text = loader.load_query(language, 'locals')

            if not query_text:
                logger.debug(f"No locals.scm for {language}")
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
            logger.warning(f"Failed to load locals query for {language}: {e}")
            return False

    def analyze(self, tree, source: bytes, language: str, file_path: str = '') -> ScopeGraph:
        """
        Analyze scopes using .scm query captures.

        Algorithm:
        1. Run locals.scm query to get all captures
        2. Build scope tree from @local.scope captures
        3. Associate definitions with scopes from @local.definition
        4. Collect references from @local.reference
        5. Resolve references using tree-sitter-highlight algorithm
        """
        import tree_sitter

        graph = ScopeGraph(file_path=file_path, language=language, query_based=True)

        if not self._ensure_query(language):
            logger.debug(f"Falling back to manual analysis for {language}")
            return _analyze_manual(tree, source, language, file_path)

        query = self._queries[language]
        cursor = tree_sitter.QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        # Collect captures by type
        scope_nodes = []
        definition_nodes = []
        definition_value_nodes = {}  # node_id -> value_node
        reference_nodes = []

        for capture_name, nodes in captures.items():
            for node in nodes:
                if capture_name == 'local.scope':
                    scope_nodes.append(node)
                elif capture_name == 'local.definition':
                    definition_nodes.append(node)
                elif capture_name == 'local.definition-value':
                    # Associate with parent definition
                    # Find the sibling definition node
                    definition_value_nodes[node.id] = node
                elif capture_name == 'local.reference':
                    reference_nodes.append(node)

        # Sort scopes by start position (ensures parents processed before children)
        scope_nodes.sort(key=lambda n: (n.start_byte, -n.end_byte))

        # Build scope tree
        scope_stack: List[int] = []
        next_scope_id = 0
        node_to_scope: Dict[int, int] = {}  # node_id -> scope_id

        non_inheriting = self.NON_INHERITING_SCOPES.get(language, set())

        for node in scope_nodes:
            # Pop scopes that have ended
            while scope_stack:
                top_scope = graph.scopes[scope_stack[-1]]
                if node.start_byte >= top_scope.end_byte:
                    scope_stack.pop()
                else:
                    break

            parent_id = scope_stack[-1] if scope_stack else None
            inherits = node.type not in non_inheriting

            scope = Scope(
                id=next_scope_id,
                parent_id=parent_id,
                start_byte=node.start_byte,
                end_byte=node.end_byte,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                kind=node.type,
                inherits=inherits,
            )

            graph.scopes[next_scope_id] = scope
            node_to_scope[node.id] = next_scope_id

            if parent_id is not None:
                graph.scopes[parent_id].children.append(next_scope_id)

            if next_scope_id == 0:
                graph.root_scope_id = 0

            scope_stack.append(next_scope_id)
            next_scope_id += 1

        # Build definitions
        hoisted = self.HOISTED_PATTERNS.get(language, set())

        for node in definition_nodes:
            # Find containing scope
            scope_id = _find_containing_scope(node, graph.scopes)
            if scope_id is None:
                scope_id = graph.root_scope_id

            name = source[node.start_byte:node.end_byte].decode('utf8', errors='replace')

            # Determine available_after_byte
            # Check if this definition has an associated value
            parent = node.parent
            is_hoisted = parent and parent.type in hoisted

            if is_hoisted:
                # Hoisted: available from scope start
                available_after = graph.scopes[scope_id].start_byte
            else:
                # Not hoisted: available after definition ends
                # Look for definition-value sibling
                value_byte = node.end_byte
                if parent:
                    for sibling in parent.children:
                        if sibling.id in definition_value_nodes:
                            value_byte = sibling.end_byte
                            break
                available_after = value_byte

            # Determine kind
            kind = _infer_definition_kind(node, parent)

            definition = Definition(
                name=name,
                node_id=node.id,
                start_byte=node.start_byte,
                end_byte=node.end_byte,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                scope_id=scope_id,
                kind=kind,
                available_after_byte=available_after,
            )

            graph.definitions[node.id] = definition
            if scope_id in graph.scopes:
                graph.scopes[scope_id].definitions.append(definition)

        # Collect references (filter out definitions)
        definition_ids = set(graph.definitions.keys())

        for node in reference_nodes:
            if node.id in definition_ids:
                continue  # Skip - this is a definition, not a reference

            scope_id = _find_containing_scope(node, graph.scopes)
            if scope_id is None:
                scope_id = graph.root_scope_id

            name = source[node.start_byte:node.end_byte].decode('utf8', errors='replace')

            ref = Reference(
                name=name,
                node_id=node.id,
                start_byte=node.start_byte,
                start_line=node.start_point[0] + 1,
                scope_id=scope_id,
            )

            graph.references.append(ref)

        # Resolve references
        _resolve_all_references(graph)

        return graph


def _find_containing_scope(node, scopes: Dict[int, Scope]) -> Optional[int]:
    """Find the innermost scope containing a node."""
    best_scope_id = None
    best_size = float('inf')

    for scope_id, scope in scopes.items():
        if scope.start_byte <= node.start_byte and node.end_byte <= scope.end_byte:
            size = scope.end_byte - scope.start_byte
            if size < best_size:
                best_size = size
                best_scope_id = scope_id

    return best_scope_id


def _infer_definition_kind(node, parent) -> str:
    """Infer the kind of definition from node context."""
    if not parent:
        return 'variable'

    parent_type = parent.type

    # Function-related
    if parent_type in ('function_definition', 'function_declaration'):
        # Check if this is the function name or a parameter
        name_node = parent.child_by_field_name('name')
        if name_node and name_node.id == node.id:
            return 'function'
        return 'parameter'

    if parent_type in ('parameters', 'formal_parameters', 'typed_parameter',
                       'default_parameter', 'list_splat_pattern', 'dictionary_splat_pattern',
                       'rest_pattern', 'object_pattern', 'array_pattern'):
        return 'parameter'

    # Class
    if parent_type in ('class_definition', 'class_declaration'):
        name_node = parent.child_by_field_name('name')
        if name_node and name_node.id == node.id:
            return 'class'

    # Import
    if parent_type in ('import_statement', 'import_from_statement', 'aliased_import',
                       'import_specifier', 'import_clause', 'namespace_import'):
        return 'import'

    # Variable declarator
    if parent_type == 'variable_declarator':
        return 'variable'

    return 'variable'


# =============================================================================
# MANUAL FALLBACK ANALYZER (when queries unavailable)
# =============================================================================

# Scope-defining node types by language (fallback)
SCOPE_NODES = {
    'python': {
        'module': ('module', True),
        'function': ('function_definition', True),
        'class': ('class_definition', False),
        'lambda': ('lambda', True),
        'comprehension': ('list_comprehension', True),
        'dict_comprehension': ('dictionary_comprehension', True),
        'set_comprehension': ('set_comprehension', True),
        'generator': ('generator_expression', True),
    },
    'javascript': {
        'program': ('program', True),
        'function': ('function_declaration', True),
        'function_expr': ('function_expression', True),
        'arrow': ('arrow_function', True),
        'method': ('method_definition', True),
        'class': ('class_declaration', True),
        'block': ('statement_block', True),
        'for': ('for_statement', True),
        'for_in': ('for_in_statement', True),
        'catch': ('catch_clause', True),
    },
    'typescript': {
        'program': ('program', True),
        'function': ('function_declaration', True),
        'function_expr': ('function_expression', True),
        'arrow': ('arrow_function', True),
        'method': ('method_definition', True),
        'class': ('class_declaration', True),
        'block': ('statement_block', True),
        'for': ('for_statement', True),
        'for_in': ('for_in_statement', True),
        'catch': ('catch_clause', True),
    },
}


def _analyze_manual(tree, source: bytes, language: str, file_path: str = '') -> ScopeGraph:
    """Manual AST traversal fallback when queries unavailable."""
    graph = ScopeGraph(file_path=file_path, language=language, query_based=False)

    scope_types = _get_scope_types(language)
    scope_stack: List[int] = []
    next_scope_id = 0

    root = tree.root_node
    root_scope = Scope(
        id=next_scope_id,
        parent_id=None,
        start_byte=root.start_byte,
        end_byte=root.end_byte,
        start_line=root.start_point[0] + 1,
        end_line=root.end_point[0] + 1,
        kind='module' if language == 'python' else 'program',
        inherits=True,
    )
    graph.scopes[next_scope_id] = root_scope
    graph.root_scope_id = next_scope_id
    scope_stack.append(next_scope_id)
    next_scope_id += 1

    def visit_node(node, depth=0):
        nonlocal next_scope_id

        node_type = node.type
        scope_info = scope_types.get(node_type)
        created_scope = False

        if scope_info:
            inherits = scope_info[1]
            parent_id = scope_stack[-1] if scope_stack else None

            new_scope = Scope(
                id=next_scope_id,
                parent_id=parent_id,
                start_byte=node.start_byte,
                end_byte=node.end_byte,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                kind=node_type,
                inherits=inherits,
            )
            graph.scopes[next_scope_id] = new_scope

            if parent_id is not None and parent_id in graph.scopes:
                graph.scopes[parent_id].children.append(next_scope_id)

            scope_stack.append(next_scope_id)
            next_scope_id += 1
            created_scope = True

        _extract_definitions_manual(node, graph, scope_stack, language, source)
        _extract_references_manual(node, graph, scope_stack, language)

        for child in node.children:
            visit_node(child, depth + 1)

        if created_scope and scope_stack:
            scope_stack.pop()

    visit_node(root)
    _resolve_all_references(graph)

    return graph


def _get_scope_types(language: str) -> Dict[str, Tuple[str, bool]]:
    """Get scope-creating node types for a language."""
    lang_scopes = SCOPE_NODES.get(language, SCOPE_NODES.get('python', {}))
    return {v[0]: (k, v[1]) for k, v in lang_scopes.items()}


def _extract_definitions_manual(node, graph: ScopeGraph, scope_stack: List[int],
                                language: str, source: bytes):
    """Extract definitions manually (fallback)."""
    if not scope_stack:
        return

    current_scope_id = scope_stack[-1]
    parent = node.parent
    if not parent:
        return

    if node.type != 'identifier':
        return

    # Check definition contexts
    is_def = False
    kind = 'variable'

    if language == 'python':
        if parent.type == 'function_definition':
            name_node = parent.child_by_field_name('name')
            if name_node and name_node.id == node.id:
                is_def, kind = True, 'function'
        elif parent.type == 'class_definition':
            name_node = parent.child_by_field_name('name')
            if name_node and name_node.id == node.id:
                is_def, kind = True, 'class'
        elif parent.type in ('parameters', 'typed_parameter', 'default_parameter'):
            is_def, kind = True, 'parameter'
        elif parent.type == 'assignment':
            for child in parent.children:
                if child.type == '=':
                    break
                if child.id == node.id:
                    is_def, kind = True, 'variable'
                    break
        elif parent.type == 'for_statement':
            for child in parent.children:
                if child.type == 'in':
                    break
                if child.id == node.id:
                    is_def, kind = True, 'variable'
                    break
        elif parent.type in ('import_statement', 'import_from_statement', 'aliased_import'):
            is_def, kind = True, 'import'

    elif language in ('javascript', 'typescript'):
        if parent.type == 'function_declaration':
            name_node = parent.child_by_field_name('name')
            if name_node and name_node.id == node.id:
                is_def, kind = True, 'function'
        elif parent.type == 'class_declaration':
            name_node = parent.child_by_field_name('name')
            if name_node and name_node.id == node.id:
                is_def, kind = True, 'class'
        elif parent.type == 'variable_declarator':
            name_node = parent.child_by_field_name('name')
            if name_node and name_node.id == node.id:
                is_def, kind = True, 'variable'
        elif parent.type == 'formal_parameters':
            is_def, kind = True, 'parameter'
        elif parent.type in ('import_specifier', 'import_clause', 'namespace_import'):
            is_def, kind = True, 'import'

    if is_def:
        name = source[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        definition = Definition(
            name=name,
            node_id=node.id,
            start_byte=node.start_byte,
            end_byte=node.end_byte,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            scope_id=current_scope_id,
            kind=kind,
            available_after_byte=node.end_byte,
        )
        graph.definitions[node.id] = definition
        if current_scope_id in graph.scopes:
            graph.scopes[current_scope_id].definitions.append(definition)


def _extract_references_manual(node, graph: ScopeGraph, scope_stack: List[int], language: str):
    """Extract references manually (fallback)."""
    if not scope_stack or node.type != 'identifier':
        return

    if node.id in graph.definitions:
        return

    parent = node.parent
    if not parent:
        return

    # Skip definition contexts
    skip_parents = ('function_definition', 'class_definition', 'function_declaration',
                    'class_declaration', 'variable_declarator', 'parameters',
                    'formal_parameters', 'typed_parameter', 'default_parameter',
                    'import_statement', 'import_from_statement', 'import_specifier')

    if parent.type in skip_parents:
        return

    current_scope_id = scope_stack[-1]
    ref = Reference(
        name=node.text.decode('utf8', errors='replace') if node.text else '',
        node_id=node.id,
        start_byte=node.start_byte,
        start_line=node.start_point[0] + 1,
        scope_id=current_scope_id,
    )
    graph.references.append(ref)


# =============================================================================
# RESOLUTION AND DETECTION FUNCTIONS
# =============================================================================

def _resolve_all_references(graph: ScopeGraph):
    """Resolve all references to their definitions."""
    for ref in graph.references:
        ref.resolved_def = resolve_reference(ref, graph)


def resolve_reference(ref: Reference, graph: ScopeGraph) -> Optional[Definition]:
    """
    Resolve a reference to its definition.

    Algorithm (from tree-sitter-highlight):
    1. Start from reference's scope
    2. Walk scopes innermost → outermost
    3. For each scope, check definitions newest → oldest
    4. Match if: name matches AND ref.start_byte >= def.available_after_byte
    5. Stop if scope.inherits == False
    """
    current_scope_id = ref.scope_id

    while current_scope_id is not None:
        scope = graph.get_scope(current_scope_id)
        if not scope:
            break

        # Check definitions in this scope (reverse order = newest first)
        for definition in reversed(scope.definitions):
            if definition.name == ref.name:
                # Check temporal ordering (TDZ compliance)
                if ref.start_byte >= definition.available_after_byte:
                    return definition

        # Stop if scope doesn't inherit (class body in Python)
        if not scope.inherits:
            break

        current_scope_id = scope.parent_id

    return None


def find_unused_definitions(graph: ScopeGraph) -> List[Definition]:
    """Find definitions that are never referenced."""
    referenced_ids: Set[int] = set()
    for ref in graph.references:
        if ref.resolved_def:
            referenced_ids.add(ref.resolved_def.node_id)

    unused = []
    for node_id, definition in graph.definitions.items():
        if node_id not in referenced_ids:
            # Skip kinds that might be used externally
            if definition.kind in ('import', 'class', 'function'):
                continue
            unused.append(definition)

    return unused


def find_shadowed_definitions(graph: ScopeGraph) -> List[Tuple[Definition, Definition]]:
    """Find definitions that shadow outer scope definitions."""
    shadowed_pairs = []

    for scope_id, scope in graph.scopes.items():
        if scope.parent_id is None:
            continue

        for inner_def in scope.definitions:
            outer_def = _find_in_ancestors(inner_def.name, scope.parent_id, graph)
            if outer_def:
                shadowed_pairs.append((inner_def, outer_def))

    return shadowed_pairs


def _find_in_ancestors(name: str, scope_id: Optional[int], graph: ScopeGraph) -> Optional[Definition]:
    """Find a definition with given name in ancestor scopes."""
    while scope_id is not None:
        scope = graph.get_scope(scope_id)
        if not scope:
            break

        for definition in scope.definitions:
            if definition.name == name:
                return definition

        if not scope.inherits:
            break

        scope_id = scope.parent_id

    return None


# =============================================================================
# PUBLIC API
# =============================================================================

# Singleton analyzer
_analyzer: Optional[QueryBasedScopeAnalyzer] = None


def analyze_scopes(tree, source: bytes, language: str, file_path: str = '') -> ScopeGraph:
    """
    Analyze scopes in a parsed tree.

    Args:
        tree: tree-sitter Tree object
        source: Source code as bytes
        language: Language name (python, javascript, typescript)
        file_path: Optional file path for reporting

    Returns:
        ScopeGraph with all scopes, definitions, and references
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = QueryBasedScopeAnalyzer()

    return _analyzer.analyze(tree, source, language, file_path)


def get_scope_summary(graph: ScopeGraph) -> dict:
    """Get summary statistics for a scope graph."""
    return {
        'total_scopes': len(graph.scopes),
        'total_definitions': len(graph.definitions),
        'total_references': len(graph.references),
        'resolved_references': sum(1 for r in graph.references if r.resolved_def),
        'unresolved_references': sum(1 for r in graph.references if not r.resolved_def),
        'unused_definitions': len(find_unused_definitions(graph)),
        'shadowed_pairs': len(find_shadowed_definitions(graph)),
        'query_based': graph.query_based,
    }


if __name__ == '__main__':
    # Test with a simple Python file
    import tree_sitter
    import tree_sitter_python

    code = b'''
def outer():
    x = 1
    def inner():
        x = 2  # shadows outer x
        y = 3  # unused
        print(x)
    inner()

class MyClass:
    value = 10
    def method(self):
        # value not accessible here (PEP 227)
        return self.value
'''

    parser = tree_sitter.Parser()
    parser.language = tree_sitter.Language(tree_sitter_python.language())
    tree = parser.parse(code)

    graph = analyze_scopes(tree, code, 'python', 'test.py')

    print("=" * 60)
    print("SCOPE ANALYSIS TEST (Query-Based)")
    print("=" * 60)
    print(f"Query-based: {graph.query_based}")

    print(f"\nScopes: {len(graph.scopes)}")
    for sid, scope in graph.scopes.items():
        inherit_str = "" if scope.inherits else " [no-inherit]"
        print(f"  [{sid}] {scope.kind} (lines {scope.start_line}-{scope.end_line}){inherit_str}")
        for d in scope.definitions:
            print(f"       def: {d.name} ({d.kind}) available@{d.available_after_byte}")

    print(f"\nReferences: {len(graph.references)}")
    for ref in graph.references[:10]:  # First 10
        resolved = f"-> {ref.resolved_def.name}@L{ref.resolved_def.start_line}" if ref.resolved_def else "UNRESOLVED"
        print(f"  {ref.name}@L{ref.start_line} {resolved}")

    print(f"\nUnused definitions:")
    for d in find_unused_definitions(graph):
        print(f"  {d.name} at line {d.start_line}")

    print(f"\nShadowed definitions:")
    for inner, outer in find_shadowed_definitions(graph):
        print(f"  {inner.name}@L{inner.start_line} shadows {outer.name}@L{outer.start_line}")

    print(f"\nSummary: {get_scope_summary(graph)}")
