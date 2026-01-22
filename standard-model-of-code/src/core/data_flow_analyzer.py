#!/usr/bin/env python3
"""
DATA FLOW ANALYZER - Assignment and mutation tracking for D6:EFFECT (purity).

Extends scope_analyzer with data flow tracking:
- Assignment detection (value flows)
- Mutation detection (state changes)
- Purity scoring (0.0 = impure, 1.0 = pure)

Architecture:
- Builds on ScopeGraph from scope_analyzer
- Uses tree-sitter queries for assignment detection
- Tracks value flow: which values feed into which variables

Usage:
    from src.core.data_flow_analyzer import analyze_data_flow, calculate_purity

    flow_graph = analyze_data_flow(tree, source, 'python')
    purity = calculate_purity(flow_graph)

Theory Link:
    D6:EFFECT - Distinguishes pure functions (no side effects) from impure ones.
    Purity is measured by: 1.0 - (mutations / total_assignments)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

# Lazy imports
_tree_sitter = None
_languages = {}


def _get_tree_sitter():
    """Lazy load tree-sitter module."""
    global _tree_sitter
    if _tree_sitter is None:
        import tree_sitter
        _tree_sitter = tree_sitter
    return _tree_sitter


def _get_language(lang: str):
    """Lazy load language module."""
    global _languages
    if lang not in _languages:
        if lang == 'python':
            import tree_sitter_python
            _languages[lang] = tree_sitter_python.language()
        elif lang in ('javascript', 'typescript'):
            import tree_sitter_javascript
            _languages[lang] = tree_sitter_javascript.language()
        else:
            return None
    return _languages[lang]


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class Assignment:
    """
    A write to a variable (assignment or mutation).

    Attributes:
        target_name: Variable being written to
        target_node_id: tree-sitter node id of target
        source_names: List of variable names that flow into this assignment
        start_line: Line number of assignment
        start_byte: Byte offset of assignment
        end_byte: End byte offset
        is_mutation: True if modifying existing variable (augmented assignment, attribute)
        is_global_write: True if writing to global/nonlocal
        is_attribute_write: True if writing to object attribute
    """
    target_name: str
    target_node_id: int
    source_names: List[str]
    start_line: int
    start_byte: int
    end_byte: int
    is_mutation: bool = False
    is_global_write: bool = False
    is_attribute_write: bool = False

    def __hash__(self):
        return hash((self.target_name, self.target_node_id))


@dataclass
class SideEffect:
    """
    A detected side effect (function call, I/O, etc.).

    Attributes:
        kind: Type of side effect (io, call, global, external)
        name: Name of function/operation causing side effect
        line: Line number
        evidence: Code snippet or pattern that revealed the side effect
    """
    kind: str  # 'io', 'call', 'global', 'external', 'attribute_mutation'
    name: str
    line: int
    evidence: str


@dataclass
class DataFlowGraph:
    """
    Complete data flow analysis for a file or function.

    Attributes:
        file_path: Source file path
        language: Programming language
        assignments: All assignments in the scope
        mutations: Assignments that modify existing state
        side_effects: Detected side effects (I/O, external calls)
        pure_score: 0.0 (all mutations) to 1.0 (no mutations)
    """
    file_path: str
    language: str
    assignments: List[Assignment] = field(default_factory=list)
    mutations: List[Assignment] = field(default_factory=list)
    side_effects: List[SideEffect] = field(default_factory=list)
    pure_score: float = 1.0

    @property
    def is_pure(self) -> bool:
        """True if no mutations or side effects detected."""
        return len(self.mutations) == 0 and len(self.side_effects) == 0

    @property
    def purity_rating(self) -> str:
        """Human-readable purity rating."""
        if self.pure_score >= 0.95:
            return 'pure'
        elif self.pure_score >= 0.75:
            return 'mostly_pure'
        elif self.pure_score >= 0.50:
            return 'mixed'
        elif self.pure_score >= 0.25:
            return 'mostly_impure'
        else:
            return 'impure'


# =============================================================================
# SIDE EFFECT INDICATORS
# =============================================================================

# Functions that typically indicate side effects
SIDE_EFFECT_FUNCTIONS = {
    'python': {
        'io': ['print', 'input', 'open', 'read', 'write', 'close', 'flush'],
        'external': ['requests', 'urllib', 'socket', 'subprocess', 'os.system'],
        'global': ['globals', 'setattr', 'delattr', 'exec', 'eval'],
    },
    'javascript': {
        'io': ['console.log', 'console.error', 'alert', 'prompt', 'fetch'],
        'external': ['XMLHttpRequest', 'WebSocket', 'localStorage', 'sessionStorage'],
        'global': ['eval', 'document.write'],
    },
}

# Methods that mutate their receiver object
MUTATING_METHODS = {
    'python': {
        # List mutations
        'append', 'extend', 'insert', 'pop', 'remove', 'clear', 'reverse', 'sort',
        # Dict mutations
        'update', 'pop', 'popitem', 'clear', 'setdefault',
        # Set mutations
        'add', 'discard', 'remove', 'pop', 'clear',
        'update', 'intersection_update', 'difference_update', 'symmetric_difference_update',
    },
    'javascript': {
        # Array mutations
        'push', 'pop', 'shift', 'unshift', 'splice', 'reverse', 'sort', 'fill', 'copyWithin',
        # Map/Set mutations
        'set', 'delete', 'clear',
    },
}


# =============================================================================
# CORE ANALYSIS
# =============================================================================

def analyze_data_flow(tree, source: bytes, language: str,
                      file_path: str = '') -> DataFlowGraph:
    """
    Analyze data flow in a parsed tree.

    Args:
        tree: tree-sitter Tree object
        source: Source code as bytes
        language: Language name (python, javascript, typescript)
        file_path: Optional file path for reporting

    Returns:
        DataFlowGraph with assignments, mutations, and purity score
    """
    graph = DataFlowGraph(file_path=file_path, language=language)

    # Extract assignments and mutations
    if language == 'python':
        _analyze_python_data_flow(tree, source, graph)
    elif language in ('javascript', 'typescript'):
        _analyze_js_data_flow(tree, source, graph)

    # Calculate purity score
    graph.pure_score = calculate_purity(graph)

    return graph


def _analyze_python_data_flow(tree, source: bytes, graph: DataFlowGraph):
    """Analyze Python data flow using AST traversal."""
    # Track variables declared global/nonlocal for is_global_write detection
    global_vars: set = set()

    def visit_node(node):
        node_type = node.type

        # Regular assignment: x = value
        if node_type == 'assignment':
            _process_python_assignment(node, source, graph, global_vars)

        # Augmented assignment: x += value (mutation)
        elif node_type == 'augmented_assignment':
            _process_python_augmented_assignment(node, source, graph, global_vars)

        # Attribute assignment: obj.attr = value (mutation)
        elif node_type == 'assignment' and _is_attribute_target(node):
            # Already handled in _process_python_assignment
            pass

        # Global/nonlocal declarations
        elif node_type in ('global_statement', 'nonlocal_statement'):
            _process_global_statement(node, source, graph, global_vars)

        # Function calls that may have side effects or mutate objects
        elif node_type == 'call':
            _check_side_effect_call(node, source, graph, 'python')
            _check_mutating_method_call(node, source, graph, 'python')

        # Delete statement (mutation)
        elif node_type == 'delete_statement':
            _process_delete_statement(node, source, graph)

        # Recurse
        for child in node.children:
            visit_node(child)

    visit_node(tree.root_node)


def _analyze_js_data_flow(tree, source: bytes, graph: DataFlowGraph):
    """Analyze JavaScript/TypeScript data flow."""

    def visit_node(node):
        node_type = node.type

        # Variable declaration with initializer
        if node_type == 'variable_declarator':
            _process_js_declarator(node, source, graph)

        # Assignment expression
        elif node_type == 'assignment_expression':
            _process_js_assignment(node, source, graph)

        # Augmented assignment
        elif node_type == 'augmented_assignment_expression':
            _process_js_augmented_assignment(node, source, graph)

        # Update expression (++, --)
        elif node_type == 'update_expression':
            _process_js_update(node, source, graph)

        # Function calls
        elif node_type == 'call_expression':
            _check_side_effect_call(node, source, graph, 'javascript')
            _check_mutating_method_call(node, source, graph, 'javascript')

        # Recurse
        for child in node.children:
            visit_node(child)

    visit_node(tree.root_node)


# =============================================================================
# PYTHON-SPECIFIC EXTRACTORS
# =============================================================================

def _process_python_assignment(node, source: bytes, graph: DataFlowGraph,
                                global_vars: set = None):
    """Process Python assignment: target = value."""
    if global_vars is None:
        global_vars = set()

    # Get left (target) and right (value) sides
    left = node.child_by_field_name('left')
    right = node.child_by_field_name('right')

    if not left:
        # Fallback: first child is target
        for child in node.children:
            if child.type != '=':
                if left is None:
                    left = child
                else:
                    right = child
                    break

    if not left:
        return

    target_name, is_attribute = _get_python_target_name(left, source)
    source_names = _extract_referenced_names(right, source) if right else []

    # Check if this is a write to a global/nonlocal variable
    is_global = target_name in global_vars

    assignment = Assignment(
        target_name=target_name,
        target_node_id=left.id,
        source_names=source_names,
        start_line=node.start_point[0] + 1,
        start_byte=node.start_byte,
        end_byte=node.end_byte,
        is_mutation=is_attribute or is_global,  # Global writes are mutations
        is_attribute_write=is_attribute,
        is_global_write=is_global,
    )

    graph.assignments.append(assignment)

    if is_attribute or is_global:
        graph.mutations.append(assignment)


def _process_python_augmented_assignment(node, source: bytes, graph: DataFlowGraph,
                                          global_vars: set = None):
    """Process Python augmented assignment: target += value (always a mutation)."""
    if global_vars is None:
        global_vars = set()

    left = node.child_by_field_name('left')
    right = node.child_by_field_name('right')

    if not left:
        for child in node.children:
            if child.type == 'identifier' or child.type == 'attribute':
                left = child
                break

    if not left:
        return

    target_name, is_attribute = _get_python_target_name(left, source)
    source_names = _extract_referenced_names(right, source) if right else []
    # Include the target itself since it's read and written
    source_names.insert(0, target_name)

    # Check if this is a write to a global/nonlocal variable
    is_global = target_name in global_vars

    assignment = Assignment(
        target_name=target_name,
        target_node_id=left.id,
        source_names=source_names,
        start_line=node.start_point[0] + 1,
        start_byte=node.start_byte,
        end_byte=node.end_byte,
        is_mutation=True,  # Augmented assignment is always a mutation
        is_attribute_write=is_attribute,
        is_global_write=is_global,
    )

    graph.assignments.append(assignment)
    graph.mutations.append(assignment)


def _process_global_statement(node, source: bytes, graph: DataFlowGraph,
                               global_vars: set = None):
    """Process global/nonlocal statement and track declared globals."""
    if global_vars is None:
        global_vars = set()

    for child in node.children:
        if child.type == 'identifier':
            name = source[child.start_byte:child.end_byte].decode('utf8', errors='replace')
            # Track this variable as global for subsequent assignment detection
            global_vars.add(name)
            effect = SideEffect(
                kind='global',
                name=name,
                line=node.start_point[0] + 1,
                evidence=f"global {name}" if node.type == 'global_statement' else f"nonlocal {name}",
            )
            graph.side_effects.append(effect)


def _process_delete_statement(node, source: bytes, graph: DataFlowGraph):
    """Process delete statement as mutation."""
    for child in node.children:
        if child.type == 'identifier':
            name = source[child.start_byte:child.end_byte].decode('utf8', errors='replace')
            assignment = Assignment(
                target_name=name,
                target_node_id=child.id,
                source_names=[],
                start_line=node.start_point[0] + 1,
                start_byte=node.start_byte,
                end_byte=node.end_byte,
                is_mutation=True,
            )
            graph.assignments.append(assignment)
            graph.mutations.append(assignment)


def _get_python_target_name(node, source: bytes) -> Tuple[str, bool]:
    """Get target name and whether it's an attribute write."""
    if node.type == 'identifier':
        name = source[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        return name, False
    elif node.type == 'attribute':
        # Get full attribute path: obj.attr
        text = source[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        return text, True
    elif node.type == 'subscript':
        # Array/dict indexing: arr[i]
        text = source[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        return text, True
    elif node.type == 'tuple_pattern' or node.type == 'list_pattern':
        # Destructuring: a, b = ...
        return '<destructured>', False
    else:
        text = source[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        return text, False


# =============================================================================
# JAVASCRIPT-SPECIFIC EXTRACTORS
# =============================================================================

def _process_js_declarator(node, source: bytes, graph: DataFlowGraph):
    """Process JS variable declarator: const x = value."""
    name_node = node.child_by_field_name('name')
    value_node = node.child_by_field_name('value')

    if not name_node:
        return

    target_name = source[name_node.start_byte:name_node.end_byte].decode('utf8', errors='replace')
    source_names = _extract_referenced_names(value_node, source) if value_node else []

    assignment = Assignment(
        target_name=target_name,
        target_node_id=name_node.id,
        source_names=source_names,
        start_line=node.start_point[0] + 1,
        start_byte=node.start_byte,
        end_byte=node.end_byte,
        is_mutation=False,
    )

    graph.assignments.append(assignment)


def _process_js_assignment(node, source: bytes, graph: DataFlowGraph):
    """Process JS assignment expression: target = value."""
    left = node.child_by_field_name('left')
    right = node.child_by_field_name('right')

    if not left:
        return

    is_attribute = left.type in ('member_expression', 'subscript_expression')
    target_name = source[left.start_byte:left.end_byte].decode('utf8', errors='replace')
    source_names = _extract_referenced_names(right, source) if right else []

    assignment = Assignment(
        target_name=target_name,
        target_node_id=left.id,
        source_names=source_names,
        start_line=node.start_point[0] + 1,
        start_byte=node.start_byte,
        end_byte=node.end_byte,
        is_mutation=is_attribute,
        is_attribute_write=is_attribute,
    )

    graph.assignments.append(assignment)

    if is_attribute:
        graph.mutations.append(assignment)


def _process_js_augmented_assignment(node, source: bytes, graph: DataFlowGraph):
    """Process JS augmented assignment: target += value."""
    left = node.child_by_field_name('left')
    right = node.child_by_field_name('right')

    if not left:
        return

    target_name = source[left.start_byte:left.end_byte].decode('utf8', errors='replace')
    source_names = _extract_referenced_names(right, source) if right else []
    source_names.insert(0, target_name)

    assignment = Assignment(
        target_name=target_name,
        target_node_id=left.id,
        source_names=source_names,
        start_line=node.start_point[0] + 1,
        start_byte=node.start_byte,
        end_byte=node.end_byte,
        is_mutation=True,
    )

    graph.assignments.append(assignment)
    graph.mutations.append(assignment)


def _process_js_update(node, source: bytes, graph: DataFlowGraph):
    """Process JS update expression: i++ or ++i (mutation)."""
    # Find the identifier being updated
    for child in node.children:
        if child.type == 'identifier':
            target_name = source[child.start_byte:child.end_byte].decode('utf8', errors='replace')

            assignment = Assignment(
                target_name=target_name,
                target_node_id=child.id,
                source_names=[target_name],
                start_line=node.start_point[0] + 1,
                start_byte=node.start_byte,
                end_byte=node.end_byte,
                is_mutation=True,
            )

            graph.assignments.append(assignment)
            graph.mutations.append(assignment)
            break


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _is_attribute_target(node) -> bool:
    """Check if assignment target is an attribute access."""
    left = node.child_by_field_name('left')
    if left and left.type in ('attribute', 'subscript', 'member_expression', 'subscript_expression'):
        return True
    return False


def _extract_referenced_names(node, source: bytes) -> List[str]:
    """Extract all identifier names referenced in a node."""
    if node is None:
        return []

    names = []

    def collect_names(n):
        if n.type == 'identifier':
            name = source[n.start_byte:n.end_byte].decode('utf8', errors='replace')
            names.append(name)
        for child in n.children:
            collect_names(child)

    collect_names(node)
    return names


def _check_side_effect_call(node, source: bytes, graph: DataFlowGraph, language: str):
    """Check if a function call has side effects."""
    indicators = SIDE_EFFECT_FUNCTIONS.get(language, {})

    # Get the function name being called
    func_node = node.child_by_field_name('function')
    if not func_node:
        for child in node.children:
            if child.type in ('identifier', 'attribute', 'member_expression'):
                func_node = child
                break

    if not func_node:
        return

    func_name = source[func_node.start_byte:func_node.end_byte].decode('utf8', errors='replace')

    # Check against known side effect indicators
    for effect_kind, names in indicators.items():
        for indicator in names:
            if indicator in func_name or func_name == indicator:
                effect = SideEffect(
                    kind=effect_kind,
                    name=func_name,
                    line=node.start_point[0] + 1,
                    evidence=f"Call to {func_name}",
                )
                graph.side_effects.append(effect)
                return


def _check_mutating_method_call(node, source: bytes, graph: DataFlowGraph, language: str):
    """
    Check if a method call mutates its receiver object.

    Detects patterns like: list.append(), dict.update(), set.add()
    These are recorded as mutations even though they don't use assignment syntax.
    """
    mutating_methods = MUTATING_METHODS.get(language, set())
    if not mutating_methods:
        return

    # Get the function/method being called
    func_node = node.child_by_field_name('function')
    if not func_node:
        for child in node.children:
            if child.type in ('attribute', 'member_expression'):
                func_node = child
                break

    if not func_node:
        return

    # Check if it's a method call (attribute access)
    if func_node.type not in ('attribute', 'member_expression'):
        return

    # Get the method name (the last part of the attribute chain)
    method_name = None
    if func_node.type == 'attribute':
        # Python: obj.method
        attr_node = func_node.child_by_field_name('attribute')
        if attr_node:
            method_name = source[attr_node.start_byte:attr_node.end_byte].decode('utf8', errors='replace')
    elif func_node.type == 'member_expression':
        # JavaScript: obj.method
        prop_node = func_node.child_by_field_name('property')
        if prop_node:
            method_name = source[prop_node.start_byte:prop_node.end_byte].decode('utf8', errors='replace')

    if not method_name:
        # Fallback: try to extract from children
        for child in func_node.children:
            if child.type == 'identifier' and child != func_node.children[0]:
                method_name = source[child.start_byte:child.end_byte].decode('utf8', errors='replace')
                break

    if method_name and method_name in mutating_methods:
        # Get the receiver object name
        receiver_name = '<object>'
        if func_node.type == 'attribute':
            obj_node = func_node.child_by_field_name('object')
            if obj_node:
                receiver_name = source[obj_node.start_byte:obj_node.end_byte].decode('utf8', errors='replace')
        elif func_node.type == 'member_expression':
            obj_node = func_node.child_by_field_name('object')
            if obj_node:
                receiver_name = source[obj_node.start_byte:obj_node.end_byte].decode('utf8', errors='replace')

        # Record as a mutation
        assignment = Assignment(
            target_name=receiver_name,
            target_node_id=func_node.id,
            source_names=[],
            start_line=node.start_point[0] + 1,
            start_byte=node.start_byte,
            end_byte=node.end_byte,
            is_mutation=True,
            is_attribute_write=True,  # Method mutation is similar to attribute write
        )

        graph.assignments.append(assignment)
        graph.mutations.append(assignment)


# =============================================================================
# PURITY CALCULATION
# =============================================================================

def calculate_purity(graph: DataFlowGraph) -> float:
    """
    Calculate purity score for a data flow graph.

    Formula:
        purity = 1.0 - (mutations + side_effects) / (total_assignments + side_effects + 1)

    Returns:
        Float from 0.0 (completely impure) to 1.0 (completely pure)
    """
    total_assignments = len(graph.assignments)
    mutation_count = len(graph.mutations)
    side_effect_count = len(graph.side_effects)

    # Avoid division by zero
    denominator = total_assignments + side_effect_count + 1

    # Impurity factors
    impurity_factors = mutation_count + side_effect_count

    # Calculate purity (higher is better)
    purity = 1.0 - (impurity_factors / denominator)

    # Clamp to [0, 1]
    return max(0.0, min(1.0, purity))


def get_purity_factors(graph: DataFlowGraph) -> Dict:
    """Get detailed breakdown of purity factors."""
    return {
        'total_assignments': len(graph.assignments),
        'mutations': len(graph.mutations),
        'side_effects': len(graph.side_effects),
        'mutation_types': _count_mutation_types(graph),
        'side_effect_types': _count_side_effect_types(graph),
        'pure_score': graph.pure_score,
        'purity_rating': graph.purity_rating,
        'is_pure': graph.is_pure,
    }


def _count_mutation_types(graph: DataFlowGraph) -> Dict[str, int]:
    """Count mutations by type."""
    counts = {'attribute_write': 0, 'augmented': 0, 'other': 0}
    for m in graph.mutations:
        if m.is_attribute_write:
            counts['attribute_write'] += 1
        elif len(m.source_names) > 0 and m.target_name in m.source_names:
            counts['augmented'] += 1
        else:
            counts['other'] += 1
    return counts


def _count_side_effect_types(graph: DataFlowGraph) -> Dict[str, int]:
    """Count side effects by type."""
    counts = {}
    for effect in graph.side_effects:
        counts[effect.kind] = counts.get(effect.kind, 0) + 1
    return counts


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def analyze_function_purity(func_node, source: bytes, language: str) -> Tuple[float, Dict]:
    """
    Analyze purity of a single function.

    Args:
        func_node: tree-sitter node for the function
        source: Full source code as bytes
        language: Language name

    Returns:
        Tuple of (purity_score, factors_dict)
    """
    # Create a mini data flow graph for just this function
    graph = DataFlowGraph(file_path='', language=language)

    if language == 'python':
        def visit(node):
            if node.type == 'assignment':
                _process_python_assignment(node, source, graph)
            elif node.type == 'augmented_assignment':
                _process_python_augmented_assignment(node, source, graph)
            elif node.type == 'call':
                _check_side_effect_call(node, source, graph, 'python')
            for child in node.children:
                visit(child)
        visit(func_node)

    elif language in ('javascript', 'typescript'):
        def visit(node):
            if node.type == 'assignment_expression':
                _process_js_assignment(node, source, graph)
            elif node.type == 'augmented_assignment_expression':
                _process_js_augmented_assignment(node, source, graph)
            elif node.type == 'update_expression':
                _process_js_update(node, source, graph)
            elif node.type == 'call_expression':
                _check_side_effect_call(node, source, graph, 'javascript')
            for child in node.children:
                visit(child)
        visit(func_node)

    graph.pure_score = calculate_purity(graph)
    return graph.pure_score, get_purity_factors(graph)


def get_data_flow_summary(graph: DataFlowGraph) -> Dict:
    """Get summary statistics for a data flow graph."""
    return {
        'total_assignments': len(graph.assignments),
        'mutations': len(graph.mutations),
        'mutation_ratio': len(graph.mutations) / max(len(graph.assignments), 1),
        'side_effects': len(graph.side_effects),
        'pure_score': graph.pure_score,
        'purity_rating': graph.purity_rating,
        'is_pure': graph.is_pure,
    }


# =============================================================================
# MAIN TEST
# =============================================================================

if __name__ == '__main__':
    import tree_sitter
    import tree_sitter_python

    code = b'''
def pure_function(x, y):
    """This function is pure - no mutations."""
    z = x + y
    result = z * 2
    return result

def impure_function(data):
    """This function has mutations and side effects."""
    data['count'] += 1      # mutation (attribute write)
    total = 0
    total += data['count']  # mutation (augmented assignment)
    print(f"Total: {total}")  # side effect (I/O)
    return total

class Counter:
    def increment(self):
        self.count += 1     # mutation (attribute write)
'''

    parser = tree_sitter.Parser()
    parser.language = tree_sitter.Language(tree_sitter_python.language())
    tree = parser.parse(code)

    print("=" * 60)
    print("DATA FLOW ANALYZER TEST")
    print("=" * 60)

    graph = analyze_data_flow(tree, code, 'python', 'test.py')

    print(f"\n📊 Summary:")
    print(f"   Assignments: {len(graph.assignments)}")
    print(f"   Mutations: {len(graph.mutations)}")
    print(f"   Side Effects: {len(graph.side_effects)}")
    print(f"   Purity Score: {graph.pure_score:.2f}")
    print(f"   Purity Rating: {graph.purity_rating}")

    print(f"\n📝 Assignments:")
    for a in graph.assignments:
        mut = "🔴 MUTATION" if a.is_mutation else "🟢 clean"
        print(f"   L{a.start_line}: {a.target_name} <- {a.source_names} {mut}")

    print(f"\n⚠️  Side Effects:")
    for e in graph.side_effects:
        print(f"   L{e.line}: [{e.kind}] {e.name} - {e.evidence}")

    print(f"\n📈 Purity Factors:")
    factors = get_purity_factors(graph)
    for k, v in factors.items():
        print(f"   {k}: {v}")
