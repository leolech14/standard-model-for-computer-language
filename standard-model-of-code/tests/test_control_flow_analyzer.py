"""
Tests for ControlFlowAnalyzer - cyclomatic complexity and nesting depth.
"""
import pytest

try:
    import tree_sitter
    import tree_sitter_python
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False

try:
    from src.core.control_flow_analyzer import (
        analyze_control_flow,
        calculate_cyclomatic_complexity,
        calculate_nesting_depth,
        analyze_function_complexity,
        get_complexity_rating,
        get_nesting_rating,
        ControlFlowMetrics,
    )
except ImportError:
    from core.control_flow_analyzer import (
        analyze_control_flow,
        calculate_cyclomatic_complexity,
        calculate_nesting_depth,
        analyze_function_complexity,
        get_complexity_rating,
        get_nesting_rating,
        ControlFlowMetrics,
    )


def parse_python(code: str):
    """Helper to parse Python code."""
    if not HAS_TREE_SITTER:
        pytest.skip("tree-sitter not available")
    parser = tree_sitter.Parser()
    parser.language = tree_sitter.Language(tree_sitter_python.language())
    return parser.parse(bytes(code, 'utf8'))


class TestCyclomaticComplexity:
    """Tests for cyclomatic complexity calculation."""

    def test_simple_function_cc1(self):
        """Empty function has CC=1."""
        code = "def foo(): pass"
        tree = parse_python(code)
        cc = calculate_cyclomatic_complexity(tree, 'python')
        assert cc == 1

    def test_single_if_cc2(self):
        """Single if adds 1 to CC."""
        code = """
def foo(x):
    if x > 0:
        return x
    return 0
"""
        tree = parse_python(code)
        cc = calculate_cyclomatic_complexity(tree, 'python')
        assert cc == 2  # 1 (base) + 1 (if)

    def test_if_elif_else_cc3(self):
        """if/elif/else: if and elif each add 1."""
        code = """
def foo(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
"""
        tree = parse_python(code)
        cc = calculate_cyclomatic_complexity(tree, 'python')
        assert cc == 3  # 1 + 1 (if) + 1 (elif)

    def test_for_loop_cc2(self):
        """For loop adds 1 to CC."""
        code = """
def foo(items):
    for item in items:
        print(item)
"""
        tree = parse_python(code)
        cc = calculate_cyclomatic_complexity(tree, 'python')
        assert cc == 2  # 1 + 1 (for)

    def test_while_loop_cc2(self):
        """While loop adds 1 to CC."""
        code = """
def foo(x):
    while x > 0:
        x -= 1
"""
        tree = parse_python(code)
        cc = calculate_cyclomatic_complexity(tree, 'python')
        assert cc == 2  # 1 + 1 (while)

    def test_try_except_cc2(self):
        """Except clause adds 1 to CC."""
        code = """
def foo():
    try:
        risky()
    except Exception:
        handle()
"""
        tree = parse_python(code)
        cc = calculate_cyclomatic_complexity(tree, 'python')
        assert cc == 2  # 1 + 1 (except)

    def test_boolean_and_adds_cc(self):
        """Boolean 'and' adds 1 to CC."""
        code = """
def foo(a, b):
    if a and b:
        return True
"""
        tree = parse_python(code)
        cc = calculate_cyclomatic_complexity(tree, 'python')
        assert cc >= 3  # 1 + 1 (if) + 1 (and)

    def test_boolean_or_adds_cc(self):
        """Boolean 'or' adds 1 to CC."""
        code = """
def foo(a, b):
    if a or b:
        return True
"""
        tree = parse_python(code)
        cc = calculate_cyclomatic_complexity(tree, 'python')
        assert cc >= 3  # 1 + 1 (if) + 1 (or)

    def test_complex_function(self):
        """Complex function with multiple decision points."""
        code = """
def complex(x, y):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                return i
    elif x < 0:
        while y > 0:
            y -= 1
    return y
"""
        tree = parse_python(code)
        cc = calculate_cyclomatic_complexity(tree, 'python')
        # 1 + if + for + inner_if + elif + while = 6
        assert cc >= 5


class TestNestingDepth:
    """Tests for nesting depth calculation."""

    def test_flat_code_depth0(self):
        """Code with no nesting has depth 0."""
        code = "x = 1"
        tree = parse_python(code)
        depth = calculate_nesting_depth(tree, 'python')
        assert depth == 0

    def test_single_if_depth1(self):
        """Single if has depth 1."""
        code = """
if True:
    x = 1
"""
        tree = parse_python(code)
        depth = calculate_nesting_depth(tree, 'python')
        assert depth == 1

    def test_nested_if_depth2(self):
        """Nested if has depth 2."""
        code = """
if True:
    if True:
        x = 1
"""
        tree = parse_python(code)
        depth = calculate_nesting_depth(tree, 'python')
        assert depth == 2

    def test_function_with_if_depth2(self):
        """Function containing if has depth 2."""
        code = """
def foo():
    if True:
        x = 1
"""
        tree = parse_python(code)
        depth = calculate_nesting_depth(tree, 'python')
        assert depth == 2  # function + if

    def test_deep_nesting(self):
        """Deeply nested code."""
        code = """
def foo():
    if True:
        for x in []:
            while True:
                try:
                    pass
                except:
                    pass
"""
        tree = parse_python(code)
        depth = calculate_nesting_depth(tree, 'python')
        assert depth >= 5


class TestAnalyzeControlFlow:
    """Tests for full control flow analysis."""

    def test_returns_all_metrics(self):
        """analyze_control_flow returns all expected fields."""
        code = "def foo(): pass"
        tree = parse_python(code)
        metrics = analyze_control_flow(tree, bytes(code, 'utf8'), 'python')

        assert 'cyclomatic_complexity' in metrics
        assert 'max_nesting_depth' in metrics
        assert 'decision_points' in metrics
        assert 'branches' in metrics
        assert 'early_returns' in metrics
        assert 'loops' in metrics
        assert 'exception_handlers' in metrics

    def test_counts_loops(self):
        """Correctly counts loops."""
        code = """
def foo():
    for x in []: pass
    while True: pass
"""
        tree = parse_python(code)
        metrics = analyze_control_flow(tree, bytes(code, 'utf8'), 'python')
        assert metrics['loops'] == 2

    def test_counts_exception_handlers(self):
        """Correctly counts exception handlers."""
        code = """
def foo():
    try:
        pass
    except TypeError:
        pass
    except ValueError:
        pass
"""
        tree = parse_python(code)
        metrics = analyze_control_flow(tree, bytes(code, 'utf8'), 'python')
        assert metrics['exception_handlers'] == 2


class TestComplexityRating:
    """Tests for complexity rating functions."""

    def test_simple_rating(self):
        assert get_complexity_rating(1) == 'simple'
        assert get_complexity_rating(10) == 'simple'

    def test_moderate_rating(self):
        assert get_complexity_rating(11) == 'moderate'
        assert get_complexity_rating(20) == 'moderate'

    def test_complex_rating(self):
        assert get_complexity_rating(21) == 'complex'
        assert get_complexity_rating(50) == 'complex'

    def test_very_complex_rating(self):
        assert get_complexity_rating(51) == 'very_complex'
        assert get_complexity_rating(100) == 'very_complex'


class TestNestingRating:
    """Tests for nesting rating functions."""

    def test_shallow_rating(self):
        assert get_nesting_rating(0) == 'shallow'
        assert get_nesting_rating(2) == 'shallow'

    def test_moderate_rating(self):
        assert get_nesting_rating(3) == 'moderate'
        assert get_nesting_rating(4) == 'moderate'

    def test_deep_rating(self):
        assert get_nesting_rating(5) == 'deep'
        assert get_nesting_rating(6) == 'deep'

    def test_very_deep_rating(self):
        assert get_nesting_rating(7) == 'very_deep'
        assert get_nesting_rating(10) == 'very_deep'


class TestFunctionLevelAnalysis:
    """Tests for function-level complexity analysis."""

    def test_analyze_function_returns_metrics(self):
        """analyze_function_complexity returns ControlFlowMetrics."""
        code = """
def foo(x):
    if x > 0:
        return x
    return 0
"""
        tree = parse_python(code)
        # Find the function node
        func_node = None
        for child in tree.root_node.children:
            if child.type == 'function_definition':
                func_node = child
                break

        if func_node:
            metrics = analyze_function_complexity(func_node, 'python')
            assert isinstance(metrics, ControlFlowMetrics)
            assert metrics.cyclomatic_complexity >= 1
