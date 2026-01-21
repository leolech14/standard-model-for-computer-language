#!/usr/bin/env python3
"""
CONTROL FLOW ANALYZER - Cyclomatic complexity and nesting depth metrics.

Provides control flow analysis for:
- Cyclomatic complexity (McCabe metric)
- Nesting depth (max indentation level)
- Branch counting (decision points)

Formula: CC = E - N + 2P (simplified: decision_points + 1)

Decision nodes by language:
- Python: if, elif, for, while, try, except, and, or, comprehension if
- JavaScript: if, else if, for, while, switch case, catch, &&, ||, ?:

Usage:
    from src.core.control_flow_analyzer import (
        calculate_cyclomatic_complexity,
        calculate_nesting_depth,
        analyze_control_flow,
    )

    metrics = analyze_control_flow(tree, source, 'python')
    print(f"CC: {metrics['cyclomatic_complexity']}")
    print(f"Max nesting: {metrics['max_nesting_depth']}")
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class ControlFlowMetrics:
    """Control flow metrics for a function/method."""
    cyclomatic_complexity: int
    max_nesting_depth: int
    decision_points: int
    branches: int
    early_returns: int
    loops: int
    exception_handlers: int


# =============================================================================
# DECISION NODE TYPES BY LANGUAGE
# =============================================================================

DECISION_NODES = {
    'python': {
        # Each adds 1 to CC
        'if_statement': 1,
        'elif_clause': 1,
        'for_statement': 1,
        'while_statement': 1,
        'except_clause': 1,
        'with_statement': 0,  # Not a decision point
        # Boolean operators add complexity
        'and_operator': 1,  # 'and' in binary_operator
        'or_operator': 1,   # 'or' in binary_operator
        # Comprehensions with conditions
        'list_comprehension': 0,  # The 'if' inside adds, not the comprehension itself
        'conditional_expression': 1,  # ternary: x if cond else y
    },
    'javascript': {
        'if_statement': 1,
        'else_clause': 0,  # else itself doesn't add (the if already counted)
        'for_statement': 1,
        'for_in_statement': 1,
        'while_statement': 1,
        'do_statement': 1,
        'switch_case': 1,  # each case
        'catch_clause': 1,
        'ternary_expression': 1,
        # Boolean operators
        'binary_expression': 0,  # Check for && and || separately
    },
    'typescript': {
        'if_statement': 1,
        'else_clause': 0,
        'for_statement': 1,
        'for_in_statement': 1,
        'while_statement': 1,
        'do_statement': 1,
        'switch_case': 1,
        'catch_clause': 1,
        'ternary_expression': 1,
    },
}

# Nesting nodes (increase depth)
NESTING_NODES = {
    'python': [
        'if_statement', 'elif_clause', 'else_clause',
        'for_statement', 'while_statement',
        'try_statement', 'except_clause', 'finally_clause',
        'with_statement',
        'function_definition', 'class_definition',
        'list_comprehension', 'dictionary_comprehension',
    ],
    'javascript': [
        'if_statement', 'else_clause',
        'for_statement', 'for_in_statement', 'while_statement', 'do_statement',
        'try_statement', 'catch_clause', 'finally_clause',
        'switch_statement',
        'function_declaration', 'function_expression', 'arrow_function',
        'class_declaration', 'method_definition',
    ],
    'typescript': [
        'if_statement', 'else_clause',
        'for_statement', 'for_in_statement', 'while_statement', 'do_statement',
        'try_statement', 'catch_clause', 'finally_clause',
        'switch_statement',
        'function_declaration', 'function_expression', 'arrow_function',
        'class_declaration', 'method_definition',
    ],
}


# =============================================================================
# CORE ANALYSIS FUNCTIONS
# =============================================================================

def analyze_control_flow(tree, source: bytes, language: str) -> Dict:
    """
    Analyze control flow metrics for a parsed tree.

    Args:
        tree: tree-sitter Tree object
        source: Source code as bytes
        language: Language name (python, javascript, typescript)

    Returns:
        Dict with cyclomatic_complexity, max_nesting_depth, and details
    """
    cc = calculate_cyclomatic_complexity(tree, language)
    depth = calculate_nesting_depth(tree, language)
    details = _get_detailed_metrics(tree, source, language)

    return {
        'cyclomatic_complexity': cc,
        'max_nesting_depth': depth,
        'decision_points': details['decision_points'],
        'branches': details['branches'],
        'early_returns': details['early_returns'],
        'loops': details['loops'],
        'exception_handlers': details['exception_handlers'],
    }


def calculate_cyclomatic_complexity(tree, language: str) -> int:
    """
    Calculate cyclomatic complexity (McCabe metric).

    Formula: CC = decision_points + 1

    Args:
        tree: tree-sitter Tree object
        language: Language name

    Returns:
        Cyclomatic complexity score (minimum 1)
    """
    decision_nodes = DECISION_NODES.get(language, DECISION_NODES['python'])
    decision_count = 0

    def visit(node):
        nonlocal decision_count

        node_type = node.type

        # Check if this is a decision node
        if node_type in decision_nodes:
            decision_count += decision_nodes[node_type]

        # Special handling for Python boolean operators
        if language == 'python' and node_type == 'boolean_operator':
            # 'and' and 'or' each add 1
            op_node = None
            for child in node.children:
                if child.type in ('and', 'or'):
                    decision_count += 1
                    break

        # Special handling for JavaScript && and ||
        if language in ('javascript', 'typescript') and node_type == 'binary_expression':
            for child in node.children:
                if child.type in ('&&', '||'):
                    decision_count += 1
                    break

        # Special handling for Python comprehension conditions
        if language == 'python' and node_type == 'if_clause':
            # This is the 'if' inside a comprehension
            decision_count += 1

        # Visit children
        for child in node.children:
            visit(child)

    visit(tree.root_node)

    # CC is decision_points + 1 (minimum of 1 for any function)
    return decision_count + 1


def calculate_nesting_depth(tree, language: str) -> int:
    """
    Calculate maximum nesting depth.

    Args:
        tree: tree-sitter Tree object
        language: Language name

    Returns:
        Maximum nesting depth (0 for flat code)
    """
    nesting_nodes = set(NESTING_NODES.get(language, NESTING_NODES['python']))
    max_depth = 0

    def visit(node, current_depth):
        nonlocal max_depth

        node_type = node.type

        # Check if this node increases nesting
        new_depth = current_depth
        if node_type in nesting_nodes:
            new_depth = current_depth + 1
            if new_depth > max_depth:
                max_depth = new_depth

        # Visit children
        for child in node.children:
            visit(child, new_depth)

    visit(tree.root_node, 0)

    return max_depth


def _get_detailed_metrics(tree, source: bytes, language: str) -> Dict:
    """Get detailed control flow metrics."""
    metrics = {
        'decision_points': 0,
        'branches': 0,
        'early_returns': 0,
        'loops': 0,
        'exception_handlers': 0,
    }

    loop_types = {'for_statement', 'for_in_statement', 'while_statement', 'do_statement'}
    exception_types = {'except_clause', 'catch_clause'}

    def visit(node, in_function=False):
        node_type = node.type

        # Track if we're in a function
        is_function = node_type in ('function_definition', 'function_declaration',
                                     'arrow_function', 'method_definition')
        new_in_function = in_function or is_function

        # Decision points
        if node_type in ('if_statement', 'elif_clause', 'conditional_expression',
                         'ternary_expression', 'switch_case'):
            metrics['decision_points'] += 1
            metrics['branches'] += 1

        # Loops
        if node_type in loop_types:
            metrics['loops'] += 1
            metrics['decision_points'] += 1

        # Exception handlers
        if node_type in exception_types:
            metrics['exception_handlers'] += 1
            metrics['decision_points'] += 1

        # Early returns (return not at end of function)
        if node_type == 'return_statement' and new_in_function:
            # Check if this is the last statement (simplified: count all returns > 1)
            metrics['early_returns'] += 1

        # Visit children
        for child in node.children:
            visit(child, new_in_function)

    visit(tree.root_node)

    # Adjust early returns (if only 1 return, it's not "early")
    if metrics['early_returns'] > 0:
        metrics['early_returns'] = max(0, metrics['early_returns'] - 1)

    return metrics


# =============================================================================
# FUNCTION-LEVEL ANALYSIS
# =============================================================================

def analyze_function_complexity(node, language: str) -> ControlFlowMetrics:
    """
    Analyze control flow metrics for a single function node.

    Args:
        node: tree-sitter Node representing a function
        language: Language name

    Returns:
        ControlFlowMetrics for the function
    """
    # Create a fake "tree" with this node as root for reuse
    decision_nodes = DECISION_NODES.get(language, DECISION_NODES['python'])
    nesting_nodes = set(NESTING_NODES.get(language, NESTING_NODES['python']))

    decision_count = 0
    max_depth = 0
    loops = 0
    exception_handlers = 0
    early_returns = 0
    branches = 0

    loop_types = {'for_statement', 'for_in_statement', 'while_statement', 'do_statement'}
    exception_types = {'except_clause', 'catch_clause'}

    def visit(n, depth):
        nonlocal decision_count, max_depth, loops, exception_handlers, early_returns, branches

        node_type = n.type

        # Nesting
        new_depth = depth
        if node_type in nesting_nodes:
            new_depth = depth + 1
            if new_depth > max_depth:
                max_depth = new_depth

        # Decision points
        if node_type in decision_nodes:
            decision_count += decision_nodes[node_type]

        # Boolean operators
        if language == 'python' and node_type == 'boolean_operator':
            for child in n.children:
                if child.type in ('and', 'or'):
                    decision_count += 1
                    break

        if language in ('javascript', 'typescript') and node_type == 'binary_expression':
            for child in n.children:
                if child.type in ('&&', '||'):
                    decision_count += 1
                    break

        # Specific counts
        if node_type in loop_types:
            loops += 1

        if node_type in exception_types:
            exception_handlers += 1

        if node_type in ('if_statement', 'elif_clause', 'switch_case'):
            branches += 1

        if node_type == 'return_statement':
            early_returns += 1

        for child in n.children:
            visit(child, new_depth)

    visit(node, 0)

    # Adjust early returns
    if early_returns > 0:
        early_returns = max(0, early_returns - 1)

    return ControlFlowMetrics(
        cyclomatic_complexity=decision_count + 1,
        max_nesting_depth=max_depth,
        decision_points=decision_count,
        branches=branches,
        early_returns=early_returns,
        loops=loops,
        exception_handlers=exception_handlers,
    )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_complexity_rating(cc: int) -> str:
    """
    Get human-readable complexity rating.

    Based on standard thresholds:
    - 1-10: Simple
    - 11-20: Moderate
    - 21-50: Complex
    - >50: Very complex (refactor recommended)
    """
    if cc <= 10:
        return 'simple'
    elif cc <= 20:
        return 'moderate'
    elif cc <= 50:
        return 'complex'
    else:
        return 'very_complex'


def get_nesting_rating(depth: int) -> str:
    """
    Get human-readable nesting rating.

    Based on common thresholds:
    - 0-2: Shallow
    - 3-4: Moderate
    - 5-6: Deep
    - >6: Very deep (refactor recommended)
    """
    if depth <= 2:
        return 'shallow'
    elif depth <= 4:
        return 'moderate'
    elif depth <= 6:
        return 'deep'
    else:
        return 'very_deep'


if __name__ == '__main__':
    # Test with a sample Python file
    import tree_sitter
    import tree_sitter_python

    code = b'''
def complex_function(x, y):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                try:
                    result = y / i
                except ZeroDivisionError:
                    return None
                if result > 10:
                    return result
    elif x < 0:
        while y > 0:
            y -= 1
    else:
        return x and y or 0
    return y
'''

    parser = tree_sitter.Parser()
    parser.language = tree_sitter.Language(tree_sitter_python.language())
    tree = parser.parse(code)

    metrics = analyze_control_flow(tree, code, 'python')

    print("=" * 60)
    print("CONTROL FLOW ANALYSIS TEST")
    print("=" * 60)
    print(f"\nCyclomatic Complexity: {metrics['cyclomatic_complexity']} ({get_complexity_rating(metrics['cyclomatic_complexity'])})")
    print(f"Max Nesting Depth: {metrics['max_nesting_depth']} ({get_nesting_rating(metrics['max_nesting_depth'])})")
    print(f"\nDetails:")
    print(f"  Decision points: {metrics['decision_points']}")
    print(f"  Branches: {metrics['branches']}")
    print(f"  Loops: {metrics['loops']}")
    print(f"  Exception handlers: {metrics['exception_handlers']}")
    print(f"  Early returns: {metrics['early_returns']}")
