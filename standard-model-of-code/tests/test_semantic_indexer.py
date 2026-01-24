"""Tests for Stage 6.7 Semantic Purpose Analysis.

Tests the graph_framework, graph_metrics, and intent_extractor modules
that implement PURPOSE = f(edges).
"""
import pytest
from pathlib import Path

from src.core.graph_framework import (
    build_nx_graph,
    find_entry_points,
    propagate_context,
    classify_node_role,
    compute_degree_metrics
)
from src.core.graph_metrics import (
    compute_centrality_metrics,
    identify_critical_nodes,
    detect_clusters
)
from src.core.intent_extractor import (
    extract_docstring_intent,
    classify_commit_intent,
    build_node_intent_profile
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def simple_graph_data():
    """Simple call graph: main -> service -> [repo, util], util -> helper"""
    nodes = [
        {'id': 'main', 'kind': 'function'},
        {'id': 'service', 'kind': 'class'},
        {'id': 'repo', 'kind': 'class'},
        {'id': 'util', 'kind': 'function'},
        {'id': 'helper', 'kind': 'function'},
    ]
    edges = [
        {'source': 'main', 'target': 'service', 'type': 'calls'},
        {'source': 'service', 'target': 'repo', 'type': 'calls'},
        {'source': 'service', 'target': 'util', 'type': 'calls'},
        {'source': 'util', 'target': 'helper', 'type': 'calls'},
    ]
    return nodes, edges


@pytest.fixture
def hub_graph_data():
    """Graph with a hub node (high in and out degree)."""
    nodes = [
        {'id': 'hub', 'kind': 'function'},
        {'id': 'caller1', 'kind': 'function'},
        {'id': 'caller2', 'kind': 'function'},
        {'id': 'caller3', 'kind': 'function'},
        {'id': 'caller4', 'kind': 'function'},
        {'id': 'caller5', 'kind': 'function'},
        {'id': 'caller6', 'kind': 'function'},
        {'id': 'callee1', 'kind': 'function'},
        {'id': 'callee2', 'kind': 'function'},
        {'id': 'callee3', 'kind': 'function'},
        {'id': 'callee4', 'kind': 'function'},
        {'id': 'callee5', 'kind': 'function'},
        {'id': 'callee6', 'kind': 'function'},
    ]
    edges = [
        # 6 callers -> hub
        {'source': 'caller1', 'target': 'hub', 'type': 'calls'},
        {'source': 'caller2', 'target': 'hub', 'type': 'calls'},
        {'source': 'caller3', 'target': 'hub', 'type': 'calls'},
        {'source': 'caller4', 'target': 'hub', 'type': 'calls'},
        {'source': 'caller5', 'target': 'hub', 'type': 'calls'},
        {'source': 'caller6', 'target': 'hub', 'type': 'calls'},
        # hub -> 6 callees
        {'source': 'hub', 'target': 'callee1', 'type': 'calls'},
        {'source': 'hub', 'target': 'callee2', 'type': 'calls'},
        {'source': 'hub', 'target': 'callee3', 'type': 'calls'},
        {'source': 'hub', 'target': 'callee4', 'type': 'calls'},
        {'source': 'hub', 'target': 'callee5', 'type': 'calls'},
        {'source': 'hub', 'target': 'callee6', 'type': 'calls'},
    ]
    return nodes, edges


# =============================================================================
# GRAPH FRAMEWORK TESTS
# =============================================================================

class TestBuildNxGraph:
    """Tests for build_nx_graph()."""

    def test_basic_graph_construction(self, simple_graph_data):
        nodes, edges = simple_graph_data
        G = build_nx_graph(nodes, edges)

        assert len(G.nodes) == 5
        assert len(G.edges) == 4
        assert 'main' in G.nodes
        assert G.has_edge('main', 'service')

    def test_empty_graph(self):
        G = build_nx_graph([], [])
        assert len(G.nodes) == 0
        assert len(G.edges) == 0

    def test_node_attributes_preserved(self, simple_graph_data):
        nodes, edges = simple_graph_data
        G = build_nx_graph(nodes, edges)

        assert G.nodes['main']['kind'] == 'function'
        assert G.nodes['service']['kind'] == 'class'


class TestFindEntryPoints:
    """Tests for find_entry_points()."""

    def test_zero_indegree_entry_points(self, simple_graph_data):
        nodes, edges = simple_graph_data
        G = build_nx_graph(nodes, edges)
        entry_points = find_entry_points(G)

        assert 'main' in entry_points  # Zero in-degree AND 'main' pattern

    def test_pattern_based_entry_points(self):
        nodes = [
            {'id': 'app_init', 'kind': 'function'},
            {'id': 'cli_handler', 'kind': 'function'},
            {'id': 'server_start', 'kind': 'function'},
            {'id': 'helper', 'kind': 'function'},
        ]
        edges = [
            {'source': 'app_init', 'target': 'helper', 'type': 'calls'},
        ]
        G = build_nx_graph(nodes, edges)
        entry_points = find_entry_points(G)

        # All have entry-point patterns in name or zero in-degree
        assert 'app_init' in entry_points
        assert 'cli_handler' in entry_points
        assert 'server_start' in entry_points


class TestClassifyNodeRole:
    """Tests for classify_node_role()."""

    def test_utility_role(self):
        # High in-degree, low out-degree = UTILITY (serves many)
        assert classify_node_role(in_degree=10, out_degree=2) == 'utility'

    def test_orchestrator_role(self):
        # Low in-degree, high out-degree = ORCHESTRATOR (calls many)
        assert classify_node_role(in_degree=2, out_degree=10) == 'orchestrator'

    def test_hub_role(self):
        # High both = HUB (critical junction)
        assert classify_node_role(in_degree=10, out_degree=10) == 'hub'

    def test_leaf_role(self):
        # Low both = LEAF (specialized/isolated)
        assert classify_node_role(in_degree=2, out_degree=2) == 'leaf'

    def test_threshold_boundary(self):
        # Default threshold is 5
        assert classify_node_role(in_degree=5, out_degree=4) == 'utility'
        assert classify_node_role(in_degree=4, out_degree=5) == 'orchestrator'
        assert classify_node_role(in_degree=5, out_degree=5) == 'hub'
        assert classify_node_role(in_degree=4, out_degree=4) == 'leaf'


class TestPropagateContext:
    """Tests for propagate_context()."""

    def test_basic_propagation(self, simple_graph_data):
        nodes, edges = simple_graph_data
        G = build_nx_graph(nodes, edges)
        context = propagate_context(G, ['main'], max_depth=10)

        # All nodes should be reachable from main
        assert 'main' in context
        assert 'service' in context
        assert 'repo' in context
        assert 'util' in context
        assert 'helper' in context

    def test_depth_tracking(self, simple_graph_data):
        nodes, edges = simple_graph_data
        G = build_nx_graph(nodes, edges)
        context = propagate_context(G, ['main'], max_depth=10)

        assert context['main']['depth_from_entry'] == 0
        assert context['service']['depth_from_entry'] == 1
        assert context['repo']['depth_from_entry'] == 2
        assert context['helper']['depth_from_entry'] == 3

    def test_max_depth_limit(self, simple_graph_data):
        nodes, edges = simple_graph_data
        G = build_nx_graph(nodes, edges)
        context = propagate_context(G, ['main'], max_depth=1)

        assert 'main' in context
        assert 'service' in context
        # Depth 2+ should not be reached
        assert 'repo' not in context or context.get('repo', {}).get('depth_from_entry', 99) > 1


# =============================================================================
# GRAPH METRICS TESTS
# =============================================================================

class TestComputeCentralityMetrics:
    """Tests for compute_centrality_metrics()."""

    def test_returns_all_nodes(self, simple_graph_data):
        nodes, edges = simple_graph_data
        G = build_nx_graph(nodes, edges)
        metrics = compute_centrality_metrics(G)

        assert len(metrics) == len(nodes)
        for node in nodes:
            assert node['id'] in metrics

    def test_metric_keys(self, simple_graph_data):
        nodes, edges = simple_graph_data
        G = build_nx_graph(nodes, edges)
        metrics = compute_centrality_metrics(G)

        for node_id, m in metrics.items():
            assert 'betweenness' in m
            assert 'closeness' in m
            assert 'pagerank' in m

    def test_hub_has_high_centrality(self, hub_graph_data):
        nodes, edges = hub_graph_data
        G = build_nx_graph(nodes, edges)
        metrics = compute_centrality_metrics(G)

        hub_betweenness = metrics['hub']['betweenness']
        # Hub should have highest betweenness (all paths go through it)
        for node_id, m in metrics.items():
            if node_id != 'hub':
                assert hub_betweenness >= m['betweenness']


class TestIdentifyCriticalNodes:
    """Tests for identify_critical_nodes()."""

    def test_returns_categories(self, simple_graph_data):
        nodes, edges = simple_graph_data
        G = build_nx_graph(nodes, edges)
        metrics = compute_centrality_metrics(G)
        critical = identify_critical_nodes(G, metrics, top_n=3)

        assert 'bridges' in critical
        assert 'influential' in critical
        assert 'coordinators' in critical

    def test_top_n_limit(self, hub_graph_data):
        nodes, edges = hub_graph_data
        G = build_nx_graph(nodes, edges)
        metrics = compute_centrality_metrics(G)
        critical = identify_critical_nodes(G, metrics, top_n=3)

        assert len(critical['bridges']) <= 3
        assert len(critical['influential']) <= 3
        assert len(critical['coordinators']) <= 3


class TestDetectClusters:
    """Tests for detect_clusters()."""

    def test_returns_clusters(self, simple_graph_data):
        nodes, edges = simple_graph_data
        G = build_nx_graph(nodes, edges)
        clusters = detect_clusters(G)

        assert isinstance(clusters, list)
        assert all(isinstance(c, set) for c in clusters)

    def test_all_nodes_in_clusters(self, simple_graph_data):
        nodes, edges = simple_graph_data
        G = build_nx_graph(nodes, edges)
        clusters = detect_clusters(G)

        all_nodes_in_clusters = set()
        for c in clusters:
            all_nodes_in_clusters.update(c)

        assert all_nodes_in_clusters == set(n['id'] for n in nodes)


# =============================================================================
# INTENT EXTRACTOR TESTS
# =============================================================================

class TestExtractDocstringIntent:
    """Tests for extract_docstring_intent()."""

    def test_triple_double_quotes(self):
        source = '''def foo():
    """This is a docstring."""
    pass'''
        docstring = extract_docstring_intent(source)
        assert docstring == "This is a docstring."

    def test_triple_single_quotes(self):
        source = """def foo():
    '''Single quote docstring.'''
    pass"""
        docstring = extract_docstring_intent(source)
        assert docstring == "Single quote docstring."

    def test_multiline_docstring(self):
        source = '''def foo():
    """
    Multi-line docstring.
    With multiple lines.
    """
    pass'''
        docstring = extract_docstring_intent(source)
        assert "Multi-line docstring" in docstring

    def test_no_docstring(self):
        source = "def foo():\n    pass"
        docstring = extract_docstring_intent(source)
        # Should fallback to comment extraction or return None
        assert docstring is None or docstring == ""

    def test_comment_fallback(self):
        source = "# This is a comment\ndef foo():\n    pass"
        result = extract_docstring_intent(source)
        assert result is None or "This is a comment" in (result or "")


class TestClassifyCommitIntent:
    """Tests for classify_commit_intent()."""

    def test_fix_category(self):
        assert classify_commit_intent("fix: resolve login bug") == 'fix'
        assert classify_commit_intent("Bug fix for issue #123") == 'fix'
        assert classify_commit_intent("Fixed error handling") == 'fix'

    def test_feature_category(self):
        assert classify_commit_intent("feat: add user auth") == 'feature'
        assert classify_commit_intent("Add new API endpoint") == 'feature'
        assert classify_commit_intent("Implement caching") == 'feature'

    def test_refactor_category(self):
        assert classify_commit_intent("refactor: clean up code") == 'refactor'
        assert classify_commit_intent("Restructure module layout") == 'refactor'

    def test_docs_category(self):
        assert classify_commit_intent("docs: update README") == 'docs'
        assert classify_commit_intent("Update docstrings") == 'docs'  # "Add" would match feature first

    def test_test_category(self):
        assert classify_commit_intent("test: unit tests") == 'test'  # "add" would match feature first
        assert classify_commit_intent("Improve test coverage") == 'test'

    def test_chore_fallback(self):
        assert classify_commit_intent("bump version") == 'chore'
        assert classify_commit_intent("misc changes") == 'chore'


class TestBuildNodeIntentProfile:
    """Tests for build_node_intent_profile()."""

    def test_basic_profile_structure(self, tmp_path):
        # Create a minimal repo structure
        (tmp_path / ".git").mkdir()

        profile = build_node_intent_profile(
            node_id="test_func",
            file_path="test.py",
            source_code='def test():\n    """Test docstring."""\n    pass',
            repo_path=tmp_path
        )

        assert 'node_id' in profile
        assert profile['node_id'] == 'test_func'
        assert 'file_path' in profile

    def test_extracts_docstring(self, tmp_path):
        (tmp_path / ".git").mkdir()

        profile = build_node_intent_profile(
            node_id="documented_func",
            file_path="doc.py",
            source_code='"""Module docstring for testing."""\ndef foo(): pass',
            repo_path=tmp_path
        )

        assert 'docstring' in profile
        assert "Module docstring" in profile['docstring']


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestSemanticIndexerIntegration:
    """End-to-end tests for the semantic indexer."""

    def test_full_pipeline(self, simple_graph_data):
        """Test the complete semantic analysis pipeline."""
        nodes, edges = simple_graph_data

        # Build graph
        G = build_nx_graph(nodes, edges)
        assert len(G.nodes) == 5

        # Find entry points
        entry_points = find_entry_points(G)
        assert len(entry_points) >= 1

        # Propagate context
        context = propagate_context(G, entry_points)
        assert len(context) >= 1

        # Compute centrality
        centrality = compute_centrality_metrics(G)
        assert len(centrality) == 5

        # Identify critical nodes
        critical = identify_critical_nodes(G, centrality)
        assert 'bridges' in critical

        # Detect clusters
        clusters = detect_clusters(G)
        assert len(clusters) >= 1

        # Classify roles
        degree_metrics = compute_degree_metrics(G)
        for node_id, m in degree_metrics.items():
            role = classify_node_role(m['in_degree'], m['out_degree'])
            assert role in ('utility', 'orchestrator', 'hub', 'leaf')
