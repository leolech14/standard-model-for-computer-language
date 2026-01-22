"""
Tests for DataFlowAnalyzer - assignment/mutation tracking for D6:EFFECT (purity).
"""
import pytest

try:
    import tree_sitter
    import tree_sitter_python
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False

try:
    from src.core.data_flow_analyzer import (
        analyze_data_flow,
        calculate_purity,
        get_purity_factors,
        get_data_flow_summary,
        analyze_function_purity,
        Assignment,
        SideEffect,
        DataFlowGraph,
    )
except ImportError:
    from core.data_flow_analyzer import (
        analyze_data_flow,
        calculate_purity,
        get_purity_factors,
        get_data_flow_summary,
        analyze_function_purity,
        Assignment,
        SideEffect,
        DataFlowGraph,
    )


def parse_python(code: str):
    """Helper to parse Python code."""
    if not HAS_TREE_SITTER:
        pytest.skip("tree-sitter not available")
    parser = tree_sitter.Parser()
    parser.language = tree_sitter.Language(tree_sitter_python.language())
    return parser.parse(bytes(code, 'utf8'))


class TestDataFlowAnalyzer:
    """Tests for DataFlowAnalyzer core functionality."""

    def test_simple_assignment(self):
        """Detects simple variable assignment."""
        code = '''
x = 1
y = 2
z = x + y
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert len(graph.assignments) >= 3
        assert len(graph.mutations) == 0
        assert graph.pure_score > 0.8

    def test_augmented_assignment_is_mutation(self):
        """Augmented assignment (+=, -=) is detected as mutation."""
        code = '''
x = 0
x += 1
x -= 2
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert len(graph.mutations) == 2  # += and -=
        assert graph.pure_score < 0.7

    def test_attribute_write_is_mutation(self):
        """Attribute assignment is detected as mutation."""
        code = '''
obj.attr = 5
obj.nested.value = 10
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert len(graph.mutations) >= 2
        assert any(a.is_attribute_write for a in graph.mutations)

    def test_subscript_write_is_mutation(self):
        """Subscript assignment (arr[i] = x) is detected as mutation."""
        code = '''
arr = [1, 2, 3]
arr[0] = 99
data['key'] = 'value'
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        # arr[0] and data['key'] should be mutations
        attr_mutations = [a for a in graph.mutations if a.is_attribute_write]
        assert len(attr_mutations) >= 2

    def test_print_is_side_effect(self):
        """print() call is detected as I/O side effect."""
        code = '''
def greet():
    print("Hello")
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert len(graph.side_effects) >= 1
        assert any(e.kind == 'io' for e in graph.side_effects)

    def test_pure_function_has_high_score(self):
        """Pure function (no mutations) has high purity score."""
        code = '''
def add(a, b):
    result = a + b
    return result
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert graph.pure_score >= 0.9
        assert graph.purity_rating in ('pure', 'mostly_pure')

    def test_impure_function_has_low_score(self):
        """Function with mutations has low purity score."""
        code = '''
def update_counter(data):
    data['count'] += 1
    print(data['count'])
    return data
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert graph.pure_score < 0.7
        assert graph.purity_rating in ('mixed', 'mostly_impure', 'impure')

    def test_global_statement_is_side_effect(self):
        """global statement is detected as side effect."""
        code = '''
count = 0

def increment():
    global count
    count += 1
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        global_effects = [e for e in graph.side_effects if e.kind == 'global']
        assert len(global_effects) >= 1

    def test_delete_is_mutation(self):
        """del statement is detected as mutation."""
        code = '''
x = 1
del x
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert len(graph.mutations) >= 1

    def test_source_names_tracking(self):
        """Assignment tracks which variables flow into target."""
        code = '''
a = 1
b = 2
c = a + b
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        # Find assignment to 'c'
        c_assignments = [a for a in graph.assignments if a.target_name == 'c']
        assert len(c_assignments) >= 1

        # c should reference a and b
        c_assignment = c_assignments[0]
        assert 'a' in c_assignment.source_names
        assert 'b' in c_assignment.source_names


class TestPurityCalculation:
    """Tests for purity score calculation."""

    def test_empty_graph_is_pure(self):
        """Empty data flow graph has perfect purity."""
        graph = DataFlowGraph(file_path='test.py', language='python')
        assert calculate_purity(graph) == 1.0

    def test_only_clean_assignments_is_pure(self):
        """Graph with only clean assignments is mostly pure."""
        graph = DataFlowGraph(file_path='test.py', language='python')
        graph.assignments = [
            Assignment('x', 1, [], 1, 0, 10),
            Assignment('y', 2, ['x'], 2, 10, 20),
        ]
        score = calculate_purity(graph)
        assert score >= 0.8

    def test_mutations_reduce_purity(self):
        """Mutations reduce purity score."""
        graph = DataFlowGraph(file_path='test.py', language='python')
        mutation = Assignment('x', 1, ['x'], 1, 0, 10, is_mutation=True)
        graph.assignments = [mutation]
        graph.mutations = [mutation]

        score = calculate_purity(graph)
        assert score < 0.7

    def test_side_effects_reduce_purity(self):
        """Side effects reduce purity score."""
        graph = DataFlowGraph(file_path='test.py', language='python')
        graph.side_effects = [
            SideEffect('io', 'print', 1, 'print()'),
            SideEffect('io', 'input', 2, 'input()'),
        ]

        score = calculate_purity(graph)
        assert score < 0.5


class TestPurityRatings:
    """Tests for purity rating labels."""

    def test_pure_rating(self):
        """High purity score gets 'pure' rating."""
        graph = DataFlowGraph(file_path='test.py', language='python')
        graph.pure_score = 0.98
        assert graph.purity_rating == 'pure'

    def test_mostly_pure_rating(self):
        """Moderate-high purity score gets 'mostly_pure' rating."""
        graph = DataFlowGraph(file_path='test.py', language='python')
        graph.pure_score = 0.80
        assert graph.purity_rating == 'mostly_pure'

    def test_mixed_rating(self):
        """Middle purity score gets 'mixed' rating."""
        graph = DataFlowGraph(file_path='test.py', language='python')
        graph.pure_score = 0.55
        assert graph.purity_rating == 'mixed'

    def test_impure_rating(self):
        """Low purity score gets 'impure' rating."""
        graph = DataFlowGraph(file_path='test.py', language='python')
        graph.pure_score = 0.15
        assert graph.purity_rating == 'impure'


class TestDataFlowSummary:
    """Tests for summary statistics."""

    def test_summary_contains_expected_keys(self):
        """Summary dict contains expected keys."""
        code = '''
x = 1
x += 1
print(x)
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')
        summary = get_data_flow_summary(graph)

        assert 'total_assignments' in summary
        assert 'mutations' in summary
        assert 'mutation_ratio' in summary
        assert 'side_effects' in summary
        assert 'pure_score' in summary
        assert 'purity_rating' in summary
        assert 'is_pure' in summary

    def test_purity_factors_breakdown(self):
        """get_purity_factors provides detailed breakdown."""
        code = '''
x = 1
x += 1
y = x * 2
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')
        factors = get_purity_factors(graph)

        assert 'mutation_types' in factors
        assert 'side_effect_types' in factors
        assert isinstance(factors['mutation_types'], dict)


class TestMultipleFunctions:
    """Tests for files with multiple functions."""

    def test_mixed_purity_file(self):
        """File with pure and impure functions."""
        code = '''
def pure_add(a, b):
    return a + b

def impure_log(msg):
    print(msg)
    return msg

def mixed_update(data, key, value):
    data[key] = value
    return data
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        # Should detect mutations and side effects
        assert len(graph.assignments) >= 1
        assert len(graph.mutations) >= 1  # data[key] = value
        assert len(graph.side_effects) >= 1  # print(msg)


class TestEdgeCases:
    """Tests for edge cases and special patterns."""

    def test_method_with_self_mutation(self):
        """Method that mutates self.* is detected."""
        code = '''
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        # self.count assignments should be mutations
        self_mutations = [a for a in graph.mutations if 'self.' in a.target_name]
        assert len(self_mutations) >= 1

    def test_chained_assignment(self):
        """Chained assignment: a = b = 0."""
        code = '''
a = b = c = 0
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        # Should detect at least one assignment
        assert len(graph.assignments) >= 1

    def test_walrus_operator(self):
        """Walrus operator assignment: (x := 1)."""
        code = '''
if (n := len([1, 2, 3])) > 2:
    print(n)
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        # Should be counted as data flow (walrus is assignment)
        # This tests that the analyzer doesn't crash on walrus
        assert isinstance(graph, DataFlowGraph)

    def test_empty_code(self):
        """Empty code produces empty graph."""
        code = ''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert len(graph.assignments) == 0
        assert len(graph.mutations) == 0
        assert graph.pure_score == 1.0


class TestDataFlowIsPure:
    """Tests for is_pure property."""

    def test_no_mutations_is_pure(self):
        """Graph with no mutations is pure."""
        graph = DataFlowGraph(file_path='test.py', language='python')
        graph.assignments = [Assignment('x', 1, [], 1, 0, 10)]
        assert graph.is_pure

    def test_mutations_not_pure(self):
        """Graph with mutations is not pure."""
        graph = DataFlowGraph(file_path='test.py', language='python')
        mutation = Assignment('x', 1, ['x'], 1, 0, 10, is_mutation=True)
        graph.assignments = [mutation]
        graph.mutations = [mutation]
        assert not graph.is_pure

    def test_side_effects_not_pure(self):
        """Graph with side effects is not pure."""
        graph = DataFlowGraph(file_path='test.py', language='python')
        graph.side_effects = [SideEffect('io', 'print', 1, 'print()')]
        assert not graph.is_pure


class TestMethodCallMutations:
    """Tests for method call mutation detection (list.append, dict.update, etc.)."""

    def test_list_append_is_mutation(self):
        """list.append() is detected as mutation."""
        code = '''
items = []
items.append(1)
items.append(2)
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        # Should detect the append calls as mutations
        assert len(graph.mutations) >= 2
        assert any('items' in m.target_name for m in graph.mutations)

    def test_list_extend_is_mutation(self):
        """list.extend() is detected as mutation."""
        code = '''
data = [1, 2]
data.extend([3, 4])
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert len(graph.mutations) >= 1

    def test_dict_update_is_mutation(self):
        """dict.update() is detected as mutation."""
        code = '''
config = {}
config.update({'key': 'value'})
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert len(graph.mutations) >= 1

    def test_set_add_is_mutation(self):
        """set.add() is detected as mutation."""
        code = '''
seen = set()
seen.add('item')
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert len(graph.mutations) >= 1

    def test_list_sort_is_mutation(self):
        """list.sort() is detected as mutation."""
        code = '''
numbers = [3, 1, 2]
numbers.sort()
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert len(graph.mutations) >= 1

    def test_dict_clear_is_mutation(self):
        """dict.clear() is detected as mutation."""
        code = '''
cache = {'a': 1}
cache.clear()
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        assert len(graph.mutations) >= 1

    def test_method_mutations_reduce_purity(self):
        """Method call mutations reduce purity score."""
        code = '''
def process_items():
    items = []
    items.append(1)
    items.append(2)
    items.extend([3, 4])
    return items
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        # Multiple mutations should significantly reduce purity
        assert graph.pure_score < 0.7
        assert graph.purity_rating in ('mixed', 'mostly_impure', 'impure')


class TestGlobalWriteTracking:
    """Tests for global/nonlocal variable write tracking."""

    def test_global_write_is_flagged(self):
        """Assignment to global variable sets is_global_write flag."""
        code = '''
counter = 0

def increment():
    global counter
    counter += 1
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        # Should have global side effect
        assert len(graph.side_effects) >= 1
        global_effects = [e for e in graph.side_effects if e.kind == 'global']
        assert len(global_effects) >= 1

        # Should have mutation with is_global_write flag
        global_mutations = [m for m in graph.mutations if m.is_global_write]
        assert len(global_mutations) >= 1

    def test_nonlocal_write_is_flagged(self):
        """Assignment to nonlocal variable sets is_global_write flag."""
        code = '''
def outer():
    x = 0
    def inner():
        nonlocal x
        x += 1
    inner()
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        # Should have nonlocal side effect
        nonlocal_effects = [e for e in graph.side_effects if 'nonlocal' in e.evidence]
        assert len(nonlocal_effects) >= 1

    def test_global_and_local_mix(self):
        """Mix of global and local writes are distinguished."""
        code = '''
total = 0

def add(x):
    global total
    result = x * 2
    total += x
    return result
'''
        tree = parse_python(code)
        graph = analyze_data_flow(tree, bytes(code, 'utf8'), 'python')

        # Should have both global and non-global assignments
        global_writes = [a for a in graph.assignments if a.is_global_write]
        local_writes = [a for a in graph.assignments if not a.is_global_write]

        assert len(global_writes) >= 1
        assert len(local_writes) >= 1
